"""Author and close the frozen horizon-sensitivity experiment."""

from __future__ import annotations

from uuid import UUID, uuid4

from campaign import StorageRoot, author_experiment, close_experiment, run

from kairos.config import SelectedStudySource, TrainRequest
from kairos.experiments import ExperimentKind, load_experiment_manifest
from kairos.study import load_study

_KIND = ExperimentKind.K_STUDY
_LSTM_CELLS = tuple(f"{chain}.lstm" for chain in ("ethereum", "polygon", "avalanche"))
_HORIZONS = (2, 3, 4, 5, 10, 25, 50, 100, 200)


def prepare(storage_root: StorageRoot, hpo_experiment_id: UUID) -> None:
    experiment_id = uuid4()
    manifest = load_experiment_manifest(storage_root, ExperimentKind.HPO, hpo_experiment_id)
    if not set(_LSTM_CELLS) <= manifest.keys():
        raise ValueError("HPO manifest is missing selected LSTM Studies")
    cells: list[tuple[str, TrainRequest]] = []
    for cell in _LSTM_CELLS:
        study_id = manifest[cell]
        study = load_study(storage_root, study_id)
        selected_index, _ = study.best_result()
        for horizon in _HORIZONS:
            request = TrainRequest(
                source=SelectedStudySource(
                    corpus_id=study.request.corpus_id,
                    study_id=study_id,
                    study_result_index=selected_index,
                    experiment=study.request.experiment.model_copy(
                        update={"horizon_blocks": horizon}
                    ),
                )
            )
            cells.append((f"{cell}.K{horizon}", request))

    author_experiment(storage_root, _KIND, experiment_id, cells)

    print(experiment_id)


def close(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(storage_root, _KIND, experiment_id)
    print(experiment_id)


if __name__ == "__main__":
    run(prepare, close)
