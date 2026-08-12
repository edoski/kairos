"""Scientific block rows loaded from Blockweaver datasets."""

from __future__ import annotations

from pathlib import Path

import polars as pl
from blockweaver import Dataset, open_dataset
from pydantic import UUID4

_SCHEMA = pl.Schema(
    {
        "block_number": pl.Int64,
        "timestamp": pl.Int64,
        "base_fee_per_gas": pl.Int64,
        "gas_used": pl.Int64,
        "gas_limit": pl.Int64,
        "tx_count": pl.Int64,
        "effective_priority_fee_per_gas_p50": pl.Int64,
        "effective_priority_fee_per_gas_p90": pl.Int64,
    }
)


class BlockFrame:
    """One isolated frame of contiguous canonical block facts."""

    __slots__ = ("_chain_id", "_frame")

    def __init__(self, frame: pl.DataFrame, chain_id: int) -> None:
        if frame.schema != _SCHEMA:
            raise ValueError(f"Block schema must be exactly {_SCHEMA}, got {frame.schema}")
        if frame.is_empty():
            raise ValueError("BlockFrame must be nonempty")

        self._frame = frame.clone()
        self._chain_id = chain_id

    @property
    def chain_id(self) -> int:
        return self._chain_id

    @property
    def first_block(self) -> int:
        return int(self._frame[0, "block_number"])

    @property
    def last_block(self) -> int:
        return int(self._frame[-1, "block_number"])

    def select_range(self, first_block: int, last_block: int) -> BlockFrame:
        if first_block > last_block:
            raise ValueError("Selected range must not be inverted")
        if first_block < self.first_block or last_block > self.last_block:
            raise ValueError("Selected range must be within the BlockFrame extent")
        return BlockFrame(
            self._frame.slice(first_block - self.first_block, last_block - first_block + 1),
            self._chain_id,
        )

    def to_polars(self) -> pl.DataFrame:
        return self._frame.clone()


def open_corpus_dataset(storage_root: Path, corpus_id: UUID4) -> Dataset:
    """Open the UUID-addressed Blockweaver dataset without hydrating its rows."""

    return open_dataset(storage_root / "datasets" / str(corpus_id))


def load_corpus_blocks(storage_root: Path, corpus_id: UUID4) -> BlockFrame:
    """Load KAIROS block facts from a verified Blockweaver dataset."""

    dataset = open_corpus_dataset(storage_root, corpus_id)
    return BlockFrame(pl.read_parquet(dataset.data_path), dataset.chain_id)
