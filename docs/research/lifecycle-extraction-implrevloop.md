# Generic lifecycle extraction implementation-review ledger

Status: initial extraction program complete; consolidation plan reviewed and awaiting execution
approval. Planning baselines are clean KAIROS `c0021cb99fa1c28295059a1cc827d6d68afca633`
and clean Servatus
`2ccf749e2a4c3f5ad7ca572ee34fe78e5b1bb78f`. The separate inference-benchmark
scientific-readiness gate remains open.

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
- Within this Servatus extraction, preserve the exact canonical KAIROS output paths, filenames,
  schemas, associations, ordering, and byte formats. Servatus changes future staging and commit
  mechanics only. Existing finalized outputs remain valid and readable. Incomplete old-layout work
  stays untouched and, if it must be resumed or finalized, uses the old checkout before clean-break
  cutover; Servatus adds no legacy parser.
- The separately planned Blockweaver--KAIROS dataset alignment in task
  `019fea93-223d-7d42-bcfc-c4a499b59dd0` is outside this run. It may later replace only the external
  corpus boundary under its own ledger and migration authorization. This run neither implements nor
  alters that plan, touches `outputs/corpora` or `outputs/datasets`, nor makes Servatus understand
  datasets, corpus UUIDs, Blockweaver manifests, or migration. Studies, trials, artifacts,
  evaluations, experiments, figures, and other KAIROS-owned outputs retain the exact-preservation
  rule.
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

    def child(self, name: str, *, identity: bytes) -> "Workspace": ...

    def publish(self, build: Callable[[Draft], None]) -> Publication: ...


def publish(destination: Path, build: Callable[[Draft], None]) -> Publication: ...


def publish_file(destination: Path, write: Callable[[Path], None]) -> Publication: ...
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

Concurrent child workspaces cover Study fan-in without a generic workflow engine. KAIROS constructs
the canonical Study workspace and opens one `child(name, identity=...)` per Method without entering
the parent as an exclusive writer. A child holds a shared parent lifecycle lease and its own
exclusive writer lock, so different children run concurrently while a duplicate child fails
immediately. Parent entry remains exclusive and fails while any child is active. Each child retains
one complete private result; KAIROS later enters the parent, validates the exact ordered trial set,
and publishes the canonical Study. Servatus knows neither Method indices nor the number, readiness,
order, or meaning of children.

`publish(destination, build)` is the disposable directory sibling for mobile export and benchmark
directory units. `publish_file(destination, write)` is its explicit regular-file sibling: Servatus
passes one already-created empty adjacent stage file, the application writes and validates it in
place, and Servatus rejects inode substitution or a non-regular result. Both use the same durable
no-replace transaction and always remove their private stage after failure. Neither has a resumable
workspace or identity binding. Do not overload `publish()` with shape inference, add a `kind` flag,
or introduce a KAIROS wrapper.

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
criteria were absorbed into this ledger and the standalone Servatus repository. The duplicated
KAIROS research note was deleted in Slice 6; the public contract above remains the implementation
authority.

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
- `publish_file()` gives its writer an existing empty regular file and requires in-place mutation.
  The pinned inode must remain a regular file on the destination filesystem through validation and
  sync. Application bytes, schema, and validation remain entirely caller-owned.
- `Workspace.child(name, identity=...)` accepts one safe leaf, verifies the opaque parent identity,
  and returns a normal resumable Workspace under the parent's private work. Different children hold
  shared parent lifecycle leases and may overlap; the same child remains a nonblocking exclusive
  writer. Parent finalization uses the existing nonblocking exclusive lifecycle lock and fails
  `WorkspaceBusy` while any child is active. Servatus never waits for or interprets child readiness.
- Workspace open and cleanup take a short exclusive coordination lock on the verified stable
  destination-parent directory descriptor. This prevents a removable lock pathname from being
  unlinked and recreated as a different inode while another opener still holds the old lock. Never
  block on the parent lifecycle lock while holding coordination: unavailable shared/exclusive leases
  fail immediately, avoiding deadlock with child cleanup.
- The owner-only private Workspace container is the lifecycle trust root. Active handles pin and
  verify that parent entry; the durable identity inside it binds the lifecycle lock and work inode
  across normal reopens. Servatus does not claim isolation from arbitrary code running as the same
  Unix account that renames and recreates the entire owner-only container: such code can also read or
  rewrite every user-owned artifact and is outside this unprivileged library's security boundary.
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
external; there is no KAIROS Corpus publisher to extract. The later Blockweaver dataset-alignment
plan therefore requires no Servatus product change.

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
backend, or public interface. The source-pinned decision was absorbed into this ledger and the
standalone Servatus repository; the duplicated KAIROS research note was deleted in Slice 6.

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
`c494182cd6f036a253d41a00df5447b867b719b3`

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

Stable-release correction: after live acceptance, the same implementer committed
`c494182cd6f036a253d41a00df5447b867b719b3` (`chore(release): prepare stable 0.1.0`) on top of the
unamended candidate. Only README, ADR 0003, `pyproject.toml`, and `uv.lock` changed. The delta records
the validated Slurm 23.11.4 envelope and SMT/core-topology constraint, changes synchronized package
metadata from `0.1.0rc1` to `0.1.0`, and leaves all source, rendering, resource arithmetic, and
runtime dependencies unchanged. The same fresh reviewer checked the fixed `0c454bd...c494182`
range: `GREEN LIGHT`, Standards 0 findings and Spec 0 findings. Full verification reported and
proportionally repeated 169 passing tests with one expected platform skip, Ruff, formatting,
Pyright, Vulture, build, artifact metadata, installed wheel/CLI, and diff checks. Stable local head
is clean and awaits the separately authorized push/tag/release/PyPI sequence.

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

Status: complete and green; stable `0.1.0` released and published

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
- The live gate is accepted. The same Slice 2 implementer committed the narrow release-hardening
  correction at `c494182cd6f036a253d41a00df5447b867b719b3`; the same fresh reviewer returned
  `GREEN LIGHT` with zero Standards and Spec findings. Servatus is a clean stable `0.1.0` candidate.
  No scheduler-rendering or automatic-resource change resulted from the finding.
- Servatus `main` and annotated tag `v0.1.0` were pushed to the public
  `https://github.com/edoski/servatus` repository. GitHub CI passed on Ubuntu and macOS for both the
  branch push (run `31385574471`) and tag push (run `31385627514`). The published GitHub Release is
  `https://github.com/edoski/servatus/releases/tag/v0.1.0`.
- Release-triggered Trusted Publishing completed successfully in GitHub Actions run `31385685069`.
  PyPI exposes `servatus==0.1.0` with provenance: wheel SHA-256
  `3e78710f808068a58525d8cd36e29621d9b75d4e04635994c0dc56ebaffc05cc` and sdist SHA-256
  `f8bb055c83ad033aaf5433f4b87f4160fe4f86d97a8f3b49ebaed335c8f6aa10`. A strict isolated install
  from the PyPI index imported the package and returned metadata version `0.1.0`.

### Prerequisite Slice 2A: Servatus atomic regular-file publication

Status: complete and green; exact baseline `c494182cd6f036a253d41a00df5447b867b719b3`;
accepted head `f60335416b549fdc252c56152af2b9678e94bb72`

Implementer: `/root/slice2a_file_publication_impl`; sole writer in the Servatus `main` worktree.

Reviewer: `/root/slice2a_file_publication_review`, with fresh parallel Standards and Spec lanes.

Reason:

- Slice 3's read-only implementation pass found that KAIROS publishes two immutable canonical
  regular files, `protocol.json` and `sweep-NNN.parquet`, while Servatus 0.1 publishes only complete
  directory trees. Changing those destinations or retaining a KAIROS rename shim would violate the
  clean extraction boundary.
- Three independent interface designs and one disposable writer probe converged on one explicit
  addition: `publish_file(destination, write)`. The existing `publish()` and `Workspace` interfaces
  remain unchanged. A polymorphic Draft, output-kind flag, auto-detection, resumable file workspace,
  filesystem adapter, or KAIROS wrapper adds concepts without another real caller and is rejected.

Scope:

- Add `publish_file()` to the compact public interface and reuse the private POSIX transaction.
- Create one uniquely named destination-adjacent empty regular-file stage with exclusive creation,
  pin its descriptor and inode, pass its path to the application writer, and require in-place
  writing and validation. Use ordinary `0o666` creation subject to the process umask so the
  published file has normal writer-compatible permissions; preserve an explicit writer `chmod`.
- After the writer returns, reject substitution, symlink, directory, special-file, or filesystem
  change; sync the file; commit through the existing descriptor-relative kernel no-replace rename;
  sync the destination parent; and clean only this attempt's exact stage on failure.
- Preserve `DestinationExists`, `CrossDevicePublication`, `UnsafePublication`, and
  `UnsupportedPlatform`; propagate application exceptions unchanged and do not turn a committed
  result into apparent failure because of private residue.
- Document the narrow file contract and prepare a backward-compatible `0.2.0` candidate. A new
  public API is a minor release, not a `0.1.1` bug-fix release.

Non-goals:

- Directory or Workspace behavior changes; streams; copies; object stores; Windows; overwrite;
  multi-file transactions; validators; ML types; Blockweaver integration; datasets; corpus
  migration; KAIROS edits; external release or publication before its explicit gate.

Expected outcome:

> Any application can atomically expose either one validated immutable regular file or one validated
> immutable directory tree through two explicit operations backed by one durable transaction.

Checks:

- Existing-empty-stage writer ergonomics for ordinary `pathlib` and binary writers; successful
  bytes and mode; builder exception; missing/substituted/wrong-type stage; destination race;
  same-filesystem enforcement; file and parent sync ordering; cleanup ownership and failures;
  Linux/macOS exclusive rename; existing directory and Workspace suite unchanged.
- Full Pytest, Ruff check/format, strict Pyright, Vulture, lock check, wheel/sdist build and content
  inspection, installed-wheel import/version/API smoke, CLI help, and clean fixed-range diff.
- Fresh implementer and distinct reviewer under the same ordered correction loop. No KAIROS output,
  Blockweaver file, SSH, Slurm, Apptainer, GPU, push, tag, GitHub Release, or PyPI mutation.

Dependencies and gates:

- The accepted and published Servatus `0.1.0` head is the exact implementation baseline.
- Slice 3 was paused until the resulting Servatus release became reproducibly installable. The user
  authorized the `0.2.0` push, tag, GitHub Release, and PyPI publication after the green review.

Recorded result:

- Implementation commit `f60335416b549fdc252c56152af2b9678e94bb72`
  (`feature(publication): add atomic regular files`) added the explicit regular-file transaction,
  shared no-replace commit path, public export, documentation, focused adversarial coverage, and
  synchronized `0.2.0` metadata without a runtime dependency.
- The fresh reviewer returned `GREEN LIGHT`: Standards 0 findings and Spec 0 findings for the exact
  `c494182...f603354` range.
- Accepted gates: 179 tests passed and one platform-specific skip; Ruff check/format, strict
  Pyright, Vulture, lock check, wheel/sdist build and content inspection, isolated wheel install,
  `0.2.0` metadata and `publish_file` smoke, installed CLI help, and fixed-range diff check.
- Worktree clean. No push, tag, release, PyPI, GitHub, KAIROS, Blockweaver, SSH, Slurm, Apptainer,
  GPU, output, or external-state mutation occurred.
- The reviewed head was pushed to `main`; GitHub CI run `31389354062` passed on Ubuntu and macOS.
  Annotated tag `v0.2.0` points exactly to `f603354`; tag CI run `31389412085` passed on both
  platforms. GitHub Release `https://github.com/edoski/servatus/releases/tag/v0.2.0` triggered
  Trusted Publishing run `31389483759`, which succeeded without a long-lived upload token.
- PyPI exposes `servatus==0.2.0` with provenance. Wheel SHA-256:
  `122a26ac97b266595ba9aedb2350569b4f5970b7b067de38ddb4c3c9f170df19`; source archive SHA-256:
  `cfaa6a9829d25a8e15cd1c556af60cc60c25588f77d42186bd42dab1fb677fdf`. A fresh empty-cache index
  install returned `0.2.0`, imported `publish_file`, and passed the installed CLI smoke.

### Slice 3: KAIROS disposable publication adoption

Status: complete and green; exact baseline `79428b5db28e05082976732eaf882ed67640c984`;
accepted head `87f09c09f0441af49990c7c9be296e3286783ed2`

Checkout: run-owned `/Users/edo/dev/python/kairos-servatus-extraction` worktree on
`codex/servatus-extraction`, created from the clean committed local `main` baseline. The pre-existing
main worktree remains on `main` with its user-owned `app/package.json` edit and four untracked thesis
notes untouched. No run-owned change may be made in that main worktree.

Implementer: `/root/slice3_kairos_publication_impl`; sole writer in the run-owned worktree.

Reviewer: `/root/slice3_kairos_publication_review`, with fresh parallel Standards and Spec lanes.

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

Recorded result:

- Initial implementation `52574968d9035728c92f33c6bdeaf988ea509e94`
  (`refactor(publication): adopt Servatus transactions`) pinned `servatus==0.2.0` in root and mobile
  exporter projects, adopted `publish_file()` for exact protocol and Parquet destinations, adopted
  `publish()` for energy and mobile directories, and deleted local generic mechanics/tests.
- The first review rejected one P2 Standards finding and returned Spec green: the protocol writer
  lambda returned `Path.write_text()`'s integer instead of the callback contract's `None`; configured
  root Pyright did not include the experiment file, while an explicit file check exposed it.
- Correction `87f09c09f0441af49990c7c9be296e3286783ed2`
  (`fix(publication): return none from protocol writer`) added one typed writer without suppression or
  interface widening. The same reviewer and lanes returned `GREEN LIGHT`: Standards 0, Spec 0.
- Accepted gates: 112 root tests, 15 benchmark tests, 9 mobile-export tests including host XNNPACK
  export, Ruff check/format, strict root and explicit experiment Pyright, Vulture, root/mobile lock
  checks, installed Servatus API and mobile CLI smokes, residue/diff/status checks. Worktree clean.
- No canonical output, data, scratch, checkpoint, protected main-worktree dirt, remote system, GPU,
  GitHub, PyPI, corpus, dataset, or future Blockweaver plan was touched.

