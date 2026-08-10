# Servatus: Submitit Dependency Decision

**Status:** decision-ready

**Date:** 2026-08-10

**KAIROS baseline:** `56f24ae364a70ba704b56a01edbc43f90156fd3e`

**Submitit baseline:** `1.5.4`, tag commit `e49d5e7f3890c866cd3c75023cbf7b0954360469`

## Decision

Servatus should **not depend on Submitit**, even privately, for V1. Implement one narrow native
OpenSSH/Slurm adapter behind the Servatus `Campaign` interface.

Submitit is mature and useful. It is the wrong layer. Its public abstraction is a Python callable
serialized into a shared job folder, executed by a Submitit Python worker, and returned through a
serialized result. Servatus needs opaque commands and stdin, a workstation-to-cluster SSH boundary,
one allocation containing several independent application processes, durable submission ambiguity,
and application-owned completion. Using Submitit would retain all Servatus state and recovery code
while adding a second execution runtime and state tree.

This is not a rejection of external dependencies. It is a rejection of an abstraction mismatch.
If Servatus later becomes a cluster-local Python-callable launcher whose users need Slurm arrays,
distributed ranks, callable results, cancellation handles, and automatic requeue, revisit Submitit.

## Evidence scope

This decision uses Submitit 1.5.4, the latest PyPI release on the decision date. PyPI marks it
production/stable and lists `cloudpickle` and `typing_extensions` as runtime dependencies
([PyPI](https://pypi.org/project/submitit/),
[package metadata](https://github.com/facebookincubator/submitit/blob/1.5.4/pyproject.toml)). The
source inspection is pinned to the 1.5.4 tag rather than `main`.

The KAIROS comparison is pinned to the baseline above. Current user-owned worktree changes are not
part of this decision.

## Required Servatus contract

Servatus must extract mechanics without taking application meaning from KAIROS:

- Submission begins on a workstation, crosses one noninteractive OpenSSH boundary, and invokes one
  `sbatch` per allocation ([KAIROS execution](../../src/kairos/execution.py#L84-L92),
  [ADR 0007](../adr/0007-native-external-execution-boundary.md#decision)).
- One allocation contains one to four ordered, independent processes. Each gets distinct opaque
  input, one GPU, its CPU and memory share, an exclusive exact `srun` step, and a per-slot log
  ([KAIROS execution](../../src/kairos/execution.py#L95-L140)).
- Pending work is packed into the fewest balanced allocations. Nine tasks at capacity four become
  `3 + 3 + 3`, avoiding a singleton tail
  ([launcher](../../experiments/launch.py#L75-L102),
  [packing tests](../../tests/experiments/test_launch.py#L124-L168)).
- Submission state is durable before the operator trusts it. The current launcher flushes and
  syncs accepted rows, but still has an acceptance gap between `sbatch` and that sync
  ([launcher](../../experiments/launch.py#L83-L96)). Servatus must close or truthfully expose that
  gap.
- The application defines completion from canonical scientific objects. Scheduler success is not
  scientific completion ([launcher](../../experiments/launch.py#L27-L49),
  [ADR 0006](../adr/0006-direct-durable-object-authority.md#decision)).
- Interrupted model fitting resumes from application scratch and Lightning `last.ckpt`; the
  scheduler layer does not own model state
  ([modeling](../../src/kairos/modeling.py#L270-L333)).
- Publication happens only after application validation, atomically exposes a complete directory,
  and removes resumable scratch only after commit
  ([ADR 0006](../adr/0006-direct-durable-object-authority.md#decision)).

The generic Servatus task is therefore an identity plus argv and stdin bytes. It is not a Python
callable, a return value, or a workflow node.

## What Submitit actually owns

Submitit's public path is:

```text
Python callable + arguments
  -> cloudpickle submission in a shared folder
  -> generated batch script
  -> local sbatch
  -> srun Python -m submitit.core._submit
  -> unpickle and invoke callable
  -> pickle success/error result
  -> Job reads sacct, logs, and result pickle
```

The official structure guide states that functions, arguments, and outputs are pickled and that
Submitit must exist in the worker environment
([structure](https://github.com/facebookincubator/submitit/blob/1.5.4/docs/structure.md#under-the-hood)).
`SlurmExecutor` requires a shared folder, selects a Python command, checks for local `srun`, and
submits `python -m submitit.core._submit`
([executor](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/slurm/slurm.py#L211-L258),
[worker command](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/slurm/slurm.py#L353-L366)).
The worker waits for the submitted pickle, executes it, then writes a result pickle
([worker](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/submission.py#L24-L69)).

Submitit provides real value:

- common Slurm option rendering plus escape hatches for additional options;
- job IDs, state, logs, cancellation, and callable exception recovery;
- job arrays with parallelism limits;
- local and in-process debug executors;
- rank and node environment information;
- signal-driven checkpoint and requeue support.

Those features are mature. Most are outside Servatus V1, and the in-scope pieces do not compose
cleanly with its contract.

Its command helper does not bridge the gap. `CommandFunction` has no stdin input and buffers full
stdout and stderr in memory, so long-running ML commands need a custom subprocess wrapper anyway
([command helper](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/utils.py#L285-L360)).
Its status watcher caches finished states and suppresses `sacct` failures with a warning that status
may be inaccurate; Servatus must instead expose an unavailable or ambiguous status truthfully
([watcher](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/core.py#L73-L145)).

## The best feasible Submitit architecture

Submitit cannot run in the workstation process because its Slurm executor invokes local `sbatch`,
`sacct`, `scancel`, and `srun`. The least-wrong integration is a remote Python driver:

```text
workstation
  Servatus Campaign
    1. fsync allocation intent
    2. ssh cluster "servatus _submit <allocation-id>"

cluster login node
  remote Servatus + Submitit driver
    3. create shared Submitit job folder
    4. configure SlurmExecutor
    5. submit rank-dispatch callable
    6. persist Submitit job ID
    7. return Servatus receipt

compute node
  Submitit worker Python
    8. load shared pickle
    9. choose task by SLURM_LOCALID
   10. invoke Apptainer application with that task's stdin
   11. write Submitit result pickle
```

For `N` tasks in one allocation, `tasks_per_node=N` launches the same submitted callable at every
rank; the callable must inspect the rank and select one payload. Submitit's multi-submission path is
not an alternative: more than one delayed submission becomes a Slurm job array
([array implementation](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/slurm/slurm.py#L321-L351)).
A job array creates separately schedulable array elements, not one packed allocation containing N
independent steps
([Slurm arrays](https://slurm.schedmd.com/job_array.html)).

This integration has two variants, both poor fits:

1. **One Submitit `srun`, N ranks.** The rank wrapper selects distinct tasks. This changes KAIROS's
   N independent exclusive steps into one multi-rank step and requires Servatus and Submitit in the
   worker Python environment.
2. **Disable Submitit's `srun`, then launch N exclusive steps from the callable.** This preserves
   KAIROS semantics, but Servatus must recreate its current process supervisor and `srun` rendering.
   Submitit is then used mainly for `#SBATCH` rendering and `sbatch` invocation.

Container placement also has no clean answer:

- Run the Submitit worker outside the application image: the cluster must provide a shared,
  version-pinned Servatus/Submitit Python installation on every compute node.
- Run it inside the image using Submitit's custom `python` command: every application image must
  contain matching Servatus, Submitit, `cloudpickle`, and a Python entry point before the application
  can start. The executor supports a custom Python shell command, including container launchers, but
  the caller owns its correctness
  ([executor `python`](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/slurm/slurm.py#L218-L258)).

Either choice weakens Servatus's useful process boundary: an application image should implement an
argv/stdin contract, not embed the scheduler client library.

## Feasibility and crash probe

A throwaway probe used real Submitit 1.5.4 with fake `sbatch` and `srun` executables. It configured
one node, three tasks, one GPU per task, `--exclusive --exact`, and a custom
`apptainer exec --nv ... python` command. The generated script contained every requested resource
and container fragment. Three simulated Slurm ranks loaded the same submitted callable, selected by
`SLURM_LOCALID`, and returned three distinct opaque payloads. The remote-driver architecture is
therefore technically feasible.

A second probe injected a process failure immediately after fake `sbatch` returned accepted job ID
`4242`. Files left behind were one UUID-named temporary pickle and one temporary submission script.
The worker path `jobs/4242/4242_submitted.pkl` did not exist. This reproduces the source-level race
below: feasibility does not provide the required durability.

The probe exercised script generation and Submitit's local worker dispatch only. It did not claim a
real Slurm, SSH, GPU, or Apptainer run.

## Failure semantics

Submitit does not close Servatus's dangerous submission gap. It adds a second one.

| Failure point | Native Servatus adapter | Submitit-backed adapter |
| --- | --- | --- |
| Before SSH | Durable intent, no remote effect | Same |
| SSH fails before controller acceptance | Intent remains retryable after resolution | Same, plus remote driver state |
| Controller accepts but reply is lost | Job has the complete submitted batch script; Servatus resolves the deterministic allocation identity or stays ambiguous | Same acceptance ambiguity; Submitit has no idempotent submission token |
| Driver dies after `sbatch` but before job files are finalized | Not applicable when the script is sent directly to `sbatch` stdin | Accepted job may not have its expected submitted pickle or recorded `Job` handle |
| Worker starts | Needs Slurm, Apptainer, immutable image, and application storage | Also needs shared Submitit files and compatible Submitit/cloudpickle worker code |
| Application finishes but Submitit result write fails | Application completion probe remains authoritative | Scheduler/Submitit can report failure although the canonical application object is complete |
| Preemption or timeout | Application scratch survives; explicit resubmission resumes each unfinished task | Submitit signals and requeues the allocation through a callable protocol; completed siblings may rerun and external child-process signaling needs adapter logic |
| Cleanup | Servatus removes its own campaign state under its lifecycle rules | Servatus must also retain or clean scripts, input pickles, result pickles, and Submitit logs |

The accepted-job race is visible in Submitit's source. It invokes `sbatch`, parses the job ID, moves
the generated script, and only afterward moves the temporary callable pickle to the job-ID path
([submission sequence](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/core.py#L891-L916),
[`sbatch` sequence](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/core.py#L927-L961)).
The worker waits up to 60 seconds for that pickle, then fails
([worker wait](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/submission.py#L36-L48)).
The pickle write and promotion use ordinary write and rename operations without file or directory
syncing
([pickle write](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/utils.py#L229-L237),
[promotion](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/utils.py#L96-L102)).

Submitit checkpointing is also application-coupled rather than free resilience. A callable must
provide a checkpoint method returning a new `DelayedSubmission`; the cluster must send the expected
user signal, and the application must skip prior work after rescheduling
([checkpointing guide](https://github.com/facebookincubator/submitit/blob/1.5.4/docs/checkpointing.md)).
Its signal handler acts only on rank zero and requeues the Slurm job
([signal handler](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/job_environment.py#L169-L251)).
That does not replace per-task Lightning checkpoints or Servatus workspaces.

## Operational requirements with Submitit

A private Submitit backend would require all of the following:

- a remotely installed, version-pinned Servatus driver;
- Submitit and `cloudpickle` on the login node;
- compatible Submitit, `cloudpickle`, Python, and callable modules in the worker runtime;
- a shared writable folder visible before submission and from every compute node;
- ownership, retention, and cleanup rules for Submitit scripts, pickles, results, and logs;
- a rank-dispatch wrapper or a replacement multi-step supervisor;
- translation from Submitit jobs and errors into stable Servatus types;
- Servatus's own durable intent, receipt, retry, and ambiguity state around Submitit;
- direct remote tooling or serialized job handles for later status and cancellation;
- cluster signal configuration before relying on Submitit preemption behavior.

Submitit's own tips warn that the shared folder is mandatory, fills quickly, has no cleaning
mechanism, and that module changes between submission and execution can change or break the job
([tips](https://github.com/facebookincubator/submitit/blob/1.5.4/docs/tips.md)). Immutable images
reduce the module-drift risk but increase the requirement that every image include the Submitit
worker stack.

## Comparative result

| Criterion | Native private Slurm adapter | Private Submitit backend |
| --- | --- | --- |
| Exact packed-allocation contract | Direct | Requires rank wrapper or bypass |
| Opaque argv/stdin tasks | Direct | Must adapt through pickled callable |
| Workstation-to-Slurm SSH | One native boundary | Remote Python service/command required |
| Accepted submission payload | Batch script retained by Slurm controller | Batch script plus separately finalized shared pickle |
| Durable ambiguity | Servatus must implement once | Servatus must implement around Submitit |
| Application completion | One authority | Must override Submitit result semantics |
| Resumable workspace/publication | Servatus | Servatus; Submitit adds nothing |
| Status/cancel/log helpers | Small native commands | Strong Submitit support, but remote translation required |
| Arrays/distributed ranks/requeue | Future work or non-goal | Strong Submitit support |
| Runtime dependencies | Python standard library plus native tools | Submitit, cloudpickle, typing extensions, remote worker stack |
| State trees | Servatus campaign/workspace | Servatus plus Submitit folder |
| Slurm code maintained by Servatus | Small renderer and command adapter | Less flag rendering, more integration and lifecycle code |

Submitit wins only in capabilities Servatus does not currently want. It loses on every defining
Servatus boundary.

## Native adapter shape

Keep one private `_slurm.py` module. Do not create a scheduler plugin framework before a second
scheduler is required.

```text
Campaign.submit
  1. freeze ordered task identities and balanced allocation plan
  2. write and fsync local intent with unique allocation ID and script digest
  3. render one deterministic, self-contained batch script
  4. ssh -T -o BatchMode=yes HOST sbatch --parsable
  5. parse positive job ID and optional cluster name
  6. write and fsync receipt

Campaign.resolve
  1. query squeue for the unique allocation job name
  2. query sacct over the intent's bounded submission window if accounting is available
  3. accept exactly one matching job, accept explicit operator `not-submitted`, or remain ambiguous
```

Slurm documents that `sbatch` accepts the script on stdin, returns after the controller has accepted
the script and assigned a job ID, and moves no other user files
([`sbatch` behavior](https://slurm.schedmd.com/sbatch.html#DESCRIPTION)). `--parsable` returns only
the job ID and optional cluster name
([`--parsable`](https://slurm.schedmd.com/sbatch.html#OPT_parsable)). `squeue` and `sacct` both
support job-name queries; completed-job resolution through `sacct` remains conditional on cluster
accounting and the requested time range
([`squeue --name`](https://slurm.schedmd.com/squeue.html#OPT_name),
[`sacct --name`](https://slurm.schedmd.com/sacct.html#OPT_name)). If resolution cannot prove one
answer, Servatus fails closed and requires explicit operator resolution.

This is more resilient than current KAIROS without pretending to provide exactly-once scheduler
submission. It also stays smaller than the Submitit integration because the Slurm CLI is already the
stable system boundary.

## Why not use only Submitit's script renderer?

That would capture the attractive part without the runtime, but it is not a supported public layer.
The renderer is `_make_sbatch_string`, and submission customization uses protected executor methods
([renderer](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/slurm/slurm.py#L395-L535),
[executor base](https://github.com/facebookincubator/submitit/blob/1.5.4/submitit/core/core.py#L651-L743)).
Depending on those internals would buy tens of lines of formatting at the cost of version-sensitive
coupling.

Submitit's plugin API does not fix this. A plugin must provide an Executor, Job, InfoWatcher, and
JobEnvironment ([plugin guide](https://github.com/facebookincubator/submitit/blob/1.5.4/docs/plugins.md)).
An SSH-aware Servatus plugin would reimplement the remote state, status, and environment layers that
Servatus already owns.

## Code and maintenance effect

Both designs let KAIROS remove the same generic infrastructure: `kairos.execution`, campaign
packing/journaling, and most mechanics tests. Submitit therefore does not make KAIROS leaner than a
native Servatus adapter.

Inside Servatus, Submitit can remove a small batch-header renderer, one `sbatch` invocation, job-ID
parsing, and some optional `sacct`/`scancel` helpers. It adds the remote driver, rank dispatch,
worker-runtime installation, shared-folder ownership, cleanup, state translation, and tests for the
two interacting lifecycle systems. Net Servatus code and operational surface increase.

Submitit remains a healthy reference implementation. Reuse its ideas and validate against its
behavior; do not reuse its runtime.

## Reconsideration triggers

Reopen this decision only if at least one product requirement changes:

- submission normally occurs on a Slurm login node rather than through SSH;
- the public task becomes a Python callable and Submitit owns its returned value;
- job arrays are preferred over packed multi-GPU allocations;
- distributed same-callable multi-rank jobs become the primary workload;
- automatic Submitit checkpoint/requeue becomes authoritative for work recovery;
- live job handles, cancellation, and remote exception retrieval become core enough to justify the
  Submitit worker runtime.

Until then, the optimal Servatus architecture is native OpenSSH/Slurm plus Servatus-owned durable
campaign state and workspace publication.
