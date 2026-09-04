import type { BlockRow } from "./domain";

export type FeatureName =
  | "log_base_fee_per_gas"
  | "gas_utilization"
  | "log_exact_forming_base_fee_per_gas"
  | "log_gas_limit"
  | "log1p_tx_count"
  | "log1p_effective_priority_fee_per_gas_p50"
  | "log1p_effective_priority_fee_per_gas_p90"
  | "block_interval_seconds"
  | "hour_sin"
  | "hour_cos"
  | "dow_sin"
  | "dow_cos";

type FeatureManifest = {
  name: FeatureName;
  mean: number;
  standard_deviation: number;
};

export type ChainManifest = {
  context_blocks: number;
  features: readonly FeatureManifest[];
};

export type PriorityFeeRewards = readonly [p50: bigint, p90: bigint];

export function predecessorOffset(manifest: ChainManifest): 0 | 1 {
  return manifest.features.some(
    (feature) => feature.name === "block_interval_seconds",
  )
    ? 1
    : 0;
}

/**
 * Builds the flat row-major `[C,F]` Float32 matrix in manifest feature order.
 * Expects ascending contiguous blocks, one leading predecessor for interval features,
 * and reward rows aligned by height with the final `C` blocks.
 */
export function buildModelInput(
  blocks: readonly BlockRow[],
  priorityFeeRewards: readonly PriorityFeeRewards[],
  manifest: ChainManifest,
): Float32Array {
  const offset = predecessorOffset(manifest);
  const featureCount = manifest.features.length;
  const output = new Float32Array(manifest.context_blocks * featureCount);

  for (let row = 0; row < manifest.context_blocks; row += 1) {
    const blockIndex = row + offset;
    const block = blocks[blockIndex];
    for (let column = 0; column < featureCount; column += 1) {
      const feature = manifest.features[column];
      const raw = rawFeature(
        feature.name,
        block,
        blocks[blockIndex - 1],
        priorityFeeRewards[row],
      );
      const index = row * featureCount + column;
      output[index] =
        (raw - feature.mean) / feature.standard_deviation;
      if (!Number.isFinite(output[index])) {
        throw new Error("Model input must contain finite float32 values");
      }
    }
  }

  return output;
}

function rawFeature(
  feature: FeatureName,
  block: BlockRow,
  predecessor: BlockRow,
  priorityFeeRewards: PriorityFeeRewards,
): number {
  switch (feature) {
    case "log_base_fee_per_gas":
      return logBigInt(block.baseFeePerGas);
    case "gas_utilization":
      return Number(block.gasUsed) / Number(block.gasLimit);
    case "log_exact_forming_base_fee_per_gas":
      return logBigInt(formingChildBaseFee(block));
    case "log_gas_limit":
      return logBigInt(block.gasLimit);
    case "log1p_tx_count":
      return Math.log1p(block.transactionCount);
    case "log1p_effective_priority_fee_per_gas_p50":
      return Math.log1p(Number(priorityFeeRewards[0]));
    case "log1p_effective_priority_fee_per_gas_p90":
      return Math.log1p(Number(priorityFeeRewards[1]));
    case "block_interval_seconds": {
      return Number(block.timestamp - predecessor.timestamp);
    }
    case "hour_sin":
      return Math.sin(hourAngle(block.timestamp));
    case "hour_cos":
      return Math.cos(hourAngle(block.timestamp));
    case "dow_sin":
      return Math.sin(dayOfWeekAngle(block.timestamp));
    case "dow_cos":
      return Math.cos(dayOfWeekAngle(block.timestamp));
  }
}

function logBigInt(value: bigint): number {
  return Math.log(Number(value));
}

/**
 * Applies Ethereum's EIP-1559 parent-to-child recurrence using ordered
 * integer division and a minimum one-wei increase.
 */
function formingChildBaseFee(block: BlockRow): bigint {
  const gasTarget = block.gasLimit / 2n;
  if (block.gasUsed === gasTarget) {
    return block.baseFeePerGas;
  }
  if (block.gasUsed > gasTarget) {
    const increase =
      (block.baseFeePerGas * (block.gasUsed - gasTarget)) /
      gasTarget /
      8n;
    return block.baseFeePerGas + (increase > 0n ? increase : 1n);
  }
  const decrease =
    (block.baseFeePerGas * (gasTarget - block.gasUsed)) /
    gasTarget /
    8n;
  return block.baseFeePerGas - decrease;
}

function hourAngle(timestamp: bigint): number {
  const hour = Number((timestamp / 3_600n) % 24n);
  return (2 * Math.PI * hour) / 24;
}

function dayOfWeekAngle(timestamp: bigint): number {
  const day = Number((timestamp / 86_400n + 4n) % 7n);
  return (2 * Math.PI * day) / 7;
}
