"""Boundary, chronology and exact-protocol checks for the research kernels."""

import numpy as np
import pandas as pd
import pytest

from experiments.math_exp.stats_analysis.step10.transition_models import (
    CANDIDATES,
    Y_COLUMN,
    filtered_variance,
    fit_candidate,
    sample_joint,
    simulate_paths,
)
from kairos.temporal import _forming_child_base_fee


@pytest.fixture
def training():
    rng = np.random.default_rng(17)
    x = rng.uniform(0, 2, 1600)
    y = 5 + 0.8 * x + rng.normal(0, 0.2, len(x))
    x[::200], y[::200] = 0, 0
    return pd.DataFrame({"X": x, Y_COLUMN: y, "block_number": np.arange(len(x))})


@pytest.mark.parametrize("name", CANDIDATES)
def test_joint_draws_are_repeatable_bounded_and_finite(training, name):
    model = fit_candidate(training, name)
    first, variance = sample_joint(model, 0.7, 5, 500, np.random.default_rng(4))
    repeated, _ = sample_joint(model, 0.7, 5, 500, np.random.default_rng(4))
    assert np.array_equal(first, repeated)
    assert np.isfinite(first).all()
    assert np.all((first[:, 0] >= 0) & (first[:, 0] <= 2))
    assert np.all(first[:, 1] >= 0)
    if variance is not None:
        assert np.isfinite(variance).all() and (variance > 0).all()
    if name == "regime":
        expected_high = model.transitions[0, 1]
        assert abs((first[:, 0] >= 1.5).mean() - expected_high) < 0.1
    if name == "empirical":
        assert all(np.any(np.all(model.outcomes == row, axis=1)) for row in first)
    if name == "mixture":
        assert model.diagnostics["mixture_converged"]
        assert np.isclose(model.mixture[0].sum(), 1)


def test_empirical_fallback_keeps_real_joint_outcomes(training):
    model = fit_candidate(training, "empirical")
    model.conditional_pools.clear()
    draws, _ = sample_joint(model, 2, 100, 4000, np.random.default_rng(5))
    assert draws[:, 1].max() <= training[Y_COLUMN].max()
    assert np.any((draws[:, 0] == 0) & (draws[:, 1] == 0))


def test_garch_filter_consumes_only_observed_history(training):
    model = fit_candidate(training, "garch")
    observed = pd.DataFrame({Y_COLUMN: [5.0, 4.0]})
    omega, alpha, beta = model.garch_parameters
    previous_y, expected = model.training_last_y, model.next_variance
    for y in observed[Y_COLUMN]:
        error = y - (model.coefficients[1, 0] + model.coefficients[1, 1] * previous_y)
        expected = omega + alpha * error**2 + beta * expected
        previous_y = y
    assert filtered_variance(model, observed) == pytest.approx(expected)
    assert filtered_variance(model, observed.iloc[:0]) == model.next_variance


def test_simulated_base_fee_uses_parent_then_integer_gas(training):
    model = fit_candidate(training, "empirical")
    parent = pd.Series(
        {"X": 1.0, Y_COLUMN: 5.0, "base_fee_per_gas": 1000, "gas_used": 50, "gas_limit": 101}
    )
    paths = simulate_paths(model, parent, 4, 50, np.random.default_rng(8))
    assert np.all(paths["B"][:, 0] == 1000)
    assert np.allclose(paths["X"] * 101 / 2, np.rint(paths["X"] * 101 / 2))
    assert np.isfinite(paths["P"]).all()
    for row in range(50):
        for step in range(1, 4):
            expected = _forming_child_base_fee(
                int(paths["B"][row, step - 1]), round(paths["X"][row, step - 1] * 101 / 2), 101
            )
            assert paths["B"][row, step] == expected


def test_rejects_gaps_bad_states_and_overflow(training):
    bad = training.copy()
    bad.loc[10, "block_number"] += 1
    with pytest.raises(ValueError, match="consecutivi"):
        fit_candidate(bad, "baseline")
    with pytest.raises(ValueError, match="sconosciuto"):
        fit_candidate(training, "missing")
    model = fit_candidate(training, "baseline")
    with pytest.raises(ValueError, match="supporto"):
        sample_joint(model, 3, 5, 1, np.random.default_rng(3))
    parent = pd.Series(
        {"X": 1.0, Y_COLUMN: 10000.0, "base_fee_per_gas": 1000, "gas_used": 50, "gas_limit": 100}
    )
    model.coefficients[1] = [10000, 0]
    with pytest.raises(OverflowError, match="numerico"):
        simulate_paths(model, parent, 1, 1, np.random.default_rng(1))


@pytest.mark.parametrize("gas_limit", [101, 103])
def test_integer_gas_projection_keeps_sampled_regime(training, gas_limit):
    model = fit_candidate(training, "regime")
    parent = pd.Series(
        {"X": 1.0, Y_COLUMN: 5.0, "base_fee_per_gas": 1000, "gas_used": 50, "gas_limit": gas_limit}
    )
    assigned, _ = sample_joint(model, 1.0, 5.0, 2000, np.random.default_rng(12))
    paths = simulate_paths(model, parent, 1, 2000, np.random.default_rng(12))
    assert np.array_equal(assigned[:, 0] >= 1.5, paths["X"][:, 0] >= 1.5)