### Prerequisite Slice 3A: Servatus concurrent child workspaces

Status: complete and green; exact Servatus baseline
`f60335416b549fdc252c56152af2b9678e94bb72`; accepted head
`b8eb73f33d54a67efd9f192739223d8103877939`

Implementer: `/root/slice3a_child_workspace_impl`; sole writer in the Servatus `main` worktree.

Reviewer: `/root/slice3a_child_workspace_review`, with fresh parallel Standards and Spec lanes.

Reason:

- Slice 4's read-only mapping proved evaluation and artifact training fit one ordinary Workspace,
  but the planned nested Study composition does not preserve real HPO concurrency. Entering the
  parent takes its exclusive lock for the whole context, while KAIROS intentionally runs nine
  Methods for one Study in concurrent `4 + 4 + 1` allocations. Holding the parent during `_fit()`
  would reject or serialize sibling GPU work.
- KAIROS must not regain generic parent initialization, retry, lock, or scratch coordination. The
  missing concurrency lease belongs in Servatus because every application using concurrent private
  children before one final publication has the same lifecycle race.

Design evidence:

- Independent minimal-interface and adversarial audits converged on one additive method:
  `Workspace.child(name, identity=...) -> Workspace`. A child holds a shared parent lifecycle lease
  and its own exclusive lock; parent entry remains exclusive and nonblocking.
- A third design considered first-class `Parts`, `Assembly`, contribution registries, incomplete
  state, and lane leases. Those designs are valid but add a class, errors, registries, readiness-like
  state, and roughly 180--280 production lines for one known caller. Reject them until a second real
  need proves the one-method hierarchy insufficient.
- A deleted throwaway spawned-process prototype on macOS proved different-child overlap,
  duplicate-child exclusion, parent exclusion/retry, cleanup/open ordering, and 30 simultaneous
  first-initialization/finalization races. Negative controls proved that unlinking and recreating a
  lock pathname without stable-parent coordination permits two exclusive locks on different inodes.
  Blocking parent acquisition while holding coordination deadlocks and is forbidden.

Scope:

- Add only `Workspace.child(name, *, identity) -> Workspace`; `name` is one safe opaque leaf. Reuse
  existing errors and Workspace path/publish behavior. No new public class or readiness value.
- Child entry verifies the parent identity and canonical-destination absence under a short exclusive
  coordination flock on the pinned destination-parent directory, then holds the parent lifecycle
  lock shared and the child lock exclusive/nonblocking for the whole context. Lock order is stable
  parent coordination, parent lifecycle, child lifecycle.
- Different children overlap; duplicate child, child during parent finalization, or parent during an
  active child raises `WorkspaceBusy` immediately. A conflicting parent or child identity raises
  `WorkConflict`. A canonical parent destination prevents new child state.
- Child failure preserves only its resumable work. Child success atomically retains one immutable
  private result under parent work and cleans only its child workspace. Parent validation/build
  failure or destination collision preserves all child results/work. Parent success publishes the
  canonical object and then removes the complete private hierarchy.
- Harden Workspace open/cleanup around the removable lifecycle-lock inode: use the verified stable
  destination-parent directory descriptor as the short coordination lock; check finalized state;
  pin the active container; durably bind and verify the lifecycle lock and work inode inside the
  authentic owner-only container; never unlink or recreate lifecycle locks outside that choreography.
- Document the contract and prepare additive `0.3.0` metadata. Slurm, Campaign, publication formats,
  dependencies, and existing root Workspace semantics otherwise remain unchanged.

Non-goals:

- Expected-child lists, status, polling, waiting, automatic readiness, registries, `Parts` or
  `Assembly`, workflow topology, KAIROS Method knowledge, lock-mode flags, arbitrary relative child
  paths, multi-level recursion without a real caller, scheduler changes, corpus/dataset work,
  compatibility shims, or isolation from hostile/arbitrary mutation by the same Unix account that
  owns the private container.

Expected outcome:

> Independent children can resume and complete concurrently under one future immutable destination,
> while the application alone decides when and how their validated results become one canonical
> object.

Checks:

- Real spawned-process tests on Linux and macOS: simultaneous first sibling children overlap;
  duplicate child is busy; parent is busy during a child and succeeds afterward; child is busy
  during parent entry; identity mismatch; failed-child resume; parent validation failure preserves
  completed children; canonical destination blocks stale children; cleanup/open and
  cleanup/finalization barrier races admit only valid outcomes; replacement lock/work entries inside
  an authentic container fail before application entry; an active handle rejects container path
  replacement before publication or cleanup.
- Existing Workspace/file/directory/Campaign suites, Ruff check/format, strict Pyright, Vulture, lock
  check, wheel/sdist inspection, installed-wheel version/API/CLI smokes, clean fixed-range diff.
- After local green and separate authorization, one isolated CPU-only shared-scratch smoke should
  prove coherent shared/exclusive `flock` across distinct research-cluster nodes. No GPU smoke is
  needed because no Campaign, Slurm renderer, resource, image, or application hot path changes.

Dependencies and gates:

- The released `0.2.0` head is the exact implementation baseline. Use a fresh Servatus implementer
  and distinct two-lane reviewer; rejected findings return to the same workers.
- The user authorized push, annotated tag, GitHub Release, and PyPI `0.3.0` after green review.
- A cross-node shared-filesystem smoke is a site deployment gate rather than a package-release gate:
  `flock` coherence depends on the selected shared filesystem and mount configuration, while this
  release changes no scheduler or application execution code. KAIROS remote cutover remains blocked
  until the smoke passes; local adoption may proceed once `0.3.0` is reproducibly installable.

Recorded result:

- Initial implementation `c21c6fe62f9e4814591581b89693804e86458f2b`
  (`feature(workspace): add concurrent children`) added one public method, shared-parent/exclusive-
  child leases, stable-parent coordination, real spawned-process tests, ADR/docs, and `0.3.0`
  metadata with zero new dependencies.
- Review round 1 returned Standards 0 and one P1 Spec finding: replacing an active named lifecycle
  lock could give a later opener a different inode and bypass exclusion. Correction
  `97059b47c34b0a9d49b4e24ba8573a72cd135e0a`
  (`fix(workspace): pin lifecycle lock identity`) durably bound container, lock, and work pins and
  closed both root and child lock-replacement repros.
- Correction review then exposed that a trust record inside a wholesale replaced owner-only
  container cannot authenticate the old container to a fresh opener. The ledger and implementation
  now state the honest unprivileged boundary: the private owner-only container is the trust root;
  same-account arbitrary whole-root recreation is outside scope, while active-handle replacement and
  lock/work substitution inside an authentic container fail closed. Documentation correction
  `b8eb73f33d54a67efd9f192739223d8103877939` recorded that boundary without removing the prior fix.
- The same reviewer and lanes returned final `GREEN LIGHT`: Standards 0, Spec 0; both P1s closed
  within the explicit trust boundary. Accepted gates: 202 tests and one platform skip, repeated real
  process races, Ruff check/format, strict Pyright, Vulture, lock/diff checks, wheel/sdist inspection,
  and fresh Python 3.11 installed `0.3.0` API/CLI smokes. Worktree clean.
- An authorized read-only queue preflight found the user's existing jobs unchanged. Immediate
  two-node CPU acceptance request `44619` obtained no allocation and was cancelled by Slurm at zero
  runtime because nodes/QOS were unavailable; it left no queued job. Only a fresh isolated path
  `/scratch.hpc/edoardo.galli3/servatus-flock-0.3.0-b8eb73f` was created. The cross-node proof remains
  required before remote KAIROS cutover and must not be retried while current queue pressure remains.
- The reviewed head was pushed to public `main`; GitHub CI run `31397290192` passed on Ubuntu and
  macOS. Annotated tag `v0.3.0` points exactly to `b8eb73f`; tag CI run `31397359840` passed on both
  platforms. GitHub Release `https://github.com/edoski/servatus/releases/tag/v0.3.0` triggered
  Trusted Publishing run `31397445672`, which succeeded without a long-lived token.
- PyPI exposes `servatus==0.3.0` with provenance. Wheel SHA-256:
  `699535487fd1947fa00bb817ca066f66ee3e625424192df82d13cd37159c3bdb`; source archive SHA-256:
  `8e396b5d123b670f49acae136a5e27364a5ec80e7e28c110f3a8111ac46cc88c`. A fresh empty-cache index
  install returned `0.3.0`, exposed `Workspace.child`, and passed the installed CLI smoke.

### Slice 4: KAIROS resumable ML object lifecycle adoption

Status: complete and green; exact baseline `03e95e41486fcdafbb12d2f889759d77047e0df7`;
accepted head `7d31bcbaf9a61a69003f6fd7bfbb694fb041011e`

Implementer: `/root/slice4_kairos_workspace_impl`; sole writer in the run-owned worktree.

Reviewer: `/root/slice4_kairos_workspace_review`, with fresh parallel Standards and Spec lanes.

Scope:

- Replace evaluation, artifact, candidate-result, and Study hidden workspace/staging/rename/cleanup
  mechanics with ordinary and concurrent child Servatus Workspaces.
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

Recorded result:

- Initial implementation `8055724e629fd69e424af44432edd035dd15137f`
  (`refactor(lifecycle): adopt Servatus workspaces`) pinned `servatus==0.3.0`, moved evaluation and
  artifact training to ordinary Workspaces, moved candidates to concurrent child Workspaces, moved
  Study finalization to the exclusive parent, passed stable paths into `_fit`, and deleted local
  scratch/stage/rename/link/cleanup mechanics.
- Review round 1 rejected one P3 Standards and one P2 Spec finding. Two tests reconstructed Servatus
  child locks without exercising KAIROS; `publish_study` inspected trial 0 before acquiring parent
  exclusivity, so an active unpublished child raised `FileNotFoundError` instead of `WorkspaceBusy`.
- Correction `7d31bcbaf9a61a69003f6fd7bfbb694fb041011e`
  (`fix(lifecycle): lock study before inspection`) uses the known Study UUID as parent identity,
  acquires the exclusive parent before any child read, binds each indexed child to the exact full
  TuneRequest, deletes dependency-copy tests, and strengthens the production finalizer-busy test.
  The same reviewer and lanes returned `GREEN LIGHT`: Standards 0, Spec 0.
- Accepted gates: 23 focused and 113 full tests; real Lightning interruption/resume; reverse Study
  completion with exact order; Ruff check/format; configured and explicit touched-file Pyright;
  Vulture; lock/API/version/residue/diff/status checks. Worktree clean.
- No canonical output, data, scratch, checkpoint, corpus, dataset, protected main dirt, remote job,
  GPU, Slurm, Apptainer, or external system was touched.

### Slice 5: KAIROS campaign and experiment lifecycle adoption

Status: complete and green; exact baseline `6f2d4a2486f37216268d7ebf2f3984529f2f97c9`;
accepted head `b8afc22ff37640bcd72af2bba5098fae43c4bfb4`

Implementer: `/root/slice5_kairos_campaign_impl`; sole writer in the run-owned KAIROS worktree and
the Servatus prerequisite correction.

Reviewer: `/root/slice5_kairos_campaign_review`, with the same parallel Standards and Spec lanes
through both correction loops.

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

Recorded result:

- Initial implementation `efbfdc770fdce55176b2b954b38fe7a7dc4d156b`
  (`refactor(execution): adopt Servatus campaigns`) deleted `kairos.execution`, `jobs.tsv`, and
  `REMOTE.yaml`; added KAIROS-owned worker/task translation; moved packing, native submission,
  receipts, ambiguity, retry, and restart to Servatus; replaced the target with strict TOML
  profiles; retained cells, typed requests, completion probes, and manifest meaning in KAIROS; and
  preserved the exact production resource request and canonical output layout.
- Review round 1 returned Standards 0 and two Spec findings. The immutable Campaign roster broke the
  real prepare -> launch -> `hpo extend` -> relaunch flow, and Servatus had changed protected log
  semantics from job-ID/zero-based combined logs to allocation-ID/one-based split logs.
- The same implementer produced reviewed Servatus `0.4.0` candidate commits
  `836d6c857776f1bb638c176faf0447f4f10e348e` and
  `81ab533f6e680f457a4501cbff9b8c09a75a8c76`. Exact-prefix append-only Campaign growth preserves
  durable receipts, retry, ambiguity, and accepted-prefix skipping; durable state owns the roster
  across stale handles and submission races; `%j.out` and zero-based `%j-<slot>.out` combine both
  streams. The prerequisite correction review returned Standards 0 and Spec 0 after closing one
  stale-handle P1/P2 round.
- Authorized release `v0.4.0` completed from exact reviewed head `81ab533f`: main CI
  `31406203457`, tag CI `31406276870`, and Trusted Publishing `31406342319` passed. PyPI records
  owner `edoski`; wheel SHA-256 is
  `e26dd21451a87a12dfc961259534cc12da45ddf2ea6dc99ed465ae8431029af5` and sdist SHA-256 is
  `1d8f17a39a5e33a47b00daa69405c81c29bbff81da5538cf6c58b1529b64e196`.
- KAIROS correction `b8afc22ff37640bcd72af2bba5098fae43c4bfb4`
  (`fix(experiments): support HPO campaign extension`) pins the published artifacts. Its real
  author/launch integration accepts an ordered 27-task prefix, extends to 54, submits the 27-task
  suffix exactly once in seven allocations, retains all 54 receipt keys, and leaves zero pending.
  The same reviewer returned final `GREEN LIGHT`: Standards 0, Spec 0.
- Accepted KAIROS gates: 41 focused and 125 full tests; Ruff check/format; strict Pyright; Vulture;
  lock and offline frozen sync; installed Servatus API; CLI; dependency/source residue; exact diff
  and clean status. No compatibility or migration path was added.
- No canonical output, data, scratch, checkpoint, corpus, dataset, protected main dirt, remote job,
  queue, GPU, Slurm, SSH, Apptainer runtime, or deployment was touched.

### Slice 6: KAIROS clean-break documentation and integration gate

Status: complete and green; exact baseline `002335ee9c226ab410b7d025e3594366be5cf609`;
accepted head `f5391bbb5c157e2b94e08807c0dee5430c2bb5ad`

Implementer: `/root/slice6_kairos_docs_impl`; sole writer in the run-owned KAIROS worktree.

