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
from .study import candidate_result_directory, load_candidate_result, load_study

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

    def task(self) -> Task:
        """Project this validated KAIROS envelope into one Servatus Task."""

        if isinstance(self.request, TuneRequest):
            key = f"study:{self.request.study_id}:method:{cast(int, self.method_index)}"
        elif isinstance(self.request, TrainRequest):
            key = f"artifact:{self.request.artifact_id}"
        else:
            key = f"evaluation:{self.request.evaluation_id}"
        return Task(key, ("remote", "worker"), self.model_dump_json().encode("utf-8") + b"\n")


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
        if task != envelope.task():
            raise ValueError("Servatus Task does not match its execution envelope")
        request = envelope.request
        if isinstance(request, TuneRequest):
            study = study_directory(storage_root, request.study_id)
            if study.exists():
                canonical = studies.get(request.study_id)
                if canonical is None:
                    canonical = load_study(storage_root, request.study_id).request
                    studies[request.study_id] = canonical
                if canonical != request:
                    raise ValueError("canonical Study request does not match execution task")
                return True
            if not study.parent.exists():
                return False
            method_index = cast(int, envelope.method_index)
            result = candidate_result_directory(storage_root, request.study_id, method_index)
            if not result.exists():
                return False
            load_candidate_result(result, request, method_index)
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
