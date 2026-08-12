from __future__ import annotations

from pathlib import Path
from uuid import UUID

import numpy as np
import polars as pl

from kairos.config import (
    BlockWindow,
    EvaluateRequest,
    ExperimentSemantics,
    FitMethod,
    LstmDefinition,
    Method,
    TrainRequest,
    TuneRequest,
)
from kairos.experiments import ExperimentKind, ExperimentManifest, experiment_manifest_path
from kairos.study import RetainedResult, Study
from tests.experiments.helpers import publish_test_study
from tests.helpers import read_tsv_rows, run_script, write_blockweaver_dataset

_ROOT = Path(__file__).parents[2]
_K_STUDY_SCRIPT = _ROOT / "experiments" / "k_study.py"
_HELD_OUT_SCRIPT = _ROOT / "experiments" / "held_out.py"
_HPO_EXPERIMENT_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
_CORPUS_ID = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
_HORIZONS = (2, 3, 4, 5, 10, 25, 50, 100, 200)
_METHOD = Method(
    model=LstmDefinition(family="lstm", hidden=2, layers=1, head_hidden=2, dropout=0.0),
    fit=FitMethod(
        learning_rate=0.001,
        weight_decay=0.0,
        accumulation=1,
        gradient_clip_norm=1.0,
        seed=2026,
        max_epochs=2,
        validate_every_completed_epoch=1,
        patience=0,
        min_delta=0.0,
    ),
)


def _publish_hpo(storage_root: Path) -> None:
    cells = {}
    for index, cell in enumerate(
        f"{chain}.{family}"
        for chain in ("ethereum", "polygon", "avalanche")
        for family in ("lstm", "transformer", "transformer_lstm")
    ):
        study_id = UUID(f"10000000-0000-4000-8000-{index:012d}")
        request = TuneRequest(
            study_id=study_id,
            corpus_id=_CORPUS_ID,
            experiment=ExperimentSemantics(
                training_window=BlockWindow(first_parent_block=100, last_parent_block=200),
                validation_window=BlockWindow(first_parent_block=401, last_parent_block=500),
                context_blocks=25,
                horizon_blocks=5,
                ordered_features=("log_base_fee_per_gas",),
            ),
            methods=(
                _METHOD,
                _METHOD.model_copy(update={"fit": _METHOD.fit.model_copy(update={"seed": index})}),
            ),
        )
        publish_test_study(
            storage_root,
            Study(
                request=request,
                trials=(
                    RetainedResult(objective=2.0, selected_epoch=1, completed_epochs=1),
                    RetainedResult(objective=1.0, selected_epoch=1, completed_epochs=1),
                ),
            ),
        )
        cells[cell] = study_id
    manifest_path = experiment_manifest_path(storage_root, ExperimentKind.HPO, _HPO_EXPERIMENT_ID)
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(ExperimentManifest(root=cells).model_dump_json(), encoding="utf-8")


def test_k_study_and_held_out_author_the_exact_rosters_and_windows(tmp_path: Path) -> None:
    _publish_hpo(tmp_path)

    k_experiment_id = UUID(
        run_script(_K_STUDY_SCRIPT, "prepare", tmp_path, _HPO_EXPERIMENT_ID).stdout.strip()
    )
    k_bundle = tmp_path / "experiments" / "k_study" / f".{k_experiment_id}"
    rows = read_tsv_rows(k_bundle / "cells.tsv")
    requests = [TrainRequest.model_validate_json(Path(row["request"]).read_bytes()) for row in rows]

    assert [row["cell"] for row in rows] == [
        f"{chain}.lstm.K{horizon}"
        for chain in ("ethereum", "polygon", "avalanche")
        for horizon in _HORIZONS
    ]
    assert [request.source.experiment.horizon_blocks for request in requests[:9]] == list(_HORIZONS)
    assert {request.source.study_result_index for request in requests} == {1}
    assert len({request.artifact_id for request in requests}) == 27

    k_manifest = ExperimentManifest(root={row["cell"]: UUID(row["artifact_id"]) for row in rows})
    canonical_path = experiment_manifest_path(tmp_path, ExperimentKind.K_STUDY, k_experiment_id)
    canonical_path.parent.mkdir(parents=True)
    canonical_path.write_text(k_manifest.model_dump_json(), encoding="utf-8")
    blocks = np.arange(1_001, dtype=np.int64)
    write_blockweaver_dataset(
        tmp_path,
        _CORPUS_ID,
        pl.DataFrame(
            {
                "block_number": blocks,
                "timestamp": blocks,
                "base_fee_per_gas": blocks + 1,
                "gas_used": blocks,
                "gas_limit": blocks + 1,
                "tx_count": blocks,
                "effective_priority_fee_per_gas_p50": blocks,
                "effective_priority_fee_per_gas_p90": blocks,
            }
        ),
    )

    held_out_id = UUID(
        run_script(
            _HELD_OUT_SCRIPT, "prepare", tmp_path, _HPO_EXPERIMENT_ID, k_experiment_id
        ).stdout.strip()
    )
    held_out_bundle = tmp_path / "experiments" / "held_out" / f".{held_out_id}"
    evaluation_rows = read_tsv_rows(held_out_bundle / "cells.tsv")
    evaluation_requests = [
        EvaluateRequest.model_validate_json(Path(row["request"]).read_bytes())
        for row in evaluation_rows
    ]

    assert [row["cell"] for row in evaluation_rows] == [
        f"{chain}.lstm.K{horizon}"
        for chain in ("ethereum", "polygon", "avalanche")
        for horizon in _HORIZONS
    ]
    assert len({request.evaluation_id for request in evaluation_requests}) == 27
    assert [request.testing_window for request in evaluation_requests[:4]] == [
        BlockWindow(first_parent_block=701, last_parent_block=803),
        BlockWindow(first_parent_block=701, last_parent_block=802),
        BlockWindow(first_parent_block=701, last_parent_block=801),
        BlockWindow(first_parent_block=701, last_parent_block=800),
    ]
