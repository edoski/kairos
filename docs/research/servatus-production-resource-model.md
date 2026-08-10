# Servatus production resource model

Date: 2026-08-10

## Decision

Servatus V1 should support one production-shaped execution mode: homogeneous, independent work
units packed as concurrent exact steps inside a single-node Slurm allocation. It should expose a
small typed `ResourceRequest`, constrain it with a concrete `SlurmTarget`, and ask Slurm to allocate
exactly the sum of the packed work. It must never request a whole node or all GPUs merely because a
node has them.

This is the common single-node ML case and the current KAIROS case. Multi-node distributed jobs,
job arrays, heterogeneous jobs, fractional GPUs, arbitrary GRES, and raw `#SBATCH` passthrough are
not V1 requirements. Supporting those now would enlarge the public contract without improving the
KAIROS extraction.

## Primary-source findings

### Allocation and steps are different resource boundaries

`sbatch` creates a job allocation. Each `srun` inside the batch script creates a job step that uses a
subset of that allocation. Slurm validates and selects resources for the allocation, while step
selection is a separate, simpler operation ([Job Launch Design Guide](https://slurm.schedmd.com/job_launch.html)).

`srun --exact` restricts a step to its requested non-GRES resources. Parallel exact steps block or
fail when their requested resources do not fit inside the allocation. Inside an existing allocation,
`srun --exclusive` is a synonym for `--exact`; `--overlap` instead permits sharing
([srun](https://slurm.schedmd.com/srun.html)). Servatus should preserve KAIROS's explicit
`--exclusive --exact` child-step shape and never emit `--overlap`.

Allocation-level `--exclusive` has different semantics: it can allocate every CPU and GRES on each
selected node, even when the job requested less. Slurm also notes that memory remains limited to the
requested amount ([sbatch](https://slurm.schedmd.com/sbatch.html)). Servatus must therefore never
emit job-level `--exclusive` in its normal mode. That is the direct guard against requesting all 12
GPUs of a node for one one-GPU task.

### GPUs must be requested twice and consistently

Slurm allocates no GRES unless the job requests one. `--gres=gpu[:type]:N` requests `N` GPUs per
node. The newer `--gpus*` family requires `select/cons_tres`; the generic `--gres` path is the more
portable interface. Typed and untyped GRES requests must remain consistent between the job and its
steps ([GRES Scheduling](https://slurm.schedmd.com/gres.html)).

An exact step can request part of the job's GPU allocation. Those GPUs then remain unavailable to
other concurrent steps, and Slurm maps assigned devices through `CUDA_VISIBLE_DEVICES`
([GRES Scheduling](https://slurm.schedmd.com/gres.html)). Servatus should not assign physical CUDA
indices itself.

For `n` homogeneous packed tasks requiring `g` GPUs each, V1 therefore emits:

```text
job allocation: --nodes=1 --ntasks=n --gres=<gpu-resource>:n*g
each child step: --nodes=1 --ntasks=1 --gres=<gpu-resource>:g --exact
```

When `g == 0`, Servatus omits both GRES options and GPU container enablement. When `g > 0`, the
target must define an allowed GPU GRES name and a sufficient per-allocation ceiling. Counts are
whole GPUs. MPS, shards, and other fractional-sharing schemes are separate site-specific resource
models and remain outside V1.

### CPU, memory, and time should use one unambiguous mode

`--cpus-per-task` tells the controller how many colocated processors every task requires. Without
it, Slurm assumes one processor per task ([sbatch](https://slurm.schedmd.com/sbatch.html)). V1
should expose a positive `cpus_per_task`, request it at allocation and step level, and never silently
increase the requested count.

Slurm offers `--mem`, `--mem-per-cpu`, and `--mem-per-gpu`, but they are mutually exclusive.
`--mem=0` means all memory on every node. `--mem-per-cpu` may also be rewritten into a different
CPU count when it exceeds a site maximum ([sbatch](https://slurm.schedmd.com/sbatch.html)). That
flexibility is harmful to a small exact model. V1 should expose only positive absolute
`memory_mib_per_task`, emit `--mem=n*M` for the one-node allocation and `--mem=M` for each exact
step, and reject zero. Slurm's own step daemon memory is included in the job's memory usage, and
strict enforcement depends on site cgroup/configuration, so Servatus must not promise that all
requested bytes are application-usable or locally enforceable
([sbatch](https://slurm.schedmd.com/sbatch.html)).

`--time` limits the allocation, not each step. Slurm rounds second values upward to minute
resolution and sends `SIGTERM`, then `SIGKILL`, at expiry. A value of zero requests no limit, while
a request above the partition maximum can remain pending indefinitely
([sbatch](https://slurm.schedmd.com/sbatch.html)). Servatus should require a positive time limit,
parse only its documented canonical duration syntax, show the rounded Slurm limit in the plan, and
reject values above the target's declared ceiling.

### Placement and policy are site-owned

Partition, account, QOS, constraint names, available GRES, and their relationships are defined by
the cluster. Associations and QOS can impose job, submitted-job, wall-time, per-job TRES,
per-node TRES, and aggregate TRES limits. Which limit wins depends on the configured hierarchy
([Resource Limits](https://slurm.schedmd.com/resource_limits.html)). Job-submit plugins may also
set defaults, change a request, or reject it before scheduling
([Job Submit Plugin API](https://slurm.schedmd.com/job_submit_plugins.html)).

A target profile can prevent mistakes using administrator-supplied names and conservative ceilings,
but it is not a security boundary. Users can edit local files. Slurm remains the authority for
identity, admission, policy, availability, enforcement, priority, and billing.

Slurm records minimum requested TRES separately from resources allocated after job start. Those
values may differ because of node geometry, site defaults, plugins, or allocation policy
([sacct](https://slurm.schedmd.com/sacct.html)). Servatus V1 retains its own exact request; the
production gate compares `ReqTRES` and `AllocTRES` through site tools without adding a monitoring or
accounting subsystem. Neither value proves application utilization, and GPU utilization accounting
itself depends on site configuration ([TRES](https://slurm.schedmd.com/tres.html)).

### Planning and cluster validation are separate operations

`sbatch --test-only` validates a script against the live controller, returns a current scheduling
estimate, and submits no job ([sbatch](https://slurm.schedmd.com/sbatch.html)). It still contacts
the cluster and exercises current site configuration. Slurm warns clients not to issue controller
RPCs in unbounded loops because they can degrade controller performance
([sbatch](https://slurm.schedmd.com/sbatch.html)).

Servatus should therefore expose two distinct operations:

- `servatus plan`: fully local. Parse, validate, pack, and print the exact allocations, steps,
  resource totals, commands, script digests, and value origins. No SSH or Slurm contact.
- `servatus validate`: explicit remote preflight. Run one `sbatch --test-only` per distinct
  allocation shape serially and with no retry storm. Report Slurm's answer as a time-specific
  cluster decision, not a durable guarantee.

Submission must remain a separate explicit command. `plan` must never imply that Slurm will accept
or start the work.

### Environment and rendering need a hostile-input boundary

`sbatch` normally exports the caller's complete environment. `SBATCH_*` variables override options
embedded in the batch script, while explicit command-line options override environment variables.
`--export=NIL` limits propagation to Slurm/SPANK variables without implicitly loading the login
environment ([sbatch](https://slurm.schedmd.com/sbatch.html)).

Servatus should:

- render all scheduler selections as separate, strictly quoted command-line arguments rather than
  interpolated `#SBATCH` text;
- invoke `sbatch`, `srun`, `squeue`, and `sacct` from the target's one absolute `slurm_bin` directory
  and invoke its absolute container-runtime path from an SSH-side sanitized environment;
- use a clean export mode supported by the target and pass application environment values
  explicitly;
- reject NUL/newline-bearing names and unknown TOML keys;
- redact opaque arguments and stdin from ordinary plan/journal output, while documenting that the
  payload is embedded in the submitted batch script, may be visible to cluster administrators or
  accounting, and therefore must not contain secrets; and
- provide no raw scheduler-argument or raw-directive escape hatch in V1.

The current Slurm web manuals describe version 26.05; matching documentation for other releases
ships with their source ([man-page index](https://slurm.schedmd.com/man_index.html)). Servatus must
use the SSH target's own CLI, record `sbatch --version`, and declare a tested version window only
after probing the research cluster. It should rely on the long-standing `--gres`, `--parsable`, and
narrow text interfaces, not unversioned JSON schemas. Any feature outside the tested subset must
fail capability validation before submission. Environment isolation must likewise fail closed if
the chosen safe mode is unavailable; it must not silently fall back to `--export=ALL`.

## Final V1 boundary

The authoritative public types live in the
[`lifecycle-extraction-implrevloop.md`](lifecycle-extraction-implrevloop.md) ledger rather than being
duplicated here. `ResourceRequest` requires exact CPU, MiB memory, whole-GPU count, and a validated
canonical Slurm time string. Direct construction and TOML loading run the same validation; no target
default supplies a missing resource.

`SlurmTarget` states one concrete site route and safe operating envelope. It owns one absolute
`slurm_bin` directory, an absolute Apptainer path, image/work/log paths, ordered partitions,
optional account/QOS/constraint, count-free GPU GRES, exact allocation ceilings, controller-call
cap, and script-size cap. Every partition in one target must truthfully share that conservative
envelope; otherwise a user or administrator defines separate targets such as `a100-short` and
`h100-long`. These are preventive user-side checks, not authoritative cluster policy.

One `Campaign.plan(target, resources, ...)` call supplies one homogeneous request for the selected
opaque tasks. `Campaign.submit(plan)` eagerly submits only that immutable plan. Work requiring
another shape uses another Campaign; V1 does not attach resources to individual `Task` values.

Because Servatus sends complete encoded payloads inside the accepted batch script, the target also
caps the final script in bytes. Slurm's `SchedulerParameters=max_script_size` defaults to four
megabytes and larger values may harm controller performance
([slurm.conf](https://slurm.schedmd.com/slurm.conf.html)). The live gate must inventory the site's
value; Servatus rejects an oversized rendered script locally and never relies on a payload file that
must appear after scheduler acceptance.

## Planner invariants

For a pack of `n` tasks and request `(C, M, G, T)`:

```text
allocation_cpus       = n * C
allocation_memory_mib = n * M
allocation_gpus       = n * G
allocation_time       = T
```

The largest legal pack is bounded by every applicable ceiling:

```text
n <= max_tasks_per_allocation
n*C <= max_cpus_per_allocation
n*M <= max_memory_mib_per_allocation
n*G <= max_gpus_per_allocation       when G > 0
T <= max_time_limit
```

Without an operator cap, the planner derives the largest pack size that fits every target ceiling;
it never changes `C`, `M`, `G`, or `T`. It then uses the existing balanced packing rule to avoid a
small tail where possible. An explicit `tasks_per_allocation` may lower that derived capacity, but a
value above it is rejected rather than silently clamped. A single task that exceeds a ceiling is
rejected rather than split across nodes or silently enlarged.

Every packed task receives an explicit step with its exact resource subset. The aggregate
allocation must equal the checked sum of those concurrent steps. No implicit defaults, resource
escalation, overcommit, overlap, or whole-node request is permitted.

The immutable Servatus intent records:

- the target and resource-request digests;
- each explicit user-supplied resource value and target guardrail;
- task order and pack membership;
- exact `sbatch` argument vector and complete batch script digest;
- computed aggregate resource totals; and
- later, the validated Slurm version and accepted job ID.

## Validation ownership

Servatus can prove locally:

- schema and type correctness, including rejecting booleans as integers;
- positive CPU, memory, and time; nonnegative whole-GPU count;
- strict duration syntax and canonical Slurm rounding;
- absolute executable and remote paths;
- no unknown keys, control characters, duplicate/conflicting fields, or raw options;
- typed/untyped GPU consistency between allocation and steps;
- exact aggregate arithmetic and all declared target ceilings;
- complete rendered script size at or below the live-validated target cap;
- single-node feasibility relative to the declared profile;
- deterministic balanced packing and script/argument rendering; and
- absence of job-level exclusivity, overlap, unlimited time, and all-memory requests.

Only the target Slurm controller can decide:

- whether partition, account, QOS, constraint, and GRES names exist and are allowed for this user;
- whether the installed Slurm plugins support and preserve the request;
- whether current association, QOS, partition, or aggregate TRES limits admit it;
- whether nodes satisfying the combined request exist or are currently available;
- whether CPUs or memory are rounded due to hardware topology or site configuration;
- whether cgroups enforce CPU, memory, and device isolation;
- how the request is prioritized and billed; and
- when or whether a valid pending job starts.

`servatus validate` narrows that uncertainty at one moment. It does not move those decisions into
Servatus.

## KAIROS compatibility fixture

KAIROS's current request becomes one ordinary Servatus profile and request:

```text
ResourceRequest(
    cpus_per_task=32,
    memory_mib_per_task=65536,
    gpus_per_task=1,
    time_limit="3-00:00:00",
)
target.partitions = ("h100sxm5", "h100pcie", "a100", "l40s", "l40")
target.gpu_gres = "gpu"
target.max_tasks_per_allocation = 4
target.max_allocations_per_submit = 64
target.max_script_bytes = <authorized live-cluster value>
```

For four tasks, Servatus must request one node, four tasks, 128 CPUs, 262144 MiB, and four GPU GRES,
then launch four concurrent exact steps with one GPU, 32 CPUs, and 65536 MiB each. For nine tasks,
balanced packing remains `3 + 3 + 3`; no job asks for more than three GPUs. A one-task pack asks for
one GPU. Nothing derives a request from the node's full capacity. The target ceilings are
conservative request guardrails, not claims about the physical capacity of every listed partition;
the live-cluster gate must inventory and validate that combined route before adoption.

The KAIROS migration cannot be accepted from unit tests alone. Its gates are:

1. Golden parity for task bytes and order, `9 -> 3 + 3 + 3`, allocation totals, step arguments,
   image, paths, and logs.
2. A local assertion that no generated allocation contains job-level `--exclusive`, `--overlap`,
   `--mem=0`, or a GPU count above the pack's exact sum.
3. Separately authorized CPU-only, one-GPU, two-GPU-process, and four-packed-step smokes. The packed
   smoke must show four simultaneous steps with distinct physical GPU UUIDs and unchanged
   application results; relative CUDA indices alone are insufficient evidence of isolation.
4. Comparison of `sacct` `ReqTRES`, `AllocTRES`, elapsed time, exit state, and GPU utilization when
   the cluster records it, plus a representative old/new KAIROS timing comparison on the same
   dedicated partition and GPU model, preferably the same node. Record comparable node, driver,
   power, clock, and physical GPU UUID facts; the mixed production route is not controlled A/B
   evidence.
5. Migration only after the real gate passes; queued jobs continue using their existing checkout
   and image.

Local equivalence supports the expectation of unchanged throughput. Only the real cluster gate can
support a throughput claim.

## Explicit V1 exclusions

- Job arrays: separate jobs with their own lifecycle, not KAIROS's packed concurrent steps
  ([Job Arrays](https://slurm.schedmd.com/job_array.html)).
- Heterogeneous jobs: co-scheduled components add lifecycle and accounting complexity not needed
  for homogeneous single-node ML ([Heterogeneous Jobs](https://slurm.schedmd.com/heterogeneous_jobs.html)).
- Multi-node or elastic distributed training.
- Fractional GPUs, MPS, shards, MIG-specific orchestration, manual GPU-index assignment, and GPU
  frequency control.
- `--mem-per-cpu`, `--mem-per-gpu`, zero/all memory, whole-node exclusivity, overcommit, overlap,
  and oversubscription.
- Reservations, dependencies, licenses, nodelists, arbitrary signals, mail, priority, requeue,
  preemption policy, and interactive `salloc`.
- Arbitrary raw Slurm flags or `#SBATCH` directives.

These are future features only after two real projects need the same typed behavior. Production
readiness means the supported contract is safe, inspectable, documented, and tested—not that
Servatus mirrors every `sbatch` option.
