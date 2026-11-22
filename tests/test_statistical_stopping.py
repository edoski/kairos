from types import SimpleNamespace

import numpy as np
import pytest

from experiments.math_exp.stats_analysis.step11 import stopping


def surface_for(monkeypatch, utilization, **kwargs):
    def deterministic_joint(model, x, y, size, rng):
        return np.column_stack([np.full(size, utilization), np.zeros(size)]), None

    monkeypatch.setattr(stopping, "sample_joint", deterministic_joint)
    return stopping.solve_bellman(
        SimpleNamespace(name="empirical"),
        np.arange(100, 2001, 10),
        [0, 1, 2],
        [0, 1],
        gas_limit=100,
        draws=2,
        **kwargs,
    )


@pytest.mark.parametrize("utilization,expected_stop", [(0, False), (1, True), (2, True)])
def test_bellman_waits_for_decreasing_cost_and_stops_on_ties(
    monkeypatch, utilization, expected_stop
):
    surface = surface_for(monkeypatch, utilization, horizon=5, fixed_offer=0)
    assert stopping.decision(surface, 1000, 1, 0, remaining=5) is expected_stop


def test_terminal_action_is_forced_even_outside_interpolation_grid(monkeypatch):
    surface = surface_for(monkeypatch, 0, horizon=1)
    assert stopping.decision(surface, 3000, 2, 2, remaining=1)
    assert surface.stop_masks[1].all()


def test_offered_cost_uses_previous_fee_and_has_wei_units(monkeypatch):
    surface = surface_for(monkeypatch, 1, horizon=1, offer_multiplier=2)
    expected = surface.base_grids[1][:, None, None] + 2 * np.expm1(surface.y_grid)[None, None, :]
    assert np.allclose(surface.values[1], np.broadcast_to(expected, surface.values[1].shape))


def test_exact_integer_rounding_can_make_waiting_pointless_at_one_wei(monkeypatch):
    monkeypatch.setattr(
        stopping, "sample_joint", lambda model, x, y, size, rng: (np.zeros((size, 2)), None)
    )
    surface = stopping.solve_bellman(
        SimpleNamespace(name="empirical"),
        np.arange(1, 21),
        [0, 1, 2],
        [0, 1],
        gas_limit=101,
        fixed_offer=0,
        horizon=2,
        draws=2,
    )
    assert stopping.decision(surface, 1, 0, 0, remaining=2)
    assert surface.continuations[2][0, 0, 0] == 1


def test_adaptive_recursion_takes_expectation_after_future_stop_decision(monkeypatch):
    high_y = np.log1p(1000)

    def branching_joint(model, x, y, size, rng):
        if x == 0.5:
            return np.array([[1, 0], [1, high_y]]), None
        return np.tile([2 if y == 0 else 0, 0], (size, 1)), None

    monkeypatch.setattr(stopping, "sample_joint", branching_joint)
    surface = stopping.solve_bellman(
        SimpleNamespace(name="empirical"),
        np.arange(100, 3001, 25),
        [0, 0.5, 1, 2],
        [0, high_y],
        gas_limit=100,
        horizon=3,
        draws=2,
    )
    row = np.flatnonzero(surface.base_grids[3] == 1000)[0]
    # Next decision: stop in the low-tip branch, wait in the high-tip branch.
    assert surface.continuations[3][row, 1, 0] == pytest.approx((1000 + 875) / 2)
    assert not stopping.decision(surface, 1000, 0.5, 0, remaining=3)
    assert min(np.mean([1000, 2000]), np.mean([1125, 875])) == 1000


def test_interpolation_preserves_cost_in_raw_fee_units(monkeypatch):
    monkeypatch.setattr(
        stopping,
        "sample_joint",
        lambda model, x, y, size, rng: (np.tile([1, np.log1p(50)], (size, 1)), None),
    )
    surface = stopping.solve_bellman(
        SimpleNamespace(name="empirical"),
        np.arange(100, 2001, 10),
        [0, 1, 2],
        [0, np.log1p(100)],
        gas_limit=100,
        horizon=2,
        draws=2,
    )
    row = np.flatnonzero(surface.base_grids[2] == 1000)[0]
    assert surface.continuations[2][row, 1, 1] == pytest.approx(1050)
    assert stopping.decision(surface, 1000, 1, np.log1p(40), 2)
    assert not stopping.decision(surface, 1000, 1, np.log1p(60), 2)


def test_state_domain_shrinks_without_silent_extrapolation(monkeypatch):
    surface = surface_for(monkeypatch, 2, horizon=5, fixed_offer=0)
    assert surface.base_grids[5][-1] < surface.base_grids[1][-1]
    with pytest.raises(ValueError):
        stopping.decision(surface, 2000, 1, 0, remaining=5)
    with pytest.raises(ValueError):
        stopping.decision(surface, 1000, 1, 2, remaining=5)


def test_odd_limit_rounding_cannot_silently_leave_the_utilization_grid(monkeypatch):
    monkeypatch.setattr(
        stopping,
        "sample_joint",
        lambda model, x, y, size, rng: (np.tile([0.5, 0], (size, 1)), None),
    )
    with pytest.raises(ValueError, match="rounded utilization"):
        stopping.solve_bellman(
            SimpleNamespace(name="empirical"),
            np.arange(100, 2001, 10),
            [0.5, 2],
            [0, 1],
            gas_limit=101,
            horizon=2,
            draws=2,
        )


def test_invalid_cost_and_state_are_rejected(monkeypatch):
    with pytest.raises(ValueError, match="non-finite offered cost"):
        stopping.solve_bellman(
            SimpleNamespace(name="empirical"),
            [100, 1000],
            [0, 2],
            [0, 1000],
            gas_limit=100,
            horizon=1,
        )
    surface = surface_for(monkeypatch, 1, horizon=1)
    with pytest.raises(ValueError, match="invalid observable state"):
        stopping.decision(surface, 1000, 3, 0, remaining=1)


def test_joint_outcomes_need_full_state_grid_support(monkeypatch):
    def invalid_joint(model, x, y, size, rng):
        return np.column_stack([np.full(size, 2.1), np.zeros(size)]), None

    monkeypatch.setattr(stopping, "sample_joint", invalid_joint)
    with pytest.raises(ValueError, match="outside the supplied state grids"):
        stopping.solve_bellman(
            SimpleNamespace(name="empirical"),
            [100, 1000],
            [0, 2],
            [0, 1],
            gas_limit=100,
            horizon=2,
            draws=2,
        )
