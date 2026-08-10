"""KAIROS command-line application."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from servatus import Campaign, ResourceRequest, SlurmTarget

from .config import WORKFLOW_REQUEST_ADAPTER, TrainRequest, TuneRequest
from .evaluation import evaluate
from .modeling import run_candidate, train
from .study import publish_study
from .workers import CandidateProcessInput, candidate_task, workflow_task

app = typer.Typer(add_completion=False)
remote_app = typer.Typer()
study_app = typer.Typer()
app.add_typer(remote_app, name="remote", hidden=True)
app.add_typer(study_app, name="study")


def _resolve_storage_root() -> Path:
    storage_root = Path(os.environ["STORAGE_ROOT"])
    if not storage_root.is_absolute():
        raise ValueError("STORAGE_ROOT must be an absolute path")
    return storage_root


@app.command("submit")
def submit_command(
    request_paths: Annotated[list[Path], typer.Argument(metavar="REQUEST.json")],
    target_path: Annotated[Path, typer.Option("--target", dir_okay=False, readable=True)] = Path(
        "REMOTE.toml"
    ),
    resource_path: Annotated[
        Path, typer.Option("--resources", dir_okay=False, readable=True)
    ] = Path("RESOURCES.toml"),
    retry: Annotated[bool, typer.Option("--retry")] = False,
) -> None:
    target = SlurmTarget.from_toml(target_path)
    resources = ResourceRequest.from_toml(resource_path)
    if resources.gpus_per_task != 1:
        raise ValueError("KAIROS workflow tasks require exactly one GPU")
    requests = [WORKFLOW_REQUEST_ADAPTER.validate_json(path.read_bytes()) for path in request_paths]
    for request_path, request in zip(request_paths, requests, strict=True):
        task = workflow_task(request)
        campaign = Campaign.open(_request_campaign_path(request_path, task.key), (task,))
        plan = campaign.plan(
            target, resources, retry=(task.key,) if retry else (), tasks_per_allocation=1
        )
        for receipt in campaign.submit(plan):
            typer.echo(receipt)


@remote_app.command("workflow")
def workflow_command() -> None:
    request = WORKFLOW_REQUEST_ADAPTER.validate_json(sys.stdin.buffer.read())
    storage_root = _resolve_storage_root()

    if isinstance(request, TrainRequest):
        train(request, storage_root)
    else:
        evaluate(request, storage_root)


@remote_app.command("candidate", hidden=True)
def candidate_command() -> None:
    candidate = CandidateProcessInput.model_validate_json(sys.stdin.buffer.read())
    storage_root = _resolve_storage_root()
    run_candidate(storage_root, candidate.request, candidate.method_index)


@study_app.command("run")
def study_run_command(
    request_path: Annotated[Path, typer.Argument(metavar="TUNE_REQUEST.json")],
    method_index: Annotated[int, typer.Argument(metavar="METHOD_INDEX")],
    target_path: Annotated[Path, typer.Option("--target", dir_okay=False, readable=True)] = Path(
        "REMOTE.toml"
    ),
    resource_path: Annotated[
        Path, typer.Option("--resources", dir_okay=False, readable=True)
    ] = Path("RESOURCES.toml"),
    retry: Annotated[bool, typer.Option("--retry")] = False,
) -> None:
    request = TuneRequest.model_validate_json(request_path.read_bytes())
    task = candidate_task(CandidateProcessInput(request=request, method_index=method_index))
    target = SlurmTarget.from_toml(target_path)
    resources = ResourceRequest.from_toml(resource_path)
    if resources.gpus_per_task != 1:
        raise ValueError("KAIROS candidate tasks require exactly one GPU")
    campaign = Campaign.open(_request_campaign_path(request_path, task.key), (task,))
    plan = campaign.plan(
        target, resources, retry=(task.key,) if retry else (), tasks_per_allocation=1
    )
    for receipt in campaign.submit(plan):
        typer.echo(receipt)


@study_app.command("finalize")
def study_finalize_command(study_id: Annotated[UUID, typer.Argument(metavar="STUDY_ID")]) -> None:
    publish_study(_resolve_storage_root(), study_id)


def _request_campaign_path(request_path: Path, task_key: str) -> Path:
    safe_key = task_key.replace(":", "-")
    return request_path.resolve().with_name(f".{request_path.name}.{safe_key}.campaign")
