# App simplification implementation-review ledger

Status: both authorized slices independently green; final integration passed, local integration and
cleanup in progress

Authority: the current `app/` implementation at
`5a1245908eb0e3150051155394db9dce2215d6be`, the user's 2026-08-09 decisions in this
conversation, `AGENTS.md`, `docs/CONTEXT.md`, and accepted ADRs 0006 and 0007. This ledger is the
future implementation Spec.

## Pre-run state

- Checkout: `/Users/edo/dev/python/kairos`
- Branch: `main`
- Immutable planning baseline: `5a1245908eb0e3150051155394db9dce2215d6be`
- Status: clean; `main` matched the local `origin/main` ref before the planning commit
- Worktrees: one pre-existing `main` worktree at `/Users/edo/dev/python/kairos`
- Pre-existing branches: `main` and `codex/compact-cuda-execution`
- Run-owned branch: `codex/app-simplification`
- Run-owned worktree: `/Users/edo/dev/python/kairos-app-simplification`
- Planning commit on `main`: `afda6171084b26a5b391ec292f2347d9e66abcdb`
- Implementation checkout policy: use the safest repository-native isolation, a run-owned
  `codex/app-simplification` branch at `/Users/edo/dev/python/kairos-app-simplification`; keep the
  pre-existing `main` checkout and branches intact until final fast-forward integration
- Authorized: both ledger slices, local app/docs edits, focused and full local checks, worker
  dispatch, local commits, isolated branch/worktree creation, final fast-forward integration into
  `main`, and removal of run-owned isolation after every gate is green
- Not authorized: pushes, pull requests, external RPC calls, simulator/device runs, generated model
  assets, exporter runs, remote work, Slurm work, or image builds

## User decisions already fixed

- `app/` is a small self-contained university demonstration with no real users, other developers,
  compatibility obligation, or speculative maintenance needs. Clean, lean, elegant, direct code
  takes priority over product machinery.
- Analytics remains a first-class view backed by real locally persisted runs and resolved outcomes.
  Do not replace it with synthetic/demo data or session-only fixtures.
- Retain all three current graphs: Recommended wait distribution, Savings by wait, and Base fee by
  wait. Preserve their selected `(chain,K)` collection, values, labels, colors, legends, pending
  behavior, empty states, summary cards, run count/list, and run details.
- Chart deletion and graph-to-table replacement are rejected. Simplify chart-adjacent code only
  when the result is materially clearer and does not create a generic chart configuration layer,
  move logic across more files, or change rendered meaning.
- Replace continuous block watching and automatic outcome work with one explicit Analytics
  **Refresh outcomes** action if the final implementation is simpler both conceptually and in
  code. No timer, subscription, poll loop, background task, retry loop, or refresh abstraction may
  replace the current watcher.
- Persisted history, retryable pending outcomes, exact selected-chain resolution, and the ordered
  history/selection publication seam remain. Manual refresh changes when work starts, not the
  durability or outcome facts.
- Four discrete horizons do not justify a native slider. Visible `K=2`, `K=3`, `K=4`, and `K=5`
  choices are the preferred simpler control.
- Delete the global visual KAIROS header. The Inference and Analytics page titles already identify
  the active view; retain the top device safe-area inset without keeping an empty branding bar.
- Extract the existing Inference network cards into one shared `NetworkChoices` component and use
  that exact presentation as the first section below the page title in both views. Add no visual
  variants or second screen-local renderer.
- Use a clean break. Delete superseded watcher, slider, status, styles, tests, dependencies, and
  documentation directly; add no compatibility props, aliases, transition paths, or regression
  tests for removed architecture.

## Design rule

Remove optional product choreography before abstracting it. Keep direct modules at real seams:
raw RPC, scientific feature construction, native ExecuTorch execution, local durable history, and
React publication ordering. One adapter does not justify a new interface. A changed visual control
must be simpler in both interface and implementation, not merely moved into another file.

## Protected behavior

- Exact chain and horizon domains and one applied selection shared by inference and Analytics.
- The top device safe-area inset, readable status-bar treatment, both page titles, and the bottom
  navigation safe area after deletion of the visual header.
- One fresh exact context per Run, conditional predecessor support, fee-history `[50,90]` origin,
  row-count and tuple validation, parent continuity, positive base fees, exact bigint arithmetic,
  finite Float32 features, and safe bigint conversion.
- Distinct inference error boundaries for chain reads, feature construction, native inference, and
  run persistence.
