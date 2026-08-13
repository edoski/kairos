from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from servatus import Campaign, TaskConflict

import experiments.campaign as campaign_module
from experiments.campaign import append_experiment, author_experiment, close_experiment
from kairos.config import (
    EvaluateRequest,
    ExperimentSemantics,
    FitMethod,
    LstmDefinition,
    Method,
    SelectedStudySource,
    TrainRequest,
    TuneRequest,
)
from kairos.experiments import (
    ExperimentKind,
    experiment_campaign_directory,
    experiment_directory,
    load_experiment_manifest,
)
from kairos.study import RetainedResult, Study
from kairos.workers import ExecutionTask, execution_envelope
from tests.experiments.helpers import publish_test_study
from tests.helpers import window

_EXPERIMENT_ID = UUID("10000000-0000-4000-8000-000000000001")


def _evaluate(index: int) -> EvaluateRequest:
    return EvaluateRequest(
        evaluation_id=UUID(f"20000000-0000-4000-8000-{index:012d}"),
        artifact_id=UUID(f"30000000-0000-4000-8000-{index:012d}"),
        corpus_id=UUID("40000000-0000-4000-8000-000000000001"),
        testing_window=window(300),
    )


def _train() -> TrainRequest:
    experiment = ExperimentSemantics(
        training_window=window(100),
        validation_window=window(200),
        context_blocks=1,
        horizon_blocks=2,
        ordered_features=("log_base_fee_per_gas",),
    )
    return TrainRequest(
        artifact_id=UUID("50000000-0000-4000-8000-000000000001"),
        source=SelectedStudySource(
            corpus_id=UUID("40000000-0000-4000-8000-000000000001"),
            study_id=UUID("60000000-0000-4000-8000-000000000001"),
            study_result_index=0,
            experiment=experiment,
        ),
    )


def _tune() -> TuneRequest:
    fit = FitMethod(
        learning_rate=0.001,
        weight_decay=0.0,
        accumulation=1,
        gradient_clip_norm=1.0,
        seed=1,
        max_epochs=1,
        validate_every_completed_epoch=1,
        patience=0,
        min_delta=0.0,
    )
    return TuneRequest(
        study_id=UUID("60000000-0000-4000-8000-000000000001"),
        corpus_id=UUID("40000000-0000-4000-8000-000000000001"),
        experiment=_train().source.experiment,
        methods=tuple(
            Method(
                model=LstmDefinition(
                    family="lstm", hidden=hidden, layers=1, head_hidden=1, dropout=0.0
                ),
                fit=fit,
            )
            for hidden in (1, 2)
        ),
    )


def test_fixed_authoring_seals_exact_task_order_and_tune_fanout(tmp_path: Path) -> None:
    evaluate = (_evaluate(1), _evaluate(2))
    fixed = author_experiment(
        tmp_path,
        ExperimentKind.HELD_OUT,
        _EXPERIMENT_ID,
        [("first", evaluate[0]), ("second", evaluate[1])],
    )

    assert [execution_envelope(task).cell for task in fixed.tasks] == ["first", "second"]
    with pytest.raises(TaskConflict, match="sealed"):
        Campaign.open(
            experiment_campaign_directory(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID),
            (*fixed.tasks, ExecutionTask(request=_evaluate(3), cell="third").task()),
        )

    tune_id = UUID("10000000-0000-4000-8000-000000000002")
    tune = author_experiment(
        tmp_path, ExperimentKind.HPO, tune_id, [("ethereum.lstm", _tune())], seal=False
    )
    assert [execution_envelope(task).method_index for task in tune.tasks] == [0, 1]
    assert {execution_envelope(task).request.study_id for task in tune.tasks} == {_tune().study_id}


def test_append_preserves_exact_prefix_and_rejects_duplicate_cell(tmp_path: Path) -> None:
    first = author_experiment(
        tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, [("first", _evaluate(1))], seal=False
    )
    prefix = first.tasks

    campaign = append_experiment(
        tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, [("second", _evaluate(2))]
    )

    assert campaign.tasks[:1] == prefix
    assert [execution_envelope(task).cell for task in campaign.tasks] == ["first", "second"]
    with pytest.raises(ValueError, match="new and unique"):
        append_experiment(
            tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, [("second", _evaluate(3))]
        )


def test_close_seals_and_validates_one_post_seal_roster_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    author_experiment(
        tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, [("first", _evaluate(1))], seal=False
    )
    path = experiment_campaign_directory(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID)
    real_load = Campaign.load

    def load_with_concurrent_suffix(campaign_path: Path) -> Campaign:
        campaign = real_load(campaign_path)
        seal = campaign.seal

        def append_then_seal() -> None:
            prefix = campaign.tasks
            Campaign.open(
                campaign_path, (*prefix, ExecutionTask(request=_evaluate(2), cell="second").task())
            )
            seal()

        monkeypatch.setattr(campaign, "seal", append_then_seal)
        return campaign

    monkeypatch.setattr(
        campaign_module, "Campaign", SimpleNamespace(load=load_with_concurrent_suffix)
    )

    with pytest.raises(ValueError, match="roster does not match expected cells"):
        close_experiment(
            tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, expected_cells=("first",)
        )

    sealed = real_load(path)
    assert [execution_envelope(task).cell for task in sealed.tasks] == ["first", "second"]
    with pytest.raises(TaskConflict, match="sealed"):
        Campaign.open(
            path, (*sealed.tasks, ExecutionTask(request=_evaluate(3), cell="third").task())
        )


