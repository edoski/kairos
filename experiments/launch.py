"""Launch one experiment bundle through a durable Servatus Campaign."""

from __future__ import annotations

from collections.abc import Collection, Sequence
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from bundle import read_cells
from servatus import Campaign, ResourceRequest, SlurmTarget, Task

from kairos.addresses import (
    artifact_directory,
    evaluation_directory,
    evaluation_json_path,
    evaluation_observations_path,
    study_directory,
)
from kairos.config import WORKFLOW_REQUEST_ADAPTER, EvaluateRequest, TrainRequest, TuneRequest
from kairos.modeling import load_artifact
from kairos.observations import validate_observations
from kairos.study import load_study
from kairos.workers import CandidateProcessInput, candidate_task, workflow_task

_MAX_TASKS_PER_JOB = 4
_CAMPAIGN_DIRECTORY = ".servatus-campaign"
_TargetPath = Annotated[Path, typer.Option("--target", dir_okay=False, readable=True)]
_ResourcePath = Annotated[Path, typer.Option("--resources", dir_okay=False, readable=True)]
_RetryKeys = Annotated[list[str] | None, typer.Option("--retry", metavar="TASK_KEY")]


def candidates(
    bundle: Path,
    tasks_per_job: int = _MAX_TASKS_PER_JOB,
    target: _TargetPath = Path("REMOTE.toml"),
    resources: _ResourcePath = Path("RESOURCES.toml"),
    retry: _RetryKeys = None,
) -> None:
    bundle = bundle.resolve()
    rows = read_cells(bundle)
    inputs = tuple(
        CandidateProcessInput(
            request=TuneRequest.model_validate_json(Path(row["request"]).read_bytes()),
            method_index=int(row["method_index"]),
        )
        for row in rows
    )
    storage_root = bundle.parents[2]
    _launch(
        bundle,
        tuple(candidate_task(candidate) for candidate in inputs),
        tasks_per_job,
        target,
        resources,
        completed=_completed_candidates(storage_root, inputs),
        retry=retry or (),
    )


def workflows(
    bundle: Path,
    tasks_per_job: int = _MAX_TASKS_PER_JOB,
    target: _TargetPath = Path("REMOTE.toml"),
    resources: _ResourcePath = Path("RESOURCES.toml"),
    retry: _RetryKeys = None,
) -> None:
    bundle = bundle.resolve()
    rows = read_cells(bundle)
    requests = tuple(
        WORKFLOW_REQUEST_ADAPTER.validate_json(Path(row["request"]).read_bytes()) for row in rows
    )
    storage_root = bundle.parents[2]
    _launch(
        bundle,
        tuple(workflow_task(request) for request in requests),
        tasks_per_job,
        target,
        resources,
        completed=_completed_workflows(storage_root, requests),
        retry=retry or (),
    )


def _launch(
    bundle: Path,
    tasks: Sequence[Task],
    tasks_per_job: int,
    target_path: Path,
    resource_path: Path,
    *,
    completed: Collection[str],
    retry: Collection[str],
) -> None:
    if not 2 <= tasks_per_job <= _MAX_TASKS_PER_JOB:
        raise ValueError("tasks per job must be between two and four")

    target = SlurmTarget.from_toml(target_path)
    resources = ResourceRequest.from_toml(resource_path)
    if resources.gpus_per_task != 1:
        raise ValueError("KAIROS experiment tasks require exactly one GPU")

    campaign = Campaign.open(bundle / _CAMPAIGN_DIRECTORY, tasks)
    plan = campaign.plan(
        target, resources, completed=completed, retry=retry, tasks_per_allocation=tasks_per_job
    )
    for receipt in campaign.submit(plan):
        print(receipt)


def _completed_candidates(
    storage_root: Path, candidates: Sequence[CandidateProcessInput]
) -> set[str]:
    expected_requests: dict[UUID, TuneRequest] = {}
    for candidate in candidates:
        existing = expected_requests.setdefault(candidate.request.study_id, candidate.request)
        if existing != candidate.request:
            raise ValueError("experiment candidates disagree on one Study request")

    completed: set[str] = set()
    for study_id, request in expected_requests.items():
        if not study_directory(storage_root, study_id).exists():
            continue
        canonical = load_study(storage_root, study_id)
        if canonical.request != request:
            raise ValueError("canonical Study request does not match experiment task")
        completed.update(
            candidate_task(candidate).key
            for candidate in candidates
            if candidate.request.study_id == study_id
        )
    return completed


def _completed_workflows(
    storage_root: Path, requests: Sequence[TrainRequest | EvaluateRequest]
) -> set[str]:
    completed: set[str] = set()
    for request in requests:
        if isinstance(request, TrainRequest):
            if not artifact_directory(storage_root, request.artifact_id).exists():
                continue
            association, _ = load_artifact(storage_root, request.artifact_id)
            if association.request != request:
                raise ValueError("canonical artifact request does not match experiment task")
        else:
            if not evaluation_directory(storage_root, request.evaluation_id).exists():
                continue
            canonical = EvaluateRequest.model_validate_json(
                evaluation_json_path(storage_root, request.evaluation_id).read_bytes()
            )
            if canonical != request:
                raise ValueError("canonical evaluation request does not match experiment task")
            validate_observations(evaluation_observations_path(storage_root, request.evaluation_id))
        completed.add(workflow_task(request).key)
    return completed


app = typer.Typer(add_completion=False)
app.command()(candidates)
app.command()(workflows)


if __name__ == "__main__":
    app()
