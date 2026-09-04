import { describe, expect, it } from "vitest";

import {
  formatChartAxisValue,
  formatSavings,
  summarizeRuns,
  waitBuckets,
} from "../src/analytics";
import type { InferenceRun } from "../src/history";
import { inferenceRun } from "./helpers";

const GWEI = 1_000_000_000;

function resolved(
  id: string,
  wait: number,
  immediateBaseFeeGwei: number,
  selectedBaseFeeGwei: number,
): InferenceRun {
  return inferenceRun({
    id,
    selected_action_k: wait,
    target_block: 11 + wait,
    outcome: {
      immediate_base_fee_per_gas: immediateBaseFeeGwei * GWEI,
      selected_base_fee_per_gas: selectedBaseFeeGwei * GWEI,
    },
  });
}

describe("analytics", () => {
  it("computes realized metrics from supported outcomes and wait from every run", () => {
    const runs = [
      resolved("saved", 1, 100, 80),
      resolved("lost", 2, 100, 120),
      resolved("act-now", 0, 100, 100),
      inferenceRun({
        id: "pending",
        selected_action_k: 3,
        target_block: 14,
      }),
    ];

    const summary = summarizeRuns(runs);

    expect(summary.averageWait).toBe(1.5);
    expect(summary.averageSavingsPercent).toBeCloseTo(0);
    expect(summary.winPercent).toBeCloseTo(50);
  });

  it("aggregates resolved and pending runs into wait buckets", () => {
    const selectedRuns = [
      resolved("act-now", 0, 10, 10),
      resolved("saved", 1, 10, 8),
      resolved("saved-more", 1, 20, 12),
      inferenceRun({
        id: "pending",
        selected_action_k: 1,
        target_block: 12,
      }),
      resolved("lost", 2, 10, 12),
      inferenceRun({
        id: "pending-longest",
        selected_action_k: 4,
        target_block: 15,
      }),
    ];
    expect(waitBuckets(selectedRuns, 5)).toEqual([
      {
        selectedBaseFeeGwei: 10,
        immediateBaseFeeGwei: 10,
        wait: 0,
        runCount: 1,
        savingsPercent: 0,
      },
      {
        selectedBaseFeeGwei: 10,
        immediateBaseFeeGwei: 15,
        wait: 1,
        runCount: 3,
        savingsPercent: 30,
      },
      {
        selectedBaseFeeGwei: 12,
        immediateBaseFeeGwei: 10,
        wait: 2,
        runCount: 1,
        savingsPercent: -20,
      },
      {
        selectedBaseFeeGwei: null,
        immediateBaseFeeGwei: null,
        wait: 3,
        runCount: 0,
        savingsPercent: null,
      },
      {
        selectedBaseFeeGwei: null,
        immediateBaseFeeGwei: null,
        wait: 4,
        runCount: 1,
        savingsPercent: null,
      },
    ]);
  });

  it("returns empty analytics for an empty selection", () => {
    expect(summarizeRuns([])).toEqual({
      averageWait: null,
      averageSavingsPercent: null,
      winPercent: null,
    });
    expect(waitBuckets([], 5)).toEqual([]);
  });

  it("normalizes negative display zero without changing calculations", () => {
    expect(formatSavings(-0.0001)).toBe("0.0%");
    expect(formatSavings(-0.06)).toBe("-0.1%");
  });

  it("formats chart axes at the precision required by their step", () => {
    expect(formatChartAxisValue(0.5, 0.5, "%")).toBe("0.5%");
    expect(formatChartAxisValue(0.05, 0.05)).toBe("0.05");
    expect(formatChartAxisValue(10, 5)).toBe("10");
  });
});
