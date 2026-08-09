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

## Slice 1 — Trust canonical K-study authorship

Status: approved as output-neutral cleanup, not started

### Scope

- Keep held-out production code deriving horizons and the maximum horizon from the canonical
  K-study manifest.
- Add no exact-roster check or separately hard-coded `K=200` authority.
- Delete the test that blesses a 72-cell held-out experiment after removing `K=200`.

### Non-goals

- No production-code change.
- No chain, family, feature, context, horizon, selection, window, metric, reducer, plotting, or
  canonical address change.
- No alteration of completed canonical objects or live/queued experiment state.

### Protected behavior and accepted change

- HPO final selection still requires nine cells.
- K-study authoring still expands those cells through its fixed nine `_HORIZONS` values.
- K-study closure still verifies every authored artifact before publication.
- Strict manifest hydration remains.

### Expected outcome

Held-out trusts the canonical K-study publisher. The test suite stops manufacturing and supporting
an impossible partial canonical manifest.

### Checks

- Exact 81-cell authored roster and unchanged testing windows.
- Existing selection, reducer, and manifest round-trip tests.
- Focused experiment tests, full Python suite, Ruff, format, Pyright, required Vulture scan, and
  diff check.

### Dependencies and gates

- Depends only on generated-environment preflight.
- No remote campaign may be launched, altered, closed, or replaced.

## Slice 2 — Process-wide native model serialization

Status: approved, not started

### Scope

- Move the native-operation serial queue in `app/src/model.ts` from runtime-instance ownership to
  module ownership.
- Keep each runtime's current artifact/model and disposal promise local.
- Add one deferred two-runtime test proving old forward → old delete → new load/forward.

### Non-goals

- No App transition controller, revision system, lease, observer, or compatibility layer.
- No shared process-wide ModelRuntime or artifact catalog.
- No change to history, selection, RPC, feature, inference, or UI behavior.

### Protected behavior

- Rejection-safe queue continuation, copied native outputs, tensor validation, artifact caching,
  final disposal, and per-engine ownership remain.

### Expected outcome

Chain replacement cannot overlap old native work with the new engine. The production delta stays
near zero because only queue ownership moves.

### Checks

- Existing model/inference/engine lifecycle and App race tests.
- New two-runtime deferred lifecycle test.
- App unit suite, TypeScript check, Expo Doctor, and diff check.

### Dependencies and gates

- Independent of Slice 1, but runs second to keep one writer on `main`.
- Native device/model execution is not claimed unless actually run.

## Slice 3 — Trust scientific manifests and repair canonical prose

Status: proposed, awaiting approval

### Scope

- Add no expected-set checks to experiment stages or figures.
- Remove `c_study` expected-set and field-by-field family/context/source/Method revalidation after
  strict manifest and Study loading, including the second `C=25` assertion; retain the frozen
  context-selection rule.
- In all four figure scripts, remove curated cell-parse errors, one-trial rechecks, inferred
  completeness checks, and impossible empty/loop-result guards. Project canonical labels and
  rolling horizons directly. Keep every plotting calculation and valid-data branch.
- Direct-index canonical family/display/feature style tables instead of providing fallbacks for
  labels the fixed publishers cannot emit.
- In fresh tune-cell authoring, trust each fixed producer to emit unique new labels. Retain the
  intersection check when HPO `extend` appends to an existing active bundle.
- Delete mutation tests that exist only for those upstream-owned relationships.
- Update `docs/KAIROS.md` to `C=25`, 13 contexts, 117 cells, nine reused Studies, 108 new Studies,
  and the existing 5% chain-mean selection rule.

### Non-goals

- No generic cell-label framework or shared validator abstraction.
- No scientific roster, feature selection, context selection, HPO, window, reducer, figure style,
  or canonical object change.
- No weakening of strict manifest or Study hydration.
- Keep HPO `select()`'s exact final roster check because partial per-chain authoring through
  `prepare --chain` and `extend` is a supported normal workflow.

### Protected behavior and accepted change

