from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

import pytest

import kairos.cli as cli
from kairos.cli import app
from kairos.config import EvaluateRequest, ExperimentSemantics, SelectedStudySource, TrainRequest
from kairos.workers import ExecutionTask
from tests.helpers import dispatch, fake_campaign, window, write_servatus_config

CORPUS_ID = UUID("10000000-0000-4000-8000-000000000001")
ARTIFACT_ID = UUID("20000000-0000-4000-8000-000000000001")
EVALUATION_ID = UUID("30000000-0000-4000-8000-000000000001")
STUDY_ID = UUID("40000000-0000-4000-8000-000000000001")
STORAGE_ROOT = Path("/remote/storage root")


def _experiment() -> ExperimentSemantics:
    return ExperimentSemantics(
        training_window=window(100),
        validation_window=window(210),
        context_blocks=20,
        horizon_blocks=10,
        ordered_features=("log_base_fee_per_gas",),
    )


def _train_request() -> TrainRequest:
    source = SelectedStudySource(
        corpus_id=CORPUS_ID, study_id=STUDY_ID, study_result_index=2, experiment=_experiment()
    )
    return TrainRequest(artifact_id=ARTIFACT_ID, source=source)


def _evaluate_request() -> EvaluateRequest:
    return EvaluateRequest(
        evaluation_id=EVALUATION_ID,
        artifact_id=ARTIFACT_ID,
        corpus_id=CORPUS_ID,
        testing_window=window(300),
    )


def test_submit_uses_one_durable_campaign_per_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = _evaluate_request()
    request_paths = (tmp_path / "request-0.json", tmp_path / "request-1.json")
    for request_path in request_paths:
        request_path.write_text(request.model_dump_json(), encoding="utf-8")
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    load = Mock(wraps=cli.load_profile)
    monkeypatch.setattr(cli, "load_profile", load)
    open_campaign, campaign = fake_campaign(monkeypatch, cli)
    arguments = (
        "submit",
        *(str(request_path) for request_path in request_paths),
        "--profile",
        "OTHER",
        "--retry",
    )

    result = dispatch(app, *arguments)

    assert result.exit_code == 0
    assert result.output == "1001;research\n" * 2
    load.assert_called_once_with("OTHER")
    assert open_campaign.call_count == 2
    campaign_path, tasks = open_campaign.call_args.args
    assert campaign_path == tmp_path / f".request-1.json.evaluation-{EVALUATION_ID}.campaign"
    assert tasks[0].key == f"evaluation:{EVALUATION_ID}"
    profile = campaign.plan.call_args.args[0]
    assert profile.label == "OTHER"
    assert campaign.plan.call_args.kwargs == {
        "view": campaign.inspect.return_value,
        "retry": (f"evaluation:{EVALUATION_ID}",),
    }
    assert campaign.submit.call_args.kwargs["probe"] is campaign.inspect.call_args.args[0]


def test_remote_worker_dispatches_train_and_evaluate_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    train_request = _train_request()
    evaluate_request = _evaluate_request()
    train_calls: list[tuple[TrainRequest, Path]] = []
    evaluate_calls: list[tuple[EvaluateRequest, Path]] = []
    monkeypatch.setenv("STORAGE_ROOT", str(STORAGE_ROOT))

    def run(storage_root: Path, task: ExecutionTask) -> None:
        if isinstance(task.request, TrainRequest):
            train_calls.append((task.request, storage_root))
        else:
            evaluate_calls.append((task.request, storage_root))

    monkeypatch.setattr(cli, "run_task", run)

    train_result = dispatch(
        app, "remote", "worker", input=ExecutionTask(request=train_request).model_dump_json()
    )
    evaluate_result = dispatch(
        app, "remote", "worker", input=ExecutionTask(request=evaluate_request).model_dump_json()
    )

    assert train_result.exit_code == 0
    assert train_result.output == ""
    assert evaluate_result.exit_code == 0
    assert evaluate_result.output == ""
    assert train_calls == [(train_request, STORAGE_ROOT)]
    assert evaluate_calls == [(evaluate_request, STORAGE_ROOT)]
