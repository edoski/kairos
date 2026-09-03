import { type PropsWithChildren, type ReactNode } from "react";
import { StyleSheet, Text, View } from "react-native";
import { BarChart as GiftedBarChart } from "react-native-gifted-charts";

import { formatChartAxisValue, type WaitBucket } from "../analytics";
import { styles as sharedStyles } from "../styles";
import { colors, radii } from "../theme";

const CHART_HEIGHT = 138;
const GRAPH_AXIS_TEXT = { color: colors.muted, fontSize: 9 } as const;
const AXIS_PROPS = {
  barBorderRadius: radii.small / 2,
  disablePress: true,
  endSpacing: 10,
  initialSpacing: 10,
  rulesColor: colors.border,
  xAxisColor: colors.muted,
  xAxisLabelsAtBottom: true,
  xAxisLabelsHeight: 14,
  xAxisLabelTextStyle: GRAPH_AXIS_TEXT,
  yAxisLabelWidth: 34,
  yAxisTextStyle: GRAPH_AXIS_TEXT,
  yAxisThickness: 0,
} as const;

function niceStep(range: number): number {
  const rough = range / 3;
  const magnitude = 10 ** Math.floor(Math.log10(rough));
  const normalized = rough / magnitude;
  const multiplier =
    normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
  return multiplier * magnitude;
}

function chartScale(values: readonly number[]) {
  const rawMinimum = Math.min(0, ...values);
  const rawMaximum = Math.max(0, ...values);
  const step = niceStep(
    rawMinimum === rawMaximum ? 1 : rawMaximum - rawMinimum,
  );
  const minimum = Math.floor(rawMinimum / step) * step;
  const maximum = Math.max(step, Math.ceil(rawMaximum / step) * step);
  const positiveSections = Math.round(maximum / step);
  const negativeSections = Math.round(Math.abs(minimum) / step);

  return {
    noOfSections: positiveSections,
    noOfSectionsBelowXAxis: negativeSections,
    stepHeight: CHART_HEIGHT / (positiveSections + negativeSections),
    stepValue: step,
  };
}

function ChartCard({
  children,
  empty,
  legend,
  title,
  xAxisTitle,
}: PropsWithChildren<{
  empty: "outcomes" | null;
  legend?: ReactNode;
  title: string;
  xAxisTitle: string;
}>) {
  return (
    <View style={[sharedStyles.surface, styles.chartCard]}>
      <View style={styles.headerRow}>
        <Text style={styles.chartTitle}>{title}</Text>
        {legend}
      </View>
      {empty === null ? (
        <View style={styles.graph}>
          {children}
          <Text style={styles.graphXAxisTitle}>{xAxisTitle}</Text>
        </View>
      ) : (
        <View style={styles.emptyGraph}>
          <Text style={styles.emptyGraphTitle}>No outcomes yet</Text>
          <Text style={styles.emptyGraphText}>
            Resolved inferences will populate this graph.
          </Text>
        </View>
      )}
    </View>
  );
}

function RecommendedWaitChart({
  buckets,
}: {
  buckets: readonly WaitBucket[];
}) {
  return (
    <ChartCard
      empty={null}
      title="Recommended wait distribution"
      xAxisTitle="Wait (blocks)"
    >
      <GiftedBarChart
        {...AXIS_PROPS}
        {...chartScale(buckets.map((bucket) => bucket.runCount))}
        data={buckets.map((bucket) => ({
          frontColor: colors.blue,
          label: String(bucket.wait),
          value: bucket.runCount,
        }))}
      />
    </ChartCard>
  );
}