- Complete canonical stage and figure outputs remain identical.
- Fixed upstream authors remain responsible for complete rosters.
- Typed manifests and Studies are trusted instead of rechecked against the same pipeline's request
  fields.
- Manually edited or partially manufactured canonical manifests may fail later with ordinary
  lookup/loader errors rather than tailored messages.

### Expected outcome

Internal scientific pipeline outputs stop being treated as hostile input. The canonical manual
matches the implemented context protocol.

### Checks

- Unchanged complete-roster manifests, selection, tables, and deterministic figures.
- Byte-compare deterministic vector PDFs from a small canonical fixture before and after.
- Focused experiment/figure tests, full Python suite, and static/dead-code checks.

### Dependencies and gates

- Runs after Slice 1 so held-out authority has its final shape.
- No experiment authoring, launch, closure, or canonical output mutation is authorized.

## Slice 4 — Durable publication and validation ownership

Status: proposed, awaiting approval

### Scope

- Remove `_validate_trial()` from `retain_result()`; keep publication-time validation.
- Reject a pre-existing canonical Evaluation before corpus/artifact loading or inference; retain the
  late pre-rename race guard.
- Delete repository-unused `reduce_artifact_validation()`, its API prose, and its dedicated test
  call. Inline the artifact-result loader if that deletion leaves it with one caller. Existing
  artifact loading and observation reduction remain authoritative.

### Non-goals

- No weaker raw/disk validation and no removal of existing early or late publication guards.
- Keep experiment bundle publication's current early collision refusal and atomic rename; add no
  second check for an implausible same-UUID concurrent publisher.
- No durable-object layout, request schema, metric, checkpoint, evidence, or scratch policy change.
- No external compatibility shim for the unused function.

### Protected behavior and accepted change

- Known Evaluation collisions fail before expensive work and create no scratch.
- Existing publication behavior remains unchanged.
- Complete successful outputs remain unchanged.

### Expected outcome

Each fact has one validation owner: publication validates retained trials, preflight rejects known
collisions, and canonical loaders/reducers replace an unused convenience seam.

### Checks

- Focused Study, artifact, and Evaluation tests.
- Early Evaluation collision does no inference or scratch work; its existing late guard still
  preserves scratch.
- Full Python suite and static/dead-code checks.

### Dependencies and gates

- Runs after Slice 3 so experiment boundary ownership is already fixed.
- Clean-break deletion assumes repository consumers define the supported surface.

## Slice 5 — Direct remote execution

Status: proposed, awaiting approval

### Scope

- Retain balanced `_allocation_sizes()`, ADR 0007's one-to-four-process allocation contract, and
  one GPU per exclusive step. Nine tasks at capacity four remain `3+3+3`; larger campaigns retain
  the fewest allocations without avoidable singleton tails.
- Replace count-bearing `gres` configuration plus `_scaled_gres()` with a count-free `gres_name`;
  render `:1` per step and `:<task_count>` per allocation.
- Flatten the behavior-free, one-owner `_Resources` record into `_Remote` and remove the matching
  `resources:` level from `REMOTE.yaml` and fixtures. Keep strict raw hydration and every resource
  value configurable.
- Retain `job_id`, `slot`, `row`, and the human-readable `cell` field in temporary `jobs.tsv`.
  Although `cells.tsv[row]` can derive the label, the direct field makes failed Slurm rows easier to
  identify and prune before resubmission.
- Quote the allocation-level Slurm output path and strengthen the existing fixture with a space.
- Remove redundant strict call flags whose owning Pydantic records already enforce strict parsing.
- Remove default workflow discriminator arguments and the lone direct CLI runner from typed test
  fixtures where shared helpers/defaults already own them.
- Update only the affected operator documentation and golden script.

### Non-goals

- No SSH, Slurm, job submission, queue, image reference, resource quantity, request payload, or
  scientific-execution change.
