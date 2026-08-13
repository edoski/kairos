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
from kairos.workers import ExecutionTask
from tests.helpers import (
    dispatch,
    fake_campaign,
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


def _launch_args(bundle: Path) -> tuple[str, ...]:
    return (str(bundle),)


def _candidate_tasks(bundle: Path) -> tuple[list[dict[str, str]], tuple[Task, ...]]:
    rows = read_tsv_rows(bundle / "cells.tsv")
    return rows, tuple(
        ExecutionTask(
            request=TuneRequest.model_validate_json(Path(row["request"]).read_bytes()),
            method_index=int(row["method_index"]),
            cell=row["cell"],
        ).task()
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
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    launcher = _load_launcher(monkeypatch)
    open_campaign, campaign = fake_campaign(monkeypatch, launcher)

    _, initial_tasks = _candidate_tasks(bundle)
    first = dispatch(launcher.app, "candidates", *_launch_args(bundle))

    hpo.extend(tmp_path, context_id, hpo_id, ["avalanche"])
    capsys.readouterr()
    _, full_tasks = _candidate_tasks(bundle)
    second = dispatch(launcher.app, "candidates", *_launch_args(bundle))

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert len(initial_tasks) == 27
    assert full_tasks[:27] == initial_tasks
    assert len(full_tasks) == 54
    assert [call.args for call in open_campaign.call_args_list] == [
        (tmp_path / "experiments" / ".servatus" / "hpo" / str(hpo_id), initial_tasks),
        (tmp_path / "experiments" / ".servatus" / "hpo" / str(hpo_id), full_tasks),
    ]
    assert [call.kwargs for call in campaign.plan.call_args_list] == [
        {"view": campaign.inspect.return_value, "retry": (), "tasks_per_allocation": None},
        {"view": campaign.inspect.return_value, "retry": (), "tasks_per_allocation": None},
    ]
    assert campaign.submit.call_count == 2


def test_candidates_plan_from_campaign_result_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    experiment_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    bundle = tmp_path / "experiments" / "feature_ablation" / f".{experiment_id}"
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    launcher = _load_launcher(monkeypatch)
    _, campaign = fake_campaign(monkeypatch, launcher)

    result = dispatch(launcher.app, "candidates", *_launch_args(bundle))

    assert result.exit_code == 0
    campaign.inspect.assert_called_once()
    assert campaign.plan.call_args.kwargs == {
        "view": campaign.inspect.return_value,
        "retry": (),
        "tasks_per_allocation": None,
    }


def test_candidates_require_one_request_per_study(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = TuneRequest.model_validate_json(
        Path(
            read_tsv_rows(
                tmp_path
                / "experiments"
                / "feature_ablation"
                / f".{UUID(run_script(_FEATURE_SCRIPT, 'prepare', tmp_path).stdout.strip())}"
                / "cells.tsv"
            )[0]["request"]
        ).read_bytes()
    )
    second = first.model_copy(update={"corpus_id": UUID("90000000-0000-4000-8000-000000000001")})
    bundle = tmp_path / "experiments" / "hpo" / ".bundle"
    (bundle / "requests").mkdir(parents=True)
    paths = (bundle / "requests" / "0.json", bundle / "requests" / "1.json")
    paths[0].write_text(first.model_dump_json(), encoding="utf-8")
    paths[1].write_text(second.model_dump_json(), encoding="utf-8")
    with (bundle / "cells.tsv").open("x", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination, delimiter="\t", lineterminator="\n")
        writer.writerow(("cell", "request", "method_index", "study_id"))
        writer.writerow(("first", paths[0], 0, first.study_id))
        writer.writerow(("second", paths[1], 0, first.study_id))
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    launcher = _load_launcher(monkeypatch)

    result = dispatch(launcher.app, "candidates", str(bundle))

    assert result.exit_code == 1
    assert str(result.exception) == "experiment candidates disagree on one Study request"


def test_workflows_submit_ordered_tasks_with_completion_retry_and_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, requests = _write_workflow_bundle(tmp_path, 9)
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    launcher = _load_launcher(monkeypatch)
    open_campaign, campaign = fake_campaign(monkeypatch, launcher)
    retry_key = ExecutionTask(request=requests[-1], cell="cell-8").task().key

    result = dispatch(
        launcher.app,
        "workflows",
        *_launch_args(bundle),
        "--profile",
        "OTHER",
        "--tasks-per-job",
        "4",
        "--retry",
        retry_key,
    )

    assert result.exit_code == 0
    assert result.output == "1001;research\n"
    tasks = tuple(
        ExecutionTask(request=request, cell=f"cell-{index}").task()
        for index, request in enumerate(requests)
    )
    assert open_campaign.call_args.args == (
        tmp_path / "experiments" / ".servatus" / "held_out" / "bundle",
        tasks,
    )
    profile = campaign.plan.call_args.args[0]
    assert profile.label == "OTHER"
    assert campaign.plan.call_args.kwargs == {
        "view": campaign.inspect.return_value,
        "retry": [retry_key],
        "tasks_per_allocation": 4,
    }