Reviewer: `/root/slice6_kairos_docs_review`, with fresh parallel Standards and Spec lanes.

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

Recorded result:

- Initial implementation `d92b37a46850f4dccad46570aa9321677f2f98c2`
  (`refactor(servatus): complete KAIROS integration`) added ADR 0008, superseded ADR 0007's local
  implementation ownership, narrowed ADR 0006 to KAIROS object authority plus Servatus mechanics,
  rewrote active execution/publication documentation, deleted two duplicated generic Servatus
  research notes, removed dependency-internal tests, and aligned the isolated mobile exporter on
  published `servatus==0.4.0`.
- Review round 1 returned Standards 0 and one Spec P1: pruning removed the only exact assertion of
  KAIROS's committed production target/resource profile. The same review found no removable wrapper,
  middle-man, or duplicated generic mechanism in the remaining launcher, worker, CLI, or bundle
  lines; those lines own KAIROS task meaning, canonical completion, user intent, and presentation.
- Correction `f5391bbb5c157e2b94e08807c0dee5430c2bb5ad` restores one public-parser config contract for ordered
  partitions, script and submit caps, exact one-task resources, and four-task ceilings without
  retesting Servatus planning or rendering. The same reviewer returned `GREEN LIGHT`: Standards 0,
  Spec 0.
- Accepted gates: 116 root tests, 9 mobile-export tests, 43 App tests; App typecheck; Ruff
  check/format; strict Pyright; Vulture; root/mobile locks and frozen syncs; npm dry install with
  package/lock hashes preserved; CLI/import/profile/canonical-layout/residue/diff/status checks.
- Physical production Python from planning baseline `56f24ae` is 4,222 -> 4,166 (`-56`): `src/`
  is `-92`, `experiments/` is `+43`, and mobile exporter production is `-7`. Tests are `+110` after
  retaining typed task, completion, extension, restart, retry, and profile integration contracts.
  Excluding this run's 1,752-line execution ledger, active documentation is approximately flat
  after removing 650 lines of duplicated generic research. The planning LOC estimate was too
  optimistic and was not used as a correctness target.
- No canonical output, data, scratch, checkpoint, corpus, dataset, protected main dirt, remote job,
  queue, GPU, Slurm, SSH, Apptainer runtime, device, or external deployment was touched.

### Slice 7: compact-CUDA reconciliation

Status: complete and green; extraction baseline `f193a223a1264213706fd08e4ce3e274e518802f`;
main-synced base `f00ef948fb670b3e86163e0dc6aa73e67594053c`; accepted compact head
`68262eb8b2de96adef4c27d25ed1acc8c8675970`

Implementer: `/root/slice7_compact_cuda_impl`; sole writer in the run-owned compact worktree.

Reviewer: `/root/slice7_compact_cuda_review`, with fresh parallel Standards and Spec lanes.

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

Recorded result:

- Main advanced after the extraction fork by one user commit,
  `274a4dd3ea7f5ae65e576de539f85ee29c6c3ba8` (`Restrict horizon study to selected LSTMs`). It was
  carried onto the green extraction as `f00ef948fb670b3e86163e0dc6aa73e67594053c`; range-diff and
  stable patch ID `c051d1ea` are exact.
- The pre-existing compact branch was reconciled non-destructively with merge commit
  `68262eb8b2de96adef4c27d25ed1acc8c8675970`. Its only nonmerge commits above the integrated base
  remain the original `32758207` and `3a1fe154`; no rebase, reset, force move, or branch deletion
  occurred.
- Conflicts were limited to modeling's Servatus work path versus CUDA loader setup and corresponding
  test imports. Resolution preserves Workspace/full-state resume and publication while retaining
  the approved `.to(device).loader(...)` historical batching path.
- Independent review returned `GREEN LIGHT`: Standards 0, Spec 0. Original and reconciled CUDA
  deltas have the same 10-file roster, per-file numstat, and all 249 added/deleted lines; only index
  hashes, hunk offsets, and integration context differ.
- Accepted gates: 32 CUDA-focused and 117 full root tests; 9 mobile-export tests including host
  XNNPACK; 43 App tests; Ruff check/format; strict Pyright; Vulture; root/mobile locks; App typecheck;
  npm dry install; CLI/import/topology/hunk/conflict/residue/diff/status checks.
- No real CUDA/GPU, image, Slurm, SSH, remote, output, data, checkpoint, corpus, dataset, device, or
  deployment claim or mutation was made. Those remain final external gates.

### Slice 8: KAIROS directory-publication parent permissions

Status: green; exact extraction baseline `01046b4b7f7f73177c2cb3d7d528c439c870dd77`

Trigger:

- Final-image A/B job `44718` completed both old and new synthetic GPU fits, then the new image
  failed during Study finalization. CephFS does not support native no-replace directory rename, so
  Servatus correctly selected its coherent-lock fallback and rejected the group-writable
  `studies/` parent.
- The exact cluster condition is deterministic: account umask `0002` plus KAIROS's default
  `Path.mkdir()` creates mode `0775`; Servatus directory fallback requires an owner-owned parent
  without group/other write. A fast local umask-`0002` repro produces the same mode and failure
  precondition.
- This is a KAIROS integration defect, not a reason to weaken Servatus. An ordinary directory
  rename inside a group-writable parent cannot preserve the package's no-clobber guarantee against
  a non-cooperating writer.

Scope:

- Request mode `0755` when KAIROS creates each direct parent used for directory publication:
  Studies, Artifacts, Evaluations, experiment manifests, inference-energy units, and mobile export.
  Experiment authoring must create the exact canonical experiment-kind parent explicitly; a
  recursive `requests/` mkdir otherwise leaves the intermediate parent at `0775`.
- Leave regular-file publication parents unchanged: Servatus's hard-link fallback already provides
  kernel-enforced create-if-absent semantics there.
- Keep Servatus `0.4.1`, every output path, file roster, schema, hard link, request, and scientific
  validation unchanged. Add no wrapper, compatibility path, storage initializer, chmod helper, or
  new configuration surface.
- Add lean umask-`0002` tests at the KAIROS caller seams. They prove newly created direct parents are
  `0755`; they do not retest Servatus fallback internals.

Cutover boundary:

- Explicit mkdir modes do not modify an already-existing `0775` directory. After all old jobs and
  old-layout closure work finish, the final cutover preflight may inspect only owner/mode metadata
  for exact known publication parents and remove group/other write from those exact directories.
- No recursive chmod, glob, output traversal, content read, copy, rewrite, inode/path change, or
  schema migration is allowed. If an exact parent is not owned by the KAIROS account or shared
  write is intentional, fail closed and choose a per-owner namespace rather than weakening
  Servatus. This is bounded permission preparation, not output migration.

Implementation-review loop:

- A fresh implementer changes only the KAIROS callers/tests/docs required above in the isolated
  extraction worktree. A distinct reviewer runs parallel Standards and Spec lanes against the
  exact fixed range. Findings return to the same workers until zero-finding `GREEN LIGHT`.
- After local green, reconcile the accepted extraction head into compact CUDA while proving its
  original ten-file CUDA delta remains patch-identical. Build a fresh exact-SHA image in new
  isolated paths; never overwrite `004f951` or `ade5827`.
- Re-run only the affected isolated CephFS publication and final KAIROS functional gates. The
  successful old/new compute evidence from `44718`/`44720` remains valid: request, epochs,
  objective, and metrics were identical; `116.63s` old versus `118.39s` new is ratio `1.015`.

Recorded result:

- The fresh implementer committed `0f70ead03359c94f2d5ab479c89c63becbc9b64c`
  (`fix(publication): create safe directory parents`). Seven direct directory-publication parent
  creators now request mode `0755`; regular-file publishers, paths, schemas, hard links, and
  scientific validation are unchanged. The same implementer closed one review finding in separate
  commit `223cfacf7f0a2eee02ebdbcea9f61555500d1c24` by restoring `bundle_path()` as the sole bundle
  address owner. The same independent reviewer returned `GREEN LIGHT`: Standards 0, Spec 0.
- Extraction gates passed: 109 root tests, 9 mobile-export tests including host XNNPACK, 43 App
  tests, Ruff check/format, strict Pyright, Vulture, root/mobile locks, App typecheck, npm dry
  install, and clean diff/status checks.
- Compact CUDA was reconciled without rewriting its history at
  `f49db0b712845632f6a5457159b628e635a00f9f`. Its only nonmerge CUDA commits remain `32758207` and
  `3a1fe154`; the ten-file roster, per-file numstat, and all 249 changed lines remain patch-identical.
  Independent review returned `GREEN LIGHT`: Standards 0, Spec 0. Gates passed: 110 root tests, 32
  CUDA-focused tests, 9 mobile-export tests, 43 App tests, and all static, lock, CLI, App, npm,
  topology, conflict, residue, and clean-status checks.
- Build job `44721` created and tested the exact clean `f49db0b` image at
  `/scratch.hpc/edoardo.galli3/deployments/kairos-cuda-f49db0b.sif` through `sbuild` with 8 CPUs,
  30 GiB, and one hour. The prior `004f951`, `9385753`, and `ade5827` images remain untouched.
- Exact-production-shape job `44722` requested 128 CPUs, 256 GiB, and four GPUs but never obtained a
  node. After the user authorized a smaller equivalent functional gate, it was cancelled while
  pending with zero elapsed time and no node. Replacement `44828` reduced CPU and memory to 8 CPUs
  and 32 GiB while retaining four GPUs; it proved the active constraint was four-GPU availability,
  not CPU or memory, and was likewise cancelled pending with zero elapsed time and no node.
- The user then authorized the minimal gate for the changed seam. Synthetic candidate job `44829`
  completed in 27 seconds with exact `cpu=2,mem=8G,gres/gpu=1`; CPU finalizer `44830` atomically
  published and strictly loaded Study `f45717de-df84-4c10-b203-083b4a80c6a3`. Synthetic
  `TrainRequest` job `44831` completed in 12 seconds with the same TRES; CPU validator `44832`
  strictly loaded Artifact `f70c4af8-323e-4d57-81b2-9a1415262c18`.
- Both changed directory parents are mode `0755`; each immutable Study/Artifact directory is mode
  `0700`. Validators proved exact canonical file rosters, one Study reduction row with finite
  metrics, one completed epoch, a loadable non-training LSTM Artifact, and request-bound identities.
  Servatus logs are exactly `%j.out` plus zero-based `%j-0.out` for both GPU jobs. Every path and
  output is under the isolated `kairos-f49db0b-small` acceptance namespace.
- The smaller final smoke is sufficient for Slice 8 because the reviewed delta changes only parent
  creation modes. Four-task concurrent launch, distinct GPU isolation, aggregate exit behavior,
  TRES arithmetic, and zero-based combined log rendering were already proven live before this
  correction and their source paths did not change. The prior same-GPU A/B remains the performance
  evidence; it showed equal requests, epochs, objectives, and metrics with new/old ratio `1.01509`.
- No thesis input, canonical production output, production scratch, existing science job, or
  independent automation was read or mutated. No production configuration, branch push/merge, or
  cleanup is part of this accepted slice.

### Slice 9: production target cutover

Status: green; exact baseline is the accepted Slice 8/acceptance head
`99b730b71ba3d9b79e7a2507e85b3bf519d03f62`

Expected outcome:

- Future KAIROS submissions use the accepted immutable `f49db0b` image. Already-submitted Slurm
  jobs remain bound to the scripts and old image path captured at submission.

Scope and non-goals:

- Change only the production image in `REMOTE.toml` to
  `/scratch.hpc/edoardo.galli3/deployments/kairos-cuda-f49db0b.sif`. `REMOTE.toml` remains the sole
  deployment-image authority; do not mirror its rotating image value in a test.
- Keep partitions, paths, resource requests, caps, scripts, outputs, schemas, and every application
  behavior unchanged. Do not rebuild the image: `REMOTE.toml` is workstation-side submission
  configuration and the accepted SIF already contains exact product SHA `f49db0b`.
- Preserve the old image and old lifecycle state while queued old-image jobs exist. Do not cancel,
  release, reprioritize, rewrite, or otherwise mutate those jobs.
- A fresh implementer commits the fixed slice; a distinct reviewer returns `GREEN LIGHT` only with
  Standards 0 and Spec 0. Then reconcile the accepted commit into compact CUDA with exact delta
  parity before branch publication.

Cutover permission preparation:

- Read-only exact-path preflight found only the core `studies` and `artifacts` parents present, both
  owner `edoardo.galli3`, device `49`, and mode `0775`; all other six inferred core parents were
  absent. Under the user's approval, nonrecursive `chmod go-w` changed only those two directory
  modes to `0755`. Revalidation proved their paths, owners, devices, and inodes
  (`1099895357882`, `1099906115439`) unchanged. No contents were listed or read.
- This metadata change cannot disrupt queued same-account jobs: owner `rwx` is unchanged. Absent
  parents will be created as `0755` by Slice 8. Benchmark-energy and mobile-export parents remain
  user-supplied and were not guessed or mutated.

Recorded result:

- Fresh implementer commit `9e7349abee2d25bc0f6cbe9ba06b41db51552c2a`
  (`config(remote): use accepted Servatus image`) changed the production image path and initially
  mirrored it in the production-profile test. Full root tests passed (`109`), with Ruff
  check/format, strict Pyright, Vulture, lock, and diff gates green.
- The first extraction review returned Standards 0 and Spec 0. Compact integration review then
  rejected the shared delta with two Standards findings: the exact-image assertion created
  configuration/test shotgun surgery, and the ledger still described already-granted cutover
  authority as pending. The same implementer removes the assertion; this ledger correction makes
  `REMOTE.toml` the single rotating image authority and narrows remaining gates to publication,
  merge, and cleanup. Resources, paths, caps, outputs, schemas, and runtime behavior remain
  unchanged. External refs remain untouched until correction re-review is green.
- Same-implementer correction `83cc092b145f12c8e4defa7fab9f76a4451c562e` removed only the
  mirrored assertion. The same compact reviewer returned `GREEN LIGHT`: Standards 0, Spec 0.
  Final Slice 9 product delta is exactly one `REMOTE.toml` image-line replacement; full root tests
  (`109`) and all focused/static/lock/diff gates remain green.

### Slice 10: selected-LSTM horizon contract alignment

