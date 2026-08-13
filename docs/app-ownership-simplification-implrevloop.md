# App ownership simplification implementation-review ledger

Status: all four slices independently green; isolated final gates passed; final local `main`
integration authorized and ready

Authority: the current `app/` implementation at
`ff2a9e26ba67a7b4b58cc9e389a4eb4e81ff7b95`, the user's 2026-08-13 decisions in this
conversation, `AGENTS.md`, `docs/CONTEXT.md`, the accepted ADRs, and this ledger. This ledger is the
authoritative Spec for a future implementation-review run.

## Relationship to prior work

`docs/app-simplification-implrevloop.md` remains the immutable execution record for the completed
2026-08-09 simplification. Its retained Analytics, explicit outcome refresh, direct network and
horizon controls, local persistence, raw RPC guards, and native output guards remain useful
evidence.

This ledger cleanly supersedes that record's future authority over four implementation choices:

- selection application no longer shares the history FIFO;
- chain changes no longer replace a chain-bound inference engine;
- native operations no longer require a process-wide queue once one mounted inference runtime owns
  the model runtime;
- Analytics no longer owns a temporary local horizon while sharing the global chain.

The prior ledger's rejection of removing `attempt` is also superseded. The raw, scientific,
numeric, and native validations that decision protected remain required.

No accepted ADR fixes the app concurrency, selection, history, or presentation design. ADR 0006
governs canonical Study, artifact, evaluation, and mobile-export publication authority; ADR 0008
governs Servatus execution lifecycle; ADR 0009 governs Corpus authority. This app-only plan does not
conflict with them. ADR 0007 is superseded.

## Planning state

- Checkout: `/Users/edo/dev/python/kairos`
- Branch: `main`
- Immutable proposal-audit and ledger-planning baseline:
  `ff2a9e26ba67a7b4b58cc9e389a4eb4e81ff7b95`
- Baseline subject: `chore(deploy): select accepted CUDA image`
- Pre-ledger status: clean; local `main` matched local `origin/main`
- Pre-existing worktrees: one `main` worktree at `/Users/edo/dev/python/kairos`
- Pre-existing branches:
  - `main` at `ff2a9e26ba67a7b4b58cc9e389a4eb4e81ff7b95`
  - `codex/compact-cuda-execution` at
    `45f27ef9ce345c59e4c469522e2aa184f613a9e6`
  - `codex/compact-dataset-alignment` at
    `05ca43b1c51d2c68fd61065cf69b41e7548ca58a`
- Current run-owned write: this ledger only
- Run-owned branch: `codex/app-ownership-simplification`, created from
  `ff2a9e26ba67a7b4b58cc9e389a4eb4e81ff7b95`
- Run-owned worktree: `/Users/edo/dev/python/kairos-app-ownership-simplification`
- Proposed implementation branch: `codex/app-ownership-simplification`; name was free at planning
- Proposed implementation worktree: `/Users/edo/dev/python/kairos-app-ownership-simplification`;
  path was free at planning
- Planning/first-slice baseline commit:
  `5c2fec6d481b565597086c41718bbedc65d29880`
- Slice 1 product head: `fca527c699622a350d401e32bc162aa0cc77203d`
- Slice 1 green ledger head and Slice 2 baseline:
  `341cd651ae863674a3d05134f4ecb4ecb3e9c999`
- Slice 2 final product head: `259110f21f954d62d78a25fd9068866a2487dcf4`
- Slice 2 green ledger head and Slice 3 baseline:
  `b1d83a923ee644541fb3322c8960e3f1bd68f628`
- Slice 3 product head: `f881208fd6905f091fe1b5a906aeb3a5a8bddc17`
- Slice 3 green ledger head and Slice 4 baseline:
  `b2a16c042c4398af094468a3479eff0a8e2d1084`
- Slice 4 product head: `b86746c422431e71d5946282ae0bf1060d16c53c`
- Main checkout after isolation: clean at `ff2a9e26ba67a7b4b58cc9e389a4eb4e81ff7b95`
- Concurrent task `019fea73-abd5-7a51-9681-f0443f647884` was notified before implementation.
  It expects no `app/` product overlap, but may later change KAIROS execution code and shared docs.
  This run must not integrate into `main` until that task is fully complete and integrated; re-pin
  and reconcile against its final `main` before this run's final integration.
- Model assets: `app/assets/models/manifest.json` and the twelve `.pte` files remain absent
- Installed app dependencies at execution start: React 19.2.0, React Native 0.83.10, Expo 55.0.28,
  React Native ExecuTorch 0.9.2, and Viem 2.55.8
- Planning-baseline checks at the unchanged product head: 43/43 app tests, normal TypeScript,
  strict unused-local/parameter TypeScript, and Expo Doctor 19/19 passed

## Current authority

Authorized now:

- implement all four approved slices in order in the isolated run-owned worktree;
- dispatch one fresh implementer and one distinct reviewer per slice under the protocol below;
- create local commits and run the local checks required by this ledger;
- maintain and commit this ledger on the isolated branch.

Not authorized now:

