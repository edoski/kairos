# Lean codebase implementation-review ledger

Status: planning only; implementation paused pending approval of the proposed substantial slices

Authority: two codebase-wide audits, initially pinned to
`6da8bf7e2ba1304f9ac009472c96965f89265838` and re-audited at
`1c3745fddb93e85ff5d84e596ccf78f47ff9113b`, plus the user's 2026-08-09 annotations.
Product code did not change between those pins. This ledger is the slice review Spec. `AGENTS.md`,
`docs/CONTEXT.md`, ADR 0006, and ADR 0007 are the Standards sources.

## Pre-run state

- Checkout: `/Users/edo/dev/python/kairos`
- Branch: `main`
- Planning baseline: `6da8bf7e2ba1304f9ac009472c96965f89265838`
- Worktrees: one existing `main` worktree; no run-owned branch or worktree
- Protected unrelated state: untracked `tmp/`
- Proposed checkout policy: direct `main`, one writer at a time, no branch or worktree
- Run-owned planning file: `docs/lean-codebase-implrevloop.md`
- Authorized in this phase: this planning ledger only
- Not authorized in this phase: product implementation, ignored-environment recreation, native
  regeneration, remote jobs, image builds, RPC calls, device runs, pushes, or pull requests
- Execution protocol after approval: one fresh implementer per slice, then one separate fresh
  reviewer using `code-review`; rejected findings return to the same implementer and reviewer until
  zero-finding `GREEN LIGHT`
- This ledger is temporary review state. Remove it only after every approved slice and the final
  repository verification are green.

## User decisions already fixed

- Process-wide native model-operation serialization is approved as the remaining high-priority
  fix.
- Direct minimum-outcome vectorization is approved with its roughly 341 MiB largest-authored-window
  temporary-memory tradeoff; values and first-tie behavior must remain exact.
- Balanced allocation packing is retained. Sustained and tail GPU occupancy take priority over the
  line reduction from ordinary chunking.
- Temporary `jobs.tsv` retains its human-readable `cell` field so failed Slurm rows remain direct
  to identify and resubmit. The one-owner `_Resources` flattening remains independent.
- Removing powermetrics liveness polling from the measured active loop is approved. Health checks
  remain before and after each phase so collector failure still invalidates the measurement.
- The implementation sequence is consolidated from nine narrow slices into four larger ownership
  slices. No accepted, proposed, protected, rejected, or externally gated item is dropped.
- The proposed held-out K-study roster guard is rejected after tracing the authoring chain. HPO
  publication requires nine cells, K-study authoring expands them through its fixed nine horizons,
  and closure verifies every artifact. Held-out should trust that canonical manifest.
- The small mechanical sweep is approved only where scientific semantics and thesis data outputs
  remain unchanged.
- Accessibility expansion is rejected. KAIROS is a no-user thesis demo; do not add accessibility
  semantics, wrappers, or tests.
- Raw-input, scientific, durable-publication, native-runtime, race, and external-adapter guards
  listed below remain protected.
- The substantial cleanup set is not yet treated as approved. This ledger separates actual
  simplification from line-increasing correctness work so it can be approved precisely.
- License decision is fixed: remove the unsupported MIT metadata claim and add no license file or
  replacement claim.

## Design rule

Trust typed, publisher-owned internal values. Validate once at the boundary that owns the fact.
Keep direct code even when a more elaborate abstraction could optimize a rare case. Do not remove
guards at raw RPC, disk hydration, scientific protocol, numerical, atomic publication, native
runtime, concurrent state, or shell/scheduler boundaries.

## Line-count and leanness classification

Counts are directional estimates, not quotas. Exact deltas are recorded after each implementation
commit. Test-deletion estimates overlap where noted.

