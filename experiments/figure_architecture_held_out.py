"""Render the matched K=5 held-out architecture comparison."""

from __future__ import annotations

import argparse
from pathlib import Path
from uuid import UUID

import numpy as np
from figure_style import (
    DEFAULT_OUTPUT_DIRECTORY,
    add_family_legend,
    display_name,
    family_style,
    save_pdf,
    subplots,
)

from kairos.evaluation import reduce_evaluation, reduce_evaluation_intervals
from kairos.experiments import ExperimentKind, load_experiment_manifest

_CHAINS = ("ethereum", "polygon", "avalanche")
_FAMILIES = ("lstm", "transformer", "transformer_lstm")
_ECONOMIC_METRICS = (
    ("base_fee_savings", "Base-fee savings (%)", 100.0),
    ("base_fee_optimality_gap", "Cost over optimum (%)", 100.0),
)
_CLASSIFICATION_METRICS = (("accuracy", "Accuracy (%)", 100.0), ("f1_macro", "Macro-F1 (%)", 100.0))
_REGRESSION_METRICS = (("log_fee_mae", "Log-fee MAE", 1.0), ("log_fee_mse", "Log-fee MSE", 1.0))


def _load_results(storage_root: Path, experiment_id: UUID) -> tuple[dict, dict]:
    manifest = load_experiment_manifest(storage_root, ExperimentKind.HELD_OUT, experiment_id)
    expected = {f"{chain}.{family}.K5" for chain in _CHAINS for family in _FAMILIES}
    if set(manifest) != expected:
        raise ValueError("architecture figure requires the exact three-chain K=5 roster")

    points = {}
    intervals = {}
    for chain in _CHAINS:
        for family in _FAMILIES:
            evaluation_id = manifest[f"{chain}.{family}.K5"]
            points[chain, family] = reduce_evaluation(storage_root, evaluation_id).row(
                0, named=True
            )
            intervals[chain, family] = reduce_evaluation_intervals(storage_root, evaluation_id).row(
                0, named=True
            )
    return points, intervals


def _render_panel(points: dict, intervals: dict, metrics: tuple, output: Path) -> Path:
    figure, axes = subplots(1, 2, height=2.55)
    positions = np.arange(len(_CHAINS), dtype=np.float64)
    width = 0.24
    for column, (metric, label, scale) in enumerate(metrics):
        axis = axes[0, column]
        for family_index, family in enumerate(_FAMILIES):
            values = np.asarray(
                [scale * points[chain, family][metric] for chain in _CHAINS], dtype=np.float64
            )
            lower = np.asarray(
                [scale * intervals[chain, family][f"{metric}_lower"] for chain in _CHAINS],
                dtype=np.float64,
            )
            upper = np.asarray(
                [scale * intervals[chain, family][f"{metric}_upper"] for chain in _CHAINS],
                dtype=np.float64,
            )
            if np.any((values < lower) | (values > upper)):
                raise ValueError(f"{metric} point estimate must lie within its interval")
            color, _ = family_style(family)
            axis.bar(
                positions + (family_index - 1) * width,
                values,
                width,
                yerr=np.vstack((values - lower, upper - values)),
                capsize=1.5,
                color=color,
                label=display_name(family),
            )
        axis.set_xticks(positions)
        axis.set_xticklabels([display_name(chain) for chain in _CHAINS])
        axis.set_ylabel(label)
        if metric == "base_fee_savings":
            axis.axhline(0.0, color="#333333", linewidth=0.7)
        if metric == "base_fee_optimality_gap":
            axis.set_ylim(bottom=0.0)
    add_family_legend(figure, axes[0, 0])
    return save_pdf(figure, output)


def render(storage_root: Path, experiment_id: UUID, output_directory: Path) -> tuple[Path, ...]:
    points, intervals = _load_results(storage_root, experiment_id)
    outputs = (
        _render_panel(
            points,
            intervals,
            _ECONOMIC_METRICS,
            output_directory / "architecture-held-out-economic.pdf",
        ),
        _render_panel(
            points,
            intervals,
            _CLASSIFICATION_METRICS,
            output_directory / "architecture-held-out-classification.pdf",
        ),
        _render_panel(
            points,
            intervals,
            _REGRESSION_METRICS,
            output_directory / "architecture-held-out-regression.pdf",
        ),
    )
    for output in outputs:
        print(output)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storage_root", type=Path)
    parser.add_argument("experiment_id", type=UUID)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    arguments = parser.parse_args()
    render(arguments.storage_root, arguments.experiment_id, arguments.output_directory)


if __name__ == "__main__":
    main()