- integration into or mutation of the `main` checkout before concurrent task
  `019fea73-abd5-7a51-9681-f0443f647884` is fully finished and integrated;
- push or pull request;
- external RPC, simulator, device, visual, exporter, generated-asset, remote, Slurm, image-build, or
  scientific-workload execution.

When implementation is explicitly authorized, use the proposed isolated branch and worktree unless
the user supplies a different checkout policy. Preserve all pre-existing branches, worktrees, and
unrelated changes. Keep the main checkout unchanged until every authorized slice is independently
green and final integration is authorized.

## Fixed product decisions

- Use a clean break. Delete superseded ownership, tests, and documentation directly. Add no legacy
  shim, compatibility prop, transitional alias, alternate runtime, fallback path, or architecture
  transition test.
- `app/` remains a small self-contained university demonstration. Prefer direct ownership and few
  concepts over product-scale state or lifecycle frameworks.
- Retain Inference, Analytics, both tabs, local durable run history, outcome refresh, run details,
  Summary, and all three graphs.
- Retain the three chains and four horizons. One global `{chain, horizon}` selection controls both
  screens.
- Selection changes apply immediately. AsyncStorage latency must not delay visible controls.
- A successfully completed run remains scientifically valid after later selection changes because
  it owns its chain, `K`, artifact, head, action, and target facts. Record it durably even when it no
  longer owns inference presentation.
- A successfully completed outcome refresh remains valid for its captured chain after later
  selection changes. Record its resolved outcomes; do not predicate durable work on visible
  selection.
- One monotonic inference generation guards presentation only. Every real selection transition,
  including `A -> B -> A`, invalidates the older result's loading, success, and error publication.
  Same-value taps do nothing.
- One mounted inference runtime owns one model catalog, one model runtime, and one session per
  chain. Chain changes do not create, dispose, or temporarily detach that runtime.
- The inference runtime lifecycle must survive React development setup-cleanup-setup correctly.
  Each effect setup receives a fresh live runtime and its cleanup disposes that same runtime. Do not
  retain one terminally disposed `useState(create...)` value through Strict Mode or Fast Refresh.
- Native load, forward, model replacement, and disposal remain serialized, but the queue belongs
  to the single model runtime rather than the JavaScript module process.
- Run history has one concrete app-specific owner. Its public operations express recording and
  pending-outcome resolution; a generic transaction callback remains internal.
- History load and every read-transform-save transaction share one rejection-safe FIFO. Save
  succeeds before React publication. A failed save changes neither the latest committed value nor
  visible runs.
- History writes require a successful initial load. A load failure must not let a later run replace
  existing storage with an empty in-memory value. No new retry UI is required; restart remains the
  recovery path.
- Run identity and `ran_at` remain minted when the completed result enters the durable history
  queue. Concurrent successful runs therefore appear in completion/record order. This simpler
  ordering is accepted.
- Pending outcomes remain retryable. Failed and future siblings remain unchanged; successful
  siblings commit in original order.
- Remove inference-layer phase wrapping. Preserve precise lower-owner errors, mapping Viem
  `BaseError` values to `shortMessage` once at presentation seams. Preserve normal `Error.message`,
  string rejections, and a compact unknown fallback. Add no app error hierarchy.
- Keep the explicit workflow message for run-history save failure. Persistence failure is different
  from inference or RPC failure.
- Keep raw RPC, feature, numeric, prediction, and native tensor validation. Only checks already
  guaranteed by the pinned typed decoder may be removed after exact source verification.
- A restrained Analytics split is included because the current 550-line screen has stable chart,
  run-detail, and orchestration regions. The split improves navigation and style ownership; it is
  not a chart framework or LOC-reduction target.
- Preserve `chartScale`, all three chart meanings, their data, dimensions, ticks, negative-value
  support, colors, legends, labels, order, empty states, and the single selected `(chain,K)` run
  collection.
- Preserve the incremental mean. Its numerical stability is more valuable than a negligible
  expression-size reduction.

## Target ownership

The intended end state is:

```text
App
  tab
  one immediate {chain, horizon}
  inference presentation state
  one inference generation

Inference runtime
  run(chain, K)
  currentHead(chain)
  resolveOutcome(chain, immediateBlock, selectedBlock)
  one model catalog
  one ModelRuntime with a local native FIFO
  one ChainSession per chain

Run history
  runs
  storageError
  record(result)
  resolvePending(chain, headBlock, resolver)
  private load/read-transform-save FIFO

RPC, features, model, analytics
  retain their existing conceptual seams and boundary validation
```

The names may change if the implementation finds a clearer collision-free term, but the ownership,
interfaces, and guarantees may not drift without updating this ledger and obtaining user agreement.

## Protected behavior

- One fresh exact closed-head context per Run.
- Conditional predecessor support for interval features.
- One aligned context-wide `eth_feeHistory(..., [50, 90])` call when the selected feature route
  requires priority fees.
