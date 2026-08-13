"""KAIROS execution tasks and their opaque Servatus boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Self, TypeAlias, cast
from uuid import UUID

from pydantic import Field, model_validator
from servatus import Profile, ResultProbe, Task

from .addresses import artifact_directory, evaluation_directory, study_directory
from .config import EvaluateRequest, TrainRequest, TuneRequest
from .evaluation import evaluate, load_evaluation
from .modeling import load_artifact, run_candidate, train
from .records import StrictFrozenRecord
from .study import candidate_result_directory, load_candidate_result, load_validated_study

ExecutionRequest: TypeAlias = Annotated[
    TuneRequest | TrainRequest | EvaluateRequest, Field(discriminator="workflow")
]


class ExecutionTask(StrictFrozenRecord):
    request: ExecutionRequest
    method_index: int | None = None
    cell: Annotated[str, Field(min_length=1)] | None = None

    @model_validator(mode="after")
    def validate_execution(self) -> Self:
        if isinstance(self.request, TuneRequest):
            if self.method_index is None:
                raise ValueError("method_index is required for a TuneRequest")
            self.request.method_at(self.method_index)
        elif self.method_index is not None:
            raise ValueError("method_index is only valid for a TuneRequest")
        return self


def execution_task(
    request: ExecutionRequest, *, method_index: int | None = None, cell: str | None = None
) -> Task:
    """Map one typed KAIROS execution to one stable Servatus Task."""

    envelope = ExecutionTask(request=request, method_index=method_index, cell=cell)
    if isinstance(request, TuneRequest):
        key = f"study:{request.study_id}:method:{cast(int, envelope.method_index)}"
    elif isinstance(request, TrainRequest):
        key = f"artifact:{request.artifact_id}"
    else:
        key = f"evaluation:{request.evaluation_id}"
    return Task(key, ("remote", "worker"), envelope.model_dump_json().encode("utf-8") + b"\n")


def load_profile(name: str | None) -> Profile:
    return Profile.load(Path.cwd() / "SERVATUS.toml", name=name)


def run_task(storage_root: Path, task: ExecutionTask) -> None:
    request = task.request
    if isinstance(request, TuneRequest):
        run_candidate(storage_root, request, cast(int, task.method_index))
    elif isinstance(request, TrainRequest):
        train(request, storage_root)
    else:
        evaluate(request, storage_root)


def result_probe(storage_root: Path) -> ResultProbe:
    studies: dict[UUID, TuneRequest] = {}

    def probe(task: Task) -> bool:
        envelope = ExecutionTask.model_validate_json(task.stdin)
        expected = execution_task(
            envelope.request, method_index=envelope.method_index, cell=envelope.cell
        )
        if task != expected:
            raise ValueError("Servatus Task does not match its execution envelope")

        request = envelope.request
        if isinstance(request, TuneRequest):
            if study_directory(storage_root, request.study_id).exists():
                canonical = studies.get(request.study_id)
                if canonical is None:
                    canonical = load_validated_study(storage_root, request.study_id).request
                    studies[request.study_id] = canonical
                if canonical != request:
                    raise ValueError("canonical Study request does not match execution task")
                return True
            method_index = cast(int, envelope.method_index)
            if not candidate_result_directory(storage_root, request, method_index).exists():
                return False
            load_candidate_result(storage_root, request, method_index)
            return True
        if isinstance(request, TrainRequest):
            if not artifact_directory(storage_root, request.artifact_id).exists():
                return False
            association, _ = load_artifact(storage_root, request.artifact_id)
            if association.request != request:
                raise ValueError("canonical Artifact request does not match execution task")
            return True
        if not evaluation_directory(storage_root, request.evaluation_id).exists():
            return False
        if load_evaluation(storage_root, request.evaluation_id) != request:
            raise ValueError("canonical Evaluation request does not match execution task")
        return True

    return probe
