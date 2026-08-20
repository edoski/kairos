from __future__ import annotations

import json
import signal
import stat
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import cast
from uuid import UUID

import polars as pl
import pytest
import torch
from torch import nn

import experiments.inference_benchmark as benchmark
from kairos.config import (
    BlockWindow,
    EvaluateRequest,
    ExperimentSemantics,
    FitMethod,
    LstmDefinition,
    Method,
    SelectedStudySource,
    TrainRequest,
)
from kairos.min_block_fee import MinBlockFeeOutput, TargetState
from kairos.modeling import ArtifactAssociation
from kairos.temporal import FeatureState, HistoricalDataset, _HistoricalBacking

_K_STUDY_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
_HELD_OUT_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
_COMPARATOR_ID = UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee")
_CORPUS_ID = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
_STUDY_ID = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd")
_METHOD = Method(
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
)


def _experiment(horizon: int) -> ExperimentSemantics:
    return ExperimentSemantics(
        training_window=BlockWindow(first_parent_block=10, last_parent_block=19),
        validation_window=BlockWindow(first_parent_block=30, last_parent_block=39),
        context_blocks=2,
        horizon_blocks=horizon,
        ordered_features=("log_base_fee_per_gas",),
    )


def _association(horizon: int, artifact_id: UUID) -> ArtifactAssociation:
    return ArtifactAssociation(
        request=TrainRequest(
            artifact_id=artifact_id,
            source=SelectedStudySource(
                corpus_id=_CORPUS_ID,
                study_id=_STUDY_ID,
                study_result_index=0,
                experiment=_experiment(horizon),
            ),
        ),
        feature_state=FeatureState(means=(0.0,), standard_deviations=(1.0,)),
        target_state=TargetState(mean=0.0, standard_deviation=1.0),
        method=_METHOD,
    )


def _request(index: int, horizon: int) -> EvaluateRequest:
    return EvaluateRequest(
        evaluation_id=UUID(f"20000000-0000-4000-8000-{index:012d}"),
        artifact_id=UUID(f"10000000-0000-4000-8000-{index:012d}"),
        corpus_id=_CORPUS_ID,
        testing_window=BlockWindow(
            first_parent_block=100, last_parent_block=100 + benchmark.ROLLING_HORIZONS[0] - horizon
        ),
    )


def _selection(index: int, horizon: int) -> benchmark.Selection:
    request = _request(index, horizon)
    return benchmark.Selection(
        artifact_id=request.artifact_id,
        support_evaluation_id=request.evaluation_id,
        corpus_id=request.corpus_id,
        testing_window=request.testing_window,
    )


class _Dataset:
    def __init__(self, origins: tuple[int, ...]) -> None:
        self.origins = origins
        self.inputs = torch.arange(40, dtype=torch.float32).reshape(20, 2)

    def __len__(self) -> int:
        return len(self.origins)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        return {
            "inputs": self.inputs[index : index + 2],
            "origin_block": torch.tensor(self.origins[index]),
        }


class _Model(nn.Module):
    def __init__(self, horizon: int, events: list[str]) -> None:
        super().__init__()
        self.horizon = horizon
        self.events = events

    def forward(self, inputs: torch.Tensor) -> MinBlockFeeOutput:
        self.events.append(f"model{self.horizon}:{int(inputs[0, 0, 0])}")
        return MinBlockFeeOutput(
            action_logits=torch.zeros(1, self.horizon), minimum_fee_z=torch.zeros(1)
        )


def _cell(events: list[str]) -> benchmark._Cell:
    return benchmark._Cell(
        name="ethereum.lstm",
        horizons={
            horizon: benchmark._Horizon(
                model=_Model(horizon, events),
                dataset=cast(
                    HistoricalDataset,
                    _Dataset(tuple(range(100, 101 + benchmark.ROLLING_HORIZONS[0] - horizon))),
                ),
            )
            for horizon in reversed(benchmark.ROLLING_HORIZONS)
        },
    )


