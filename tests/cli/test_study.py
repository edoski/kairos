from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

import kairos.cli as cli
from kairos.cli import app
from kairos.config import ExperimentSemantics, FitMethod, LstmDefinition, Method, TuneRequest
from kairos.workers import ExecutionTask
from tests.helpers import dispatch, fake_campaign, window, write_servatus_config

STUDY_ID = UUID("10000000-0000-4000-8000-000000000001")
CORPUS_ID = UUID("20000000-0000-4000-8000-000000000001")
STORAGE_ROOT = Path("/remote/storage root")


METHOD = Method(
    model=LstmDefinition(family="lstm", hidden=16, layers=1, head_hidden=8, dropout=0.2),
    fit=FitMethod(
        learning_rate=3e-4,
        weight_decay=1e-4,
        accumulation=1,
        gradient_clip_norm=0.75,
        seed=17,
        max_epochs=12,
        validate_every_completed_epoch=1,
        patience=4,
        min_delta=0.01,
    ),
)
REQUEST = TuneRequest(
    study_id=STUDY_ID,
    corpus_id=CORPUS_ID,
    experiment=ExperimentSemantics(
        training_window=window(100),
        validation_window=window(210),
        context_blocks=20,
        horizon_blocks=10,
        ordered_features=("log_base_fee_per_gas",),
    ),
    methods=(METHOD,),
)


def test_study_run_submits_typed_candidate_and_prints_job_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request_path = tmp_path / "TUNE_REQUEST.json"
    request_path.write_text(REQUEST.model_dump_json(), encoding="utf-8")
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    open_campaign, campaign = fake_campaign(monkeypatch, cli)

    result = dispatch(app, "study", "run", str(request_path), "0")

    assert result.exit_code == 0
    assert result.output == "1001;research\n"
    campaign_path, tasks = open_campaign.call_args.args
    assert campaign_path == request_path.with_name(
        f".{request_path.name}.study-{STUDY_ID}-method-0.campaign"
    )
    assert tasks[0].key == f"study:{STUDY_ID}:method:0"
    assert tasks[0].args == ("remote", "worker")
    assert (
        tasks[0].stdin
        == ExecutionTask(request=REQUEST, method_index=0).model_dump_json().encode() + b"\n"
    )
    profile = campaign.plan.call_args.args[0]
    assert profile.label == "TEST"
    assert campaign.plan.call_args.kwargs == {"view": campaign.inspect.return_value, "retry": ()}


def test_remote_worker_dispatches_candidate_input(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = ExecutionTask(request=REQUEST, method_index=0).model_dump_json()
    calls: list[tuple[Path, TuneRequest, int]] = []

    def fake_run_task(storage_root: Path, task: ExecutionTask) -> None:
        calls.append((storage_root, task.request, task.method_index or 0))

    monkeypatch.setenv("STORAGE_ROOT", str(STORAGE_ROOT))
    monkeypatch.setattr(cli, "run_task", fake_run_task)

    result = dispatch(app, "remote", "worker", input=payload)

    assert result.exit_code == 0
    assert result.output == ""
    assert calls == [(STORAGE_ROOT, REQUEST, 0)]


def test_remote_worker_rejects_method_index_outside_request() -> None:
    payload = (
        ExecutionTask(request=REQUEST, method_index=0)
        .model_dump_json()
        .replace('"method_index":0', '"method_index":1')
    )

    result = dispatch(app, "remote", "worker", input=payload)

    assert result.exit_code == 1
    assert "method_index must identify a request Method" in str(result.exception)