- No allocation-packing or job-recovery policy change.
- No generic scheduler abstraction.
- Do not alter `deploy/Apptainer.def` in this slice. The suggested `kairos --help` smoke is useful
  but does not materially simplify code and would require a separately authorized immutable remote
  image build/test gate.

### Protected behavior and accepted change

- Balanced packing and its focused matrix remain because sustained and tail GPU occupancy matter.
- Submission failure leaves the failed and later groups unrecorded, so rerunning submits them.
  After a submitted allocation fails remotely, the operator can remove its failed `jobs.tsv` rows
  and rerun; retained candidate scratch resumes and already-canonical candidate rows are skipped.
- Generated Bash remains the external protocol and keeps its focused golden test.
- Strict YAML/env/stdin/subprocess checks and positive job-ID parsing remain.

### Expected outcome

Remote submission keeps its occupancy-aware packing rule and gains one direct GPU resource name.
Scientific work inside each Slurm step is unchanged.

### Checks

- One-to-four balanced task allocations, spaced log path, GRES rendering, positive job IDs,
  journal recovery, aggregate process failure, and `bash -n`.
- Focused execution/launch tests, CLI help, full Python suite, and static/dead-code checks.

### Dependencies and gates

- No external scheduler or login-node access is required or authorized.
- Any future Apptainer definition edit is a separate slice requiring the documented `sbuild`
  immutable build and `apptainer test` procedure plus explicit remote authorization.

## Slice 6 — Honest inference-benchmark hot path

Status: measured-loop polling removal approved; remaining cleanup proposed, awaiting approval

### Scope

- Approved: remove `process.poll()`/liveness checks from each measured active-loop cascade; retain
  checks before and after each phase.
- Remove repeated `model.eval()` where the artifact loader already owns evaluation mode.
- Trust the canonical K-study and held-out publishers inside benchmark resolution: remove the
  reconstructed nine-group/36-label roster check and the redundant per-artifact horizon assertion.
  Retain the artifact/evaluation join because the operator supplies two independent experiment
  IDs.
- Load one benchmark Corpus per canonical architecture/chain group instead of supporting
  impossible mixed-Corpus horizons.
- Keep the powermetrics sample rate in one owner. Inline the one-call energy-settings builder, use
  one concrete internal dictionary type, and remove defensive copies.
- Trust atomic energy publication on resume instead of rescanning the three-file inventory. Keep
  settings equality because settings are raw operator input and are not in `protocol.json`.
- Remove the exporter Corpus-request cache; repeated small request reads are acceptable and produce
  the same bundle.
- Inline the exporter's one-call feature-contract copier without removing `_FeatureContract`, which
  still owns cross-horizon equality, example geometry, and manifest data.
- Remove only Pydantic call-site strict flags demonstrably duplicated by a
  `StrictFrozenRecord` configuration. Retain roster TypeAdapter strictness, Torch export strictness,
  and equal-length checks at external/native boundaries. Remove internal `zip(strict=True)` only
  where both sequences were constructed from the same local sequence.
- Replace derived first-horizon indexing with the existing horizon constant.
- Remove tests that require zero-copy storage identity or freeze transition-era protocol field
  order; retain values, shapes, chronology, protocol round-trip/mismatch, and resume behavior.
- Declare Pydantic directly in the mobile exporter because it imports it directly.

### Non-goals

- No timing statistic, energy equation, rolling policy, batch size, warmup, phase duration, output
  schema, artifact selection, or exporter validation change.
- No benchmark database, measurement abstraction, or compatibility layer.
- No change to existing benchmark output directories.

### Protected behavior and accepted change

- Removing poll overhead intentionally changes future measured latency/energy values by measuring
  the declared model-compute loop more faithfully. It does not rewrite thesis data.
- Powermetrics process health still fails the phase outside the measured inner loop.
- Same-origin and coverage checks remain because they define the measured rolling scientific
  quantity.
- Native exporter boundary validation and XNNPACK parity remain.

### Expected outcome

The active loop contains only view selection, four forwards/decodes, and minimal counting. Tests
assert observable data, not storage implementation.

### Checks