def _energy_cell(events: list[str]) -> benchmark._Cell:
    return benchmark._Cell(
        name="ethereum.lstm",
        horizons={
            horizon: benchmark._Horizon(
                model=_Model(horizon, events),
                dataset=cast(HistoricalDataset, _Dataset((100, 101, 102))),
            )
            for horizon in reversed(benchmark.ROLLING_HORIZONS)
        },
    )


def _resolved() -> dict[str, dict[int, benchmark.Selection]]:
    resolved: dict[str, dict[int, benchmark.Selection]] = {}
    for index, (chain, horizon) in enumerate(
        (chain, horizon)
        for chain in ("ethereum", "polygon", "avalanche")
        for horizon in reversed(benchmark.ROLLING_HORIZONS)
    ):
        resolved.setdefault(f"{chain}.lstm", {})[horizon] = _selection(index, horizon)
    return resolved


def _protocol() -> benchmark.Protocol:
    return benchmark._protocol(
        _K_STUDY_ID, _HELD_OUT_ID, _resolved(), warmup_iterations=2, sweeps=1
    )


def _architecture_resolved() -> dict[str, dict[int, benchmark.Selection]]:
    return {
        f"{chain}.{family}": {5: _selection(index + 100, 5)}
        for index, (chain, family) in enumerate(
            (chain, family)
            for chain in ("avalanche", "ethereum", "polygon")
            for family in ("lstm", "transformer", "transformer_lstm")
        )
    }


def _architecture_protocol() -> benchmark.Protocol:
    return benchmark._architecture_protocol(
        _K_STUDY_ID,
        _HELD_OUT_ID,
        _COMPARATOR_ID,
        _architecture_resolved(),
        warmup_iterations=2,
        sweeps=1,
    )


def test_resolve_joins_canonical_artifacts_and_evaluations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    k_study = {}
    held_out = {}
    source = _resolved()
    for group, selections in source.items():
        for horizon, selection in selections.items():
            label = f"{group}.K{horizon}"
            k_study[label] = selection.artifact_id
            held_out[label] = selection.support_evaluation_id
            request = EvaluateRequest(
                evaluation_id=selection.support_evaluation_id,
                artifact_id=selection.artifact_id,
                corpus_id=selection.corpus_id,
                testing_window=selection.testing_window,
            )
            path = (
                tmp_path / "evaluations" / str(selection.support_evaluation_id) / "evaluation.json"
            )
            path.parent.mkdir(parents=True)
            path.write_text(request.model_dump_json())
    for index, (group, horizon) in enumerate(
        (group, horizon) for group in source for horizon in (10, 25, 50, 100, 200)
    ):
        k_study[f"{group}.K{horizon}"] = UUID(f"30000000-0000-4000-8000-{index:012d}")
        held_out[f"{group}.K{horizon}"] = UUID(f"40000000-0000-4000-8000-{index:012d}")

    monkeypatch.setattr(
        benchmark,
        "load_experiment_manifest",
        lambda root, kind, experiment_id: (
            k_study if kind == benchmark.ExperimentKind.K_STUDY else held_out
        ),
    )
    monkeypatch.setattr(benchmark, "_load_cell", lambda *_args: pytest.fail("model loaded"))

    resolved = benchmark._resolve(tmp_path, _K_STUDY_ID, _HELD_OUT_ID)

    assert resolved == source
    protocol = benchmark._protocol(_K_STUDY_ID, _HELD_OUT_ID, resolved, 2, 10)
    assert len(protocol.roster) == 12
    assert sorted(protocol.roster) == [
        f"{group}.K{horizon}"
        for group in sorted(source)
        for horizon in reversed(benchmark.ROLLING_HORIZONS)
    ]
    missing = held_out.pop("polygon.lstm.K4")
    with pytest.raises(ValueError, match="three complete LSTM rolling groups"):
        benchmark._resolve(tmp_path, _K_STUDY_ID, _HELD_OUT_ID)
    held_out["polygon.lstm.K4"] = missing
    surplus_labels = []
    for index, horizon in enumerate(reversed(benchmark.ROLLING_HORIZONS), start=36):
        selection = _selection(index, horizon)
        label = f"surplus.lstm.K{horizon}"
        surplus_labels.append(label)
        k_study[label] = selection.artifact_id
        held_out[label] = selection.support_evaluation_id
    with pytest.raises(ValueError, match="three complete LSTM rolling groups"):
        benchmark._resolve(tmp_path, _K_STUDY_ID, _HELD_OUT_ID)
    for label in surplus_labels:
        del k_study[label], held_out[label]
    label = "ethereum.lstm.K5"
    k_study[label] = UUID("ffffffff-ffff-4fff-8fff-ffffffffffff")
    with pytest.raises(ValueError, match="does not name"):
        benchmark.run_policy_latency(tmp_path, _K_STUDY_ID, _HELD_OUT_ID, tmp_path / "output", 2, 1)
    assert not (tmp_path / "output").exists()


