"""Native artifact evaluation and scientific reduction."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import numpy as np
import polars as pl
import torch
from servatus import Draft, publish

from . import _runtime
from .addresses import evaluation_directory, evaluation_json_path, evaluation_observations_path
from .config import EvaluateRequest
from .corpus import load_corpus_blocks
from .modeling import load_artifact
from .observations import (
    collect_observations,
    economic_metrics,
    read_observations,
    reduce_observations,
    validate_observations,
)
from .statistics import clustered_mean_intervals
from .temporal import prepare_historical_window

_DEVICE = torch.device("cuda:0")
ROLLING_HORIZONS = (5, 4, 3, 2)


def evaluate(request: EvaluateRequest, storage_root: Path) -> None:
    """Publish canonical observations for one exact artifact/window request."""

    canonical = evaluation_directory(storage_root, request.evaluation_id)
    canonical.parent.mkdir(mode=0o755, exist_ok=True)

    def assemble(draft: Draft) -> None:
        association, model = load_artifact(storage_root, request.artifact_id)
        if association.request.source.corpus_id != request.corpus_id:
            raise ValueError("artifact source Corpus must match the evaluation Corpus")
        blocks = load_corpus_blocks(storage_root, request.corpus_id)
        experiment = association.training_definition.experiment
        dataset = prepare_historical_window(
            blocks,
            experiment,
            request.testing_window,
            feature_state=association.feature_state,
            target_state=association.target_state,
        )

        _runtime.configure_torch()
        observations = collect_observations(
            dataset,
            model,
            blocks,
            request.testing_window,
            target_state=association.target_state,
            horizon_blocks=experiment.horizon_blocks,
            device=_DEVICE,
            batch_size=_runtime.EVALUATION_BATCH_SIZE,
        )
        (draft.path / "evaluation.json").write_text(request.model_dump_json(), encoding="utf-8")
        observations.write_parquet(draft.path / "observations.parquet")

    publish(canonical, assemble)


def load_evaluation(storage_root: Path, evaluation_id: UUID) -> EvaluateRequest:
    request = EvaluateRequest.model_validate_json(
        evaluation_json_path(storage_root, evaluation_id).read_bytes()
    )
    if request.evaluation_id != evaluation_id:
        raise ValueError("embedded evaluation ID does not match the requested evaluation")
    validate_observations(evaluation_observations_path(storage_root, evaluation_id))
    return request


def reduce_evaluation(storage_root: Path, evaluation_id: UUID) -> pl.DataFrame:
    """Derive one testing evaluation's shared metrics from its observations."""

    return reduce_observations(evaluation_observations_path(storage_root, evaluation_id))


def reduce_baselines(storage_root: Path, evaluation_id: UUID) -> pl.DataFrame:
    """Derive immediate and deadline policy metrics from one testing evaluation."""

    columns = read_observations(evaluation_observations_path(storage_root, evaluation_id))
    rows = []
    for policy in ("immediate", "deadline"):
        rows.append({"policy": policy, **economic_metrics(columns, policy)})
    return pl.DataFrame(rows)


def reduce_rolling(storage_root: Path, roster: Mapping[str, Mapping[int, UUID]]) -> pl.DataFrame:
    """Compare one-shot and rolling economics for explicit K-study cells."""

    rows = [
        _reduce_rolling_cell(storage_root, cell, evaluation_ids)
        for cell, evaluation_ids in roster.items()
    ]
    return pl.DataFrame(rows)


def reduce_rolling_intervals(
    storage_root: Path, roster: Mapping[str, Mapping[int, UUID]]
) -> pl.DataFrame:
    """Return paired hourly-bootstrap intervals for rolling mean economics."""

    rows = []
    for cell, evaluation_ids in roster.items():
        replay = _replay_rolling_cell(storage_root, cell, evaluation_ids)
        immediate = replay.initial["immediate_base_fee_per_gas"]
        minimum = replay.initial["minimum_base_fee_per_gas"]
        one_shot_selected = replay.initial["selected_base_fee_per_gas"]
        rolling_selected = replay.final["selected_base_fee_per_gas"]
        one_shot_savings = (immediate - one_shot_selected) / immediate
        rolling_savings = (immediate - rolling_selected) / immediate
        one_shot_gap = (one_shot_selected - minimum) / minimum
        rolling_gap = (rolling_selected - minimum) / minimum
        clusters = _rolling_hour_clusters(
            storage_root, evaluation_ids[ROLLING_HORIZONS[0]], replay.initial["origin_block"]
        )
        intervals = clustered_mean_intervals(
            {
                "one_shot_base_fee_savings": one_shot_savings,
                "rolling_base_fee_savings": rolling_savings,
                "delta_base_fee_savings": rolling_savings - one_shot_savings,
                "one_shot_base_fee_optimality_gap": one_shot_gap,
                "rolling_base_fee_optimality_gap": rolling_gap,
                "delta_base_fee_optimality_gap": rolling_gap - one_shot_gap,
            },
            clusters,
            seed=2026 ^ (evaluation_ids[ROLLING_HORIZONS[0]].int & 0xFFFF_FFFF),
        )
        row: dict[str, str | float] = {"cell": cell}
        for metric, (lower, upper) in intervals.items():
            row[f"{metric}_lower"] = lower
            row[f"{metric}_upper"] = upper
        rows.append(row)
    return pl.DataFrame(rows)