- Focused benchmark protocol, measurement, resume, reduction, and exporter tests.
- A small timing-boundary test proves liveness polling is outside the measured loop.
- Mismatched K-study/held-out IDs still fail; manually truncated canonical manifests no longer get
  a dedicated failure mode.
- Exporter test passes through its normal regenerated environment without a PATH workaround.
- Full Python suite and static/dead-code checks.

### Dependencies and gates

- No live powermetrics campaign, thesis result regeneration, model export, or device run is part of
  this slice.

## Slice 7 — Deep experiment tests

Status: proposed, awaiting approval

### Scope

- Add focused owner-level tests for `publish_bundle` and `close_bundle`; cover shared reporting once
  through one public stage command instead of a separate generic reporting matrix.
- Build minimal canonical upstream manifests/Studies directly in downstream stage tests.
- Retain one compact whole-pipeline smoke test.
- Delete repeated serialization dumps, publication choreography, and upstream pipeline replay.
- Use exclusive fixture creation directly; do not add old-fixture comparison machinery merely to
  diagnose an accidental identifier collision.
- Delete manual-corruption matrices for context Studies, partial closed feature/K-study manifests,
  benchmark horizon labels, and other states that fixed canonical publishers cannot emit.

### Non-goals

- No product behavior change.
- No deletion of scientific roster, selection, window, reducer, collision, resume, or deterministic
  figure assertions from their owning modules.
- No production extraction solely to shorten tests.

### Protected behavior

- Exact fixed rosters, scientific windows, atomic no-clobber publication, interruption/resume,
  canonical reductions, and one end-to-end path remain covered.

### Expected outcome

Downstream tests trust typed upstream boundaries. Generic bundle behavior is tested once at its
owner. The suite loses roughly 105–145 non-overlapping lines here, plus impossible-state tests
assigned to their product slices, and several repeated subprocess stages.

### Checks

- Run affected tests before and after and record test count, coverage ownership, and elapsed time.
- Full Python suite and static/dead-code checks.

### Dependencies and gates

- Runs after Slices 1, 3, 4, and 6 so tests target final owners once.

## Slice 8 — App shallow cleanup

Status: proposed, awaiting approval

### Scope

- Inline the one-line `runsForSelection` wrapper, replace the runtime-only feature-name roster with
  a direct type union, and inline the small feature-name constants and one-use gas-utilization
  helper.
- Make the repository-internal feature/target/mobile manifest aliases module-private; inline only a
  one-use alias if the containing interface stays clearer.
- Remove impossible chart-scale guards and unsupported same-engine block-watch replacement cleanup.
- Remove inference-test event-log choreography, duplicated result-field reconstruction in the
  history test, and analytics fixtures that inject impossible zero selected fees.

### Non-goals

- No style movement, visual redesign, wrapper layer, component merger, memoization, App lifecycle
  controller, or change to nested scrolling. `styles.ts` already groups shared, analytics, and
  inference declarations into coherent contiguous blocks; moving about 300 lines would add files
  or namespaces without behavioral leverage.
- No accessibility semantics or accessibility-specific tests. This is a no-user demo.
- Do not replace the online mean recurrence in this program. Ordinary summation can change the
  last floating-point bits of displayed analytics and therefore does not meet the output-neutral
  mechanical condition.
- No removal of race, retry, RPC, bigint, feature, native tensor, or queue guards.

### Protected behavior and accepted change

- Layout, colors, spacing, copy, navigation, selection, and analytics values stay unchanged.

### Expected outcome

Small internal seams and duplicated test structures disappear. The already-coherent presentation
layout stays untouched.

### Checks

- Existing focused behavior tests.
- App unit suite, TypeScript check, Expo Doctor, and diff check.

### Dependencies and gates

- Runs after Slice 2 to avoid revisiting the same app tests twice.
- No simulator/device visual gate is introduced because styles and rendered behavior do not move.

## Slice 9 — Output-neutral mechanical sweep and repository surface

