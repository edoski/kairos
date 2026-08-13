"""Immutable Study publication and selected-Method loading."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Self, TypeAlias, cast
from uuid import UUID

import polars as pl
import torch
from pydantic import UUID4, Field, model_validator
from servatus import Draft, Workspace

from .addresses import (
    study_directory,
    study_json_path,
    study_trial_checkpoint_path,
    study_trial_observations_path,
)
from .config import Method, SelectedStudySource, TrainingDefinition, TuneRequest
from .observations import reduce_observations, validate_observations
from .records import StrictFrozenRecord

_Epoch: TypeAlias = Annotated[int, Field(ge=1)]


class RetainedResult(StrictFrozenRecord):
    objective: Annotated[float, Field(allow_inf_nan=False)]
    selected_epoch: _Epoch
    completed_epochs: _Epoch

    @model_validator(mode="after")
    def validate_epochs(self) -> Self:
        if self.selected_epoch > self.completed_epochs:
            raise ValueError("selected_epoch must not exceed completed_epochs")
        return self


class Study(StrictFrozenRecord):
    request: TuneRequest
    trials: tuple[RetainedResult, ...]

    @model_validator(mode="after")
    def validate_trials(self) -> Self:
        if len(self.trials) != len(self.request.methods):
            raise ValueError("trials must align with request methods")
        for method, result in zip(self.request.methods, self.trials):  # noqa: B905
            if result.completed_epochs > method.fit.max_epochs:
                raise ValueError("completed_epochs must not exceed method.fit.max_epochs")
        return self

    def best_result(self) -> tuple[int, RetainedResult]:
        return min(enumerate(self.trials), key=lambda indexed: indexed[1].objective)


class _CandidateResult(StrictFrozenRecord):
    request: TuneRequest
    result: RetainedResult


def assemble_candidate_result(
    draft: Draft,
    request: TuneRequest,
    result: RetainedResult,
    selected_checkpoint: Path,
    observations: pl.DataFrame,
) -> None:
    """Write one completed candidate's exact retained-result tree."""

    draft.link(selected_checkpoint, "selected.ckpt")
    observations.write_parquet(draft.path / "validation.parquet")
    (draft.path / "result.json").write_text(
        _CandidateResult(request=request, result=result).model_dump_json(), encoding="utf-8"
    )


def publish_study(storage_root: Path, study_id: UUID4) -> None:
    canonical = study_directory(storage_root, study_id)
    canonical.parent.mkdir(mode=0o755, exist_ok=True)
    parent = Workspace(canonical, identity=study_id.bytes)
    with parent as workspace:
        first = _load_candidate_result_path(parent.path / "trial-0")
        request = first.request
        if request.study_id != study_id:
            raise ValueError("result Study ID does not match requested Study ID")

        def assemble(draft: Draft) -> None:
            expected_trials = tuple(
                parent.path / f"trial-{index}" for index in range(len(request.methods))
            )
            if set(parent.path.glob("trial-*")) != set(expected_trials):
                raise ValueError("retained trials do not match TuneRequest methods")

            trials = []
            for index, retained in enumerate(expected_trials):
                candidate = first if index == 0 else _load_candidate_result_path(retained)
                if candidate.request != request:
                    raise ValueError("result requests must be identical")
                _validate_trial(retained, request, index, candidate.result)
                draft.link(retained / "selected.ckpt", f"trials/{index}/selected.ckpt")
                draft.link(retained / "validation.parquet", f"trials/{index}/validation.parquet")
                trials.append(candidate.result)

            (draft.path / "study.json").write_text(
                Study(request=request, trials=tuple(trials)).model_dump_json(), encoding="utf-8"
            )

        workspace.publish(assemble)


def load_study(storage_root: Path, study_id: UUID) -> Study:
    return _read_study(storage_root, study_id, with_reductions=False)[0]


def _read_study(
    storage_root: Path, study_id: UUID, *, with_reductions: bool
) -> tuple[Study, pl.DataFrame | None]:
    study = Study.model_validate_json(study_json_path(storage_root, study_id).read_bytes())
    if study.request.study_id != study_id:
        raise ValueError("Study ID does not match requested Study ID")
    reductions = []
    for index, result in enumerate(study.trials):
        if not study_trial_checkpoint_path(storage_root, study_id, index).is_file():
            raise FileNotFoundError("Study trial selected checkpoint is missing")
        observations = study_trial_observations_path(storage_root, study_id, index)
        if not with_reductions:
            validate_observations(observations)
            continue
        metrics = reduce_observations(observations)
        if result.objective != metrics["base_fee_optimality_gap"][0]:
            raise ValueError("Study objective must equal validation observations")
        reductions.append(pl.DataFrame({"method_index": [index]}).hstack(metrics))
    return study, pl.concat(reductions) if with_reductions else None


def candidate_result_directory(storage_root: Path, study_id: UUID, method_index: int) -> Path:
    parent = Workspace(study_directory(storage_root, study_id), identity=study_id.bytes)
    return parent.path / f"trial-{method_index}"


def load_candidate_result(path: Path, request: TuneRequest, method_index: int) -> RetainedResult:
    candidate = _load_candidate_result_path(path)
    if candidate.request != request:
        raise ValueError("candidate request does not match execution task")
    _validate_trial(path, request, method_index, candidate.result)
    return candidate.result


def reduce_study(storage_root: Path, study_id: UUID) -> pl.DataFrame:
    return cast(pl.DataFrame, _read_study(storage_root, study_id, with_reductions=True)[1])


def load_validated_study(storage_root: Path, study_id: UUID) -> Study:
    return _read_study(storage_root, study_id, with_reductions=True)[0]


def load_selected_method(storage_root: Path, source: SelectedStudySource) -> Method:
    study = load_study(storage_root, source.study_id)
    if study.request.corpus_id != source.corpus_id:
        raise ValueError("selected source Corpus ID does not match canonical Study")
    return study.request.method_at(source.study_result_index)


def _validate_trial(
    retained: Path, request: TuneRequest, method_index: int, result: RetainedResult
) -> None:
    expected = TrainingDefinition(
        experiment=request.experiment, method=request.method_at(method_index)
    ).model_dump(mode="json")
    checkpoint = torch.load(retained / "selected.ckpt", map_location="cpu", weights_only=True)
    if checkpoint["hyper_parameters"]["association"] != expected:
        raise ValueError("selected checkpoint association must match the request Method")
    metrics = reduce_observations(retained / "validation.parquet")
    if result.objective != metrics["base_fee_optimality_gap"][0]:
        raise ValueError("result objective must equal validation observations")


def _load_candidate_result_path(path: Path) -> _CandidateResult:
    return _CandidateResult.model_validate_json((path / "result.json").read_bytes())
