import AsyncStorage from "@react-native-async-storage/async-storage";

import type { Chain } from "./domain";
import type {
  InferenceOutcome,
  InferenceResult,
} from "./inference";
import { createSerialQueue } from "./serialQueue";

const STORAGE_KEY = "kairos.runs";

export type InferenceRun = InferenceResult & {
  id: string;
  ran_at: string;
  outcome?: InferenceOutcome;
};

/**
 * Serializes initial load and complete save-before-publish mutations.
 * Failed saves retain committed state; unresolved outcomes remain pending for retry.
 */
export type RunHistory = {
  readonly runs: readonly InferenceRun[];
  readonly storageError: string | null;
  record(result: InferenceResult): Promise<void>;
  resolvePending(
    chain: Chain,
    headBlock: number,
    resolver: (
      immediateBlock: number,
      selectedBlock: number,
    ) => Promise<InferenceOutcome>,
  ): Promise<void>;
  subscribe(listener: () => void): () => void;
};

let runSequence = 0;

export function createRunHistory(): RunHistory {
  let runs: readonly InferenceRun[] = [];
  let storageError: string | null = null;
  let started = false;
  let loaded = false;
  const listeners = new Set<() => void>();
  const enqueue = createSerialQueue();

  function publish(): void {
    listeners.forEach((listener) => listener());
  }

  function start(): void {
    if (started) return;
    started = true;
    void enqueue(async () => {
      try {
        runs = await loadRuns();
        loaded = true;
        storageError = null;
      } catch (error) {
        storageError = errorMessage(error);
      }
      publish();
    });
  }

  function update(
    transform: (
      current: readonly InferenceRun[],
    ) => readonly InferenceRun[] | Promise<readonly InferenceRun[]>,
  ): Promise<void> {
    start();
    return enqueue(async () => {
      if (!loaded) {
        throw new Error(storageError ?? "Could not load run history.");
      }

      const current = runs;
      const next = await transform(current);
      if (next === current) return;

      try {
        await saveRuns(next);
      } catch (error) {
        storageError = errorMessage(error);
        publish();
        throw error;
      }

      runs = next;
      storageError = null;
      publish();
    });
  }

  const history: RunHistory = {
    get runs() {
      return runs;
    },
    get storageError() {
      return storageError;
    },
    record(result) {
      return update((current) => addRun(current, result));
    },
    resolvePending(chain, headBlock, resolver) {
      return update((current) =>
        resolvePendingRuns(current, chain, headBlock, resolver),
      );
    },
    subscribe(listener) {
      listeners.add(listener);
      start();
      return () => listeners.delete(listener);
    },
  };
  return history;
}

function addRun(
  runs: readonly InferenceRun[],
  result: InferenceResult,
): InferenceRun[] {
  const ranAt = new Date().toISOString();
  runSequence += 1;
  return [
    {
      id: `${ranAt}:${runSequence}`,
      ran_at: ranAt,
      ...result,
    },
    ...runs,
  ];
}

async function resolvePendingRuns(
  runs: readonly InferenceRun[],
  chain: Chain,
  headBlock: number,
  resolveOutcome: (
    immediateBlock: number,
    selectedBlock: number,
  ) => Promise<InferenceOutcome>,
): Promise<readonly InferenceRun[]> {
  let changed = false;
  const resolved = await Promise.all(
    runs.map(async (run) => {
      if (
        run.chain !== chain ||
        run.outcome !== undefined ||
        run.target_block > headBlock
      ) {
        return run;
      }
      try {
        const outcome = await resolveOutcome(
          run.head_block + 1,
          run.target_block,
        );
        changed = true;
        return { ...run, outcome };
      } catch {
        return run;
      }
    }),
  );
  return changed ? resolved : runs;
}

async function loadRuns(): Promise<InferenceRun[]> {
  const stored = await AsyncStorage.getItem(STORAGE_KEY);
  return stored === null ? [] : (JSON.parse(stored) as InferenceRun[]);
}

function saveRuns(runs: readonly InferenceRun[]): Promise<void> {
  return AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(runs));
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
