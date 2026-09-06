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

import { executeModel } from "../src/model";
import { modelSelection } from "./helpers";

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
  it("builds the float32 input tensor and decodes ordinary numbers", async () => {
    const module = native();
    const input = new Float32Array([1, 2]);
    await expect(executeModel(module, modelSelection(2), input)).resolves.toEqual({
      selectedAction: 1,
      predictedFee: expect.closeTo(predictedFee(0.25)),
    });
    expect(module.forward).toHaveBeenCalledWith([
      { dataPtr: input, sizes: [1, 2, 1], scalarType: 6 },
    ]);
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

    await expect(
      executeModel(
        module,
        modelSelection(2),
        new Float32Array([1, 2]),
      ),
    ).rejects.toThrow(message);
  });

  it("selects the first action when maximum logits tie", async () => {
    const module = native(async () => [
      output([1, 4, 4, 0], [1, 4]),
      output([0], [1]),
    ]);

    await expect(
      executeModel(module, modelSelection(4), new Float32Array([1, 2])),
    ).resolves.toEqual({
      selectedAction: 1,
      predictedFee: expect.closeTo(100),
    });
  });

  it.each([NaN, Infinity, -Infinity, 2_000, -2_000])("rejects invalid decoded fee from z=%s", async (z) => {
    const module = native(async () => [
      output([0, 1], [1, 2]),
      output([z], [1]),
    ]);

    await expect(
      executeModel(module, modelSelection(2), new Float32Array([1, 2])),
    ).rejects.toThrow("Predicted fee must be positive and finite");
  });
});
