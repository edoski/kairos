# Generic lifecycle extraction implementation-review ledger

Status: Slice 2 complete and green; authorized live production preflight in progress

This ledger is the planning authority for extracting KAIROS's generic remote-work and durable-work
lifecycle into a reusable standalone repository.

## Pre-run state

- KAIROS checkout: `/Users/edo/dev/python/kairos`
- Branch: `main`
- Immutable planning baseline: `56f24ae364a70ba704b56a01edbc43f90156fd3e`
- Worktrees: one pre-existing main worktree; no run-owned branch or worktree
- Pre-existing branches: `main` and `codex/compact-cuda-execution`, with their existing remotes
- Protected pre-existing work: modified `app/package.json` adding the existing `allowScripts`
  declaration and untracked `docs/research/thesis-epigraph-candidates.md`
- Concurrent user-owned work observed later and left untouched:
  `docs/research/thesis-epigraph-finalists.md` and
  `docs/research/thesis-epigraph-fresh-pass.md`, plus
  `docs/research/thesis-epigraph-canonical-epics-pass.md`
- Run-owned planning file: `docs/research/lifecycle-extraction-implrevloop.md`
- External mutations authorized on 2026-08-10: create and push the public
  `edoski/servatus` GitHub repository and claim the normalized PyPI project name `servatus` during
  Slice 1. Prefer PyPI Trusted Publishing; request a token only if the authenticated publisher path
  cannot complete the first prerelease upload.
- Local Servatus implementation and its ordered commit/review loop are authorized. Remote research
  SSH, Slurm commands, scheduler mutation, image builds, file transfer, scientific execution, and
  any write to KAIROS outputs or remote scratch remain unauthorized.

## Fixed intent

- Create one standalone repository that can support KAIROS and future ML projects.
- Extract generic work identity, private resumable work state, staged output, atomic no-clobber
  publication, completion/restart bookkeeping, remote submission, allocation packing, and durable
  submission receipts where those concepts prove genuinely generic.
- Leave all KAIROS scientific and application meaning in KAIROS: typed Corpus, Study, Method,
  training, artifact, evaluation, observation, experiment, mobile, and model-selection contracts.
- Preserve KAIROS's full-state `last.ckpt` resume behavior. The generic repository may own the
  durable workspace that keeps the file, but it must not interpret Lightning checkpoints or decide
  when training is scientifically complete.
- Preserve immutable direct canonical KAIROS objects, no-overwrite publication, failed-work
  preservation, exact request/object associations, deterministic ordering, and canonical manifest
  authority.
- Treat all pre-existing KAIROS thesis data as immutable external state. Never rewrite, move,
  migrate, delete, chmod, relink, clean, or otherwise mutate canonical outputs, logs, checkpoints,
  experiment drafts, scratch, or other existing work. Do not contact or mutate currently running or
  queued research-cluster jobs. They finish through their existing checkout, scripts, and immutable
  image before any cutover.
- Preserve the exact canonical KAIROS output paths, filenames, schemas, associations, ordering, and
  byte formats. Servatus changes future staging and commit mechanics only. Existing finalized
  outputs remain valid and readable. Incomplete old-layout work stays untouched and, if it must be
  resumed or finalized, uses the old checkout before clean-break cutover; Servatus adds no legacy
  parser.
- Use a clean break. After KAIROS adopts the new module, delete replaced KAIROS infrastructure and
  tests instead of retaining wrappers, compatibility modes, migrations, or parallel execution
  paths.
- Optimize for a small deep interface, direct ownership, few concepts, ordinary Python, and lean
  interface-level tests. Do not build a workflow language, scheduler platform, experiment tracker,
  model framework, artifact database, plugin system, or distributed control plane.
- Make Servatus production-ready inside a declared narrow envelope: unprivileged workstation-side
  submission of homogeneous independent processes in single-node Slurm allocations. Cover ordinary
  CPU-only, one-GPU, and whole-multi-GPU processes without adding distributed ranks, heterogeneous
  jobs, arrays, daemons, or scheduler plugins.
- Make every workload resource explicit and inspectable. Derive allocation totals from the actual
  packed task count, never from node capacity, never silently escalate or clamp a request, and treat
  target limits as local guardrails rather than cluster authorization.
- Preserve KAIROS's current resource values, task bytes and order, balanced packing, concurrent
  exclusive exact steps, image, paths, logs, wait behavior, and aggregate exit result. Local parity
  is necessary; an authorized real-cluster comparison is required before any throughput claim or
  cutover.
- Produce mythological, historical, Greek, or Latin repository-name candidates and check current
  package/repository collisions before recommending them.

## Existing protected contracts

- ADR 0006: direct durable object authority and hidden-sibling atomic publication.
- ADR 0007: native OpenSSH/Slurm/Apptainer execution with scientific requests independent of host,
  queue, log, and transfer state.
- `docs/CONTEXT.md`: KAIROS domain terminology remains KAIROS-owned and must not leak into the new
  repository's interface.
- POSIX hard links and rename are currently same-filesystem operations. The extracted module must
  either make this an explicit interface invariant or use a different mechanism without weakening
  immutability and no-clobber behavior.

## Recommended repository

Recommended name: **Servatus**, from Latin *servatus*, “saved, preserved, kept safe.” Use
`servatus` for the GitHub repository, Python distribution, import package, and executable. The name
fits the package's central promise: preserving resumable work across failure and exposing validated
results safely, without binding the project to KAIROS, ML, Slurm, or one storage layout.

One standalone Python repository contains a public library and a thin operator CLI. The library is
the primary seam used by KAIROS. The CLI mirrors campaign operations for humans and future projects;
KAIROS does not shell out to it.

Servatus is a durable Slurm-work package, not an ML framework. Its short description should be:

> Run resumable work through Slurm and atomically publish validated outputs.

Resilience is concentrated at the two demonstrated failure boundaries: distributed submission and
POSIX publication. Campaign records intent before external acceptance and refuses ambiguous replay;
Workspace locks writers, preserves resumable state, syncs durable content, and commits with a
kernel no-replace operation. Elsewhere, prefer direct values, concrete adapters, and propagated
application exceptions. Do not turn resilience into retries, plugins, backend matrices, recovery
frameworks, or defensive layers for trusted internal state.

The repository owns two sibling deep modules:

1. `Campaign`: immutable opaque task and resource plans, exact inspectable single-node Slurm
   allocations, native OpenSSH/Apptainer execution, durable submission intent and receipts, restart
   skipping, and explicit ambiguity resolution.
2. `Workspace`: single-writer resumable private work, binding to an opaque identity, unique staged
   output, hard-link assembly, durable atomic no-replace publication, and success-only cleanup.

They stay separate because submission and publication occur in different processes and cannot form
one transaction. Combining them would either expose scheduler state to every publisher or make the
package understand KAIROS output topology.

### Public Python interface

```python
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True, slots=True)
class Task:
    key: str
    args: tuple[str, ...]
    stdin: bytes


@dataclass(frozen=True, slots=True)
class ResourceRequest:
    cpus_per_task: int
    memory_mib_per_task: int
    gpus_per_task: int
    time_limit: str

    @classmethod
    def from_toml(cls, path: Path) -> "ResourceRequest": ...


@dataclass(frozen=True, slots=True)
class SlurmTarget:
    host: str
    slurm_bin: PurePosixPath
    apptainer: PurePosixPath
    image: PurePosixPath
    work_root: PurePosixPath
    log_root: PurePosixPath
    partitions: tuple[str, ...]
    account: str | None
    qos: str | None
    constraint: str | None
    gpu_gres: str | None
    max_tasks_per_allocation: int
    max_cpus_per_allocation: int
    max_memory_mib_per_allocation: int
    max_gpus_per_allocation: int
    max_time_limit: str
    max_allocations_per_submit: int
    max_script_bytes: int

    @classmethod
    def from_toml(cls, path: Path) -> "SlurmTarget": ...


@dataclass(frozen=True, slots=True)
class PlannedAllocation:
    task_keys: tuple[str, ...]
    cpus: int
    memory_mib: int
    gpus: int
    time_limit: str


class SubmissionPlan:
    @property
    def digest(self) -> str: ...

    @property
    def allocations(self) -> tuple[PlannedAllocation, ...]: ...


@dataclass(frozen=True, slots=True)
class JobReceipt:
    allocation_id: str
    job_id: int
    cluster: str | None
    task_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CampaignStatus:
    pending_task_keys: tuple[str, ...]
    receipts: tuple[JobReceipt, ...]
    ambiguous_allocation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Publication:
    destination: Path
    cleanup_pending: bool


class Campaign:
    @classmethod
    def open(cls, path: Path, tasks: Sequence[Task]) -> "Campaign": ...

    def plan(
        self,
        target: SlurmTarget,
        resources: ResourceRequest,
        *,
        completed: Collection[str] = (),
        retry: Collection[str] = (),
        tasks_per_allocation: int | None = None,
    ) -> SubmissionPlan: ...

    def submit(self, plan: SubmissionPlan) -> tuple[JobReceipt, ...]: ...

    def reconcile(self, target: SlurmTarget, allocation_id: str) -> JobReceipt: ...

    def resolve(
        self,
        allocation_id: str,
        *,
        job_id: int | None,
        cluster: str | None = None,
    ) -> None: ...

    def status(self) -> CampaignStatus: ...


class Draft:
    @property
    def path(self) -> Path: ...

    def link(self, source: Path, destination: str | PurePosixPath) -> None: ...


class Workspace:
    def __init__(self, destination: Path, *, identity: bytes) -> None: ...

    def __enter__(self) -> "Workspace": ...
    def __exit__(self, *exc: object) -> None: ...

    @property
    def path(self) -> Path: ...

    def publish(self, build: Callable[[Draft], None]) -> Publication: ...


def publish(destination: Path, build: Callable[[Draft], None]) -> Publication: ...
```