- Native tensor count, dtype, shape, storage length, finiteness, copied outputs, artifact caching,
  process-wide native-operation serialization, replacement, and disposal.
- Real `kairos.runs` persistence, stable run order and identity, pending-outcome retry, sibling
  outcome isolation, save-before-publication, storage failure behavior, and one selected
  `(chain,K)` collection feeding Summary, all graphs, run count/list, and details.
- `Selection.applied`, latest `Selection.intended`, engine identity, stale-result rejection, and the
  rejection-safe ordered update queue while history persistence and selection can overlap.
- Existing graph calculations and presentation. A chart cleanup that changes floating-point
  reduction order, scale, number of sections, missing-bucket treatment, copy, or visible result is
  rejected.

## Audit conclusion

The scientific, RPC, native, persistence, and chart modules are not the current simplification
target. Their complexity corresponds to real boundaries or retained Analytics behavior. The two
worthwhile clean breaks are:

1. replace continuous chain watching with explicit outcome refresh, delete the live-status feature
   cluster, and delete the now-unnecessary global header; and
2. replace indirect network/horizon controls with shared visible fixed choices while leaving the
   graphs intact.

No independent chart-refactor slice is planned. `ChartCard`, `AXIS_PROPS`, `niceStep`,
`chartScale`, and the three semantic chart functions already concentrate shared behavior without a
speculative configuration framework.

## Slice 1 — Explicit outcome refresh and native lifecycle deletion

Status: complete; independent `GREEN LIGHT`

### Execution record

- Immutable slice product baseline: `afda6171084b26a5b391ec292f2347d9e66abcdb`
- Checkout: clean `codex/app-simplification` at
  `/Users/edo/dev/python/kairos-app-simplification`
- Allowed writer scope: Slice 1 app code, focused tests, README, and `docs/KAIROS.md`; the
  implementer must not edit this ledger
- Assigned implementer: `/root/slice1_implementer`
- Reserved independent reviewer: `/root/slice1_reviewer`
- External gates: no real RPC, simulator/device, generated asset, exporter, remote, Slurm, image,
  push, or pull-request work
- Pre-dispatch branch head: `53b198aaecb09140cf987962ed1b47e941ddc21c`
- Implementation commit: `fe5c64cf8bb4313bc6a7eea463d1a759296d5270`
  (`refactor(app): replace block watcher with manual refresh`)
- Implementer verification: focused tests 28/28; full app tests 43/43; typecheck and strict unused
  checks passed; Expo Doctor 19/19; clean npm lock check, diff check, Vulture, and scoped residue
  audit passed; worktree clean
- Review range: `53b198aaecb09140cf987962ed1b47e941ddc21c...fe5c64cf8bb4313bc6a7eea463d1a759296d5270`
- Review result: `/root/slice1_reviewer` returned Standards `GREEN LIGHT` with zero findings and
  Spec `GREEN LIGHT` with zero findings; checkout remained clean
- Correction rounds: none
- Orchestrator integration check: clean branch at the implementation commit and app typecheck passed
- Unrun as gated: real RPC, simulator/device/visual acceptance, generated assets/exporter, remote,
  Slurm/image work, push, and pull request

### Scope

- Add one **Refresh outcomes** action to Analytics. The screen owns only its button loading/error
  presentation and calls one `onRefresh(): Promise<void>` prop.
- On refresh, capture the current applied chain and engine, read the current head block once, then
  use the existing ordered `commitRuns` path to resolve eligible pending runs for that chain.
- Preserve `resolvePendingRuns`' current head eligibility check, parallel sibling resolution,
  per-run failure isolation, original ordering, and object identity for unchanged runs. Persist and
  publish only when at least one run changes.
- Replace the subscription-shaped RPC interface with one direct current-head read. Remove
  `ChainSession.watchBlocks`, stored `unwatch`, and session disposal when it becomes behavior-free.
- Replace `InferenceEngine.watchBlocks` with the narrow current-head operation required by manual
  refresh. Keep safe bigint conversion at the inference seam.
- Remove `ChainSnapshot`, `RpcStatus`, `rpcStatus`, `snapshot`, automatic block callbacks,
  `resolveOutcomes`, continuous status updates, and fire-and-forget polling error handling.
- Remove the Inference screen's Live conditions section and delete the complete visual KAIROS
  header, including `AppHeader`, its status dot, navy header bar, and one-use module. Fold top
  safe-area handling into the root app container and keep the status bar readable against the page
  background. Retain the Inference and Analytics page titles; add no replacement header.
- Keep model runtime disposal on engine replacement/unmount. Delete only session/watch lifecycle
  that becomes empty.
