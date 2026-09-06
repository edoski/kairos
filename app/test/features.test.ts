import { describe, expect, it } from "vitest";
import type { BlockRow } from "../src/domain";
import { buildModelInput } from "../src/features";
import type { ChainManifest, FeatureName } from "../src/features";
import fixture from "./fixtures/features.json";

function fixtureBlocks(): BlockRow[] {
  return fixture.blocks.map((block) => ({
    number: BigInt(block.number),
    timestamp: BigInt(block.timestamp),
    baseFeePerGas: BigInt(block.baseFeePerGas),
    gasUsed: BigInt(block.gasUsed),
    gasLimit: BigInt(block.gasLimit),
    transactionCount: block.transactionCount,
  }));
}

function fixturePriorityFeeRewards(): readonly (readonly [bigint, bigint])[] {
  return fixture.priorityFeeRewards.map(([p50, p90]) => [
    BigInt(p50),
    BigInt(p90),
  ]);
}

function fixtureManifest(): ChainManifest {
  return {
    context_blocks: fixture.manifest.context_blocks,
    features: fixture.manifest.features.map((feature) => ({
      ...feature,
      name: feature.name as FeatureName,
    })),
  };
}

describe("buildModelInput", () => {
  it("matches the Python float32 oracle for all transforms in manifest order", () => {
    const result = buildModelInput(
      fixtureBlocks(),
      fixturePriorityFeeRewards(),
      fixtureManifest(),
    );

    expect(result).toBeInstanceOf(Float32Array);
    expect(result).toHaveLength(
      fixture.manifest.context_blocks * fixture.manifest.features.length,
    );
    result.forEach((value, index) => {
      expect(
        Math.abs(value - fixture.expected[index]),
      ).toBeLessThanOrEqual(1e-6);
    });
  });

  it("uses exact forming-fee integer arithmetic", () => {
    const blocks = fixtureBlocks();
    const formingBlocks = [
      blocks[0],
      { ...blocks[1], baseFeePerGas: 1n, gasUsed: 101n, gasLimit: 200n },
      { ...blocks[2], baseFeePerGas: 9n, gasUsed: 0n, gasLimit: 200n },
      { ...blocks[3], baseFeePerGas: 10n, gasUsed: 100n, gasLimit: 200n },
      blocks[4],
    ];
    const formingInput = buildModelInput(
      formingBlocks,
      [
        [0n, 0n],
        [0n, 0n],
        [0n, 0n],
        [0n, 0n],
      ],
      {
        context_blocks: 4,
        features: [
          {
            name: "log_exact_forming_base_fee_per_gas",
            mean: 0,
            standard_deviation: 1,
          },
        ],
      },
    );

    ["2", "8", "10", fixture.formingChildBaseFees[3]].forEach((fee, index) => {
      expect(
        Math.abs(formingInput[index] - Math.log(Number(fee))),
      ).toBeLessThanOrEqual(1e-6);
    });
  });

  it("rejects nonfinite final float32 features", () => {
    expect(() =>
      buildModelInput(fixtureBlocks().slice(0, 2), [[0n, 0n]], {
        context_blocks: 1,
        features: [
          {
            name: "log_base_fee_per_gas",
            mean: -Number.MAX_VALUE,
            standard_deviation: 1,
          },
        ],
      }),
    ).toThrow("Model input must contain finite float32 values");
  });
});
