"""Author and reduce the retrospective held-out horizon refinement."""

from __future__ import annotations

from uuid import UUID

from campaign import (
    StorageRoot,
    author_experiment,
    close_experiment,
    print_metrics,
    print_study_metrics,
    run,
)

from kairos.config import (
    BlockWindow,
    EvaluateRequest,
    SelectedStudySource,
    TrainRequest,
    TuneRequest,
)
from kairos.evaluation import reduce_evaluation
from kairos.experiments import ExperimentKind, load_experiment_manifest
from kairos.study import load_study

_CELLS = (("ethereum", 15), ("ethereum", 20), ("avalanche", 75))
_LABELS = tuple(f"{chain}.lstm.K{horizon}" for chain, horizon in _CELLS)
_TESTING_WINDOWS = {
    "ethereum": BlockWindow(first_parent_block=25_268_964, last_parent_block=25_590_029),
    "avalanche": BlockWindow(first_parent_block=81_367_529, last_parent_block=90_987_193),
}


def prepare_hpo(
    storage_root: StorageRoot, source_hpo_experiment_id: UUID, experiment_id: UUID
) -> None:
    source = load_experiment_manifest(storage_root, ExperimentKind.HPO, source_hpo_experiment_id)
    studies = {
        chain: load_study(storage_root, source[f"{chain}.lstm"])
        for chain in {chain for chain, _ in _CELLS}
    }
    cells = []
    for chain, horizon in _CELLS:
        study = studies[chain]
        cells.append(
            (
                f"{chain}.lstm.K{horizon}",
                TuneRequest(
                    corpus_id=study.request.corpus_id,
                    experiment=study.request.experiment.model_copy(
                        update={"horizon_blocks": horizon}
                    ),
                    methods=study.request.methods,
                ),
            )
        )
    author_experiment(storage_root, ExperimentKind.HPO, experiment_id, cells)
    print(experiment_id)


def prepare_artifacts(
    storage_root: StorageRoot, refinement_hpo_experiment_id: UUID, experiment_id: UUID
) -> None:
    manifest = load_experiment_manifest(
        storage_root, ExperimentKind.HPO, refinement_hpo_experiment_id
    )
    if tuple(manifest) != _LABELS:
        raise ValueError("refinement HPO roster does not match the frozen cells")
    cells = []
    for cell, study_id in manifest.items():
        study = load_study(storage_root, study_id)
        selected_index, _ = study.best_result()
        cells.append(
            (
                cell,
                TrainRequest(
                    source=SelectedStudySource(
                        corpus_id=study.request.corpus_id,
                        study_id=study_id,
                        study_result_index=selected_index,
                        experiment=study.request.experiment,
                    )
                ),
            )
        )
    author_experiment(storage_root, ExperimentKind.K_STUDY, experiment_id, cells)
    print(experiment_id)


def prepare_evaluations(
    storage_root: StorageRoot,
    refinement_hpo_experiment_id: UUID,
    refinement_k_experiment_id: UUID,
    experiment_id: UUID,
) -> None:
    studies = load_experiment_manifest(
        storage_root, ExperimentKind.HPO, refinement_hpo_experiment_id
    )
    artifacts = load_experiment_manifest(
        storage_root, ExperimentKind.K_STUDY, refinement_k_experiment_id
    )
    if tuple(studies) != _LABELS or tuple(artifacts) != _LABELS:
        raise ValueError("refinement manifests do not match the frozen cells")
    cells = []
    for cell, artifact_id in artifacts.items():
        chain = cell.split(".", maxsplit=1)[0]
        study = load_study(storage_root, studies[cell])
        cells.append(
            (
                cell,
                EvaluateRequest(
                    artifact_id=artifact_id,
                    corpus_id=study.request.corpus_id,
                    testing_window=_TESTING_WINDOWS[chain],
                ),
            )
        )
    author_experiment(storage_root, ExperimentKind.HELD_OUT, experiment_id, cells)
    print(experiment_id)


def close_hpo(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(storage_root, ExperimentKind.HPO, experiment_id, expected_cells=_LABELS)
    print(experiment_id)


def close_artifacts(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(storage_root, ExperimentKind.K_STUDY, experiment_id, expected_cells=_LABELS)
    print(experiment_id)


def close_evaluations(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(storage_root, ExperimentKind.HELD_OUT, experiment_id, expected_cells=_LABELS)
    print(experiment_id)


def report_hpo(storage_root: StorageRoot, experiment_id: UUID) -> None:
    print_study_metrics(storage_root, ExperimentKind.HPO, experiment_id)


def report_evaluations(storage_root: StorageRoot, experiment_id: UUID) -> None:
    print_metrics(storage_root, ExperimentKind.HELD_OUT, experiment_id, reduce_evaluation)


if __name__ == "__main__":
    run(
        prepare_hpo,
        prepare_artifacts,
        prepare_evaluations,
        close_hpo,
        close_artifacts,
        close_evaluations,
        report_hpo,
        report_evaluations,
    )
