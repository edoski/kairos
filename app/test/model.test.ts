import { describe, expect, it, vi } from "vitest";

const executorch = vi.hoisted(() => ({
  init: vi.fn(),
  module: vi.fn(),
}));

vi.mock("react-native-executorch", () => ({
  ExecutorchModule: executorch.module,
  ScalarType: { FLOAT: 6, INT: 3 },
  initExecutorch: executorch.init,
}));

vi.mock("react-native-executorch-expo-resource-fetcher", () => ({
  ExpoResourceFetcher: { name: "expo-resource-fetcher" },
}));

import { createModelRuntime } from "../src/model";
import { deferred, modelSelection } from "./helpers";

type NativeTensor = {
  dataPtr: ArrayBuffer | Float32Array;
  sizes: number[];
  scalarType: number;
};

function output(
  values: readonly number[],
  sizes: number[],
  scalarType = 6,
): NativeTensor {
  return {
    dataPtr: new Float32Array(values).buffer,
    sizes,
    scalarType,
  };
}

function native(
  forward: (inputs: NativeTensor[]) => Promise<NativeTensor[]> = async () => [
    output([0, 1], [1, 2]),
    output([0.25], [1]),
  ],
) {
  return {
    load: vi.fn(async (_source: number) => undefined),
    forward: vi.fn(forward),
    delete: vi.fn(),
  };
}

function predictedFee(z: number): number {
  return Math.exp(Math.log(100) + 0.5 * z);
}

describe("model runtime", () => {
  it("loads on first execution and reuses an unchanged model", async () => {
    const module = native();
    const factory = vi.fn(() => module);
    const runtime = createModelRuntime(factory);
    const selected = modelSelection(2);
    const input = new Float32Array([1, 2]);

    const first = await runtime.execute(selected, input);
    const second = await runtime.execute(selected, input);

    expect(factory).toHaveBeenCalledTimes(1);
    expect(module.load).toHaveBeenCalledOnce();
    expect(module.load).toHaveBeenCalledWith(12);
    expect(module.forward).toHaveBeenCalledTimes(2);
    expect(module.forward).toHaveBeenLastCalledWith([
      {
        dataPtr: input,
        sizes: [1, 2, 1],
        scalarType: 6,
      },
    ]);
    expect(first).toEqual({
      selectedAction: 1,
      predictedFee: expect.closeTo(predictedFee(0.25)),
    });
    expect(second).toEqual(first);

    await runtime.dispose();
    expect(module.delete).toHaveBeenCalledOnce();
  });

  it("serializes concurrent execution, replacement, and disposal", async () => {
    const forward = deferred<NativeTensor[]>();
    const events: string[] = [];
    const firstOutputs = [
      output([0, 1], [1, 2]),
      output([0.25], [1]),
    ];
    const first = native(async () => {
      events.push("forward first");
      return forward.promise;
    });
    first.load.mockImplementation(async () => {
      events.push("load first");
    });
    first.delete.mockImplementation(() => {
      events.push("delete first");
    });
    const second = native(async () => {
      events.push("forward second");
      return [output([1, 0, 2], [1, 3]), output([-0.5], [1])];
    });
    second.load.mockImplementation(async () => {
      events.push("load second");
    });
    second.delete.mockImplementation(() => events.push("delete second"));
    const factory = vi
      .fn()
      .mockImplementationOnce(() => first)
      .mockImplementationOnce(() => second);
    const runtime = createModelRuntime(factory);
    const firstSelection = modelSelection(2);
    const secondSelection = modelSelection(3);

    const firstRun = runtime.execute(
      firstSelection,
      new Float32Array([1, 2]),
    );
    await vi.waitFor(() => expect(first.forward).toHaveBeenCalledOnce());

    const secondRun = runtime.execute(
      secondSelection,
      new Float32Array([1, 2]),
    );
    const disposal = runtime.dispose();

    forward.resolve(firstOutputs);
    await expect(firstRun).resolves.toEqual({
      selectedAction: 1,
      predictedFee: expect.closeTo(predictedFee(0.25)),
    });
    await expect(secondRun).resolves.toEqual({
      selectedAction: 2,
      predictedFee: expect.closeTo(predictedFee(-0.5)),
    });
    await disposal;
    expect(events).toEqual([
      "load first",
      "forward first",
      "delete first",
      "load second",
      "forward second",
      "delete second",
    ]);
    expect(() =>
      runtime.execute(firstSelection, new Float32Array([1, 2])),
    ).toThrow("Model runtime is disposed");
    await expect(runtime.dispose()).resolves.toBeUndefined();
  });

  it("retries with a fresh module after a load failure", async () => {
    const failed = native();
    failed.load.mockRejectedValueOnce(new Error("load failed"));
    const loaded = native();
    const factory = vi
      .fn()
      .mockImplementationOnce(() => failed)
      .mockImplementationOnce(() => loaded);
    const runtime = createModelRuntime(factory);
    const selected = modelSelection(2);
    const input = new Float32Array([1, 2]);

    await expect(runtime.execute(selected, input)).rejects.toThrow(
      "load failed",
    );
    await expect(runtime.execute(selected, input)).resolves.toEqual({
      selectedAction: 1,
      predictedFee: expect.closeTo(predictedFee(0.25)),
    });
    expect(loaded.load).toHaveBeenCalledOnce();
    await runtime.dispose();
    expect(loaded.delete).toHaveBeenCalledOnce();
  });

  it.each([
    {
      name: "output count",
      outputs: [output([0, 1], [1, 2])],
      message: "exactly two",
    },
    {
      name: "logit scalar type",
      outputs: [output([0, 1], [1, 2], 3), output([0], [1])],
      message: "float32",
    },
    {
      name: "logit shape",
      outputs: [output([0, 1], [2]), output([0], [1])],
      message: "shape [1, 2]",
    },
    {
      name: "minimum scalar type",
      outputs: [output([0, 1], [1, 2]), output([0], [1], 3)],
      message: "float32",
    },
    {
      name: "minimum shape",
      outputs: [output([0, 1], [1, 2]), output([0], [1, 1])],
      message: "shape [1]",
    },
    {
      name: "finite values",
      outputs: [output([0, Number.NaN], [1, 2]), output([0], [1])],
      message: "finite",
    },
  ])("rejects invalid $name", async ({ outputs, message }) => {
    const module = native(async () => outputs);
    const runtime = createModelRuntime(() => module);

    await expect(
      runtime.execute(
        modelSelection(2),
        new Float32Array([1, 2]),
      ),
    ).rejects.toThrow(message);
    await runtime.dispose();
  });

  it("selects the first action when maximum logits tie", async () => {
    const module = native(async () => [
      output([1, 4, 4, 0], [1, 4]),
      output([0], [1]),
    ]);
    const runtime = createModelRuntime(() => module);

    await expect(
      runtime.execute(modelSelection(4), new Float32Array([1, 2])),
    ).resolves.toEqual({
      selectedAction: 1,
      predictedFee: expect.closeTo(100),
    });
    await runtime.dispose();
  });

  it("rejects decoded fee overflow", async () => {
    const module = native(async () => [
      output([0, 1], [1, 2]),
      output([2_000], [1]),
    ]);
    const runtime = createModelRuntime(() => module);

    await expect(
      runtime.execute(modelSelection(2), new Float32Array([1, 2])),
    ).rejects.toThrow("Predicted fee must be positive and finite");
    await runtime.dispose();
  });
});
