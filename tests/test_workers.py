from __future__ import annotations

from pathlib import Path
from typing import Literal
from uuid import UUID

import pytest
from pydantic import ValidationError

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
from kairos.workers import CandidateProcessInput, candidate_task, workflow_task
from tests.helpers import window

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
def test_workflow_task_preserves_exact_request_bytes(
    workflow_value: WorkflowRequest, key: str
) -> None:
    task = workflow_task(workflow_value)

    assert task.key == key
    assert task.args == ("remote", "workflow")
    assert task.stdin == workflow_value.model_dump_json().encode("utf-8") + b"\n"


def test_candidate_task_owns_validated_method_and_exact_payload() -> None:
    request = _tune_request()
    candidate = CandidateProcessInput(request=request, method_index=0)

    task = candidate_task(candidate)

    assert task.key == f"study:{_STUDY_ID}:method:0"
    assert task.args == ("remote", "candidate")
    assert task.stdin == candidate.model_dump_json().encode("utf-8") + b"\n"

    with pytest.raises(ValidationError, match="method_index must identify"):
        CandidateProcessInput(request=request, method_index=1)


def test_image_runs_workers_from_servatus_work_root() -> None:
    definition = (_ROOT / "deploy" / "Apptainer.def").read_text(encoding="utf-8")

    assert '%runscript\n    export STORAGE_ROOT="$PWD"\n    exec kairos "$@"\n' in definition
