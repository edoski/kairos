# ADR 0008: Servatus Lifecycle Boundary

## Status

Accepted. Supersedes ADR 0007's implementation ownership.

## Context

KAIROS needs durable work and one workstation-to-Slurm execution path, but those mechanics do not
define its scientific objects. Keeping them in KAIROS duplicated reusable lifecycle code and made
the application own scheduler recovery and publication transactions.

## Decision

KAIROS uses [Servatus](https://github.com/edoski/servatus) for durable workspaces, atomic
publication, campaign state, packing, and native OpenSSH/Slurm/Apptainer submission.

KAIROS retains the application seam. One strict execution envelope maps typed Tune, Train, and
Evaluate inputs directly to opaque Servatus Tasks. Hidden `kairos remote worker` hydrates it and
calls KAIROS training or evaluation owners. One KAIROS result probe validates canonical results
while Servatus owns observation and retry eligibility. KAIROS also owns resource and target values,
immutable image contents, and every scientific request, association, schema, and manifest.

ADR 0006 remains authoritative for canonical objects. KAIROS chooses each destination, identity,
file roster, and validation rule; Servatus implements the transaction that preserves resumable or
disposable work and publishes assembled files without overwrite. Campaign Tasks are the sole
pre-publication experiment roster and Campaign state remains private execution history after
manifest publication. Corpus production remains external under ADR 0009.

## Consequences

OpenSSH, Slurm, and Apptainer remain the native execution path through one external package.
Scientific requests and durable objects remain independent of target, queue, log, receipt, and
retry state. KAIROS contains no scheduler renderer, packing algorithm, campaign journal, duplicate
completed-set join, workspace implementation, compatibility path, or generic lifecycle schema.