- Exact fee-history origin, row count, tuple width, and nonnegative values.
- Positive block base fees and parent continuity across separately fetched RPC calls.
- Exact bigint arithmetic until the safe JSON/presentation conversion seam.
- Finite Float32 features and positive finite inverse-standardized predictions.
- Canonical first-maximum action tie behavior.
- Native output count, dtype, shape, storage length, finiteness, and copied values before module
  replacement or deletion.
- Model artifact caching and serialized replacement/disposal.
- Real unbounded `kairos.runs` persistence, stable run identity, save-before-publication, and
  rejection-safe queue progress.
- Manual-only **Refresh outcomes** initiation, one head read for eligibility, parallel exact outcome
  reads, future-run retention, and failed-sibling isolation.
- One selected `(chain,K)` collection feeding Summary, all graphs, run count/list, and details.
- Existing safe-area, page-title, direct network/horizon controls, result timeline, overlays, and
  bottom navigation behavior.

## Program non-goals

- No removal of Analytics, graphs, history, outcomes, tabs, local persistence, or run details.
- No server inference, download path, alternate native runtime, cache service, remote fallback, or
  synthetic/demo history.
- No polling, subscription, timer, focus effect, app-state observer, background task, retry loop,
  or automatic outcome refresh.
- No independent Analytics selection, second filter owner, kept-alive navigation state, or
  persisted selection.
- No cancellation framework, abort controller, engine lease, transition controller, observable,
  state manager, Redux, Zustand, React Navigation, or server-state library.
- No generic persistence repository, storage adapter interface, transaction framework, event bus,
  or public reference-identity update callback.
- No generic chart renderer, chart registry, modal framework, generic choice component, UI design
  system, or broad style-file fragmentation.
- No chart scale, arithmetic reducer, visible copy, or visual redesign.
- No broad validation deletion. Do not remove parent continuity, safe bigint, finite prediction,
  native output, copied-output, or schema/order checks.
- No edits to Python scientific, experiment, exporter, Servatus, Blockweaver, CUDA, deployment, or
  research-image code except a direct documentation reference proven necessary by the app change.
- No new package dependency.

## Proposal disposition

| Proposal | Decision |
| --- | --- |
| Remove selection from history queue | Accepted with the app-lifetime inference runtime |
| One app-lifetime inference owner | Accepted with restartable React effect ownership |
| One concrete persistent-history owner | Accepted; expose concrete operations only |
| Consistent selection semantics | Accepted as one global `{chain, horizon}` |
| Remove layered `attempt` | Accepted with compact Viem presentation mapping |
| Keep boundary validation | Accepted; only decoder-guaranteed type checks may leave |
| Restrained Analytics split | Accepted as the final, low-risk presentation slice |
| Optional `NetworkChoices.disabled` | Accepted |
| Narrow `Setup` props | Accepted |
| Remove unused TypeScript `baseUrl` | Accepted |
| Replace `WaitBucket.label` with numeric `wait` | Accepted |
| Replace incremental mean with `sum / length` | Rejected; retain stable arithmetic |
| Remove or redesign `chartScale` | Rejected without asset-enabled visual evidence |

## Slice 1 - One inference runtime and local native lifecycle

Status: independently green

### Execution record

- Immutable slice baseline: `5c2fec6d481b565597086c41718bbedc65d29880`
- Checkout: `/Users/edo/dev/python/kairos-app-ownership-simplification` on
  `codex/app-ownership-simplification`; clean at dispatch
- Allowed writer scope: inference/model/RPC ownership, the narrow App lifecycle wiring it exposes,
  focused tests, and directly affected current mobile documentation
- Implementer: `/root/slice1_implement`; read/used the `implement` skill
- Implementation head: `fca527c699622a350d401e32bc162aa0cc77203d`
- Reviewer: `/root/slice1_review`; distinct and read/used the `code-review` skill with separate
  `/root/slice1_review/standards_axis` and `/root/slice1_review/spec_axis` workers
- Fixed review range:
  `5c2fec6d481b565597086c41718bbedc65d29880...fca527c699622a350d401e32bc162aa0cc77203d`
- Review result: `GREEN LIGHT`; Standards 0 findings, Spec 0 findings
- Correction rounds: none
- Implementer checks: focused inference/model 17 passed; focused App/history 12 passed; full app
  suite 44 passed; normal and strict-unused TypeScript passed; Expo Doctor 19/19 passed;
  `git diff --check` and residue audit passed
- Orchestrator integration check: App/inference/model 26 passed; branch and main statuses clean;
  fixed commit list and changed-path scope verified. An initial Jest-only `--runInBand` flag was
  rejected by Vitest before test execution; the corrected Vitest command passed.
- Explicitly unrun: generated model assets, native simulator/device, real ExecuTorch, real RPC,
  exporter parity, and visual acceptance

### Scope

- Replace the chain-bound inference engine with one chain-parameterized inference runtime.
- Create the model catalog once, create exactly one model runtime, and create one immutable session
  per supported chain. Avoid a generic session cache or registry.
- Change Run, current-head, and outcome-resolution operations to accept the chain they execute.
- Remove chain-change engine creation, disposal, temporary detachment, and engine identity from
  `App`.
