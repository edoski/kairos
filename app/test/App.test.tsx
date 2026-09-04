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
  resolveRun(index: number, result: InferenceResult): void;
};

const runtimes: RuntimeHarness[] = [];
let history: RunHistory;
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
    resolveRun(index, result) {
      pending[index].resolve(result);
    },
  };
}

function runHistory(): RunHistory {
  let runs: readonly InferenceRun[] = [];
  const listeners = new Set<() => void>();
  return {
    get runs() {
      return runs;
    },
    get storageError() {
      return null;
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
  mocks.createRunHistory.mockReset().mockReturnValue(history);
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
    expect(history.record).toHaveBeenNthCalledWith(1, newer);
    expect(history.record).toHaveBeenNthCalledWith(2, older);
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
    expect(history.resolvePending).toHaveBeenCalledWith(
      "ethereum",
      100,
      expect.any(Function),
    );
    const resolver = vi.mocked(history.resolvePending).mock.calls[0][2];
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