Only these application-facing values and a compact error hierarchy are exported from
`servatus.__init__`. Script rendering, journals, POSIX calls, locks, filesystem traversal, command
execution, and test adapters remain internal seams.

`build(draft)` is the semantic seam. Servatus commits only after the callback returns. KAIROS writes
the exact output tree and performs every domain validation inside that callback before returning.
Servatus never receives a validator registry, output schema, completion enum, or ML-specific type.

`Workspace(destination, identity=...)` derives a stable hidden sibling from the application-owned
destination, binds it to the SHA-256 digest of the opaque identity, and exposes only its mutable
`path`. Reopening with different identity raises `WorkConflict`. The context holds a nonblocking
exclusive writer lock. A worker failure preserves the workspace; another same-key worker fails
immediately instead of concurrently mutating checkpoints.

Nested workspaces cover Study fan-in without a generic workflow engine. KAIROS opens the canonical
Study workspace, then opens one nested workspace whose private destination is the KAIROS-owned
`trial-<method_index>` result. The nested workspace retains that complete private result. KAIROS
later validates the exact ordered trial set and publishes the canonical Study through the parent
workspace. Servatus knows neither Method indices nor the number or meaning of trials.

`publish(destination, build)` is the disposable sibling for mobile export and benchmark units. It
uses the same staged commit but always removes its private stage after failure. It has no resumable
workspace or identity binding.

### Resource and planning contract

`ResourceRequest` states one independent application's exact need. Direct construction and TOML
loading run the same validation. All four fields are required;
there are no resource defaults or automatic detection. CPU and memory are positive, GPUs are a
nonnegative whole count, and wall time uses one strict documented `[days-]hours:minutes:seconds`
form with a positive effective Slurm duration. Memory is stored in MiB and rendered as an exact
binary unit; zero/all-memory requests are invalid.

One `SubmissionPlan` is homogeneous: every included Task uses the same request. A project with CPU
preprocessing, one-GPU training, and two-GPU evaluation creates three Campaigns rather than asking
Servatus to bin-pack unlike tasks. `gpus_per_task=0` omits allocation and step GRES plus Apptainer
`--nv`. A positive value gives one opaque application process exactly that many Slurm-assigned GPUs;
Servatus does not create ranks, `torchrun`, MPI, or application topology.

`SlurmTarget` is one concrete execution lane. It owns validated OpenSSH, one absolute remote
`slurm_bin` directory from which Servatus derives `sbatch`, `srun`, `squeue`, and `sacct`, the
absolute Apptainer path, immutable image and filesystem roots, ordered partitions, optional typed account/QOS/simple
constraint, one count-free GPU GRES, conservative request ceilings, a controller-call cap, and a
maximum rendered batch-script size. A target can be supplied by an administrator, but a local TOML
file is not a security boundary. Slurm associations, QOS,
partitions, plugins, availability, enforcement, priority, allocation granularity, and billing remain
authoritative. If listed partitions do not share one truthful conservative envelope, use separate
targets. Servatus never claims the envelope is a physical node inventory.

For an allocation containing `n` Tasks with `(C, M, G, T)`:

```text
allocation CPUs       = n * C
allocation memory MiB = n * M
allocation GPUs       = n * G
allocation wall time  = T
```

Every child step requests `(C, M, G)` again. The effective packing capacity is the minimum of the
caller cap, target task cap, and the integer CPU, memory, and applicable GPU ceilings. One Task that
cannot fit is rejected before journal mutation or SSH. A requested packing cap above the feasible
cap is rejected rather than silently reduced. Larger resource requests may therefore produce more
allocations, but Servatus never changes `C`, `M`, `G`, or `T` and never rounds a partial group up to
target capacity. One one-GPU Task on a twelve-GPU node requests one GPU.

`Campaign.plan()` is deterministic and makes no SSH/Slurm call or submission-state mutation. Its
immutable result binds the task, completion/retry selection, target, resources, ordered groups,
exact aggregate totals, scripts, and payload/script digests. Public summaries show Task keys,
resource totals, value origins, and digests—not opaque stdin. Complete script display is an explicit
diagnostic because it contains payloads. `Campaign.submit(plan)` rejects a foreign or stale plan,
durably records its exact digest, submits serially up to the target's per-invocation allocation cap,
and leaves the rest pending. It never recomputes a materially different plan behind a reviewed dry
run. Planning rejects any completely rendered script above `max_script_bytes`; opaque payloads are
never staged separately after scheduler acceptance. The live target cap must not exceed the site's
configured Slurm script limit. Submission is eager: the bounded loop finishes before returning its
receipt tuple, so callers cannot accidentally submit nothing or only a consumed iterator prefix.

The packing rule remains deterministic: preserve authored order, use the fewest allocations for the
effective cap, keep sizes within one, and place larger groups first. This preserves KAIROS's current
behavior, but the ledger does not call it universally throughput-optimal; queue state and runtime
variance make no static grouping policy universally optimal. `tasks_per_allocation` remains the one
operator tuning knob and may only lower the legal cap.

The source-backed Slurm rationale, failure boundaries, exact arithmetic, and operator acceptance
criteria are recorded in
[`servatus-production-resource-model.md`](servatus-production-resource-model.md). That record is
evidence for this ledger; the public contract above remains the implementation authority.

Raw `#SBATCH`, SSH, shell, `srun`, Apptainer, environment, and arbitrary option passthrough are not
interfaces. Strict TOML rejects unknown keys, booleans as integers, controls, NULs, relative remote
paths, count-bearing GRES values, and conflicting resource owners. The native adapter uses a
deterministic minimal remote environment so hostile `SBATCH_*` or related variables cannot change a
reviewed plan. Exact environment isolation and absolute tool paths must pass the live-cluster gate
before KAIROS migration.

### Campaign contract

- `Task.key` is nonempty, unique, stable, and opaque. KAIROS uses keys such as
  `study:<uuid>:method:<index>`, `artifact:<uuid>`, and `evaluation:<uuid>`.
- `Task.args` are arguments to the immutable image runscript, never shell text. `Task.stdin` is
  byte-exact opaque application input. Both are embedded in the accepted batch script and may be
  visible to cluster administrators or accounting. They must not contain secrets. Ordinary summaries
  redact them; complete-script diagnostics explicitly expose them.
- `Campaign.open()` freezes task order and the digest of every key, argument vector, and payload.
  Reopening with reordered or changed tasks raises `TaskConflict` before submission.
- Campaign state uses owner-only files, rejects symlink/path substitution, atomically replaces
  records, fsyncs their directory, and fails closed on unknown schema versions.
- A Campaign binds to the first submitted target/resource/plan lineage. Changing resources, target
  semantics, or payloads requires a new Campaign; retry never silently increases time or resources.
- KAIROS supplies `completed` after applying its own canonical-object checks. Servatus never treats
  scheduler acceptance or path existence as scientific completion.
- `retry` is explicit. It creates a new attempt for an already receipted, noncompleted task and
  preserves the earlier receipt.
- Pending tasks retain authored order and are balanced into the fewest homogeneous allocations;
  group sizes differ by at most one and larger groups come first. Current `9 -> 3 + 3 + 3` behavior
  remains.
- V1 uses one node and one independent process per Task. Each Task receives one concurrent
  `srun --exclusive --exact --nodes=1 --ntasks=1` step with its exact CPU, memory, and zero-or-more
  whole-GPU request. The parent starts all steps, waits for all of them, does not cancel successful
  siblings after one failure, and exits nonzero if any step fails.
- Every allocation uses one native
  `ssh -T -o BatchMode=yes ... <slurm_bin>/sbatch --parsable` call. The remote
  script runs one immutable Apptainer image, binds and changes to `work_root`, passes task arguments
  to the image runscript, and safely decodes opaque stdin without interpolating it as shell.
- Scheduler job names/comments contain only a Servatus prefix and random allocation identity, never
  task keys, arguments, paths, or payloads.
