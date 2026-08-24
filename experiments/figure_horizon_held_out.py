"""Render final held-out horizon figures, including retrospective refinement."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from uuid import UUID

import numpy as np
from figure_style import DEFAULT_OUTPUT_DIRECTORY, display_name, save_pdf, subplots

from kairos.evaluation import reduce_baselines, reduce_evaluation, reduce_evaluation_intervals
from kairos.experiments import ExperimentKind, load_experiment_manifest

_CHAIN_STYLES = {"ethereum": "#0072B2", "polygon": "#D55E00", "avalanche": "#009E73"}
_POLICY_STYLES = {
    "learned": ("#0072B2", "o", "-", "Learned"),
    "immediate": ("#666666", "s", "--", "Immediate"),
    "deadline": ("#D55E00", "^", "--", "Deadline"),
}
_ECONOMIC_METRICS = (
    ("base_fee_savings", "Base-fee savings (%)"),
    ("base_fee_optimality_gap", "Cost over optimum (%)"),
)
_CLASSIFICATION_METRICS = (("accuracy", "Accuracy (%)", 100.0), ("f1_macro", "Macro-F1 (%)", 100.0))
_REGRESSION_METRICS = (("log_fee_mae", "Log-fee MAE", 1.0), ("log_fee_mse", "Log-fee MSE", 1.0))


def _load_results(
    storage_root: Path, experiment_ids: tuple[UUID, ...], *, with_confidence_intervals: bool
) -> tuple[
    tuple[str, ...],
    dict[str, tuple[int, ...]],
    dict[tuple[str, int, str], dict],
    dict[tuple[str, int], dict[str, tuple[float, float]]],
]:
    selected = {}
    for experiment_id in experiment_ids:
        manifest = load_experiment_manifest(storage_root, ExperimentKind.HELD_OUT, experiment_id)
        for cell, evaluation_id in manifest.items():
            chain, family, horizon_label = cell.split(".")
            if family != "lstm" or chain not in _CHAIN_STYLES:
                raise ValueError("horizon figures require the selected three-chain LSTM roster")
            horizon = int(horizon_label.removeprefix("K"))
            if (chain, horizon) in selected:
                raise ValueError(f"duplicate held-out horizon cell: {cell}")
            selected[chain, horizon] = evaluation_id

    horizons: dict[str, set[int]] = defaultdict(set)
    results = {}
    intervals = {}
    for (chain, horizon), evaluation_id in selected.items():
        horizons[chain].add(horizon)
        results[chain, horizon, "learned"] = reduce_evaluation(storage_root, evaluation_id).row(
            0, named=True
        )
        for baseline in reduce_baselines(storage_root, evaluation_id).iter_rows(named=True):
            results[chain, horizon, baseline["policy"]] = baseline
        if with_confidence_intervals:
            intervals[chain, horizon] = _confidence_intervals(storage_root, evaluation_id)
    return (
        tuple(_CHAIN_STYLES),
        {chain: tuple(sorted(values)) for chain, values in horizons.items()},
        results,
        intervals,
    )


def _confidence_intervals(
    storage_root: Path, evaluation_id: UUID
) -> dict[str, tuple[float, float]]:
    row = reduce_evaluation_intervals(storage_root, evaluation_id).row(0, named=True)
    return {
        metric: (row[f"{metric}_lower"], row[f"{metric}_upper"])
        for metric in (
            "accuracy",
            "f1_macro",
            "log_fee_mae",
            "log_fee_mse",
            "base_fee_savings",
            "base_fee_optimality_gap",
        )
    }


def _configure_horizon_axis(axis, values: tuple[int, ...], *, bottom: bool) -> None:
    axis.set_xscale("log")
    axis.set_xticks(values)
    axis.set_xticklabels([str(value) for value in values], rotation=35, ha="right")
    axis.minorticks_off()
    if bottom:
        axis.set_xlabel("Horizon blocks K")
    else:
        axis.tick_params(axis="x", labelbottom=False)


def _render_economic(
    chains, horizons, results, intervals, output: Path, *, max_horizon: int | None
) -> Path:
    figure, axes = subplots(len(chains), 2, height=1.85 * len(chains))
    for row, chain in enumerate(chains):
        values = tuple(
            horizon for horizon in horizons[chain] if max_horizon is None or horizon <= max_horizon
        )
        for column, (metric, label) in enumerate(_ECONOMIC_METRICS):
            axis = axes[row, column]
            for policy, (color, marker, line_style, policy_label) in _POLICY_STYLES.items():
                points = [100.0 * results[chain, horizon, policy][metric] for horizon in values]
                if policy == "learned" and intervals:
                    bounds = [intervals[chain, horizon][metric] for horizon in values]
                    lower = [100.0 * bound[0] for bound in bounds]
                    upper = [100.0 * bound[1] for bound in bounds]
                    axis.errorbar(
                        values,
                        points,
                        yerr=(np.asarray(points) - lower, upper - np.asarray(points)),
                        color=color,
                        marker=marker,
                        linestyle=line_style,
                        capsize=1.5,
                        label=policy_label,
                    )
                else:
                    axis.plot(
                        values,
                        points,
                        color=color,
                        marker=marker,
                        linestyle=line_style,
                        label=policy_label,
                    )
            axis.axhline(0.0, color="#333333", linewidth=0.7)
            _configure_horizon_axis(axis, values, bottom=row == len(chains) - 1)
            if row == 0:
                axis.set_title(label)
            if column == 0:
                axis.set_ylabel(display_name(chain))
            if metric == "base_fee_optimality_gap":
                axis.set_ylim(bottom=0.0)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside upper center", ncols=3, frameon=False)
    return save_pdf(figure, output)


def _render_predictive(
    chains, horizons, results, intervals, metrics, output: Path, *, max_horizon: int | None
) -> Path:
    figure, axes = subplots(len(chains), 2, height=1.85 * len(chains))
    for row, chain in enumerate(chains):
        values = tuple(
            horizon for horizon in horizons[chain] if max_horizon is None or horizon <= max_horizon
        )
        for column, (metric, label, scale) in enumerate(metrics):
            axis = axes[row, column]
            points = [scale * results[chain, horizon, "learned"][metric] for horizon in values]
            bounds = [intervals[chain, horizon][metric] for horizon in values] if intervals else []
            axis.errorbar(
                values,
                points,
                yerr=(
                    np.asarray(points) - [scale * bound[0] for bound in bounds],
                    [scale * bound[1] for bound in bounds] - np.asarray(points),
                )
                if bounds
                else None,
                color=_CHAIN_STYLES[chain],
                marker="o",
                capsize=1.5,
            )
            _configure_horizon_axis(axis, values, bottom=row == len(chains) - 1)
            if row == 0:
                axis.set_title(label)
            if column == 0:
                axis.set_ylabel(display_name(chain))
    return save_pdf(figure, output)


def render(
    storage_root: Path,
    experiment_id: UUID,
    refinement_experiment_id: UUID,
    output_directory: Path,
    *,
    with_confidence_intervals: bool = True,
) -> tuple[Path, ...]:
    chains, horizons, results, intervals = _load_results(
        storage_root,
        (experiment_id, refinement_experiment_id),
        with_confidence_intervals=with_confidence_intervals,
    )
    outputs = (
        _render_economic(
            chains,
            horizons,
            results,
            intervals,
            output_directory / "horizon-held-out-economic.pdf",
            max_horizon=None,
        ),
        _render_predictive(
            chains,
            horizons,
            results,
            intervals,
            _CLASSIFICATION_METRICS,
            output_directory / "horizon-held-out-classification.pdf",
            max_horizon=None,
        ),
        _render_predictive(
            chains,
            horizons,
            results,
            intervals,
            _REGRESSION_METRICS,
            output_directory / "horizon-held-out-regression.pdf",
            max_horizon=None,
        ),
        _render_economic(
            chains,
            horizons,
            results,
            intervals,
            output_directory / "horizon-held-out-economic-k25.pdf",
            max_horizon=25,
        ),
        _render_predictive(
            chains,
            horizons,
            results,
            intervals,
            _CLASSIFICATION_METRICS,
            output_directory / "horizon-held-out-classification-k25.pdf",
            max_horizon=25,
        ),
        _render_predictive(
            chains,
            horizons,
            results,
            intervals,
            _REGRESSION_METRICS,
            output_directory / "horizon-held-out-regression-k25.pdf",
            max_horizon=25,
        ),
    )
    for output in outputs:
        print(output)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storage_root", type=Path)
    parser.add_argument("experiment_id", type=UUID)
    parser.add_argument("refinement_experiment_id", type=UUID)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    parser.add_argument("--without-confidence-intervals", action="store_true")
    arguments = parser.parse_args()
    render(
        arguments.storage_root,
        arguments.experiment_id,
        arguments.refinement_experiment_id,
        arguments.output_directory,
        with_confidence_intervals=not arguments.without_confidence_intervals,
    )


if __name__ == "__main__":
    main()
