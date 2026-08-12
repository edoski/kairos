"""Scientific block rows loaded from Blockweaver datasets."""

from __future__ import annotations

from pathlib import Path

import polars as pl
from blockweaver import Dataset, open_dataset
from pydantic import UUID4

from .config import CorpusDefinition

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

    __slots__ = ("_definition", "_frame")

    def __init__(self, frame: pl.DataFrame, definition: CorpusDefinition) -> None:
        if frame.schema != _SCHEMA:
            raise ValueError(f"Block schema must be exactly {_SCHEMA}, got {frame.schema}")

        self._frame = frame.clone()
        self._definition = definition

    @property
    def definition(self) -> CorpusDefinition:
        return self._definition

    def select_range(self, first_block: int, last_block: int) -> BlockFrame:
        if first_block > last_block:
            raise ValueError("Selected range must not be inverted")
        if first_block < self._definition.first_block or last_block > self._definition.last_block:
            raise ValueError("Selected range must be within the BlockFrame definition")

        definition = CorpusDefinition(
            chain_id=self._definition.chain_id, first_block=first_block, last_block=last_block
        )
        return BlockFrame(
            self._frame.slice(
                first_block - self._definition.first_block, last_block - first_block + 1
            ),
            definition,
        )

    def to_polars(self) -> pl.DataFrame:
        return self._frame.clone()


def _open_corpus_dataset(storage_root: Path, corpus_id: UUID4) -> Dataset:
    return open_dataset(storage_root / "datasets" / str(corpus_id))


def _definition(dataset: Dataset) -> CorpusDefinition:
    return CorpusDefinition(
        chain_id=dataset.chain_id, first_block=dataset.first_block, last_block=dataset.last_block
    )


def load_corpus_definition(storage_root: Path, corpus_id: UUID4) -> CorpusDefinition:
    """Load the scientific identity and range for one Blockweaver dataset."""

    return _definition(_open_corpus_dataset(storage_root, corpus_id))


def load_corpus_blocks(storage_root: Path, corpus_id: UUID4) -> BlockFrame:
    """Load KAIROS block facts from a verified Blockweaver dataset."""

    dataset = _open_corpus_dataset(storage_root, corpus_id)
    return BlockFrame(pl.read_parquet(dataset.data_path), _definition(dataset))
