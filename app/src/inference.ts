import { buildModelInput } from "./features";
import type { Chain, Horizon } from "./domain";
import { createDefaultModelCatalog, createModelRuntime } from "./model";
import type { ModelCatalog, ModelRuntime } from "./model";
import { createChainSession } from "./rpc";
import type { ChainSession } from "./rpc";

/**
 * A decision anchored at `head_block`; action `0` targets `head_block + 1`.
 * The predicted minimum base fee is denominated in wei per gas.
 */
export type InferenceResult = {
  chain: Chain;
  K: Horizon;
  head_block: number;
  selected_action_k: number;
  target_block: number;
  predicted_minimum_base_fee_per_gas: number;
};

export type InferenceOutcome = {
  immediate_base_fee_per_gas: number;
  selected_base_fee_per_gas: number;
};

export type InferenceRuntime = {
  currentHead(chain: Chain): Promise<number>;
  run(chain: Chain, K: Horizon): Promise<InferenceResult>;
  resolveOutcome(
    chain: Chain,
    immediateBlock: number,
    selectedBlock: number,
  ): Promise<InferenceOutcome>;
  dispose(): Promise<void>;
};

export type InferenceRuntimeDependencies = {
  catalog: ModelCatalog;
  model: ModelRuntime;
  sessions: Readonly<Record<Chain, ChainSession>>;
};

export function createInferenceRuntime(
  dependencies: InferenceRuntimeDependencies = defaultDependencies(),
): InferenceRuntime {
  const { catalog, model, sessions } = dependencies;

  async function run(chain: Chain, K: Horizon): Promise<InferenceResult> {
    const selection = catalog.select(chain, K);
    const session = sessions[chain];
    const context = await session.sync();

    const head = context.blocks[context.blocks.length - 1];
    const input = buildModelInput(
      context.blocks,
      context.priorityFeeRewards,
      selection.chainManifest,
    );
    const prediction = await model.execute(selection, input);
    const immediateBlock = head.number + 1n;
    const targetBlock = immediateBlock + BigInt(prediction.selectedAction);
    return {
      chain,
      K: selection.K,
      head_block: Number(head.number),
      selected_action_k: prediction.selectedAction,
      target_block: Number(targetBlock),
      predicted_minimum_base_fee_per_gas: prediction.predictedFee,
    };
  }

  async function currentHead(chain: Chain): Promise<number> {
    const session = sessions[chain];
    return Number(await session.readHead());
  }

  async function resolveOutcome(
    chain: Chain,
    immediateBlock: number,
    selectedBlock: number,
  ): Promise<InferenceOutcome> {
    const session = sessions[chain];
    const immediate = BigInt(immediateBlock);
    const selected = BigInt(selectedBlock);
    const outcome = await session.readOutcome(immediate, selected);
    return {
      immediate_base_fee_per_gas: Number(outcome.immediateBaseFeePerGas),
      selected_base_fee_per_gas: Number(outcome.selectedBaseFeePerGas),
    };
  }

  return {
    currentHead,
    run,
    resolveOutcome,
    dispose: () => model.dispose(),
  };
}

function defaultDependencies(): InferenceRuntimeDependencies {
  const catalog = createDefaultModelCatalog();
  return {
    catalog,
    model: createModelRuntime(),
    sessions: {
      ethereum: createChainSession(
        "ethereum",
        catalog.chainManifest("ethereum"),
      ),
      polygon: createChainSession(
        "polygon",
        catalog.chainManifest("polygon"),
      ),
      avalanche: createChainSession(
        "avalanche",
        catalog.chainManifest("avalanche"),
      ),
    },
  };
}
