"""Render the final one-shot versus rolling held-out comparison."""

from __future__ import annotations

import argparse
from pathlib import Path
from uuid import UUID

import numpy as np
from figure_style import DEFAULT_OUTPUT_DIRECTORY, display_name, save_pdf, subplots

from kairos.evaluation import ROLLING_HORIZONS, reduce_rolling, reduce_rolling_intervals
from kairos.experiments import ExperimentKind, load_experiment_manifest

_CHAINS = ("ethereum", "polygon", "avalanche")
_POLICIES = {
    "one_shot": ("#666666", "One-shot K=5"),
    "rolling": ("#0072B2", "Rolling K=5→4→3→2"),
}
_METRICS = (
    ("base_fee_savings", "Base-fee savings (%)"),
    ("base_fee_optimality_gap", "Cost over optimum (%)"),
)


def _roster(storage_root: Path, experiment_id: UUID):
    manifest = load_experiment_manifest(storage_root, ExperimentKind.HELD_OUT, experiment_id)
    roster = {}
    for chain in _CHAINS:
        evaluations = {}
        for horizon in ROLLING_HORIZONS:
            cell = f"{chain}.lstm.K{horizon}"
            evaluations[horizon] = manifest[cell]
        roster[f"{chain}.lstm"] = evaluations
    return roster


def render(
    storage_root: Path,
    experiment_id: UUID,
    output_directory: Path,
    *,
    with_confidence_intervals: bool = True,
) -> Path:
    roster = _roster(storage_root, experiment_id)
    metrics = {
        row["cell"]: row for row in reduce_rolling(storage_root, roster).iter_rows(named=True)
    }
    intervals = (
        {
            row["cell"]: row
            for row in reduce_rolling_intervals(storage_root, roster).iter_rows(named=True)
        }
        if with_confidence_intervals
        else {}
    )

    figure, axes = subplots(1, len(_METRICS), height=3.0)
    positions = np.arange(len(_CHAINS), dtype=np.float64)
    width = 0.34
    for column, (metric, title) in enumerate(_METRICS):
        axis = axes[0, column]
        pair_tops = np.zeros(len(_CHAINS), dtype=np.float64)
        pair_bottoms = np.zeros(len(_CHAINS), dtype=np.float64)
        for policy_index, (policy, (color, label)) in enumerate(_POLICIES.items()):
            x = positions + (-width / 2 if policy_index == 0 else width / 2)
            points = np.array(
                [100.0 * metrics[f"{chain}.lstm"][f"{policy}_{metric}"] for chain in _CHAINS]
            )
            if intervals:
                lower = np.array(
                    [
                        100.0
                        * intervals[f"{chain}.lstm"][f"{policy}_{metric}_lower"]
                        for chain in _CHAINS
                    ]
                )
                upper = np.array(
                    [
                        100.0
                        * intervals[f"{chain}.lstm"][f"{policy}_{metric}_upper"]
                        for chain in _CHAINS
                    ]
                )
                yerr = (points - lower, upper - points)
                pair_tops = np.maximum(pair_tops, upper)
                pair_bottoms = np.minimum(pair_bottoms, lower)
            else:
                yerr = None
                pair_tops = np.maximum(pair_tops, points)
                pair_bottoms = np.minimum(pair_bottoms, points)
            axis.bar(
                x,
                points,
                width=width,
                yerr=yerr,
                color=color,
                edgecolor="white",
                linewidth=0.6,
                capsize=2.5,
                label=label,
                error_kw={"elinewidth": 0.9, "capthick": 0.9},
            )
        span = max(float(pair_tops.max() - pair_bottoms.min()), 0.1)
        for index, chain in enumerate(_CHAINS):
            row = metrics[f"{chain}.lstm"]
            delta = 100.0 * (row[f"rolling_{metric}"] - row[f"one_shot_{metric}"])
            axis.text(
                positions[index],
                pair_tops[index] + 0.035 * span,
                f"Δ {delta:+.3f} pp",
                ha="center",
                va="bottom",
                fontsize=7.5,
            )
        axis.axhline(0.0, color="#333333", linewidth=0.7)
        axis.set_xticks(positions, [display_name(chain) for chain in _CHAINS])
        axis.set_title(title)
        axis.set_ylabel("Percent")
        bottom = min(0.0, float(pair_bottoms.min()) - 0.04 * span)
        axis.set_ylim(bottom=bottom, top=float(pair_tops.max()) + 0.20 * span)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside upper center", ncols=2, frameon=False)
    output = save_pdf(figure, output_directory / "rolling-held-out-comparison.pdf")
    print(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storage_root", type=Path)
    parser.add_argument("experiment_id", type=UUID)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    parser.add_argument("--without-confidence-intervals", action="store_true")
    arguments = parser.parse_args()
    render(
        arguments.storage_root,
        arguments.experiment_id,
        arguments.output_directory,
        with_confidence_intervals=not arguments.without_confidence_intervals,
    )


if __name__ == "__main__":
    main()
