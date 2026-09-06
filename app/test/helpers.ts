import type { Horizon } from "../src/domain";
import type { InferenceRun } from "../src/history";
import type { InferenceResult } from "../src/inference";
import type {
  ModelSelection,
} from "../src/bundledModels";

function modelEntry(): ModelSelection["modelManifest"] {
  return {
    target: { mean: Math.log(100), standard_deviation: 0.5 },
  };
}

export const chainManifest: ModelSelection["chainManifest"] = {
  context_blocks: 2,
  features: [
    {
      name: "log_base_fee_per_gas",
      mean: 0,
      standard_deviation: 1,
    },
  ],
  models: {
    2: modelEntry(),
    3: modelEntry(),
    4: modelEntry(),
    5: modelEntry(),
  },
};

export function modelSelection(K: Horizon): ModelSelection {
  return {
    K,
    source: 10 + K,
    chainManifest,
    modelManifest: chainManifest.models[K],
  };
}

export function inferenceResult(
  overrides: Partial<InferenceResult> = {},
): InferenceResult {
  return {
    chain: "ethereum",
    K: 5,
    head_block: 10,
    selected_action_k: 1,
    target_block: 12,
    predicted_minimum_base_fee_per_gas: 9_000_000_000,
    ...overrides,
  };
}

export function inferenceRun(
  overrides: Partial<InferenceRun> = {},
): InferenceRun {
  return {
    id: "run",
    ran_at: "2026-07-26T10:00:00.000Z",
    ...inferenceResult(),
    ...overrides,
  };
}

export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((next, fail) => {
    resolve = next;
    reject = fail;
  });
  return { promise, reject, resolve };
}
