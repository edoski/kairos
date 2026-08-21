"""KAIROS experiment authoring and scientific close over Servatus Campaigns."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Annotated, TypeAlias, cast
from uuid import UUID

import polars as pl
import typer
from servatus import Campaign, Draft, Task, publish

from kairos.addresses import study_directory
from kairos.config import EvaluateRequest, TrainRequest, TuneRequest
from kairos.experiments import (
    ExperimentKind,
    ExperimentManifest,
    experiment_campaign_directory,
    experiment_directory,
    load_experiment_manifest,
)
from kairos.study import publish_study, reduce_study
from kairos.workers import ExecutionTask, execution_envelope, result_probe

StorageRoot: TypeAlias = Annotated[Path, typer.Argument(resolve_path=True)]
ExperimentRequest: TypeAlias = TuneRequest | TrainRequest | EvaluateRequest
_REQUEST_TYPE = {
    ExperimentKind.FEATURE_ABLATION: TuneRequest,
    ExperimentKind.C_STUDY: TuneRequest,
    ExperimentKind.HPO: TuneRequest,
    ExperimentKind.K_STUDY: TrainRequest,
    ExperimentKind.COMPARATOR_STUDY: TrainRequest,
    ExperimentKind.HELD_OUT: EvaluateRequest,
}


def run(*commands: Callable[..., None]) -> None:
    app = typer.Typer(add_completion=False)
    for command in commands:
        app.command()(command)
    app()


def author_experiment(
    storage_root: Path,
    kind: ExperimentKind,
    experiment_id: UUID,
    cells: Iterable[tuple[str, ExperimentRequest]],
    *,
    seal: bool = True,
) -> Campaign:
    path = experiment_campaign_directory(storage_root, kind, experiment_id)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _, tasks = _author_tasks(kind, cells)
    campaign = Campaign.open(path, tasks)
    if seal:
        campaign.seal()
    return campaign


def append_experiment(
    storage_root: Path,
    kind: ExperimentKind,
    experiment_id: UUID,
    cells: Iterable[tuple[str, ExperimentRequest]],
) -> Campaign:
    path = experiment_campaign_directory(storage_root, kind, experiment_id)
    campaign = Campaign.load(path)
    prefix = campaign.tasks
    suffix_cells, suffix = _author_tasks(kind, cells)
    existing_cells = {execution_envelope(task).cell for task in prefix}
    if existing_cells & suffix_cells:
        raise ValueError("experiment cells must be new and unique")
    return Campaign.open(path, (*prefix, *suffix))


def close_experiment(
    storage_root: Path,
    kind: ExperimentKind,
    experiment_id: UUID,
    *,
    expected_cells: tuple[str, ...] | None = None,
) -> dict[str, UUID]:
    campaign = Campaign.load(experiment_campaign_directory(storage_root, kind, experiment_id))
    tasks = campaign.tasks
    cells, studies = _roster(kind, tasks)
    if expected_cells is not None and tuple(cells) != expected_cells:
        raise ValueError("experiment roster does not match expected cells")

    campaign.seal()
    sealed_tasks = campaign.tasks
    if sealed_tasks != tasks:
        cells, studies = _roster(kind, sealed_tasks)
        if expected_cells is not None and tuple(cells) != expected_cells:
            raise ValueError("experiment roster does not match expected cells")
    if not campaign.inspect(result_probe(storage_root), scheduler=False).results_ready:
        raise RuntimeError("experiment results are incomplete")

    for study_id in studies:
        if not study_directory(storage_root, study_id).exists():
            publish_study(storage_root, study_id)

    publish_experiment_manifest(storage_root, kind, experiment_id, cells)
    return cells


def publish_experiment_manifest(
    storage_root: Path, kind: ExperimentKind, experiment_id: UUID, cells: dict[str, UUID]
) -> None:
    destination = experiment_directory(storage_root, kind, experiment_id)
    destination.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    manifest = ExperimentManifest(root=cells)

    def assemble(draft: Draft) -> None:
        (draft.path / "manifest.json").write_text(manifest.model_dump_json(), encoding="utf-8")

    publish(destination, assemble)


def print_metrics(
    storage_root: Path,
    kind: ExperimentKind,
    experiment_id: UUID,
    reducer: Callable[[Path, UUID], pl.DataFrame],
) -> None:
    results = []
    for cell, record_id in load_experiment_manifest(storage_root, kind, experiment_id).items():
        metrics = reducer(storage_root, record_id)
        results.append(pl.DataFrame({"cell": [cell] * metrics.height}).hstack(metrics))
    print(pl.concat(results).write_csv(None, separator="\t"), end="")


def print_study_metrics(storage_root: Path, kind: ExperimentKind, experiment_id: UUID) -> None:
    print_metrics(storage_root, kind, experiment_id, reduce_study)


def _author_tasks(
    kind: ExperimentKind, cells: Iterable[tuple[str, ExperimentRequest]]
) -> tuple[frozenset[str], tuple[Task, ...]]:
    cells = tuple(cells)
    labels = [cell for cell, _ in cells]
    if len(labels) != len(set(labels)):
        raise ValueError("experiment cells must be new and unique")

    tasks = []
    for cell, request in cells:
        _require_request(kind, request)
        if isinstance(request, TuneRequest):
            tasks.extend(
                ExecutionTask(request=request, method_index=index, cell=cell).task()
                for index in range(len(request.methods))
            )
        else:
            tasks.append(ExecutionTask(request=request, cell=cell).task())
    return frozenset(labels), tuple(tasks)


def _roster(
    kind: ExperimentKind, tasks: Iterable[Task]
) -> tuple[dict[str, UUID], dict[UUID, TuneRequest]]:
    cells: dict[str, UUID] = {}
    studies: dict[UUID, TuneRequest] = {}
    methods: dict[str, list[int]] = {}
    for task in tasks:
        envelope = execution_envelope(task)
        if envelope.cell is None:
            raise ValueError("experiment Task is missing its cell")
        request = envelope.request
        _require_request(kind, request)
        record_id = _record_id(request)
        if cells.setdefault(envelope.cell, record_id) != record_id:
            raise ValueError("experiment cell maps to multiple records")
        if isinstance(request, TuneRequest):
            if studies.setdefault(request.study_id, request) != request:
                raise ValueError("experiment candidates disagree on one Study request")
            methods.setdefault(envelope.cell, []).append(cast(int, envelope.method_index))

    for cell, indexes in methods.items():
        request = studies[cells[cell]]
        if indexes != list(range(len(request.methods))):
            raise ValueError("experiment candidate Tasks must match ordered Study methods")
    return cells, studies


def _record_id(request: ExperimentRequest) -> UUID:
    if isinstance(request, TuneRequest):
        return request.study_id
    if isinstance(request, TrainRequest):
        return request.artifact_id
    return request.evaluation_id


def _require_request(kind: ExperimentKind, request: ExperimentRequest) -> None:
    expected = _REQUEST_TYPE[kind]
    if not isinstance(request, expected):
        raise ValueError(f"{kind} experiments require {expected.__name__}")