- `JobReceipt` means Slurm accepted the allocation. It never means a task ran successfully or
  produced a valid KAIROS object. It preserves the positive integer job ID and optional cluster from
  `sbatch --parsable` output and prints the exact `job_id[;cluster]` form.

Before contacting Slurm, Campaign writes and syncs an immutable allocation intent containing a
stable allocation ID, ordered task keys, script digest, submission window, and unique Slurm job
name. After parsing the positive job ID, it writes and syncs the receipt. An intent without a
receipt is `ambiguous`; automatic submission stops instead of risking duplicate GPU work.
`reconcile()` makes one bounded absolute-path `squeue`/`sacct` lookup and adopts only one exact
identity match;
missing, multiple, unavailable, or unprovable results remain ambiguous. `resolve(..., job_id=N,
cluster=...)` manually adopts an operator-provided job identity. `resolve(..., job_id=None)` records the operator's
assertion that Slurm did not accept the allocation and permits a fresh attempt. Servatus does not
poll, monitor, or turn scheduler state into application completion.

This is not exactly-once execution. The package promises durable intent, fail-closed ambiguity, and
explicit recovery. A human can still make an incorrect resolution; canonical no-replace
publication remains the final data-safety backstop.

### Workspace and publication contract

- Supported systems are POSIX Linux and macOS. Windows and object stores are outside V1.
- Work, stage, hard-link sources, and destination must share one filesystem. Cross-device use raises
  `CrossDevicePublication`; there is no silent copy fallback.
- `Draft.link()` accepts only a regular-file source path, rejects an occupied or escaping
  destination, and requires the caller not to mutate the source inode after linking.
- Builders may use `Draft.path` for ordinary application-native writers such as Polars and Torch.
  Symlinks and special files are rejected before commit.
- Every publication attempt gets a unique stage. Concurrent attempts cannot delete each other's
  state.
- A builder exception exposes no destination. Disposable stages are removed; resumable Workspace
  state is preserved. The original exception propagates.
- Before commit, files and directories are synced. Commit uses a kernel no-replace rename primitive,
  not check-then-`Path.rename()`: `renameat2(RENAME_NOREPLACE)` on Linux and
  `renamex_np(RENAME_EXCL)` on macOS. Unsupported systems fail rather than weaken no-clobber.
- The destination parent is synced after commit. Hardware durability remains subject to the
  filesystem and mount guarantees.
- Successful Workspace publication removes private state only after commit and parent sync.
  Cleanup failure is reported as committed output with `cleanup_pending=True`; it must never turn a
  committed object into an apparent failed task.
- If a process restarts after commit but before cleanup, canonical application validation remains
  authoritative. Servatus may remove matching residue but never overwrites or reinterprets the
  canonical object.

These guarantees strengthen current KAIROS behavior. Current check-then-rename code does not prove
strict no-clobber against an empty raced destination, does not lock same-ID workers, and does not
sync publication directories. Existing behavior remains the minimum compatibility target, not the
new module's ceiling.

### What moves and what stays

| Servatus owns | KAIROS owns |
| --- | --- |
| Opaque task identity, order, argv, and stdin lifecycle | Request parsing and `CandidateProcessInput` |
| Strict target/resource TOML, ceilings, exact arithmetic, and dry-run plan | Actual image, storage, and KAIROS resource values |
| OpenSSH, Slurm script, Apptainer invocation, job ID | Immutable KAIROS image contents and runscript |
| Deterministic balanced packing, allocation intent, receipts, retry history | Which work units an experiment requires |
| Submission restart and ambiguity state | Canonical completion checks supplied to Campaign |
| Hidden workspace and unique stage placement | Canonical KAIROS destination paths and filenames |
| Single-writer lock and identity binding | UUID and request/association meaning |
| Hard links, same-device checks, sync, exclusive rename | Which files belong in an output |
| Failure preservation and success cleanup | `last.ckpt` format and Lightning resume behavior |
| Atomic absent-or-complete visibility | Study roster/order, objectives, and selection |
| One-shot output publication | Observation, artifact, evaluation, and mobile validation |
| Generic campaign state format | `cells.tsv` authored scientific design |
| Generic submission provenance | Final experiment manifest and cell-to-object meaning |

`cells.tsv`, typed request files, `ExperimentKind`, and canonical manifests remain in KAIROS.
`jobs.tsv` leaves KAIROS and is replaced by Servatus-owned campaign state. Corpus production remains
external; there is no KAIROS Corpus publisher to extract.

`CandidateProcessInput` moves from `kairos.execution` to KAIROS request/worker ownership. Hidden
`kairos remote workflow` and `kairos remote candidate` leaves remain KAIROS application adapters.
The KAIROS Apptainer image and its site-specific build procedure remain KAIROS-owned.

### Rejected designs

1. **One minimal `run()` interface.** Rejected because scheduler acceptance and validated
   publication cannot form one transaction. It hides two different lifetimes behind flags and
   callbacks.
2. **Global package-owned run store.** Rejected for V1. It introduces framework result promotion,
   retirement, and garbage-collection state. Destination-adjacent nested Workspaces cover current
   direct objects and Study fan-in while keeping topology application-owned.
3. **CLI-first object/task/finalizer protocol.** Rejected because the package would own all-of-N
   readiness and trigger application finalizers. That moves Study topology out of KAIROS and creates
   a workflow language.
4. **Exposed scheduler and filesystem ports.** Rejected until a second production adapter exists.
   Native OpenSSH/Slurm/Apptainer and POSIX are the concrete V1 implementations. Fake adapters are
   private test seams.
5. **Submitit, Hydra, Parsl, Snakemake, Nextflow, or Row as dependencies.** Rejected. Submitit is the
   only plausible narrow library, but its callable/pickle worker protocol is the wrong side of the
   SSH boundary and adds an accepted-but-unrunnable crash window. The others are workflow runtimes
   or CLIs that would duplicate Campaign, topology, cache, or completion ownership. None owns
   application-validated immutable publication through the current SSH/Apptainer deployment seam.
6. **Resources attached to every Task.** Rejected because heterogeneous grouping, bin packing, and
   scheduler topology would leak into the Task interface. Different resource shapes use separate
   homogeneous Campaigns.
7. **Named resource presets or administrator policy objects.** Rejected as required interfaces.
   Presets hide exact workload intent; a local policy object cannot enforce authorization. Concrete
   strict targets may be administrator-authored, but Slurm remains the policy authority.
8. **Raw scheduler escape hatches.** Rejected because arbitrary directives or arguments can conflict
   with derived resources, bypass review, and poison provenance. Add one typed target field only
   after two real deployments require the same behavior.

### Repository shape

```text
servatus/
  .github/workflows/ci.yml
  .github/workflows/publish.yml
  .gitignore
  AGENTS.md
  CONTRIBUTING.md
  LICENSE
  README.md
  SECURITY.md
  pyproject.toml
  uv.lock
  docs/
    CONTEXT.md
    agents/
      issue-tracker.md
    adr/
      README.md
      0001-opaque-application-seam.md
      0002-posix-workspace-publication.md
      0003-native-slurm-campaign.md
  src/servatus/
    __init__.py
    __main__.py
    _campaign.py
    _posix.py
    _slurm.py
    _workspace.py
    cli.py
  tests/
    test_campaign.py
    test_cli.py
    test_slurm.py
    test_workspace.py
```

Use Python 3.11 or newer, Hatchling, `uv`, dataclasses, `tomllib`, `argparse`, `json`, `pathlib`,
`subprocess`, `shlex`, `fcntl`, `ctypes`, and ordinary POSIX calls. V1 has zero Python runtime
dependencies and no plugin mechanism. Development uses pytest, Ruff, Pyright, and Vulture.

The root README owns installation, public interface, strict target/resource/task formats, the
supported Slurm/version envelope, planning and provenance, operator/admin deployment guidance,
guarantees, and non-goals. `SECURITY.md` states that Servatus is an unprivileged user client rather
than a policy or isolation layer. `docs/CONTEXT.md` defines only Servatus terms. Three ADRs record
the application seam, durable POSIX transaction, and native Slurm campaign. Do not create
overlapping guides or design documents.

CLI:

```text
servatus plan TASKS.jsonl --target TARGET.toml --resources RESOURCES.toml --campaign STATE_DIR \
  --output PLAN.json [--tasks-per-allocation N]
servatus validate STATE_DIR PLAN.json
servatus submit STATE_DIR PLAN.json
servatus status STATE_DIR
servatus reconcile STATE_DIR ALLOCATION_ID --target TARGET.toml
servatus resolve STATE_DIR ALLOCATION_ID (--job-id N [--cluster NAME] | --not-submitted)
```

The task file is a CLI adapter format: key, argument vector, and stdin file path. The Python
interface remains authoritative. KAIROS uses the Python interface directly and does not author this
generic file. Planning reads and freezes the task bytes in Campaign state, while `PLAN.json` contains
only the immutable plan, public resource values, and digests—not opaque stdin. `validate` performs
one bounded remote `sbatch --test-only` call per distinct allocation shape and never submits or
changes Campaign state. `submit` accepts that exact plan or rejects it as stale; it does not
silently re-plan.