| Change | Expected tracked LOC | Simpler design? | Planning decision |
| --- | ---: | --- | --- |
| Trust canonical K-study authorship and delete the manual partial-manifest test | Tests `-20..30`; production neutral | Yes. Held-out keeps deriving its geometry from its canonical input. | Approved output-neutral cleanup |
| One module-level native operation queue plus cross-runtime test | Production neutral, tests `+20..35` | Yes. One owner matches one process-global native resource. | Approved high priority |
| Remove retention-time Study revalidation | Production `-1`, tests neutral | Yes. Publication remains the sole durable authority. | Recommend |
| Reject a known evaluation collision before inference | Roughly neutral; mostly moved code | Yes. The control flow states the real precondition first. | Recommend |
| Add another late bundle collision refusal | Program delta `0` | No. It duplicates the early check, narrows but does not eliminate the race, and covers implausible concurrent publication of one minted UUID. | Rejected |
| Trust canonical experiment/figure manifests and remove internal Study, roster, label, and completeness rechecks | Production `-70..95`, tests `-75..85` | Yes. Fixed upstream authors own these facts. | Recommend |
| Retain balanced allocation packing | Neutral | Yes. The existing fewest-allocation policy avoids avoidable singleton tails and protects GPU occupancy. | Approved retention |
| Flatten the one-owner remote resource record | Production/config `-3..5` | Yes. The behavior-free nested record has one owner and one consumer. | Recommend; retain the job-journal cell label |
| Quote the Slurm allocation log path | Neutral | No material simplification; fixes one external-adapter defect. | Recommend as correctness work |
| Remove benchmark liveness polling from the measured active loop | Production/tests `-5..15` | Yes. The measured region contains computation, while phase-boundary health checks remain. | Approved |
| Remove canonical-manifest revalidation from benchmark setup | Production `-25..35`, tests `-15..25` | Yes. Campaign setup becomes direct while the two-ID association guard stays. | Recommend |
| Remove dead training-loss metric collection and repeated derived training definitions | Production/tests `-10..20` | Yes. Nothing consumes the metric; one hydrated definition remains. | Recommend |
| Move bundle mechanics to owner tests and shrink downstream pipeline monoliths | Tests `-105..145` net; estimates overlap | Yes. Tests stop replaying trusted upstream modules while one compact integration smoke stays. | Recommend |
| Localize app styles | Production `0..+10`; about 300 lines move | No. The current file already has coherent screen blocks; moving them adds namespaces and files. | Rejected |
| Add local accessibility semantics and focused tests | Program delta `0` | No. This expands a no-user demo. | Rejected |
| Remove shallow app wrappers/constants, unused exports, impossible chart guards, and choreography assertions | Production `-15..25`, tests `-25..40` | Yes. | Approved if output-neutral |
| Vectorize minimum-outcome calculation in one expression | Production `-7` | Yes. It removes arbitrary chunk policy; peak temporary memory rises to about 341 MiB for the largest authored window. | Approved with resource tradeoff |
| Remove redundant strict flags, casts, internal equal-length checks, one-call helpers, inert checkpoint options, and test ceremony | Production/tests `-45..85` | Yes. | Approved if output-neutral |
| Delete repository-unused `reduce_artifact_validation()` and its prose/test call | Production/docs/tests `-10..20` | Yes. Existing loaders/reducer own all behavior. | Recommend clean break |
| Delete the completed validation-evidence process ledger after moving its still-live protocol facts into canonical docs | Documentation `-369` | Yes. Git retains implementation history; active contracts belong in `KAIROS.md`, `CONTEXT.md`, and ADRs. | Recommend after contract check |
| Add direct exporter dependency | Metadata/lock roughly `+3` | No. It fixes packaging ownership. | Recommend as completeness work |
| Remove the unsupported MIT metadata claim | Metadata `-1` | Yes, narrowly: the package stops claiming authority not established by a license file or ownership decision. | Approved |
| Repair the stale research citation and context-study prose | Neutral to small increase | No code simplification. It restores contract accuracy. | Recommend |

The meaningful additions are the native cross-runtime lifecycle test, a split early/late Evaluation
collision test, and exporter dependency metadata/lock entries. Production queue ownership merely
moves. The Evaluation preflight adds about two production lines to put a real precondition before
expensive work. No new production validation machinery remains in the plan.

### Estimated net program delta

This estimate excludes this temporary ledger and ignored/generated environment state. It counts
overlapping experiment-test deletions only once.

- Production, configuration, and current durable documentation: roughly 110–180 fewer lines.
- Tests: roughly 220–300 fewer lines. The main reduction is replacing downstream pipeline
  monoliths and tampering/choreography matrices with owner tests.
