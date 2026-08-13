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
  ModelOutput,
  ModelRuntime,
} from "../src/model";
import type {
  ChainOutcome,
  ChainSession,
  PreparedChainContext,
} from "../src/rpc";
import {
  chainManifest,
  hashOf,
  modelSelection,
} from "./helpers";

function block(
  number: bigint,
  baseFeePerGas = number + 10n,
): BlockRow {
  return {
    number,
    hash: hashOf(number),
    parentHash: hashOf(number - 1n),
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
    priorityFeeRewards: null,
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
  output: ModelOutput = {
    actionLogits: new Float32Array([0, 1]),
    minimumFeeZ: 0,
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
      actionLogits: new Float32Array([-1, 4, 1, 0]),
      minimumFeeZ: 2,
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
      artifact_id: chainManifest.models[4].artifact_id,
      head_block: 11,
      head_hash: hashOf(11n),
      selected_action_k: 1,
      target_block: 13,
      predicted_minimum_base_fee_per_gas: expect.closeTo(
        Math.exp(Math.log(100) + 1),
      ),
    });
    await inference.dispose();
  });

  it("propagates RPC and native failures from their owners", async () => {
    const rpcError = new Error("HTTP transport details");
    const unavailable = session(async () => {
      throw rpcError;
    });
    const chainFailure = createTestRuntime({
      sessions: sessions({ avalanche: unavailable }),
    }).inference;
    await expect(chainFailure.run("avalanche", 2)).rejects.toBe(rpcError);
    await chainFailure.dispose();

    const model = runtime();
    const nativeCause = new Error("native cause");
    const nativeError = new Error("native load details", {
      cause: nativeCause,
    });
    vi.mocked(model.execute).mockRejectedValue(nativeError);
    const modelFailure = createTestRuntime({ model }).inference;
    await expect(modelFailure.run("ethereum", 2)).rejects.toBe(nativeError);
    expect(nativeError.cause).toBe(nativeCause);
    await modelFailure.dispose();
  });

  it("propagates feature validation from its owner", async () => {
    const model = runtime();
    const invalidManifest = {
      ...chainManifest,
      features: [
        {
          name: "log_base_fee_per_gas" as const,
          mean: 0,
          standard_deviation: 0,
        },
      ],
    };
    const invalidCatalog: ModelCatalog = {
      chainManifest: vi.fn(() => invalidManifest),
      select: vi.fn((_chain, K) => ({
        ...modelSelection(K),
        chainManifest: invalidManifest,
      })),
    };
    const inference = createTestRuntime({
      catalog: invalidCatalog,
      model,
    }).inference;

    await expect(inference.run("ethereum", 2)).rejects.toThrow(
      "Model input must contain finite float32 values",
    );
    expect(model.execute).not.toHaveBeenCalled();
    await inference.dispose();
  });

  it("rejects a nonfinite decoded fee", async () => {
    const inference = createTestRuntime({
      model: runtime({
        actionLogits: new Float32Array([0, 1]),
        minimumFeeZ: 2_000,
      }),
    }).inference;
    await expect(inference.run("ethereum", 2)).rejects.toThrow(
      "Predicted fee must be positive and finite",
    );
    await inference.dispose();
  });

  it("selects the first action when maximum logits tie", async () => {
    const inference = createTestRuntime({
      model: runtime({
        actionLogits: new Float32Array([1, 4, 4, 0]),
        minimumFeeZ: 0,
      }),
    }).inference;

    await expect(inference.run("ethereum", 4)).resolves.toMatchObject({
      selected_action_k: 1,
      target_block: 12,
    });
    await inference.dispose();
  });

  it("rejects an unsafe external head block without losing raw precision", async () => {
    const unsafe = BigInt(Number.MAX_SAFE_INTEGER) + 1n;
    const unsafeHead = session(async () => context(unsafe, 20n));
    const inference = createTestRuntime({
      sessions: sessions({ ethereum: unsafeHead }),
    }).inference;

    await expect(inference.run("ethereum", 2)).rejects.toThrow(
      "head block exceeds the safe integer range",
    );
    await inference.dispose();
  });

  it("reads the selected chain head once through a safe integer", async () => {
    const avalanche = session();
    const { dependencies, inference } = createTestRuntime({
      sessions: sessions({ avalanche }),
    });

    await expect(inference.currentHead("avalanche")).resolves.toBe(10);
    expect(avalanche.readHead).toHaveBeenCalledOnce();
    expect(dependencies.sessions.ethereum.readHead).not.toHaveBeenCalled();

    vi.mocked(avalanche.readHead).mockResolvedValueOnce(
      BigInt(Number.MAX_SAFE_INTEGER) + 1n,
    );
    await expect(inference.currentHead("avalanche")).rejects.toThrow(
      "head block exceeds the safe integer range",
    );
    await inference.dispose();
  });

  it("reads exact outcome blocks from the selected chain session", async () => {
    const polygon = session();
    const { dependencies, inference } = createTestRuntime({
      sessions: sessions({ polygon }),
    });

    await expect(
      inference.resolveOutcome("polygon", 11, 12),
    ).resolves.toEqual({
      immediate_base_fee_per_gas: 20,
      selected_base_fee_per_gas: 18,
    });
    expect(polygon.readOutcome).toHaveBeenCalledWith(11n, 12n);
    expect(dependencies.sessions.ethereum.readOutcome).not.toHaveBeenCalled();

    vi.mocked(polygon.readOutcome).mockResolvedValueOnce({
      immediateBaseFeePerGas: BigInt(Number.MAX_SAFE_INTEGER) + 1n,
      selectedBaseFeePerGas: 18n,
    });
    await expect(
      inference.resolveOutcome("polygon", 11, 12),
    ).rejects.toThrow("immediate base fee exceeds the safe integer range");
    await inference.dispose();
  });

  it("disposes its one model runtime", async () => {
    const model = runtime();
    const inference = createTestRuntime({ model }).inference;

    await inference.dispose();
    expect(model.dispose).toHaveBeenCalledOnce();
  });
});
