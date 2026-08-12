from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from uuid import UUID

import polars as pl
import pytest
from click.testing import Result
from servatus import JobReceipt, ResourceRequest, SlurmTarget, Task
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

_BLOCK_SCHEMA = [
    {"name": "block_number", "type": "Int64", "unit": "block"},
    {"name": "timestamp", "type": "Int64", "unit": "unix_second"},
    {"name": "base_fee_per_gas", "type": "Int64", "unit": "wei/gas"},
    {"name": "gas_used", "type": "Int64", "unit": "gas"},
    {"name": "gas_limit", "type": "Int64", "unit": "gas"},
    {"name": "tx_count", "type": "Int64", "unit": "transaction"},
    {"name": "effective_priority_fee_per_gas_p50", "type": "Int64", "unit": "wei/gas"},
    {"name": "effective_priority_fee_per_gas_p90", "type": "Int64", "unit": "wei/gas"},
]


@dataclass
class CampaignCall:
    path: Path
    tasks: tuple[Task, ...]
    target: SlurmTarget | None = None
    resources: ResourceRequest | None = None
    options: dict[str, object] = field(default_factory=dict)
    submitted: bool = False


def capture_campaigns(monkeypatch: pytest.MonkeyPatch, module: ModuleType) -> list[CampaignCall]:
    calls: list[CampaignCall] = []

    class FakeCampaign:
        def __init__(self, call: CampaignCall) -> None:
            self.call = call

        @classmethod
        def open(cls, path: Path, tasks: tuple[Task, ...]) -> FakeCampaign:
            call = CampaignCall(path, tasks)
            calls.append(call)
            return cls(call)

        def plan(
            self, target: SlurmTarget, resources: ResourceRequest, **options: object
        ) -> CampaignCall:
            self.call.target = target
            self.call.resources = resources
            self.call.options = options
            return self.call

        def submit(self, plan: CampaignCall) -> tuple[JobReceipt, ...]:
            assert plan is self.call
            self.call.submitted = True
            index = calls.index(self.call) + 1
            return (
                JobReceipt(
                    f"allocation-{index}",
                    1_000 + index,
                    "research",
                    tuple(task.key for task in self.call.tasks),
                ),
            )

    monkeypatch.setattr(module, "Campaign", FakeCampaign)
    return calls


def write_blockweaver_dataset(
    storage_root: Path, dataset_id: UUID, frame: pl.DataFrame, *, chain_id: int = 1
) -> Path:
    """Write one minimal valid Blockweaver 0.3.2 test artifact."""

    destination = storage_root / "datasets" / str(dataset_id)
    destination.mkdir(parents=True)
    data_path = destination / "blocks.parquet"
    frame.write_parquet(data_path)

    first_block = int(frame[0, "block_number"])
    last_block = int(frame[-1, "block_number"])
    first_timestamp = int(frame[0, "timestamp"])
    last_timestamp = int(frame[-1, "timestamp"])
    data = data_path.read_bytes()
    manifest = {
        "acquisition_plan": {
            "families": [
                {
                    "family": "header",
                    "fields": [
                        "number",
                        "hash",
                        "parentHash",
                        "timestamp",
                        "baseFeePerGas",
                        "gasUsed",
                        "gasLimit",
                        "transactions",
                    ],
                    "method": "eth_getBlockByNumber",
                },
                {
                    "family": "fee_history",
                    "method": "eth_feeHistory",
                    "reward_percentiles": [50, 90],
                },
            ]
        },
        "chain": {"chain_id": chain_id, "name": "test"},
        "completed_at": "2026-01-01T00:00:00Z",
        "dataset_id": str(dataset_id),
        "finalized_anchor": {
            "block_hash": "0x" + "b" * 64,
            "block_number": last_block + 1,
            "tag": "finalized",
        },
        "output": {
            "bytes": len(data),
            "filename": data_path.name,
            "format": "parquet",
            "sha256": hashlib.sha256(data).hexdigest(),
        },
        "requested_range": {"from": first_block, "kind": "block", "to": last_block},
        "resolved_range": {
            "from_block": first_block,
            "from_timestamp": first_timestamp,
            "to_block": last_block,
            "to_timestamp": last_timestamp,
        },
        "row_count": frame.height,
        "schema": _BLOCK_SCHEMA,
        "source": {"provider": "primary", "type": "rpc", "verifier": "verifier"},
        "target_hash": "0x" + "a" * 64,
        "tool_version": "0.3.2",
        "verification": {
            "primary_chain_id": chain_id,
            "sampled_blocks": sorted({first_block, last_block}),
            "target_agreement": True,
            "verifier_chain_id": chain_id,
        },
    }
    (destination / "manifest.json").write_text(
        json.dumps(
            manifest, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
        )
        + "\n",
        encoding="utf-8",
    )
    return destination


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
