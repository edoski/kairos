"""KAIROS worker inputs and their opaque Servatus task boundary."""

from __future__ import annotations

from typing import Self

from pydantic import model_validator
from servatus import Task

from .config import TrainRequest, TuneRequest, WorkflowRequest
from .records import StrictFrozenRecord


class CandidateProcessInput(StrictFrozenRecord):
    request: TuneRequest
    method_index: int

    @model_validator(mode="after")
    def validate_method_index(self) -> Self:
        self.request.method_at(self.method_index)
        return self


def workflow_task(request: WorkflowRequest) -> Task:
    """Map one typed workflow request to its stable worker task."""

    if isinstance(request, TrainRequest):
        key = f"artifact:{request.artifact_id}"
    else:
        key = f"evaluation:{request.evaluation_id}"
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
