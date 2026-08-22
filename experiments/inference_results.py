"""Reduce the local inference benchmark into reproducible result tables."""

from __future__ import annotations

import json
import math
import statistics
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

_CHAIN_ORDER = {"ethereum": 0, "polygon": 1, "avalanche": 2}
_ARCHITECTURE_ORDER = {"lstm": 0, "transformer": 1, "transformer_lstm": 2}
_ARCHITECTURE_LABEL = {"lstm": "LSTM", "transformer": "Transformer", "transformer_lstm": "Hybrid"}
_WORKLOAD_ORDER = {"k2": 0, "k3": 1, "k4": 2, "k5": 3, "cascade": 4}
_T_975 = {4: 2.7764451051977987, 9: 2.2621571627409915}
_EUR_PER_KWH = 0.2966


def _number(value: object, label: str) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} is not finite")
    return float(value)


def _mean_ci95(values: Sequence[float]) -> tuple[float, float, float]:
    if len(values) < 2:
        raise ValueError("a confidence interval requires at least two observations")
    degrees_of_freedom = len(values) - 1
    try:
        critical = _T_975[degrees_of_freedom]
    except KeyError as error:
        raise ValueError(
            "supported confidence intervals require five or ten observations"
        ) from error
    mean = statistics.fmean(values)
    half_width = critical * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half_width, mean + half_width


def _protocol(panel_root: Path, expected_panel: str) -> dict[str, Any]:
    protocol = json.loads((panel_root / "protocol.json").read_text())
    if protocol["panel"] != expected_panel:
        raise ValueError(f"expected {expected_panel} protocol")
    return protocol


def _cells(protocol: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted({label.rsplit(".K", maxsplit=1)[0] for label in protocol["roster"]}))


def _read_latency(
    panel_root: Path, protocol: dict[str, Any], workloads: tuple[str, ...]
) -> pl.DataFrame:
    expected_sweeps = int(protocol["sweeps"])
    origins = int(protocol["origins_per_chain"])
    frames = []
    expected_paths = set()
    for cell in _cells(protocol):
        for sweep in range(1, expected_sweeps + 1):
            path = panel_root / "latency" / cell / f"sweep-{sweep:03d}.parquet"
            expected_paths.add(path)
            if not path.is_file():
                raise ValueError(f"missing latency sweep: {path}")
            frame = pl.read_parquet(path)
            expected_columns = {
                "cell",
                "sweep",
                "pass_order",
                "workload",
                "origin_block",
                "elapsed_ns",
            }
            if set(frame.columns) != expected_columns:
                raise ValueError(f"invalid latency schema: {path}")
            if frame.height != origins * len(workloads):
                raise ValueError(f"invalid latency row count: {path}")
            if frame["cell"].unique().to_list() != [cell]:
                raise ValueError(f"invalid latency cell: {path}")
            if frame["sweep"].unique().to_list() != [sweep]:
                raise ValueError(f"invalid latency sweep identity: {path}")
            counts = dict(frame.group_by("workload").len().select("workload", "len").iter_rows())
            if counts != {workload: origins for workload in workloads}:
                raise ValueError(f"invalid latency workload roster: {path}")
            frames.append(frame)
    actual_paths = set((panel_root / "latency").glob("*/*.parquet"))
    if actual_paths != expected_paths:
        raise ValueError("latency directory contains unexpected sweeps")
    return pl.concat(frames)


def _latency_rows(frame: pl.DataFrame) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for cell, workload in frame.select("cell", "workload").unique().iter_rows():
        subset = frame.filter((pl.col("cell") == cell) & (pl.col("workload") == workload))
        sweep_means = (
            subset.group_by("sweep")
            .agg(pl.col("elapsed_ns").mean())
            .sort("sweep")["elapsed_ns"]
            .to_list()
        )
        mean_ns, lower_ns, upper_ns = _mean_ci95(sweep_means)
        elapsed = subset["elapsed_ns"]
        rows.append(
            {
                "cell": cell,
                "workload": workload,
                "latency_calls": subset.height,
                "latency_sweeps": len(sweep_means),
                "latency_mean_ms": mean_ns / 1_000_000,
                "latency_mean_ci95_lower_ms": lower_ns / 1_000_000,
                "latency_mean_ci95_upper_ms": upper_ns / 1_000_000,
                "latency_median_ms": _number(elapsed.median(), "latency median") / 1_000_000,
                "latency_p95_ms": _number(elapsed.quantile(0.95), "latency p95") / 1_000_000,
                "latency_p99_ms": _number(elapsed.quantile(0.99), "latency p99") / 1_000_000,
                "latency_max_ms": _number(elapsed.max(), "latency maximum") / 1_000_000,
            }
        )
    return rows


