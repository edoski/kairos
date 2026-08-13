from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Literal
from uuid import UUID

import polars as pl
import pytest
from pydantic import ValidationError
from servatus import ConfigurationError, Profile, Task

import kairos.workers as workers
from kairos.addresses import evaluation_json_path, evaluation_observations_path
from kairos.config import (
    EvaluateRequest,
    ExperimentSemantics,
    FitMethod,
    LstmDefinition,
    Method,
    SelectedStudySource,
    TrainRequest,
    TuneRequest,
    WorkflowRequest,
)
from kairos.observations import OBSERVATION_SCHEMA
from kairos.workers import ExecutionTask, execution_task, load_profile, result_probe, run_task
from tests.helpers import SERVATUS_TOML, window

_ROOT = Path(__file__).parents[1]
_CORPUS_ID = UUID("00000000-0000-4000-8000-000000000001")
_ARTIFACT_ID = UUID("00000000-0000-4000-8000-000000000002")
_EVALUATION_ID = UUID("00000000-0000-4000-8000-000000000003")
_STUDY_ID = UUID("00000000-0000-4000-8000-000000000004")


def _experiment() -> ExperimentSemantics:
    return ExperimentSemantics(
        training_window=window(100),
        validation_window=window(210),
        context_blocks=20,
        horizon_blocks=10,
        ordered_features=("log_base_fee_per_gas",),
    )


def _workflow(workflow: Literal["train", "evaluate"]) -> WorkflowRequest:
    if workflow == "evaluate":
        return EvaluateRequest(
            evaluation_id=_EVALUATION_ID,
            artifact_id=_ARTIFACT_ID,
            corpus_id=_CORPUS_ID,
            testing_window=window(300),
        )
    return TrainRequest(
        artifact_id=_ARTIFACT_ID,
        source=SelectedStudySource(
            corpus_id=_CORPUS_ID, study_id=_STUDY_ID, study_result_index=0, experiment=_experiment()
        ),
    )


def _tune_request() -> TuneRequest:
    return TuneRequest(
        study_id=_STUDY_ID,
        corpus_id=_CORPUS_ID,
        experiment=_experiment(),
        methods=(
            Method(
                model=LstmDefinition(
                    family="lstm", hidden=16, layers=1, head_hidden=8, dropout=0.2
                ),
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
            ),
        ),
    )


@pytest.mark.parametrize(
    ("workflow_value", "key"),
    [
        (_workflow("train"), f"artifact:{_ARTIFACT_ID}"),
        (_workflow("evaluate"), f"evaluation:{_EVALUATION_ID}"),
    ],
)
def test_execution_task_preserves_direct_and_experiment_bytes(
    workflow_value: WorkflowRequest, key: str
) -> None:
    direct = execution_task(workflow_value)
    experiment = execution_task(workflow_value, cell="ethereum.lstm")

    assert direct.key == key
    assert direct.args == ("remote", "worker")
    assert direct.stdin == ExecutionTask(request=workflow_value).model_dump_json().encode() + b"\n"
    assert experiment.key == key
    assert experiment.args == ("remote", "worker")
    assert experiment.stdin == (
        ExecutionTask(request=workflow_value, cell="ethereum.lstm").model_dump_json().encode()
        + b"\n"
    )


def test_execution_task_owns_validated_candidate_method() -> None:
    request = _tune_request()
    envelope = ExecutionTask(request=request, method_index=0, cell="ethereum.lstm.full")
    task = execution_task(request, method_index=0, cell="ethereum.lstm.full")

    assert task.key == f"study:{_STUDY_ID}:method:0"
    assert task.args == ("remote", "worker")
    assert task.stdin == envelope.model_dump_json().encode("utf-8") + b"\n"

    with pytest.raises(ValidationError, match="method_index must identify"):
        ExecutionTask(request=request, method_index=1)
    with pytest.raises(ValidationError, match="method_index is only valid"):
        ExecutionTask(request=_workflow("train"), method_index=0)
    with pytest.raises(ValidationError, match="at least 1 character"):
        ExecutionTask(request=_workflow("evaluate"), cell="")


def test_run_task_dispatches_every_execution_kind(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path("/storage")
    requests = (_tune_request(), _workflow("train"), _workflow("evaluate"))
    calls: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        workers,
        "run_candidate",
        lambda storage_root, request, method_index: calls.append(
            ("candidate", storage_root, request, method_index)
        ),
    )
    monkeypatch.setattr(
        workers,
        "train",
        lambda request, storage_root: calls.append(("train", storage_root, request)),
    )
    monkeypatch.setattr(
        workers,
        "evaluate",
        lambda request, storage_root: calls.append(("evaluate", storage_root, request)),
    )

    run_task(root, ExecutionTask(request=requests[0], method_index=0))
    run_task(root, ExecutionTask(request=requests[1]))
    run_task(root, ExecutionTask(request=requests[2]))

    assert calls == [
        ("candidate", root, requests[0], 0),
        ("train", root, requests[1]),
        ("evaluate", root, requests[2]),
    ]


