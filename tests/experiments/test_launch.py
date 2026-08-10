from __future__ import annotations

import base64
import csv
import importlib.util
from pathlib import Path
from types import ModuleType
from uuid import UUID

import pytest
from servatus import Campaign, ResourceRequest, SlurmTarget, Task, _slurm

from kairos.config import EvaluateRequest, TuneRequest
from kairos.study import RetainedResult, Study
from kairos.workers import CandidateProcessInput, candidate_task
from tests.experiments.helpers import publish_generated_studies
from tests.helpers import dispatch, read_tsv_rows, run_script, window, write_servatus_config

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


def _capture_submissions(monkeypatch: pytest.MonkeyPatch) -> list[tuple[tuple[str, ...], bytes]]:
    calls: list[tuple[tuple[str, ...], bytes]] = []

    def submit(_target: SlurmTarget, argv: tuple[str, ...], script: bytes) -> _slurm.Result:
        calls.append((argv, script))
        return _slurm.Result(0, f"{1_000 + len(calls)};research\n".encode(), b"")

    monkeypatch.setattr(_slurm, "_run_ssh", submit)
    return calls


def _launch_args(bundle: Path, target: Path, resources: Path) -> tuple[str, ...]:
    return (str(bundle), "--target", str(target), "--resources", str(resources))


def _task_count(argv: tuple[str, ...]) -> int:
    return int(next(arg.removeprefix("--ntasks=") for arg in argv if arg.startswith("--ntasks=")))


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


def test_candidates_use_domain_tasks_and_restart_from_servatus_receipts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    experiment_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    bundle = tmp_path / "experiments" / "feature_ablation" / f".{experiment_id}"
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = _capture_submissions(monkeypatch)

    result = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))

    assert result.exit_code == 0
    assert result.output.splitlines() == [f"{job_id};research" for job_id in range(1_001, 1_027)]
    assert [_task_count(argv) for argv, _ in calls] == [4] * 24 + [3, 3]
    assert all(script.count(b"remote candidate") == _task_count(argv) for argv, script in calls)
    assert (bundle / ".servatus-campaign").is_dir()

    repeated = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))

    assert repeated.exit_code == 0
    assert repeated.output == ""
    assert len(calls) == 26


def test_hpo_extend_reopens_campaign_and_submits_only_authored_suffix(
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
    calls = _capture_submissions(monkeypatch)

    initial_rows, initial_tasks = _candidate_tasks(bundle)
    initial_request_bytes = tuple(Path(row["request"]).read_bytes() for row in initial_rows)
    first = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))
    first_call_count = len(calls)

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
    suffix = full_tasks[27:]
    suffix_calls = calls[first_call_count:]
    suffix_scripts = b"".join(script for _, script in suffix_calls)
    status = Campaign.open(bundle / ".servatus-campaign", full_tasks).status()
    assert first_call_count == 7
    assert [_task_count(argv) for argv, _ in suffix_calls] == [4] * 6 + [3]
    assert tuple(key for receipt in status.receipts for key in receipt.task_keys) == tuple(
        task.key for task in full_tasks
    )
    assert status.pending_task_keys == ()
    assert all(base64.b64encode(task.stdin) not in suffix_scripts for task in initial_tasks)
    assert all(suffix_scripts.count(base64.b64encode(task.stdin)) == 1 for task in suffix)
    assert [suffix_scripts.index(base64.b64encode(task.stdin)) for task in suffix] == sorted(
        suffix_scripts.index(base64.b64encode(task.stdin)) for task in suffix
    )


def test_candidates_skip_exact_canonical_studies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    experiment_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    bundle = tmp_path / "experiments" / "feature_ablation" / f".{experiment_id}"
    rows = read_tsv_rows(bundle / "cells.tsv")
    publish_generated_studies(tmp_path, rows[:9], default_objective=1.0)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = _capture_submissions(monkeypatch)

    result = dispatch(launcher.app, "candidates", *_launch_args(bundle, target, resources))

    assert result.exit_code == 0
    assert [_task_count(argv) for argv, _ in calls] == [4] * 21 + [3, 3, 3]