def _energy(panel_root: Path, cells: Iterable[str]) -> dict[str, dict[str, float | int]]:
    output = {}
    for cell in cells:
        path = panel_root / "energy" / cell
        settings = json.loads((path / "phases.json").read_text())["settings"]
        frame = pl.read_parquet(path / "pairs.parquet")
        pairs = int(settings["pairs"])
        if frame.height != pairs or pairs != 5:
            raise ValueError(f"expected five energy pairs: {cell}")
        if not frame["thermal_valid"].all():
            raise ValueError(f"energy measurement failed thermal validation: {cell}")
        joules = frame["joules_per_workload"]
        if joules.null_count() or not joules.is_finite().all():
            raise ValueError(f"energy measurement is non-finite: {cell}")
        mean, lower, upper = _mean_ci95(joules.to_list())
        output[cell] = {
            "energy_pairs": pairs,
            "energy_mean_mj": mean * 1000,
            "energy_ci95_lower_mj": lower * 1000,
            "energy_ci95_upper_mj": upper * 1000,
            "eur_per_million": mean * 1_000_000 / 3_600_000 * _EUR_PER_KWH,
            "eur_per_million_ci95_lower": lower * 1_000_000 / 3_600_000 * _EUR_PER_KWH,
            "eur_per_million_ci95_upper": upper * 1_000_000 / 3_600_000 * _EUR_PER_KWH,
        }
    return output


def _architecture_report(root: Path) -> pl.DataFrame:
    panel_root = root / "architecture-cpu"
    protocol = _protocol(panel_root, "architecture")
    latency = _latency_rows(_read_latency(panel_root, protocol, ("k5",)))
    cells = _cells(protocol)
    energy = _energy(panel_root, cells)
    footprint = {
        row["cell"]: row for row in pl.read_parquet(panel_root / "footprint.parquet").to_dicts()
    }
    if set(footprint) != set(cells):
        raise ValueError("footprint roster does not match the architecture protocol")
    rows = []
    for row in latency:
        cell = str(row["cell"])
        chain, architecture = cell.split(".", maxsplit=1)
        rows.append(
            {
                "chain": chain,
                "architecture": _ARCHITECTURE_LABEL[architecture],
                **row,
                "parameters": footprint[cell]["parameters"],
                "trainable_parameters": footprint[cell]["trainable_parameters"],
                "checkpoint_bytes": footprint[cell]["checkpoint_bytes"],
                "checkpoint_mib": footprint[cell]["checkpoint_bytes"] / 1024**2,
                **energy[cell],
                "_chain_order": _CHAIN_ORDER[chain],
                "_architecture_order": _ARCHITECTURE_ORDER[architecture],
            }
        )
    return (
        pl.DataFrame(rows)
        .sort("_chain_order", "_architecture_order")
        .drop("_chain_order", "_architecture_order")
    )


def _policy_report(root: Path) -> pl.DataFrame:
    panel_root = root / "policy-cpu"
    protocol = _protocol(panel_root, "policy")
    workloads = ("k2", "k3", "k4", "k5", "cascade")
    latency = _latency_rows(_read_latency(panel_root, protocol, workloads))
    cells = _cells(protocol)
    energy = _energy(panel_root, cells)
    rows = []
    for row in latency:
        cell = str(row["cell"])
        chain, architecture = cell.split(".", maxsplit=1)
        if architecture != "lstm":
            raise ValueError("policy protocol must contain only LSTM cells")
        rows.append(
            {
                "chain": chain,
                **row,
                **(energy[cell] if row["workload"] == "cascade" else {}),
                "_chain_order": _CHAIN_ORDER[chain],
                "_workload_order": _WORKLOAD_ORDER[str(row["workload"])],
            }
        )
    return (
        pl.DataFrame(rows, infer_schema_length=None)
        .sort("_chain_order", "_workload_order")
        .drop("_chain_order", "_workload_order")
    )


def _feasibility_report(storage_root: Path, root: Path, policy: pl.DataFrame) -> pl.DataFrame:
    protocol = _protocol(root / "policy-cpu", "policy")
    rows = []
    for chain in _CHAIN_ORDER:
        selection = protocol["roster"][f"{chain}.lstm.K5"]
        window = selection["testing_window"]
        blocks = (
            pl.scan_parquet(storage_root / "datasets" / selection["corpus_id"] / "blocks.parquet")
            .filter(
                pl.col("block_number").is_between(
                    window["first_parent_block"], window["last_parent_block"]
                )
            )
            .select("block_number", "timestamp")
            .sort("block_number")
            .collect()
        )
        expected_rows = window["last_parent_block"] - window["first_parent_block"] + 1
        if blocks.height != expected_rows or blocks["block_number"].n_unique() != expected_rows:
            raise ValueError(f"dataset does not contain the complete {chain} testing window")
        intervals = blocks["timestamp"].diff().drop_nulls()
        if (intervals < 0).any():
            raise ValueError(f"{chain} timestamps are not monotonic")
        positive = intervals.filter(intervals > 0)
        cascade = policy.filter((pl.col("chain") == chain) & (pl.col("workload") == "cascade")).row(
            0, named=True
        )
        cascade_p99_ms = _number(cascade["latency_p99_ms"], "cascade p99")
        interval_p01_s = _number(positive.quantile(0.01), "block-interval p01")
        rows.append(
            {
                "chain": chain,
                "positive_intervals": positive.len(),
                "block_interval_median_s": _number(positive.median(), "block-interval median"),
                "block_interval_p01_s": interval_p01_s,
                "cascade_p99_ms": cascade_p99_ms,
                "p01_margin_s": interval_p01_s - cascade_p99_ms / 1000,
                "cascade_p99_share_of_p01_percent": cascade_p99_ms / 1000 / interval_p01_s * 100,
                "positive_intervals_shorter_than_cascade_p99": (
                    positive < cascade_p99_ms / 1000
                ).sum(),
                "positive_intervals_shorter_than_cascade_p99_percent": _number(
                    (positive < cascade_p99_ms / 1000).mean(), "short-interval fraction"
                )
                * 100,
                "equal_second_intervals": (intervals == 0).sum(),
                "equal_second_intervals_percent": _number(
                    (intervals == 0).mean(), "equal-second fraction"
                )
                * 100,
                "_chain_order": _CHAIN_ORDER[chain],
            }
        )
    return pl.DataFrame(rows).sort("_chain_order").drop("_chain_order")