- Update README and `docs/KAIROS.md` mobile wording from block watching/automatic resolution to
  explicit user refresh. State that pending outcomes remain retryable and persisted.
- Delete only tests and styles that assert the removed watcher/status/live-snapshot feature. Add
  one focused App-level refresh test through the Analytics prop and retain focused history/RPC
  outcome tests at their owning seams.

### Non-goals

- No removal or weakening of Analytics, graphs, history persistence, run details, outcome fields,
  selected-chain filtering, the ordered update queue, applied/intended selection, or stale-result
  checks.
- No refresh interval, timer, subscription, focus effect, app-state observer, retry, backoff,
  caching, background fetch, notification, or generic refresh controller.
- No attempt to resolve future target blocks. One current-head read remains the eligibility
  authority.
- No model reload, inference rerun, context fetch, fee-history fetch, or snapshot/base-fee display
  during Refresh outcomes.
- No swallowing of durable save failures. The Analytics refresh control must finish and present a
  compact failure state if the ordered refresh operation rejects.
- No chart, reducer, inference-result, native-model, feature, or visual-selection redesign.

### Protected behavior and accepted tradeoffs

- A pending run changes only after the operator presses Refresh outcomes and its target block is at
  or below the freshly read selected-chain head.
- Failed or not-yet-eligible outcomes remain pending and retryable on the next press; one failed run
  does not block a successful sibling.
- The app no longer advertises continuous RPC health or live block/base-fee conditions. This is an
  accepted feature deletion for a no-user demonstration.
- The app no longer shows a global KAIROS branding bar. The active page title supplies the useful
  identity, while the top device inset remains protected.
- Analytics may be stale until Refresh outcomes is pressed. Explicit user control is preferred to
  invisible background activity.

### Expected outcome

The app performs no network work merely because it is open. A Run reads the chain to make one
recommendation; Refresh outcomes reads the current head and updates eligible stored outcomes. The
continuous watcher, status, snapshot, unwatch, and visual app-header concepts no longer exist.

### Checks

- Focused history tests: eligible resolution, future pending retention, failed sibling retention,
  stable order, and unchanged object identity.
- Focused RPC/inference tests: one current-head read, safe integer conversion, exact outcome block
  reads, and model-only disposal.
- Focused App tests: refresh uses the applied chain/engine, saves before publishing, no-op refresh
  does not save, stale engine does not publish, and save rejection reaches the control.
- Existing Analytics reducer/chart tests unchanged except import fallout.
- `npm test`, `npm run typecheck`, strict unused-local/parameter TypeScript check,
  `npx expo-doctor`, lockfile check, `git diff --check`, and scoped residue searches for
  `watchBlocks`, `RpcStatus`, `ChainSnapshot`, `snapshot`, `AppHeader`, `headerSafeArea`, and removed
  status/live/header styles.
- Native simulator/device and real RPC checks remain unrun. The final asset-dependent activation
  gate owns those claims.

### Dependencies and external gates

- First implementation slice in the authorized isolated run.
- No generated model asset is required for unit/type checks.
- Native visual acceptance remains deferred until the final twelve assets and supported custom
  development build exist.

## Slice 2 — Direct fixed selection controls around retained graphs

Status: complete; independent `GREEN LIGHT`

### Execution record

- Immutable slice product baseline: `fe5c64cf8bb4313bc6a7eea463d1a759296d5270`
- Checkout: clean `codex/app-simplification` at
  `/Users/edo/dev/python/kairos-app-simplification`
- Allowed writer scope: Slice 2 app controls, focused tests, package dependency/lock cleanup, and
  directly exposed dead styles/imports; the implementer must not edit this ledger
- Assigned implementer: `/root/slice2_implementer`
- Reserved independent reviewer: `/root/slice2_reviewer`
- External gates: no real RPC, simulator/device, generated asset, exporter, remote, Slurm, image,
  push, or pull-request work
- Pre-dispatch branch head: `cbc4baeb49aad106611df524378a8497740248ab`
- Implementation commit: `30e51539c823d44f890fdb58a5e6c4e709ed51d9`
  (`refactor(app): simplify selection controls`)
- Implementer verification: full app tests 43/43; typecheck and strict unused checks passed; Expo
  Doctor 19/19; clean npm lock check, diff check, Vulture, control/dependency residue audit, shared
  component count, and three-chart/single-`buckets` audit passed; worktree clean
