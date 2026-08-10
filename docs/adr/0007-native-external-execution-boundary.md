# ADR 0007: Native External Execution Boundary

## Status

Superseded by [ADR 0008](0008-servatus-lifecycle-boundary.md).

## Context

KAIROS needs one narrow path from a workstation to a CUDA Slurm host. Native OpenSSH, Slurm, and file-transfer tools provide the host boundary.

## Decision

KAIROS originally owned cwd-local target configuration, OpenSSH invocation, generated Slurm
scripts, allocation packing, and `sbatch` receipt parsing. Every process ran the same immutable
Apptainer image through one exclusive Slurm step and received exactly one GPU. Its runscript invoked
the installed `kairos` executable with a generated-job entry point. Workflow processes received one
strict `WorkflowRequest` directly; candidate processes received one strict record containing the
`TuneRequest` and Method index.

Submission ends when Slurm returns the job ID. Scheduler tools monitor jobs, and file-transfer tools move completed objects between hosts.

## Consequences

The submission interface stays small. Packing changes allocation efficiency, not scientific
execution: each fit or evaluation remains an isolated single-GPU process with its original
request, work, result, and resume behavior. Scientific requests and durable objects remain
independent of host, queue, log, and transfer state. The immutable image owns one KAIROS revision
plus its fixed loader and Torch runtime profile. ADR 0008 retains these boundaries while moving the
generic implementation to Servatus.