- Completed process-ledger residue: 369 fewer documentation lines after its live facts are checked
  into canonical documentation.
- Total: roughly **700–850 fewer tracked lines**, with a planning midpoint near **775 fewer lines**.

The estimate assumes accessibility stays excluded and the MIT metadata claim is removed. Exact
deltas are recorded per implementation commit; deletion count is not an acceptance criterion.

### License recommendation

The [University of Bologna IP regulation](https://normateneo.unibo.it/regolamento-in-materia-di-proprieta-industriale-e-intellettuale-delluniversita-di-bologna)
treats software as an intangible asset and states that rights to student-created software can
belong to the University when it is produced within University educational/research activity using
authorized University structures or resources. KAIROS is a thesis project using University
research infrastructure, so personal ownership is not safe to assume.

Remove `license = { text = "MIT" }` from `pyproject.toml` for now. Do not add an unlicensed-code
notice or another license. If the supervisor/KTO later confirms who owns the software and authorizes
open-source release, MIT is the leanest permissive choice; add the standard MIT text with the
confirmed rights holder then. If academic citation becomes useful, handle it separately with a
`CITATION.cff`; MIT itself does not establish a citation request.

## Protected guards

The following are out of deletion scope unless a later demonstrated contract change is approved:

- strict raw JSON/YAML/RPC/CLI hydration and forbidden-extra-field behavior;
- exact ordered schemas, dtypes, UUID/typed associations, feature width, and artifact identity;
- causal training/validation/testing separation, predecessor support, fixed scientific rosters,
  rolling-origin coverage, action range, and exact metric definitions;
- finite feature, target, prediction, validation, and model-output checks;
- full-state `last.ckpt` resume, selected-checkpoint evidence, and objective/evidence equality;
- early and late collision refusal, scratch preservation, atomic publication, and no overwrite;
- exact RPC bigint conversion, fee-history tuple/count/origin, parent continuity, and positive fees;
- native tensor count/type/shape/length/finiteness, copied outputs, artifact caching, and disposal;
- app history/selection queues, stale-result currentness checks, retryable sibling outcomes, and
  rejection-safe queue continuation;
- Slurm/YAML/stdin/subprocess parsing, positive job IDs, shell quoting, per-step GPU isolation, and
  golden external script behavior;
- ExecuTorch/XNNPACK export and native parity gates.

## Pre-implementation gate: generated local state

The tracked tree has no FABLE residue. Ignored `.venv`, `tools/mobile-export/.venv`, and generated
iOS/Pods state still contain pre-rename absolute paths. They currently break the exact executable
forms of `uv run vulture`, `uv run pytest`, and the default exporter test.

After implementation authorization, recreate these generated environments cleanly; add no shim.
Snapshot the protected `tmp/` path first and do not touch it. This is recoverable workspace work,
not a product commit. Record the recreation commands and prove the normal commands work before the
first slice. Regenerate iOS/Pods state only before native iOS verification.

## Consolidation map

| Previous slices | Consolidated owner |
| --- | --- |
| 4 plus core/modeling parts of 9 | Slice 1 — scientific core and durable ownership |
| 1, 3, and 7 plus experiment/docs parts of 9 | Slice 2 — experiment pipeline, figures, tests, and canonical documentation |
| 5 and 6 plus execution/exporter parts of 9 | Slice 3 — operational execution, benchmark, and mobile exporter |
| 2 and 8 plus app parts of 9 | Slice 4 — App native lifecycle and shallow cleanup |

## Slice 1 — Scientific core and durable ownership

Status: direct outcome vectorization and previously scoped output-neutral mechanics approved;
remaining ownership cleanup proposed, awaiting approval

### Scope

- Compute minimum outcomes in one direct matrix expression instead of arbitrary 4,096-row chunks.
  Preserve exact values and first-tie behavior; accept about 341 MiB temporary peak memory for the
  largest authored window.
- Inline the two owner-specific uniqueness checks and remove `_require_unique`. Remove redundant
  internal `np.int64` casts, `zip(strict=True)`, and strict call flags only where typed owners
  already prove dtype, length, or strict hydration.
- Let `decode_action` own action-logit finiteness; observation collection keeps its independent
  minimum-fee finiteness check. Remove the test-side `self.eval()` setup that currently makes the
  production-owned evaluation-mode assertion vacuous.
- Remove unused `training_total_loss` epoch logging while keeping the identical per-batch
  classification-plus-regression loss for backpropagation. Keep validation loss, validation
  optimality gap, finite checks, early stopping, and selected-objective evidence.
- Derive one `TrainingDefinition` per artifact fit, preserving seeding before module construction.
  Remove inert `auto_insert_metric_name=False` from the literal `last` checkpoint,
  schema-irrelevant fixture rows, and assertions that pin Lightning choreography instead of results.
- Remove retention-time `_validate_trial()` and redundant Study zip strictness; reuse the already
  loaded first candidate. Publication remains the durable trial-validation owner.
- Reject a known Evaluation collision before loading/inference while retaining its late race guard.
- Delete repository-unused `reduce_artifact_validation()`, its API prose/test call, and any helper
  left with one caller, including `_load_artifact_result` if applicable. Canonical artifact loading
  and observation reduction remain authoritative.

### Non-goals

- No schema, dtype, feature, target, loss, prediction, action, metric, checkpoint, evidence,
  association, scratch, or durable-object layout change.
- No bypass of `BlockFrame.select_range()` or constructor validation through flags, private
  constructors, or `object.__new__`.
- No private-helper rename sweep, uniform extra candidate reload, compatibility wrapper, or second
  experiment-bundle collision check.
- No removal of raw/disk, causal, numerical, publication, resume, or selected-evidence guards.

### Protected behavior and accepted change

- Scientific and thesis-facing values remain identical. Minimum-outcome parity includes first ties.
- The training objective still drives the same gradients; only its unused epoch copy disappears.
- Known Evaluation collisions fail before expensive work and create no scratch. Late races still
  preserve scratch.
- Publication still validates exact requests, trials, checkpoints, observations, and objectives.

### Expected outcome

The Python scientific core has one owner for each invariant, one derived training definition, and
no unused metric or repeated trusted-value ceremony.

### Checks

- Capture small temporary fixtures for temporal outputs, observation reduction, Study selection,
  checkpoint naming, and artifact loading; compare before and after without adding permanent goldens.
- Representative memory check for the largest authored outcome geometry.
- Focused temporal, configuration, modeling, Study, artifact, and Evaluation tests.
- Early and late Evaluation collision behavior, interruption/resume, and objective/evidence parity.
- Full Python suite, Ruff, format, Pyright, configured Vulture with manual classification, and diff
  check. Any scientific-output difference rejects the individual cleanup.

### Dependencies and gates

- Runs after generated-environment preflight.
- No Corpus, Study, artifact, Evaluation, experiment, scratch, or remote state may be mutated.

## Slice 2 — Trusted experiment pipeline, figures, tests, and canonical documentation

Status: canonical K-study trust cleanup and MIT-claim removal approved; remaining experiment and
documentation cleanup proposed, awaiting approval

### Scope

- Keep held-out deriving horizons and maximum horizon from the canonical K-study manifest. Add no
  hard-coded roster or separate `K=200` authority; delete the manufactured 72-cell test.
- Remove `c_study` expected-set and family/context/source/Method revalidation, including its second
  `C=25` assertion. Keep the frozen context-selection rule.
- In all four figure scripts, remove curated label-parse errors, one-trial rechecks, inferred
  completeness checks, impossible empty/loop-result guards, and fallbacks for canonical style and
  feature labels. Keep every plotting calculation and valid-data branch.
- Trust fixed producers to emit unique fresh tune-cell labels. Keep the intersection check used by
  normal HPO `extend` against an existing active bundle.
- Move generic `publish_bundle` and `close_bundle` behavior to focused owner tests. Cover reporting
  once through a public stage command, build minimal typed upstream fixtures directly, retain one
  compact whole-pipeline smoke, and delete repeated serialization/publication choreography and
  upstream replay.
- Delete manual-corruption matrices for context Studies, partial closed feature/K-study manifests,
  benchmark horizon labels, and other states fixed canonical publishers cannot emit. Keep roster,
  selection, window, reducer, collision, resume, and deterministic-figure assertions at their owner.
- Remove redundant experiment strict flags and test constructor ceremony where record
  configuration/defaults already own them.
- Correct `docs/KAIROS.md` to `C=25`, 13 contexts, 117 cells, nine reused Studies, 108 new Studies,
  and the 5% chain-mean rule; repair the stale research citation.
- After every still-live fact is present in canonical docs, delete the completed 369-line
  validation-evidence process ledger. Remove the unsupported MIT metadata claim and add no license.

### Non-goals

- No scientific roster, feature/context/HPO selection, window, reducer, figure appearance,
  canonical object, or report-value change.
- No generic cell-label validator, shared figure CLI helper, or production extraction solely to
  shorten tests.
- Keep HPO `select()`'s exact nine-cell final check because partial `prepare --chain`/`extend`
  authoring is supported. Keep strict manifest/Study hydration and canonical closure verification.
- No experiment authoring, launch, closure, output replacement, or license/ownership assertion.

### Protected behavior and accepted change

- Exact fixed rosters, windows, selections, atomic publication, interruption/resume, reductions,
  deterministic figures, and one end-to-end path remain covered.
- Complete canonical manifests, tables, reports, and figures remain identical. Manually edited
  canonical objects may fail later with ordinary lookup/loader errors instead of tailored messages.
- Git retains implementation history after the completed process ledger is removed.

### Expected outcome

Experiments and figures trust canonical upstream publishers, tests verify behavior at its owner, and
canonical documentation contains the live scientific contract without completed process residue.

### Checks

- Exact 81-cell K-study roster, held-out windows, 117-cell context protocol, HPO selection, and
  manifest round trips.
- Byte-compare deterministic vector PDFs from a small canonical fixture.
- Record affected test count, coverage ownership, and elapsed time before and after.
- Focused experiment, bundle, figure, reducer, and documentation checks; full Python suite plus
  Ruff, format, Pyright, configured Vulture, and diff check.

### Dependencies and gates

- Runs after Slice 1 so tests and experiment consumers target final core owners.
- No canonical outputs, queued jobs, live campaigns, or remote objects may be altered.

## Slice 3 — Operational execution, benchmark, and mobile exporter

Status: benchmark measured-loop polling removal approved; balanced packing and recovery retention
fixed; remaining operational cleanup proposed, awaiting approval

### Scope

- Retain balanced `_allocation_sizes()`, one-to-four processes, one GPU per exclusive step, and the
  fewest allocations without avoidable singleton tails. Retain `job_id`, `slot`, `row`, and `cell`
  in `jobs.tsv` for direct failed-row diagnosis and resubmission.
- Replace count-bearing `gres` plus `_scaled_gres()` with count-free `gres_name`; render `:1` per
  step and `:<task_count>` per allocation. Flatten the behavior-free `_Resources` record into
  `_Remote` while keeping every raw resource value configurable and strictly hydrated.
- Quote the allocation-level Slurm output path. Remove duplicated strict flags, default workflow
  discriminator arguments, and the lone direct CLI runner from typed fixtures.
- Remove `process.poll()` liveness checks from each measured active-loop cascade while retaining
  collector checks before and after every phase.
- Trust canonical benchmark publishers: remove reconstructed nine-group/36-label and artifact
  horizon revalidation, load one Corpus per canonical architecture/chain group, and keep the
  two-experiment artifact/evaluation join plus same-origin and coverage checks.
- Remove repeated `model.eval()`. Give powermetrics `sample_rate_ms` and energy settings one owner;
  use one concrete internal settings dictionary without defensive copies. Trust atomic energy
  publication instead of rescanning its file inventory; keep raw settings equality on resume.
- Remove benchmark tests for storage-pointer identity and transition-era protocol field order while
  retaining values, shapes, chronology, protocol round-trip/mismatch, and resume behavior.
- Replace derived first-horizon indexing with the existing horizon constant.
- Remove the exporter Corpus-request cache and inline its one-call feature-contract copier while
  retaining `_FeatureContract`. Remove internal equal-length ceremony only for locally paired
  sequences; keep raw roster TypeAdapter, Torch export, manifest-width, native-output, delegation,
  parity, chain, horizon, and shared-feature gates.
- Delete the raw-byte XNNPACK substring assertion after real delegation inspection and host
  execution. Declare Pydantic directly in the exporter and regenerate its lock once.
- Update affected operator documentation and the golden Slurm script.

### Non-goals

- No allocation-packing, job-recovery, SSH, scheduler, queue, resource quantity, request payload,
  scientific-execution, timing statistic, energy equation, rolling policy, batch, warmup, duration,
  output schema, artifact selection, or existing-output change.
- No generic scheduler, benchmark database, measurement abstraction, or compatibility layer.
- No `deploy/Apptainer.def` edit. Any future change requires explicit remote authorization, an
  immutable `sbuild`, and `apptainer test`.

### Protected behavior and accepted change

- Balanced packing preserves sustained and tail GPU occupancy. Submission failures leave later
  groups pending; failed submitted rows can be pruned and resubmitted with candidate scratch intact.
- For identical inputs and remote resource values, the generated script must request the same
  allocation count/sizes, partition, task count, total GRES name/count, one GPU per `srun` step,
  CPUs, memory, and time limit. Flattening configuration may not change schedulable capacity.
- Poll removal intentionally makes future latency/energy values measure the declared computation
  more faithfully. Powermetrics failure still invalidates the phase; existing thesis data stays
  untouched.
- Strict YAML/env/stdin/subprocess/job-ID parsing, generated Bash behavior, benchmark scientific
  quantity, atomic resume/publication, and native exporter parity remain.

### Expected outcome

Operational Python has direct GPU resource ownership, an interference-free measured loop, trusted
canonical setup, and a smaller exporter without sacrificing throughput, recovery, or native gates.

### Checks

- Balanced one-to-four-task allocation matrix, journal recovery, spaced log path, GRES rendering,
  positive job IDs, aggregate process failure, golden script, and `bash -n`.
- Before/after Slurm-script comparison proving exact resource-request equivalence; the only allowed
  script delta is correct quoting where the existing path expression is unsafe.
- Benchmark protocol, timing boundary, measurement, resume, reduction, mismatched-ID, same-origin,
  coverage, powermetrics failure, and atomic publication tests.
- Exporter suite through its normal regenerated environment, including real XNNPACK delegation and
  host execution; no PATH workaround.
- CLI help, full Python suite, Ruff, format, Pyright, configured Vulture, lock/diff checks.

### Dependencies and gates

- Runs after Slice 2 so benchmark and exporter tests consume the final canonical experiment shape.
- No scheduler/login-node access, live powermetrics campaign, thesis result regeneration, model
  export, device run, image build, or external submission is authorized.

## Slice 4 — App native lifecycle and shallow cleanup

Status: process-wide native serialization approved; remaining output-neutral cleanup proposed,
awaiting approval

### Scope

- Move the native-operation serial queue in `app/src/model.ts` from runtime-instance to module
  ownership. Keep each runtime's current model/artifact and disposal promise local. Add one deferred
  two-runtime test proving old forward → old delete → new load/forward.
- Inline `runsForSelection`, replace runtime `FEATURE_NAMES` with a direct union, and inline the
  small priority-fee/`block_interval_seconds` constants and one-use gas-utilization helper.
- Make repository-internal feature/target/mobile manifest aliases module-private; inline a one-use
  alias only when the containing interface stays clearer.
- Remove impossible chart-scale guards and unsupported same-engine block-watch replacement cleanup.
- Remove inference event-log choreography, duplicated history result reconstruction, impossible
  `selected_base_fee_per_gas=0` analytics fixtures, and other output-neutral app test ceremony
  already listed in this ledger.

### Non-goals

- No App transition controller, revision/lease/observer system, shared runtime/catalog,
  compatibility layer, visual redesign, style movement, component merger, memoization, or nested
  scrolling change.
- No accessibility semantics or tests. No app analytics mean rewrite.
- No removal of RPC/bigint, finite-feature, native tensor/output, artifact cache/disposal, race,
  retry, history/selection queue, stale-currentness, or rejection-safe continuation guards.

### Protected behavior and accepted change

- Layout, colors, spacing, copy, navigation, selection, analytics values, RPC behavior, and history
  remain unchanged.
- Rejection-safe serialization, copied native outputs, tensor validation, caching, final disposal,
  and per-engine ownership remain.

### Expected outcome

Chain replacement cannot overlap old native work with a new engine, and the App loses shallow
internal seams and duplicated test choreography without changing rendered or observable behavior.

### Checks

- Existing model, inference, engine lifecycle, history, analytics, and App race tests.
- New cross-runtime deferred lifecycle test.
- App unit suite, TypeScript check, Expo Doctor, and diff check.

### Dependencies and gates

- Runs after Slice 3 only to preserve one-writer sequencing; it is architecturally independent.
- No simulator visual gate is introduced because styles do not move. Native device/model execution
  is not claimed unless actually run.

## Explicitly rejected or deferred audit candidates

- No held-out, stage, or figure expected-roster checks. Fixed canonical experiment authors own
  those rosters; downstream code trusts their manifests.
- No second experiment-bundle collision check. The current early refusal plus atomic rename is
  adequate for a single-operator demo with minted experiment UUIDs.
- No generic figure CLI helper: it saves repeated entry-point lines by adding a shallow concept.
- No ordinary allocation chunks or `jobs.tsv` cell-label deletion. Balanced packing and direct
  failed-row identification protect the user's GPU-throughput and recovery priorities.
- No app analytics mean rewrite in the conditional mechanical sweep: floating-point order can
  change displayed values.
- No app style relocation: the current file already has coherent screen sections, while relocation
  adds files/namespaces and a visual verification gate for near-zero line reduction.
- No accessibility expansion for the no-user demo.
- No App transition controller, shared process-wide runtime/catalog, accessibility wrapper,
  network-picker variant abstraction, or speculative memoization.
- No optional validation flags, compatibility readers, legacy aliases, or old-path shims.
- No removal of `StrictFrozenRecord`, address helpers, observation reducers, execution interfaces,
  rolling reducers, artifact association, full-state resume, or atomic-publication guards.
- No removal of benchmark same-origin/coverage checks or the two-experiment artifact/evaluation
  join; those own the measured scientific quantity and raw operator pairing respectively.
- No removal of mobile-export roster, chain, horizon, shared-feature, native-output, delegation, or
  parity checks; `MOBILE.yaml` is raw operator input and export is a native boundary.
- No bypass of `BlockFrame.select_range()` or constructor validation through private constructors,
  flags, or `object.__new__`; that would add more machinery than it removes.
- No Apptainer definition edit without a separately authorized immutable remote build and test.
- No destructive cleanup of `tmp/`, canonical outputs, queued jobs, remote objects, or previous
  deployment images.

## Per-slice review protocol

For each approved slice, the orchestrator must:

1. record baseline SHA, exact `git status`, protected paths, checkout policy, implementer, reviewer,
   and allowed mutation scope in this ledger;
2. delegate implementation to a fresh agent using `implement`; the implementer runs focused checks,
   one proportional full suite, and commits exactly the slice;
3. inspect the commit and worktree before review;
4. delegate a pinned baseline-to-head review to a separate fresh agent using `code-review`, with
   this slice section as Spec and repository instructions/domain docs/ADRs as Standards;
5. return all actionable findings to the same implementer, then the same reviewer, until both axes
   report zero findings and `GREEN LIGHT`;
6. record implementation/correction SHAs, checks, findings, rejected candidates, and final green
   review in this ledger before starting the next slice.

No implementation and review work may overlap on the shared checkout. The root orchestrator does
not edit product code or review its own changes.

## Final completion gate

After every approved slice is green:

- run the full Python suite, app suite, TypeScript check, Expo Doctor, exporter suite, Ruff, format,
  Pyright, exact configured `uv run vulture` with manual classification, CLI help, lock checks, and
  diff check;
- run or explicitly gate any required simulator/device or remote image verification; do not claim
  unrun external checks;
- inspect the complete range from planning baseline to final head for accidental scientific,
  durable-schema, API, or protected-guard drift;
- confirm `tmp/` and all unrelated state are untouched;
- update the final slice/review record, then remove this temporary ledger in its own scoped commit;
- do not push or open a pull request without separate authorization.