- Move the native serial queue inside the model runtime. It must cover load, forward, replacement,
  copied-output completion, and disposal for that runtime.
- Remove the cross-runtime serialization test. Retain or strengthen same-runtime concurrency,
  replacement, copied-output, and terminal-disposal coverage.
- Give React effect setup and cleanup explicit ownership of one fresh runtime instance. A
  development setup-cleanup-setup cycle must leave a live current instance rather than reusing a
  disposed one.
- Update `docs/KAIROS.md` to describe one mounted runtime and runtime-local native serialization.
  Do not rewrite the completed prior ledger.

### Non-goals

- No selection, durable-history, Analytics-filter, error-message, validation, or screen-file split
  in this slice except direct compile/test fallout.
- No native parallelism. Model work remains serial.
- No module singleton that survives an App lifecycle, global runtime registry, lazy chain-cache
  abstraction, runtime pool, model preloading, or multiple loaded model retention.
- No change to model selection, feature construction, prediction decoding, RPC acquisition, or
  outcome facts.

### Protected behavior and accepted tradeoffs

- One runtime reuses the currently loaded artifact and replaces it serially when `(chain,K)` selects
  another artifact.
- Separate RPC preparations may overlap; native model operations may not.
- Disposal remains terminal for one runtime instance and runs only for the instance owned by the
  corresponding effect setup.
- Selection changes no longer dispose native resources. Until Slice 2, current stale-publication
  behavior may remain as the temporary sequential-slice state; no compatibility path or test for
  that temporary state is required.

### Expected outcome

Changing network or horizon changes only the arguments to a stable inference owner. The app no
longer creates, invalidates, or disposes an engine during ordinary selection. Native safety lives
inside the one model runtime that requires it.

### Checks

- Focused inference tests for all three chain-parameterized operations and exact chain/session/model
  selection.
- Focused model tests for reuse, replacement, concurrent same-runtime calls, copied outputs,
  load failure cleanup, and terminal disposal.
- Focused App lifecycle test proving development setup-cleanup-setup leaves a usable runtime and
  cleanup disposes only its owned instance.
- Existing RPC and feature tests unchanged except interface fallout.
- Full `npm test` from `app/`.
- `npm run typecheck` and
  `npx tsc --noEmit --noUnusedLocals --noUnusedParameters` from `app/`.
- `npx expo-doctor` from `app/`.
- `git diff --check`, clean status, and residue audit for `ActiveEngine`, chain-dependent engine
  effects, module-global `serializeNativeOperation`, and cross-runtime serialization assertions.

### Dependencies and external gates

- First product slice.
- Requires an exact clean implementation baseline and isolated run-owned checkout.
- Generated model assets, native simulator/device execution, real RPC, and visual acceptance remain
  gated and unrun.

## Slice 2 - Immediate global selection and concrete run history

Status: independently green after one correction round

### Execution record

- Immutable slice baseline: `341cd651ae863674a3d05134f4ecb4ecb3e9c999`
- Checkout: `/Users/edo/dev/python/kairos-app-ownership-simplification` on
  `codex/app-ownership-simplification`; clean at dispatch
- Allowed writer scope: App selection/presentation orchestration, history ownership and storage,
  Analytics controlled selection, focused tests, and directly affected current mobile docs
- Implementer: `/root/slice2_implement`; fresh for this slice and read/used the `implement` skill
- Initial implementation head: `c0e48c868bddbc5de8fb04c5c37428b15fee0804`
- Reviewer: `/root/slice2_review`; distinct and read/used the `code-review` skill with separate
  `/root/slice2_review/standards_axis` and `/root/slice2_review/spec_axis` workers
- Initial fixed review range:
  `341cd651ae863674a3d05134f4ecb4ecb3e9c999...c0e48c868bddbc5de8fb04c5c37428b15fee0804`
- Initial review: Spec 0 findings; Standards one P3 Duplicated Code finding for two identical
  horizon-selection closures in `App.tsx`
- Correction round 1: the same implementer added one named `selectHorizon(Horizon)` owner in
  `259110f21f954d62d78a25fd9068866a2487dcf4`; only `app/App.tsx` changed
- Focused correction review range:
  `c0e48c868bddbc5de8fb04c5c37428b15fee0804...259110f21f954d62d78a25fd9068866a2487dcf4`
- Final review result: `GREEN LIGHT`; the same reviewer confirmed the finding closed and no new
  issue in the correction hunks
- Implementer checks: focused App/history 19 passed; full app suite 51 passed; normal and
  strict-unused TypeScript passed; Expo Doctor 19/19 passed; diff, scope, and residue audits passed
- Correction checks: focused App tests 11 passed; normal and strict-unused TypeScript and
  `git diff --check` passed
- Orchestrator integration check: App/history 19 passed; final diff check, commit list, branch
  status, and clean main status passed
- Explicitly unrun: generated model assets, native simulator/device, real ExecuTorch, real RPC,
  exporter parity, and visual acceptance

### Scope

- Replace `Selection.applied`/`Selection.intended` with one immediate selection state and one
  synchronously updated selection ref for rapid composed changes.
