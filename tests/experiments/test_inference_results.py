from __future__ import annotations

import json
import math
from pathlib import Path

import polars as pl
import pytest

import experiments.inference_results as results


def test_latency_confidence_interval_uses_ten_sweep_means() -> None:
    frame = pl.DataFrame(
        {
            "cell": ["ethereum.lstm"] * 20,
            "workload": ["k5"] * 20,
            "sweep": [sweep for sweep in range(1, 11) for _ in range(2)],
            "elapsed_ns": [value for value in range(1, 11) for _ in range(2)],
        }
    )

    row = results._latency_rows(frame)[0]
    expected_half_width = 2.2621571627409915 * math.sqrt(55 / 6) / math.sqrt(10)

    assert row["latency_calls"] == 20
    assert row["latency_sweeps"] == 10
    assert row["latency_mean_ms"] == pytest.approx(5.5e-6)
    assert row["latency_mean_ci95_lower_ms"] == pytest.approx(
        (5.5 - expected_half_width) / 1_000_000
    )
    assert row["latency_mean_ci95_upper_ms"] == pytest.approx(
        (5.5 + expected_half_width) / 1_000_000
    )
    assert row["latency_median_ms"] == pytest.approx(5.5e-6)


def test_energy_confidence_interval_uses_five_paired_trials(tmp_path: Path) -> None:
    cell = "ethereum.lstm"
    path = tmp_path / "energy" / cell
    path.mkdir(parents=True)
    (path / "phases.json").write_text(json.dumps({"settings": {"pairs": 5}}))
    pl.DataFrame(
        {"thermal_valid": [True] * 5, "joules_per_workload": [0.001, 0.002, 0.003, 0.004, 0.005]}
    ).write_parquet(path / "pairs.parquet")

    row = results._energy(tmp_path, (cell,))[cell]
    expected_half_width = 2.7764451051977987 * math.sqrt(2.5e-6) / math.sqrt(5)

    assert row["energy_pairs"] == 5
    assert row["energy_mean_mj"] == pytest.approx(3.0)
    assert row["energy_ci95_lower_mj"] == pytest.approx((0.003 - expected_half_width) * 1000)
    assert row["energy_ci95_upper_mj"] == pytest.approx((0.003 + expected_half_width) * 1000)
    assert row["eur_per_million"] == pytest.approx(0.003 * 1_000_000 / 3_600_000 * 0.2966)


def test_energy_reduction_rejects_invalid_measurements(tmp_path: Path) -> None:
    cell = "ethereum.lstm"
    path = tmp_path / "energy" / cell
    path.mkdir(parents=True)
    (path / "phases.json").write_text(json.dumps({"settings": {"pairs": 5}}))
    pl.DataFrame(
        {
            "thermal_valid": [True, True, False, True, True],
            "joules_per_workload": [0.001, 0.002, 0.003, 0.004, 0.005],
        }
    ).write_parquet(path / "pairs.parquet")

    with pytest.raises(ValueError, match="thermal validation"):
        results._energy(tmp_path, (cell,))