def test_result_only_close_publishes_exact_manifest_without_scheduler(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = _evaluate(1)
    campaign = author_experiment(
        tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, [("ethereum.lstm.K5", request)]
    )
    state_path = experiment_campaign_directory(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID)
    before = state_path.joinpath("campaign.json").read_bytes()
    observed: list[bool] = []

    class View:
        results_ready = True

    def inspect(_probe: object, *, scheduler: bool = True) -> View:
        observed.append(scheduler)
        return View()

    monkeypatch.setattr(campaign, "inspect", inspect)
    monkeypatch.setattr(campaign_module.Campaign, "load", lambda _path: campaign)

    cells = close_experiment(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID)

    assert observed == [False]
    assert cells == {"ethereum.lstm.K5": request.evaluation_id}
    assert load_experiment_manifest(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID) == cells
    canonical = experiment_directory(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID)
    assert {path.name for path in canonical.iterdir()} == {"manifest.json"}
    assert (canonical / "manifest.json").read_bytes() == (
        b'{"ethereum.lstm.K5":"20000000-0000-4000-8000-000000000001"}'
    )
    assert state_path.joinpath("campaign.json").read_bytes() == before


def test_publication_failure_preserves_campaign_and_component_objects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = _evaluate(1)
    campaign = author_experiment(
        tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID, [("ethereum.lstm.K5", request)]
    )
    state_path = experiment_campaign_directory(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID)
    before = state_path.joinpath("campaign.json").read_bytes()
    component = tmp_path / "evaluations" / str(request.evaluation_id)
    component.mkdir(parents=True)
    (component / "evidence").write_bytes(b"complete")
    view = type("View", (), {"results_ready": True})()
    monkeypatch.setattr(campaign, "inspect", lambda *_args, **_kwargs: view)
    monkeypatch.setattr(campaign_module.Campaign, "load", lambda _path: campaign)
    monkeypatch.setattr(
        campaign_module,
        "publish",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("publication failed")),
    )

    with pytest.raises(RuntimeError, match="publication failed"):
        close_experiment(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID)

    assert state_path.joinpath("campaign.json").read_bytes() == before
    assert (component / "evidence").read_bytes() == b"complete"
    assert not experiment_directory(tmp_path, ExperimentKind.HELD_OUT, _EXPERIMENT_ID).exists()


def test_experiment_kind_rejects_the_wrong_typed_request(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="k_study.*TrainRequest"):
        author_experiment(
            tmp_path, ExperimentKind.K_STUDY, _EXPERIMENT_ID, [("wrong", _evaluate(1))]
        )
    campaign = author_experiment(
        tmp_path,
        ExperimentKind.COMPARATOR_STUDY,
        _EXPERIMENT_ID,
        [("ethereum.transformer.K5", _train())],
    )
    assert execution_envelope(campaign.tasks[0]).request == _train()


def test_tune_close_validates_objective_and_association(tmp_path: Path) -> None:
    request = _tune()
    author_experiment(tmp_path, ExperimentKind.HPO, _EXPERIMENT_ID, [("ethereum.lstm", request)])
    study = Study(
        request=request,
        trials=tuple(
            RetainedResult(objective=float(index), selected_epoch=1, completed_epochs=1)
            for index in range(len(request.methods))
        ),
    )
    publish_test_study(tmp_path, study)

    assert close_experiment(tmp_path, ExperimentKind.HPO, _EXPERIMENT_ID) == {
        "ethereum.lstm": request.study_id
    }


def test_tune_close_rejects_objective_mismatched_with_observations(tmp_path: Path) -> None:
    request = _tune()
    author_experiment(tmp_path, ExperimentKind.HPO, _EXPERIMENT_ID, [("ethereum.lstm", request)])
    study = Study(
        request=request,
        trials=tuple(
            RetainedResult(objective=float(index), selected_epoch=1, completed_epochs=1)
            for index in range(len(request.methods))
        ),
    )
    publish_test_study(tmp_path, study)
    study_path = tmp_path / "studies" / str(request.study_id) / "study.json"
    study_path.write_text(
        study.model_copy(
            update={
                "trials": (study.trials[0].model_copy(update={"objective": 0.5}), study.trials[1])
            }
        ).model_dump_json(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="objective must equal validation observations"):
        close_experiment(tmp_path, ExperimentKind.HPO, _EXPERIMENT_ID)