def test_result_probe_validates_exact_task_and_canonical_result(tmp_path: Path) -> None:
    request = _workflow("evaluate")
    task = execution_task(request)
    probe = result_probe(tmp_path)
    assert not probe(task)

    evaluation_json_path(tmp_path, request.evaluation_id).parent.mkdir(parents=True)
    evaluation_json_path(tmp_path, request.evaluation_id).write_text(
        request.model_dump_json(), encoding="utf-8"
    )
    pl.DataFrame(
        [
            {
                "origin_block": 1,
                "predicted_action_k": 0,
                "predicted_minimum_log_base_fee": 1.0,
                "minimum_action_k": 0,
                "immediate_base_fee_per_gas": 2,
                "immediate_effective_priority_fee_per_gas_p50": 1,
                "selected_base_fee_per_gas": 2,
                "selected_effective_priority_fee_per_gas_p50": 1,
                "deadline_base_fee_per_gas": 2,
                "deadline_effective_priority_fee_per_gas_p50": 1,
                "minimum_base_fee_per_gas": 2,
            }
        ],
        schema=OBSERVATION_SCHEMA,
    ).write_parquet(evaluation_observations_path(tmp_path, request.evaluation_id))

    assert probe(task)
    foreign = Task("wrong", task.args, task.stdin)
    with pytest.raises(ValueError, match="does not match its execution envelope"):
        probe(foreign)

    evaluation_json_path(tmp_path, request.evaluation_id).write_text(
        request.model_copy(
            update={"artifact_id": UUID("00000000-0000-4000-8000-000000000004")}
        ).model_dump_json(),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="request does not match"):
        probe(task)


def test_result_probe_uses_domain_loaders_for_study_and_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tune = _tune_request()
    train_request = _workflow("train")
    study = SimpleNamespace(request=tune)
    association = SimpleNamespace(request=train_request)
    candidate_calls: list[tuple[Path, TuneRequest, int]] = []
    monkeypatch.setattr(
        workers, "candidate_result_directory", lambda *_: SimpleNamespace(exists=lambda: True)
    )
    monkeypatch.setattr(
        workers, "load_candidate_result", lambda *args: candidate_calls.append(args)
    )
    monkeypatch.setattr(workers, "load_validated_study", lambda *_: study)
    monkeypatch.setattr(workers, "load_artifact", lambda *_: (association, object()))

    assert result_probe(tmp_path)(execution_task(tune, method_index=0))
    assert candidate_calls == [(tmp_path, tune, 0)]

    (tmp_path / "studies" / str(tune.study_id)).mkdir(parents=True)
    (tmp_path / "artifacts" / str(train_request.artifact_id)).mkdir(parents=True)
    probe = result_probe(tmp_path)
    assert probe(execution_task(tune, method_index=0))
    assert probe(execution_task(train_request))

    study.request = _tune_request().model_copy(
        update={"study_id": UUID("00000000-0000-4000-8000-000000000005")}
    )
    with pytest.raises(ValueError, match="Study request does not match"):
        result_probe(tmp_path)(execution_task(tune, method_index=0))


def test_production_profiles_preserve_kairos_resource_contract() -> None:
    profile = Profile.load(_ROOT / "SERVATUS.toml")
    target = profile.target
    resources = profile.resources

    assert profile.label == "KAIROS"
    assert target.host == "research"
    assert str(target.image) == "/scratch.hpc/edoardo.galli3/deployments/kairos-cuda-352cc96.sif"
    assert str(target.work_root) == "/scratch.hpc/edoardo.galli3/kairos"
    assert str(target.log_root) == "/scratch.hpc/edoardo.galli3/logs/kairos"
    assert target.partitions == ("h100sxm5", "h100pcie", "a100", "l40s", "l40")
    assert target.max_script_bytes == 1_048_576
    assert target.max_tasks_per_allocation == 4
    assert target.max_cpus_per_allocation == 128
    assert target.max_memory_mib_per_allocation == 262_144
    assert target.max_gpus_per_allocation == 4
    assert target.max_time_limit == "3-00:00:00"
    assert target.max_allocations_per_submit == 64
    assert resources.cpus_per_task == 24
    assert resources.memory_mib_per_task == 65_536
    assert resources.gpus_per_task == 1
    assert resources.time_limit == "3-00:00:00"


@pytest.mark.parametrize(
    ("document", "name", "message"),
    [
        (None, None, "cannot read TOML"),
        ("[profiles.TEST.resources]\n", None, "profile.*must contain"),
        (SERVATUS_TOML.replace('default_profile = "TEST"\n\n', ""), None, "selection is required"),
        (SERVATUS_TOML, "MISSING", "is not declared"),
    ],
)
def test_profile_errors_stop_at_the_cwd_configuration_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    document: str | None,
    name: str | None,
    message: str,
) -> None:
    monkeypatch.chdir(tmp_path)
    if document is not None:
        (tmp_path / "SERVATUS.toml").write_text(document, encoding="utf-8")

    with pytest.raises(ConfigurationError, match=message):
        load_profile(name)


def test_image_runs_workers_from_servatus_work_root() -> None:
    definition = (_ROOT / "deploy" / "Apptainer.def").read_text(encoding="utf-8")

    assert '%runscript\n    export STORAGE_ROOT="$PWD"\n    exec kairos "$@"\n' in definition