- Review range: `cbc4baeb49aad106611df524378a8497740248ab...30e51539c823d44f890fdb58a5e6c4e709ed51d9`
- Review result: `/root/slice2_reviewer` returned Standards `GREEN LIGHT` with zero findings and
  Spec `GREEN LIGHT` with zero findings; checkout remained clean
- Correction rounds: none
- Unrun as gated: real RPC, simulator/device/visual acceptance, generated assets/exporter, remote,
  Slurm/image work, push, and pull request

### Scope

- Replace `HorizonSlider` in Inference and Analytics with one small shared `HorizonChoices` module
  used identically by both callers. It renders the four visible values from canonical `HORIZONS`
  and accepts only selected value, change callback, and optional disabled state.
- Remove the Inference prediction-space/slider card. Keep the selected `K` label and use the four
  direct choices as the complete horizon interaction.
- Delete `HorizonSlider`, `@react-native-community/slider`, its lock entries, and slider/prediction
  styles after caller and dependency verification.
- Extract Inference's existing `NetworkChoices` cards into one small shared component. It accepts
  only the selected chain, change callback, and disabled state, and owns the current card, icon,
  checkmark, and label presentation without variants.
- Render that same `NetworkChoices` component inside an identical **Network** section immediately
  below the page title in Inference and Analytics. In Analytics it precedes load errors, Summary,
  horizon choices, and graphs; Inference retains its current top-of-page placement.
- Replace Analytics' title-and-network-badge row with its plain page title followed by the shared
  Network section. Rename inference-only network-card styles to shared names if necessary rather
  than retaining caller-specific styling.
- Remove `networkPickerOpen`, the Analytics `NetworkPicker` module, close choreography, chevron,
  and now-unused modal/network-sheet styles.
- Preserve all graph components and their placement below the selected horizon. Remove only dead
  imports/styles exposed by the control cleanup.
- Keep Run details and the error dialog on the existing `Overlay`; two distinct callers justify the
  shared modal implementation after network-picker deletion.

### Non-goals

- No graph deletion, graph-to-table replacement, carousel, graph picker, chart library swap,
  custom chart renderer, chart configuration registry, or chart file split.
- No Analytics calculation, run filtering, summary, count, order, copy, legend, scale, or empty
  state change.
- No generic `Choice<T>`, network-control variant prop, duplicate screen-local network renderer,
  form framework, navigation library, state manager, memoization, broad style relocation, or
  accessibility expansion.
- No change to global chain selection semantics: changing the Analytics chain still changes the
  applied app chain and engine.
- No removal of the inference result timeline. It explains the selected action after a Run; only
  the setup-time prediction-space decoration is removed.

### Protected behavior and accepted tradeoffs

- All three chains and four horizons remain visible and selectable. Disabled inference controls
  stay disabled while inference is loading.
- Both screens show the exact same Network section immediately after their title. Analytics does
  not retain a badge, modal, or alternate compact presentation.
- The Analytics horizon remains a local graph filter initialized from the applied inference
  horizon. The chain remains global.
- The screen becomes less decorative. Direct comprehension and fewer UI concepts take priority
  over the slider and modal interaction.
- Charts may move vertically because controls shrink, but their own dimensions, values, labels,
  colors, ordering, and content remain unchanged.

### Expected outcome

Each page begins with its title and the same directly pressable Network choices. Every finite
selection is visible; the app has no native slider or network-picker state, while Analytics retains
its complete summary, three graphs, run list, and details.

### Checks

- Focused component checks only if they assert selection values/callbacks rather than React Native
  internals. Do not add a UI matrix or transition test suite.
- Existing App, Analytics, inference, history, RPC, feature, and model tests.
- `npm test`, `npm run typecheck`, strict unused-local/parameter TypeScript check,
  `npx expo-doctor`, lockfile check, `git diff --check`, and residue searches for the removed slider
  package/component and network-picker state/styles. Confirm `NetworkChoices` has one definition,
  two callers, and no presentation variants.
- Inspect the final source to confirm every current graph remains present exactly once and consumes
  the same `buckets` collection.
- Native simulator/device visual acceptance remains deferred to the final asset-dependent gate;
  do not claim it from type checks or unit tests.

### Dependencies and external gates

- Runs only after Slice 1 is committed and independently green.
- The less-decorative shared controls were explicitly authorized on 2026-08-09.
- No real RPC, model asset, simulator, device, exporter, or remote work is authorized by this
  ledger.

## Final integration record