Status: complete and green; accepted head
`76a1396a42bcfb0897bdf661a066bd030a0644d3`

- Exact baseline: `e894870a886cd0585b32aed93f39f832eb2005db`
- Initial implementation: `7660cf39241aebd50c651d9a02a4cf3183ccf310`

Trigger and expected outcome:

- Final main integration review found one P1 predating the merge: the intentional horizon-study
  restriction authors exactly three chain-LSTM cells across nine horizons, while its active manual
  still promised nine architecture-chain cells. The corrected K-study and held-out authoring
  contract owns 27 records; its rolling report selects the three chain-LSTM groups over `K=2..5`,
  for 12 records.
- The inference cost/time benchmark is a separate consumer contract. It takes explicit completed
  full-roster canonical manifests and requires nine manifest-derived chain-family groups over
  `K=2..5`, for 36 artifacts and evaluations.

Scope:

- Keep `experiments/k_study.py` and `held_out.py` manifest-driven behavior unchanged. Prove their
  exact ordered 27-label selected-LSTM authoring roster.
- In inference benchmark resolution, require exactly nine complete groups over
  `ROLLING_HORIZONS` without hard-coding chain or family names. Reject partial or surplus campaign
  rosters and evaluation-to-artifact mismatches before model loading.
- Use one realistic benchmark fixture with all three chains, all three model families, four rolling
  horizons, and the five nonrolling horizon labels. Prove 36 protocol labels while retaining the
  separate 27-label authoring proof. Do not duplicate reducer, loader, or publisher tests.
- Align active `docs/KAIROS.md` with the selected-LSTM author and rolling-report contract. Preserve
  the inference-benchmark planning contract at nine groups/36 records and document its distinct
  full-roster manifest source boundary.
- HPO remains nine architecture-chain Studies with 81 Method rows; that upstream contract is not
  the horizon roster and must not change. No scientific outputs, schemas, IDs, resources, remote
  state, user-owned main dirt, or queued jobs may be touched.

Readiness:

- The narrowed K-study author cannot generate the other 24 rolling benchmark models. Before the
  inference campaign, verify the explicit completed full-roster K-study/held-out manifest pair and
  its canonical objects. If that pair is unavailable or incompatible, separately scope a dedicated
  benchmark-input author; do not widen the horizon-sensitivity author implicitly.
- Implementer gates at `7660cf39241aebd50c651d9a02a4cf3183ccf310`: 16 focused tests and 109
  full root tests passed; repository Ruff check/format, configured and explicit experiment
  Pyright, Vulture, root/mobile lock checks, and diff/status hygiene were green.

Implementation-review loop:

- Initial independent review returned Standards green and one Spec finding: this ledger still
  collapsed the benchmark to the selected-LSTM roster. The same implementer corrected only this
  record at `76a1396a42bcfb0897bdf661a066bd030a0644d3`. The same reviewer returned `GREEN LIGHT`:
  Standards 0, Spec 0.

### Slice 11: final campaign path and production CPU profile

Status: complete and green; extraction, main, and compact final reviews green; product refs
published; protected user work restored; closing ledger-only work follows the final choreography
recorded below

- Exact baseline: `76a1396a42bcfb0897bdf661a066bd030a0644d3`.
- Initial implementation `44d9c7c89d137685cb38d1b866773370951f34c7` changed the campaign path and
  production CPU profile. Independent review returned one Spec P2: two KAIROS bundle fixtures knew
  Servatus's private `state.json` filename.
- Correction `8840c049ab5ecb7c31d812631fa71833e0571660` replaced that private coupling with
  opaque campaign-state sentinels. The same reviewer returned `GREEN LIGHT`: Standards 0, Spec 0.
- Compact merge `cb86c3c9` contains correction `8840c049` as its exact second parent. Later
  ledger-only correction `0cc4ab1` was merged into compact at
  `1a5dea51542e264fcea0e73e801c3a645d7f42e3`, with parents `cb86c3c9` and `0cc4ab1` and zero
  product or resolution delta. Subsequent ledger-only correction syncs preserve that zero-product
  delta. Compact inherited all accepted extraction corrections; its final same-reviewer review at
  `3f1926f4073b9f8febe81a347d8e381e1142a7c1` returned `GREEN LIGHT`: Standards 0, Spec 0.
- Final extraction, local-main integration, and compact-CUDA reviews all returned `GREEN LIGHT`
  with Standards 0 and Spec 0. Accepted main
  `e7b703509e40b03de317d5f9b80c7b3a913b92c8` and compact-CUDA
  `bea658d51068615a407229c23405a7f34d2d3010` were atomically normal-fast-forwarded to both
  `origin` and `research`; no force push was used. These are the published product refs. Any later
  docs-only completion commits receive final review and normal fast-forward publication before
  handoff.
- User stash `98047c1edb3425506d561ba8f4fc56238337741e` was applied after publication. The sole
  `docs/KAIROS.md` conflict was resolved by retaining both the accepted Servatus semantics and the
  user's K-study figure changes. All eight nonoverlapping protected-file hashes matched their
  pre-cutover values; all nine user-owned paths remain deliberately modified or untracked. The
  exact stash was then dropped.
- New KAIROS experiment bundles store their Servatus campaign at `.servatus/`. This is a clean
  break: there is no alias, fallback, migration, or parser for `.servatus-campaign/` or
  `jobs.tsv`.
- The active old-layout HPO bundle `dfd33e91-702e-46c5-8cb1-3c510af4c048` must finish, finalize,
  and close entirely through image `004f951` and its existing `jobs.tsv` lifecycle. The first
  Servatus campaign is the next new K-study artifact bundle. The old image and lifecycle state
  remain preserved until that bundle is closed.
- The production resource profile now requests 24 CPUs, 65536 MiB, one GPU, and three days per
  task. Four packed tasks request 96 CPUs. The 24-CPU choice preserves headroom for the current
  four-worker DataLoader while crossing the observed scheduling threshold that prevented a
  128-CPU four-pack from fitting a node with 104 CPUs free. The target ceilings remain four tasks,
  128 CPUs, 262144 MiB, four GPUs, and three days per allocation; every other target and resource
  value remains unchanged.
- Servatus receipts prove scheduler acceptance, not scientific completion. KAIROS continues to
  derive completion from canonical Study, artifact, or evaluation evidence, and retries remain
  explicit task keys. Queue awareness and the one-free-QOS-slot policy remain external operator or
  heartbeat concerns; they do not enter Servatus.
- TDD proved the profile and campaign-path changes through the public Servatus parsers and KAIROS
  experiment seams. Seventeen focused and 109 full tests passed. Ruff check/format, configured
  Pyright, Vulture, root and mobile lock/frozen-sync checks, both CLI help paths, source residue,
  diff, and status gates passed.
- Prior extraction, acceptance, and cutover-check worktrees and the local temporary root were
  removed. The lifecycle-scoped `/private/tmp/kairos-servatus-final-compact` review worktree is
  intentionally excluded: final choreography retains it through completion-record correction
  review and publication, then removes it before handoff. After owner and inode validation, the
  exact run-owned roots carrying `f49db0b`, `ade5827`, and `9385753` under remote `build`, `cache`,
  `acceptance`, and `logs` were permanently removed. Deployment images `004f951`, `9385753`,
  `ade5827`, and `f49db0b` remain preserved.
- The production `studies` and `artifacts` publication parents retain their owner and inode and are
  now mode `0755`; only group/other write permission was removed. No thesis output, active or
  queued job, queue state, production object content, or old campaign state was changed.

### Consolidation planning pass

Status: planning GREEN; product implementation awaits explicit approval

Immutable planning state:

- KAIROS `main` is clean at `c0021cb99fa1c28295059a1cc827d6d68afca633`, two local user commits
  ahead of published `origin/main`: `7cca6fcb` and `c0021cb9`. Its only worktree is the pre-existing
  main checkout. Pre-existing `codex/compact-cuda-execution` remains outside run ownership.
- Servatus `main` is clean at `2ccf749e2a4c3f5ad7ca572ee34fe78e5b1bb78f`, exactly public
  release `v0.4.1`, with one pre-existing main worktree.
- Planning may update only this ledger. It creates no branch or worktree and contacts no Slurm,
  SSH, Apptainer, output, dataset, campaign, or external publication surface.

Execution checkout and review policy:

- Planning ends with one ledger-only KAIROS commit. Product implementation does not begin until the
  user approves this plan.
- On approval, create one recorded run-owned Servatus integration branch/worktree from exact
  `2ccf749e` and one recorded run-owned KAIROS integration branch/worktree from the accepted
  planning head. Leave both existing main worktrees and the pre-existing compact-CUDA branch
  untouched until reviewed final integration. Record paths, branches, refs, and clean status.
- Each slice starts from the exact clean prior accepted head. A fresh implementer must read and use
  the `implement` skill, commit only its slice, report its SHA/checks, and never edit this ledger or
  self-review. The orchestrator verifies the repository range before review.
- A distinct fresh reviewer must read and use the `code-review` skill against the fixed baseline and
  head, run Standards and Spec as separate axes, and return GREEN only with zero findings on both.
  Rejections return to the same implementer; correction deltas return to the same reviewer until
  GREEN. Only then may the ledger advance and the next baseline be recorded.
- No push, release, PyPI publication, image build, Slurm job, production configuration change, or
  destructive cleanup follows from this plan. Each external gate requires its stated later
  authority. Remove only run-owned branches/worktrees/evidence after their commits are integrated;
  preserve every pre-existing ref and checkout.

Governing outcome:

- Servatus should own as much reusable ML/GPU-project execution, runtime, durable-state,
  filesystem, publication, retirement, cleanup, retry, and reconciliation mechanics as can form a
  deep generic module. KAIROS should retain only task meaning, scientific completion, typed
  requests and associations, canonical paths and schemas, manifests, metrics, model/checkpoint
  meaning, and project/site policy.
- KAIROS must use only a small public Servatus interface. It must not know or test private Servatus
  state filenames, schemas, locks, stages, transport helpers, cleanup implementation, or other
  incidental details.
- The consolidation should make both repositories leaner, simpler, easier to read, and more local.
  Moving a line without hiding reusable complexity fails the deletion test; convenience wrappers,
  plugin seams, DAG/HPO abstractions, and one-off KAIROS concepts are non-goals.
- Servatus remains strict at raw configuration, serialized state, filesystem, subprocess,
  scheduler-receipt, ownership, symlink, inode, locking, no-clobber, durability, and concurrency
  seams. Repeated validation of already-typed or already-validated internal values is a candidate
  for removal only when the same failure remains caught at its owning seam.
- Research must evaluate successful-publication retirement and every other credible generic
  lifecycle leak in KAIROS, then audit all Servatus modules, public exports, CLI, tests, docs, and
  defensive checks for consolidation. The final plan will reject speculative extraction and state
  exact supported changes, ordered slices, checks, non-goals, release dependencies, and external
  gates.

Expected outcome:

One reviewed implementation plan identifies the smallest deep Servatus interface that owns all
supported generic mechanics, leaves a straightforward KAIROS client containing only application
meaning, removes private coupling and duplicate tests, and preserves every canonical output path,
schema, scientific association, GPU execution behavior, and failure-safety guarantee. Planning
alone makes no product or external change.

#### Consolidation audit decision

The whole-repository deletion audit found one remaining generic production leak in KAIROS.
`publish_bundle()` commits the canonical manifest through Servatus and then calls raw
`shutil.rmtree()` on the authored sibling bundle. KAIROS therefore still owns commit/cleanup
ordering, exact cleanup-target binding, cleanup durability, and the distinction between committed
success and post-commit residue. Cleanup can currently raise after the manifest is already durable.

Servatus will deepen the existing directory-publication transaction with one keyword-only option:

```python
publication = publish(canonical, assemble, retire=bundle)
```

`retire` accepts one existing, distinct, owner-only directory whose parent is exactly the
destination parent. Servatus pins the parent and source inode before invoking the builder, leaves
the source untouched on every precommit failure, commits and syncs the destination first, removes
only the pinned tree descriptor-relatively, and syncs the parent again. A missing, moved,
substituted, unsafe, or unremovable source after commit never changes committed success into
failure: `Publication.cleanup_pending` is true and Servatus emits one nonfatal cleanup warning.
The structured result remains available to callers. The source must be quiescent before the
transaction; this operation is not a writer lease or a recursive-delete callback.

This seam passes the deletion test: without it, every client with retained authored state must
reimplement safe tree pinning, commit-first ordering, durable removal, race handling, and
post-commit outcome reporting. It is narrower than an arbitrary callback and keeps application
meaning out of Servatus.

Re-homing the whole authored experiment bundle into `Workspace.path` is rejected. That would force
prepare, HPO extension, launch, monitoring, load, and close commands through another long-lived
lease; replace the current operator-addressed bundle with a hashed private path; and couple nested
Campaign access to Workspace choreography. It adds client code to solve a quiescence condition the
operator already owns. `Campaign.close()` is also rejected: a scheduler receipt proves acceptance,
not scientific completion, and Campaign cannot decide which canonical records or manifest make an
experiment complete.

No other generic production implementation remains in KAIROS. The audit found no KAIROS-owned SSH,
Slurm rendering, packing, lock, journal, staging, rename, hard-link, fsync, retry-state,
reconciliation, or no-clobber algorithm. The following remain application meaning and policy:

- `cells.tsv`, typed request files, cell labels, HPO append rules, and manifest schemas;
- canonical Study, Artifact, and Evaluation completion and scientific validation;
- Task keys, opaque payload bytes, worker commands, explicit retry-key selection, and receipt
  presentation;
- `last.ckpt`, Method order, objective/checkpoint association, metrics, benchmark protocols, and
  scientific resume rules;
- canonical namespace creation, one-GPU policy, two-to-four packing choice, resource values, image,
  partitions, and external queue/QOS policy.

Servatus must not gain a generic Bundle, experiment tracker, finalizer protocol, DAG, HPO model,
completion callback, scheduler adapter/plugin system, queue monitor, automatic retry, `run()`
facade, parent-directory creator, or compatibility parser. These would enlarge the surface without
hiding reusable complexity.

The audit also found a real existing Servatus safety defect: Workspace documentation names its
hidden container as an owner-only trust root, but current open paths accept pre-existing permissive
container/work directories and permissive lock/identity files. That contract must be enforced
before adding functionality.