- Apply selection changes immediately, reset inference presentation, and increment one monotonic
  inference generation for every real transition.
- Capture selection and generation at Run start. Always record a successfully completed result.
  Publish loading, error, and success only while that generation remains current.
- Ensure `A -> B -> A` invalidates the original generation even though its final selection value
  equals the current value.
- Replace the incomplete history functions-plus-App-transaction split with one concrete app history
  owner exposing `runs`, `storageError`, `record(result)`, and
  `resolvePending(chain, headBlock, resolver)` or an equally narrow interface.
- Keep the generic reference-sensitive read-transform-save update private to history.
- Serialize initial load and every mutation. Block later writes after load failure. Save before
  publishing; retain the current committed value after failure; preserve queue progress.
- Make pending-outcome resolution return the original array when every element is unchanged.
- Capture the selected chain when Refresh outcomes begins. Read that chain's head once and finish
  valid resolution/persistence for that chain even if the visible selection later changes.
- Make Analytics controlled by the global `chain` and `horizon`. Remove `initialHorizon` and local
  `analyticsHorizon`.
- Rename visible history failure input from load-only semantics to storage semantics if the final
  owner reports load and save failures through one value.
- Update `docs/KAIROS.md` to describe immediate global selection, generation-scoped presentation,
  valid old-selection persistence, and the concrete history FIFO. Do not rewrite the completed
  prior ledger.

### Non-goals

- No public generic history `update` callback or persistence framework.
- No independent Analytics filter, selection persistence, run cancellation, abort signal, engine
  lease, or background refresh.
- No requirement to finish work across App/process termination. The guarantee covers selection and
  tab changes while the mounted App remains alive.
- No request-start history ordering or new history schema. Completion/record ordering remains.
- No chart, reducer, RPC validation, native validation, or broad screen split in this slice.

### Protected behavior and accepted tradeoffs

- Existing stored history always loads before a new mutation can replace it.
- Load failure prevents mutation for the mounted App lifetime and remains visible; restart is the
  accepted recovery path.
- Current-generation save failure presents the existing compact run-save failure. A stale
  generation does not replace inference presentation, but history retains a storage error.
- Two completed runs may commit in completion order. The native queue serializes model execution;
  their RPC preparation may overlap.
- Outcome refresh is chain-specific and horizon-independent. Horizon changes never cancel it.
- Failed and future outcome siblings remain persisted and retryable. No-op refresh does not write
  or publish a new array.

### Expected outcome

Controls respond immediately. Inference presentation always belongs to the latest selection/run,
while every completed valid run and outcome update reaches one durable history owner. `App` no
longer coordinates storage transactions, engine identity, or applied-versus-intended selection.

### Checks

- Selection updates immediately while an earlier history save remains pending.
- A completed old-selection result persists but never replaces current inference presentation.
- A newer run owns presentation while both successful runs persist in completion order.
- `A -> B -> A` invalidates the original result's presentation.
- An old-chain outcome refresh persists valid outcomes after chain or horizon changes.
- Analytics horizon changes propagate to Inference and survive tab remount because they are global.
- Initial load completes before an early run write; failed initial load blocks later writes.
- Failed save does not publish runs or replace the last committed history value.
- Concurrent history mutations are FIFO and the queue continues after rejection.
- Unchanged pending resolution returns the original array; eligible success, future retention, and
  failed-sibling retry behavior remain.
- Full `npm test`, typecheck, strict unused check, Expo Doctor, `git diff --check`, and clean status.
- Residue audit for `selectionState`, `applied`, `intended`, `enqueueOrderedUpdate` in `App`, engine
  identity/currentness predicates, `initialHorizon`, and `analyticsHorizon`.

### Dependencies and external gates

- Starts only after Slice 1 is committed and independently green.
- Generated model assets, native simulator/device execution, real RPC, and visual acceptance remain
  gated and unrun.

## Slice 3 - Direct errors and retained boundary validation

Status: independently green

### Execution record

- Immutable slice baseline: `b1d83a923ee644541fb3322c8960e3f1bd68f628`
- Checkout: `/Users/edo/dev/python/kairos-app-ownership-simplification` on
  `codex/app-ownership-simplification`; clean at dispatch
- Allowed writer scope: inference error propagation, shared presentation mapping, the one verified
  redundant RPC type check, focused tests, and directly affected current mobile docs
- Implementer: `/root/slice3_implement`; fresh for this slice and read/used the `implement` skill
- Implementation head: `f881208fd6905f091fe1b5a906aeb3a5a8bddc17`
- Reviewer: `/root/slice3_review`; distinct and read/used the `code-review` skill with separate
  `/root/slice3_review/standards_axis` and `/root/slice3_review/spec_axis` workers
- Fixed review range:
  `b1d83a923ee644541fb3322c8960e3f1bd68f628...f881208fd6905f091fe1b5a906aeb3a5a8bddc17`
