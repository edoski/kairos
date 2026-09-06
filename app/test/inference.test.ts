import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Chain } from "../src/domain";
import type { PreparedChainContext } from "../src/rpc";
import { deferred, modelSelection } from "./helpers";

const mocks = vi.hoisted(() => ({ module: vi.fn(), reader: vi.fn(), select: vi.fn() }));
vi.mock("react-native-executorch", () => ({
  ExecutorchModule: mocks.module, ScalarType: { FLOAT: 6 }, initExecutorch: vi.fn(),
}));
vi.mock("react-native-executorch-expo-resource-fetcher", () => ({ ExpoResourceFetcher: {} }));
vi.mock("../src/bundledModels", () => ({ selectModel: mocks.select }));
vi.mock("../src/rpc", () => ({ createChainReader: mocks.reader }));

function context(head: bigint): PreparedChainContext {
  return {
    blocks: [head - 2n, head - 1n, head].map((number) => ({
      number, timestamp: 1_700_000_000n + number, baseFeePerGas: number + 10n,
      gasUsed: 100n, gasLimit: 200n, transactionCount: 0,
    })),
    priorityFeeRewards: [[1n, 2n], [1n, 2n]],
  };
}
function outputs() {
  return [
    { dataPtr: new Float32Array([0, 1]).buffer, sizes: [1, 2], scalarType: 6 },
    { dataPtr: new Float32Array([0.25]).buffer, sizes: [1], scalarType: 6 },
  ];
}
function native() {
  return { load: vi.fn(async (): Promise<void> => undefined), forward: vi.fn(async () => outputs()), delete: vi.fn() };
}
const readers = Object.fromEntries(["ethereum", "polygon", "avalanche"].map((chain) => [chain, {
  readContext: vi.fn(), readHead: vi.fn(), readOutcome: vi.fn(),
}])) as Record<Chain, { readContext: ReturnType<typeof vi.fn>; readHead: ReturnType<typeof vi.fn>; readOutcome: ReturnType<typeof vi.fn> }>;
let inference: typeof import("../src/inference");
beforeEach(async () => {
  vi.resetModules();
  mocks.module.mockReset().mockImplementation(function () { return native(); });
  mocks.select.mockReset().mockImplementation((_chain, K) => modelSelection(K));
  mocks.reader.mockReset().mockImplementation((chain: Chain) => readers[chain]);
  for (const reader of Object.values(readers)) {
    reader.readContext.mockReset().mockResolvedValue(context(10n));
    reader.readHead.mockReset().mockResolvedValue(20n);
    reader.readOutcome.mockReset().mockResolvedValue({ immediateBaseFeePerGas: 20n, selectedBaseFeePerGas: 18n });
  }
  inference = await import("../src/inference");
});

describe("request-scoped inference", () => {
  it("serializes load, fresh context, execution and release and keeps the result usable afterward", async () => {
    const loaded = deferred<void>();
    const forwarded = deferred<ReturnType<typeof outputs>>();
    const first = native(); const second = native();
    first.load.mockReturnValueOnce(loaded.promise);
    first.forward.mockReturnValueOnce(forwarded.promise);
    const events: string[] = [];
    first.delete.mockImplementation(() => { events.push("released first"); });
    second.load.mockImplementation(async () => { events.push("loaded second"); });
    mocks.module.mockImplementationOnce(function () { return first; }).mockImplementationOnce(function () { return second; });
    const one = inference.infer("polygon", 2);
    const two = inference.infer("polygon", 2);
    await vi.waitFor(() => expect(first.load).toHaveBeenCalledOnce());
    expect(readers.polygon.readContext).not.toHaveBeenCalled();
    expect(mocks.module).toHaveBeenCalledOnce();
    loaded.resolve();
    await vi.waitFor(() => expect(first.forward).toHaveBeenCalledOnce());
    expect(readers.polygon.readContext).toHaveBeenCalledWith(2);
    expect(readers.ethereum.readContext).not.toHaveBeenCalled();
    expect(first.forward).toHaveBeenCalledWith([{
      dataPtr: new Float32Array([Math.log(19), Math.log(20)]), sizes: [1, 2, 1], scalarType: 6,
    }]);
    const tensors = outputs();
    forwarded.resolve(tensors);
    const result = await one;
    await two;
    expect(events).toEqual(["released first", "loaded second"]);
    expect(second.delete).toHaveBeenCalledOnce();
    new Float32Array(tensors[1].dataPtr).fill(NaN);
    expect(result).toEqual({ chain: "polygon", K: 2, head_block: 10, selected_action_k: 1,
      target_block: 12, predicted_minimum_base_fee_per_gas: expect.closeTo(Math.exp(Math.log(100) + .125)) });
  });

  it.each(["load", "context", "features", "forward", "decode"])("recovers after a %s failure and releases every successfully loaded module", async (stage) => {
    const failed = native(); const recovered = native();
    mocks.module.mockImplementationOnce(function () { return failed; }).mockImplementationOnce(function () { return recovered; });
    if (stage === "load") failed.load.mockRejectedValueOnce(new Error("load failed"));
    if (stage === "context") readers.ethereum.readContext.mockRejectedValueOnce(new Error("context failed"));
    if (stage === "features") readers.ethereum.readContext.mockResolvedValueOnce(context(-10n));
    if (stage === "forward") failed.forward.mockRejectedValueOnce(new Error("forward failed"));
    if (stage === "decode") failed.forward.mockResolvedValueOnce([]);
    await expect(inference.infer("ethereum", 2)).rejects.toThrow();
    expect(failed.delete).toHaveBeenCalledTimes(stage === "load" ? 0 : 1);
    await expect(inference.infer("ethereum", 2)).resolves.toMatchObject({ head_block: 10 });
    expect(recovered.delete).toHaveBeenCalledOnce();
  });

  it("reads observed outcomes outside the native queue", async () => {
    const loading = deferred<void>(); const module = native();
    module.load.mockReturnValueOnce(loading.promise);
    mocks.module.mockImplementationOnce(function () { return module; });
    const pending = inference.infer("ethereum", 2);
    await vi.waitFor(() => expect(module.load).toHaveBeenCalledOnce());
    await expect(inference.currentHead("polygon")).resolves.toBe(20);
    await expect(inference.resolveOutcome("polygon", 21, 23)).resolves.toEqual({ immediate_base_fee_per_gas: 20, selected_base_fee_per_gas: 18 });
    expect(readers.polygon.readOutcome).toHaveBeenCalledWith(21n, 23n);
    loading.resolve(); await pending;
  });
});
