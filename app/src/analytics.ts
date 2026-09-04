import type { Horizon } from "./domain";
import type { InferenceRun } from "./history";

/**
 * `runCount` includes pending runs; fee and savings means use resolved outcomes only.
 */
export type WaitBucket = {
  selectedBaseFeeGwei: number | null;
  immediateBaseFeeGwei: number | null;
  runCount: number;
  savingsPercent: number | null;
  wait: number;
};

const RUN_DATE_FORMATTER = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  hour: "2-digit",
  hourCycle: "h23",
  minute: "2-digit",
  month: "short",
});
const GWEI = 1_000_000_000;

/**
 * Averages wait over all runs and savings over resolved runs.
 * Win rate includes only resolved runs whose action waits at least one block.
 */
export function summarizeRuns(runs: readonly InferenceRun[]) {
  const realized = runs.flatMap((run) => {
    const savings = realizedSavingsPercent(run);
    return savings === null ? [] : [[run.selected_action_k, savings] as const];
  });
  const waited = realized.filter(([action]) => action !== 0);
  const winCount = waited.filter(([, savings]) => savings > 0).length;

  return {
    averageWait: mean(runs.map((run) => run.selected_action_k)),
    averageSavingsPercent: mean(realized.map(([, savings]) => savings)),
    winPercent:
      waited.length === 0 ? null : (winCount / waited.length) * 100,
  };
}

/**
 * Returns base-fee savings versus acting in the next block.
 * Positive means the selected block was cheaper.
 */
export function realizedSavingsPercent(run: InferenceRun): number | null {
  return run.outcome === undefined ? null : savingsPercent(run.outcome);
}

function savingsPercent(outcome: NonNullable<InferenceRun["outcome"]>): number {
  return (
    ((outcome.immediate_base_fee_per_gas -
      outcome.selected_base_fee_per_gas) /
      outcome.immediate_base_fee_per_gas) *
    100
  );
}

export function formatRunDate(value: string): string {
  return RUN_DATE_FORMATTER.format(new Date(value));
}

export function formatSavings(value: number): string {
  const formatted = value.toFixed(1);
  return `${formatted === "-0.0" ? "0.0" : formatted}%`;
}

export function formatWeiAsGwei(value: number): string {
  const gwei = value / GWEI;
  if (gwei >= 100) {
    return `${gwei.toFixed(0)} Gwei`;
  }
  if (gwei >= 10) {
    return `${gwei.toFixed(1)} Gwei`;
  }
  return `${gwei.toFixed(2)} Gwei`;
}

export function formatChartAxisValue(
  value: number,
  step: number,
  suffix = "",
): string {
  const fractionDigits =
    step >= 1 ? 0 : Math.min(6, Math.ceil(-Math.log10(step)));
  return `${value.toFixed(fractionDigits)}${suffix}`;
}

export function waitBuckets(
  runs: readonly InferenceRun[],
  horizon: Horizon,
): WaitBucket[] {
  if (runs.length === 0) {
    return [];
  }

  return Array.from({ length: horizon }, (_, offset) => {
    const matchingRuns = runs.filter(
      (run) => run.selected_action_k === offset,
    );
    const outcomes = matchingRuns.flatMap((run) =>
      run.outcome === undefined ? [] : [run.outcome],
    );
    const selectedFeeMean = mean(
      outcomes.map((outcome) => outcome.selected_base_fee_per_gas),
    );
    const immediateFeeMean = mean(
      outcomes.map((outcome) => outcome.immediate_base_fee_per_gas),
    );

    return {
      selectedBaseFeeGwei:
        selectedFeeMean === null ? null : selectedFeeMean / GWEI,
      immediateBaseFeeGwei:
        immediateFeeMean === null ? null : immediateFeeMean / GWEI,
      runCount: matchingRuns.length,
      savingsPercent: mean(outcomes.map(savingsPercent)),
      wait: offset,
    };
  });
}

function mean(values: readonly number[]): number | null {
  if (values.length === 0) {
    return null;
  }
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}
