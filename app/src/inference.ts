import { ExecutorchModule } from "react-native-executorch";
import { buildModelInput } from "./features";
import type { Chain, Horizon } from "./domain";
import { selectModel } from "./bundledModels";
import { executeModel } from "./model";
import { createChainReader } from "./rpc";
import { createSerialQueue } from "./serialQueue";

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

const serialize = createSerialQueue();
const readers = {
  ethereum: createChainReader("ethereum"),
  polygon: createChainReader("polygon"),
  avalanche: createChainReader("avalanche"),
};

export function infer(chain: Chain, K: Horizon): Promise<InferenceResult> {
  return serialize(async () => {
    const selection = selectModel(chain, K);
    const module = new ExecutorchModule();
    await module.load(selection.source);
    try {
      const context = await readers[chain].readContext(
        selection.chainManifest.context_blocks,
      );
      const head = context.blocks[context.blocks.length - 1];
      const input = buildModelInput(
        context.blocks,
        context.priorityFeeRewards,
        selection.chainManifest,
      );
      const prediction = await executeModel(module, selection, input);
      return {
        chain,
        K,
        head_block: Number(head.number),
        selected_action_k: prediction.selectedAction,
        target_block: Number(
          head.number + 1n + BigInt(prediction.selectedAction),
        ),
        predicted_minimum_base_fee_per_gas: prediction.predictedFee,
      };
    } finally {
      module.delete();
    }
  });
}

export async function currentHead(chain: Chain): Promise<number> {
  return Number(await readers[chain].readHead());
}

export async function resolveOutcome(
  chain: Chain,
  immediateBlock: number,
  selectedBlock: number,
): Promise<InferenceOutcome> {
  const outcome = await readers[chain].readOutcome(
    BigInt(immediateBlock),
    BigInt(selectedBlock),
  );
  return {
    immediate_base_fee_per_gas: Number(outcome.immediateBaseFeePerGas),
    selected_base_fee_per_gas: Number(outcome.selectedBaseFeePerGas),
  };
}