Cancellation stays native and outside Servatus V1. The README tells an operator to use the printed
receipt with the site's ordinary `scancel` command. Cancelling a job cancels the entire packed
allocation, does not establish application completion, and does not enable retry automatically. An
unresolved ambiguous allocation has no proven job identity and must be reconciled or manually
resolved before any cancellation decision.

`SlurmTarget.from_toml()` and `ResourceRequest.from_toml()` strictly reject unknown keys, booleans
where integers are expected, relative remote paths, control characters, counted GRES names,
nonpositive CPU/memory/time values, negative GPUs, and invalid time forms. Moving current
`REMOTE.yaml` to `REMOTE.toml` and resources to `RESOURCES.toml` lets both repositories drop PyYAML
from this infrastructure path.

CI runs Linux and macOS interface tests, Ruff, Pyright, Vulture, wheel/sdist build, and an installed
CLI smoke. Tests use temporary filesystems and fake executables; no test contacts SSH, Slurm,
Apptainer, GPUs, or external storage.

### Explicit V1 non-goals

- ML models, datasets, HPO, metrics, experiment tracking, registries, or scientific schemas.
- DAGs, dependencies, all-of-N object finalization, or a workflow language.
- Scheduler plugins, local execution, Kubernetes, cloud batch, DRMAA, Docker, or SSH libraries.
- Multi-node, ranks, MPI, `torchrun`, elastic/distributed training, heterogeneous Campaign resources,
  Slurm heterogeneous jobs, or arrays.
- Fractional/shared GPUs, MPS, shards, manual GPU indices, GPU-frequency control, arbitrary GRES, or
  automatic GPU-model inference.
- Raw scheduler/directive/environment passthrough, resource discovery or escalation, queue-aware
  packing, dynamic work stealing, whole-node exclusivity, overlap, overcommit, or alternate Slurm
  memory modes.
- Background queue monitoring, polling, automatic retry, cancellation, hold/release, or requeue.
- Image building, file transfer, rsync, deployment, or secrets management.
- Object stores, network filesystems without the required POSIX guarantees, cross-filesystem
  publication, copy fallback, symlink publication, or Windows.
- Exactly-once execution or automatic inference of application completion.
- Generic manifests, validator registries, callback classes, dependency-injection containers, or
  compatibility shims.

### Ecosystem decision

- Submitit is the nearest small library. It provides real arrays, job handles, status, cancellation,
  logs, result transport, rank metadata, and requeue support. Its natural contract is nevertheless
  cluster-local Python callable/pickle submission, not workstation-to-SSH opaque tasks. It does not
  own durable Campaign intent, application completion, workspace cleanup, or publication.
- Snakemake and Nextflow validate isolated work and success-gated stage-out as useful patterns, but
  would move orchestration into a file DAG or JVM/Groovy workflow language.
- Parsl is a full DAG/futures/worker runtime.
- Row is the nearest lean CLI, but product-path existence is weaker than KAIROS canonical
  validation and it has no atomic publication transaction.

Use those projects as design evidence, not dependencies. Servatus's distinguishing contract is:

```text
opaque task
  -> durable submission intent and receipt
  -> resumable single-writer workspace
  -> application-owned work and validation
  -> atomic immutable publication
  -> success-only cleanup
```

### Scheduler dependency decision

Servatus V1 has no scheduler-library dependency. Its private Campaign adapter invokes OpenSSH and
Slurm's stable command-line interfaces directly. Submitit is prior art, not a dependency, optional
backend, or public interface. The full source-pinned decision is recorded in
[`servatus-submitit-decision.md`](servatus-submitit-decision.md).

A real Submitit 1.5.4 fake-Slurm probe proved the strongest case for adoption: one allocation could
launch three ranks, give each one GPU and a distinct opaque payload, and enter through an Apptainer
Python command. It also proved the decisive failure. Submitit calls `sbatch` before moving its
temporary callable pickle to the job-ID path. A process failure immediately after accepted job
`4242` left no worker payload. Repairing that through Servatus would require replacing Submitit's
private submission core, the exact behavior the dependency was meant to own.

The native adapter instead prepares the complete deterministic script and payload before one
`ssh ... sbatch --parsable` call. It fsyncs the intent first and the receipt afterward. Lost replies
still create unavoidable ambiguity, but an accepted Slurm job remains runnable because the
controller already owns its complete batch script. Servatus reconciles or fails closed; it never
silently resubmits.

Reconsider Submitit only when at least two real projects require its natural profile: submission
from a Slurm login node, a shared pinned Python environment, Python-callable tasks and results,
conventional arrays or distributed ranks, or library-owned cancellation/requeue. Do not add a
speculative adapter before then.

### Naming candidates

Availability was checked on 2026-08-10. “Clear” means the normalized PyPI URL returned no project
and GitHub name search found no material exact-name repository. It is not a reservation or trademark
clearance.

| Rank | Name | Meaning and fit | Collision check |
| --- | --- | --- | --- |
| 1 | **Servatus** | Latin “saved, preserved, kept safe”; resumable work and safe publication | PyPI clear; no exact GitHub repository |
| 2 | **Peractus** | Latin “carried through, completed”; whole lifecycle | PyPI clear; no exact GitHub repository |
| 3 | **Relatus** | Latin “carried back, reported”; remote work returned | PyPI clear; one inactive exact repository |
| 4 | **Conditus** | Latin “stored away, hidden”; private durable state | PyPI clear; one inactive exact repository |
| 5 | **Epanodos** | Greek “return, recurrence”; resume and retry | PyPI clear; no exact GitHub repository |
| 6 | **Frontinus** | Roman engineer and infrastructure administrator | PyPI clear; no exact GitHub repository |

Reject `Ergon`, `Nostos`, `Consus`, `Custos`, `Opifex`, `Cursus`, `Telos`, `Themis`, `Limen`, and
`Dromeus`: their package or repository names already collide materially with developer tools,
storage systems, ML, authentication, or compute projects.

## Implementation-review slices

Every slice uses a fresh implementer following the `implement` skill and a distinct fresh reviewer
following `code-review`. Review pins the exact baseline and committed head, runs Standards and Spec
as separate parallel axes, and returns `GREEN LIGHT` only with zero actionable findings. Rejected
findings return to the same implementer; the same reviewer checks only the correction delta and
finding closure. The orchestrator never implements or reviews product changes.

Global protected-state gate for every slice: no agent or command may mutate pre-existing KAIROS
canonical outputs, logs, checkpoints, experiment drafts, scratch, thesis data, remote storage, or
running/queued jobs. No research-cluster SSH or scheduler command is authorized. Tests use synthetic
temporary directories only. Any future live acceptance requires a new explicit authorization after
the current jobs drain; this approval does not supply it.

### Setup gate: repository inception

Status: complete

- Create the empty public `edoski/servatus` GitHub repository with the approved short description;
  Slice 1 adds the MIT license. No issues, PRs, releases, or package upload are implied beyond the
  explicit steps below.
- Create `/Users/edo/dev/python/servatus` with branch `main` and one empty baseline commit so every
  implementation slice has a real fixed point and three-dot review range.
- Push only the empty inception baseline before Slice 1 implementation. Push the Slice 1 head only
  after independent zero-finding review.
- Record its remote, baseline SHA, initial branches, and worktrees in this ledger.
- New-repository implementation works directly on its isolated `main`, one writer at a time.
- KAIROS implementation uses a run-owned `codex/servatus-extraction` worktree from the then-current
  `main`, preserving the existing dirty main checkout and pre-existing compact-CUDA branch.
- GitHub creation and the Slice 1 pushes are authorized. No KAIROS remote push is authorized.

Recorded inception:

- Public repository: `https://github.com/edoski/servatus`
- Local checkout: `/Users/edo/dev/python/servatus`
- Branch/worktrees: one `main` worktree; no other branch or worktree
- Immutable baseline: `eea6135f08eeeb4ba418577616e3c9a7e52c2948`
- Baseline commit: `chore: initialize repository`
- Remote: `origin=https://github.com/edoski/servatus.git`; baseline pushed successfully

### Slice 1: Servatus durable workspace and publication

Status: complete; baseline `eea6135f08eeeb4ba418577616e3c9a7e52c2948`; accepted head
`d09a846c46ebad655317462da8edca1d967166d1`

Implementer: `/root/slice1_workspace_impl`; direct writer on the single Servatus `main` worktree.

Reviewer: `/root/slice1_workspace_review`, with independent parallel Standards and Spec lanes.

Scope:

- Bootstrap the complete standalone repository shape, governance files, zero-dependency packaging,
  context glossary, ADRs 0001–0002, Linux/macOS CI, and a least-privilege PyPI Trusted Publishing
  workflow. Slice 1 uses version `0.0.1`; it is a functional publication-only alpha, not the
  production-ready `0.1.0` release.
