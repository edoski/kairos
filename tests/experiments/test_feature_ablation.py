from pathlib import Path
from uuid import UUID

from kairos.config import BlockWindow, TuneRequest
from tests.helpers import read_tsv_rows, run_script

_SCRIPT = Path(__file__).parents[2] / "experiments" / "feature_ablation.py"


def test_prepare_authors_the_exact_feature_roster(tmp_path: Path) -> None:
    experiment_id = UUID(run_script(_SCRIPT, "prepare", tmp_path).stdout.strip())
    bundle = tmp_path / "experiments" / "feature_ablation" / f".{experiment_id}"
    rows = read_tsv_rows(bundle / "cells.tsv")
    requests = [TuneRequest.model_validate_json(Path(row["request"]).read_bytes()) for row in rows]

    assert len(rows) == 102
    assert [row["cell"] for row in rows[:12]] == [
        "ethereum.lstm.full",
        "ethereum.lstm.without_base_fee",
        "ethereum.lstm.without_gas_utilization",
        "ethereum.lstm.without_exact_forming_base_fee",
        "ethereum.lstm.without_gas_limit",
        "ethereum.lstm.without_transaction_count",
        "ethereum.lstm.without_block_interval",
        "ethereum.lstm.without_hour",
        "ethereum.lstm.without_day_of_week",
        "ethereum.lstm.without_priority_fee_p50",
        "ethereum.lstm.without_priority_fee_p90",
        "ethereum.lstm.base_only",
    ]
    assert rows[-1]["cell"] == "avalanche.transformer_lstm.base_only"
    assert len({request.study_id for request in requests}) == 102
    assert {len(request.methods) for request in requests} == {1}
    assert {row["method_index"] for row in rows} == {"0"}
    assert requests[0].experiment.training_window == BlockWindow(
        first_parent_block=23_936_094, last_parent_block=25_118_158
    )
    assert requests[0].experiment.validation_window == BlockWindow(
        first_parent_block=25_118_359, last_parent_block=25_268_763
    )
    assert requests[0].experiment.context_blocks == 25
    assert requests[0].experiment.horizon_blocks == 5
    assert requests[0].experiment.ordered_features == (
        "log_base_fee_per_gas",
        "gas_utilization",
        "log_exact_forming_base_fee_per_gas",
        "log_gas_limit",
        "log1p_tx_count",
        "block_interval_seconds",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "log1p_effective_priority_fee_per_gas_p50",
        "log1p_effective_priority_fee_per_gas_p90",
    )
    assert requests[7].experiment.ordered_features == (
        "log_base_fee_per_gas",
        "gas_utilization",
        "log_exact_forming_base_fee_per_gas",
        "log_gas_limit",
        "log1p_tx_count",
        "block_interval_seconds",
        "dow_sin",
        "dow_cos",
        "log1p_effective_priority_fee_per_gas_p50",
        "log1p_effective_priority_fee_per_gas_p90",
    )
    assert requests[11].experiment.ordered_features == ("log_base_fee_per_gas",)
    assert "log_exact_forming_base_fee_per_gas" not in requests[-2].experiment.ordered_features
