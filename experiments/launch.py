"""Launch one experiment bundle through a durable Servatus Campaign."""

from __future__ import annotations

from collections.abc import Collection, Sequence
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from bundle import read_cells
from servatus import Campaign, Profile, Task

from kairos.config import WORKFLOW_REQUEST_ADAPTER, TuneRequest
from kairos.workers import ExecutionTask, load_profile, result_probe

_RetryKeys = Annotated[list[str] | None, typer.Option("--retry", metavar="TASK_KEY")]


def candidates(
    bundle: Path,
    tasks_per_job: int | None = None,
    profile: Annotated[str | None, typer.Option("--profile")] = None,
    retry: _RetryKeys = None,
) -> None:
    bundle = bundle.resolve()
    rows = read_cells(bundle)
    requests: dict[UUID, TuneRequest] = {}
    tasks: list[Task] = []
    for row in rows:
        request = TuneRequest.model_validate_json(Path(row["request"]).read_bytes())
        existing = requests.setdefault(request.study_id, request)
        if existing != request:
            raise ValueError("experiment candidates disagree on one Study request")
        tasks.append(
            ExecutionTask(
                request=request, method_index=int(row["method_index"]), cell=row["cell"]
            ).task()
        )
    storage_root = bundle.parents[2]
    _launch(bundle, tasks, tasks_per_job, load_profile(profile), storage_root, retry=retry or ())


def workflows(
    bundle: Path,
    tasks_per_job: int | None = None,
    profile: Annotated[str | None, typer.Option("--profile")] = None,
    retry: _RetryKeys = None,
) -> None:
    bundle = bundle.resolve()
    rows = read_cells(bundle)
    storage_root = bundle.parents[2]
    _launch(
        bundle,
        tuple(
            ExecutionTask(
                request=WORKFLOW_REQUEST_ADAPTER.validate_json(Path(row["request"]).read_bytes()),
                cell=row["cell"],
            ).task()
            for row in rows
        ),
        tasks_per_job,
        load_profile(profile),
        storage_root,
        retry=retry or (),
    )


def _launch(
    bundle: Path,
    tasks: Sequence[Task],
    tasks_per_job: int | None,
    profile: Profile,
    storage_root: Path,
    *,
    retry: Collection[str],
) -> None:
    campaign_root = storage_root / "experiments" / ".servatus"
    campaign_root.mkdir(mode=0o700, exist_ok=True)
    campaign_parent = campaign_root / bundle.parent.name
    campaign_parent.mkdir(mode=0o700, exist_ok=True)
    campaign_path = campaign_parent / bundle.name.removeprefix(".")
    campaign = Campaign.open(campaign_path, tuple(tasks))
    probe = result_probe(storage_root)
    view = campaign.inspect(probe)
    plan = campaign.plan(profile, view=view, retry=retry, tasks_per_allocation=tasks_per_job)
    for receipt in campaign.submit(plan, probe=probe):
        print(receipt)


app = typer.Typer(add_completion=False)
app.command()(candidates)
app.command()(workflows)


if __name__ == "__main__":
    app()
