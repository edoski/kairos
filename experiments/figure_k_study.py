"""Render validation horizon sensitivity from canonical K-study artifacts."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from uuid import UUID

from figure_style import DEFAULT_OUTPUT_DIRECTORY, display_name, save_pdf, subplots

from kairos.addresses import artifact_observations_path
from kairos.experiments import ExperimentKind, load_experiment_manifest
from kairos.observations import reduce_observations

_PREDICTIVE_METRICS = (
    ("accuracy", "Accuracy (%)", 100.0),
    ("f1_macro", "Macro-F1 (%)", 100.0),
    ("log_fee_mae", "Log-fee MAE", 1.0),
    ("log_fee_mse", "Log-fee MSE", 1.0),
)
_ECONOMIC_METRICS = (
    ("base_fee_savings", "Base-fee savings (%)", 100.0),
    ("base_fee_optimality_gap", "Cost over optimum (%)", 100.0),
)
_CHAIN_STYLES = {
    "ethereum": ("#0072B2", "o"),
    "polygon": ("#D55E00", "s"),
    "avalanche": ("#009E73", "^"),
}
_DETAIL_MAX_HORIZON = 25


def _load_results(
    storage_root: Path, experiment_id: UUID
) -> tuple[tuple[str, ...], dict[str, tuple[int, ...]], dict[tuple[str, int], dict[str, float]]]:
    manifest = load_experiment_manifest(storage_root, ExperimentKind.K_STUDY, experiment_id)
    chains: list[str] = []
    horizons: dict[str, list[int]] = defaultdict(list)
    metrics: dict[tuple[str, int], dict[str, float]] = {}
    for cell, artifact_id in manifest.items():
        chain, family, horizon_label = cell.split(".")
        if family != "lstm":
            raise ValueError("K-study figures require the selected LSTM roster")
        horizon = int(horizon_label.removeprefix("K"))
        if chain not in chains:
            chains.append(chain)
        horizons[chain].append(horizon)
        metrics[chain, horizon] = reduce_observations(
            artifact_observations_path(storage_root, artifact_id)
        ).row(0, named=True)
    return (
        tuple(chains),
        {chain: tuple(sorted(values)) for chain, values in horizons.items()},
        metrics,
    )


def _render_group(
    chains: tuple[str, ...],
    horizons: dict[str, tuple[int, ...]],
    results: dict[tuple[str, int], dict[str, float]],
    metrics: tuple[tuple[str, str, float], ...],
    output: Path,
    *,
    max_horizon: int | None = None,
) -> Path:
    columns = 2
    rows = (len(metrics) + columns - 1) // columns
    figure, axes = subplots(rows, columns, height=2.35 * rows)
    ticks = sorted(
        {
            horizon
            for chain in chains
            for horizon in horizons[chain]
            if max_horizon is None or horizon <= max_horizon
        }
    )
    for index, (metric, label, scale) in enumerate(metrics):
        axis = axes[index // columns, index % columns]
        for chain in chains:
            values = tuple(
                horizon
                for horizon in horizons[chain]
                if max_horizon is None or horizon <= max_horizon
            )
            color, marker = _CHAIN_STYLES[chain]
            axis.plot(
                values,
                [scale * results[chain, horizon][metric] for horizon in values],
                color=color,
                marker=marker,
                label=display_name(chain),
            )
        axis.set_xscale("log")
        axis.set_xticks(ticks)
        axis.set_xticklabels([str(value) for value in ticks])
        axis.minorticks_off()
        axis.set_xlabel("Horizon blocks K")
        axis.set_ylabel(label)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside upper center", ncols=len(labels), frameon=False)
    return save_pdf(figure, output)


def _render_economic_detail(
    chains: tuple[str, ...],
    horizons: dict[str, tuple[int, ...]],
    results: dict[tuple[str, int], dict[str, float]],
    output: Path,
) -> Path:
    figure, axes = subplots(len(chains), len(_ECONOMIC_METRICS), height=1.5 * len(chains))
    ticks = sorted(
        {
            horizon
            for chain in chains
            for horizon in horizons[chain]
            if horizon <= _DETAIL_MAX_HORIZON
        }
    )
    for row, chain in enumerate(chains):
        values = tuple(horizon for horizon in horizons[chain] if horizon <= _DETAIL_MAX_HORIZON)
        color, marker = _CHAIN_STYLES[chain]
        for column, (metric, label, scale) in enumerate(_ECONOMIC_METRICS):
            axis = axes[row, column]
            axis.plot(
                values,
                [scale * results[chain, horizon][metric] for horizon in values],
                color=color,
                marker=marker,
            )
            axis.axhline(0.0, color="#333333", linewidth=0.7)
            axis.set_xscale("log")
            axis.set_xticks(ticks)
            axis.set_xticklabels([str(value) for value in ticks])
            axis.minorticks_off()
            if row == 0:
                axis.set_title(label)
            if row == len(chains) - 1:
                axis.set_xlabel("Horizon blocks K")
            else:
                axis.tick_params(axis="x", labelbottom=False)
            if column == 0:
                axis.set_ylabel(display_name(chain))
            if metric == "base_fee_optimality_gap":
                axis.set_ylim(bottom=0.0)
    return save_pdf(figure, output)


def render(
    storage_root: Path, experiment_id: UUID, output_directory: Path
) -> tuple[Path, Path, Path, Path]:
    chains, horizons, results = _load_results(storage_root, experiment_id)
    predictive = _render_group(
        chains,
        horizons,
        results,
        _PREDICTIVE_METRICS,
        output_directory / "horizon-validation-predictive.pdf",
    )
    economic = _render_group(
        chains,
        horizons,
        results,
        _ECONOMIC_METRICS,
        output_directory / "horizon-validation-economic.pdf",
    )
    economic_detail = _render_economic_detail(
        chains, horizons, results, output_directory / "horizon-validation-economic-k25.pdf"
    )
    predictive_detail = _render_group(
        chains,
        horizons,
        results,
        _PREDICTIVE_METRICS,
        output_directory / "horizon-validation-predictive-k25.pdf",
        max_horizon=_DETAIL_MAX_HORIZON,
    )
    print(predictive)
    print(economic)
    print(economic_detail)
    print(predictive_detail)
    return predictive, economic, economic_detail, predictive_detail


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storage_root", type=Path)
    parser.add_argument("experiment_id", type=UUID)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    arguments = parser.parse_args()
    render(arguments.storage_root, arguments.experiment_id, arguments.output_directory)


if __name__ == "__main__":
    main()