Status: previously scoped mechanical items approved conditionally; second-audit additions below
remain proposed, awaiting approval

### Scope

- Remove redundant internal `np.int64` casts and `zip(strict=True)` where BlockFrame/Polars already
  own exact column type and equal length.
- Approved: compute the minimum-outcome matrix directly instead of chunking it through an arbitrary
  4,096-row policy. Preserve exact values and first-tie behavior. Accept about 341 MiB of temporary
  peak memory for the largest currently authored window; reject the implementation if proportional
  full-suite and representative-memory checks show unexpected material pressure.
- New proposal: inline the two owner-specific uniqueness checks and delete the shallow
  `_require_unique` helper.
- Remove redundant `strict=True` call flags where `StrictFrozenRecord` or
  `ExperimentManifest.model_config` already owns strict parsing.
- New proposal: remove duplicate action-logit finiteness checking from observation collection;
  `decode_action` remains its owner. Keep the independently required minimum-fee finiteness check.
- New proposal: remove dead `training_total_loss` logging and its choreography test. This metric is
  the epoch aggregation of the same classification-cross-entropy plus standardized-fee Smooth-L1
  loss already returned per batch for backpropagation. No logger, progress bar, callback,
  checkpoint, report, or durable output consumes the epoch copy. Validation loss, validation
  optimality gap, finite checks, early stopping, and selected-objective evidence remain.
- New proposal: derive one `TrainingDefinition` per artifact fit instead of rebuilding it through a
  one-call helper and both association/module paths. Preserve seeding before module construction.
- Remove the redundant Study zip strictness. Reuse the already-loaded first candidate rather than
  performing a uniform extra disk hydration.
- Remove inert checkpoint filename configuration, schema-irrelevant fixture rows, and assertions
  that pin Lightning choreography rather than outputs.
- New proposal: delete the exporter raw-byte XNNPACK substring assertion after the real
  program-delegation and host-execution gates.
- Apply the output-neutral app removals assigned to Slice 8 if that slice is not approved, without
  moving styles.
- Repair the stale research citation.
- New proposal: after Slice 3 moves every still-live protocol fact into canonical docs, delete the
  completed 369-line `docs/research/validation-evidence-implrevloop.md`. Git history remains the
  record of its implementation/review loop and superseded operational detail.
- Resolve the exporter direct dependency in Slice 6 or here, but only once.
- Remove the unsupported MIT metadata claim; add no license file.

### Explicit exclusions

- No arithmetic implementation change, including the app analytics mean.
- No schema, field order, dtype, serialized record, manifest, protocol, UUID, path, scientific
  roster, window, feature value, prediction, action, metric, checkpoint, plot, or report change.
- No removal of any protected guard.
- No figure CLI helper; four tiny entry points are clearer than another shared abstraction.
- No private-helper rename sweep; underscore-only churn does not simplify behavior.
- No uniform first-candidate reload; one extra strict disk hydration is less direct.
- No Apptainer smoke edit without its external build/test gate.
- No license file or ownership assertion without supervisor/KTO confirmation.

### Protected behavior

- For valid inputs, scientific and thesis-facing outputs remain identical.
- Raw malformed inputs continue to fail at the same owning boundary. Exact error wording need not
  be preserved unless it is an external CLI/API contract.

### Expected outcome

Repeated internal-trust ceremony and choreography-only tests disappear without changing any
scientific value or durable product.

### Checks

- Capture small deterministic pre-edit fixtures for temporal features, experiment manifests,
  observation reduction, Study selection, and model checkpoint naming; compare after the edit.
  Do not add permanent golden machinery solely for this sweep.
- Existing focused tests, full Python and app suites where touched, Ruff, format, Pyright, required
  Vulture scan with manual classification, Expo Doctor where touched, and diff check.
- Any output difference rejects the candidate cleanup; revert that individual item rather than
  adding compensation code.

### Dependencies and gates

- Runs last so mechanical edits do not create merge/review noise for semantic slices.
- MIT metadata removal is approved and recorded as correctness/completeness work.

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
