import { beforeEach, describe, expect, it, vi } from "vitest";

import type { InferenceOutcome } from "../src/inference";
import { deferred, inferenceResult, inferenceRun } from "./helpers";

const storage = vi.hoisted(() => ({
  getItem: vi.fn(),
  setItem: vi.fn(),
}));

vi.mock("@react-native-async-storage/async-storage", () => ({
  default: storage,
}));

import { createRunHistory } from "../src/history";

function outcome(
  overrides: Partial<InferenceOutcome> = {},
): InferenceOutcome {
  return {
    immediate_base_fee_per_gas: 12_000_000_000,
    selected_base_fee_per_gas: 10_000_000_000,
    ...overrides,
  };
}

function startHistory() {
  const history = createRunHistory();
  history.subscribe(() => undefined);
  return history;
}

beforeEach(() => {
  storage.getItem.mockReset().mockResolvedValue(null);
  storage.setItem.mockReset().mockResolvedValue(undefined);
});

describe("run history", () => {
  it("mints stable unique identity when each result enters the queue", async () => {
    const result = inferenceResult();
    const history = startHistory();

    await history.record(result);
    await history.record(result);

    expect(history.runs).toHaveLength(2);
    expect(history.runs[0]).toMatchObject({
      id: expect.any(String),
      ran_at: expect.any(String),
      ...result,
    });
    expect(history.runs[0].id).not.toBe(history.runs[1].id);
  });

  it("loads stored history before an early run write", async () => {
    const load = deferred<string | null>();
    const existing = inferenceRun({ id: "existing" });
    storage.getItem.mockReturnValueOnce(load.promise);
    const history = startHistory();

    const record = history.record(inferenceResult({ head_hash: "0xnew" }));
    expect(storage.setItem).not.toHaveBeenCalled();

    load.resolve(JSON.stringify([existing]));
    await record;

    expect(history.runs).toHaveLength(2);
    expect(history.runs[0]).toMatchObject({ head_hash: "0xnew" });
    expect(history.runs[1]).toEqual(existing);
    expect(storage.setItem).toHaveBeenCalledWith(
      "kairos.runs",
      JSON.stringify(history.runs),
    );
  });

  it("blocks writes after initial load failure", async () => {
    storage.getItem.mockRejectedValueOnce(new Error("Corrupt history"));
    const history = startHistory();

    await expect(history.record(inferenceResult())).rejects.toThrow(
      "Corrupt history",
    );
    expect(history.runs).toEqual([]);
    expect(history.storageError).toBe("Corrupt history");
    expect(storage.setItem).not.toHaveBeenCalled();
  });

  it("publishes only after save and preserves committed history on failure", async () => {
    const existing = inferenceRun({ id: "existing" });
    const save = deferred<void>();
    storage.getItem.mockResolvedValueOnce(JSON.stringify([existing]));
    storage.setItem.mockReturnValueOnce(save.promise);
    const history = startHistory();
    await vi.waitFor(() => expect(history.runs).toEqual([existing]));
    const committed = history.runs;

    const record = history.record(inferenceResult({ head_hash: "0xnew" }));
    await vi.waitFor(() => expect(storage.setItem).toHaveBeenCalledOnce());
    expect(history.runs).toBe(committed);

    save.reject(new Error("Storage unavailable"));
    await expect(record).rejects.toThrow("Storage unavailable");
    expect(history.runs).toBe(committed);
    expect(history.storageError).toBe("Storage unavailable");

    await history.record(inferenceResult({ head_hash: "0xretry" }));
    expect(storage.setItem).toHaveBeenCalledTimes(2);
    expect(history.runs[0]).toMatchObject({ head_hash: "0xretry" });
    expect(history.storageError).toBeNull();
  });

  it("serializes concurrent records and continues after rejection", async () => {
    const firstSave = deferred<void>();
    storage.setItem.mockReturnValueOnce(firstSave.promise);
    const history = startHistory();
    await vi.waitFor(() => expect(storage.getItem).toHaveBeenCalledOnce());

    const first = history.record(inferenceResult({ head_hash: "0xfirst" }));
    const second = history.record(inferenceResult({ head_hash: "0xsecond" }));
    await vi.waitFor(() => expect(storage.setItem).toHaveBeenCalledOnce());
    firstSave.reject(new Error("First save failed"));
    await expect(first).rejects.toThrow("First save failed");
    await second;

    expect(storage.setItem).toHaveBeenCalledTimes(2);
    expect(history.runs).toHaveLength(1);
    expect(history.runs[0]).toMatchObject({ head_hash: "0xsecond" });
  });

  it("commits concurrent successful records in FIFO order", async () => {
    const firstSave = deferred<void>();
    storage.setItem.mockReturnValueOnce(firstSave.promise);
    const history = startHistory();
    await vi.waitFor(() => expect(storage.getItem).toHaveBeenCalledOnce());

    const first = history.record(inferenceResult({ head_hash: "0xfirst" }));
    const second = history.record(inferenceResult({ head_hash: "0xsecond" }));
    await vi.waitFor(() => expect(storage.setItem).toHaveBeenCalledOnce());
    firstSave.resolve();
    await first;
    await second;

    expect(storage.setItem).toHaveBeenCalledTimes(2);
    expect(history.runs).toHaveLength(2);
    expect(history.runs[0]).toMatchObject({ head_hash: "0xsecond" });
    expect(history.runs[1]).toMatchObject({ head_hash: "0xfirst" });
  });

  it("keeps no-op pending resolution as the original array without saving", async () => {
    const future = inferenceRun({
      id: "future",
      head_block: 20,
      target_block: 25,
    });
    const otherChain = inferenceRun({ id: "polygon", chain: "polygon" });
    const complete = inferenceRun({ id: "complete", outcome: outcome() });
    storage.getItem.mockResolvedValueOnce(
      JSON.stringify([future, otherChain, complete]),
    );
    const history = startHistory();
    await vi.waitFor(() => expect(history.runs).toHaveLength(3));
    const committed = history.runs;
    storage.setItem.mockClear();

    const resolve = vi.fn();
    await history.resolvePending("ethereum", 24, resolve);

    expect(history.runs).toBe(committed);
    expect(storage.setItem).not.toHaveBeenCalled();
    expect(resolve).not.toHaveBeenCalled();
  });

  it("commits successful outcomes while failed and future siblings remain retryable", async () => {
    const failed = inferenceRun({
      id: "failed",
      head_block: 10,
      target_block: 12,
    });
    const successful = inferenceRun({
      id: "successful",
      head_block: 20,
      target_block: 22,
    });
    const future = inferenceRun({
      id: "future",
      head_block: 30,
      target_block: 35,
    });
    storage.getItem.mockResolvedValueOnce(
      JSON.stringify([failed, successful, future]),
    );
    const history = startHistory();
    await vi.waitFor(() => expect(history.runs).toHaveLength(3));
    const resolve = vi
      .fn()
      .mockRejectedValueOnce(new Error("RPC unavailable"))
      .mockResolvedValue(outcome());

    await history.resolvePending("ethereum", 22, resolve);
    expect(history.runs[0]).toMatchObject({ id: "failed" });
    expect(history.runs[0].outcome).toBeUndefined();
    expect(history.runs[1]).toEqual({ ...successful, outcome: outcome() });
    expect(history.runs[2]).toMatchObject({ id: "future" });
    expect(history.runs[2].outcome).toBeUndefined();

    await history.resolvePending("ethereum", 35, resolve);
    expect(history.runs[0].outcome).toBeDefined();
    expect(history.runs[1].outcome).toBeDefined();
    expect(history.runs[2].outcome).toBeDefined();
    expect(storage.setItem).toHaveBeenCalledTimes(2);
  });
});
