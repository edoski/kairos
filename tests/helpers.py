from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import polars as pl
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

_BLOCK_UNITS = {
    "block_number": "block",
    "timestamp": "unix_second",
    "block_hash": "hex",
    "base_fee_per_gas": "wei/gas",
    "gas_used": "gas",
    "gas_limit": "gas",
    "tx_count": "transaction",
    "effective_priority_fee_per_gas_p50": "wei/gas",
    "effective_priority_fee_per_gas_p90": "wei/gas",
}


def write_blockweaver_dataset(
    storage_root: Path,
    dataset_id: UUID,
    frame: pl.DataFrame,
    *,
    chain_id: int = 1,
    output_format: str = "parquet",
) -> Path:
    """Write one minimal valid Blockweaver 0.3.2 test artifact."""

    destination = storage_root / "datasets" / str(dataset_id)
    destination.mkdir(parents=True)
    data_path = destination / f"blocks.{output_format}"
    if output_format == "parquet":
        frame.write_parquet(data_path)
    else:
        frame.write_csv(data_path)

    first_block = int(frame[0, "block_number"])
    last_block = int(frame[-1, "block_number"])
    first_timestamp = int(frame[0, "timestamp"])
    last_timestamp = int(frame[-1, "timestamp"])
    percentiles = [
        percentile
        for percentile in (50, 90)
        if f"effective_priority_fee_per_gas_p{percentile}" in frame.columns
    ]
    header_fields = ["number", "hash", "parentHash", "timestamp"]
    for column, rpc_field in (
        ("base_fee_per_gas", "baseFeePerGas"),
        ("gas_used", "gasUsed"),
        ("gas_limit", "gasLimit"),
        ("tx_count", "transactions"),
    ):
        if column in frame.columns and rpc_field not in header_fields:
            header_fields.append(rpc_field)
    families: list[dict[str, object]] = [
        {"family": "header", "method": "eth_getBlockByNumber", "fields": header_fields}
    ]
    if percentiles:
        families.append(
            {"family": "fee_history", "method": "eth_feeHistory", "reward_percentiles": percentiles}
        )

    data = data_path.read_bytes()
    target_hash = str(frame[-1, "block_hash"]) if "block_hash" in frame.columns else "0x" + "a" * 64
    manifest = {
        "acquisition_plan": {"families": families},
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
            "format": output_format,
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
        "schema": [
            {
                "name": name,
                "type": "UTF-8" if name == "block_hash" else "Int64",
                "unit": _BLOCK_UNITS[name],
            }
            for name in frame.columns
        ],
        "source": {"provider": "primary", "type": "rpc", "verifier": "verifier"},
        "target_hash": target_hash,
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
