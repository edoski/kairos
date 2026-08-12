from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
from types import ModuleType
from uuid import UUID

import pytest
from servatus import Task

from kairos.config import EvaluateRequest, TuneRequest
from kairos.study import RetainedResult, Study
from kairos.workers import CandidateProcessInput, candidate_task, workflow_task
from tests.experiments.helpers import publish_generated_studies
from tests.helpers import (
    capture_campaigns,
    dispatch,
    read_tsv_rows,
    run_script,
    window,
    write_servatus_config,
)

_ROOT = Path(__file__).parents[2]
_FEATURE_SCRIPT = _ROOT / "experiments" / "feature_ablation.py"
_HPO_SCRIPT = _ROOT / "experiments" / "hpo.py"
_LAUNCH_SCRIPT = _ROOT / "experiments" / "launch.py"


def _load_launcher(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.syspath_prepend(str(_ROOT / "experiments"))
    spec = importlib.util.spec_from_file_location("experiment_launch", _LAUNCH_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_hpo(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.syspath_prepend(str(_ROOT / "experiments"))
    spec = importlib.util.spec_from_file_location("experiment_hpo_for_launch", _HPO_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_workflow_bundle(root: Path, count: int) -> tuple[Path, list[EvaluateRequest]]:
    bundle = root / "experiments" / "held_out" / ".bundle"
    requests = bundle / "requests"
    requests.mkdir(parents=True)
    rows: list[tuple[str, Path]] = []
    values: list[EvaluateRequest] = []
    for index in range(count):
        request = EvaluateRequest(
            evaluation_id=UUID(f"10000000-0000-4000-8000-{index + 1:012d}"),
            artifact_id=UUID(f"20000000-0000-4000-8000-{index + 1:012d}"),
            corpus_id=UUID("30000000-0000-4000-8000-000000000001"),
            testing_window=window(300),
        )
        path = requests / f"{index}.json"
        path.write_text(request.model_dump_json(), encoding="utf-8")
        rows.append((f"cell-{index}", path))
        values.append(request)
    with (bundle / "cells.tsv").open("x", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination, delimiter="\t", lineterminator="\n")
        writer.writerow(("cell", "request"))
        writer.writerows(rows)
    return bundle, values


def _launch_args(bundle: Path, target: Path, resources: Path) -> tuple[str, ...]:
    return (str(bundle), "--target", str(target), "--resources", str(resources))


def _candidate_tasks(bundle: Path) -> tuple[list[dict[str, str]], tuple[Task, ...]]:
    rows = read_tsv_rows(bundle / "cells.tsv")
    return rows, tuple(
        candidate_task(
            CandidateProcessInput(
                request=TuneRequest.model_validate_json(Path(row["request"]).read_bytes()),
                method_index=int(row["method_index"]),
            )
        )
        for row in rows
    )


def test_hpo_extend_reopens_campaign_with_exact_authored_suffix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    feature_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    feature_bundle = tmp_path / "experiments" / "feature_ablation" / f".{feature_id}"
    source_rows = {row["cell"]: row for row in read_tsv_rows(feature_bundle / "cells.tsv")}
    families = ("lstm", "transformer", "transformer_lstm")
    sources = {
        (chain, family): Study(
            request=TuneRequest.model_validate_json(
                Path(source_rows[f"{chain}.{family}.full"]["request"]).read_bytes()
            ),
            trials=(RetainedResult(objective=1.0, selected_epoch=1, completed_epochs=1),),
        )
        for chain in ("ethereum", "avalanche")
        for family in families
    }
    hpo = _load_hpo(monkeypatch)
    monkeypatch.setattr(
        hpo,
        "selected_context_studies",
        lambda _root, _experiment_id, chains: (
            {(chain, family): sources[chain, family] for chain in chains for family in families},
            (),
        ),
    )
    context_id = UUID("40000000-0000-4000-8000-000000000001")
    hpo.prepare(tmp_path, context_id, ["ethereum"])
    hpo_id = UUID(capsys.readouterr().out.strip())
    bundle = tmp_path / "experiments" / "hpo" / f".{hpo_id}"
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = capture_campaigns(monkeypatch, launcher)

    initial_rows, initial_tasks = _candidate_tasks(bundle)
    initial_request_bytes = tuple(Path(row["request"]).read_bytes() for row in initial_rows)
    first = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))

    hpo.extend(tmp_path, context_id, hpo_id, ["avalanche"])
    capsys.readouterr()
    full_rows, full_tasks = _candidate_tasks(bundle)
    second = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert len(initial_rows) == 27
    assert full_rows[:27] == initial_rows
    assert (
        tuple(Path(row["request"]).read_bytes() for row in full_rows[:27]) == initial_request_bytes
    )
    assert full_tasks[:27] == initial_tasks
    assert len(full_tasks) == 54
    assert [call.path for call in calls] == [bundle / ".servatus"] * 2
    assert [call.tasks for call in calls] == [initial_tasks, full_tasks]
    assert [call.options for call in calls] == [
        {"completed": set(), "retry": (), "tasks_per_allocation": 4},
        {"completed": set(), "retry": (), "tasks_per_allocation": 4},
    ]
    assert all(call.submitted for call in calls)


def test_candidates_skip_exact_canonical_studies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    experiment_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    bundle = tmp_path / "experiments" / "feature_ablation" / f".{experiment_id}"
    rows = read_tsv_rows(bundle / "cells.tsv")
    publish_generated_studies(tmp_path, rows[:9], default_objective=1.0)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = capture_campaigns(monkeypatch, launcher)

    result = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))

    assert result.exit_code == 0
    expected_completed = {
        candidate_task(
            CandidateProcessInput(
                request=TuneRequest.model_validate_json(Path(row["request"]).read_bytes()),
                method_index=int(row["method_index"]),
            )
        ).key
        for row in rows[:9]
    }
    assert calls[0].options == {
        "completed": expected_completed,
        "retry": (),
        "tasks_per_allocation": 4,
    }


