import importlib.util
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock
from uuid import UUID

import pytest
from servatus import JobReceipt

from kairos.experiments import ExperimentKind, experiment_campaign_directory
from tests.helpers import dispatch, write_servatus_config

_ROOT = Path(__file__).parents[2]
_LAUNCH_SCRIPT = _ROOT / "experiments" / "launch.py"
_EXPERIMENT_ID = UUID("10000000-0000-4000-8000-000000000001")


def _load_launcher(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.syspath_prepend(str(_ROOT / "experiments"))
    spec = importlib.util.spec_from_file_location("experiment_launch", _LAUNCH_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launch_uses_profile_result_view_retry_and_public_campaign_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_servatus_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    launcher = _load_launcher(monkeypatch)
    campaign = Mock()
    view = object()
    plan = object()
    campaign.inspect.return_value = view
    campaign.plan.return_value = plan
    campaign.submit.return_value = (JobReceipt("allocation", 1001, "research", ()),)
    load = Mock(return_value=campaign)
    monkeypatch.setattr(launcher, "Campaign", type("Campaign", (), {"load": load}))

    result = dispatch(
        launcher.app,
        str(tmp_path),
        ExperimentKind.HPO,
        str(_EXPERIMENT_ID),
        "--profile",
        "OTHER",
        "--tasks-per-job",
        "4",
        "--retry",
        "study:one:method:0",
        "--allow-duplicate-risk",
        "study:one:method:0",
    )

    assert result.exit_code == 0
    assert result.output == "1001;research\n"
    load.assert_called_once_with(
        experiment_campaign_directory(tmp_path, ExperimentKind.HPO, _EXPERIMENT_ID)
    )
    probe = campaign.inspect.call_args.args[0]
    profile = campaign.plan.call_args.args[0]
    assert profile.label == "OTHER"
    assert campaign.plan.call_args.kwargs == {
        "view": view,
        "retry": ["study:one:method:0"],
        "allow_duplicate_risk": ["study:one:method:0"],
        "tasks_per_allocation": 4,
    }
    campaign.submit.assert_called_once_with(plan, probe=probe)
