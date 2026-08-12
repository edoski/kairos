from __future__ import annotations

from uuid import UUID

import polars as pl
from polars.testing import assert_frame_equal

from kairos.config import CorpusDefinition
from kairos.corpus import load_corpus_blocks, load_corpus_definition
from tests.helpers import write_blockweaver_dataset

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


def test_load_corpus_reads_one_valid_blockweaver_dataset(tmp_path) -> None:
    blocks = _valid_blocks()
    write_blockweaver_dataset(tmp_path, CORPUS_ID, blocks, chain_id=137)

    loaded = load_corpus_blocks(tmp_path, CORPUS_ID)

    assert loaded.definition == CorpusDefinition(chain_id=137, first_block=100, last_block=102)
    assert_frame_equal(loaded.to_polars(), blocks)
    assert load_corpus_definition(tmp_path, CORPUS_ID) == loaded.definition
