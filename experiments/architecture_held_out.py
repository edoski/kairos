"""Author and reduce the matched K=5 held-out architecture comparison."""

from __future__ import annotations

from itertools import product
from uuid import UUID

from campaign import StorageRoot, author_experiment, close_experiment, print_metrics, run

from kairos.config import BlockWindow, EvaluateRequest, SelectedStudySource, TrainRequest
from kairos.evaluation import load_evaluation, reduce_evaluation
from kairos.experiments import ExperimentKind, load_experiment_manifest
from kairos.study import load_study

_CHAINS = ("ethereum", "polygon", "avalanche")
_FAMILIES = ("lstm", "transformer", "transformer_lstm")
_COMPARATORS = ("transformer", "transformer_lstm")
_POLYGON_TRAINING = BlockWindow(first_parent_block=87_218_603, last_parent_block=88_724_108)
_POLYGON_VALIDATION = BlockWindow(first_parent_block=88_724_309, last_parent_block=89_127_308)
_ARTIFACT_CELLS = tuple(f"polygon.{family}.K5" for family in _COMPARATORS)
_EVALUATION_CELLS = tuple(f"{chain}.{family}.K5" for chain, family in product(_CHAINS, _FAMILIES))


def prepare_polygon_artifacts(
    storage_root: StorageRoot, hpo_experiment_id: UUID, experiment_id: UUID
) -> None:
    hpo = load_experiment_manifest(storage_root, ExperimentKind.HPO, hpo_experiment_id)
    cells = []
    for family in _COMPARATORS:
        source_cell = f"polygon.{family}"
        study = load_study(storage_root, hpo[source_cell])
        selected_index, _ = study.best_result()
        experiment = study.request.experiment
        if experiment.horizon_blocks != 5:
            raise ValueError(f"{source_cell} Study is not K=5")
        cells.append(
            (
                f"{source_cell}.K5",
                TrainRequest(
                    source=SelectedStudySource(
                        corpus_id=study.request.corpus_id,
                        study_id=study.request.study_id,
                        study_result_index=selected_index,
                        experiment=experiment.model_copy(
                            update={
                                "training_window": _POLYGON_TRAINING,
                                "validation_window": _POLYGON_VALIDATION,
                            }
                        ),
                    )
                ),
            )
        )
    author_experiment(storage_root, ExperimentKind.COMPARATOR_STUDY, experiment_id, cells)
    print(experiment_id)


def prepare_evaluations(
    storage_root: StorageRoot,
    stage5_experiment_id: UUID,
    comparator_experiment_id: UUID,
    polygon_comparator_experiment_id: UUID,
    experiment_id: UUID,
) -> None:
    stage5 = load_experiment_manifest(storage_root, ExperimentKind.HELD_OUT, stage5_experiment_id)
    comparators = load_experiment_manifest(
        storage_root, ExperimentKind.COMPARATOR_STUDY, comparator_experiment_id
    )
    polygon = load_experiment_manifest(
        storage_root, ExperimentKind.COMPARATOR_STUDY, polygon_comparator_experiment_id
    )
    cells = []
    for chain, family in product(_CHAINS, _FAMILIES):
        template = load_evaluation(storage_root, stage5[f"{chain}.lstm.K5"])
        if family == "lstm":
            request = template
        else:
            artifacts = polygon if chain == "polygon" else comparators
            request = EvaluateRequest(
                artifact_id=artifacts[f"{chain}.{family}.K5"],
                corpus_id=template.corpus_id,
                testing_window=template.testing_window,
            )
        cells.append((f"{chain}.{family}.K5", request))
    author_experiment(storage_root, ExperimentKind.HELD_OUT, experiment_id, cells)
    print(experiment_id)


def close_polygon_artifacts(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(
        storage_root, ExperimentKind.COMPARATOR_STUDY, experiment_id, expected_cells=_ARTIFACT_CELLS
    )
    print(experiment_id)


def close_evaluations(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(
        storage_root, ExperimentKind.HELD_OUT, experiment_id, expected_cells=_EVALUATION_CELLS
    )
    print(experiment_id)


def report_evaluations(storage_root: StorageRoot, experiment_id: UUID) -> None:
    print_metrics(storage_root, ExperimentKind.HELD_OUT, experiment_id, reduce_evaluation)


if __name__ == "__main__":
    run(
        prepare_polygon_artifacts,
        prepare_evaluations,
        close_polygon_artifacts,
        close_evaluations,
        report_evaluations,
    )