- Review result: `GREEN LIGHT`; Standards 0 findings, Spec 0 findings
- Correction rounds: none
- Viem proof: pinned Viem 2.55.8 types return bigint fee-history quantities, and its formatter
  applies `BigInt` to every reward scalar. Only the post-decoder p50/p90 bigint checks were removed;
  tuple width and nonnegative checks remain.
- Protected-guard audit: fee-history origin/presence/rows/width/sign, positive base fees, parent
  continuity, finite Float32 features, positive finite predictions, safe bigint conversion, native
  tensor count/dtype/shape/storage/finiteness/copying, model serialization/lifecycle, and normalized
  native causes all remain reachable
- Implementer checks: focused errors/inference/RPC/model 33 passed; supporting
  App/history/features 22 passed; full app suite 58 passed; normal and strict-unused TypeScript
  passed; Expo Doctor 19/19 passed; diff, scope, status, and residue checks passed
- Orchestrator integration check: focused errors/inference/RPC/model 33 passed; final diff check,
  commit list, branch status, and clean main status passed
- Explicitly unrun: live transport failures, generated model assets, native simulator/device, real
  ExecuTorch, real RPC, exporter parity, and visual acceptance

### Scope

- Delete layered inference `attempt` wrapping and let precise RPC, feature, native, prediction, and
  safe-integer errors propagate from their owners.
- Add one compact presentation mapping used by both inference and outcome refresh. Map Viem
  `BaseError` to `shortMessage`, preserve normal `Error.message`, preserve string rejections, and
  use one compact fallback for other values.
- Retain the explicit run-history persistence failure message at the Run workflow seam.
- Remove only the `typeof p50/p90 === "bigint"` checks after re-verifying the pinned Viem decoder
  source and types. Retain reward tuple width and nonnegative-value validation.
- Replace tests of generic phase wrapper messages/causes with focused owner-error propagation and
  presentation-mapping tests.

### Non-goals

- No error class hierarchy, error code translation table, telemetry, logging framework, retry,
  backoff, transport-detail dialog, or phase wrapper under another name.
- No removal or weakening of raw RPC structure, exact alignment, parent continuity, safe integer,
  finite feature/prediction, native tensor, copied-output, or model lifecycle checks.
- No selection, history transaction, chart, arithmetic, or screen ownership change beyond compile
  fallout.

### Protected behavior and accepted tradeoffs

- Viem request metadata, body, documentation URL, and version do not fill the user dialog;
  `shortMessage` supplies compact transport text.
- KAIROS validation errors remain precise and visible beneath the existing Inference error title.
- ExecuTorch errors retain their normalized code/message/cause for debugging even though the UI
  displays only the compact message.
- Persistence remains a workflow failure and keeps its explicit user-facing wording.

### Expected outcome

Each owner reports the error it understands, and presentation performs one compact mapping. The
inference path has no repeated try/catch wrappers, while every meaningful external and scientific
guard remains intact.

### Checks

- Focused inference tests for direct RPC, feature, native, prediction-overflow, and safe-bigint
  errors.
- Focused presentation mapping tests for Viem `BaseError`, normal `Error`, string, and unknown
  values.
- Focused RPC tests retaining fee-history origin/shape/sign, positive fees, and parent continuity.
- Focused model tests retaining tensor count/type/shape/storage/finiteness and copied outputs.
- Full `npm test`, typecheck, strict unused check, Expo Doctor, `git diff --check`, and clean status.
- Residue audit for inference `attempt` and removed post-decoder bigint type ceremony.
- Manual source inspection that every protected guard named above remains reachable.

### Dependencies and external gates

- Starts only after Slice 2 is committed and independently green.
- No live transport failure, native runtime, simulator/device, or real RPC claim may be made from
  mocked tests.

## Slice 4 - Focused Analytics and presentation cleanup

Status: independently green

### Execution record

- Immutable slice baseline: `b2a16c042c4398af094468a3479eff0a8e2d1084`
- Checkout: `/Users/edo/dev/python/kairos-app-ownership-simplification` on
  `codex/app-ownership-simplification`; clean at dispatch
- Allowed writer scope: Analytics chart/run-detail extraction, styles owned by those extracted
  modules, the accepted small component/type/config cleanups, and focused tests
- Implementer: `/root/slice4_implement`; fresh for this slice and read/used the `implement` skill
- Implementation head: `b86746c422431e71d5946282ae0bf1060d16c53c`
- Reviewer: `/root/slice4_review`; distinct and read/used the `code-review` skill with separate
  `/root/slice4_review/standards_axis` and `/root/slice4_review/spec_axis` workers
- Fixed review range:
  `b2a16c042c4398af094468a3479eff0a8e2d1084...b86746c422431e71d5946282ae0bf1060d16c53c`
- Review result: `GREEN LIGHT`; Standards 0 findings, Spec 0 findings
- Correction rounds: none
- Implementer checks: focused Analytics 3 passed; full app suite 58 passed; normal and
  strict-unused TypeScript passed; Expo Doctor 19/19 passed; diff and residue checks passed
- Static audit: exactly three charts remain; all consume the same buckets and retain scale inputs,
  titles, labels, legends, order, dimensions, empty copy, and run-detail copy
