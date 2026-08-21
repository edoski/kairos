"""Render the paired Polygon temporal-alignment diagnostic."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from uuid import UUID

from figure_style import DEFAULT_OUTPUT_DIRECTORY, save_pdf, subplots

from kairos.evaluation import reduce_evaluation
from kairos.experiments import ExperimentKind, load_experiment_manifest

_COHORT_STYLES = {
    "stale_history": ("#666666", "s", "--", "Stale-history fit"),
    "chicago_training": ("#0072B2", "o", "-", "Chicago fit"),
}
_ECONOMIC_METRICS = (
    ("base_fee_savings", "Base-fee savings (%)"),
    ("base_fee_optimality_gap", "Cost over optimum (%)"),
)
def _load_results(
    storage_root: Path, experiment_id: UUID
) -> tuple[tuple[int, ...], dict[tuple[str, int], dict[str, float]]]:
    manifest = load_experiment_manifest(storage_root, ExperimentKind.HELD_OUT, experiment_id)
    roster: dict[str, set[int]] = defaultdict(set)
    results = {}
    for cell, evaluation_id in manifest.items():
        parts = cell.split(".")
        if len(parts) != 5:
            raise ValueError("temporal-alignment cells must name training and testing roles")
        chain, cohort, testing_role, family, horizon_label = parts
        if (
            chain != "polygon"
            or cohort not in _COHORT_STYLES
            or testing_role != "chicago_tail"
            or family != "lstm"
        ):
            continue
        horizon = int(horizon_label.removeprefix("K"))
        roster[cohort].add(horizon)
        results[cohort, horizon] = reduce_evaluation(storage_root, evaluation_id).row(
            0, named=True
        )
    if (
        set(roster) != set(_COHORT_STYLES)
        or roster["stale_history"] != roster["chicago_training"]
    ):
        raise ValueError("temporal-alignment figures require the same horizons in both cohorts")
    return tuple(sorted(roster["stale_history"])), results


def _plot_cohorts(axis, horizons, results, metric, *, scale=100.0) -> None:
    for cohort, (color, marker, line_style, label) in _COHORT_STYLES.items():
        axis.plot(
            horizons,
            [scale * results[cohort, horizon][metric] for horizon in horizons],
            color=color,
            marker=marker,
            linestyle=line_style,
            label=label,
        )
    axis.set_xscale("log")
    axis.set_xticks(horizons)
    axis.set_xticklabels([str(value) for value in horizons], rotation=35, ha="right")
    axis.minorticks_off()
    axis.set_xlabel("Horizon blocks K")


def _render_economic(horizons, results, output: Path) -> Path:
    figure, axes = subplots(1, 2, height=2.35)
    for column, (metric, label) in enumerate(_ECONOMIC_METRICS):
        axis = axes[0, column]
        _plot_cohorts(axis, horizons, results, metric)
        axis.axhline(0.0, color="#333333", linewidth=0.7)
        axis.set_ylabel(label)
        if metric == "base_fee_optimality_gap":
            axis.set_ylim(bottom=0.0)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside upper center", ncols=2, frameon=False)
    return save_pdf(figure, output)


def render(storage_root: Path, experiment_id: UUID, output_directory: Path) -> Path:
    horizons, results = _load_results(storage_root, experiment_id)
    economic = _render_economic(
        horizons, results, output_directory / "polygon-temporal-alignment-economic.pdf"
    )
    print(economic)
    return economic


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storage_root", type=Path)
    parser.add_argument("experiment_id", type=UUID)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    arguments = parser.parse_args()
    render(arguments.storage_root, arguments.experiment_id, arguments.output_directory)


if __name__ == "__main__":
    main()
