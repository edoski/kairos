"""Launch one authored experiment through its Servatus Campaign."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from servatus import Campaign

from kairos.experiments import ExperimentKind, experiment_campaign_directory
from kairos.workers import load_profile, result_probe

_ProfileName = Annotated[str | None, typer.Option("--profile")]
_RetryKeys = Annotated[list[str] | None, typer.Option("--retry", metavar="TASK_KEY")]
_DuplicateRiskKeys = Annotated[
    list[str] | None, typer.Option("--allow-duplicate-risk", metavar="TASK_KEY")
]


def launch(
    storage_root: Path,
    kind: ExperimentKind,
    experiment_id: UUID,
    tasks_per_job: int | None = None,
    profile_name: _ProfileName = None,
    retry: _RetryKeys = None,
    allow_duplicate_risk: _DuplicateRiskKeys = None,
) -> None:
    profile = load_profile(profile_name)
    campaign = Campaign.load(experiment_campaign_directory(storage_root, kind, experiment_id))
    probe = result_probe(storage_root)
    view = campaign.inspect(probe)
    plan = campaign.plan(
        profile,
        view=view,
        retry=retry or (),
        allow_duplicate_risk=allow_duplicate_risk or (),
        tasks_per_allocation=tasks_per_job,
    )
    for receipt in campaign.submit(plan, probe=probe):
        print(receipt)


app = typer.Typer(add_completion=False)
app.command()(launch)


if __name__ == "__main__":
    app()
