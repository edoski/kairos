import { StrictMode, type ReactNode } from "react";
import {
  act,
  create,
  type ReactTestRenderer,
} from "react-test-renderer";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { AppTab } from "../src/components/BottomTabs";
import type { Chain, Horizon } from "../src/domain";
import type { InferenceRun, RunHistory } from "../src/history";
import type {
  InferenceRuntime,
  InferenceResult,
} from "../src/inference";
import {
  deferred,
  inferenceResult,
  inferenceRun,
} from "./helpers";

const mocks = vi.hoisted(() => ({
  analyticsProps: null as {
    chain: Chain;
    horizon: Horizon;
    onChainChange(chain: Chain): void;
    onHorizonChange(horizon: Horizon): void;
    onRefresh(): Promise<void>;
    runs: readonly InferenceRun[];
    storageError: string | null;
  } | null,
  bottomTabsProps: null as { onSelect(tab: AppTab): void } | null,
  createInferenceRuntime: vi.fn(),
  createRunHistory: vi.fn(),
  inferenceProps: null as {
    chain: Chain;
    horizon: Horizon;
    onChainChange(chain: Chain): void;
    onHorizonChange(horizon: Horizon): void;
    onRun(): void;
    state: Record<string, unknown>;
  } | null,
}));

vi.mock("react-native", () => {
  const View = ({ children }: { children?: ReactNode }) => children ?? null;
  return {
    StatusBar: () => null,
    StyleSheet: { create: <T,>(styles: T) => styles },
    View,
  };
});

vi.mock("react-native-safe-area-context", () => {
  const View = ({ children }: { children?: ReactNode }) => children ?? null;
  return {
    SafeAreaProvider: View,
    SafeAreaView: View,
  };
});

vi.mock("../src/components/BottomTabs", () => ({
  BottomTabs: (props: NonNullable<typeof mocks.bottomTabsProps>) => {
    mocks.bottomTabsProps = props;
    return null;
  },
}));

vi.mock("../src/screens/AnalyticsScreen", () => ({
  AnalyticsScreen: (props: NonNullable<typeof mocks.analyticsProps>) => {
    mocks.analyticsProps = props;
    return null;
  },
}));

vi.mock("../src/screens/InferenceScreen", () => ({
  InferenceScreen: (props: NonNullable<typeof mocks.inferenceProps>) => {
    mocks.inferenceProps = props;
    return null;
  },
}));

vi.mock("../src/history", () => ({
  createRunHistory: mocks.createRunHistory,
}));

vi.mock("../src/inference", () => ({
  createInferenceRuntime: mocks.createInferenceRuntime,
}));

import App from "../App";

type RuntimeHarness = {
  runtime: InferenceRuntime;
  rejectRun(index: number, error: unknown): void;
  resolveRun(index: number, result: InferenceResult): void;
};

type HistoryHarness = {
  owner: RunHistory;
  publish(
    runs: readonly InferenceRun[],
    storageError?: string | null,
  ): void;
};

const runtimes: RuntimeHarness[] = [];
let history: HistoryHarness;
let root: ReactTestRenderer | null = null;

function runtime(): RuntimeHarness {
  const pending: Array<ReturnType<typeof deferred<InferenceResult>>> = [];
  const value: InferenceRuntime = {
    currentHead: vi.fn(async (_chain) => 100),
    run: vi.fn((_chain, _horizon) => {
      const request = deferred<InferenceResult>();
      pending.push(request);
      return request.promise;
    }),
    resolveOutcome: vi.fn(async (_chain, _immediate, _selected) => {
      throw new Error("unused");
    }),
    dispose: vi.fn(async () => undefined),
  };
  return {
    runtime: value,
    rejectRun(index, error) {
      pending[index].reject(error);
    },
    resolveRun(index, result) {
      pending[index].resolve(result);
    },
  };
}

function runHistory(): HistoryHarness {
  let runs: readonly InferenceRun[] = [];
  let storageError: string | null = null;
  const listeners = new Set<() => void>();
  const owner: RunHistory = {
    get runs() {
      return runs;
    },
    get storageError() {
      return storageError;
    },
    record: vi.fn(async (result) => {
      runs = [inferenceRun({ ...result, id: `run-${runs.length}` }), ...runs];
      listeners.forEach((listener) => listener());
    }),
    resolvePending: vi.fn(async () => undefined),
    subscribe: vi.fn((listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    }),
  };
  return {
    owner,
    publish(nextRuns, nextStorageError = storageError) {
      runs = nextRuns;
      storageError = nextStorageError;
      listeners.forEach((listener) => listener());
    },
  };
}

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  runtimes.length = 0;
  history = runHistory();
  mocks.analyticsProps = null;
  mocks.bottomTabsProps = null;
  mocks.inferenceProps = null;
  mocks.createRunHistory.mockReset().mockReturnValue(history.owner);
  mocks.createInferenceRuntime.mockReset().mockImplementation(() => {
    const created = runtime();
    runtimes.push(created);
    return created.runtime;
  });
});

afterEach(async () => {
  if (root !== null) {
    await act(async () => root?.unmount());
    root = null;
  }
});

async function renderApp(strict = false): Promise<void> {
  await act(async () => {
    root = create(
      strict ? (
        <StrictMode>
          <App />
        </StrictMode>
      ) : (
        <App />
      ),
    );
  });
}

