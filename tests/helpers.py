from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import Mock

import pytest
from click.testing import Result
from servatus import CampaignView, JobReceipt
from torch.utils.data import DataLoader, Dataset
from typer import Typer
from typer.testing import CliRunner

from kairos.config import BlockWindow

SERVATUS_TOML = """default_profile = "TEST"

[profiles.TEST.target]
host = "research-alias"
slurm_bin = "/opt/slurm/bin"
apptainer = "/usr/bin/apptainer"
image = "/opt/kairos image.sif"
work_root = "/remote/storage root"
log_root = "/remote/log root"
partitions = ["thesis-partition"]
gpu_gres = "gpu:a100"
max_tasks_per_allocation = 4
max_cpus_per_allocation = 32
max_memory_mib_per_allocation = 196608
max_gpus_per_allocation = 4
max_time_limit = "3-00:00:00"
max_allocations_per_submit = 64
max_script_bytes = 1048576

[profiles.TEST.resources]
cpus_per_task = 8
memory_mib_per_task = 49152
gpus_per_task = 1
time_limit = "17:23:45"

[profiles.OTHER.target]
host = "other-research"
slurm_bin = "/opt/slurm/bin"
apptainer = "/usr/bin/apptainer"
image = "/opt/other.sif"
work_root = "/remote/other"
log_root = "/remote/other-logs"
partitions = ["other-partition"]
gpu_gres = "gpu:a100"
max_tasks_per_allocation = 2
max_cpus_per_allocation = 16
max_memory_mib_per_allocation = 98304
max_gpus_per_allocation = 2
max_time_limit = "1-00:00:00"
max_allocations_per_submit = 16
max_script_bytes = 1048576

[profiles.OTHER.resources]
cpus_per_task = 4
memory_mib_per_task = 24576
gpus_per_task = 1
time_limit = "12:00:00"
"""


def fake_campaign(monkeypatch: pytest.MonkeyPatch, module: ModuleType) -> tuple[Mock, Mock]:
    receipt = JobReceipt("allocation", 1001, "research", ())
    campaign = Mock()
    campaign.inspect.return_value = Mock(spec=CampaignView)
    campaign.plan.return_value = object()
    campaign.submit.return_value = (receipt,)
    open_campaign = Mock(return_value=campaign)
    monkeypatch.setattr(module, "Campaign", SimpleNamespace(open=open_campaign))
    return open_campaign, campaign


def run_script(script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(argument) for argument in arguments)],
        check=True,
        capture_output=True,
        text=True,
    )


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def write_servatus_config(root: Path) -> Path:
    path = root / "SERVATUS.toml"
    path.write_text(SERVATUS_TOML, encoding="utf-8")
    return path


def dispatch(app: Typer, *arguments: str, input: str | None = None) -> Result:
    return CliRunner().invoke(app, list(arguments), input=input)


def single_process_loader(
    dataset: Dataset[Any], *, batch_size: int, shuffle: bool
) -> DataLoader[Any]:
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def window(first: int) -> BlockWindow:
    return BlockWindow(first_parent_block=first, last_parent_block=first + 9)