- Implement `Workspace`, `Draft`, `Publication`, `publish()`, the compact public errors, identity
  binding, nonblocking writer lock, stable work path, unique stage, hard-link helper, recursive sync,
  Linux/macOS no-replace rename, success cleanup, and committed-with-residue reporting.
- Test only through the public interface on real temporary filesystems, with narrow private fault
  injection for crash points unavailable through ordinary calls.
- After the Slice 1 implementation and correction loop returns green, push the accepted head,
  configure PyPI's pending Trusted Publisher for `edoski/servatus` and the exact publish workflow,
  and manually publish `0.0.1` to claim the normalized project name. PyPI documents that a pending
  publisher does not reserve a name; only its first successful upload creates the project. Use no
  long-lived API token unless the authenticated OIDC setup cannot be completed and the user then
  supplies one explicitly.

Non-goals:

- Campaign, Slurm, SSH, Apptainer, task files, KAIROS imports, application schemas, or a global run
  store.
- Automatic releases, release-on-push, TestPyPI, signed tags, GitHub Release creation, or any claim
  that `0.0.1` is production-ready.

Protected behavior and tradeoffs:

- Preserve failed resumable work and clean disposable stages.
- Never overwrite a destination or silently copy across filesystems.
- Support only Linux/macOS POSIX semantics. Fail closed on unsupported no-replace primitives.
- Accept the small hidden platform implementation needed for a truthful exclusive rename instead
  of advertising a weaker check-then-rename guarantee.
- The implementation and tests operate only in `/Users/edo/dev/python/servatus` and temporary test
  directories. They must not read or write KAIROS `outputs/`, experiment data, scratch, remote
  storage, or scheduler state.

Expected outcome:

> Any Python project can keep resumable private work and publish an application-validated immutable
> directory through one small interface, with no ML knowledge and no partial or overwritten
> canonical output.

Checks:

- Workspace binding, restart, same-key lock, builder failure, hard-link inode, escaping paths,
  special files, cross-device rejection, destination races, no-replace behavior, file/directory
  sync ordering, successful cleanup, post-commit cleanup failure, and nested workspace publication.
- `uv run pytest`, Ruff check/format, Pyright, Vulture, wheel/sdist build, and installed-library
  import smoke on supported local platforms; CI matrix covers Linux and macOS.
- Inspect the built `0.0.1` wheel/sdist before upload; verify PyPI project ownership and artifact
  hashes after upload. Publishing happens only from the accepted commit through the pinned workflow.

Dependencies and gates:

- Depends only on the repository inception baseline.
- GitHub and PyPI mutations are the authorized Slice 1 external systems. Research SSH, Slurm,
  Apptainer, KAIROS data, and KAIROS code remain out of scope.

Recorded result:

- Initial implementation: `b138b40a881f372f7d9d374a9d863743bd3df690`
  (`feature(workspace): add durable publication`). The first independent review rejected it with
  six Standards and four Spec findings. The hard findings covered NUL-truncated C paths, path-based
  macOS parent substitution, crash-stranded identity initialization, and double-close descriptor
  ownership. Softer findings covered stage cleanup, bounded corrupt-state reads, and documenting
  linked-source immutability.
- Correction: `d09a846c46ebad655317462da8edca1d967166d1`. It added raw-boundary NUL
  rejection, descriptor-relative macOS `renameatx_np(RENAME_EXCL)`, atomic synced identity
  installation, bounded identity reads, exact descriptor/stage ownership, sync-failure cleanup,
  adversarial race coverage, and the hard-link immutability contract.
- Same-reviewer correction review: `GREEN LIGHT`; Standards 0 findings, Spec 0 findings.
- Accepted local gates: 30 tests passed and one Linux-only cross-device test skipped locally;
  Ruff check/format, strict Pyright, Vulture, Python 3.11, wheel/sdist build and inspection,
  installed-wheel import, and diff checks passed.
- Accepted head pushed to public `edoski/servatus` `main`. GitHub CI run
  `31377009274` passed the full gate on both Ubuntu and macOS.
- GitHub environment `pypi` and PyPI Trusted Publishing bind exactly
  `edoski/servatus`, `.github/workflows/publish.yml`, and environment `pypi`. Publish run
  `31377016353` succeeded from the accepted head using OIDC and no long-lived token.
- PyPI `servatus` is claimed under the user's account as sole owner. Version `0.0.1` is live. The
  wheel SHA-256 is `67b6e0187f51c4df979c69c60fab2440de10078fbec884789ca3a24f4ca8ff7c`;
  the sdist SHA-256 is `d45605ac4deda280a1ec8d6064f77ea5f11415fa1843e8bfc11ee98cb51e14bf`.
  Both match the accepted local build, and a fresh PyPI install/import smoke returned `0.0.1`.
- No GitHub Release or tag was created. No KAIROS application code, outputs, experiment data,
  scratch, remote files, running/queued jobs, SSH, Slurm, or Apptainer state was touched.

### Slice 2: Servatus Slurm Campaign and CLI

Status: complete and green; exact baseline
`d09a846c46ebad655317462da8edca1d967166d1`; accepted head
`0c454bd38da4f3d5b0ba4f0777b708f8a2eb011c`

Implementer: `/root/slice2_campaign_impl`; direct writer on the single Servatus `main` worktree.

Reviewer: `/root/slice2_campaign_review`, with fresh parallel Standards and Spec lanes.

Implementation record: `a329339691ef26f30a0c642af988982845374a98`
(`feature(campaign): add durable Slurm execution`), 17 files and `+2566/-33`. The implementer
reported 141 passing synthetic tests and one expected platform skip; Ruff check/format, strict
Pyright, Vulture, wheel/sdist build and inspection, isolated installed-wheel import/version, and
both installed CLI help paths passed. The worktree was clean. Live SSH, Slurm, Apptainer, GPU,
TRES, throughput, push, release, and publication gates were not run before review.

Review round 1: rejected at `a329339691ef26f30a0c642af988982845374a98`; Standards 4
findings, Spec 6 findings. Standards found a writer/loader state-size contradiction, missing parent
sync for new Campaign installation, leaked journal stages on write/sync failure, and untyped
malformed-plan exceptions. Spec found non-GPU GRES accepted as GPU, incomplete explicit
plan/intent provenance and sensitive-script diagnostics, type-confused plan comparison, raw rather
than effective Slurm time, discarded `sbatch --test-only` decisions, and invalid direct target path
types surviving until planning. Worst severity was P1. All findings returned to the same
implementer; the same reviewer will inspect only the correction delta and closure.

Correction round 1: `b0723013ea857542da0f96e886eb82363f6ab1e7`
(`fix(campaign): harden durable submission plans`). The original implementer resumed preserved
partial work after one usage-limit interruption and committed without amending the rejected head.
It reports all ten findings mapped to fixes, 167 full-suite tests passing with one expected platform
skip, 137 focused tests passing, and all static/build/artifact/installed-CLI gates green. The
original reviewer is re-reviewing only `a329339...b072301` and finding closure; one usage-limit
interruption was retried with the same reviewer and worker identities.

The original reviewer and both original review lanes then failed before sampling because their
service usage allowance was exhausted. The user explicitly authorized replacing those blocked
lanes with fresh subagents. `/root/slice2_campaign_rereview` is the fresh read-only correction
reviewer, with fresh parallel Standards and Spec lanes pinned to the unchanged correction delta and
the same ten closure criteria. This is an operational waiver of same-reviewer continuity, not a
waiver of either review axis or the zero-finding gate.

Correction re-review 1: rejected at `b0723013ea857542da0f96e886eb82363f6ab1e7`.
The fresh lanes incorporated all late pre-interrupt findings and confirmed criteria 1 and 3–10
closed. One P1 remained on both axes: a concurrent opener could observe a newly created Campaign
directory, skip the creator's pending parent-directory sync, install state, and return without any
successful proof that the parent entry was durable. The reviewer reproduced the ordering
deterministically. That single finding was returned to the original implementer for correction
round 2; stable correction hunks remain out of scope.

Correction round 2: `0c454bd38da4f3d5b0ba4f0777b708f8a2eb011c`
(`fix(campaign): prove directory durability on open`). Every opener now descriptor-syncs the parent
before Campaign state access, so it must wait for or supply a successful durability proof. The
implementer reports deterministic blocked/failing two-opener coverage, 169 passing tests with one
expected platform skip, and all static/build/artifact/installed-CLI gates green. The same fresh
reviewer pair checked only `b072301...0c454bd` and the remaining P1 closure.

Final correction review: `GREEN LIGHT`; Standards 0 findings, Spec 0 findings. Four focused
durability/concurrency tests, 169 full-suite tests with one expected platform skip, 122 Campaign/CLI
tests, Ruff check/format, strict Pyright, Vulture, and diff checks passed. All ten round-1 findings
and the one round-2 concurrency finding are closed. Live SSH, Slurm, Apptainer, GPU, TRES,
isolation, and throughput checks remain external-gate work. The accepted `0.1.0rc1` candidate is
local and unpushed.