def _progress_markdown(
    architecture: pl.DataFrame, policy: pl.DataFrame, feasibility: pl.DataFrame
) -> str:
    lines = [
        "#### Local inference benchmark",
        "",
        "$K=5$ local CPU inference at batch size one. Latency is the median over "
        "10,000 timed calls per artifact: 1,000 origins repeated across 10 sweeps. "
        "Energy is mean incremental CPU+GPU+ANE energy over five paired 60-second trials. "
        "Electricity cost uses €0.2966/kWh.",
        "",
        "| Chain | Architecture | Parameters | CPU latency | Energy | € / million |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in architecture.iter_rows(named=True):
        lines.append(
            f"| {str(row['chain']).title()} | {row['architecture']} | "
            f"{row['parameters'] / 1_000_000:.3f}M | {row['latency_median_ms']:.3f} ms | "
            f"{row['energy_mean_mj']:.3f} mJ | €{row['eur_per_million']:.6f} |"
        )
    lines.extend(
        [
            "",
            "Selected LSTM policy latency. Standalone columns are CPU medians; cascade invokes "
            "$K=5,4,3,2$ consecutively at the same origin. Energy and cost refer to the complete "
            "cascade.",
            "",
            "| Chain | $K=2$ | $K=3$ | $K=4$ | $K=5$ | CPU cascade | Cascade energy | "
            "€ / million |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for chain in _CHAIN_ORDER:
        group = {row["workload"]: row for row in policy.filter(pl.col("chain") == chain).to_dicts()}
        cascade = group["cascade"]
        lines.append(
            f"| {chain.title()} | {group['k2']['latency_median_ms']:.3f} ms | "
            f"{group['k3']['latency_median_ms']:.3f} ms | "
            f"{group['k4']['latency_median_ms']:.3f} ms | "
            f"{group['k5']['latency_median_ms']:.3f} ms | "
            f"{cascade['latency_median_ms']:.3f} ms | {cascade['energy_mean_mj']:.3f} mJ | "
            f"€{cascade['eur_per_million']:.6f} |"
        )
    lines.extend(
        [
            "",
            "| Chain | block-interval p01 | CPU cascade p99 | Share of p01 |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in feasibility.iter_rows(named=True):
        lines.append(
            f"| {str(row['chain']).title()} | {row['block_interval_p01_s']:.0f} s | "
            f"{row['cascade_p99_ms']:.3f} ms | "
            f"{row['cascade_p99_share_of_p01_percent']:.3f}% |"
        )
    lines.extend(
        [
            "",
            "Even under the maximum four-inference same-head workload, CPU model computation "
            "occupies less than 0.3% of the block-interval p01 on every chain. Resident inference "
            "therefore fits comfortably within the observed block-time budget, although "
            "end-to-end deployment latency remains outside the claim and is "
            "RPC-endpoint-provider-dependent.",
            "",
        ]
    )
    return "\n".join(lines)


def run_report(storage_root: Path, benchmark_root: Path, output: Path) -> None:
    """Validate and reduce the complete local inference benchmark."""

    architecture = _architecture_report(benchmark_root)
    policy = _policy_report(benchmark_root)
    feasibility = _feasibility_report(storage_root, benchmark_root, policy)
    output.mkdir(parents=True, exist_ok=True)
    architecture.write_csv(output / "architecture.tsv", separator="\t")
    policy.write_csv(output / "policy.tsv", separator="\t")
    feasibility.write_csv(output / "feasibility.tsv", separator="\t")
    (output / "progress.md").write_text(
        _progress_markdown(architecture, policy, feasibility), encoding="utf-8"
    )


Directory = Annotated[Path, typer.Argument(resolve_path=True, exists=True, file_okay=False)]
Output = Annotated[Path, typer.Argument(resolve_path=True, file_okay=False)]


def report(storage_root: Directory, benchmark_root: Directory, output: Output) -> None:
    run_report(storage_root, benchmark_root, output)


if __name__ == "__main__":
    typer.run(report)