describe("App inference presentation", () => {
  it("keeps the newer selection and run on screen while both results record", async () => {
    const older = inferenceResult({ head_block: 10 });
    const newer = inferenceResult({ chain: "polygon", head_block: 20 });
    await renderApp();

    act(() => mocks.inferenceProps!.onRun());
    act(() => mocks.inferenceProps!.onChainChange("polygon"));
    act(() => mocks.inferenceProps!.onRun());
    await act(async () => runtimes[0].resolveRun(1, newer));
    expect(mocks.inferenceProps!.chain).toBe("polygon");
    expect(mocks.inferenceProps!.state).toEqual({
      status: "success",
      result: newer,
    });

    await act(async () => runtimes[0].resolveRun(0, older));
    expect(history.owner.record).toHaveBeenNthCalledWith(1, newer);
    expect(history.owner.record).toHaveBeenNthCalledWith(2, older);
    expect(mocks.inferenceProps!.state).toEqual({
      status: "success",
      result: newer,
    });
  });

  it("does nothing for same-value selection changes", async () => {
    const result = inferenceResult();
    await renderApp();
    act(() => mocks.inferenceProps!.onRun());
    act(() => {
      mocks.inferenceProps!.onChainChange("ethereum");
      mocks.inferenceProps!.onHorizonChange(5);
    });

    await act(async () => runtimes[0].resolveRun(0, result));
    expect(mocks.inferenceProps!.state).toEqual({
      status: "success",
      result,
    });
  });

  it("publishes only current-generation errors", async () => {
    await renderApp();
    act(() => mocks.inferenceProps!.onRun());
    act(() => mocks.inferenceProps!.onChainChange("polygon"));

    await act(async () =>
      runtimes[0].rejectRun(0, new Error("Old failure")),
    );
    expect(mocks.inferenceProps!.state).toEqual({ status: "idle" });
  });

  it("keeps stale save failures out of inference presentation", async () => {
    const save = deferred<void>();
    vi.mocked(history.owner.record).mockReturnValueOnce(save.promise);
    await renderApp();
    act(() => mocks.inferenceProps!.onRun());
    act(() => runtimes[0].resolveRun(0, inferenceResult()));
    await vi.waitFor(() =>
      expect(history.owner.record).toHaveBeenCalledOnce(),
    );

    act(() => mocks.inferenceProps!.onChainChange("polygon"));
    await act(async () => {
      history.publish([], "Storage unavailable");
      save.reject(new Error("Storage unavailable"));
      await Promise.resolve();
    });
    expect(mocks.inferenceProps!.state).toEqual({ status: "idle" });

    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.storageError).toBe("Storage unavailable");
  });
});

describe("App owners", () => {
  it("creates one runtime lazily and disposes it once", async () => {
    await renderApp(true);

    expect(runtimes).toHaveLength(0);

    act(() => {
      mocks.inferenceProps!.onRun();
      mocks.inferenceProps!.onRun();
    });
    expect(runtimes).toHaveLength(1);
    expect(runtimes[0].runtime.run).toHaveBeenCalledTimes(2);

    await act(async () => root?.unmount());
    root = null;
    expect(runtimes[0].runtime.dispose).toHaveBeenCalledOnce();
  });

  it("uses the current inference error path for runtime construction failure", async () => {
    mocks.createInferenceRuntime.mockImplementationOnce(() => {
      throw new Error("Native setup failed");
    });
    await renderApp();

    act(() => mocks.inferenceProps!.onRun());
    expect(mocks.inferenceProps!.state).toEqual({
      message: "Native setup failed",
      status: "error",
    });
  });

  it("shows load and save failures through one history error", async () => {
    await renderApp();
    act(() => history.publish([], "Corrupt history"));
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.storageError).toBe("Corrupt history");

    act(() => mocks.bottomTabsProps!.onSelect("inference"));
    vi.mocked(history.owner.record).mockImplementationOnce(async () => {
      history.publish([], "Storage unavailable");
      throw new Error("Storage unavailable");
    });
    act(() => mocks.inferenceProps!.onRun());
    await act(async () =>
      runtimes[0].resolveRun(0, inferenceResult()),
    );
    expect(mocks.inferenceProps!.state).toEqual({
      message: "Could not save this run.",
      status: "error",
    });

    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.storageError).toBe("Storage unavailable");
  });
});

describe("App outcome refresh and global selection", () => {
  it("finishes refresh for its captured chain after selection changes", async () => {
    const head = deferred<number>();
    const created = runtime();
    vi.mocked(created.runtime.currentHead).mockReturnValueOnce(head.promise);
    mocks.createInferenceRuntime.mockImplementationOnce(() => {
      runtimes.push(created);
      return created.runtime;
    });
    await renderApp();
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    const refresh = mocks.analyticsProps!.onRefresh();
    act(() => {
      mocks.analyticsProps!.onChainChange("polygon");
      mocks.analyticsProps!.onHorizonChange(4);
    });
    expect(mocks.analyticsProps).toMatchObject({
      chain: "polygon",
      horizon: 4,
    });

    await act(async () => {
      head.resolve(100);
      await refresh;
    });
    expect(history.owner.resolvePending).toHaveBeenCalledWith(
      "ethereum",
      100,
      expect.any(Function),
    );
    const resolver = vi.mocked(history.owner.resolvePending).mock.calls[0][2];
    await expect(resolver(101, 102)).rejects.toThrow("unused");
    expect(runtimes[0].runtime.resolveOutcome).toHaveBeenCalledWith(
      "ethereum",
      101,
      102,
    );
  });

  it("keeps Analytics horizon global across tab remounts", async () => {
    await renderApp();
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    act(() => mocks.analyticsProps!.onHorizonChange(3));
    expect(mocks.analyticsProps!.horizon).toBe(3);

    act(() => mocks.bottomTabsProps!.onSelect("inference"));
    expect(mocks.inferenceProps!.horizon).toBe(3);
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.horizon).toBe(3);
  });
});