- Orchestrator integration check: focused Analytics 3 passed; final diff check, commit list, branch
  status, and clean main status passed
- Explicitly unrun: generated model assets, native simulator/device, real ExecuTorch, real RPC,
  exporter parity, and visual acceptance

### Scope

- Extract the existing chart region into one focused Analytics charts module and Run details into
  one focused module. Keep screen orchestration in `AnalyticsScreen`.
- Give extracted modules narrow domain props. Do not expose chart-library configuration or generic
  modal contracts through their interfaces.
- Co-locate only styles exclusively owned by the extracted chart and Run-details modules. Leave
  shared and remaining screen styles in their current owner; do not fragment the full stylesheet.
- Make `NetworkChoices.disabled` optional with the same default behavior as `HorizonChoices` and
  remove the explicit false caller.
- Give `Setup` only its four used props through a direct local shape; remove the whole-screen prop
  spread.
- Remove unused `compilerOptions.baseUrl` from the app TypeScript configuration.
- Replace presentation-bearing `WaitBucket.label` with numeric `wait`; convert it to text at chart
  rendering.
- Delete only imports, styles, types, and tests made dead by this exact extraction and cleanup.

### Non-goals

- No chart library swap, scale rewrite, prop pruning, visual redesign, arithmetic reducer change,
  graph deletion, graph-to-table replacement, carousel, chart registry, or generic chart module.
- No generic modal, choice, style, form, navigation, or presentation framework.
- No broad relocation of all Analytics or Inference styles.
- No state, selection, inference, history, RPC, feature, model, or persistence behavior change.

### Protected behavior and accepted tradeoffs

- `chartScale`, `AXIS_PROPS`, nice-step behavior, fixed chart height, positive/negative sections,
  and the three chart meanings remain byte-for-byte or observably equivalent.
- All Summary values, graph data, labels, colors, legends, order, empty states, run count/list, and
  details remain unchanged.
- Extraction may increase file count and redistribute LOC. Better navigation and local style
  ownership are the intended benefit.

### Expected outcome

Analytics reads as a short screen orchestrator plus two cohesive private presentation modules.
Small component interfaces describe only what their callers use, while the rendered app remains
unchanged.

### Checks

- Existing Analytics reducer tests updated only for numeric `wait`.
- Focused component tests only where needed to protect narrow props and exact retained content; do
  not create a UI matrix or snapshot suite.
- Full `npm test`, typecheck, strict unused check, Expo Doctor, `git diff --check`, and clean status.
- Inspect that all three charts exist exactly once, consume the same `buckets`, and retain the
  current scale inputs and visible copy.
- Residue audit for `disabled={false}`, whole-screen `Setup` prop spread, TypeScript `baseUrl`, and
  `WaitBucket.label`.
- Native simulator/device and visual comparison remain deferred. Static tests do not prove pixel
  parity.

### Dependencies and external gates

- Starts only after Slice 3 is committed and independently green.
- No generated model asset is required for unit/type/static checks.
- Visual acceptance remains blocked by the missing final model bundle and supported custom native
  build.

## Per-slice implementation-review protocol

After explicit implementation authorization, the orchestrator must run each slice in order:

1. Recheck `main`, `origin/main`, worktrees, branches, status, planned-name collisions, installed
   dependency versions, and model-asset absence or presence.
2. Record the exact clean slice baseline SHA and checkout in this ledger.
3. Dispatch one fresh implementer. Require it to read and use the `implement` skill, read this
   ledger plus `AGENTS.md`, `docs/CONTEXT.md`, active ADRs, and affected current docs, remain inside
   slice scope, commit the product change, and report its final SHA and checks. It must not edit this
   ledger or review its own work.
4. Verify the actual branch, commit, clean status, commit list, and scoped baseline-to-head diff.
5. Dispatch a distinct fresh reviewer only after the implementation range is fixed. Require it to
   remain read-only, read and use `code-review`, review Standards and Spec as separate parallel
   axes, use this ledger as Spec, and return `GREEN LIGHT` only when both axes have zero actionable
   findings.
6. If rejected, record the head and exact findings. Send them to the same implementer for one
   focused correction commit and relevant checks. Send only the previous reviewed head to corrected
   head plus outstanding findings to the same reviewer. Repeat with those same workers until green
   or genuinely blocked.
7. After green, run only proportional orchestrator integration/status checks, update and commit this
   ledger if authorized, use the resulting head as the next slice baseline, then retire the slice
   workers before dispatching the next fresh pair.

Standards sources are `AGENTS.md`, `docs/CONTEXT.md`, accepted ADRs, affected current documentation,
and the `code-review` smell baseline. Spec authority is this ledger. The prior completed app ledger
is historical evidence, not the new Spec.

## Final integration gate

### Isolated-branch gate record

- Candidate head before this final ledger update:
  `3b0f89d6bd31653e1c312afd66b46833fa1b5c59`
