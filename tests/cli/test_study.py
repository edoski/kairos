from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

import kairos.cli as cli
from kairos.cli import app
from kairos.config import ExperimentSemantics, FitMethod, LstmDefinition, Method, TuneRequest
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
    target_path, resource_path = write_servatus_config(tmp_path)
    open_campaign, campaign = fake_campaign(monkeypatch, cli)

    result = dispatch(
        app,
        "study",
        "run",
        str(request_path),
        "0",
        "--target",
        str(target_path),
        "--resources",
        str(resource_path),
    )

    assert result.exit_code == 0
    assert result.output == "1001;research\n"
    campaign_path, tasks = open_campaign.call_args.args
    assert campaign_path == request_path.with_name(
        f".{request_path.name}.study-{STUDY_ID}-method-0.campaign"
    )
    assert tasks[0].key == f"study:{STUDY_ID}:method:0"
    assert tasks[0].args == ("remote", "candidate")
    assert tasks[0].stdin == (
        json.dumps(
            {"request": REQUEST.model_dump(mode="json"), "method_index": 0}, separators=(",", ":")
        ).encode()
        + b"\n"
    )
    target, resources = campaign.plan.call_args.args
    assert target.host == "research-alias"
    assert resources.gpus_per_task == 1
    assert campaign.plan.call_args.kwargs == {"retry": ()}


def test_remote_candidate_dispatches_input(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = json.dumps(
        {"request": REQUEST.model_dump(mode="json"), "method_index": 0}, separators=(",", ":")
    )
    calls: list[tuple[Path, TuneRequest, int]] = []

    def fake_run_candidate(storage_root: Path, request: TuneRequest, method_index: int) -> None:
        calls.append((storage_root, request, method_index))

    monkeypatch.setenv("STORAGE_ROOT", str(STORAGE_ROOT))
    monkeypatch.setattr(cli, "run_candidate", fake_run_candidate)

    result = dispatch(app, "remote", "candidate", input=payload)

    assert result.exit_code == 0
    assert result.output == ""
    assert calls == [(STORAGE_ROOT, REQUEST, 0)]


def test_remote_candidate_rejects_method_index_outside_request() -> None:
    payload = json.dumps(
        {"request": REQUEST.model_dump(mode="json"), "method_index": 1}, separators=(",", ":")
    )

    result = dispatch(app, "remote", "candidate", input=payload)

    assert result.exit_code == 1
    assert "method_index must identify a request Method" in str(result.exception)
