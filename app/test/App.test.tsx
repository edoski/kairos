import { StrictMode, type ReactNode } from "react";
import {
  act,
  create,
  type ReactTestRenderer,
} from "react-test-renderer";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { AppTab } from "../src/components/BottomTabs";
import type { Chain, Horizon } from "../src/domain";
import type {
  InferenceRuntime,
  InferenceResult,
} from "../src/inference";
import {
  deferred,
  flushMicrotasks,
  inferenceResult,
  inferenceRun,
} from "./helpers";

const mocks = vi.hoisted(() => ({
  addRun: vi.fn(),
  analyticsProps: null as {
    chain: Chain;
    loadError: string | null;
    onChainChange(chain: Chain): void;
    onRefresh(): Promise<void>;
    runs: readonly ReturnType<typeof inferenceRun>[];
  } | null,
  bottomTabsProps: null as { onSelect(tab: AppTab): void } | null,
  createInferenceRuntime: vi.fn(),
  inferenceProps: null as {
    chain: Chain;
    horizon: Horizon;
    onChainChange(chain: Chain): void;
    onHorizonChange(horizon: Horizon): void;
    onRun(): void;
    state: Record<string, unknown>;
  } | null,
  loadRuns: vi.fn(),
  resolvePendingRuns: vi.fn(),
  saveRuns: vi.fn(),
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
  addRun: mocks.addRun,
  loadRuns: mocks.loadRuns,
  resolvePendingRuns: mocks.resolvePendingRuns,
  saveRuns: mocks.saveRuns,
}));

vi.mock("../src/inference", () => ({
  createInferenceRuntime: mocks.createInferenceRuntime,
}));

import App from "../App";

type RuntimeHarness = {
  runtime: InferenceRuntime;
  resolveRun(result: InferenceResult): void;
};

const runtimes: RuntimeHarness[] = [];
let root: ReactTestRenderer | null = null;