#### Consolidation slice C1A: Workspace trust-root correction

Baseline: Servatus `2ccf749e2a4c3f5ad7ca572ee34fe78e5b1bb78f` (`v0.4.1`).

Scope:

- Require every existing Workspace container, work directory, lifecycle lock, and identity file to
  belong to the effective user and expose no group/world permissions. Reverify those properties at
  the existing pinned-entry boundaries.
- Compare a newly created directory entry with the descriptor opened for it instead of replacing
  the first stat record without comparison.
- Replace the current check-then-`shutil.rmtree()` cleanup with descriptor-rooted recursive removal:
  hold the verified source directory descriptor, inspect/open every child without following links,
  remove only entries reached through those descriptors, reverify each parent/name binding, and
  reverify the root binding before final `rmdir`. A renamed or substituted root must survive. This
  exact primitive becomes the later retirement foundation.
- Persist a newly initialized container in its parent and sync its new internal entries before
  committing identity. Do not change the existing identity schema in this correction slice.
- Keep native no-replace, the accepted Linux file-link and coherently locked directory fallbacks,
  descriptor-relative access, symlink/special-file rejection, cross-device rejection, inode-pinned
  cleanup, child/root locks, and callback revalidation unchanged.
- Update Servatus CONTEXT, README, SECURITY, and ADRs 0002/0004 so the implemented trust-root and
  durability contract is stated once and consistently.

Tests and review:

- Red tests for permissive or foreign container, work, lock, and identity entries; created/opened
  directory substitution; root and nested cleanup substitution; parent/container sync order; and
  existing root/child races.
- Retain distinct race, replacement, hard-link, no-clobber, cleanup-pending, fallback, and macOS /
  Linux process tests. Delete only exact duplicated probes.
- Full Servatus pytest, Ruff check/format, strict Pyright, Vulture, lock/build/archive inspection,
  fresh-wheel API/CLI smoke, then fixed-range Standards and Spec review.

Expected outcome:

Workspace's documented trust root becomes true and first-creation durability plus exact cleanup are
proven before any consolidation. No public API, private schema, or KAIROS behavior changes in this
slice.

#### Consolidation slice C1B: Workspace and POSIX consolidation

Baseline: exact clean C1A GREEN head.

Scope:

- Introduce the clean Workspace identity format that stores only the three authoritative inode
  pins. Stored device numbers are currently parsed and then deliberately ignored because client
  device identities may differ; live local device/type checks remain.
- Once a durable identity exists, stop syncing its unchanged container on every reopen.
- Remove only the parent sync performed immediately after `make_unique_stage()` and
  `make_unique_file_stage()`; those names are disposable before commit. Retain content sync before
  commit and publication-parent sync after commit.
- Remove only `sorted()` from recursive sync, the second descriptor type/fstat checks inside
  `_ensure_open_entry` after type/device/identity were already established on open, and named
  `_workspace._cleanup_workspace` forwarding wrapper. Keep `_build_draft`, `sync_descriptor`, and
  pathname-to-expected-inode verification; C2 separately owns `_slurm.validate_allocation`.
- Consolidate the associated identity/sync prose in CONTEXT, README, SECURITY, and ADR 0002. Do not
  remove the production Linux locked-directory fallback or weaken its coherent-flock contract.

Tests and review:

- Identity format bounds/canonical bytes, first initialization, reopen without redundant sync,
  disposable-stage crash semantics, file/tree durability ordering, and existing native/fallback
  behavior.
- Keep distinct syscall failure/race/substitution contracts; delete only tests whose observable
  guarantee is already proved through the same public path.
- Full Servatus package/build/install gates and independent fixed-range review.

Expected outcome:

Workspace retains every accepted safety property with a smaller private record, fewer repeated
metadata syscalls, and fewer implementation-specific tests. No public API changes.

#### Consolidation slice C2: Campaign state and codec consolidation

Baseline: exact clean C1B GREEN head. Uses a clean-break Campaign/plan schema; no legacy parser is
added.

Scope:

- Keep `Task`, `ResourceRequest`, and `SlurmTarget` constructors as the sole typed value validators.
  TOML readers retain exact raw document/key checks and delegate values once.
- Parse only the plan fields required to regenerate an immutable plan, regenerate it once through
  Campaign, and compare canonical JSON bytes. This replaces derived allocation/target/resource
  validation and still rejects bool-as-int and every changed derived field.
- Thin durable intent/receipt/resolution records: remove redundant `argv_digest`, per-intent target
  and resource digests, derivable job names, receipt task-key copies, and `accepted: false` wrappers.
  Keep lineage, plan/script digests, exact argv, allocation totals, query windows, and intent order.
- Validate every bounded owner-only durable-state ingress. Stop running the complete decoder again
  immediately before writing an already-validated snapshot mutated through typed internal paths.
- Add the missing invariant that one allocation cannot be both accepted and explicitly resolved as
  not submitted.
- Remove the now-redundant Slurm validation wrapper, dead remote-path helper, extra allocation argv
  digest check, and exact duplicate mutation/GRES tests.
- Update Servatus CONTEXT, README, and ADR 0003 for the thinned private records and unchanged
  acceptance/ambiguity authority.

Tests and review:

- Canonical schema, corrupt/truncated/oversized state, receipt/resolution contradiction, task-prefix,
  revision, lineage, ambiguity, retry, intent-before-SSH, receipt-after-acceptance, crash boundary,
  and concurrent opener tests remain.
- Reduce derived-plan mutation cases to raw consumed-field type cases plus one canonical derived
  tamper that proves regeneration comparison.
- Run the full Servatus package/build/install gates and independent fixed-range review.

Expected outcome:

Campaign keeps the same acceptance, ambiguity, retry, reconciliation, and resource-lineage
guarantees while deleting roughly 110-140 lines of duplicate decoding and persisted derivations.
State remains one simple atomic snapshot; no event log, database, validation framework, or backend
abstraction is introduced.

#### Consolidation slice C3: Campaign public interface and CLI

Baseline: exact clean C2 GREEN head.

Scope:

- Rename private `Campaign._reopen(path)` to public `Campaign.load(path)`. Opening registers an
  exact task roster; loading operates on an existing durable roster.
- Add `Campaign.validate(plan)` with one small immutable public validation-result type. The method
  verifies campaign/plan authority and runs bounded Slurm `--test-only` validation. The CLI stops
  importing a private function and private result.
- Rename `CampaignStatus.pending_task_keys` to `unaccepted_task_keys`. The value means tasks without
  a proven scheduler-acceptance receipt, never incomplete application work.
- Remove the redundant `target` argument from `Campaign.reconcile()`: immutable validated lineage
  is its authority. The CLI drops `reconcile --target`.
- Add repeatable `plan --completed TASK_KEY` and `--retry TASK_KEY` flags so CLI and typed API expose
  the same explicit lifecycle controls. CLI/API parity is a supported Servatus goal, not a KAIROS
  requirement; this small addition must not delay the preceding filesystem/state corrections.
- Resolve relative `stdin_file` paths against the task JSONL parent.
- Replace the CLI's hand-written temporary/fsync/replace plan writer with owner-only
  `publish_file()`. Plan output becomes immutable/no-clobber; no `--force` or overwrite helper is
  added.
- Trim duplicated syscall/acceptance prose from README while retaining quick starts, resource and
  target configuration, security boundary, and actionable exceptions. ADRs retain design detail.
- Update CONTEXT and ADR 0003 for load/validate/reconcile/status terminology.

Tests and review:

- Public Python and installed-wheel smokes cover load, validate, status meaning, reconcile from
  lineage, explicit completed/retry selection, immutable plan output, and relative payload paths.
- CLI JSON and help use `unaccepted_task_keys`; docs say receipts prove acceptance only.
- Full Servatus gates and independent review.

Expected outcome:

Servatus's Python API and CLI express one consistent lifecycle without private crossings,
redundant target input, misleading completion language, or a second filesystem transaction.

#### Consolidation slice C4: publication preflight and retained-tree retirement

Baseline: exact clean C3 GREEN head.

Scope:

- Before invoking `publish()` or `publish_file()` callbacks, inspect the pinned destination parent
  and reject an existing destination. Commit-time no-replace remains authoritative against races.
- Add only `publish(destination, build, *, retire: Path | None = None)`. Retirement is limited to
  one existing distinct owner-only destination sibling and uses the exact contract recorded above.
- Centralize public publication-result construction. Every committed publication with residual
  stage, Workspace, or retirement cleanup emits one nonfatal `RuntimeWarning` without mutating the
  process warning filters or converting warnings-as-errors into apparent commit failure. Preserve
  `Publication.cleanup_pending` as the authoritative result. Warning delivery is best-effort and
  no warning filter or custom hook may escape after commit.
- Reuse C1A's descriptor-rooted exact tree removal and existing transaction outcomes. Do not expose
  a cleanup callback, public cleanup token, retry registry, garbage collector, or second close
  operation.
- Update package version and lock to `0.5.0`; update CONTEXT, README, SECURITY, and ADR 0002 for the
  reviewed release contract. Inspect generated artifacts in this slice, but do not publish them.

Tests and review:

- Callback is not entered for an existing destination; destination races still never overwrite.
- Retirement success, builder failure, commit failure, collision, source/destination mismatch,
  unsafe permissions, symlink/special source, source substitution, cleanup failure, parent-sync
  failure, warnings-as-errors, and exact canonical success are covered through public APIs.
- Existing native/fallback/file/directory/Workspace suites remain proportionate; do not duplicate
  every syscall matrix for the new option.
- Full Servatus gates and independent fixed-range review.

Expected outcome:

One reviewed `0.5.0` source tree owns absent-or-complete commit, early collision rejection, safe
post-commit retirement, durability, and truthful residual-cleanup reporting. Servatus should be
judged by the deletion test rather than a forced total-line target: Campaign/Workspace duplication
is deleted, while any bounded POSIX growth must correspond to the newly proven trust-root and
retirement contracts. The final measured source delta is recorded after review; safety is not
weakened to obtain a net-negative count.

#### External gate: Servatus 0.5.0

After C1A-C4 are independently GREEN, request explicit authority to push Servatus, create/tag the
GitHub `v0.5.0` release, and publish PyPI `servatus==0.5.0`. Inspect wheel/sdist contents, metadata,
zero runtime dependencies, installed API/CLI, and published hashes before KAIROS pins it. The minor
version is a deliberate pre-1.0 clean break: Campaign/plan/Workspace private schemas, status field,
reconcile signature, and CLI plan behavior change without compatibility aliases.

No existing canonical KAIROS output needs migration. Old images and active old-layout campaign/work
state remain on their old code until closed. New Servatus code must not open the active HPO bundle
or its scratch, Campaign, jobs, or outputs.

#### Post-release source audit S1: Servatus owned-seam deletion

Status: user-approved for local implementation and independent review. Because S2 is also approved
and changes a documented behavior contract, S1 and S2 prepare one clean `0.6.0` candidate rather
than an intermediate `0.5.1`. Publication remains a separate external gate.

Baseline: exact reviewed and published Servatus 0.5.0 head
`79ee407c431d1f9c0510e9462d5136fa7b58319d`.

Scope:

- Remove runtime `isinstance` checks on the typed public `Task`, `SlurmTarget`,
  `ResourceRequest`, and Campaign-produced `SubmissionPlan` interface. Raw JSON/TOML/state ingress
  retains exact validation; deliberately passing arbitrary `object()` values is not a supported
  runtime contract.
- Validate durable Campaign collection shapes once at the top-level raw-state ingress and pass
  typed collections to subordinate validators. Delete the repeated list checks. Keep task parsing,
  digest/uniqueness, lineage, allocation provenance, receipt/resolution referential integrity, and
  accepted-versus-resolved contradiction checks.
- Let exact canonical allocation-argv equality own nonempty/string/NUL-free provenance instead of
  checking those properties immediately before the equality check.
- Trust kernel facts established by `O_CREAT|O_EXCL`, an already-held descriptor, `O_DIRECTORY`,
  and inode identity. Delete impossible fresh-stage type/device branches, repeated descriptor
  type/device/identity checks, and type predicates already implied by the pinned inode. Keep every
  pathname-to-inode check around callbacks, sync, commit, and cleanup.
- Remove repeated platform/leaf validation from the private no-replace commit helper after its only
  callers have validated those values at their owning seam.
- Pin retirement at the atomic directory open, then verify owner-only metadata and the pathname to
  the opened inode. Delete the preliminary path stat because no prior inode is part of the public
  interface.
- Remove the CLI fallback made unreachable by argparse's required fixed subcommands.

Tests and review:

- Delete contrived tests that pass arbitrary untyped objects to typed public methods or monkeypatch
  kernel-created regular stages into impossible file kinds. Do not replace deleted implementation
  probes with new probes.
- Retain raw durable-state corruption, bool-versus-int, real substitution/symlink/mount,
  no-clobber, durability-order, cleanup-residue, fallback, scheduler-response, and lineage tests.
- Require the full Servatus package/static/build/install gates and independent fixed-range
  Standards/Spec review. A release and KAIROS repin remain separate external gates.

Expected outcome:

Servatus loses roughly 45-60 source lines and the corresponding nonsense tests without changing
its public interface, accepted filesystem threat model, durable-state contract, scheduler
behavior, or KAIROS ownership seam. Each retained check has one owning raw/racy boundary.

Implementation and review record:

- S1 implementation `0f2547f2259156f4722698d92090ded980133a6b` is one clean commit from exact
  0.5.0 baseline `79ee407c`. Product source is `+16/-74`, net 58 lines smaller; tests delete 15
  lines. Independent fixed-range review returned GREEN with Standards 0 and Spec 0. The reviewer
  confirmed every raw-state, lineage, scheduler, pathname/inode, mutable-permission, cross-device,
  no-clobber, durability, cleanup-residue, and cleanup-pin contract remains. Gates passed 284 tests
  with one environmental skip plus Ruff, formatting, strict Pyright, Vulture, lock, build/archive,
  metadata/zero-dependency, fresh-wheel public API/CLI, and file/directory publication smokes. S2
  starts from exact accepted `0f2547f`.

#### Post-release source audit S2: quiescent-source linearization

