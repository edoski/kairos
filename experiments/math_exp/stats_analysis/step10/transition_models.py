"""Kernel diagnostici congiunti per gli step 10 e 11, senza accesso ai dati futuri."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from arch import arch_model
from scipy.special import logsumexp
from scipy.stats import multivariate_normal

from kairos.temporal import _forming_child_base_fee

Y_COLUMN = "log_effective_priority_fee_per_gas_p50"
CANDIDATES = ("baseline", "garch", "regime", "mixture", "empirical")
REGIME_THRESHOLD = 1.5


@dataclass
class Candidate:
    name: str
    coefficients: np.ndarray
    innovations: np.ndarray
    training_last_y: float
    diagnostics: dict = field(default_factory=dict)
    garch_parameters: np.ndarray | None = None
    next_variance: float | None = None
    transitions: np.ndarray | None = None
    regime_coefficients: np.ndarray | None = None
    regime_pools: dict | None = None
    mixture: tuple | None = None
    x_edges: np.ndarray | None = None
    y_edges: np.ndarray | None = None
    conditional_pools: dict | None = None
    outcomes: np.ndarray | None = None


def _ar_coefficients(previous, current):
    return np.array(
        [
            np.linalg.lstsq(
                np.column_stack([np.ones(len(previous)), previous[:, j]]), current[:, j], rcond=None
            )[0]
            for j in range(2)
        ]
    )


def _mean(coefficients, x, y):
    return np.column_stack(
        [
            coefficients[0, 0] + coefficients[0, 1] * np.atleast_1d(x),
            coefficients[1, 0] + coefficients[1, 1] * np.atleast_1d(y),
        ]
    )


def _fit_gaussian_mixture(innovations):
    """Due componenti con covarianza piena; ridge esplicita su dati standardizzati."""
    scale = innovations.std(axis=0)
    if np.any(scale <= 0):
        raise ValueError("La miscela richiede innovazioni non degeneri")
    values = innovations / scale
    tail = np.abs(values[:, 1]) > np.quantile(np.abs(values[:, 1]), 0.9)
    means = np.array([values[~tail].mean(axis=0), values[tail].mean(axis=0)])
    covariances = np.array([np.cov(values[~tail].T), np.cov(values[tail].T)])
    weights = np.array([(~tail).mean(), tail.mean()])
    previous_likelihood = -np.inf
    for iteration in range(200):
        # Ridge 1e-8 evita covarianze singolari, senza modificare X o le fee osservate.
        covariances += np.eye(2)[None] * 1e-8
        log_density = np.column_stack(
            [
                np.log(weights[j]) + multivariate_normal.logpdf(values, means[j], covariances[j])
                for j in range(2)
            ]
        )
        normalizer = logsumexp(log_density, axis=1)
        likelihood = normalizer.sum()
        if np.abs(likelihood - previous_likelihood) < 1e-6 * len(values):
            return (weights, means * scale, covariances * scale[:, None] * scale[None, :]), {
                "mixture_iterations": iteration + 1,
                "mixture_loglik": float(likelihood),
                "mixture_converged": True,
            }
        responsibilities = np.exp(log_density - normalizer[:, None])
        counts = responsibilities.sum(axis=0)
        if np.any(counts < 3):
            raise ValueError("Componente della miscela senza osservazioni sufficienti")
        weights = counts / len(values)
        means = responsibilities.T @ values / counts[:, None]
        covariances = np.array(
            [
                ((values - means[j]) * responsibilities[:, j, None]).T
                @ (values - means[j])
                / counts[j]
                for j in range(2)
            ]
        )
        previous_likelihood = likelihood
    raise RuntimeError("La miscela gaussiana non converge entro 200 iterazioni")


def fit_candidate(training: pd.DataFrame, name: str) -> Candidate:
    """Stima solo sul training contiguo; X e log p50 sono l'intero stato stocastico."""
    if name not in CANDIDATES:
        raise ValueError(f"Candidato sconosciuto: {name}")
    values = training[["X", Y_COLUMN]].to_numpy(dtype=float)
    if len(values) < 100 or not np.isfinite(values).all():
        raise ValueError("Servono almeno 100 osservazioni finite")
    if np.any((values[:, 0] < 0) | (values[:, 0] > 2) | (values[:, 1] < 0)):
        raise ValueError("Utilizzo o log fee fuori supporto")
    if "block_number" in training and not training.block_number.diff().iloc[1:].eq(1).all():
        raise ValueError("Il training deve contenere blocchi consecutivi")
    previous, current = values[:-1], values[1:]
    coefficients = _ar_coefficients(previous, current)
    innovations = current - _mean(coefficients, previous[:, 0], previous[:, 1])
    model = Candidate(name, coefficients, innovations, float(values[-1, 1]))
    model.diagnostics.update(
        training_rows=len(values),
        training_max_y=float(values[:, 1].max()),
        innovation_correlation=float(np.corrcoef(innovations.T)[0, 1]),
    )
    if name == "garch":
        scale = innovations[:, 1].std()
        if scale <= 0:
            raise ValueError("Varianza delle innovazioni nulla")
        fit = arch_model(
            innovations[:, 1] / scale,
            mean="Zero",
            vol="GARCH",
            p=1,
            q=1,
            dist="normal",
            rescale=False,
        ).fit(disp="off")
        if fit.convergence_flag:
            raise RuntimeError("La stima GARCH non converge")
        omega = float(fit.params["omega"] * scale**2)
        alpha, beta = float(fit.params["alpha[1]"]), float(fit.params["beta[1]"])
        sigma = np.asarray(fit.conditional_volatility) * scale
        model.innovations = innovations.copy()
        model.innovations[:, 1] /= sigma
        model.garch_parameters = np.array([omega, alpha, beta])
        model.next_variance = float(omega + alpha * innovations[-1, 1] ** 2 + beta * sigma[-1] ** 2)
        model.diagnostics.update(garch_AIC=float(fit.aic), persistence=alpha + beta)
    elif name == "regime":
        old_regime = (previous[:, 0] >= REGIME_THRESHOLD).astype(int)
        new_regime = (current[:, 0] >= REGIME_THRESHOLD).astype(int)
        # Mezzo conteggio per transizione evita righe nulle: prior dichiarata, non un epsilon.
        counts = np.full((2, 2), 0.5)
        np.add.at(counts, (old_regime, new_regime), 1)
        model.transitions = counts / counts.sum(axis=1, keepdims=True)
        model.regime_coefficients = np.array(
            [
                _ar_coefficients(previous[old_regime == j], current[old_regime == j])
                for j in range(2)
            ]
        )
        model.regime_pools = {}
        for old in range(2):
            state_mean = _mean(model.regime_coefficients[old], previous[:, 0], previous[:, 1])
            for new in range(2):
                mask = (old_regime == old) & (new_regime == new)
                if mask.sum() < 10:
                    raise ValueError("Transizione di regime con meno di dieci osservazioni")
                model.regime_pools[old, new] = current[mask] - state_mean[mask]
        model.diagnostics["regime_counts"] = counts.tolist()
    elif name == "mixture":
        model.mixture, diagnostics = _fit_gaussian_mixture(innovations)
        model.diagnostics.update(diagnostics)
    elif name == "empirical":
        model.x_edges = np.array([0.5, 1, 1.5, 1.8])
        model.y_edges = np.unique(np.quantile(values[:, 1], [0.25, 0.5, 0.75]))
        keys = np.column_stack(
            [np.digitize(previous[:, 0], model.x_edges), np.digitize(previous[:, 1], model.y_edges)]
        )
        model.conditional_pools = {
            tuple(key): current[np.all(keys == key, axis=1)] for key in np.unique(keys, axis=0)
        }
        model.outcomes = current.copy()
        model.diagnostics["conditional_cells"] = len(model.conditional_pools)
    return model