- Final product head: `30e51539c823d44f890fdb58a5e6c4e709ed51d9`
- Full app tests: 43/43 across seven files
- TypeScript: normal typecheck and strict unused-local/parameter check passed
- Expo Doctor: 19/19 checks passed
- Dependency lock: `npm ci --ignore-scripts` passed and left `package.json`/lockfile unchanged; npm
  reported 20 transitive audit advisories (6 moderate, 14 high), with no dependency added by this
  run
- Static/status checks: Vulture returned no findings; full-range diff check and worktree status
  passed
- Residue: no watcher/status/snapshot/header/live-condition, slider, slider-package,
  network-picker, or removed-style terms remain in scoped app code, tests, and mobile docs
- Retained UI: one `NetworkChoices` definition with two callers, one `HorizonChoices` definition
  with two callers, and all three chart definitions/renders remain exactly once on the same
  `buckets` collection
- Full planning-baseline audit: every changed path is confined to `app/`, `README.md`,
  `docs/KAIROS.md`, and this ledger; no Python core, experiment, deployment, scientific, artifact,
  or remote path changed
- Deferred gates: real RPC, simulator/device/visual acceptance, generated model assets/exporter,
  remote, Slurm/image work, push, and pull request remain unrun

## Explicitly rejected or superseded candidates

- Delete Analytics, charts, history, outcomes, tabs, or local persistence: superseded by the user's
  decision to retain Analytics as a real view.
- Replace graphs with one table or keep only one graph: rejected. All three current graphs remain.
- Remove the ordered update queue while persistence, outcome refresh, inference save, and global
  selection share publication: rejected. Manual initiation removes background work, not the
  durable ordering seam.
- Replace one watcher with another polling/focus/app-state/background mechanism: rejected.
- Preserve live conditions through a second explicit snapshot feature: rejected for this lean plan.
  Refresh outcomes reads only the head fact required for eligibility.
- Make Analytics chain selection local to the view: rejected. One applied chain remains easier to
  explain than independent inference and Analytics chain state.
- Duplicate the Inference network cards inside Analytics or keep an Analytics-specific compact
  variant: superseded by the decision to use one exact shared control in the same page position.
- Merge the three semantic chart functions into one configuration-driven renderer: rejected as
  speculative generality.
- Move chart or screen styles into more files, merge all UI into `App.tsx`, create a transition
  controller, share a process-wide runtime/catalog, add observers, or add memoization: rejected.
- Remove RPC tuple/range/parent/bigint checks, finite feature/prediction checks, distinct `attempt`
  boundaries, native tensor validation, copied outputs, artifact caching, or native serialization:
  rejected because these guard raw, scientific, or native seams.
- Add compatibility props, migration readers, aliases, fallbacks, or architecture-transition
  tests: rejected by the clean-break policy.

## Per-slice implementation-review protocol

After explicit implementation authorization, the orchestrator must for each slice:

1. record exact baseline SHA, branch/status, allowed mutation scope, checkout policy, implementer,
   and reviewer in this ledger;
2. dispatch a fresh implementer instructed to read and use the `implement` skill, edit only the
   slice scope, run focused and full app checks, commit the product change, and report the SHA;
3. verify the actual commit, clean status, and scoped diff before review;
4. dispatch a distinct fresh reviewer instructed to read and use `code-review`, pin
   baseline-to-head, remain read-only, run Standards and Spec as separate parallel axes, and return
   `GREEN LIGHT` only with zero actionable findings;
5. return rejected findings to the same implementer, then correction hunks to the same reviewer,
   until green;
6. run a proportional orchestrator integration/status check, update this ledger, and only then
   advance to the next slice.

The orchestrator does not implement or review product changes. No implementation/review overlap is
allowed on a shared checkout. No push, PR, external RPC, device, simulator, exporter, remote,
Slurm, or image action occurs without separate authority.

## Completion gate

After every authorized slice is independently green:

- run the complete app test suite, TypeScript check, strict unused check, Expo Doctor, lock check,
  and diff/status/residue audit;
- inspect the full planning-baseline-to-head range for accidental Analytics, graph, history,
  scientific, RPC, native, or documentation drift;
- record every slice baseline/final SHA, implementer, reviewer, correction round, check, unrun
  external gate, and final branch/worktree state here;
- keep native simulator/device, real RPC, and generated-model claims explicitly deferred until
  their existing asset-dependent activation gate;
- delete this temporary ledger only if the user requests cleanup after all authorized work and
  final integration checks are green; propagate that deletion to every in-scope branch before
  reporting completion;
- remove only run-owned branches/worktrees and restore the pre-run branch/worktree shape.
