import { StrictMode, type ComponentProps, type ReactNode } from "react";
import {
  act,
  create,
  type ReactTestRenderer,
} from "react-test-renderer";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { BottomTabs } from "../src/components/BottomTabs";
import type { AnalyticsScreen } from "../src/screens/AnalyticsScreen";
import type { InferenceScreen } from "../src/screens/InferenceScreen";
import type { RunHistory } from "../src/history";
import type {
  InferenceResult,
} from "../src/inference";
import {
  deferred,
  inferenceResult,
  inferenceRun,
} from "./helpers";

const mocks = vi.hoisted(() => ({
  analyticsProps: null as ComponentProps<typeof AnalyticsScreen> | null,
  bottomTabsProps: null as ComponentProps<typeof BottomTabs> | null,
  infer: vi.fn(),
  currentHead: vi.fn(),
  resolveOutcome: vi.fn(),
  createRunHistory: vi.fn(),
  inferenceProps: null as ComponentProps<typeof InferenceScreen> | null,
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
  infer: mocks.infer,
  currentHead: mocks.currentHead,
  resolveOutcome: mocks.resolveOutcome,
}));

import App from "../App";

let history: RunHistory;
let root: ReactTestRenderer | null = null;
const pending: Array<ReturnType<typeof deferred<InferenceResult>>> = [];

function runHistory(): RunHistory {
  let snapshot: ReturnType<RunHistory["getSnapshot"]> = { runs: [], storageError: null };
  const listeners = new Set<() => void>();
  return {
    getSnapshot: () => snapshot,
    record: vi.fn(async (result) => {
      const runs = snapshot.runs;
      snapshot = { runs: [inferenceRun({ ...result, id: `run-${runs.length}` }), ...runs], storageError: null };
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
  pending.length = 0;
  history = runHistory();
  mocks.analyticsProps = null;
  mocks.bottomTabsProps = null;
  mocks.inferenceProps = null;
  mocks.createRunHistory.mockReset().mockReturnValue(history);
  mocks.infer.mockReset().mockImplementation(() => {
    const request = deferred<InferenceResult>();
    pending.push(request);
    return request.promise;
  });
  mocks.currentHead.mockReset().mockResolvedValue(100);
  mocks.resolveOutcome.mockReset().mockRejectedValue(new Error("unused"));
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
    await act(async () => pending[1].resolve(newer));
    expect(mocks.inferenceProps!.chain).toBe("polygon");
    expect(mocks.inferenceProps!.state).toEqual({
      status: "success",
      result: newer,
    });

    await act(async () => pending[0].resolve(older));
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

    await act(async () => pending[0].resolve(result));
    expect(mocks.inferenceProps!.state).toEqual({
      status: "success",
      result,
    });
  });

});

describe("App outcome refresh and global selection", () => {
  it("finishes refresh for its captured chain after selection changes", async () => {
    const head = deferred<number>();
    mocks.currentHead.mockReturnValueOnce(head.promise);
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
    expect(mocks.resolveOutcome).toHaveBeenCalledWith(
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
