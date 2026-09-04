import { describe, expect, it, vi } from "vitest";

vi.mock("react-native-executorch", () => ({
  ExecutorchModule: vi.fn(),
  ScalarType: { FLOAT: 6 },
  initExecutorch: vi.fn(),
}));

vi.mock("react-native-executorch-expo-resource-fetcher", () => ({
  ExpoResourceFetcher: { name: "expo-resource-fetcher" },
}));

import {
  createInferenceRuntime,
  type InferenceRuntimeDependencies,
} from "../src/inference";
import type { BlockRow, Chain } from "../src/domain";
import type {
  ModelCatalog,
  ModelPrediction,
  ModelRuntime,
} from "../src/model";
import type {
  ChainOutcome,
  ChainSession,
  PreparedChainContext,
} from "../src/rpc";
import {
  chainManifest,
  modelSelection,
} from "./helpers";

function block(
  number: bigint,
  baseFeePerGas = number + 10n,
): BlockRow {
  return {
    number,
    timestamp: 1_700_000_000n + number,
    baseFeePerGas,
    gasUsed: 100n,
    gasLimit: 200n,
    transactionCount: 0,
  };
}

function context(
  head: bigint,
  headBaseFee = head + 10n,
): PreparedChainContext {
  return {
    blocks: [
      block(head - 1n, headBaseFee - 1n),
      block(head, headBaseFee),
    ],
    priorityFeeRewards: [
      [1n, 2n],
      [1n, 2n],
    ],
  };
}

function session(
  sync: () => Promise<PreparedChainContext> = async () => context(10n),
): ChainSession {
  return {
    sync: vi.fn(sync),
    readHead: vi.fn(async () => 10n),
    readOutcome: vi.fn(
      async (
        _immediateBlock: bigint,
        _selectedBlock: bigint,
      ): Promise<ChainOutcome> => ({
        immediateBaseFeePerGas: 20n,
        selectedBaseFeePerGas: 18n,
      }),
    ),
  };
}

function runtime(
  output: ModelPrediction = {
    selectedAction: 1,
    predictedFee: 100,
  },
): ModelRuntime {
  return {
    execute: vi.fn(async () => output),
    dispose: vi.fn(async () => undefined),
  };
}

function sessions(
  overrides: Partial<Record<Chain, ChainSession>> = {},
): Readonly<Record<Chain, ChainSession>> {
  return {
    ethereum: session(),
    polygon: session(),
    avalanche: session(),
    ...overrides,
  };
}

function catalog(): ModelCatalog {
  return {
    chainManifest: vi.fn(() => chainManifest),
    select: vi.fn((_chain, K) => modelSelection(K)),
  };
}

function createTestRuntime(
  overrides: Partial<InferenceRuntimeDependencies> = {},
) {
  const dependencies: InferenceRuntimeDependencies = {
    catalog: catalog(),
    model: runtime(),
    sessions: sessions(),
    ...overrides,
  };
  return {
    dependencies,
    inference: createInferenceRuntime(dependencies),
  };
}

describe("InferenceRuntime", () => {
  it("uses the selected chain session and model for Run", async () => {
    const polygon = session(async () => context(11n, 40n));
    const model = runtime({
      selectedAction: 1,
      predictedFee: Math.exp(Math.log(100) + 1),
    });
    const { dependencies, inference } = createTestRuntime({
      model,
      sessions: sessions({ polygon }),
    });

    const result = await inference.run("polygon", 4);

    expect(polygon.sync).toHaveBeenCalledOnce();
    expect(dependencies.sessions.ethereum.sync).not.toHaveBeenCalled();
    expect(dependencies.catalog.select).toHaveBeenCalledWith(
      "polygon",
      4,
    );
    expect(model.execute).toHaveBeenCalledWith(
      modelSelection(4),
      new Float32Array([
        Math.fround(Math.log(39)),
        Math.fround(Math.log(40)),
      ]),
    );
    expect(result).toEqual({
      chain: "polygon",
      K: 4,
      head_block: 11,
      selected_action_k: 1,
      target_block: 13,
      predicted_minimum_base_fee_per_gas: expect.closeTo(
        Math.exp(Math.log(100) + 1),
      ),
    });
    await inference.dispose();
  });

});
