from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import kairos.corpus as corpus
from kairos.corpus import load_corpus_blocks, open_corpus_dataset

CORPUS_ID = UUID("11111111-1111-4111-8111-111111111111")
BLOCK_SCHEMA = {
    "block_number": pl.Int64,
    "timestamp": pl.Int64,
    "base_fee_per_gas": pl.Int64,
    "gas_used": pl.Int64,
    "gas_limit": pl.Int64,
    "tx_count": pl.Int64,
    "effective_priority_fee_per_gas_p50": pl.Int64,
    "effective_priority_fee_per_gas_p90": pl.Int64,
}


def _valid_blocks() -> pl.DataFrame:
    return pl.DataFrame(
        [
            (100, 1_000, 100, 50, 100, 10, 1, 2),
            (101, 1_012, 101, 51, 100, 11, 2, 4),
            (102, 1_024, 102, 52, 100, 12, 0, 0),
        ],
        schema=BLOCK_SCHEMA,
        orient="row",
    )


def test_corpus_adapter_reads_one_parquet_dataset(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocks = _valid_blocks()
    data_path = tmp_path / "blocks.parquet"
    blocks.write_parquet(data_path)
    dataset = SimpleNamespace(chain_id=137, data_path=data_path)
    opened: list[object] = []

    def open_dataset(path) -> object:
        opened.append(path)
        return dataset

    monkeypatch.setattr(corpus, "open_dataset", open_dataset)

    loaded = load_corpus_blocks(tmp_path, CORPUS_ID)

    assert open_corpus_dataset(tmp_path, CORPUS_ID) is dataset
    assert opened == [
        tmp_path / "datasets" / str(CORPUS_ID),
        tmp_path / "datasets" / str(CORPUS_ID),
    ]
    assert (loaded.chain_id, loaded.first_block, loaded.last_block) == (137, 100, 102)
    assert_frame_equal(loaded.to_polars(), blocks)