def test_workflows_preserve_kairos_nine_task_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, requests = _write_workflow_bundle(tmp_path, 9)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = _capture_submissions(monkeypatch)

    result = dispatch(
        launcher.app, "workflows", *_launch_args(bundle, target, resources), "--tasks-per-job", "4"
    )

    assert result.exit_code == 0
    assert [_task_count(argv) for argv, _ in calls] == [3, 3, 3]
    combined = b"".join(script for _, script in calls)
    positions = [
        combined.index(base64.b64encode(request.model_dump_json().encode() + b"\n"))
        for request in requests
    ]
    assert positions == sorted(positions)


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
    calls = _capture_submissions(monkeypatch)

    result = dispatch(launcher.app, "workflows", *_launch_args(bundle, target, resources))

    assert result.exit_code == 0
    assert validated == [observations]
    assert [_task_count(argv) for argv, _ in calls] == [1]
    script = calls[0][1]
    assert base64.b64encode(requests[0].model_dump_json().encode() + b"\n") not in script
    assert base64.b64encode(requests[1].model_dump_json().encode() + b"\n") in script


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


@pytest.mark.parametrize("count", [102, 108])
@pytest.mark.parametrize("capacity", [2, 3, 4])
def test_current_campaign_sizes_fit_one_submit(tmp_path: Path, count: int, capacity: int) -> None:
    target = SlurmTarget.from_toml(_ROOT / "REMOTE.toml")
    resources = ResourceRequest.from_toml(_ROOT / "RESOURCES.toml")
    tasks = tuple(Task(f"task-{index}", ("remote", "workflow"), b"{}\n") for index in range(count))

    plan = Campaign.open(tmp_path / f"campaign-{count}-{capacity}", tasks).plan(
        target, resources, tasks_per_allocation=capacity
    )

    expected = (count + capacity - 1) // capacity
    assert len(plan.allocations) == expected
    assert expected <= target.max_allocations_per_submit


def test_largest_current_hpo_payload_fits_live_script_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    experiment_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    bundle = tmp_path / "experiments" / "feature_ablation" / f".{experiment_id}"
    feature_request = TuneRequest.model_validate_json(
        Path(read_tsv_rows(bundle / "cells.tsv")[0]["request"]).read_bytes()
    )
    hpo = _load_hpo(monkeypatch)
    request = feature_request.model_copy(
        update={"methods": hpo._methods(feature_request.methods[0])}
    )
    tasks = tuple(
        candidate_task(CandidateProcessInput(request=request, method_index=index))
        for index in range(4)
    )
    target = SlurmTarget.from_toml(_ROOT / "REMOTE.toml")
    resources = ResourceRequest.from_toml(_ROOT / "RESOURCES.toml")

    plan = Campaign.open(tmp_path / "largest-payload", tasks).plan(
        target, resources, tasks_per_allocation=4
    )

    assert len(plan.allocations) == 1
    assert plan.allocations[0].task_keys == tuple(task.key for task in tasks)


def test_explicit_retry_resubmits_only_selected_accepted_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, requests = _write_workflow_bundle(tmp_path, 2)
    target, resources = write_servatus_config(tmp_path)
    launcher = _load_launcher(monkeypatch)
    calls = _capture_submissions(monkeypatch)
    args = _launch_args(bundle, target, resources)

    first = dispatch(launcher.app, "workflows", *args)
    retry = dispatch(
        launcher.app, "workflows", *args, "--retry", f"evaluation:{requests[1].evaluation_id}"
    )

    assert first.exit_code == 0
    assert retry.exit_code == 0
    assert [_task_count(argv) for argv, _ in calls] == [2, 1]
    assert retry.output == "1002;research\n"