def test_workflows_preserve_kairos_nine_task_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, requests = _write_workflow_bundle(tmp_path, 9)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = capture_campaigns(monkeypatch, launcher)

    result = dispatch(
        launcher.app, "workflows", *_launch_args(bundle, target, resources), "--tasks-per-job", "4"
    )

    assert result.exit_code == 0
    assert calls[0].path == bundle / ".servatus"
    assert calls[0].tasks == tuple(workflow_task(request) for request in requests)
    assert calls[0].options == {"completed": set(), "retry": (), "tasks_per_allocation": 4}
    assert calls[0].target is not None and calls[0].target.host == "research-alias"
    assert calls[0].resources is not None and calls[0].resources.gpus_per_task == 1
    assert calls[0].submitted


def test_workflows_skip_exact_canonical_evaluations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, requests = _write_workflow_bundle(tmp_path, 2)
    canonical = tmp_path / "evaluations" / str(requests[0].evaluation_id)
    canonical.mkdir(parents=True)
    (canonical / "evaluation.json").write_text(requests[0].model_dump_json(), encoding="utf-8")
    observations = canonical / "observations.parquet"
    observations.touch()
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    validated: list[Path] = []
    monkeypatch.setattr(launcher, "validate_observations", validated.append)
    calls = capture_campaigns(monkeypatch, launcher)

    result = dispatch(launcher.app, "workflows", *_launch_args(bundle, target, resources))

    assert result.exit_code == 0
    assert validated == [observations]
    assert calls[0].options["completed"] == {workflow_task(requests[0]).key}


@pytest.mark.parametrize("tasks_per_job", [1, 5])
def test_kairos_rejects_nonproduction_packing_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tasks_per_job: int
) -> None:
    bundle, _ = _write_workflow_bundle(tmp_path, 2)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)

    result = dispatch(
        launcher.app,
        "workflows",
        *_launch_args(bundle, target, resources),
        "--tasks-per-job",
        str(tasks_per_job),
    )

    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert str(result.exception) == "tasks per job must be between two and four"


@pytest.mark.parametrize("gpus_per_task", [0, 2])
def test_kairos_requires_one_explicit_gpu_per_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, gpus_per_task: int
) -> None:
    bundle, _ = _write_workflow_bundle(tmp_path, 2)
    target, resources = write_servatus_config(tmp_path)
    resources.write_text(
        resources.read_text().replace("gpus_per_task = 1", f"gpus_per_task = {gpus_per_task}"),
        encoding="utf-8",
    )
    launcher = _load_launcher(monkeypatch)

    result = dispatch(launcher.app, "workflows", *_launch_args(bundle, target, resources))

    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert str(result.exception) == "KAIROS experiment tasks require exactly one GPU"


def test_explicit_retry_selects_exact_task_and_prints_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, requests = _write_workflow_bundle(tmp_path, 2)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = capture_campaigns(monkeypatch, launcher)
    args = _launch_args(bundle, target, resources)

    retry = dispatch(
        launcher.app, "workflows", *args, "--retry", f"evaluation:{requests[1].evaluation_id}"
    )

    assert retry.exit_code == 0
    assert calls[0].options["retry"] == [f"evaluation:{requests[1].evaluation_id}"]
    assert retry.output == "1001;research\n"