function SavingsByWaitChart({
  buckets,
}: {
  buckets: readonly WaitBucket[];
}) {
  const data = buckets.flatMap((bucket) =>
    bucket.savingsPercent === null
      ? []
      : [
          {
            frontColor:
              bucket.savingsPercent < 0 ? colors.red : colors.teal,
            label: String(bucket.wait),
            value: bucket.savingsPercent,
          },
        ],
  );
  const scale = chartScale(data.map(({ value }) => value));
  return (
    <ChartCard
      empty={data.length === 0 ? "outcomes" : null}
      title="Savings by wait (%)"
      xAxisTitle="Wait (blocks)"
    >
      <GiftedBarChart
        {...AXIS_PROPS}
        {...scale}
        data={data}
        formatYLabel={(label) =>
          formatChartAxisValue(Number(label), scale.stepValue, "%")
        }
      />
    </ChartCard>
  );
}

function BaseFeeByWaitChart({
  buckets,
}: {
  buckets: readonly WaitBucket[];
}) {
  const data = buckets.filter(
    (
      bucket,
    ): bucket is WaitBucket & {
      selectedBaseFeeGwei: number;
      immediateBaseFeeGwei: number;
    } =>
      bucket.selectedBaseFeeGwei !== null &&
      bucket.immediateBaseFeeGwei !== null,
  );
  const scale = chartScale(
    data.flatMap((bucket) => [
      bucket.immediateBaseFeeGwei,
      bucket.selectedBaseFeeGwei,
    ]),
  );
  return (
    <ChartCard
      legend={
        <View style={styles.graphLegend}>
          <View
            style={[styles.graphLegendDot, styles.graphImmediateDot]}
          />
          <Text style={styles.graphLegendLabel}>Act now</Text>
          <View style={[styles.graphLegendDot, styles.graphKairosDot]} />
          <Text style={styles.graphLegendLabel}>KAIROS</Text>
        </View>
      }
      title="Base fee by wait (Gwei)"
      empty={data.length === 0 ? "outcomes" : null}
      xAxisTitle="Recommended wait (blocks)"
    >
      <GiftedBarChart
        {...AXIS_PROPS}
        {...scale}
        barWidth={18}
        data={data.flatMap((bucket, index) => [
          {
            frontColor: colors.amberSoft,
            label: String(bucket.wait),
            labelWidth: 36,
            spacing: 4,
            value: bucket.immediateBaseFeeGwei,
          },
          {
            frontColor: colors.blue,
            spacing: index === data.length - 1 ? 0 : 20,
            value: bucket.selectedBaseFeeGwei,
          },
        ])}
        formatYLabel={(label) =>
          formatChartAxisValue(Number(label), scale.stepValue)
        }
        spacing={0}
      />
    </ChartCard>
  );
}

export function AnalyticsCharts({
  buckets,
}: {
  buckets: readonly WaitBucket[];
}) {
  return (
    <View style={styles.chartCards}>
      <RecommendedWaitChart buckets={buckets} />
      <SavingsByWaitChart buckets={buckets} />
      <BaseFeeByWaitChart buckets={buckets} />
    </View>
  );
}

const styles = StyleSheet.create({
  chartCards: { gap: 12 },
  chartCard: {
    borderRadius: radii.large,
    gap: 14,
    overflow: "hidden",
    padding: 14,
  },
  headerRow: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  chartTitle: { color: colors.ink, fontSize: 15, fontWeight: "700" },
  graph: { gap: 2 },
  graphXAxisTitle: {
    color: colors.muted,
    fontSize: 9,
    fontWeight: "600",
    marginTop: 3,
    textAlign: "center",
  },
  graphLegend: {
    alignItems: "center",
    flexDirection: "row",
    gap: 4,
  },
  graphLegendDot: { borderRadius: 4, height: 7, marginLeft: 5, width: 7 },
  graphImmediateDot: { backgroundColor: colors.amberSoft },
  graphKairosDot: { backgroundColor: colors.blue },
  graphLegendLabel: { color: colors.muted, fontSize: 8 },
  emptyGraph: {
    alignItems: "center",
    height: 184,
    justifyContent: "center",
    padding: 24,
  },
  emptyGraphTitle: { color: colors.ink, fontSize: 16, fontWeight: "700" },
  emptyGraphText: {
    color: colors.muted,
    fontSize: 13,
    marginTop: 5,
    textAlign: "center",
  },
});