function runtime(): RuntimeHarness {
  const run = deferred<InferenceResult>();
  const value: InferenceRuntime = {
    currentHead: vi.fn(async (_chain) => 100),
    run: vi.fn((_chain, _horizon) => run.promise),
    resolveOutcome: vi.fn(async (_chain, _immediate, _selected) => {
      throw new Error("unused");
    }),
    dispose: vi.fn(async () => undefined),
  };
  return {
    runtime: value,
    resolveRun(result) {
      run.resolve(result);
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
  mocks.analyticsProps = null;
  mocks.bottomTabsProps = null;
  mocks.inferenceProps = null;
  mocks.addRun.mockReset();
  mocks.loadRuns.mockReset().mockResolvedValue([]);
  mocks.resolvePendingRuns.mockReset().mockResolvedValue([]);
  mocks.saveRuns.mockReset().mockResolvedValue(undefined);
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

describe("App inference runtime", () => {
  it("applies the latest selection after an accepted history commit", async () => {
    const result = inferenceResult();
    const acceptedRun = inferenceRun();
    const firstSave = deferred<void>();
    mocks.addRun.mockReturnValue([acceptedRun]);
    mocks.saveRuns.mockImplementationOnce(() => firstSave.promise);
    await renderApp();

    act(() => mocks.inferenceProps!.onRun());
    expect(runtimes[0].runtime.run).toHaveBeenCalledWith("ethereum", 5);

    act(() => runtimes[0].resolveRun(result));
    await vi.waitFor(() => expect(mocks.saveRuns).toHaveBeenCalledOnce());
    expect(mocks.saveRuns).toHaveBeenLastCalledWith([acceptedRun]);

    act(() => {
      mocks.inferenceProps!.onChainChange("polygon");
      mocks.inferenceProps!.onHorizonChange(4);
      mocks.inferenceProps!.onChainChange("ethereum");
      mocks.inferenceProps!.onHorizonChange(5);
    });
    expect(mocks.inferenceProps).toMatchObject({
      chain: "ethereum",
      horizon: 5,
      state: { status: "loading" },
    });
    expect(runtimes).toHaveLength(1);

    await act(async () => {
      firstSave.resolve();
      await flushMicrotasks();
    });

    expect(mocks.saveRuns).toHaveBeenCalledOnce();
    expect(mocks.inferenceProps).toMatchObject({
      chain: "ethereum",
      horizon: 5,
      state: { status: "success", result },
    });
    expect(runtimes).toHaveLength(1);
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.runs).toEqual([acceptedRun]);
  });

  it("keeps one runtime across chain selection and rejects its stale result", async () => {
    const result = inferenceResult();
    await renderApp();
    act(() => mocks.inferenceProps!.onRun());

    await act(async () => {
      mocks.inferenceProps!.onChainChange("polygon");
      await flushMicrotasks();
    });
    expect(mocks.inferenceProps!.chain).toBe("polygon");
    expect(runtimes).toHaveLength(1);
    expect(runtimes[0].runtime.dispose).not.toHaveBeenCalled();

    await act(async () => {
      runtimes[0].resolveRun(result);
      await flushMicrotasks();
    });

    expect(mocks.inferenceProps!.state).toEqual({ status: "idle" });
    expect(mocks.addRun).not.toHaveBeenCalled();
    expect(mocks.saveRuns).not.toHaveBeenCalled();
  });

  it("uses a fresh live runtime after development setup-cleanup-setup", async () => {
    await renderApp(true);

    expect(runtimes).toHaveLength(2);
    expect(runtimes[0].runtime.dispose).toHaveBeenCalledOnce();
    expect(runtimes[1].runtime.dispose).not.toHaveBeenCalled();

    act(() => mocks.inferenceProps!.onRun());
    expect(runtimes[0].runtime.run).not.toHaveBeenCalled();
    expect(runtimes[1].runtime.run).toHaveBeenCalledWith("ethereum", 5);

    await act(async () => root?.unmount());
    root = null;
    expect(runtimes[0].runtime.dispose).toHaveBeenCalledOnce();
    expect(runtimes[1].runtime.dispose).toHaveBeenCalledOnce();
  });
});

describe("App history persistence", () => {
  it("reports initial history load failures in Analytics", async () => {
    mocks.loadRuns.mockRejectedValueOnce(new Error("Corrupt history"));
    await renderApp();

    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    expect(mocks.analyticsProps!.loadError).toBe("Corrupt history");
  });

  it("reports inference save failures only through the inference state", async () => {
    const result = inferenceResult();
    mocks.addRun.mockReturnValue([inferenceRun()]);
    mocks.saveRuns.mockRejectedValueOnce(new Error("Storage unavailable"));
    await renderApp();

    act(() => mocks.inferenceProps!.onRun());
    await act(async () => {
      runtimes[0].resolveRun(result);
      await flushMicrotasks();
    });

    expect(mocks.inferenceProps!.state).toEqual({
      message: "Could not save this run.",
      status: "error",
    });
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.loadError).toBeNull();
  });
});

describe("App outcome refresh", () => {
  it("reads the applied chain head and saves resolved runs before publishing", async () => {
    const pending = inferenceRun({ id: "pending" });
    const resolved = inferenceRun({
      id: pending.id,
      outcome: {
        immediate_base_fee_per_gas: 12_000_000_000,
        selected_base_fee_per_gas: 10_000_000_000,
      },
    });
    const save = deferred<void>();
    mocks.loadRuns.mockResolvedValueOnce([pending]);
    mocks.resolvePendingRuns.mockResolvedValueOnce([resolved]);
    mocks.saveRuns.mockImplementationOnce(() => save.promise);
    await renderApp();
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    let refresh!: Promise<void>;
    act(() => {
      refresh = mocks.analyticsProps!.onRefresh();
    });
    await vi.waitFor(() => expect(mocks.saveRuns).toHaveBeenCalledOnce());

    expect(runtimes[0].runtime.currentHead).toHaveBeenCalledWith(
      "ethereum",
    );
    expect(mocks.resolvePendingRuns).toHaveBeenCalledWith(
      [pending],
      "ethereum",
      100,
      expect.any(Function),
    );
    const resolveOutcome = mocks.resolvePendingRuns.mock.calls[0][3];
    await expect(resolveOutcome(101, 102)).rejects.toThrow("unused");
    expect(runtimes[0].runtime.resolveOutcome).toHaveBeenCalledWith(
      "ethereum",
      101,
      102,
    );
    expect(mocks.saveRuns).toHaveBeenCalledWith([resolved]);
    expect(mocks.analyticsProps!.runs).toEqual([pending]);

    await act(async () => {
      save.resolve();
      await refresh;
    });
    expect(mocks.analyticsProps!.runs).toEqual([resolved]);
  });

  it("does not save when refresh leaves every run unchanged", async () => {
    const pending = inferenceRun({ id: "pending" });
    mocks.loadRuns.mockResolvedValueOnce([pending]);
    mocks.resolvePendingRuns.mockResolvedValueOnce([pending]);
    await renderApp();
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    await act(async () => mocks.analyticsProps!.onRefresh());

    expect(runtimes[0].runtime.currentHead).toHaveBeenCalledWith(
      "ethereum",
    );
    expect(mocks.saveRuns).not.toHaveBeenCalled();
    expect(mocks.analyticsProps!.runs).toEqual([pending]);
  });

  it("does not resolve or publish after the selected chain changes", async () => {
    const head = deferred<number>();
    await renderApp();
    vi.mocked(runtimes[0].runtime.currentHead).mockReturnValueOnce(
      head.promise,
    );
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    const refresh = mocks.analyticsProps!.onRefresh();
    await act(async () => {
      mocks.analyticsProps!.onChainChange("polygon");
      await flushMicrotasks();
    });
    expect(mocks.analyticsProps!.chain).toBe("polygon");
    expect(runtimes).toHaveLength(1);

    await act(async () => {
      head.resolve(100);
      await refresh;
    });
    expect(mocks.resolvePendingRuns).not.toHaveBeenCalled();
    expect(mocks.saveRuns).not.toHaveBeenCalled();
  });

  it("rejects refresh when resolved runs cannot be saved", async () => {
    const pending = inferenceRun({ id: "pending" });
    const resolved = inferenceRun({
      id: pending.id,
      outcome: {
        immediate_base_fee_per_gas: 12_000_000_000,
        selected_base_fee_per_gas: 10_000_000_000,
      },
    });
    mocks.loadRuns.mockResolvedValueOnce([pending]);
    mocks.resolvePendingRuns.mockResolvedValueOnce([resolved]);
    mocks.saveRuns.mockRejectedValueOnce(new Error("Storage unavailable"));
    await renderApp();
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    await expect(mocks.analyticsProps!.onRefresh()).rejects.toThrow(
      "Storage unavailable",
    );
    expect(mocks.analyticsProps!.runs).toEqual([pending]);
  });
});
