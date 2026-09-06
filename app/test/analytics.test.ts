import { describe, expect, it } from "vitest";

import {
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
        wait: 0,
        runCount: 1,
        realized: { selectedBaseFeeGwei: 10, immediateBaseFeeGwei: 10, savingsPercent: 0 },
      },
      {
        wait: 1,
        runCount: 3,
        realized: { selectedBaseFeeGwei: 10, immediateBaseFeeGwei: 15, savingsPercent: 30 },
      },
      {
        wait: 2,
        runCount: 1,
        realized: { selectedBaseFeeGwei: 12, immediateBaseFeeGwei: 10, savingsPercent: -20 },
      },
      {
        wait: 3,
        runCount: 0,
        realized: null,
      },
      {
        wait: 4,
        runCount: 1,
        realized: null,
      },
    ]);
  });

});

it("preserves absent summary populations without exposing NaN", () => {
  expect(summarizeRuns([])).toEqual({ averageWait: null, averageSavingsPercent: null, winPercent: null });
  expect(summarizeRuns([inferenceRun({ selected_action_k: 2 })])).toEqual({ averageWait: 2, averageSavingsPercent: null, winPercent: null });
});
