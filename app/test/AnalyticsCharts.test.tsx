import { createElement, type PropsWithChildren } from "react";
import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

vi.mock("react-native", () => {
  const Container = ({ children }: PropsWithChildren) => children ?? null;
  return {
    Text: Container,
    View: Container,
    StyleSheet: { create: <T,>(value: T) => value },
    Dimensions: { get: () => ({ width: 400, height: 800 }) },
  };
});

vi.mock("react-native-gifted-charts", async () => {
  const { getHorizSectionVals, useBarAndLineChartsWrapper, useBarChart } =
    await import("gifted-charts-core");
  return {
    BarChart(props: Omit<Parameters<typeof useBarChart>[0], "parentWidth">) {
      const { barAndLineChartsWrapperProps } = useBarChart({
        ...props,
        parentWidth: 400,
      });
      const { horizSectionProps } = useBarAndLineChartsWrapper({
        ...barAndLineChartsWrapperProps,
        isRTL: false,
      });
      const { horizSections, horizSectionsBelow, getLabelTexts } =
        getHorizSectionVals(horizSectionProps);
      const labels = [...horizSections, ...horizSectionsBelow].map(
        ({ value }, index) => getLabelTexts(value, index),
      );
      return createElement("div", { labels });
    },
  };
});

import { AnalyticsCharts } from "../src/screens/AnalyticsCharts";

let root: ReactTestRenderer;

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean })
    .IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(async () => {
  await act(async () => root?.unmount());
});

it.each([
  [1.2, ["1.5%", "1.0%", "0.5%", "0.0%"]],
  [-0.03, ["0.01%", "0.00%", "-0.01%", "-0.02%", "-0.03%"]],
  [0.00000012, ["0.00000015%", "0.00000010%", "0.00000005%", "0.00000000%"]],
])("preserves savings ticks for %s through the chart library", async (savingsPercent, expected) => {
  await act(async () => {
    root = create(
      <AnalyticsCharts buckets={[{
        wait: 1,
        runCount: 1,
        realized: {
          savingsPercent,
          immediateBaseFeeGwei: 1.2,
          selectedBaseFeeGwei: 1,
        },
      }]} />,
    );
  });
  const axes = root.root.findAllByType("div").map(({ props }) => props.labels);
  expect(axes).toEqual([
    ["1", "0"],
    expected,
    ["1.5", "1.0", "0.5", "0.0"],
  ]);
});
