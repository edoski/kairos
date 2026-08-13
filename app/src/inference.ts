import { buildModelInput } from "./features";
import type { Chain, Horizon } from "./domain";
import { createDefaultModelCatalog, createModelRuntime } from "./model";
import type {
  ModelCatalog,
  ModelOutput,
  ModelRuntime,
  ModelSelection,
} from "./model";
import { createChainSession } from "./rpc";
import type { ChainSession } from "./rpc";

export type InferenceResult = {
  chain: Chain;
  K: Horizon;
  artifact_id: string;
  head_block: number;
  head_hash: string;
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
    const prediction = decodePrediction(
      selection,
      await model.execute(selection, input),
    );
    const immediateBlock = head.number + 1n;
    const targetBlock = immediateBlock + BigInt(prediction.selectedAction);
    return {
      chain,
      K: selection.K,
      artifact_id: selection.modelManifest.artifact_id,
      head_block: safeBigInt(head.number, "head block"),
      head_hash: head.hash,
      selected_action_k: prediction.selectedAction,
      target_block: safeBigInt(targetBlock, "target block"),
      predicted_minimum_base_fee_per_gas: prediction.predictedFee,
    };
  }

  async function currentHead(chain: Chain): Promise<number> {
    const session = sessions[chain];
    return safeBigInt(await session.readHead(), "head block");
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
      immediate_base_fee_per_gas: safeBigInt(
        outcome.immediateBaseFeePerGas,
        "immediate base fee",
      ),
      selected_base_fee_per_gas: safeBigInt(
        outcome.selectedBaseFeePerGas,
        "selected base fee",
      ),
    };
  }

  const dispose = () => model.dispose();

  return {
    currentHead,
    run,
    resolveOutcome,
    dispose,
  };
}

function defaultDependencies(): InferenceRuntimeDependencies {
  const catalog = createDefaultModelCatalog();
  return {
    catalog,
    model: createModelRuntime(),
    sessions: Object.freeze({
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
    }),
  };
}

function decodePrediction(
  selection: ModelSelection,
  output: ModelOutput,
): {
  selectedAction: number;
  predictedFee: number;
} {
  const action = output.actionLogits.indexOf(
    Math.max(...output.actionLogits),
  );

  const target = selection.modelManifest.target;
  const predictedFee = Math.exp(
    target.mean + target.standard_deviation * output.minimumFeeZ,
  );
  if (!Number.isFinite(predictedFee) || predictedFee <= 0) {
    throw new Error("Predicted fee must be positive and finite");
  }

  return {
    selectedAction: action,
    predictedFee,
  };
}

function safeBigInt(value: bigint, label: string): number {
  if (value < 0n || value > BigInt(Number.MAX_SAFE_INTEGER)) {
    throw new Error(`${label} exceeds the safe integer range`);
  }
  return Number(value);
}
