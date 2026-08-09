import type { ReactNode } from "react";
import {
  act,
  create,
  type ReactTestRenderer,
} from "react-test-renderer";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { AppTab } from "../src/components/BottomTabs";
import type { Chain, Horizon } from "../src/domain";
import type {
  InferenceEngine,
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
  createInferenceEngine: vi.fn(),
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
  createInferenceEngine: mocks.createInferenceEngine,
}));

import App from "../App";

type EngineHarness = {
  engine: InferenceEngine;
  resolveRun(result: InferenceResult): void;
};

const engines: EngineHarness[] = [];
let root: ReactTestRenderer | null = null;

function engine(): EngineHarness {
  const run = deferred<InferenceResult>();
  const value: InferenceEngine = {
    currentHead: vi.fn(async () => 100),
    run: vi.fn(() => run.promise),
    resolveOutcome: vi.fn(async () => {
      throw new Error("unused");
    }),
    dispose: vi.fn(async () => undefined),
  };
  return {
    engine: value,
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
  engines.length = 0;
  mocks.analyticsProps = null;
  mocks.bottomTabsProps = null;
  mocks.inferenceProps = null;
  mocks.addRun.mockReset();
  mocks.loadRuns.mockReset().mockResolvedValue([]);
  mocks.resolvePendingRuns.mockReset().mockResolvedValue([]);
  mocks.saveRuns.mockReset().mockResolvedValue(undefined);
  mocks.createInferenceEngine.mockReset().mockImplementation(() => {
    const created = engine();
    engines.push(created);
    return created.engine;
  });
});

afterEach(async () => {
  if (root !== null) {
    await act(async () => root?.unmount());
    root = null;
  }
});

async function renderApp(): Promise<void> {
  await act(async () => {
    root = create(<App />);
  });
}

describe("App engine selection", () => {
  it("applies the latest selection after an accepted history commit", async () => {
    const result = inferenceResult();
    const acceptedRun = inferenceRun();
    const firstSave = deferred<void>();
    mocks.addRun.mockReturnValue([acceptedRun]);
    mocks.saveRuns.mockImplementationOnce(() => firstSave.promise);
    await renderApp();

    act(() => mocks.inferenceProps!.onRun());
    expect(engines[0].engine.run).toHaveBeenCalledWith(5);

    act(() => engines[0].resolveRun(result));
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
    expect(engines).toHaveLength(1);

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
    expect(engines).toHaveLength(1);
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));
    expect(mocks.analyticsProps!.runs).toEqual([acceptedRun]);
  });

  it("does not publish a result from a replaced engine", async () => {
    const result = inferenceResult();
    await renderApp();
    act(() => mocks.inferenceProps!.onRun());
    vi.mocked(engines[0].engine.dispose).mockRejectedValueOnce(
      new Error("native disposal failed"),
    );

    await act(async () => {
      mocks.inferenceProps!.onChainChange("polygon");
      await flushMicrotasks();
    });
    expect(mocks.inferenceProps!.chain).toBe("polygon");
    expect(engines).toHaveLength(2);
    expect(engines[0].engine.dispose).toHaveBeenCalledOnce();

    await act(async () => {
      engines[0].resolveRun(result);
      await flushMicrotasks();
    });

    expect(mocks.inferenceProps!.state).toEqual({ status: "idle" });
    expect(mocks.addRun).not.toHaveBeenCalled();
    expect(mocks.saveRuns).not.toHaveBeenCalled();
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
      engines[0].resolveRun(result);
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
  it("reads the applied engine head and saves resolved runs before publishing", async () => {
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

    expect(engines[0].engine.currentHead).toHaveBeenCalledOnce();
    expect(mocks.resolvePendingRuns).toHaveBeenCalledWith(
      [pending],
      "ethereum",
      100,
      engines[0].engine.resolveOutcome,
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

    expect(engines[0].engine.currentHead).toHaveBeenCalledOnce();
    expect(mocks.saveRuns).not.toHaveBeenCalled();
    expect(mocks.analyticsProps!.runs).toEqual([pending]);
  });

  it("does not resolve or publish after the selected engine changes", async () => {
    const head = deferred<number>();
    await renderApp();
    vi.mocked(engines[0].engine.currentHead).mockReturnValueOnce(head.promise);
    act(() => mocks.bottomTabsProps!.onSelect("analytics"));

    const refresh = mocks.analyticsProps!.onRefresh();
    await act(async () => {
      mocks.analyticsProps!.onChainChange("polygon");
      await flushMicrotasks();
    });
    expect(mocks.analyticsProps!.chain).toBe("polygon");
    expect(engines).toHaveLength(2);

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
