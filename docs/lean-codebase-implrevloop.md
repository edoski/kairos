# Lean codebase implementation-review ledger

Status: planning only; implementation paused pending approval of the proposed substantial slices

Authority: the codebase-wide audit pinned to
`6da8bf7e2ba1304f9ac009472c96965f89265838` and the user's 2026-08-09 annotations.
This ledger is the slice review Spec. `AGENTS.md`, `docs/CONTEXT.md`, ADR 0006, and ADR 0007 are
the Standards sources.

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
| Trust canonical experiment/figure manifests and remove internal Study relationship rechecks | Production/tests `-40..80` | Yes. Fixed upstream authors own the roster. | Recommend |
| Replace balanced allocation packing with ordinary chunks | Production/tests/docs `-35..70` | Yes. It removes an optimization policy and its matrix. | Recommend |
| Quote the Slurm allocation log path | Neutral | No material simplification; fixes one external-adapter defect. | Recommend as correctness work |
| Remove benchmark liveness polling from the measured hot loop | Production/tests `-5..15` | Yes. It makes the measured boundary direct. | Recommend |
| Move bundle mechanics to owner tests and shrink downstream pipeline monoliths | Tests `-140..200` net; estimates overlap | Yes. Tests stop replaying trusted upstream modules. | Recommend |
| Localize app styles | Roughly neutral; code moves | Yes. It shrinks a 109-key shallow global interface. | Recommend |
| Add local accessibility semantics and focused tests | Program delta `0` | No. This expands a no-user demo. | Rejected |
| Remove shallow app wrappers, type rosters, impossible chart guards, and choreography assertions | Production/tests `-15..35` | Yes. | Approved if output-neutral |
| Remove redundant strict flags, casts, `zip(strict=True)`, inert checkpoint options, and test ceremony | Production/tests `-35..70` | Yes. | Approved if output-neutral |
| Delete repository-unused `reduce_artifact_validation()` and its prose/test call | Production/docs/tests `-10..20` | Yes. Existing loaders/reducer own all behavior. | Recommend clean break |
| Add direct exporter dependency | Metadata `+1` | No. It fixes packaging ownership. | Recommend as completeness work |
| Remove the unsupported MIT metadata claim | Metadata `-1` | Yes, narrowly: the package stops claiming authority not established by a license file or ownership decision. | Approved |
| Repair the stale research citation and context-study prose | Neutral to small increase | No code simplification. It restores contract accuracy. | Recommend |

The only meaningful code addition is the native cross-runtime lifecycle test; production queue
ownership merely moves. Slurm quoting changes one expression, the sample-rate owner replaces a
duplicate literal, and the exporter dependency adds one metadata line. No new production
validation machinery remains in the plan.

### Estimated net program delta

This estimate excludes this temporary ledger and ignored/generated environment state. It counts
the overlapping 60–100-line bundle-test estimate only once inside the larger experiment-test
refactor.

- Production, configuration, and durable documentation: roughly 30–70 fewer lines.
- Tests: roughly 210–300 fewer lines. The main reduction is replacing downstream pipeline
  monoliths and tampering/choreography matrices with owner tests.
- Total: roughly **240–370 fewer tracked lines**, with a planning midpoint near **305 fewer lines**.

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
  strict manifest and Study loading; retain the frozen context-selection rule.
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

### Expected outcome

Internal scientific pipeline outputs stop being treated as hostile input. The canonical manual
matches the implemented context protocol.

### Checks

- Unchanged complete-roster manifests, selection, tables, and deterministic figures.
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
  call. Existing artifact loading and observation reduction remain authoritative.

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

- Replace balanced `_allocation_sizes()` with ordinary `tasks_per_job` chunks; nine tasks at four
  per job become `4+4+1`.
- Keep ADR 0007's one-to-four-process allocation contract and one GPU per exclusive step.
- Replace count-bearing `gres` configuration plus `_scaled_gres()` with a count-free `gres_name`;
  render `:1` per step and `:<task_count>` per allocation.
- Quote the allocation-level Slurm output path and strengthen the existing fixture with a space.
- Remove redundant strict call flags whose owning Pydantic records already enforce strict parsing.
- Update only the affected operator documentation and golden script.

### Non-goals

- No SSH, Slurm, job submission, queue, image reference, resource quantity, request payload, or
  scientific-execution change.
- No generic scheduler abstraction.
- Do not alter `deploy/Apptainer.def` in this slice. The suggested `kairos --help` smoke is useful
  but does not materially simplify code and would require a separately authorized immutable remote
  image build/test gate.

### Protected behavior and accepted change

- Packing efficiency may decrease; direct chunking is preferred.
- Generated Bash remains the external protocol and keeps its focused golden test.
- Strict YAML/env/stdin/subprocess checks and positive job-ID parsing remain.

### Expected outcome

Remote submission has one direct packing rule and one direct GPU resource name. Scientific work
inside each Slurm step is unchanged.

### Checks

- One-to-four task allocations, ordinary remainder chunk, spaced log path, GRES rendering, positive
  job IDs, aggregate process failure, and `bash -n`.
- Focused execution/launch tests, CLI help, full Python suite, and static/dead-code checks.

### Dependencies and gates

- No external scheduler or login-node access is required or authorized.
- Any future Apptainer definition edit is a separate slice requiring the documented `sbuild`
  immutable build and `apptainer test` procedure plus explicit remote authorization.

