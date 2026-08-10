from pathlib import Path
from uuid import UUID

import pytest

import experiments.bundle as bundle_module
from experiments.bundle import close_bundle, load_roster, open_bundle, write_tune_cells
from kairos.config import (
    BlockWindow,
    ExperimentSemantics,
    FitMethod,
    LstmDefinition,
    Method,
    TuneRequest,
)
from kairos.experiments import ExperimentKind, load_experiment_manifest

_EXPERIMENT_ID = UUID("10000000-0000-4000-8000-000000000001")
_STUDY_ID = UUID("20000000-0000-4000-8000-000000000001")


def _request() -> TuneRequest:
    return TuneRequest(
        study_id=_STUDY_ID,
        corpus_id=UUID("30000000-0000-4000-8000-000000000001"),
        experiment=ExperimentSemantics(
            training_window=BlockWindow(first_parent_block=1, last_parent_block=10),
            validation_window=BlockWindow(first_parent_block=13, last_parent_block=20),
            context_blocks=1,
            horizon_blocks=2,
            ordered_features=("log_base_fee_per_gas",),
        ),
        methods=(
            Method(
                model=LstmDefinition(family="lstm", hidden=1, layers=1, head_hidden=1, dropout=0.0),
                fit=FitMethod(
                    learning_rate=0.001,
                    weight_decay=0.0,
                    accumulation=1,
                    gradient_clip_norm=1.0,
                    seed=1,
                    max_epochs=1,
                    validate_every_completed_epoch=1,
                    patience=0,
                    min_delta=0.0,
                ),
            ),
        ),
    )


def test_close_preserves_bundle_after_verifier_failure_then_retries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = open_bundle(tmp_path, ExperimentKind.FEATURE_ABLATION, _EXPERIMENT_ID)
    write_tune_cells(bundle, [("ethereum.lstm.full", _request())])
    campaign = bundle / ".servatus-campaign"
    campaign.mkdir()
    (campaign / "state.json").write_text("temporary", encoding="utf-8")
    inputs = {
        path.relative_to(bundle): path.read_bytes() for path in bundle.rglob("*") if path.is_file()
    }
    canonical = bundle.with_name(str(_EXPERIMENT_ID))

    def fail(_root: Path, _study_id: UUID) -> None:
        raise RuntimeError("record is incomplete")

    with pytest.raises(RuntimeError, match="record is incomplete"):
        close_bundle(tmp_path, ExperimentKind.FEATURE_ABLATION, _EXPERIMENT_ID, "study_id", fail)

    assert not canonical.exists()
    assert not (bundle / "manifest.json").exists()
    assert {
        path.relative_to(bundle): path.read_bytes() for path in bundle.rglob("*") if path.is_file()
    } == inputs

    verified: list[UUID] = []

    close_bundle(
        tmp_path,
        ExperimentKind.FEATURE_ABLATION,
        _EXPERIMENT_ID,
        "study_id",
        lambda _root, study_id: verified.append(study_id),
    )

    assert verified == [_STUDY_ID]
    assert capsys.readouterr().out.strip() == str(_EXPERIMENT_ID)
    assert load_experiment_manifest(tmp_path, ExperimentKind.FEATURE_ABLATION, _EXPERIMENT_ID) == {
        "ethereum.lstm.full": _STUDY_ID
    }
    assert load_roster(tmp_path, ExperimentKind.FEATURE_ABLATION, _EXPERIMENT_ID, "study_id") == {
        "ethereum.lstm.full": _STUDY_ID
    }
    assert {path.name for path in canonical.iterdir()} == {"manifest.json"}
    assert not bundle.exists()


def test_publication_failure_preserves_authored_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = open_bundle(tmp_path, ExperimentKind.FEATURE_ABLATION, _EXPERIMENT_ID)
    write_tune_cells(bundle, [("ethereum.lstm.full", _request())])
    campaign = bundle / ".servatus-campaign"
    campaign.mkdir()
    (campaign / "state.json").write_text("retry", encoding="utf-8")

    def fail_publication(_destination: object, _assemble: object) -> None:
        raise RuntimeError("publication failed")

    monkeypatch.setattr(bundle_module, "publish", fail_publication)

    with pytest.raises(RuntimeError, match="publication failed"):
        close_bundle(
            tmp_path,
            ExperimentKind.FEATURE_ABLATION,
            _EXPERIMENT_ID,
            "study_id",
            lambda _root, _study_id: None,
        )

    assert not bundle.with_name(str(_EXPERIMENT_ID)).exists()
    assert (bundle / "cells.tsv").is_file()
    assert (bundle / "requests").is_dir()
    assert (campaign / "state.json").read_text() == "retry"
