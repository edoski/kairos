from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType
from uuid import UUID

import pytest

from kairos.config import FitMethod, Method, TransformerLstmDefinition, TuneRequest
from kairos.experiments import ExperimentKind, ExperimentManifest, experiment_manifest_path
from tests.experiments.helpers import publish_generated_studies
from tests.helpers import experiment_envelopes, run_script

_ROOT = Path(__file__).parents[2]
_FEATURE_SCRIPT = _ROOT / "experiments" / "feature_ablation.py"
_C_SCRIPT = _ROOT / "experiments" / "c_study.py"
_HPO_SCRIPT = _ROOT / "experiments" / "hpo.py"
_CHAINS = ("ethereum", "polygon", "avalanche")
_FAMILIES = ("lstm", "transformer", "transformer_lstm")
_CONTEXTS = (1, 2, 3, 4, 5, 10, 15, 20, 25, 50, 100, 200, 400)


def _load_hpo(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.syspath_prepend(str(_ROOT / "experiments"))
    spec = importlib.util.spec_from_file_location("experiment_hpo_owner", _HPO_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_methods_derive_search_from_the_selected_method(monkeypatch: pytest.MonkeyPatch) -> None:
    hpo = _load_hpo(monkeypatch)
    selected = Method(
        model=TransformerLstmDefinition(
            family="transformer_lstm",
            model_width=90,
            attention_heads=5,
            transformer_layers=7,
            feedforward_width=270,
            lstm_hidden=73,
            lstm_layers=3,
            head_hidden=41,
            dropout=0.17,
        ),
        fit=FitMethod(
            learning_rate=0.0023,
            weight_decay=0.0041,
            accumulation=3,
            gradient_clip_norm=0.75,
            seed=424_242,
            max_epochs=17,
            validate_every_completed_epoch=3,
            patience=4,
            min_delta=0.007,
        ),
    )

    methods = hpo._methods(selected)

    assert len(methods) == 9
    assert [method.model for method in methods[:3]] == [
        selected.model.model_copy(update={"dropout": dropout}) for dropout in (0.2, 0.1, 0.3)
    ]
    dimensions = (
        "model_width",
        "attention_heads",
        "transformer_layers",
        "feedforward_width",
        "head_hidden",
    )
    assert [tuple(getattr(method.model, name) for name in dimensions) for method in methods] == [
        (90, 5, 7, 270, 41),
        (90, 5, 7, 270, 41),
        (90, 5, 7, 270, 41),
        (192, 4, 3, 384, 192),
        (192, 4, 3, 384, 192),
        (192, 4, 3, 384, 192),
        (384, 8, 4, 768, 256),
        (384, 8, 4, 768, 256),
        (384, 8, 4, 768, 256),
    ]
    assert [(method.model.lstm_hidden, method.model.lstm_layers) for method in methods] == [
        (73, 3),
        (73, 3),
        (73, 3),
        (192, 1),
        (192, 1),
        (192, 1),
        (384, 1),
        (384, 1),
        (384, 1),
    ]
    nonsearched = (
        "accumulation",
        "gradient_clip_norm",
        "seed",
        "max_epochs",
        "validate_every_completed_epoch",
        "patience",
        "min_delta",
    )
    assert {tuple(getattr(method.fit, field) for field in nonsearched) for method in methods} == {
        tuple(getattr(selected.fit, field) for field in nonsearched)
    }
    assert [
        (method.model.dropout, method.fit.learning_rate, method.fit.weight_decay)
        for method in methods
    ] == [
        (0.2, 0.0003, 0.0001),
        (0.1, 0.0001, 0.0),
        (0.3, 0.001, 0.001),
        (0.2, 0.0001, 0.001),
        (0.1, 0.001, 0.0001),
        (0.3, 0.0003, 0.0),
        (0.2, 0.001, 0.0),
        (0.1, 0.0003, 0.001),
        (0.3, 0.0001, 0.0001),
    ]


def test_downstream_author_requires_the_canonical_manifest(tmp_path: Path) -> None:
    feature_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())

    with pytest.raises(subprocess.CalledProcessError) as absent:
        run_script(_C_SCRIPT, "prepare", tmp_path, feature_id)

    assert "/manifest.json" in absent.value.stderr


def test_context_and_hpo_pipeline_preserves_rosters_selection_and_l9(tmp_path: Path) -> None:
    feature_experiment_id = UUID(run_script(_FEATURE_SCRIPT, "prepare", tmp_path).stdout.strip())
    feature_tasks = experiment_envelopes(
        tmp_path, ExperimentKind.FEATURE_ABLATION, feature_experiment_id
    )
    feature_objectives = {
        f"{chain}.{family}.without_hour": objective
        for chain, objective in (("ethereum", 0.26), ("polygon", 1.0), ("avalanche", 1.0))
        for family in _FAMILIES
    }
    publish_generated_studies(
        tmp_path, feature_tasks, default_objective=2.0, objectives=feature_objectives
    )
    feature_winners = {
        envelope.cell.removesuffix(".without_hour"): envelope.request.study_id
        for envelope in feature_tasks
        if envelope.cell is not None
        and envelope.cell.endswith(".without_hour")
        and isinstance(envelope.request, TuneRequest)
    }
    run_script(_FEATURE_SCRIPT, "close", tmp_path, feature_experiment_id)

    c_result = run_script(_C_SCRIPT, "prepare", tmp_path, feature_experiment_id)
    c_experiment_id = UUID(c_result.stdout.strip())
    assert c_result.stderr.splitlines() == [
        "ethereum\twithout_hour\t0.26",
        "polygon\twithout_hour\t1",
        "avalanche\twithout_hour\t1",
    ]
    c_tasks = experiment_envelopes(tmp_path, ExperimentKind.C_STUDY, c_experiment_id)
    c_requests = [envelope.request for envelope in c_tasks]
    assert all(isinstance(request, TuneRequest) for request in c_requests)

    assert len(c_tasks) == 117
    assert [envelope.cell for envelope in c_tasks[:13]] == [
        f"ethereum.lstm.C{context}" for context in _CONTEXTS
    ]
    assert c_tasks[-1].cell == "avalanche.transformer_lstm.C400"
    assert [request.experiment.context_blocks for request in c_requests[:13]] == list(_CONTEXTS)
    assert {
        envelope.cell.removesuffix(".C25"): envelope.request.study_id
        for envelope in c_tasks
        if envelope.cell is not None
        and envelope.cell.endswith(".C25")
        and isinstance(envelope.request, TuneRequest)
    } == feature_winners
    assert len({request.study_id for request in c_requests} - set(feature_winners.values())) == 108

    objectives = {
        f"{chain}.{family}.{context}": objective
        for chain, context, objective in (
            ("ethereum", "C50", 0.25),
            ("polygon", "C50", 0.524),
            ("polygon", "C100", 0.5),
            ("avalanche", "C200", 0.75),
        )
        for family in _FAMILIES
    }
    objectives.update(
        {
            "ethereum.lstm.C50": 0.1,
            "ethereum.transformer.C50": 0.25,
            "ethereum.transformer_lstm.C50": 0.4,
        }
    )
    publish_generated_studies(tmp_path, c_tasks, default_objective=1.0, objectives=objectives)
    run_script(_C_SCRIPT, "close", tmp_path, c_experiment_id)

    hpo_result = run_script(
        _HPO_SCRIPT,
        "prepare",
        tmp_path,
        c_experiment_id,
        "--chain",
        "ethereum",
        "--chain",
        "polygon",
    )
    hpo_experiment_id = UUID(hpo_result.stdout.strip())
    assert hpo_result.stderr.splitlines() == [
        "chain\tselected_context\tselected_mean\tbest_context\tbest_mean\tthreshold",
        "ethereum\t25\t0.26\t50\t0.25\t0.2625",
        "polygon\t50\t0.524\t100\t0.5\t0.525",
    ]
    assert len(experiment_envelopes(tmp_path, ExperimentKind.HPO, hpo_experiment_id)) == 54

    with pytest.raises(subprocess.CalledProcessError, match="returned non-zero") as incomplete:
        run_script(_HPO_SCRIPT, "select", tmp_path, hpo_experiment_id)
    assert "HPO roster is incomplete" in incomplete.value.stderr

    extension = run_script(
        _HPO_SCRIPT, "extend", tmp_path, c_experiment_id, hpo_experiment_id, "--chain", "avalanche"
    )
    assert extension.stderr.splitlines() == [
        "chain\tselected_context\tselected_mean\tbest_context\tbest_mean\tthreshold",
        "avalanche\t200\t0.75\t200\t0.75\t0.7875",
    ]
    with pytest.raises(subprocess.CalledProcessError) as duplicate:
        run_script(
            _HPO_SCRIPT,
            "extend",
            tmp_path,
            c_experiment_id,
            hpo_experiment_id,
            "--chain",
            "avalanche",
        )
    assert "experiment cells must be new and unique" in duplicate.value.stderr

    tasks = experiment_envelopes(tmp_path, ExperimentKind.HPO, hpo_experiment_id)
    requests = {
        envelope.cell: envelope.request
        for envelope in tasks
        if isinstance(envelope.request, TuneRequest)
    }
    assert len(tasks) == 81
    assert len(requests) == 9
    assert {
        chain: {
            request.experiment.context_blocks
            for cell, request in requests.items()
            if cell.startswith(f"{chain}.")
        }
        for chain in _CHAINS
    } == {"ethereum": {25}, "polygon": {50}, "avalanche": {200}}
    assert {len(request.methods) for request in requests.values()} == {9}

    publish_generated_studies(tmp_path, tasks, default_objective=0.5)
    selected = run_script(_HPO_SCRIPT, "select", tmp_path, hpo_experiment_id)
    expected_cells = [f"{chain}.{family}" for chain in _CHAINS for family in _FAMILIES]
    assert [line.split("\t")[0] for line in selected.stdout.splitlines()] == expected_cells
    manifest = ExperimentManifest.model_validate_json(
        experiment_manifest_path(tmp_path, ExperimentKind.HPO, hpo_experiment_id).read_bytes()
    )
    assert list(manifest.root) == expected_cells

    report = run_script(_C_SCRIPT, "report", tmp_path, c_experiment_id)
    assert len(report.stdout.splitlines()) == 118
    assert report.stderr.splitlines()[-3:] == [
        "ethereum\t25\t0.26\t50\t0.25\t0.2625",
        "polygon\t50\t0.524\t100\t0.5\t0.525",
        "avalanche\t200\t0.75\t200\t0.75\t0.7875",
    ]
