"""Finite-horizon stopping on the joint empirical kernel, in wei/gas."""

from dataclasses import dataclass
from operator import index

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from experiments.math_exp.stats_analysis.step10.transition_models import sample_joint
from kairos.temporal import _forming_child_base_fee


@dataclass
class BellmanSurface:
    base_grids: dict[int, np.ndarray]
    values: dict[int, np.ndarray]
    continuations: dict[int, np.ndarray]
    stop_masks: dict[int, np.ndarray]
    x_grid: np.ndarray
    y_grid: np.ndarray
    gas_limit: int
    offer_multiplier: float
    fixed_offer: float | None


def _cost(base_fee, previous_log_priority_fee, multiplier, fixed_offer):
    try:
        with np.errstate(over="raise", invalid="raise"):
            offer = fixed_offer
            if offer is None:
                offer = 0 if multiplier == 0 else multiplier * np.expm1(previous_log_priority_fee)
            cost = np.asarray(base_fee) + offer
    except FloatingPointError as exc:
        raise ValueError("non-finite offered cost") from exc
    if not np.isfinite(cost).all():
        raise ValueError("non-finite offered cost")
    return cost


def solve_bellman(
    model,
    base_grid,
    x_grid,
    y_grid,
    gas_limit,
    offer_multiplier=1.0,
    fixed_offer=None,
    horizon=5,
    draws=64,
    seed=17,
):
    """Use paired empirical draws; hold the supplied gas limit fixed in every future block.

    B grids shrink with the remaining horizon so interpolation never extrapolates.
    X draws are mapped to integer gas usage on this fixed limit, with nearest-even rounding.
    """
    gas_limit, horizon, draws = map(index, (gas_limit, horizon, draws))
    if gas_limit < 2 or gas_limit > 2**53 or horizon < 1 or draws < 1:
        raise ValueError("invalid gas limit, horizon or draw count")
    if getattr(model, "name", None) != "empirical":
        raise ValueError("this Bellman state supports only the empirical joint kernel")
    if not np.isfinite(offer_multiplier) or offer_multiplier < 0:
        raise ValueError("offer multiplier must be finite and nonnegative")
    if fixed_offer is not None and (not np.isfinite(fixed_offer) or fixed_offer < 0):
        raise ValueError("fixed offer must be finite and nonnegative")
    grids = [np.asarray(grid, dtype=float) for grid in (base_grid, x_grid, y_grid)]
    if any(
        grid.ndim != 1
        or len(grid) < 2
        or not np.isfinite(grid).all()
        or not np.all(np.diff(grid) > 0)
        for grid in grids
    ):
        raise ValueError("grids must be finite, strictly increasing one-dimensional arrays")
    base_grid, x_grid, y_grid = grids
    if (
        base_grid[0] <= 0
        or base_grid[-1] > 2**53
        or not np.equal(base_grid, np.rint(base_grid)).all()
    ):
        raise ValueError("base grid must contain positive exactly representable integer wei")
    if x_grid[0] < 0 or x_grid[-1] > 2 or y_grid[0] < 0:
        raise ValueError("state grid violates X in [0, 2] or nonnegative log priority fee")
    # Raw-fee coordinates preserve affine offered costs between the log-state grid nodes.
    priority_grid = _cost(0, y_grid, 1, None)
    immediate = np.broadcast_to(
        _cost(base_grid[:, None, None], y_grid[None, None, :], offer_multiplier, fixed_offer),
        (len(base_grid), len(x_grid), len(y_grid)),
    ).copy()
    surface = BellmanSurface(
        {1: base_grid},
        {1: immediate},
        {1: np.full_like(immediate, np.inf)},
        {1: np.ones_like(immediate, dtype=bool)},
        x_grid,
        y_grid,
        gas_limit,
        offer_multiplier,
        fixed_offer,
    )
    if horizon == 1:
        return surface
    rng = np.random.default_rng(seed)
    joint = np.empty((len(x_grid), len(y_grid), draws, 2))
    for i, x in enumerate(x_grid):
        for j, y in enumerate(y_grid):
            joint[i, j], _ = sample_joint(model, x, y, draws, rng)
    if (
        not np.isfinite(joint).all()
        or (
            (joint[..., 0] < x_grid[0])
            | (joint[..., 0] > x_grid[-1])
            | (joint[..., 1] < y_grid[0])
            | (joint[..., 1] > y_grid[-1])
        ).any()
    ):
        raise ValueError("joint outcomes fall outside the supplied state grids")
    gas_used = np.rint(joint[..., 0] * gas_limit / 2).astype(np.int64)
    # Protocol arithmetic stays integer; only value interpolation uses floats.
    next_base = np.fromiter(
        (
            _forming_child_base_fee(int(b), int(g), gas_limit)
            for b in base_grid
            for g in gas_used.flat
        ),
        dtype=np.int64,
    ).reshape(len(base_grid), *gas_used.shape)
    rounded_x = 2 * gas_used / gas_limit
    if ((rounded_x < x_grid[0]) | (rounded_x > x_grid[-1])).any():
        raise ValueError("rounded utilization falls outside the supplied state grids")
    next_x = np.broadcast_to(rounded_x, next_base.shape)
    next_priority_fee = np.broadcast_to(np.expm1(joint[..., 1]), next_base.shape)
    for remaining in range(2, horizon + 1):
        previous_base = surface.base_grids[remaining - 1]
        inside = (next_base.min(axis=(1, 2, 3)) >= previous_base[0]) & (
            next_base.max(axis=(1, 2, 3)) <= previous_base[-1]
        )
        if inside.sum() < 2:
            raise ValueError("base grid is too narrow or sparse for this horizon")
        interpolate = RegularGridInterpolator(
            (previous_base, x_grid, priority_grid), surface.values[remaining - 1], bounds_error=True
        )
        next_states = np.stack(
            [next_base[inside], next_x[inside], next_priority_fee[inside]], axis=-1
        )
        continuation = interpolate(next_states).mean(axis=-1)
        surface.base_grids[remaining] = base_grid[inside]
        surface.continuations[remaining] = continuation
        surface.stop_masks[remaining] = immediate[inside] <= continuation
        surface.values[remaining] = np.minimum(immediate[inside], continuation)
    return surface


def decision(surface, known_base_fee, previous_x, previous_log_priority_fee, remaining):
    """Stop using the closed parent's state; no future block outcomes are arguments."""
    remaining = index(remaining)
    if remaining not in surface.values:
        raise ValueError("remaining horizon was not solved")
    state = np.asarray([known_base_fee, previous_x, previous_log_priority_fee], dtype=float)
    if not np.isfinite(state).all() or state[0] <= 0 or not 0 <= state[1] <= 2 or state[2] < 0:
        raise ValueError("invalid observable state")
    immediate = _cost(state[0], state[2], surface.offer_multiplier, surface.fixed_offer)
    if remaining == 1:
        return True
    state[2] = _cost(0, state[2], 1, None)
    continuation = RegularGridInterpolator(
        (surface.base_grids[remaining], surface.x_grid, _cost(0, surface.y_grid, 1, None)),
        surface.continuations[remaining],
        bounds_error=True,
    )(state[None, :])[0]
    return bool(immediate <= continuation)
