import type { Horizon } from "./domain";
import type { InferenceRun } from "./history";

/**
 * `runCount` includes pending runs; fee and savings means use resolved outcomes only.
 */
export type WaitBucket = {
  runCount: number;
  wait: number;
  realized: {
    selectedBaseFeeGwei: number;
    immediateBaseFeeGwei: number;
    savingsPercent: number;
  } | null;
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
    averageWait: runs.length === 0
      ? null
      : mean(runs.map((run) => run.selected_action_k)),
    averageSavingsPercent: realized.length === 0
      ? null
      : mean(realized.map(([, savings]) => savings)),
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
    return {
      runCount: matchingRuns.length,
      wait: offset,
      realized: outcomes.length === 0 ? null : {
        selectedBaseFeeGwei: mean(
          outcomes.map((outcome) => outcome.selected_base_fee_per_gas),
        ) / GWEI,
        immediateBaseFeeGwei: mean(
          outcomes.map((outcome) => outcome.immediate_base_fee_per_gas),
        ) / GWEI,
        savingsPercent: mean(outcomes.map(savingsPercent)),
      },
    };
  });
}

function mean(values: readonly number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}
