"""KAIROS command-line application."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from servatus import Campaign, Profile, ResultProbe, Task

from .config import WORKFLOW_REQUEST_ADAPTER, TuneRequest
from .study import publish_study
from .workers import ExecutionTask, load_profile, result_probe, run_task

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
    profile_name: Annotated[str | None, typer.Option("--profile")] = None,
    retry: Annotated[bool, typer.Option("--retry")] = False,
) -> None:
    requests = [WORKFLOW_REQUEST_ADAPTER.validate_json(path.read_bytes()) for path in request_paths]
    profile = load_profile(profile_name)
    storage_root = _resolve_storage_root()
    probe = result_probe(storage_root)
    for index, request_path in enumerate(request_paths):
        _submit_task(
            request_path, ExecutionTask(request=requests[index]).task(), profile, probe, retry=retry
        )


@remote_app.command("worker")
def worker_command() -> None:
    task = ExecutionTask.model_validate_json(sys.stdin.buffer.read())
    run_task(_resolve_storage_root(), task)


@study_app.command("run")
def study_run_command(
    request_path: Annotated[Path, typer.Argument(metavar="TUNE_REQUEST.json")],
    method_index: Annotated[int, typer.Argument(metavar="METHOD_INDEX")],
    profile_name: Annotated[str | None, typer.Option("--profile")] = None,
    retry: Annotated[bool, typer.Option("--retry")] = False,
) -> None:
    request = TuneRequest.model_validate_json(request_path.read_bytes())
    probe = result_probe(_resolve_storage_root())
    _submit_task(
        request_path,
        ExecutionTask(request=request, method_index=method_index).task(),
        load_profile(profile_name),
        probe,
        retry=retry,
    )


def _submit_task(
    request_path: Path, task: Task, profile: Profile, probe: ResultProbe, *, retry: bool
) -> None:
    safe_key = task.key.replace(":", "-")
    campaign_path = request_path.resolve().with_name(f".{request_path.name}.{safe_key}.campaign")
    campaign = Campaign.open(campaign_path, (task,))
    campaign.seal()
    view = campaign.inspect(probe)
    plan = campaign.plan(profile, view=view, retry=(task.key,) if retry else ())
    for receipt in campaign.submit(plan, probe=probe):
        typer.echo(receipt)


@study_app.command("finalize")
def study_finalize_command(study_id: Annotated[UUID, typer.Argument(metavar="STUDY_ID")]) -> None:
    publish_study(_resolve_storage_root(), study_id)