def filtered_variance(model: Candidate, history: pd.DataFrame) -> float | None:
    """h_{parent+1}: history contiene SOLO blocchi osservati successivi al training."""
    if model.name != "garch":
        return None
    variance, previous_y = model.next_variance, model.training_last_y
    omega, alpha, beta = model.garch_parameters
    observed_y = history[Y_COLUMN].to_numpy(dtype=float)
    if not np.isfinite(observed_y).all() or np.any(observed_y < 0):
        raise ValueError("La storia GARCH deve contenere log fee finite e non negative")
    for y in observed_y:
        error = y - (model.coefficients[1, 0] + model.coefficients[1, 1] * previous_y)
        variance = omega + alpha * error**2 + beta * variance
        previous_y = y
    return float(variance)


def sample_joint(
    model: Candidate, x, y, size: int, rng: np.random.Generator, variance=None
) -> tuple[np.ndarray, np.ndarray | None]:
    """Campiona X,Y del prossimo blocco; variance=h_prossimo, ritorna h_successivo."""
    x, y = np.broadcast_arrays(np.broadcast_to(x, (size,)), np.broadcast_to(y, (size,)))
    if size < 1 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Origini e numerosità non valide")
    if np.any((x < 0) | (x > 2) | (y < 0)):
        raise ValueError("Stato del padre fuori supporto")
    mean = _mean(model.coefficients, x, y)
    next_variance = None
    if model.name == "empirical":
        keys = np.column_stack([np.digitize(x, model.x_edges), np.digitize(y, model.y_edges)])
        draws = np.empty((size, 2))
        for key in np.unique(keys, axis=0):
            mask = np.all(keys == key, axis=1)
            pool = model.conditional_pools.get(tuple(key), model.outcomes)
            draws[mask] = pool[rng.integers(len(pool), size=mask.sum())]
        return draws, None
    if model.name == "regime":
        old = (x >= REGIME_THRESHOLD).astype(int)
        new = (rng.random(size) < model.transitions[old, 1]).astype(int)
        draws = np.empty((size, 2))
        for old_state in range(2):
            for new_state in range(2):
                mask = (old == old_state) & (new == new_state)
                if not mask.any():
                    continue
                pool = model.regime_pools[old_state, new_state]
                residual = pool[rng.integers(len(pool), size=mask.sum())]
                draws[mask] = (
                    _mean(model.regime_coefficients[old_state], x[mask], y[mask]) + residual
                )
        # Il limite aperto inferiore al taglio mantiene il regime osservabile coerente col draw.
        draws[:, 0] = np.where(
            new,
            np.clip(draws[:, 0], REGIME_THRESHOLD, 2),
            np.clip(draws[:, 0], 0, np.nextafter(REGIME_THRESHOLD, 0)),
        )
    elif model.name == "mixture":
        weights, means, covariances = model.mixture
        component = rng.choice(2, size=size, p=weights)
        draws = mean.copy()
        for j in range(2):
            mask = component == j
            draws[mask] += rng.multivariate_normal(means[j], covariances[j], size=mask.sum())
    else:
        residual = model.innovations[rng.integers(len(model.innovations), size=size)].copy()
        if model.name == "garch":
            variance = np.broadcast_to(
                model.next_variance if variance is None else variance, (size,)
            )
            if not np.isfinite(variance).all() or np.any(variance <= 0):
                raise ValueError("La varianza condizionata deve essere positiva e finita")
            residual[:, 1] *= np.sqrt(variance)
        draws = mean + residual
    draws[:, 0] = np.clip(draws[:, 0], 0, 2)
    draws[:, 1] = np.maximum(draws[:, 1], 0)
    if not np.isfinite(draws).all():
        raise OverflowError("Kernel non finito: verificare stabilità e periodo di stima")
    if model.name == "garch":
        omega, alpha, beta = model.garch_parameters
        # La censura a zero modifica l'innovazione effettivamente osservata dal processo generato.
        error = draws[:, 1] - mean[:, 1]
        next_variance = omega + alpha * error**2 + beta * variance
        if not np.isfinite(next_variance).all():
            raise OverflowError("La varianza GARCH simulata non è finita")
    return draws, next_variance


