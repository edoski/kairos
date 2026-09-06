import {
  ScalarType,
  initExecutorch,
} from "react-native-executorch";
import type { ExecutorchModule, TensorPtr } from "react-native-executorch";
import { ExpoResourceFetcher } from "react-native-executorch-expo-resource-fetcher";

import type { ModelSelection } from "./bundledModels";

export type ModelPrediction = {
  selectedAction: number;
  predictedFee: number;
};

type NativeModule = Pick<ExecutorchModule, "forward">;

initExecutorch({ resourceFetcher: ExpoResourceFetcher });

export async function executeModel(
  module: NativeModule,
  selection: ModelSelection,
  input: Float32Array,
): Promise<ModelPrediction> {
  const outputs = await module.forward([
    {
      dataPtr: input,
      sizes: [
        1,
        selection.chainManifest.context_blocks,
        selection.chainManifest.features.length,
      ],
      scalarType: ScalarType.FLOAT,
    },
  ]);
  return decodeOutputs(outputs, selection);
}

function decodeOutputs(
  outputs: readonly TensorPtr[],
  selection: ModelSelection,
): ModelPrediction {
  if (outputs.length !== 2) {
    throw new Error(
      "ExecuTorch model must return exactly two float32 tensors",
    );
  }
  const actionLogits = readFloatTensor(
    outputs[0],
    [1, selection.K],
    "action logits",
  );
  const minimumFee = readFloatTensor(
    outputs[1],
    [1],
    "minimum fee z",
  );
  if (!actionLogits.every(Number.isFinite)) {
    throw new Error("action logits output values must be finite");
  }
  const selectedAction = actionLogits.indexOf(Math.max(...actionLogits));
  const target = selection.modelManifest.target;
  const predictedFee = Math.exp(
    target.mean + target.standard_deviation * minimumFee[0],
  );
  if (!Number.isFinite(predictedFee) || predictedFee <= 0) {
    throw new Error("Predicted fee must be positive and finite");
  }
  return { selectedAction, predictedFee };
}

function readFloatTensor(
  tensor: TensorPtr,
  shape: readonly number[],
  label: string,
): Float32Array {
  if (tensor.scalarType !== ScalarType.FLOAT) {
    throw new Error(`${label} output must be float32`);
  }
  if (
    tensor.sizes.length !== shape.length ||
    tensor.sizes.some((size, index) => size !== shape[index])
  ) {
    throw new Error(
      `${label} output must have shape [${shape.join(", ")}]`,
    );
  }
  return new Float32Array(tensor.dataPtr as ArrayBuffer);
}
