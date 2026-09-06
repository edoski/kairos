import { createElement, type ComponentProps, type PropsWithChildren } from "react";
import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import type { BottomTabs } from "../src/components/BottomTabs";
import type { NetworkChoices } from "../src/components/NetworkChoices";
import { deferred } from "./helpers";

const mocks = vi.hoisted(() => ({
  head: vi.fn(),
  tabs: null as ComponentProps<typeof BottomTabs> | null,
  network: null as ComponentProps<typeof NetworkChoices> | null,
  snapshot: { runs: [], storageError: null },
}));
vi.mock("react-native", () => {
  const Container = ({ children }: PropsWithChildren) => children ?? null;
  return { ActivityIndicator: () => null, StatusBar: () => null,
    Pressable: (props: PropsWithChildren) => createElement("button", props),
    ScrollView: Container, Text: Container, View: Container,
    StyleSheet: { create: <T,>(value: T) => value } };
});
vi.mock("react-native-safe-area-context", () => ({
  SafeAreaProvider: ({ children }: PropsWithChildren) => children,
  SafeAreaView: ({ children }: PropsWithChildren) => children,
}));
vi.mock("@expo/vector-icons", () => ({ Ionicons: () => null }));
vi.mock("../src/components/NetworkChoices", () => ({ NetworkChoices: (props: ComponentProps<typeof NetworkChoices>) => { mocks.network = props; return null; } }));
vi.mock("../src/components/BottomTabs", () => ({ BottomTabs: (props: ComponentProps<typeof BottomTabs>) => { mocks.tabs = props; return null; } }));
vi.mock("../src/components/HorizonChoices", () => ({ HorizonChoices: () => null }));
vi.mock("../src/screens/InferenceScreen", () => ({ InferenceScreen: () => null }));
vi.mock("../src/screens/AnalyticsCharts", () => ({ AnalyticsCharts: () => null }));
vi.mock("../src/screens/RunDetails", () => ({ RunDetails: () => null }));
vi.mock("../src/inference", () => ({ infer: vi.fn(), currentHead: mocks.head, resolveOutcome: vi.fn() }));
vi.mock("../src/history", () => ({ createRunHistory: () => ({
  getSnapshot: () => mocks.snapshot, subscribe: () => () => {},
  record: vi.fn(), resolvePending: vi.fn(),
}) }));
import App from "../App";
let root: ReactTestRenderer;
beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.head.mockReset();
});
afterEach(async () => { await act(async () => root?.unmount()); });

it("isolates actual Analytics refresh feedback when App switches networks", async () => {
  const refresh = deferred<number>();
  mocks.head.mockReturnValueOnce(refresh.promise);
  await act(async () => { root = create(<App />); });
  act(() => mocks.tabs!.onSelect("analytics"));
  act(() => root.root.findByType("button").props.onPress());
  expect(root.root.findByType("button").props.disabled).toBe(true);
  act(() => mocks.network!.onChange("polygon"));
  expect(root.root.findByType("button").props.disabled).toBe(false);
  await act(async () => refresh.reject(new Error("Ethereum refresh failed")));
  expect(JSON.stringify(root.toJSON())).not.toContain("Ethereum refresh failed");
});
