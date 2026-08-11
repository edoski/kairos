from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from click.testing import Result
from typer import Typer
from typer.testing import CliRunner

from kairos.config import BlockWindow

REMOTE_TOML = """host = "research-alias"
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
"""

RESOURCES_TOML = """cpus_per_task = 8
memory_mib_per_task = 49152
gpus_per_task = 1
time_limit = "17:23:45"
"""


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


def write_servatus_config(root: Path) -> tuple[Path, Path]:
    target = root / "REMOTE.toml"
    resources = root / "RESOURCES.toml"
    target.write_text(REMOTE_TOML, encoding="utf-8")
    resources.write_text(RESOURCES_TOML, encoding="utf-8")
    return target, resources


def dispatch(app: Typer, *arguments: str, input: str | None = None) -> Result:
    return CliRunner().invoke(app, list(arguments), input=input)


def window(first: int) -> BlockWindow:
    return BlockWindow(first_parent_block=first, last_parent_block=first + 9)