def _reduce_rolling_cell(
    storage_root: Path, cell: str, evaluation_ids: Mapping[int, UUID]
) -> dict[str, str | float]:
    replay = _replay_rolling_cell(storage_root, cell, evaluation_ids)
    one_shot = economic_metrics(replay.initial, "selected")
    rolling = economic_metrics(replay.initial, "selected", selected=replay.final)
    metrics = {}
    for name in one_shot:
        metrics[f"one_shot_{name}"] = one_shot[name]
        metrics[f"rolling_{name}"] = rolling[name]
    return {"cell": cell, **metrics}


def reduce_rolling_traces(
    storage_root: Path, roster: Mapping[str, Mapping[int, UUID]]
) -> pl.DataFrame:
    """Summarize rolling call placement without persisting replay state."""

    rows = []
    for cell, evaluation_ids in roster.items():
        replay = _replay_rolling_cell(storage_root, cell, evaluation_ids)
        for trace, values, support in (
            ("k2_head_advance_blocks", replay.k2_head_advance_blocks, range(4)),
            (
                "maximum_same_head_cascade_length",
                replay.maximum_same_head_cascade_length,
                range(1, 5),
            ),
        ):
            for value in support:
                count = int(np.count_nonzero(values == value))
                rows.append(
                    {
                        "cell": cell,
                        "trace": trace,
                        "value": value,
                        "count": count,
                        "proportion": count / values.size,
                    }
                )
    return pl.DataFrame(rows)


@dataclass(frozen=True)
class _RollingReplay:
    initial: dict[str, np.ndarray]
    final: dict[str, np.ndarray]
    k2_head_advance_blocks: np.ndarray
    maximum_same_head_cascade_length: np.ndarray


def _replay_rolling_cell(
    storage_root: Path, cell: str, evaluation_ids: Mapping[int, UUID]
) -> _RollingReplay:
    decision_origins: np.ndarray | None = None
    call_origins = []
    selections = []
    for horizon in ROLLING_HORIZONS:
        columns = _load_rolling_observations(storage_root, evaluation_ids[horizon])
        if decision_origins is None:
            decision_origins = columns["origin_block"].copy()
        call_origins.append(decision_origins.copy())
        selection = _rolling_arrays(
            columns, decision_origins=decision_origins, cell=cell, horizon=horizon
        )
        selections.append(selection)
        if horizon != ROLLING_HORIZONS[-1]:
            decision_origins += selection["predicted_action_k"] == horizon - 1

    initial = selections[0]
    final = selections[-1]
    stacked_origins = np.stack(call_origins, axis=1)
    current_run = np.ones(stacked_origins.shape[0], dtype=np.int8)
    maximum_run = current_run.copy()
    for index in range(1, stacked_origins.shape[1]):
        current_run = np.where(
            stacked_origins[:, index] == stacked_origins[:, index - 1],
            current_run + 1,
            1,
        )
        maximum_run = np.maximum(maximum_run, current_run)
    return _RollingReplay(
        initial=initial,
        final=final,
        k2_head_advance_blocks=call_origins[-1] - call_origins[0],
        maximum_same_head_cascade_length=maximum_run,
    )


def _load_rolling_observations(storage_root: Path, evaluation_id: UUID) -> dict[str, np.ndarray]:
    columns = read_observations(evaluation_observations_path(storage_root, evaluation_id))
    origins = columns["origin_block"]
    if origins.size == 0 or np.any(np.diff(origins) != 1):
        raise ValueError("rolling observations must contain consecutive unique origins")
    return columns


def _rolling_hour_clusters(
    storage_root: Path, evaluation_id: UUID, origins: np.ndarray
) -> np.ndarray:
    request = load_evaluation(storage_root, evaluation_id)
    blocks = load_corpus_blocks(storage_root, request.corpus_id).to_polars()
    rows = origins - int(blocks[0, "block_number"])
    if np.any((rows < 0) | (rows >= blocks.height)):
        raise ValueError("rolling origins must lie within their Corpus")
    if not np.array_equal(blocks["block_number"].to_numpy()[rows], origins):
        raise ValueError("rolling origins must align with contiguous Corpus blocks")
    return blocks["timestamp"].to_numpy()[rows] // 3_600


def _rolling_arrays(
    columns: Mapping[str, np.ndarray], *, decision_origins: np.ndarray, cell: str, horizon: int
) -> dict[str, np.ndarray]:
    actions = columns["predicted_action_k"]
    if np.any((actions < 0) | (actions >= horizon)):
        raise ValueError(f"{cell} K={horizon} predicted_action_k values must be valid actions")

    origins = columns["origin_block"]
    rows = decision_origins - int(origins[0])
    if np.any((rows < 0) | (rows >= origins.size)):
        raise ValueError(f"{cell} K={horizon} evaluation lacks required decision origins")
    return {name: values[rows] for name, values in columns.items()}
