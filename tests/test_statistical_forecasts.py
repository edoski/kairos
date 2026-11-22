import numpy as np
import pandas as pd
import pytest

from experiments.math_exp.stats_analysis.step11 import validation


def test_crps_matches_pairwise_definition_and_degenerate_forecast():
    samples = np.array([0.0, 1.0, 4.0])
    expected = np.abs(samples - 2).mean() - 0.5 * np.abs(samples[:, None] - samples).mean()
    assert validation.ensemble_crps(samples, 2) == pytest.approx(expected)
    assert validation.ensemble_crps([3], 5) == 2
    with pytest.raises(ValueError):
        validation.ensemble_crps([], 5)


def test_zero_atoms_and_upper_overflow_bins_are_distinct():
    x_edges, y_edges = np.array([1.0]), np.array([10.0])
    values = np.array([[0, 0], [0.1, 0.1], [2, 100]])
    encoded = validation.joint_categories(values, x_edges, y_edges)
    assert encoded.tolist() == [0, 4, 11]
    with pytest.raises(ValueError):
        validation.joint_categories([[2.1, 1]], x_edges, y_edges)


def test_raw_fee_mean_is_not_the_exponential_of_mean_log_fee():
    draws = np.array([[1.0, 0.0], [1.0, 2.0]])
    scores = validation.score_forecast(
        draws, np.array([1.0, 1.0]), np.array([1.0]), np.array([1.0]), np.random.default_rng(2)
    )
    assert scores["mean_P_gwei"] == pytest.approx(np.expm1(draws[:, 1]).mean() / 1e9)
    assert scores["mean_P_gwei"] != pytest.approx(np.expm1(draws[:, 1].mean()) / 1e9, abs=1e-12)
    assert np.isfinite(scores["joint_log_score"])


def test_rolling_fit_never_reads_a_future_target(monkeypatch):
    frame = pd.DataFrame(
        {
            "block_number": np.arange(20004),
            "timestamp": np.arange(20004) * 12,
            "X": np.full(20004, 1.0),
            validation.Y_COLUMN: np.full(20004, 2.0),
        }
    )
    fits = []

    def fit(training, name):
        fits.append(int(training.block_number.iloc[-1]))
        return type("Model", (), {"next_variance": None})()

    def sample(model, x, y, size, rng, variance):
        return np.tile([x, y], (size, 1)), None

    monkeypatch.setattr(validation, "CANDIDATES", ("baseline",))
    monkeypatch.setattr(validation, "fit_candidate", fit)
    monkeypatch.setattr(validation, "sample_joint", sample)
    first = validation.rolling_forecasts(
        frame, "test", "testing", 20000, 20003, draws=4, refit_every=2
    )
    changed = frame.copy()
    changed.loc[20002:, validation.Y_COLUMN] = 50
    second = validation.rolling_forecasts(
        changed, "test", "testing", 20000, 20003, draws=4, refit_every=2
    )
    assert fits == [19999, 20001, 19999, 20001]
    assert np.array_equal(first.loc[:1, "mean_Y"], second.loc[:1, "mean_Y"])
    assert (first.training_last_block < first.block_number).all()
