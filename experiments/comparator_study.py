"""Author and close the matched K=5 operational comparator study."""

from __future__ import annotations

from itertools import product
from uuid import UUID, uuid4

from campaign import StorageRoot, author_experiment, close_experiment, run

from kairos.config import SelectedStudySource, TrainRequest
from kairos.experiments import ExperimentKind, load_experiment_manifest
from kairos.study import load_study

_KIND = ExperimentKind.COMPARATOR_STUDY
_CHAINS = ("ethereum", "polygon", "avalanche")
_FAMILIES = ("transformer", "transformer_lstm")
_CELLS = tuple(f"{chain}.{family}.K5" for chain, family in product(_CHAINS, _FAMILIES))


def prepare(storage_root: StorageRoot, hpo_experiment_id: UUID) -> None:
    experiment_id = uuid4()
    manifest = load_experiment_manifest(storage_root, ExperimentKind.HPO, hpo_experiment_id)
    cells = []
    for chain, family in product(_CHAINS, _FAMILIES):
        source_cell = f"{chain}.{family}"
        if source_cell not in manifest:
            raise ValueError(f"HPO manifest is missing {source_cell}")
        study_id = manifest[source_cell]
        study = load_study(storage_root, study_id)
        selected_index, _ = study.best_result()
        if study.request.experiment.horizon_blocks != 5:
            raise ValueError(f"{source_cell} Study is not K=5")
        request = TrainRequest(
            source=SelectedStudySource(
                corpus_id=study.request.corpus_id,
                study_id=study_id,
                study_result_index=selected_index,
                experiment=study.request.experiment,
            )
        )
        cells.append((f"{source_cell}.K5", request))

    author_experiment(storage_root, _KIND, experiment_id, cells)
    print(experiment_id)


def close(storage_root: StorageRoot, experiment_id: UUID) -> None:
    close_experiment(storage_root, _KIND, experiment_id, expected_cells=_CELLS)
    print(experiment_id)


if __name__ == "__main__":
    run(prepare, close)