Status: user-approved for local implementation and independent review after S1 GREEN.

Candidate scope:

- Simplify `Draft.link()` so the atomic hard link, not a preliminary source stat/open, selects the
  source inode. The linked draft entry is then inspected and rejected/removed unless it is a safe
  regular file. This changes the contract from “the pathname still denotes the inode observed at
  method entry” to “link the safe inode denoted at the kernel link linearization point.”
- Remove file/tree size and modification-time comparisons around `fsync`. Those checks detect only
  some concurrent writers and cannot prevent a write immediately afterward. The simpler contract
  requires the trusted builder to be quiescent before returning and retains pathname/inode checks,
  content sync, commit, and parent durability.

Expected outcome if later approved:

Roughly 25-40 more source lines and two misleading partial-concurrency concepts disappear. This is
not a mechanical cleanup: it deliberately narrows the same-account threat model and must be
decided, documented, implemented, and reviewed separately from S1.

Approved decision: the atomic hard-link operation is the source-inode linearization point, and a
trusted builder must stop mutating draft inputs before returning. Servatus continues to reject
unsafe linked entries, verify pathname/inode identity, sync published contents, commit without
clobber, and sync the publication parent. S2 updates package/docs/lock to `0.6.0`; build and inspect
artifacts locally, but do not push, tag, release, publish, or repin KAIROS until separately
authorized.

Portable-contract correction after first review: POSIX `link`/`linkat` returns only success or
failure, not the selected inode or a descriptor, and `unlink`/`unlinkat` cannot condition removal on
an expected inode. Therefore Servatus cannot both select the inode at pathname-link linearization
and defend portably on macOS/Linux against a hostile same-account process replacing that private
draft leaf after the link. The approved lean contract treats the owner-only draft namespace as
trusted and quiescent during synchronous `Draft.link()`. Concurrent mutation of the draft leaf is
out of contract; source replacement before the atomic link may be selected if the resulting entry
is safe. Do not add Linux-only descriptor-link machinery or restore pre-open source linearization.
Ordinary post-link inspection or validation failure must remove the just-created link before
returning so a caught failure cannot leave publishable residue. Under the quiescent namespace this
cleanup targets that created entry. Retain the final regular-file check and all commit/durability
contracts; remove the redundant post-success device check because hard-link success already proves
same filesystem. The same implementer/reviewer pair owns correction and rereview against this
revised contract.

The still larger proposal to delete regular-file cleanup hard-link pinning is rejected for this
run. It can save another roughly 35-40 lines, but it weakens exact cleanup-target retention for a
small internal simplification and deserves a concrete production need or failure model before the
accepted safety contract is reopened.

Implementation and review record:

- Initial S2 implementation `b18c13158609ab49e28c7b5af718d29d8157a09a` was rejected after
  review reproduced two races under the original too-strong wording: post-link replacement could
  be accepted, and check-then-unlink could remove a replacement. Portable POSIX cannot return the
  inode selected by pathname `link` or condition `unlink` on an expected inode. The user accepted
  the revised trusted/quiescent private-draft contract above instead of nonportable machinery or
  restored pre-open source linearization.
- Correction `efde60c563d96a0f710abcf3f0825014391f3ed7` documented the boundary, removed the
  redundant post-link device check, and cleaned ordinary rejected links. Rereview found one P1:
  inspection plus cleanup failure could leave residue that a builder caught and later published;
  it also found dead private device callback plumbing and an over-specific private test.
- Final correction `281c381548489c1dcf7a6ca8d045908d0b50ba3f` adds one narrow private poison only when
  rejected-link cleanup cannot be proven, checks it after the builder callback and aborts before
  sync/commit, removes the dead callback argument, and replaces the private probe with one public
  caught-error/no-destination regression. Fully cleaned rejection remains catchable; the source is
  untouched; transaction cleanup and the regular-file cleanup pin remain.
- The same reviewer returned final GREEN LIGHT with Standards 0 and Spec 0. Cumulative S2 product
  source is net 18 lines smaller; the combined S1+S2 candidate is version 0.6.0. Final gates passed
  289 tests with one environmental skip plus Ruff, formatting, strict Pyright, Vulture, lock,
  build/archive/version/zero-dependency inspection, and fresh-wheel public API/CLI/file/tree/link/
  Workspace smokes. Exact accepted candidate head is `281c381548489c1dcf7a6ca8d045908d0b50ba3f`.
  No push, tag, release, PyPI publication, or KAIROS repin is authorized by local acceptance; those
  remain the next external gate.

External release record:

- The user authorized the Servatus 0.6.0 external gate. Servatus `main` was fast-forwarded and
  pushed to exact accepted head `281c381548489c1dcf7a6ca8d045908d0b50ba3f`. Branch CI run
  `31597737876` and annotated-tag CI run `31597794856` passed on Ubuntu and macOS. Annotated tag
  `v0.6.0` dereferences to that exact commit; the public GitHub Release is
  `https://github.com/edoski/servatus/releases/tag/v0.6.0`.
- Trusted-publishing run `31597843846` succeeded. PyPI published wheel
  `servatus-0.6.0-py3-none-any.whl` with SHA-256
  `d1770b961bf14e9afeed731d4cee55a4eff09238db33ebaa1a5cdc32627c638f` and sdist
  `servatus-0.6.0.tar.gz` with SHA-256
  `16c99b3c10a62d63064a98ac78e665a821fea418f52fc9bab7a1c173a0e7b457`. A fresh no-cache
  public-index install verified version 0.6.0, zero runtime dependencies, public API/CLI, atomic
  hard-link publication, output bytes, and cleanup status. An initial smoke compared unresolved
  `/tmp` with canonical `/private/tmp`; the corrected canonical-path/content check passed and was a
  command assertion mistake, not a product defect.

#### Consolidation slice C5B: Servatus 0.6.0 repin

Baseline: exact clean accepted C5A head `919e93bbd3173bea09e8a6af6f17a097f197198f`
plus the exact published 0.6.0 artifacts/hashes above.

Scope:

- Change only root and mobile Servatus pins from 0.5.0 to 0.6.0 and regenerate their locks against
  the public artifacts. Preserve Blockweaver's current KAIROS pin and every dataset/corpus contract;
  the separate Blockweaver task owns later v0.3.3/K1 adoption after this handoff.
- Update directly affected active dependency documentation only. Do not add transition tests or
  mirror artifact hashes in product tests.
- Run root/mobile locks and frozen syncs, root/mobile/App tests, Ruff check/format, configured Pyright,
  manually verified Vulture, installed Servatus 0.6.0 public API/CLI/link publication smoke,
  residue/diff/status checks, and independent fixed-range review.
- Do not integrate main/compact, push KAIROS, build an image, edit `REMOTE.toml`, touch outputs/data/
  corpora, or create/launch a Campaign in this slice.

Expected outcome:

One reviewed KAIROS client head uses the public Servatus 0.6.0 contract with exact reproducible
locks and no source behavior change. C6 may then integrate that head into current main and
compact-CUDA while the Blockweaver task remains paused.

Implementation and review record:

- C5B implementation `1756a93b66b82803b11dac0d2fc9bc115f586f8d` is one clean commit from
  exact C5A head `919e93bb`; only root/mobile `pyproject.toml` and `uv.lock` changed, net zero lines.
  Both pins are `servatus==0.6.0` and both locks contain the exact published wheel/sdist hashes.
  Blockweaver remains 0.3.2 and every dataset/corpus boundary remains untouched. Independent review
  returned GREEN with Standards 0 and Spec 0. Gates passed 104 root, 9 mobile, and 43 App tests;
  root/mobile lock and frozen-sync checks; Ruff check/format; repository-configured Pyright;
  Vulture; App typecheck/dry install; installed public 0.6.0 API/CLI/hard-link publication smokes;
  residue, protected-diff, and status checks.
- Accuracy correction: `pyrightconfig.json` explicitly uses `typeCheckingMode: standard`; historical
  ledger wording calling the gate “strict Pyright” was inaccurate. Literal strict mode currently
  reports 34 pre-existing source errors and is a separate cleanup, not a C5B defect or integration
  gate. Final records use “configured Pyright.” Reviewer smoke attempts first assumed nonexistent
  convenience attributes before the corrected public metadata/`cleanup_pending` smoke passed;
  those command mistakes were not product findings.

#### Rejected consolidation findings

- A Servatus `run()`, `dispatch()`, or `open_plan_submit()` facade is rejected. It saves about a
  dozen KAIROS lines while creating a second public lifecycle, extra documentation, and a much
  larger test surface. The existing `open -> plan -> submit` interface is already direct and makes
  acceptance/retry choices explicit.
- Completion callbacks and a generic workflow/finalizer interface are rejected. Canonical Study,
  Artifact, Evaluation, roster, checkpoint, and observation validity are KAIROS scientific meaning;
  moving them would couple Servatus to application schemas.
- `Campaign.close()` and a generic Bundle abstraction are rejected. Scheduler receipts prove
  acceptance, not scientific completion, and `publish(..., retire=...)` already owns generic
  commit-first cleanup once KAIROS has decided the bundle is complete.
- GPU predicates, one-GPU rules, tasks-per-allocation policy, resource defaults, image selection,
  partitions, and queue/QOS monitoring remain KAIROS/operator policy. Servatus stays usable for CPU,
  multi-GPU, and other ML/HPC clients and must not become site-policy aware.
- Task-key/payload authoring, Pydantic request helpers, automatic completion detection, and retry
  selection remain KAIROS meaning. Servatus correctly treats tasks and completed/retry keys as
  opaque inputs.
- A scheduler plugin/backend framework, parent-directory creator, automatic retry/monitor, or
  compatibility parser is rejected as speculative generality. There is one real Slurm adapter and
  one clean-break state format; another seam would add concepts without hiding existing caller
  complexity.
- Broad removal of durable JSON/TOML validation, exact bool-versus-int checks, owner-permission
  rechecks, cross-device checks, pathname identity around callbacks/commit/deletion, no-clobber,
  parent durability, lineage, or scheduler-response parsing is rejected. These checks sit at raw or
  concurrently mutable seams and have concrete corruption/race counterexamples; they are not the
  redundant validation targeted by S1.

#### Consolidation slice C5: lean KAIROS adoption

Baseline: exact clean accepted KAIROS planning head plus exact published 0.5.0 wheel/sdist URLs and
SHA-256 hashes. Record both repository status and artifact identity before dispatch.

Scope:

- Pin exact `servatus==0.5.0` in root and mobile environments and regenerate locks from the published
  artifacts.
- Create new authored bundle roots as owner-only, then replace `publish()` plus raw
  `shutil.rmtree()` with `publish(..., retire=bundle)`. KAIROS still verifies every record and builds
  the exact manifest before it decides to close.
- Treat Evaluation as disposable publication, not resumable work: write `evaluation.json` and
  `observations.parquet` directly inside one `publish()` builder. No code resumes preserved
  Evaluation files today; Artifact fitting and Study assembly keep their meaningful Workspaces and
  `last.ckpt` behavior.
- Remove mobile export's caller-side destination-exists check and move roster/artifact loading into
  the builder so Servatus preflight avoids expensive work for a known collision.
- Rename the one KAIROS status assertion to acceptance terminology.
- Remove all KAIROS imports/patches of `servatus._slurm`. Tests fake the public `Campaign` seam and
  retain exact KAIROS Task bytes/order, canonical completion selection, explicit retry keys,
  authored HPO extension, one-GPU/resource policy, packing cap, and receipt presentation. Slurm
  argv, base64 script, generic packing, transport, journal, and retry mechanics remain tested only
  in Servatus.
- Consolidate the two direct-request CLI paths through one small private KAIROS helper that owns
  target/resource loading, the one-GPU check, one-task Campaign planning/submission, and receipt
  display. Do not add this convenience to Servatus or create a KAIROS wrapper around experiment
  Campaigns.
- Update ADR/manual wording for disposable Evaluation publication and generic bundle retirement.
  Canonical paths, schemas, labels, request bytes, manifests, output modes, and CLI success output
  remain unchanged.

Tests and review:

- Bundle verification failure preserves the entire owner-only authored bundle including opaque
  `.servatus`; retry publishes the exact manifest and retires the bundle. Generic retirement fault
  matrices are not copied into KAIROS.
- Evaluation failure after builder entry is accepted as disposable: no forensic Workspace is
  promised, and retry recomputes it. Artifact/Study resumability is unchanged.
- Evaluation association/failure and exact published bytes, mobile collision-before-load, Task
  mapping/completion/retry/profile, HPO append, full root/mobile/App/static/lock/residue/CLI gates,
  and fixed-range independent review.
- Explicit gates include root and mobile `uv lock --check` plus frozen syncs, root/mobile pytest,
  Ruff check/format, strict Pyright, `uv run vulture` with manual verification of every finding,
  App tests/typecheck/dry install, installed API/CLI help, residue scan, diff check, and clean status.

Expected outcome:

KAIROS contains no generic post-commit cleanup, disposable-workspace ceremony, caller preflight, or
private Servatus test knowledge. Its remaining code states only scientific work, application
addresses, and deployment policy. Expected reduction is modest in production code and roughly
50-100 test lines; ownership and failure truth improve without changing outputs or GPU execution.

#### Consolidation slice C5A: lean KAIROS execution client

Status: approved and active from exact C5 GREEN head
`67c1367c91550466f8d75e4c3fb811cf3ddd9334`.

Scope:

- Load target and resource TOML once at each raw CLI command, enforce the existing one-GPU KAIROS
  policy there, and pass typed values to the direct submission helper. Do not add a profile class,
  tuple, or forwarding helper.
- Remove `zip(strict=True)` where both sequences derive one-for-one from the same request paths and
  remove the one-task `tasks_per_allocation=1` override whose result cannot differ.
- Keep the operator-facing `--tasks-per-job` spelling, but make its default `None`; remove the
  KAIROS `2..4` guard and pass an explicit optional cap to Servatus. Servatus owns feasible-capacity
  validation. Omitted cap derives from the target; explicit `1` is valid; values above capacity fail
  at the Servatus owner seam.
- Remove the duplicate nonnegative candidate-index field constraint while retaining
  `TuneRequest.method_at()` as the complete bounds check. Replace the impossible third branch of
  the closed Train/Evaluate union with an ordinary typed `else`.
