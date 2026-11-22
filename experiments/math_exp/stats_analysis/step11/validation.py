"""Rolling one-block forecasts and scores for the research notebooks."""

import numpy as np
import pandas as pd

from experiments.math_exp.stats_analysis.step10.transition_models import (
    CANDIDATES,
    Y_COLUMN,
    fit_candidate,
    sample_joint,
)


def ensemble_crps(samples, observed):
    """CRPS of the equally weighted empirical forecast, in the sample's units."""
    samples = np.asarray(samples, dtype=float)
    if samples.ndim != 1 or not len(samples) or not np.isfinite(samples).all():
        raise ValueError("forecast samples must be a nonempty finite vector")
    if not np.isfinite(observed):
        raise ValueError("the observed value must be finite")
    ordered = np.sort(samples)
    weights = 2 * np.arange(1, len(samples) + 1) - len(samples) - 1
    return float(np.abs(samples - observed).mean() - weights @ ordered / len(samples) ** 2)


def category_edges(training):
    y_edges = np.unique(np.quantile(training[Y_COLUMN], [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]))
    return np.array([0.5, 1, 1.5, 1.8]), y_edges[y_edges > 0]


def joint_categories(values, x_edges, y_edges):
    """Separate the boundary atoms; use common training-only bins for positive values."""
    values = np.atleast_2d(np.asarray(values, dtype=float))
    if values.shape[1] != 2 or not np.isfinite(values).all():
        raise ValueError("joint values must be finite X,Y pairs")
    if np.any((values[:, 0] < 0) | (values[:, 0] > 2) | (values[:, 1] < 0)):
        raise ValueError("joint values violate the physical support")
    x = np.where(values[:, 0] == 0, 0, 1 + np.searchsorted(x_edges, values[:, 0], side="right"))
    x = np.where(values[:, 0] == 2, len(x_edges) + 2, x)
    y = np.where(values[:, 1] == 0, 0, 1 + np.searchsorted(y_edges, values[:, 1], side="right"))
    return x * (len(y_edges) + 2) + y


def score_forecast(draws, observed, x_edges, y_edges, rng):
    if np.any(draws[:, 1] > np.log(np.finfo(float).max) - 2):
        raise OverflowError("forecast priority fee exceeds numerical support")
    categories = joint_categories(draws, x_edges, y_edges)
    observed_category = joint_categories(observed, x_edges, y_edges)[0]
    cells = (len(x_edges) + 3) * (len(y_edges) + 2)
    # This scores a regularized categorical forecast, not a continuous joint log density.
    probability = ((categories == observed_category).sum() + 0.5) / (len(draws) + 0.5 * cells)
    result = {"joint_log_score": np.log(probability)}
    for label, samples, actual in [
        ("X", draws[:, 0], observed[0]),
        ("Y", draws[:, 1], observed[1]),
        ("P_gwei", np.expm1(draws[:, 1]) / 1e9, np.expm1(observed[1]) / 1e9),
    ]:
        # shortcut: media Monte Carlo, aumentare i campioni per decisioni sensibili alle code.
        prediction = samples.mean()
        result.update(
            {
                f"actual_{label}": actual,
                f"mean_{label}": prediction,
                f"error_{label}": actual - prediction,
                f"CRPS_{label}": ensemble_crps(samples, actual),
            }
        )
        for quantile, value in zip(
            [50, 90, 95, 99], np.quantile(samples, [0.5, 0.9, 0.95, 0.99]), strict=True
        ):
            result[f"q{quantile}_{label}"] = value
        if label != "P_gwei":
            # Randomized ensemble rank handles ties from the zero/boundary atoms.
            result[f"PIT_{label}"] = (
                (samples < actual).sum() + rng.random() * ((samples == actual).sum() + 1)
            ) / (len(samples) + 1)
    result["forecast_zero_X"] = np.mean(draws[:, 0] == 0)
    result["forecast_full_X"] = np.mean(draws[:, 0] == 2)
    result["forecast_zero_Y"] = np.mean(draws[:, 1] == 0)
    return result


def rolling_forecasts(frame, period, role, start, stop, draws=128, refit_every=1000):
    """Refit on the preceding 20k closed blocks; forecast every next block."""
    if not 20000 <= start < stop <= len(frame) or draws < 2 or refit_every < 1:
        raise ValueError("invalid rolling forecast window")
    if not frame.block_number.diff().iloc[1:].eq(1).all():
        raise ValueError("rolling forecasts require consecutive blocks")
    x_edges, y_edges = category_edges(frame.iloc[:20000])
    records = []
    for name in CANDIDATES:
        for target in range(start, stop):
            if (target - start) % refit_every == 0:
                training = frame.iloc[target - 20000 : target]
                model = fit_candidate(training, name)
                variance = model.next_variance
                training_last = int(training.block_number.iloc[-1])
            parent = frame.iloc[target - 1]
            actual = frame.iloc[target]
            assert training_last < actual.block_number
            # The same seed per origin makes each rerun deterministic across model comparisons.
            rng = np.random.default_rng(int(actual.block_number))
            samples, _ = sample_joint(model, parent.X, parent[Y_COLUMN], draws, rng, variance)
            scores = score_forecast(
                samples, np.array([actual.X, actual[Y_COLUMN]]), x_edges, y_edges, rng
            )
            records.append(
                {
                    "period": period,
                    "role": role,
                    "model": name,
                    "block_number": int(actual.block_number),
                    "timestamp": int(actual.timestamp),
                    "training_last_block": training_last,
                    "previous_X": float(parent.X),
                    **scores,
                }
            )
            if name == "garch":
                omega, alpha, beta = model.garch_parameters
                error = actual[Y_COLUMN] - (
                    model.coefficients[1, 0] + model.coefficients[1, 1] * parent[Y_COLUMN]
                )
                variance = omega + alpha * error**2 + beta * variance
        print(f"{period}, {role}: {name}, {stop - start} origini completate", flush=True)
    return pd.DataFrame(records)