def test_architecture_resolve_adds_two_matched_k5_comparators_per_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy = _resolved()
    comparators = {
        f"{chain}.{family}.K5": UUID(f"50000000-0000-4000-8000-{index:012d}")
        for index, (chain, family) in enumerate(
            (chain, family)
            for chain in ("avalanche", "ethereum", "polygon")
            for family in ("transformer", "transformer_lstm")
        )
    }
    monkeypatch.setattr(benchmark, "_resolve", lambda *_args: policy)
    monkeypatch.setattr(benchmark, "load_experiment_manifest", lambda *_args: comparators)

    resolved = benchmark._resolve_architecture(tmp_path, _K_STUDY_ID, _HELD_OUT_ID, _COMPARATOR_ID)

    assert len(resolved) == 9
    assert all(set(group) == {5} for group in resolved.values())
    for chain in ("avalanche", "ethereum", "polygon"):
        template = policy[f"{chain}.lstm"][5]
        assert resolved[f"{chain}.lstm"][5] == template
        for family in ("transformer", "transformer_lstm"):
            selection = resolved[f"{chain}.{family}"][5]
            assert selection.artifact_id == comparators[f"{chain}.{family}.K5"]
            assert selection.model_copy(update={"artifact_id": template.artifact_id}) == template

    comparators.pop("polygon.transformer.K5")
    with pytest.raises(ValueError, match="two K5 families"):
        benchmark._resolve_architecture(tmp_path, _K_STUDY_ID, _HELD_OUT_ID, _COMPARATOR_ID)


def test_batch_one_is_a_chronological_view() -> None:
    backing = _HistoricalBacking(
        first_block=100,
        inputs=torch.arange(20, dtype=torch.float32).reshape(10, 2),
        base_fees=torch.arange(100, 110, dtype=torch.int64),
    )
    dataset = HistoricalDataset(
        backing,
        _experiment(2),
        BlockWindow(first_parent_block=102, last_parent_block=104),
        TargetState(mean=0.0, standard_deviation=1.0),
    )
    origin, inputs = benchmark._batch(benchmark._Horizon(nn.Identity(), dataset), 1)
    assert origin == 103
    assert inputs.shape == (1, 2, 2)


def test_cell_load_keeps_four_canonical_models_and_datasets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved = _resolved()["ethereum.lstm"]
    loaded_artifacts: list[UUID] = []
    corpus_loads = 0

    def load_artifact(root: Path, artifact_id: UUID) -> tuple[ArtifactAssociation, nn.Module]:
        del root
        loaded_artifacts.append(artifact_id)
        horizon = next(
            horizon for horizon, request in resolved.items() if request.artifact_id == artifact_id
        )
        return _association(horizon, artifact_id), _Model(horizon, []).eval()

    def load_corpus(root: Path, corpus_id: UUID) -> object:
        nonlocal corpus_loads
        del root, corpus_id
        corpus_loads += 1
        return object()

    monkeypatch.setattr(benchmark, "load_artifact", load_artifact)
    monkeypatch.setattr(benchmark, "load_corpus_blocks", load_corpus)
    monkeypatch.setattr(
        benchmark,
        "prepare_historical_window",
        lambda blocks, experiment, window, **_states: cast(
            HistoricalDataset,
            _Dataset(tuple(range(window.first_parent_block, window.last_parent_block + 1))),
        ),
    )

    cell = benchmark._load_cell(Path("/storage"), "ethereum.lstm", resolved)

    assert loaded_artifacts == [
        resolved[horizon].artifact_id for horizon in reversed(benchmark.ROLLING_HORIZONS)
    ]
    assert corpus_loads == 1
    assert set(cell.horizons) == set(benchmark.ROLLING_HORIZONS)
    assert all(not item.model.training for item in cell.horizons.values())