def simulate_paths(
    model: Candidate,
    parent: pd.Series,
    horizon: int,
    size: int,
    rng: np.random.Generator,
    variance=None,
) -> dict[str, np.ndarray]:
    """B del primo figlio è nota; gas_limit del padre resta costante lungo i percorsi."""
    if horizon < 1 or size < 1:
        raise ValueError("Orizzonte e numero di percorsi devono essere positivi")
    gas_limit = int(parent.gas_limit)
    base_fee, gas_used = int(parent.base_fee_per_gas), int(parent.gas_used)
    if gas_limit < 2 or base_fee <= 0 or not 0 <= gas_used <= gas_limit:
        raise ValueError("Blocco padre non valido")
    result = {key: np.empty((size, horizon)) for key in ["X", "Y", "B", "P"]}
    x, y = float(parent.X), float(parent[Y_COLUMN])
    bases = np.full(size, base_fee, dtype=np.int64)
    gas = np.full(size, gas_used, dtype=np.int64)
    for step in range(horizon):
        bases = np.fromiter(
            (
                _forming_child_base_fee(int(b), int(g), gas_limit)
                for b, g in zip(bases, gas, strict=True)
            ),
            dtype=np.int64,
            count=size,
        )
        draws, variance = sample_joint(model, x, y, size, rng, variance)
        x, y = draws.T
        if np.any(y > np.log(np.finfo(float).max) - 2):
            raise OverflowError("La fee simulata supera il supporto numerico: nessun cap nascosto")
        # Il gas intero conserva l’aritmetica esatta del protocollo nella ricorrenza successiva.
        gas = np.rint(x * gas_limit / 2).astype(np.int64)
        if model.name == "regime":
            # La griglia del gas, anche con limite dispari, non deve cambiare il regime estratto.
            cutoff_gas = int(np.ceil(REGIME_THRESHOLD * gas_limit / 2))
            gas = np.where(
                x >= REGIME_THRESHOLD, np.maximum(gas, cutoff_gas), np.minimum(gas, cutoff_gas - 1)
            )
        x = 2 * gas / gas_limit
        for key, value in [("X", x), ("Y", y), ("B", bases), ("P", np.expm1(y))]:
            result[key][:, step] = value
    return result
