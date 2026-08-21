from __future__ import annotations

import numpy as np
import pytest

from kairos.statistics import (
    clustered_mean_intervals,
    clustered_metric_intervals,
    symmetric_trimmed_mean,
)


def test_symmetric_trimmed_mean_removes_exact_ranked_tails() -> None:
    values = np.concatenate((np.array([-1_000.0]), np.zeros(38), np.array([100.0])))

    assert symmetric_trimmed_mean(values, 0.025) == 0.0


def test_clustered_metric_intervals_resample_whole_clusters_deterministically() -> None:
    minimum = np.full(4, 5, dtype=np.int64)
    columns = {
        "origin_block": np.arange(4, dtype=np.int64),
        "predicted_action_k": np.array([0, 1, 0, 1], dtype=np.int64),
        "predicted_minimum_log_base_fee": np.log(minimum),
        "minimum_action_k": np.array([0, 1, 0, 1], dtype=np.int64),
        "immediate_base_fee_per_gas": np.full(4, 10, dtype=np.int64),
        "selected_base_fee_per_gas": minimum,
        "minimum_base_fee_per_gas": minimum,
    }

    result = clustered_metric_intervals(columns, np.array([0, 0, 1, 1]), resamples=20, seed=7)

    assert result == pytest.approx(
        {
            "accuracy": (1.0, 1.0),
            "f1_macro": (1.0, 1.0),
            "log_fee_mae": (0.0, 0.0),
            "log_fee_mse": (0.0, 0.0),
            "base_fee_savings": (0.5, 0.5),
            "base_fee_optimality_gap": (0.0, 0.0),
        }
    )


def test_clustered_mean_intervals_preserve_paired_cluster_differences() -> None:
    result = clustered_mean_intervals(
        {
            "one_shot": np.array([0.0, 0.0, 2.0, 2.0]),
            "rolling": np.array([1.0, 1.0, 3.0, 3.0]),
            "delta": np.ones(4),
        },
        np.array([0, 0, 1, 1]),
        resamples=20,
        seed=7,
    )

    assert result["delta"] == (1.0, 1.0)