def test_warmup_is_fixed_and_excluded_from_clocks(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []
    monkeypatch.setattr(
        benchmark.time,
        "perf_counter_ns",
        lambda: pytest.fail("warmup must not read the measurement clock"),
    )
    benchmark._warm(_cell(events), 2)
    assert len(events) == 2 * len(benchmark.ROLLING_HORIZONS)


def test_timing_uses_outer_clocks_same_origins_and_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []
    ticks = iter(range(0, 1_000, 10))

    def clock() -> int:
        events.append("clock")
        return next(ticks)

    original_decode = benchmark.decode_action

    def decode(output: MinBlockFeeOutput) -> torch.Tensor:
        events.append("decode")
        return original_decode(output)

    monkeypatch.setattr(benchmark.time, "perf_counter_ns", clock)
    monkeypatch.setattr(benchmark, "decode_action", decode)
    rows = benchmark._time_cell(_cell(events), 1)

    assert rows.columns == ["cell", "sweep", "pass_order", "workload", "origin_block", "elapsed_ns"]
    assert rows.dtypes == [pl.String, pl.Int64, pl.Int64, pl.String, pl.Int64, pl.Int64]
    expected_calls = (
        sum(1 + benchmark.ROLLING_HORIZONS[0] - horizon for horizon in benchmark.ROLLING_HORIZONS)
        + 1
    )
    assert rows["elapsed_ns"].to_list() == [10] * expected_calls
    assert rows.filter(pl.col("workload") == "cascade")["origin_block"].to_list() == [100]
    assert events[-10:] == [
        "clock",
        "model5:0",
        "decode",
        "model4:0",
        "decode",
        "model3:0",
        "decode",
        "model2:0",
        "decode",
        "clock",
    ]


def test_orders_rotate_deterministically() -> None:
    cells = ("alpha.family", "beta.family", "gamma.family")
    assert benchmark._rotate(cells, 1) == ("beta.family", "gamma.family", "alpha.family")
    first = benchmark._pass_order(1)
    assert tuple(workload.horizons for workload in first) == tuple(
        (horizon,) for horizon in reversed(benchmark.ROLLING_HORIZONS)
    ) + (benchmark.ROLLING_HORIZONS,)
    assert benchmark._pass_order(2) == (*first[1:], first[0])


def test_protocol_match_and_units_resume(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    protocol = _protocol()
    output = tmp_path / "output"
    benchmark._ensure_protocol(output, protocol)
    benchmark._ensure_protocol(output, protocol)
    assert (
        benchmark.Protocol.model_validate_json((output / "protocol.json").read_bytes()) == protocol
    )
    with pytest.raises(ValueError, match="does not match"):
        benchmark._ensure_protocol(output, protocol.model_copy(update={"warmup_iterations": 3}))

    calls = 0

    def load(*args: object) -> benchmark._Cell:
        nonlocal calls
        calls += 1
        return _cell([])

    monkeypatch.setattr(benchmark, "_load_cell", load)
    unit_output = tmp_path / "campaign"
    benchmark._ensure_protocol(unit_output, protocol)
    for _ in range(2):
        benchmark._run_unit(
            tmp_path, unit_output, protocol, "ethereum.lstm", 1, _resolved()["ethereum.lstm"]
        )
    assert calls == 1
    assert pl.read_parquet(
        unit_output / "latency" / "ethereum.lstm" / "sweep-001.parquet"
    ).columns == ["cell", "sweep", "pass_order", "workload", "origin_block", "elapsed_ns"]


def test_architecture_footprint_is_canonical_and_resumable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "campaign"
    protocol = _architecture_protocol()
    resolved = _architecture_resolved()
    benchmark._ensure_protocol(output, protocol)
    checkpoint = tmp_path / "artifact.ckpt"
    checkpoint.write_bytes(b"checkpoint")
    loads = 0

    def load(root: Path, artifact_id: UUID) -> tuple[ArtifactAssociation, nn.Module]:
        nonlocal loads
        del root
        loads += 1
        return _association(5, artifact_id), nn.Linear(2, 3)

    monkeypatch.setattr(benchmark, "_resolve_protocol", lambda *_args: resolved)
    monkeypatch.setattr(benchmark, "load_artifact", load)
    monkeypatch.setattr(benchmark, "artifact_checkpoint_path", lambda *_args: checkpoint)

    benchmark.run_footprint(tmp_path, output)
    benchmark.run_footprint(tmp_path, output)

    rows = pl.read_parquet(output / "footprint.parquet")
    assert rows.height == 9
    assert rows["checkpoint_bytes"].unique().to_list() == [len(b"checkpoint")]
    assert rows["parameters"].unique().to_list() == [9]
    assert rows["trainable_parameters"].unique().to_list() == [9]
    assert loads == 9


def test_powermetrics_parsing_and_conservative_phase_membership() -> None:
    fixture = Path(__file__).with_name("powermetrics-sample.plist").read_bytes()
    sample, repeated = benchmark._power_samples(fixture + b"\0" + fixture + b"\0")

    assert sample == repeated
    assert sample.end_second == 1_785_596_705
    assert sample.elapsed_ns == 1_008_260_624
    assert (sample.cpu_mw, sample.gpu_mw, sample.ane_mw, sample.combined_mw) == (
        2137.34,
        88.2708,
        0.0,
        2225.62,
    )
    assert sample.thermal_pressure == "Nominal"

    earliest_start = sample.end_second * 1_000_000_000 - sample.elapsed_ns
    latest_end = (sample.end_second + 1) * 1_000_000_000
    assert benchmark._contained(sample, earliest_start, latest_end)
    assert not benchmark._contained(sample, earliest_start + 1, latest_end)
    assert not benchmark._contained(sample, earliest_start, latest_end - 1)


def test_pair_reduction_time_weights_power_and_retains_thermal_state() -> None:
    fixture = Path(__file__).with_name("powermetrics-sample.plist").read_bytes()
    base = benchmark._power_samples(fixture)[0]
    samples = (
        replace(
            base,
            end_second=9,
            elapsed_ns=1_000_000_000,
            cpu_mw=800.0,
            gpu_mw=200.0,
            combined_mw=1000.0,
        ),
        replace(
            base,
            end_second=10,
            elapsed_ns=2_000_000_000,
            cpu_mw=1600.0,
            gpu_mw=400.0,
            combined_mw=2000.0,
        ),
        replace(
            base,
            end_second=21,
            elapsed_ns=1_000_000_000,
            cpu_mw=3200.0,
            gpu_mw=800.0,
            combined_mw=4000.0,
        ),
        replace(
            base,
            end_second=22,
            elapsed_ns=3_000_000_000,
            thermal_pressure="Heavy",
            cpu_mw=1600.0,
            gpu_mw=400.0,
            combined_mw=2000.0,
        ),
    )
    idle = benchmark._Phase(1, "idle", 7_000_000_000, 12_000_000_000)
    active = benchmark._Phase(
        1, "active", 18_000_000_000, 24_000_000_000, active_seconds=4.0, completed_workloads=2
    )

    row = benchmark._pair_row(samples, idle, active)
    joules_per_workload = row.pop("joules_per_workload")

    assert row == {
        "pair": 1,
        "idle_samples": 2,
        "idle_sample_seconds": 3.0,
        "active_samples": 2,
        "active_sample_seconds": 4.0,
        "idle_cpu_mw": 4000.0 / 3.0,
        "idle_gpu_mw": 1000.0 / 3.0,
        "idle_ane_mw": 0.0,
        "idle_combined_mw": 5000.0 / 3.0,
        "active_cpu_mw": 2000.0,
        "active_gpu_mw": 500.0,
        "active_ane_mw": 0.0,
        "active_combined_mw": 2500.0,
        "active_seconds": 4.0,
        "completed_workloads": 2,
        "workloads_per_second": 0.5,
        "thermal_valid": False,
    }
    assert joules_per_workload == pytest.approx(5.0 / 3.0)


def test_pair_reduction_preserves_negative_energy() -> None:
    fixture = Path(__file__).with_name("powermetrics-sample.plist").read_bytes()
    base = benchmark._power_samples(fixture)[0]
    samples = (
        replace(base, end_second=9, elapsed_ns=1_000_000_000, combined_mw=3000.0),
        replace(base, end_second=21, elapsed_ns=1_000_000_000, combined_mw=1000.0),
    )
    idle = benchmark._Phase(1, "idle", 8_000_000_000, 10_000_000_000)
    active = benchmark._Phase(
        1, "active", 20_000_000_000, 22_000_000_000, active_seconds=4.0, completed_workloads=2
    )

    assert benchmark._pair_row(samples, idle, active)["joules_per_workload"] == -4.0


def test_active_phase_rotates_origins_and_counts_completed_workloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    ticks = iter((0, 0, 4, 8, 12, 13))
    walls = iter((100, 200))
    monkeypatch.setattr(benchmark.time, "perf_counter_ns", lambda: next(ticks))
    monkeypatch.setattr(benchmark.time, "time_ns", lambda: next(walls))

    phase = benchmark._active_phase(_energy_cell(events), pair=2, duration_ns=10)

    assert phase == benchmark._Phase(
        pair=2,
        phase="active",
        start_ns=100,
        end_ns=200,
        active_seconds=13e-9,
        completed_workloads=3,
    )
    assert events[::4] == ["model5:2", "model5:4", "model5:0"]


def test_collector_health_checks_stay_outside_measured_phases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    ticks = iter(range(10))
    monkeypatch.setattr(benchmark.time, "time_ns", lambda: next(ticks))
    monkeypatch.setattr(benchmark.time, "sleep", lambda _seconds: events.append("sleep"))
    monkeypatch.setattr(
        benchmark,
        "_active_phase",
        lambda _cell, pair, _duration: (
            events.append("active") or benchmark._Phase(pair, "active", 0, 1)
        ),
    )

    phases = benchmark._run_phases(
        _energy_cell([]),
        {"pairs": 2, "phase_seconds": 1, "recovery_seconds": 1, "sample_rate_ms": 1000},
        lambda: events.append("health"),
    )

    assert [phase.phase for phase in phases] == ["idle", "active", "recovery", "idle", "active"]
    assert events == [
        "health",
        "sleep",
        "health",
        "active",
        "health",
        "health",
        "sleep",
        "health",
        "sleep",
        "health",
        "active",
        "health",
    ]


def test_powermetrics_failure_stops_collection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Process:
        returncode: int | None = None
        signal: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def send_signal(self, sent: int) -> None:
            self.signal = sent
            self.returncode = 1

        def wait(self) -> int:
            assert self.returncode is not None
            return self.returncode

    process = Process()
    invocation: list[str] = []

    def popen(argv: list[str], **options: object) -> Process:
        invocation.extend(argv)
        assert options["stdout"] is not subprocess.PIPE
        return process

    monkeypatch.setattr(benchmark.subprocess, "Popen", popen)

    with pytest.raises(RuntimeError, match="powermetrics failed"):
        benchmark._capture_power(tmp_path / "trace.plist", lambda alive: alive())

    assert invocation[:3] == ["sudo", "-n", "/usr/bin/powermetrics"]
    assert process.signal == signal.SIGTERM


@pytest.mark.usefixtures("umask_0002")
def test_energy_cell_publishes_atomically_and_resumes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = Path(__file__).with_name("powermetrics-sample.plist").read_bytes()
    sample = benchmark._power_samples(fixture)[0]
    start = sample.end_second * 1_000_000_000 - sample.elapsed_ns
    end = (sample.end_second + 1) * 1_000_000_000
    phases = [
        benchmark._Phase(1, "idle", start, end),
        benchmark._Phase(1, "active", start, end, active_seconds=2.0, completed_workloads=1),
    ]
    loads = 0
    captures = 0
    events: list[str] = []

    def load(*args: object) -> benchmark._Cell:
        nonlocal loads
        loads += 1
        return _energy_cell([])

    def capture(path: Path, measure: object) -> list[benchmark._Phase]:
        nonlocal captures
        del measure
        captures += 1
        events.append("collector")
        path.write_bytes(fixture + b"\0" + fixture + b"\0")
        return phases

    def authorize(argv: tuple[str, ...], *, check: bool) -> subprocess.CompletedProcess[bytes]:
        assert argv == ("/usr/bin/sudo", "-v")
        assert check
        events.append("authorize")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(benchmark, "_load_cell", load)
    monkeypatch.setattr(benchmark, "_warm", lambda *_args: events.append("warm"))
    monkeypatch.setattr(benchmark, "_capture_power", capture)
    monkeypatch.setattr(benchmark.subprocess, "run", authorize)
    output = tmp_path / "campaign"
    settings = {"pairs": 1, "phase_seconds": 1, "recovery_seconds": 0, "sample_rate_ms": 1000}

    for _ in range(2):
        benchmark._run_energy_unit(
            tmp_path,
            output,
            "ethereum.lstm",
            _resolved()["ethereum.lstm"],
            warmup_iterations=1,
            settings=settings,
        )

    cell = output / "energy" / "ethereum.lstm"
    assert stat.S_IMODE(cell.parent.stat().st_mode) == 0o755
    assert loads == captures == 1
    assert events == ["warm", "authorize", "collector"]
    assert {path.name for path in cell.iterdir()} == {
        "powermetrics.plist",
        "phases.json",
        "pairs.parquet",
    }
    assert json.loads((cell / "phases.json").read_text())["settings"] == settings
    assert pl.read_parquet(cell / "pairs.parquet")["pair"].to_list() == [1]

    with pytest.raises(ValueError, match="settings"):
        benchmark._run_energy_unit(
            tmp_path,
            output,
            "ethereum.lstm",
            _resolved()["ethereum.lstm"],
            warmup_iterations=1,
            settings={**settings, "phase_seconds": 2},
        )


def test_energy_command_reuses_the_existing_protocol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "campaign"
    protocol = _protocol()
    benchmark._ensure_protocol(output, protocol)
    resolved = _resolved()
    units: list[tuple[str, int, dict[str, int]]] = []
    monkeypatch.setattr(benchmark, "_resolve", lambda *_args: resolved)

    def run_unit(
        storage_root: Path,
        target: Path,
        cell: str,
        requests: object,
        warmup_iterations: int,
        settings: dict[str, int],
    ) -> None:
        del storage_root, target, requests
        units.append((cell, warmup_iterations, settings))

    monkeypatch.setattr(benchmark, "_run_energy_unit", run_unit)

    benchmark.run_energy(tmp_path, output, pairs=20, phase_seconds=60, recovery_seconds=30)

    assert [cell for cell, _, _ in units] == list(resolved)
    assert all(warmup == protocol.warmup_iterations for _, warmup, _ in units)
    assert all(
        settings
        == {"pairs": 20, "phase_seconds": 60, "recovery_seconds": 30, "sample_rate_ms": 1000}
        for _, _, settings in units
    )
