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

KAIROS retains the application seam. Typed workflow and candidate inputs map directly to opaque
Servatus tasks. Hidden `kairos remote` commands hydrate those inputs and call KAIROS training or
evaluation owners. KAIROS also owns canonical completion checks, resource and target values,
immutable image contents, and every scientific request, association, schema, and manifest.

ADRs 0006 and 0009 remain authoritative for their canonical objects. KAIROS chooses each owned
destination, identity, file roster, and validation rule; Servatus implements the transaction that
preserves resumable work and publishes the assembled files without overwrite. Corpus production
remains external, and the Blockweaver-owned dataset boundary remains outside Servatus.

## Consequences

OpenSSH, Slurm, and Apptainer remain the native execution path through one external package.
Scientific requests and durable objects remain independent of target, queue, log, receipt, and
retry state. KAIROS contains no scheduler renderer, packing algorithm, campaign journal, workspace
implementation, compatibility path, or generic lifecycle schema.