- Full app suite: 58/58 passed
- Normal TypeScript and strict unused-local/parameter TypeScript: passed
- Expo Doctor: 19/19 passed
- `npm ci --ignore-scripts`: passed and changed neither `package.json` nor `package-lock.json`; npm
  reported the unchanged lock's 6 moderate and 14 high audit findings, and no audit-fix mutation was
  attempted
- `uv run vulture`: passed with no findings; its worktree-local `.venv` is ignored
- Full planning-baseline-to-candidate `git diff --check`: passed
- Changed-path audit: product changes are confined to `app/`; documentation changes are confined
  to current `docs/KAIROS.md` and this run ledger. No Python, scientific, experiment, exporter,
  Servatus, Blockweaver, CUDA, deployment, research-image, package, or lockfile changed.
- Deleted-concept residue audit: no `ActiveEngine`, module-global `serializeNativeOperation`,
  `selectionState`, `initialHorizon`, `analyticsHorizon`, inference `attempt`, `WaitBucket.label`,
  explicit `disabled={false}`, or TypeScript `baseUrl` remains
- Chart/static audit: exactly three `GiftedBarChart` render sites remain, all fed from the one
  selected collection through the same `buckets`; `chartScale`, `AXIS_PROPS`, incremental mean,
  visible chart and run-detail copy, and negative handling remain
- Current `docs/KAIROS.md` describes the final mounted runtime, immediate global selection,
  generation-scoped presentation, durable history owner, captured-chain refresh, and compact error
  mapping. The completed prior ledger remains unchanged.
- Implementation worktree and the main checkout are clean. `main` and `origin/main` remain at
  `ff2a9e26ba67a7b4b58cc9e389a4eb4e81ff7b95`.
- The original wait-for-concurrent-task integration order was respected through all implementation,
  review, and isolated final gates. The revised order below now supersedes that pending gate.
- Generated assets, Metro/custom native build, simulator/device, visual parity, real ExecuTorch,
  real public RPC, exported-model parity, and mobile performance remain explicitly unrun.

### Integration-order decision

- The user revisited the ordering before integration and proposed landing this completed app branch
  first.
- Concurrent task `019fea73-abd5-7a51-9681-f0443f647884` confirmed its active work remains isolated
  in Servatus, no KAIROS K1/K2 work or `main` mutation has started, and its later KAIROS work already
  requires re-pinning the then-current `main`.
- The only expected later overlap is documentation: `docs/CONTEXT.md`, `docs/KAIROS.md`, and
  possibly ADRs 0006 and 0008. This app branch changes only `docs/KAIROS.md` and this ledger under
  `docs/`; it changes no ADR or `docs/CONTEXT.md` file.
- Therefore local fast-forward integration of this independently green branch is authorized now and
  does not disturb the concurrent task. Push remains unauthorized.

After all four authorized slices are independently green:

- run `npm test` from `app/`;
- run `npm run typecheck` and
  `npx tsc --noEmit --noUnusedLocals --noUnusedParameters` from `app/`;
- run `npx expo-doctor` from `app/`;
- verify the lock with `npm ci --ignore-scripts` in the isolated implementation checkout and confirm
  it changes neither `package.json` nor `package-lock.json`;
- run `uv run vulture` from the repository root, manually classify every finding, and delete
  nothing based only on the tool report;
- run `git diff --check`, status, changed-path, commit-range, and residue audits;
- inspect the full planning-baseline-to-head diff for accidental Python, scientific, experiment,
  exporter, CUDA, deployment, RPC, native, chart, history-schema, or documentation drift;
- confirm current `docs/KAIROS.md` describes the final runtime, selection, history, refresh, and
  error behavior while the completed prior ledger remains an unchanged historical record;
- confirm all three charts and their one selected `(chain,K)` collection remain;
- record every slice baseline/final SHA, implementer, reviewer, correction round, check, explicit
  unrun gate, and final checkout state in this ledger;
- fast-forward `main` only if integration is authorized and the fixed implementation range is
  green;
- remove only run-owned branches and worktrees after their commits are safely integrated;
- verify the final branch/worktree shape matches the planning state except for explicitly
  authorized branch changes.

## Deferred acceptance gates

The repository lacks the final `MOBILE.yaml`, manifest, and twelve `.pte` assets. Therefore this
program must not claim:

- successful Metro bundle or custom native build;
- simulator/device startup;
- visual or pixel parity;
- real ExecuTorch model load/forward/disposal;
- real public-RPC behavior;
- exported-model semantic parity;
- iOS/Android memory, latency, or energy behavior.

Those claims remain owned by the existing asset-dependent mobile acceptance plan. No push, pull
request, external RPC, simulator/device, exporter, remote, Slurm, image, or scientific workload is
authorized merely by executing this ledger.

## Completion condition

The run is complete only when every authorized, unblocked slice has an independently fixed
zero-finding Standards and Spec review, all final local gates pass, current documentation matches
the final code, integration status is recorded, and run-owned isolation is removed after safe
integration. Partial completion must be reported plainly.

Keep this ledger unless the user explicitly requests cleanup after completion. If cleanup is
requested, delete it only after all gates are green and propagate that deletion to every in-scope
branch before reporting completion.