- Remove the repeated candidate bounds check in the internal model runner, the minimum-fee
  finiteness check strictly subsumed by final predicted-log validation, and the duplicate rolling
  horizon branch implied by the final exact group/count/horizon-set condition.
- Make the installed DataLoader profile directly fixed at four workers; remove its test-driven
  mutable worker branch and explicit default prefetch value. Tests replace the loader at its seam
  instead of mutating production configuration.
- Inline the one-use feature-ablation objective pass-through.
- Delete fake-only Campaign status and KAIROS packing-bound tests that test configured fakes or
  Servatus arithmetic. This supersedes C5's earlier `unaccepted_task_keys` assertion requirement:
  KAIROS production never calls status, while Servatus already tests its public vocabulary.

Tests and review:

- Retain exact Task keys, argv and payload bytes/order; HPO append; canonical completion selection;
  retry forwarding; one-GPU and committed profile values; receipt presentation; scientific
  association/schema/order; and meaningful runtime output.
- Add observable tests only for load-once profile behavior and default/explicit packing delegation.
  Do not add transition tests or implementation probes for deleted branches.
- Run the same root/mobile/App/static/lock/frozen-sync/installed-interface/residue/diff gates as C5
  and independent fixed-range Standards/Spec review.

Expected outcome:

KAIROS loses roughly 12-20 production lines plus redundant tests and runtime branches. No generic
module moves to Servatus because none remains; the client becomes a thinner statement of KAIROS
task meaning, scientific completion, and explicit deployment policy with no new interface.

#### Consolidation slice C6: reviewed local KAIROS integration

Baseline: exact clean C5 GREEN head, the then-current clean local KAIROS main head, and the exact
pre-existing compact-CUDA ref. Record all merge bases and worktree/branch ownership before dispatch.

- Reconcile the accepted KAIROS change with current local `main` and the maintained compact-CUDA
  branch using normal merges; prove compact's only product delta remains its reviewed CUDA path.
- Review the extraction/main merge and compact merge as separate fixed ranges, each with distinct
  implementer/reviewer roles, exact parent/topology proofs, Standards/Spec zero findings, and the
  full KAIROS gates. Do not push, build, run remotely, or clean up in this slice.
- Preserve the two pre-existing user commits, existing main/compact refs until their reviewed
  successors are accepted, and every unrelated branch/worktree.

Required integration proof:

- Pin `git rev-parse`, `git status --porcelain`, `git merge-base`, both merge parents, ancestry, and
  first-/second-parent diffs for every merge; require `git diff --check` and no conflict residue.
- Before merging, record compact's exact non-base commit list, stable patch IDs, changed-file
  roster, numstat, and byte-level CUDA delta. After merging, require the same logical commit list
  and exact CUDA-only product delta relative to the accepted KAIROS base; use `git range-diff` and
  tree/file hashes where rebasing or merge context changes object IDs.
- Run root and mobile pytest, Ruff check/format, strict Pyright, manually verified Vulture, root and
  mobile lock/frozen-sync checks, App tests/typecheck/dry install, installed API/CLI help, residue
  scans, and clean status on the final product trees.

Expected outcome:

Two exact locally reviewed KAIROS heads contain the accepted client change, preserve the compact
CUDA-only delta, and are ready for separately authorized publication. No external state changes.

#### External gate: immutable image build and isolated acceptance

After C6 GREEN, request explicit authority for the exact remote mutations:

- Build a new immutable KAIROS image from the exact accepted compact-CUDA C6 SHA through the
  documented isolated `sbuild` path. Assert the full checkout SHA and name the build/cache/image
  paths from its short SHA. Preserve the previous image and keep `REMOTE.toml` pointing at it.
- Run an isolated CPU-only production-filesystem publication/retire smoke and one synthetic
  one-task train/evaluate publication smoke using only run-owned paths. Scheduler rendering,
  resource values, four-task packing, and throughput code are unchanged, so another four-GPU
  throughput campaign is not required.
- Do not push refs, edit production configuration, or delete evidence at this gate. Preserve the
  accepted image and exact evidence for the reviewed configuration cutover.

#### Consolidation slice C7A: reviewed image-configuration cutover

Baseline: exact clean C6 main/integration head plus the exact accepted image path, image-building
source SHA, and isolated smoke evidence.

Scope:

- A fresh implementer changes only `REMOTE.toml` from the preserved `f49db0b` image to the exact
  accepted C6 compact-CUDA image. Resource values, target paths, partitions, caps, and every other
  file remain unchanged.
- Run the public target/profile parser check, full root tests, Ruff check/format, strict Pyright,
  manually verified Vulture, lock check, diff check, and clean status. Do not add a mirrored
  hard-coded image assertion to tests.
- A distinct reviewer inspects the fixed one-line product range on Standards and Spec. No push or
  remote mutation occurs.

Expected outcome:

One reviewed KAIROS head selects the exact already-built and already-accepted immutable image; no
unreviewed post-build configuration commit remains.

#### Consolidation slice C7B: compact configuration synchronization

Baseline: exact clean C7A GREEN head and exact clean C6 compact-CUDA GREEN head.

Scope and checks:

- Merge the accepted C7A configuration commit normally into compact-CUDA. Keep the image path
  identical and preserve the exact C6 CUDA-only delta.
- Re-run target parsing, merge-parent/ancestry/tree/diff/range-diff/patch-ID parity, diff check, and
  clean status. Review the fixed merge range independently on Standards and Spec.

Expected outcome:

Main and compact-CUDA select one accepted immutable image while compact retains only its reviewed
CUDA execution delta.

#### External gate: ref publication and run-owned cleanup

After C7A/C7B GREEN, request explicit authority to:

- Push only the exact reviewed KAIROS refs and verify the remote SHA values.
- Start the clean Servatus schemas only with the next new experiment bundle. Never open or migrate
  legacy HPO bundle `dfd33e91-702e-46c5-8cb1-3c510af4c048`; preserve image `004f951` and its old
  lifecycle state until it is closed with old semantics.
- Before the 0.5 image becomes production authority, inventory only known private lifecycle
  namespaces under explicit metadata-read authorization: authored bundle `.servatus` directories
  and destination-adjacent `.servatus-*.work` roots for Studies, Artifacts, and Evaluations. Every
  pre-0.5 active item must finish on its old image or remain quarantined and unopened. Do not crawl
  canonical contents, parse old state, or migrate it. Canonical outputs remain compatible.
- After published refs and acceptance are verified, remove only recorded run-owned worktrees,
  branches, build/cache/acceptance/log evidence whose exact paths and ownership have been checked.

Expected outcome:

Published Servatus and KAIROS refs, immutable image, and future clean-break execution all use the
reviewed interface. Existing outputs remain readable and byte/schema compatible; existing jobs and
legacy work are untouched. Final branch/worktree state matches the recorded pre-run state except
for explicitly published refs.

Planning review record:

- Independent architecture review returned GREEN with zero actionable findings after the plan made
  retirement descriptor-rooted, covered every pre-0.5 private lifecycle namespace, split the
  trust-root correction from mechanical consolidation, made Evaluation's disposable-failure
  tradeoff explicit, kept `cleanup_pending` authoritative, and named the remaining KAIROS CLI
  duplication.
- Independent execution review returned GREEN with zero actionable Standards or Spec findings
  after the plan added reviewed 0.5.0 release preparation; exact run-owned checkout, baseline,
  implementer/reviewer, and correction policy; full named gates; separate local integration,
  immutable-image acceptance, reviewed `REMOTE.toml` cutover, compact synchronization, push, and
  cleanup boundaries.
- `git diff --check` passed. Planning contacted no remote scheduler, output, dataset, campaign,
  image, GitHub, or PyPI surface and changed no product code.

Execution authorization and run setup on 2026-08-11:

- The user authorized Servatus consolidation slices C1A through C4 and requested a pause before
  KAIROS slice C5. The user separately authorized pushing Servatus, creating/tagging the GitHub
  `v0.5.0` release, and publishing `servatus==0.5.0` after all four slices are independently GREEN.
- The immutable Servatus baseline is the clean released `v0.4.1` head
  `2ccf749e2a4c3f5ad7ca572ee34fe78e5b1bb78f`; its primary checkout had only `main` and no other
  worktree. This run owns branch `codex/servatus-consolidation-0.5` and worktree
  `/private/tmp/servatus-consolidation-0.5`, created at that exact baseline.
- The KAIROS orchestration baseline is clean `main` at
  `fa7ba4f1571eb293dd6d1e919cf4e9e0f532183a`, three commits ahead of `origin/main`. Existing
  `codex/compact-cuda-execution` at `a81efb47e653227381401a597a48d76ab03068ef` is pre-run state and
  is not owned or modified by the Servatus slices.
- Each slice receives one fresh implementer and one distinct reviewer. Corrections return to the
  same pair; the next slice starts only after a zero-finding Standards/Spec review. No KAIROS
  product, remote scheduler, image, output, dataset, campaign, or production scratch is in scope.
- C1A implementation commit `0cb630eb8da19518f1cf65eadb64a824bc740e54` passed 247 tests with
  one platform skip plus all static/build/installed-artifact gates. Its first independent review
  rejected four findings: stage creation still accepted a substituted inode; the C1B reopen-sync
  optimization landed early; mode-`000` regular files blocked exact cleanup; and root/nested
  removal duplicated one recursive algorithm. Correction `322296de64e5cebe6cea683c486f8fa1206aa1d7`
  closed all functional findings; its rereview rejected one unused recursive-device parameter.
  Correction `b6d7647367486375017e4ee1756a9c80903d5d1a` made that root-device invariant explicit. The same
  reviewer returned final GREEN LIGHT with Standards 0 and Spec 0. Final C1A gates passed 250 tests
  with one platform skip, Ruff check/format, strict Pyright, Vulture, lock/diff checks, build,
  archive inspection, and fresh-wheel API/CLI smokes. The Servatus worktree is clean; C1B starts
  from exact `b6d7647`.
- C1B implementation `ecf7c644a35ac4d8d6e212f55230dc37ef8b36b2` reduced the Workspace/POSIX
  slice by 56 net lines and passed 250 tests with one platform skip plus every static/build/install
  gate. Its first review rejected one P1 on both axes: `_verify_level()` reused stale open-time
  metadata, so a post-open permissive chmod escaped the C1A owner-only recheck. The same pair owns a
  focused correction that must retain a fresh UID/mode read without restoring redundant
  type/device validation. Correction `960a3f09e5865f846f34a8dcf279b575294a5446` fresh-fstats the
  already-open container, work, and lock descriptors for current owner/mode while preserving the
  pathname-to-pinned-inode check. The same reviewer returned GREEN LIGHT with Standards 0 and Spec
  0. Final C1B is a net 29-line reduction from C1A; 253 tests with one platform skip and every
  static/build/install gate pass. C2 starts from exact `960a3f0`.
- C2 implementation `e861789e262f8930a5c0b130f50b53ebe0f232d9` removed 135 Campaign/Slurm
  source lines and passed 255 tests with one platform skip plus all static/build/install gates.
  Standards review returned zero findings. Spec review rejected one P2 durable-ingress defect:
  Python numeric equality admitted float schema versions and bool/float allocation totals. The same
  pair corrected exact integer type/bounds at ingress in
  `f5cb8afcc3cbe6ebacfb33da1b7d98fe713f9a0f` without restoring the duplicate decoder. Rereview
  returned GREEN LIGHT with Standards 0 and Spec 0. Final C2 passed 262 tests with one platform
  skip plus all static/build/install gates. C3 starts from exact `f5cb8af`.
- C3 implementation `6c8c96c289a5e812f45c3e06440a09f5cff93a4d` passed 267 tests with one
  platform skip plus all static/build/install gates. Its first review rejected one shared
  Standards/Spec defect: CLI plan bytes were written while the ordinary-umask stage was still
  `0644`, before chmod to `0600`. Standards also found validation messages coupled to submission
  and a stale file-wide private-usage suppression. Correction
  `e6028749c32436340b313d9eb3afecf22e63dced` makes the empty stage `0600` before writing, gives
  validation/submission precise operation messages, and removes the suppression. Rereview returned
  GREEN LIGHT with Standards 0 and Spec 0. Final C3 passed 268 tests with one platform skip plus all
  static/build/install gates. C4 starts from exact `e602874`.
- C4 implementation `ce7c8ffe69adea70432629100fe1873ea895d14c` passed 285 tests with one
  platform skip plus all static/build/install gates and produced inspected 0.5.0 artifacts. Review
  accepted every functional retirement/preflight/warning contract but rejected three concrete
  duplications: repeated parent verification, repeated owner-only policy, and repeated pinned-tree
  verification behind a single-use wrapper. It also rejected the plan's optimistic cumulative
  “smaller overall” wording: measured C1A-C4 product source was net +126 versus v0.4.1. The same pair
  owns the deletion correction; the orchestrator must record the final measured outcome truthfully
  after rereview. Correction `79ee407c431d1f9c0510e9462d5136fa7b58319d` removes the repeated
  checks/wrapper and 18 net product lines. The correction candidate is net +108 product source lines
  versus v0.4.1: Campaign `-98`, Slurm `-9`, Workspace `-1`, CLI `+3`, public exports `+2`, and POSIX
  `+211`. The growth is concentrated in the new exact trust-root deletion and retained-tree
  retirement implementation, not duplicated client-facing surface. The same reviewer returned
  final GREEN LIGHT with Standards 0 and Spec 0, confirming one authoritative preflight check, one
  owner-only policy, and one exact pinned-tree deletion path. Final C4 passed 285 tests with one
  environmental skip plus all static/build/install gates. Exact accepted 0.5.0 source head is
  `79ee407c431d1f9c0510e9462d5136fa7b58319d`. The user authorized the Servatus push, tag, GitHub
  Release, and PyPI publication gate; KAIROS C5 remains paused until published artifact hashes are
  verified.
- Servatus `main` was fast-forwarded and pushed to exact reviewed head
  `79ee407c431d1f9c0510e9462d5136fa7b58319d`. Main CI run `31487426717` and tag CI run
  `31487474435` passed on Ubuntu and macOS. Annotated tag `v0.5.0` dereferences to that exact commit;
  the public GitHub Release is `https://github.com/edoski/servatus/releases/tag/v0.5.0`.