Authority: local implementation, commits, synthetic tests, independent review, correction, and
ledger updates are authorized. After Slice 2 is green, the user also authorizes the isolated live
Servatus production gate and, only if it passes, the stable `0.1.0` Servatus push, tag, GitHub
Release, and PyPI publication. This authority never permits KAIROS integration before its declared
dependency, mutation of KAIROS output/data/scratch, or mutation of pre-existing scheduler jobs.

Continuation authority: after Slice 2, proceed through all later slices without another routine
pause once each declared dependency and review gate is satisfied. This does not waive the external
Servatus production-acceptance gate, authorize contact with the research cluster or its jobs/files,
or authorize Servatus/KAIROS pushes, tags, GitHub Releases, PyPI publication, image deployment, or
mutation of protected KAIROS state.

Local KAIROS implementation is independent of remote cutover. After Servatus is accepted and its
stable dependency is installable, Slices 3–7 may proceed in the run-owned local worktree while old
remote jobs continue through their existing checkout and immutable image. Local work uses source,
synthetic temporary state, and ordinary tests only; it never opens or mutates thesis outputs or
remote scratch. Only deployment, image/config changes, protected-state handling, and live KAIROS
GPU comparison wait for the old remote path to be safe to retire.

Scope:

- Implement `Task`, `ResourceRequest`, strict `SlurmTarget` TOML, immutable `SubmissionPlan`,
  `Campaign`, `JobReceipt`, deterministic plan digest, exact resource arithmetic, balanced packing,
  durable intent/receipt journal, explicit retry, bounded ambiguity reconciliation, manual
  resolution, native OpenSSH invocation, quote-safe Slurm/Apptainer script rendering, opaque
  payload transport, local status, and the six CLI commands.
- Support one homogeneous request per Campaign: positive CPU/memory/time and zero-or-more whole GPUs
  for one opaque process. Compute every allocation from its actual group; omit GRES and `--nv` for
  CPU-only work and preserve the same typed or untyped GPU GRES at allocation and step scope.
- Implement fully local `plan` plus an explicit bounded `validate` using `sbatch --test-only` once per
  distinct allocation shape. Bind submission to the reviewed plan, target, request, task order,
  exact scripts, and payload digests.
- Enforce conservative target ceilings and a per-invocation allocation cap before journaling or
  SSH. Bound the complete encoded batch script using a target cap validated against Slurm's site
  configuration. Sanitize the remote scheduler environment and expose no raw command/directive
  escape hatch.
- Add ADR 0003 and complete the root README contract.

Non-goals:

- Background scheduler polling, automatic retry, monitoring, cancellation, requeue, transfer,
  image building, local execution, scheduler adapters, DAGs, heterogeneous resources, distributed
  ranks, arrays, dynamic packing, or application completion probes inside the package.

Protected behavior and tradeoffs:

- Preserve current ordered balanced one-GPU step packing and aggregate allocation exit behavior.
  Generic CPU-only and whole-multi-GPU requests must not change the one-GPU rendering path.
- Request exact partial-node resources; never render job-level `--exclusive`, never infer node
  capacity, and never silently clamp, round up, or escalate an explicit request.
- Treat target profiles as user-side guardrails. Slurm remains authoritative for policy, admission,
  isolation, allocation, and billing; Servatus is not a privileged cluster service.
- Submission acceptance remains distinct from work completion.
- Prefer fail-closed ambiguous state and explicit operator resolution over silent duplicate work.
- A reconciliation command performs one bounded query and accepts only one exact identity match.
- Keep one concrete OpenSSH/Slurm/Apptainer implementation; test adapters stay private.

Expected outcome:

> A project can submit an immutable ordered task campaign, restart submission safely, inspect local
> provenance, and resolve the unavoidable scheduler-receipt ambiguity without teaching Servatus
> what any task computes.

Checks:

- Strict target/resource schemas and injection cases; boolean-as-integer, zero/all-memory, invalid
  duration, counted-GRES, unknown-key, hostile-environment, and cap rejection; one/four-task KAIROS,
  CPU-only, and two-GPU golden scripts; opaque multiline/binary payloads.
- Exact/over-limit encoded script-size boundaries; no accepted job may depend on a post-acceptance
  payload file.
- Table/property checks over ordinary task counts and zero/one/two/four-GPU requests: positive
  ordered balanced groups, exact sums, all ceilings, partial-group totals, unchanged wall time, and
  authored-order preservation. Assert CPU-only omits GRES/`--nv`, two-GPU work gives one process two
  GPUs, and no script contains job-level exclusivity, overlap, or unlimited resources.
- Local plan has no SSH or submission-state mutation; persisted plan excludes stdin, plan/script
  digests are stable, and stale/foreign plans fail. Remote validation is bounded and never submits.
- Positive/cluster-qualified job IDs and eager full-call submission; intent-before-submit ordering;
  normal restart; failure after
  accepted job but before receipt; unique/absent/multiple/unavailable reconciliation; manual
  resolution/adoption; explicit retry history; later-group pending preservation; maximum
  allocations per invocation; installed CLI help and fake-executable end-to-end smoke.
- Full Slice 1 checks plus repository-wide pytest, Ruff, Pyright, Vulture, build, and installed-wheel
  CLI smoke. No live SSH, Slurm, GPU, or Apptainer call.

Dependencies and gates:

- Slice 1 final head is the exact baseline.
- A zero-finding review produces a `0.1.0rc1` candidate, not a stable release. Stable `0.1.0` and
  KAIROS integration depend on the external production-acceptance gate below. Push, GitHub release,
  and PyPI publication remain separately authorized external mutations.

### External gate: Servatus 0.1 production acceptance

Status: live execution passed; stable-release hardening and review pending

- Begin with read-only inventory. Never hold, release, cancel, requeue, reprioritize, alter
  dependencies, or otherwise mutate any pre-existing queued/running job. Submit new acceptance jobs
  only when the inventory establishes a noninterfering window or route; otherwise pause.
- Put every acceptance file, log, campaign, and optional test image under a newly created explicit
  SHA-named Servatus acceptance path. Never write, move, delete, relink, migrate, or clean existing
  KAIROS outputs, experiment data, logs, checkpoints, scratch, images, or other thesis state.

- Present the supported envelope and threat boundary to a cluster administrator: Servatus is an
  unprivileged user-side OpenSSH/Slurm/Apptainer client, not a scheduler plugin, daemon, security
  boundary, or replacement for Slurm policy.
- Inventory the target's Slurm version and capabilities, absolute executable paths, partitions,
  account/QOS/constraint/GRES names, cgroup/device isolation, and conservative CPU/memory/GPU/time
  ceilings, plus the configured maximum batch-script size. One target may list several partitions
  only if one truthful conservative envelope fits all of them.
- Run bounded `servatus validate` and separately authorized CPU-only, one-GPU, one-process/two-GPU,
  and four-packed-one-GPU smokes. Verify requested versus allocated TRES, logs, exit propagation,
  and four distinct physical GPU UUIDs for the packed case.
- Do not deliberately create a live ambiguous/orphan allocation. Deterministic fake-Slurm crash
  injection is sufficient for intent/receipt ambiguity; a live orphan adds scheduler risk without
  strengthening the contract.
- Review the immutable intent/receipt/ambiguity record, sanitized scheduler environment, exact
  request provenance, documentation, build artifacts, version support statement, and no privileged
  installation requirement.
- Fix any failure through another implementation/review correction loop. Stable `0.1.0` may be
  tagged and published only after this gate passes; the user authorized that stable release on
  2026-08-10. Unit tests and fake Slurm alone are insufficient.

Live record, 2026-08-10, candidate `0c454bd38da4f3d5b0ba4f0777b708f8a2eb011c`:

- Read-only inventory found Slurm 23.11.4, `select/cons_tres` with `CR_CPU_MEMORY`, cgroup task and
  affinity plugins, absolute `/usr/bin` Slurm executables, `/usr/bin/apptainer` on compute nodes,
  and no configured `SchedulerParameters` script-size override. The acceptance target imposed a
  conservative one-MiB script cap. The only pre-existing user job, `44282`, remained running on
  `h100sxm5` and was never held, released, canceled, requeued, reprioritized, or otherwise changed.
- Every new file and log stayed under local `/tmp/servatus-acceptance-0c454bd` or remote
  `/scratch.hpc/edoardo.galli3/servatus-acceptance-0c454bd`. Build job `44587` created and tested a
  44,666,880-byte diagnostic SIF on the isolated `sbuild` partition. No KAIROS output, experiment,
  checkpoint, scratch, deployment image, log, checkout, or remote configuration was opened for
  mutation.
