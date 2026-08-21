"""Time-cluster uncertainty summaries for held-out metrics."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

INTERVAL_METRICS = (
    "accuracy",
    "f1_macro",
    "log_fee_mae",
    "log_fee_mse",
    "base_fee_savings",
    "base_fee_optimality_gap",
)


def symmetric_trimmed_mean(values: np.ndarray, proportion_per_tail: float) -> float:
    """Return the mean after removing equal rank-based tails."""

    if values.ndim != 1 or values.size == 0:
        raise ValueError("values must be a nonempty vector")
    if not 0.0 <= proportion_per_tail < 0.5:
        raise ValueError("proportion_per_tail must be in [0, 0.5)")
    cut = int(np.floor(proportion_per_tail * values.size))
    if cut == 0:
        return float(np.mean(values))
    partitioned = np.partition(values, (cut, values.size - cut - 1))
    return float(np.mean(partitioned[cut:-cut]))


def clustered_mean_intervals(
    samples: Mapping[str, np.ndarray],
    clusters: np.ndarray,
    *,
    confidence: float = 0.95,
    resamples: int = 5_000,
    seed: int = 2026,
) -> dict[str, tuple[float, float]]:
    """Bootstrap paired row-level quantities by complete time cluster."""

    if clusters.ndim != 1 or clusters.size == 0:
        raise ValueError("clusters must identify every nonempty observation row")
    if not samples or any(values.shape != clusters.shape for values in samples.values()):
        raise ValueError("samples must contain one value per cluster-labelled row")
    if not 0.0 < confidence < 1.0 or resamples <= 0:
        raise ValueError("confidence and resamples must be positive and bounded")

    _, inverse = np.unique(clusters, return_inverse=True)
    cluster_count = int(inverse.max()) + 1
    row_counts = np.bincount(inverse, minlength=cluster_count).astype(np.float64)
    names = tuple(samples)
    cluster_sums = np.column_stack(
        [
            np.bincount(inverse, weights=samples[name], minlength=cluster_count)
            for name in names
        ]
    )

    draws = np.empty((resamples, len(names)), dtype=np.float64)
    rng = np.random.default_rng(seed)
    probability = np.full(cluster_count, 1.0 / cluster_count)
    start = 0
    while start < resamples:
        stop = min(start + 128, resamples)
        weights = rng.multinomial(cluster_count, probability, size=stop - start)
        draws[start:stop] = (weights @ cluster_sums) / (weights @ row_counts)[:, None]
        start = stop

    tail = (1.0 - confidence) / 2.0
    bounds = np.quantile(draws, (tail, 1.0 - tail), axis=0)
    return {
        name: (float(bounds[0, index]), float(bounds[1, index]))
        for index, name in enumerate(names)
    }


def clustered_metric_intervals(
    columns: Mapping[str, np.ndarray],
    clusters: np.ndarray,
    *,
    confidence: float = 0.95,
    resamples: int = 5_000,
    seed: int = 2026,
) -> dict[str, tuple[float, float]]:
    """Bootstrap complete time clusters and return metric confidence limits."""

    origins = columns["origin_block"]
    if origins.ndim != 1 or origins.size == 0 or clusters.shape != origins.shape:
        raise ValueError("clusters must identify every nonempty observation row")
    if not 0.0 < confidence < 1.0 or resamples <= 0:
        raise ValueError("confidence and resamples must be positive and bounded")

    _, inverse = np.unique(clusters, return_inverse=True)
    cluster_count = int(inverse.max()) + 1
    row_counts = np.bincount(inverse, minlength=cluster_count).astype(np.float64)

    immediate = columns["immediate_base_fee_per_gas"].astype(np.float64)
    selected = columns["selected_base_fee_per_gas"].astype(np.float64)
    minimum = columns["minimum_base_fee_per_gas"].astype(np.float64)
    log_errors = columns["predicted_minimum_log_base_fee"] - np.log(minimum)
    row_metrics = np.column_stack(
        (
            columns["predicted_action_k"] == columns["minimum_action_k"],
            np.abs(log_errors),
            np.square(log_errors),
            (immediate - selected) / immediate,
            (selected - minimum) / minimum,
        )
    )
    cluster_sums = np.column_stack(
        [
            np.bincount(inverse, weights=row_metrics[:, index], minlength=cluster_count)
            for index in range(row_metrics.shape[1])
        ]
    )

    predicted = columns["predicted_action_k"]
    truth = columns["minimum_action_k"]
    class_count = max(int(predicted.max()), int(truth.max())) + 1
    cluster_truth = np.zeros((cluster_count, class_count), dtype=np.float64)
    cluster_predictions = np.zeros_like(cluster_truth)
    cluster_true_positives = np.zeros_like(cluster_truth)
    np.add.at(cluster_truth, (inverse, truth), 1.0)
    np.add.at(cluster_predictions, (inverse, predicted), 1.0)
    matches = predicted == truth
    np.add.at(cluster_true_positives, (inverse[matches], truth[matches]), 1.0)

    draws = {metric: np.empty(resamples, dtype=np.float64) for metric in INTERVAL_METRICS}
    rng = np.random.default_rng(seed)
    probability = np.full(cluster_count, 1.0 / cluster_count)
    start = 0
    while start < resamples:
        stop = min(start + 128, resamples)
        weights = rng.multinomial(cluster_count, probability, size=stop - start)
        totals = weights @ row_counts
        means = (weights @ cluster_sums) / totals[:, None]
        draws["accuracy"][start:stop] = means[:, 0]
        draws["log_fee_mae"][start:stop] = means[:, 1]
        draws["log_fee_mse"][start:stop] = means[:, 2]
        draws["base_fee_savings"][start:stop] = means[:, 3]
        draws["base_fee_optimality_gap"][start:stop] = means[:, 4]

        truth_counts = weights @ cluster_truth
        prediction_counts = weights @ cluster_predictions
        true_positives = weights @ cluster_true_positives
        denominators = truth_counts + prediction_counts
        present = denominators > 0.0
        f1 = np.divide(
            2.0 * true_positives, denominators, out=np.zeros_like(denominators), where=present
        )
        draws["f1_macro"][start:stop] = np.sum(f1, axis=1) / np.sum(present, axis=1)
        start = stop

    tail = (1.0 - confidence) / 2.0
    intervals = {}
    for metric, values in draws.items():
        lower, upper = np.quantile(values, (tail, 1.0 - tail))
        intervals[metric] = (float(lower), float(upper))
    return intervals