- Trusted-publishing run `31487570056` succeeded. PyPI published wheel
  `servatus-0.5.0-py3-none-any.whl` with SHA-256
  `1d1f0bc1a0d5d38b5d9e80d6b93799e30cf6395a050d6bd9524e5d0592d389eb` and sdist
  `servatus-0.5.0.tar.gz` with SHA-256
  `1874c8776e1db515f5249a3a80f67cc8cc2c82b1ca4a9074d9963b6d0c1f9015`. A fresh no-cache public
  index install verified metadata version 0.5.0, zero runtime dependencies, `Campaign.load`,
  `ValidationResult`, exact `publish(..., retire=...)` behavior, and both CLI entry points. The
  release gate is complete. The run-owned `/private/tmp/servatus-consolidation-0.5` worktree and
  `codex/servatus-consolidation-0.5` branch were removed only after `main` and the remote tag were
  verified at the accepted head. Servatus now matches its pre-run one-worktree/one-main-branch
  shape, clean at 0.5.0. Work pauses before KAIROS C5 as requested.

KAIROS C5/C6 resumption authority on 2026-08-12:

- The legacy HPO campaign is closed at 216/216. The separately reviewed Blockweaver clean break is
  complete and published on both remotes: KAIROS `main` is exactly
  `6a8f22c2e518b4bc6885b5cc6e3d807333e3053b`; compact-CUDA is exactly
  `05ca43b1c51d2c68fd61065cf69b41e7548ca58a`. Root and mobile environments pin Blockweaver 0.3.2,
  KAIROS loads `outputs/datasets/<uuid>` through its public reader, and old corpora remain untouched.
- The user authorized C5 adoption of published Servatus 0.5.0, independent fixed-range review, and
  C6 integration into both current heads. After both heads are GREEN, push only those exact refs to
  `origin` and `research`, verify remote SHAs, then report them to task
  `019fea93-223d-7d42-bcfc-c4a499b59dd0` and stop.
- This resumption must preserve the Blockweaver dependency, dataset paths and schemas, the exact
  compact CUDA delta, canonical output paths and bytes, and old corpora. It must not build an image,
  edit `REMOTE.toml`, read/delete/migrate outputs or corpora, contact Slurm/GPU/Apptainer, create or
  launch a Campaign, or run synthetic/live campaign smokes. The Blockweaver task owns the one final
  combined image, later configuration cutover, and exact legacy-corpus cleanup.
- Pre-run state is one clean KAIROS worktree on `main`; local refs are the exact heads above plus
  pre-existing alias `codex/compact-dataset-alignment` at the compact head. Both remotes already
  match. Any new C5 branch/worktree is run-owned; the three existing refs and primary worktree are
  not.
- C5 implementation `ef817b301e7d0c68584408a2a3e2034671d413c2` passed 110 root, 9 mobile,
  and 43 App tests plus every required static/lock/installed-interface gate; production Python is
  net 15 lines smaller. Standards review returned zero findings. Spec review rejected two P2s: the
  old pending-status assertion lacked one lean `unaccepted_task_keys` replacement, and tests grew
  by 43 lines because the new public Campaign fake was too large instead of delivering the planned
  test simplification. The same implementer replaced the 52-line fake with a 15-line public capture
  seam, restored one `CampaignStatus.unaccepted_task_keys` assertion, merged three workflow cases,
  and deleted two dependency-level collision cases in correction
  `67c1367c91550466f8d75e4c3fb811cf3ddd9334`. Final C5 tests are net 63 lines smaller and contain
  106 root cases versus the 109-case baseline; production remains net 15 lines smaller. The same
  reviewer returned GREEN LIGHT with Standards 0 and Spec 0. Final gates passed 106 root, 9 mobile,
  and 43 App tests plus Ruff, formatting, strict Pyright, Vulture, exact lock/frozen-sync checks,
  installed public-interface smokes, and residue/diff checks. A final source-deletion audit is
  active before C6 integration; C6 remains blocked until it either records no supported deletion or
  a separately reviewed cleanup is accepted.
- The source-deletion and execution-ownership audits found no generic execution, submission, or
  filesystem module left in KAIROS to move into Servatus. Servatus already owns roster lineage,
  packing and resource arithmetic, submission intents and receipts, ambiguity, reconciliation,
  publication, and retirement. A new run/dispatch facade, completion callback, Campaign close,
  GPU predicate, or queue policy would be a shallow second lifecycle path and is rejected.
- C5A is a bounded KAIROS deletion slice from exact accepted C5 head `67c1367c`. It loads target and
  resources once per raw CLI command, removes a meaningless one-task packing override, delegates
  experiment packing bounds to Servatus while retaining the existing `--tasks-per-job` spelling,
  and removes redundant candidate-index, exhaustive-union, strict-zip, finiteness, rolling-roster,
  test-driven DataLoader-profile, and one-use figure-helper machinery. It must retain exact task
  bytes/order, canonical completion and scientific association/schema checks, explicit retry,
  one-GPU policy, receipt presentation, and the committed resource/profile values. The earlier
  fake-only `unaccepted_task_keys` test requirement is superseded: KAIROS production never calls
  Campaign status, and testing a configured fake or real Servatus status here would retest the
  dependency. Expected outcome: fewer KAIROS source concepts and runtime checks, roughly 12–20
  fewer production lines plus a smaller test surface, with no new interface and no output/config
  change. A fresh implementer and reviewer own C5A before C6 can start.
- C5A implementation `919e93bbd3173bea09e8a6af6f17a097f197198f` is GREEN. Its exact
  `67c1367c...919e93bb` range contains one clean commit; production Python is net 16 lines smaller
  and tests are net 10 lines smaller. Independent review returned Standards 0 and Spec 0. Final
  gates passed 104 root, 9 mobile-export, and 43 App tests plus Ruff, formatting, strict Pyright,
  Vulture, root/mobile locks and frozen syncs, App typecheck/dry install, installed API/CLI smokes,
  residue, diff, and status checks. C6 remains paused behind approved Servatus S1/S2 and the later
  public dependency repin.
- A separate read-only audit of released Servatus 0.5.0 found an internal-only slimming candidate:
  redundant typed-object checks, repeated durable-list checks after one raw-ingress validation,
  kernel-impossible file-stage branches, repeated inode-type clauses, private ingress repeats, and
  one unreachable CLI branch. Adversarial review estimates 45–60 definitely safe source-line
  deletions, with a further clean-break set requiring an explicit source-linearization decision.
  This finding does not reveal another KAIROS ownership leak. It is not part of C5A/C6: changing the
  already published dependency requires a separately authorized Servatus version/release and KAIROS
  repin, so the current 0.5.0 adoption must not be silently rewritten around it. The user then
  approved local S1 and S2 implementation/review as one 0.6.0 candidate. The separate Blockweaver
  task may continue Blockweaver-only slices concurrently but holds K1, KAIROS refs, image/config,
  and corpus cleanup until this task supplies exact accepted main/compact heads; the coordination
  message was delivered on 2026-08-12. That task subsequently completed and independently reviewed
  Blockweaver Slices 3A-3F and publicly verified release v0.3.3 at exact head
  `e69c02c2d72cc5250834233d3eee9a525e386eb0` (wheel SHA-256
  `42f368fb94daab2fdf12f8d4763be82917f4f0b37255a16be98d735c3443ec0b`; sdist
  `a5f8c55f6310e8766c23b2adb6a5000159a36bf9adb26de24027eb816b8dd9c1`). It remains paused
  before K1/KAIROS/image/config/corpus actions and instructed this task to finish S1/S2, then stop
  at any ungranted Servatus release gate.

### Historical final deployment gates for the initial extraction

This retained record describes the completed initial 0.4.1 cutover. It does not authorize or prove
the future 0.5.0 consolidation release, image, smoke, publication, or cleanup gates above.

The implementation and configuration cutover is complete. Old-layout work remains isolated on its
captured checkout, image, and `jobs.tsv` lifecycle until it closes; new work uses the clean Servatus
path. The completed deployment checklist is retained below:

1. Read-only inventory the live queue, active immutable image paths, experiment drafts, canonical
   outputs, and scratch owners.
2. Let old-image jobs finish or obtain explicit authority for any scheduler mutation. Do not hold,
   release, cancel, requeue, resubmit, move, or delete them implicitly.
3. Close or archive old-layout experiment state only through its current code before the cutover;
   do not add legacy parsing to new KAIROS or Servatus.
4. Build a new immutable KAIROS image through the documented `sbuild` partition procedure from an
   isolated exact-SHA checkout. Run `apptainer build` then `apptainer test`.
5. Run separately authorized new-path KAIROS smokes. Completed above: final-image candidate,
   Study publication/load, TrainRequest, Artifact publication/load, TRES, and log-shape gates are
   green. Existing live evidence remains authoritative for unchanged four-pack, UUID isolation,
   failure aggregation, `3 + 3 + 3`, and exact production-profile rendering.
6. Compare old/new `ReqTRES`, `AllocTRES`, logs, results, and one representative task's
   elapsed/throughput behavior using the same immutable image, input, dedicated partition, and GPU
   model, preferably the same node. This lean A/B is a gross-regression check, not a statistical
   performance study; repeated trials or a thesis-scale campaign are unnecessary unless making a
   formal performance claim. The mixed production partition route is not valid A/B evidence.
7. Run one application publication smoke. Completed above for both Study and Artifact. Preserve the
   preceding image and old execution path until production cutover passes.
8. Update remote image configuration only after acceptance. Acceptance, product publication,
   protected-work restoration, and the bounded cleanup above are complete. Ledger-only completion
   corrections follow the final review and normal-fast-forward choreography; the excluded final
   compact review worktree is then removed before handoff. Preserve the old image and old lifecycle
   state while already-submitted or unfinished old-layout work still references them.
9. Before running the inference cost/time benchmark, verify a completed canonical full-roster
   manifest pair containing all nine chain-family groups and 36 artifact/evaluation records over
   `K=2..5`. This scientific-readiness gate is not complete. If the pair is absent or incompatible,
   separately scope and authorize a dedicated benchmark-input author and GPU campaign; do not
   silently widen the selected-LSTM horizon study.

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
tasks or unsafe explicit caps. Its result was absorbed and the prototype and duplicated research
record were deleted.

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

Slice 3's first read-only implementation pass stopped without product edits at
`3018733b79bf98ae63e71d2592eee307e11f86d8`: Servatus 0.1's directory-only publication cannot
preserve the benchmark's exact standalone `protocol.json` and `sweep-NNN.parquet` destinations.
Three independent interface designs favored the narrow explicit `publish_file()` operation over a
polymorphic publication API or KAIROS shim. Prerequisite Slice 2A now closes that generic contract
before the same KAIROS implementer resumes Slice 3.

The separate future plan in task `019fea93-223d-7d42-bcfc-c4a499b59dd0` was consulted read-only on
2026-08-10. Its committed Blockweaver ledger remains unchanged and paused until this Servatus run
finishes. Only its relevant ownership rule is carried here: Blockweaver will later own the external
dataset artifact under a separately authorized clean-break migration, while Servatus remains an
opaque path transaction and KAIROS retains scientific interpretation. This run makes no corpus or
dataset change and does not pre-empt that future plan.

Prerequisite Slice 2A then completed at `f60335416b549fdc252c56152af2b9678e94bb72` through a fresh
implementation and independent two-lane review. The accepted `publish_file()` operation preserves
the ordinary file mode selected by `0o666` plus the process umask, pins the stage inode, and reuses
the same exclusive durable commit transaction as directory publication. The reviewer returned
`GREEN LIGHT` with zero Standards and Spec findings. The clean local `0.2.0` candidate is not yet
pushed, tagged, released, or published; Slice 3 remains paused until that separately authorized
external gate makes the reviewed dependency reproducibly installable.

The user then authorized that external gate. Servatus `main`, annotated tag `v0.2.0`, GitHub Release,
and PyPI Trusted Publishing all completed from exact head `f60335416b549fdc252c56152af2b9678e94bb72`.
Branch and tag CI passed on Ubuntu and macOS, the publish workflow succeeded, and a fresh index
install verified version, API, and CLI. This closes prerequisite Slice 2A and permits the same paused
KAIROS Slice 3 implementer to resume locally without contacting outputs or the research cluster.

Slice 3 completed at `87f09c09f0441af49990c7c9be296e3286783ed2`. Its first review found one
callback return-type defect; the same implementer corrected it in a separate commit and the same
two-lane reviewer returned `GREEN LIGHT` with Standards 0 and Spec 0. KAIROS now directly delegates
disposable file and directory transactions to Servatus while preserving benchmark/mobile paths,
formats, validation, and restart meaning. No protected or external state was touched.

Slice 4's fresh implementer paused read-only at `77922ac597f17a19e9eeecd269612f7339863235`
after proving that ordinary nested Workspaces would break concurrent Study candidate throughput.
Evaluation and artifact mappings remain direct; no product edit was made. Three independent designs,
an adversarial lock audit, and a deleted spawned-process prototype established the lean generic fix:
one `Workspace.child()` method with shared parent/exclusive child leases and short stable-parent
coordination. Prerequisite Slice 3A now owns that Servatus change before the same KAIROS implementer
resumes. No repository outside this ledger, output, or external system was changed by the design or
prototype work.

Prerequisite Slice 3A completed at `b8eb73f33d54a67efd9f192739223d8103877939` after two P1
review corrections: durable lifecycle-lock/work inode binding, then an explicit owner-only-container
trust boundary for arbitrary same-account whole-root replacement. The same reviewer returned final
`GREEN LIGHT` with Standards 0 and Spec 0. An immediate two-node CPU filesystem smoke obtained no
allocation and left no queued job; it is deferred to remote deployment because shared `flock`
coherence is site/mount configuration, not a package-release property. The user authorized the
reviewed `0.3.0` release; no KAIROS product code resumed before an installable package exists.

Servatus `0.3.0` was then pushed, tagged, released, and published from the exact reviewed head.
Branch/tag CI and Trusted Publishing succeeded, PyPI provenance/hashes were recorded, and a fresh
index install verified version, `Workspace.child`, and CLI. This closes prerequisite Slice 3A for
local development and permits the same paused KAIROS Slice 4 implementer to resume. The deferred
cross-node filesystem smoke remains a hard remote-deployment gate.