## Slice 6 — Honest inference-benchmark hot path

Status: proposed, awaiting approval

### Scope

- Remove `process.poll()`/liveness checks from each measured active-loop cascade; retain checks
  before and after each phase.
- Remove repeated `model.eval()` where the artifact loader already owns evaluation mode.
- Keep the powermetrics sample rate in one owner and remove the exporter corpus-request cache;
  repeated reads are acceptable and produce the same bundle.
- Remove only Pydantic call-site strict flags demonstrably duplicated by a
  `StrictFrozenRecord` configuration. Retain roster TypeAdapter strictness, Torch export strictness,
  and equal-length checks at external/native boundaries.
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
- Native exporter boundary validation and XNNPACK parity remain.

### Expected outcome

The active loop contains only view selection, four forwards/decodes, and minimal counting. Tests
assert observable data, not storage implementation.

### Checks

- Focused benchmark protocol, measurement, resume, reduction, and exporter tests.
- A small timing-boundary test proves liveness polling is outside the measured loop.
- Exporter test passes through its normal regenerated environment without a PATH workaround.
- Full Python suite and static/dead-code checks.

### Dependencies and gates

- No live powermetrics campaign, thesis result regeneration, model export, or device run is part of
  this slice.

## Slice 7 — Deep experiment tests

Status: proposed, awaiting approval

### Scope

- Add focused owner-level tests for `publish_bundle`, `close_bundle`, and shared reporting.
- Build minimal canonical upstream manifests/Studies directly in downstream stage tests.
- Retain one compact whole-pipeline smoke test.
- Delete repeated serialization dumps, publication choreography, and upstream pipeline replay.
- Make shared fixture creation fail on accidental identifier collisions instead of silently
  returning.

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
owner. The suite loses roughly 140–200 lines and several repeated subprocess stages.

### Checks

- Run affected tests before and after and record test count, coverage ownership, and elapsed time.
- Full Python suite and static/dead-code checks.

### Dependencies and gates

- Runs after Slices 1, 3, 4, and 6 so tests target final owners once.

## Slice 8 — App style locality and shallow cleanup

Status: proposed, awaiting approval

### Scope

- Move screen/component-specific styles beside their only consumers; retain `theme.ts` and only
  genuinely shared layout styles.
- Inline the one-line `runsForSelection` wrapper, replace the runtime-only feature-name roster with
  a direct type union, remove impossible chart-scale guards, and remove inference-test event-log
  choreography.

### Non-goals

- No visual redesign, wrapper layer, component merger, memoization, App lifecycle controller, or
  change to nested scrolling.
- No accessibility semantics or accessibility-specific tests. This is a no-user demo.
- Do not replace the online mean recurrence in this program. Ordinary summation can change the
  last floating-point bits of displayed analytics and therefore does not meet the output-neutral
  mechanical condition.
- No removal of race, retry, RPC, bigint, feature, native tensor, or queue guards.

### Protected behavior and accepted change

- Layout, colors, spacing, copy, navigation, selection, and analytics values stay unchanged.

### Expected outcome

Presentation details become local and the global style interface shrinks sharply.

### Checks

- Existing focused behavior tests.
- App unit suite, TypeScript check, Expo Doctor, and diff check.
- A simulator/device visual pass is required before this slice can be green because styles move.

### Dependencies and gates

- Runs after Slice 2 to avoid revisiting the same app tests twice.
- If no simulator/device is available, stop this slice at the external visual gate; do not claim
  green from static tests alone.

## Slice 9 — Output-neutral mechanical sweep and repository surface

Status: approved conditionally, not started

### Scope

- Remove redundant internal `np.int64` casts and `zip(strict=True)` where BlockFrame/Polars already
  own exact column type and equal length.
- Remove redundant `strict=True` call flags where `StrictFrozenRecord` or
  `ExperimentManifest.model_config` already owns strict parsing.
- Rename the ambiguous internal observation override and mark repository-private observation
  helpers private.
- Remove the redundant Study zip strictness and make candidate reload flow uniform.
- Remove inert checkpoint filename configuration, schema-irrelevant fixture rows, and assertions
  that pin Lightning choreography rather than outputs.
- Apply the output-neutral app removals assigned to Slice 8 if that slice is not approved, without
  moving styles.
- Repair the stale research citation.
- Resolve the exporter direct dependency in Slice 6 or here, but only once.
- Remove the unsupported MIT metadata claim; add no license file.

### Explicit exclusions

- No arithmetic implementation change, including the app analytics mean.
- No schema, field order, dtype, serialized record, manifest, protocol, UUID, path, scientific
  roster, window, feature value, prediction, action, metric, checkpoint, plot, or report change.
- No removal of any protected guard.
- No figure CLI helper; four tiny entry points are clearer than another shared abstraction.
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
- No app analytics mean rewrite in the conditional mechanical sweep: floating-point order can
  change displayed values.
- No accessibility expansion for the no-user demo.
- No App transition controller, shared process-wide runtime/catalog, accessibility wrapper,
  network-picker variant abstraction, or speculative memoization.
- No optional validation flags, compatibility readers, legacy aliases, or old-path shims.
- No removal of `StrictFrozenRecord`, address helpers, observation reducers, execution interfaces,
  rolling reducers, artifact association, full-state resume, or atomic-publication guards.
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