- Four serial `servatus validate` calls accepted the exact CPU-only, one-GPU, one-process/two-GPU,
  and four-task/four-GPU shapes without submission. Jobs `44592`–`44595` then proved byte-exact
  stdin and argv, exact requested and allocated TRES, CPU-only omission of CUDA/GRES, one visible
  physical GPU, two distinct GPUs in one process, durable unambiguous receipts, and child-exit-7 to
  allocation-exit-1 aggregation while successful siblings completed.
- The first four-pack used one Slurm CPU per task and exposed a site-topology constraint: on this
  SMT2 cluster, each exclusive step consumes one physical core while `CR_CPU_MEMORY` accounts one
  requested CPU as one logical thread. Only two steps could run at once; the later two retried and
  reused the same UUIDs. CPU-only diagnostic job `44596` reproduced the exact two-step ceiling and
  showed affinity pairs such as `0,128`. This was not a KAIROS-versus-Servatus renderer delta.
- A corrected Servatus profile requested two logical CPUs per task. Job `44598` requested and was
  allocated exactly eight CPUs, four GiB, and four GPUs; all four 12-second steps began within four
  milliseconds, completed in 14 seconds, and saw four distinct physical GPU UUIDs. Servatus must
  not silently inflate CPU requests or disable binding. The standalone documentation must state
  that it requests concurrent exact steps, while actual simultaneous placement depends on the
  site's CPU/GRES topology and a truthful resource profile. KAIROS requests 32 CPUs per GPU task,
  so its current four-way packing has ample core granularity and its renderer-equivalent throughput
  path is not negatively changed.
- The live gate is behaviorally accepted. Before stable publication, the same Slice 2 implementer
  and reviewer must complete a narrow release-hardening correction: record the validated envelope
  and topology caveat in Servatus, change `0.1.0rc1` to `0.1.0`, rerun all local artifact gates, and
  return zero Standards and Spec findings. No scheduler-rendering or automatic-resource change is
  authorized by this finding.

### Slice 3: KAIROS disposable publication adoption

Status: planned; depends on accepted, installable Servatus 0.1.0

Scope:

- Pin Servatus through the KAIROS root dependency and lock.
- Replace the local one-shot publication helper in `experiments/inference_benchmark.py` and the
  mobile export hidden-sibling choreography with `servatus.publish()`.
- Preserve application-owned builders, schemas, native XNNPACK validation, protocol identity, file
  layouts, CLI output, and all scientific/mobile behavior.
- Delete replaced generic publication code and mechanics-only tests; retain focused KAIROS adapter
  and domain/native tests.

Non-goals:

- Training, candidates, Studies, evaluation, experiment bundles, Slurm, App runtime changes, real
  mobile assets, simulator/device runs, or scientific benchmark execution.

Protected behavior and tradeoffs:

- Mobile export remains disposable after failure; benchmark units remain immutable and restart
  skipped by their KAIROS protocol.
- No transition tests or compatibility path for former scratch names.

Expected outcome:

> KAIROS and its isolated mobile exporter use the external publication transaction for two simple
> output classes while retaining complete ownership of their file contents and validity.

Checks:

- Focused benchmark and mobile-export tests, root/mobile lock checks, root Ruff and Pyright, mobile
  export installed-environment smoke, and KAIROS status/diff/residue checks.
- No native device, generated model, energy campaign, Slurm, SSH, image, push, or PR gate.

### Slice 4: KAIROS resumable ML object lifecycle adoption

Status: planned; depends on Slice 3 green

Scope:

- Replace evaluation, artifact, candidate-result, and Study hidden workspace/staging/rename/cleanup
  mechanics with nested Servatus Workspaces.
- Pass Servatus-owned stable work paths into `_fit()` while leaving Lightning `last.ckpt`, callback,
  `ckpt_path`, selected checkpoint, validation observations, objective equality, and full-state resume
  entirely in KAIROS.
- Keep KAIROS canonical addresses and exact object layouts byte-compatible.
- Keep Study fan-in, exact Method order, request equality, checkpoint associations, observation
  validation, epoch constraints, best-result selection, and earliest-tie behavior in KAIROS.
- Delete replaced generic mechanics and mechanics-only tests while retaining the full Lightning
  interruption/resume and every scientific/schema/association test.

Non-goals:

- Model architecture, data pipeline, metrics, experiment authoring, Slurm submission, Corpus
  publication, or automatic evaluation resume.

Protected behavior and tradeoffs:

- Failed work and publication conflicts preserve resumable work. Successful publication cleans it.
- Same candidate identity cannot have concurrent writers.
- Evaluation failure remains preserved forensic work; KAIROS does not claim resumable inference
  unless it gains a real resume protocol.
- Scratch path changes are a clean break after old jobs drain; no legacy lookup.

Expected outcome:

> KAIROS code describes only how to train, validate, assemble, and interpret ML objects; Servatus
> exclusively owns their private work, staged publication, collision, durability, and cleanup
> lifecycle.

Checks:

- Focused evaluation, modeling, Study, collision, nested-workspace, association, objective, and full
  interruption/resume tests; Ruff/Pyright/Vulture with every finding manually checked; exact
  canonical tree and semantic residue audit.
- No GPU training, SSH, Slurm, or image claim from local CPU tests.

### Slice 5: KAIROS campaign and experiment lifecycle adoption

Status: planned; depends on Slice 4 green

Scope:

- Move `CandidateProcessInput` to KAIROS request/worker ownership.
- Translate typed KAIROS requests into opaque Servatus Tasks with stable domain-derived keys.
- Replace `kairos.execution` with Servatus target/Campaign calls; delete the module after callers
  move.
- Reduce `experiments/launch.py` to KAIROS request parsing, task mapping, canonical completion checks,
  one direct resource/target load, and receipt printing. Servatus owns plan/order verification,
  allocation arithmetic, packing, submission, restart, retry, and generic provenance. Do not retain
  a KAIROS wrapper around replaced Servatus mechanics.
- Preserve KAIROS's existing `--tasks-per-job` spelling and two-to-four validation as its thin CLI
  policy, translating it directly to Servatus `tasks_per_allocation`; the generic package itself
  permits singleton allocations.
- Replace `jobs.tsv` with Servatus campaign state inside the hidden KAIROS experiment draft.
- Keep `cells.tsv`, typed request files, cell labels, experiment kinds, canonical record checks, and
  final manifests in KAIROS.
- Use Workspace publication for manifest-only experiment closure so closure never destroys retry
  state before a successful commit.
- Replace `REMOTE.yaml` with strict Servatus-owned `REMOTE.toml` and `RESOURCES.toml`; remove the
  now-unused root PyYAML dependency if live imports confirm none remain. KAIROS uses
  `SlurmTarget.from_toml()` and `ResourceRequest.from_toml()` directly.

Non-goals:

- Scheduler monitoring, job success inference, automatic retry, queue mutation, transfers, image
  builds, experiment redesign, or manifest format changes.

Protected behavior and tradeoffs:

- Pin the current production request exactly: one GPU, 32 CPUs, 65536 MiB, and `3-00:00:00` per
  process; ordered partitions `h100sxm5,h100pcie,a100,l40s,l40`; untyped `gpu`; at most four tasks,
  128 CPUs, 262144 MiB, and four GPUs per allocation. Use `max_allocations_per_submit=64`: current
  102-task and 108-task launch modes require up to 51 and 54 allocations respectively when the user
  chooses two tasks per job, and must remain one invocation rather than silently leaving work
  pending.
- Pin a script-size cap from the authorized live inventory and prove the largest current four-task
  KAIROS payload fits before migration; do not assume Slurm's default is the site's value.
- Preserve exact request bytes—including the current trailing line feed—and order, `9 -> 3 + 3 + 3`
  packing, one GPU per process, one-node allocation, concurrent background
  `srun --exclusive --exact` steps, image/bind/work directory, `STORAGE_ROOT`, allocation/slot log
  shape, wait-all behavior, parent aggregate failure, canonical completion skipping,
  verifier-failure preservation, and manifest-only closure.
- The generic planner, journal, and CLI add no process to the allocated GPU hot path. Preserve old
  queued jobs and their immutable checkout/image until they drain.
- Introduce explicit ambiguous-submission refusal rather than preserving the current duplicate-work
  crash window.
- Accepted but failed/cancelled jobs require explicit retry; they are not silently resubmitted.
- KAIROS may contain direct construction/mapping code for its domain values, but no local class or
  helper may re-own Servatus planning, allocation arithmetic, script rendering, journaling,
  workspace, publication, or cleanup. Delete the old modules once callers move.

Expected outcome:

> KAIROS authors and understands experiments and work requests, while Servatus alone owns how those
> opaque tasks are packed, submitted, journaled, retried, and recovered.

Checks:

- Focused CLI/worker/campaign/experiment tests using fake submission; exact resource/target mapping;
  one-to-four-allocation golden parity; request bytes and task keys; `9 -> 3 + 3 + 3`; 102-task and
  108-task allocation counts at KAIROS capacities two, three, and four; completion-probe behavior;
  target/resource config injection cases; journal restart, ambiguity, and retry; bundle
  verification/closure; installed image-command rendering.
