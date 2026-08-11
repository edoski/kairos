"""KAIROS worker inputs and their opaque Servatus task boundary."""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import Field, model_validator
from servatus import Task

from .config import EvaluateRequest, TrainRequest, TuneRequest, WorkflowRequest
from .records import StrictFrozenRecord

_NonNegativeInt = Annotated[int, Field(ge=0)]


class CandidateProcessInput(StrictFrozenRecord):
    request: TuneRequest
    method_index: _NonNegativeInt

    @model_validator(mode="after")
    def validate_method_index(self) -> Self:
        self.request.method_at(self.method_index)
        return self


def workflow_task(request: WorkflowRequest) -> Task:
    """Map one typed workflow request to its stable worker task."""

    if isinstance(request, TrainRequest):
        key = f"artifact:{request.artifact_id}"
    elif isinstance(request, EvaluateRequest):
        key = f"evaluation:{request.evaluation_id}"
    else:  # pragma: no cover - the closed typed union is exhaustive
        raise TypeError(f"unsupported workflow request: {type(request).__name__}")
    return Task(key, ("remote", "workflow"), _payload(request))


def candidate_task(candidate: CandidateProcessInput) -> Task:
    """Map one typed Study candidate to its stable worker task."""

    return Task(
        f"study:{candidate.request.study_id}:method:{candidate.method_index}",
        ("remote", "candidate"),
        _payload(candidate),
    )


def _payload(value: StrictFrozenRecord) -> bytes:
    return value.model_dump_json().encode("utf-8") + b"\n"
