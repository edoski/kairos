"""Author and reduce the Chicago Polygon model and temporal-alignment diagnostic."""

from __future__ import annotations

from uuid import UUID

from campaign import StorageRoot, author_experiment, close_experiment, print_metrics, run

from kairos.config import BlockWindow, EvaluateRequest, SelectedStudySource, TrainRequest
from kairos.evaluation import load_evaluation, reduce_evaluation
from kairos.experiments import ExperimentKind, load_experiment_manifest
from kairos.study import Study, load_study

_HORIZONS = (2, 3, 4, 5, 10, 25, 50, 100, 200)
_LABELS = tuple(f"polygon.lstm.K{horizon}" for horizon in _HORIZONS)
_TRAINING = BlockWindow(first_parent_block=87_218_603, last_parent_block=88_724_108)
_VALIDATION = BlockWindow(first_parent_block=88_724_309, last_parent_block=89_127_308)
_TESTING = BlockWindow(first_parent_block=89_127_509, last_parent_block=89_530_799)
_ROLLING_LAST_PARENT = {4: 89_530_800, 3: 89_530_801, 2: 89_530_802}


def _source_studies(
    storage_root: StorageRoot, stage3_hpo_experiment_id: UUID, per_k_hpo_experiment_id: UUID
) -> dict[int, Study]:
    stage3 = load_experiment_manifest(storage_root, ExperimentKind.HPO, stage3_hpo_experiment_id)
    per_k = load_experiment_manifest(storage_root, ExperimentKind.HPO, per_k_hpo_experiment_id)
    return {
        horizon: load_study(
            storage_root,
            stage3["polygon.lstm"] if horizon == 5 else per_k[f"polygon.lstm.K{horizon}"],
        )
        for horizon in _HORIZONS
    }


def prepare_artifacts(
    storage_root: StorageRoot,
    stage3_hpo_experiment_id: UUID,
    per_k_hpo_experiment_id: UUID,
    experiment_id: UUID,
) -> None:
    studies = _source_studies(storage_root, stage3_hpo_experiment_id, per_k_hpo_experiment_id)
    cells = []
    for horizon, cell in zip(_HORIZONS, _LABELS, strict=True):
        study = studies[horizon]
        selected_index, _ = study.best_result()
        experiment = study.request.experiment
        if experiment.horizon_blocks != horizon:
            raise ValueError(f"{cell} source Study has the wrong horizon")
        cells.append(
            (
                cell,
                TrainRequest(
                    source=SelectedStudySource(
                        corpus_id=study.request.corpus_id,
                        study_id=study.request.study_id,
                        study_result_index=selected_index,
                        experiment=experiment.model_copy(
                            update={"training_window": _TRAINING, "validation_window": _VALIDATION}
                        ),
                    )
                ),
            )
        )
    author_experiment(storage_root, ExperimentKind.K_STUDY, experiment_id, cells)
    print(experiment_id)


def prepare_evaluations(
    storage_root: StorageRoot,
    stage3_hpo_experiment_id: UUID,
    per_k_hpo_experiment_id: UUID,
    stale_k_experiment_id: UUID,
    chicago_k_experiment_id: UUID,
    experiment_id: UUID,
) -> None:
    studies = _source_studies(storage_root, stage3_hpo_experiment_id, per_k_hpo_experiment_id)
    stale = load_experiment_manifest(
        storage_root, ExperimentKind.K_STUDY, stale_k_experiment_id
    )
    chicago = load_experiment_manifest(
        storage_root, ExperimentKind.K_STUDY, chicago_k_experiment_id
    )
    if tuple(chicago) != _LABELS:
        raise ValueError("Chicago artifact roster does not match the frozen horizons")
    cells = []
    for horizon, source_cell in zip(_HORIZONS, _LABELS, strict=True):
        corpus_id = studies[horizon].request.corpus_id
        for cohort, manifest in (("stale_history", stale), ("chicago_training", chicago)):
            cells.append(
                (
                    f"polygon.{cohort}.chicago_tail.lstm.K{horizon}",
                    EvaluateRequest(
                        artifact_id=manifest[source_cell],
                        corpus_id=corpus_id,
                        testing_window=_TESTING,
                    ),
                )
            )
    author_experiment(storage_root, ExperimentKind.HELD_OUT, experiment_id, cells)
    print(experiment_id)


def prepare_rolling_evaluations(
    storage_root: StorageRoot, paired_experiment_id: UUID, experiment_id: UUID
) -> None:
    """Extend only the shorter-horizon support required by the rolling replay."""

    paired = load_experiment_manifest(storage_root, ExperimentKind.HELD_OUT, paired_experiment_id)
    cells = []
    for horizon in (4, 3, 2):
        source = load_evaluation(
            storage_root,
            paired[f"polygon.chicago_training.chicago_tail.lstm.K{horizon}"],
        )
        cells.append(
            (
                f"polygon.lstm.K{horizon}",
                EvaluateRequest(
                    artifact_id=source.artifact_id,
                    corpus_id=source.corpus_id,
                    testing_window=source.testing_window.model_copy(
                        update={"last_parent_block": _ROLLING_LAST_PARENT[horizon]}
                    ),
                ),
            )
        )
    author_experiment(storage_root, ExperimentKind.HELD_OUT, experiment_id, cells)
    print(experiment_id)


def close_artifacts(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(storage_root, ExperimentKind.K_STUDY, experiment_id, expected_cells=_LABELS)
    print(experiment_id)


def close_evaluations(storage_root: StorageRoot, experiment_id: UUID) -> None:
    expected = tuple(
        f"polygon.{cohort}.chicago_tail.lstm.K{horizon}"
        for horizon in _HORIZONS
        for cohort in ("stale_history", "chicago_training")
    )
    close_experiment(storage_root, ExperimentKind.HELD_OUT, experiment_id, expected_cells=expected)
    print(experiment_id)


def report_evaluations(storage_root: StorageRoot, experiment_id: UUID) -> None:
    print_metrics(storage_root, ExperimentKind.HELD_OUT, experiment_id, reduce_evaluation)


if __name__ == "__main__":
    run(
        prepare_artifacts,
        prepare_evaluations,
        prepare_rolling_evaluations,
        close_artifacts,
        close_evaluations,
        report_evaluations,
    )