- Assert KAIROS always requests `gpus_per_task=1` and never acquires Servatus resource defaults.
  Compare old/new rendered scripts structurally and byte-for-byte where the clean interface permits;
  explain any deliberate syntax-only transport difference.
- Root full Python tests, Ruff, Pyright, Vulture, lock check, and source/docs residue audit.
- Client-side leanness audit: one direct KAIROS-to-Servatus translation path, no `jobs.tsv`, local
  packing loop, `sbatch`/`srun`/Apptainer renderer, generic scratch transaction, compatibility shim,
  or duplicate target/resource schema remains.
- No live SSH, scheduler, queue, image, or file-transfer mutation.

### Slice 6: KAIROS clean-break documentation and integration gate

Status: planned; depends on Slice 5 green

Scope:

- Delete obsolete imports, helpers, tests, docs, YAML schema wording, scratch naming, and generic
  lifecycle explanations from KAIROS.
- Add a KAIROS ADR that supersedes ADR 0007's implementation ownership while preserving native
  OpenSSH/Slurm/Apptainer execution and the KAIROS worker/domain seam. Keep ADR 0006's direct durable
  object authority and clarify that Servatus now implements its transaction mechanics.
- Keep KAIROS docs focused on its typed requests, canonical objects, scientific validation, and thin
  Servatus adapters. Link once to Servatus for generic mechanics.
- Run full integration and measure the final production/test/documentation LOC delta without making
  line reduction a correctness target.

Non-goals:

- New features, schema changes, legacy shims, issue/PR creation, remote deployment, or scientific
  execution.

Protected behavior and tradeoffs:

- One canonical owner per fact. Do not duplicate the complete Servatus contract in KAIROS.
- Preserve unrelated `app/package.json` work and all user-owned experiment outputs.
- Expected estimate, not a target: KAIROS production may fall roughly 300–420 LOC and
  generic/mechanics tests roughly 400–520 LOC. Cross-repository LOC may increase because Servatus
  has an independent contract, CI, and tests.

Expected outcome:

> The final KAIROS repository reads as an ML/scientific application using one external durable-work
> module, with no duplicate infrastructure path, stale contract, or compatibility residue.

Checks:

- Full root pytest, Ruff check/format, Pyright, `uv run vulture` with manual validation, `uv lock
  --check`, mobile-export tests and lock, App `npm test` and `npm run typecheck`, npm lock/install dry
  run, CLI help, import/residue search, canonical layout probes, and clean scoped diff/status.
- Explicitly unrun until authorized: real GPU training, SSH, Slurm, scheduler monitoring, file
  transfer, Apptainer image build/test, mobile simulator/device, native model assets, visual checks,
  push, package publication, and PR.

### Slice 7: compact-CUDA reconciliation

Status: planned; depends on Slice 6 green

Scope:

- Reconcile the pre-existing `codex/compact-cuda-execution` branch with final `main` after the clean
  extraction, preserving only its approved device-resident historical batching delta.
- Resolve expected overlaps in modeling/tests against Servatus-owned workspace paths without
  changing scientific outputs, ordering, weighting, publication, or KAIROS domain semantics.
- Use exact merge-base, nonmerge commit list, changed hunks, patch identity, parity tests, and residue
  evidence; do not infer parity from ancestry.

Non-goals:

- New CUDA optimization, remote build, GPU smoke, Slurm work, push, branch deletion, or modification
  of any pre-existing branch beyond the approved reconciliation.

Protected behavior and tradeoffs:

- Planning snapshot: `main=56f24ae364a70ba704b56a01edbc43f90156fd3e`, compact CUDA
  `3a1fe154f08be4719714c7425bfcbcc433be1172`, merge-base equals current main, and compact CUDA has two
  nonmerge commits. Re-pin all refs when the slice begins.
- The branch is pre-existing and must remain; only a run-owned worktree may be removed.

Expected outcome:

> Compact CUDA contains the final clean KAIROS main plus only its explicit CUDA execution
> differences, with the same Servatus integration and scientific/publication contracts as main.

Checks:

- Topology, commit and hunk diff, conflict/residue scan, CUDA-focused tests, full Python/static/lock
  gates proportionate to touched files, and independent fixed-range Standards/Spec review.
- GPU/image/Slurm smoke remains an explicit external gate.

## Final external deployment gates

The clean break cannot deploy while queued jobs, running jobs, experiment drafts with old
`jobs.tsv`, or resumable old-layout scratch are still needed. Before changing the university image
or remote checkout:

1. Read-only inventory the live queue, active immutable image paths, experiment drafts, canonical
   outputs, and scratch owners.
2. Let old-image jobs finish or obtain explicit authority for any scheduler mutation. Do not hold,
   release, cancel, requeue, resubmit, move, or delete them implicitly.
3. Close or archive old-layout experiment state only through its current code before the cutover;
   do not add legacy parsing to new KAIROS or Servatus.
4. Build a new immutable KAIROS image through the documented `sbuild` partition procedure from an
   isolated exact-SHA checkout. Run `apptainer build` then `apptainer test`.
5. Run separately authorized new-path KAIROS smokes with the same immutable application image and
   request bytes. Verify the one-task and four-packed-task scripts request exactly one GPU, 32 CPUs,
   65536 MiB, and three days per process; four steps run concurrently with distinct physical GPU
   UUIDs; nine tasks remain `3 + 3 + 3`; sibling failures are aggregated without cancelling
   successful siblings; and canonical KAIROS validation remains the only completion authority.
6. Compare old/new `ReqTRES`, `AllocTRES`, logs, results, and one representative task's
   elapsed/throughput behavior using the same immutable image, input, dedicated partition, and GPU
   model, preferably the same node. This lean A/B is a gross-regression check, not a statistical
   performance study; repeated trials or a thesis-scale campaign are unnecessary unless making a
   formal performance claim. The mixed production partition route is not valid A/B evidence.
7. Run one application publication smoke. Preserve the preceding image and old execution path until
   the GPU and publication gates pass.
8. Update remote image configuration only after acceptance. File transfer, remote pushes, package
   release, and deployment each require explicit authorization.

## Run records

Planning research completed on 2026-08-10. Independent source, failure-semantics, operational,
native-cost, alternatives, and adversarial audits all rejected Submitit as an internal V1
dependency. A throwaway Submitit 1.5.4 compatibility/crash probe was absorbed into the focused
decision record and deleted. Those availability checks preceded Slice 1; the public GitHub
repository and normalized PyPI project are now both owned as recorded above.

Independent Slurm-resource, admin-readiness, KAIROS-parity, interface-minimality, policy-boundary,
common-case, flexible-interface, packing-adversarial, and ownership audits converged on the narrow
production model in this ledger. A throwaway pure planner demonstrated exact homogeneous resource
arithmetic and current KAIROS groupings (`1`, `4`, `9 -> 3 + 3 + 3`, and
`102 -> 24*4 + 3 + 3`), plus CPU-only and whole-multi-GPU handling and rejection of heterogeneous
tasks or unsafe explicit caps. Its result was absorbed and the prototype was deleted. The
source-backed record is [`servatus-production-resource-model.md`](servatus-production-resource-model.md).

Final read-only KAIROS-parity, interface-leanness, and administrator-readiness reviews found and
closed planning defects in the KAIROS allocation cap and controlled A/B conditions; eager
submission; truthful payload secrecy; duplicate evidence types; undefined result values;
deterministic Slurm executable ownership; native cancellation guidance; cluster-qualified receipts;
canonical duration representation; and serial remote validation. All three correction reviews
returned `GREEN LIGHT` with no remaining actionable finding.

Slice 1 completed through the ordered implementation, independent rejection, correction, and
zero-finding re-review loop recorded above. The accepted package is public and installable as
`servatus==0.0.1`.

The user resumed Slice 2 on 2026-08-10. Its implementation-review loop starts from the exact
accepted Slice 1 head. This resumption does not authorize any research-cluster, KAIROS-output,
GitHub release, PyPI, or deployment mutation.

The user then authorized automatic continuation through all remaining implementation slices as
normal. That authority is dependency-gated: Slice 3 cannot begin until the separately authorized
production gate accepts Servatus and stable `0.1.0` is installable. No external gate or protected
state restriction is implicitly waived.

The user subsequently authorized the live Servatus acceptance gate and the conditional stable
`0.1.0` release. Existing data and existing queued/running jobs remain strictly protected. The live
gate uses only new isolated SHA-named state and new noninterfering smoke allocations after a
read-only preflight. The Servatus gate proves resource/execution correctness, not performance;
KAIROS later needs only one controlled representative A/B to detect a gross integration regression.

The user confirmed that remote-job drain constrains cutover, not local implementation. Once the
Servatus dependency gate is satisfied, local KAIROS slices continue without contacting the GPUs or
altering the old remote checkout/image; final deployment remains blocked until protected remote
work is safe.
