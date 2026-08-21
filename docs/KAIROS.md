# KAIROS

KAIROS is a closed-parent, fixed-block-horizon system for learning when a future block is likely to minimize base fee per gas. This manual is the canonical detailed account of the product's scientific contract, worked decision, architecture, interfaces, requests, durable objects, commands, operator configuration, mobile surface, evaluation schemas, limitations, and sources.

KAIROS derives from and extends selected temporal work from *SPICE: A Predictive Framework for Cost-Optimization in Multichain Environments*. KAIROS is neither SPICE nor a reproduction of SPICE. Domain terms are defined in [CONTEXT.md](CONTEXT.md); active durable-object and execution-boundary decisions are indexed in [adr/](adr/).

## Contents

- [Overview](#overview)
- [One decision, end to end](#one-decision-end-to-end)
- [Scientific contract](#scientific-contract)
- [Architecture and deep interfaces](#architecture-and-deep-interfaces)
- [Exact reference](#exact-reference)
- [Limitations and sources](#limitations-and-sources)

## Overview

KAIROS is organized around strict request values, direct owner functions, native library objects, and UUID-addressed durable objects. Dependencies point from operator edges toward scientific owners.

### System shape

```text
verified Blockweaver dataset
        |
        v
strict workflow request --> CLI or direct Python call
        |
        +--> candidate fitting -> Study
        +--> selected fitting --> native Lightning artifact
        +--> evaluation -> observations.parquet
        |
        v
transient observation-derived reductions
```

`kairos.config` owns frozen Pydantic values, small discriminated unions, and fresh request construction through model defaults. Raw JSON and durable bytes are strictly hydrated once at their owning boundary; downstream code trusts those typed values and their already-typed nested values.

### Dependency direction

```text
cli / experiment runners
  ├─> workers ───> config
  ├─> modeling ───> corpus, study, temporal, min_block_fee
  ├─> evaluation ─> corpus, temporal, modeling, min_block_fee
  └─> Servatus campaign and publication interfaces

temporal ─────────> corpus, min_block_fee
corpus / study / min_block_fee / workers
         └────────> config and strict records
```

This high-level diagram summarizes the production import direction. Direct owner seams are:

- `corpus` resolves UUID-addressed Blockweaver datasets and maps their rows to canonical
  `BlockFrame` values.
- `temporal` owns causal feature state, fixed-block context/outcome geometry, and lazy historical examples.
- `min_block_fee` owns target state, the fixed training loss, two-head output, and decode.
- `modeling` owns request-bound candidate and selected fitting, the three concrete neural
  definitions, Lightning fitting, candidate retention, and native checkpoint loading.
- `study` owns bounded candidate membership, ordered retained results, publication, and selected-Method loading.
- `evaluation` owns canonical self-contained observations and transient reduction.
- `workers` maps typed workflow and candidate inputs to opaque durable-work tasks.

The closed model union is LSTM, Transformer, or Transformer-LSTM. Historical preparation supplies lazy contiguous CPU-backed examples; each model consumes float32 `[B,C,F]` and returns action logits `[B,K]` plus standardized minimum-fee prediction `[B]`. Architecture stays independent of target construction and evaluation accounting.

Blockweaver owns Corpus artifact production and validation
([ADR 0009](adr/0009-blockweaver-dataset-authority.md)). KAIROS delegates native remote execution and publication mechanics
at the Servatus lifecycle boundary ([ADR 0008](adr/0008-servatus-lifecycle-boundary.md)). Completed
objects own one exact request at direct canonical addresses; UUIDs identify instances and typed
associations establish meaning ([ADR 0006](adr/0006-direct-durable-object-authority.md)).

## One decision, end to end

KAIROS makes a decision immediately after a closed parent block `h`. Every number in this hand-computable Ethereum example is a fabricated teaching value.

### 1. Fix the geometry

Suppose:

```text
h = 25,400,000
C = 200 closed context blocks
K = 5 future outcome blocks
```

The model may see exactly blocks `h-C+1 … h`, or `25,399,801 … 25,400,000`. The complete outcome is `h+1 … h+K`. Actions are zero-based:

| Action `k` | Intended target block |
| ---: | ---: |
| 0 | 25,400,001 |
| 1 | 25,400,002 |
| 2 | 25,400,003 |
| 3 | 25,400,004 |
| 4 | 25,400,005 |

The arithmetic is always `target_block = h + 1 + k`.

### 2. Build only closed-parent inputs

For this calculation only, let the request's ordered feature tuple contain three supported features. Suppose closed parent `h` has:

```text
base_fee_per_gas = 24,000,000,000 wei/gas
gas_used         = 27,000,000 gas
gas_limit        = 36,000,000 gas
```

The raw closed-row features are:

```text
log_base_fee_per_gas = ln(24,000,000,000 / (1 wei/gas))
                     = 23.901320

gas_utilization = 27,000,000 / 36,000,000
                = 0.75
```

Ethereum's forming-child fee follows the exact parent recurrence. The parent target is `36,000,000 // 2 = 18,000,000 gas`. Usage exceeds target by `9,000,000`, so ordered integer arithmetic gives:

```text
increase = 24,000,000,000 * 9,000,000 // 18,000,000 // 8
         = 1,500,000,000 wei/gas

forming_child_base_fee = 25,500,000,000 wei/gas

log_exact_forming_base_fee_per_gas
  = ln(25,500,000,000 / (1 wei/gas))
  = 23.961944
```

All feature inputs come from block `h` or earlier. The exact child fee is an Ethereum parent-state result. The other 199 rows are prepared the same way from their own closed facts.

Training-only Float64 means and population standard deviations standardize the ordered raw matrix. The one-origin input is finite float32 `[C,F] = [200,3]`; a live batch is `[1,200,3]`.

### 3. Keep outcomes on the other side of the origin

Invent these complete future base fees:

```text
h+1 ... h+5 = [25.5, 23, 21, 20, 22] gwei/gas
```

They are stored and compared as positive Int64 wei/gas:

```text
[25_500_000_000, 23_000_000_000, 21_000_000_000, 20_000_000_000, 22_000_000_000]
```

Using the [canonical notation](#decision-and-target-notation), the raw outcomes are
`B_i(0) … B_i(4)`, the label is `k_i*=3`, and `m_i=20,000,000,000 wei/gas`.

The dataset item is:

| Value | Shape and dtype |
| --- | --- |
| `inputs` | `[200,3]`, float32 |
| `label` | scalar, int64 |
| `target` | scalar, float32 |
| `base_fees` | `[5]`, int64 |
| `origin_block` | scalar, int64 |

The raw minimum first enters Float64 natural-log coordinates:

```text
ell_i = ln(20,000,000,000 / (1 wei/gas)) = 23.718998
```

For a purely illustrative fitted `TargetState(mean=23.5, standard_deviation=0.25)`:

```text
mu_ell    = 23.5
sigma_ell = 0.25
z_i       = (23.718998 - 23.5) / 0.25 = 0.875992
```

Real state is fitted once from all retained training-origin minima with Float64 `ddof=0`. Validation, testing, and live inference use the persisted state.

### 4. Separate the roles

Every retained origin must have its complete `K`-block outcome inside its role. If validation begins at parent block `V`, a training origin is eligible only when `h+K < V`. Testing starts only after `validation_last_parent + K`.

Training fits feature state, target state, and weights. Validation selects epochs and retained candidate objectives. Testing measures held-out behavior.

### 5. Compute one two-head loss

For one origin, suppose the model returns:

```text
action_logits = [0.2, 1.1, -0.1, 1.7, 0.5]
minimum_fee_z = 0.7
```

The five `action_logits` values are `a_i0 … a_i4`. With `k_i*=3`, cross-entropy is:

```text
CE = log(sum_{k in 𝒦}(exp(a_ik))) - a_i,k_i*
   = log(exp(0.2)+exp(1.1)+exp(-0.1)+exp(1.7)+exp(0.5)) - 1.7
   ≈ 0.805777
```

Here `hat{z}_i=0.7`, so `e_i=hat{z}_i-z_i=0.7-0.875992=-0.175992`. Native
Smooth L1 uses its default transition at one standardized-target unit, so `|e_i| < 1`:

```text
SmoothL1(e_i) = 0.5 * e_i^2 ≈ 0.015487
total         = CE + SmoothL1(e_i) ≈ 0.821264
```

For this one-origin batch, the batch mean equals `total`. In a larger batch every origin
contributes native unweighted cross-entropy plus native default Smooth L1 once, with sample count
`B` as the denominator. No loss definition, mode, scale, threshold, or fitted classification state
is request or artifact authority.

### 6. Decode and evaluate

Canonical decode gives `hat{k}_i=3`. The intended target is block `25,400,004`.

For this outcome:

```text
B_i(0)        = 25.5 gwei/gas
B_i(hat{k}_i) = B_i(3) = 20.0 gwei/gas
P_i(0)        = 2.0 gwei/gas
P_i(hat{k}_i) = P_i(3) = 4.0 gwei/gas
k_i*          = 3
m_i           = B_i(k_i*) = 20.0 gwei/gas
```

The durable observation stores:

```text
origin_block                         = 25,400,000
predicted_action_k                   = 3
predicted_minimum_log_base_fee       = 23.675
minimum_action_k                     = 3
immediate_base_fee_per_gas           = 25,500,000,000
immediate_effective_priority_fee_per_gas_p50 = 2,000,000,000
selected_base_fee_per_gas            = 20,000,000,000
selected_effective_priority_fee_per_gas_p50  = 4,000,000,000
minimum_base_fee_per_gas             = 20,000,000,000
```

Reduction uses this row directly. Base-fee savings is `(25.5-20.0)/25.5 ≈ 0.215686`; P50 fee-inclusive savings is `1-((20.0+4.0)/(25.5+2.0)) ≈ 0.127273`; and the optimality gap is `(20.0-20.0)/20.0 = 0`. The absolute natural-log error is about `0.043998` and the squared error about `0.001936`. No losses, timestamps, waits, horizons, standardized predictions, or derived metrics are stored in the observation.

### 7. Carry the same contract on device

The exported manifest and model fix chain association, `C`, `K`, ordered features, feature state,
target state, model definition, and weights. Selection remains idle. On Run, the app reads a fresh
latest closed head and exact `C`-block range, adding only the predecessor required by interval
features. It creates `[1,C,F]`, loads or reuses the bundled model, validates both native outputs,
and decodes the action in the same way. The first Run accepts model-load and RPC latency.

Continuing the teaching values, the app result shape is:

```json
{
  "head_block": 25400000,
  "selected_action_k": 3,
  "target_block": 25400004,
  "predicted_minimum_base_fee_per_gas": 19139115255.738445
}
```

The last value follows current mobile decoding arithmetic: the displayed float32 `0.7` is
`0.699999988079071` as a Python float, then
`u * exp(hat{ell}_i) = (1 wei/gas) * exp(23.5 + 0.25 * 0.699999988079071)`.

## Scientific contract

KAIROS is a closed-parent, fixed-block-horizon temporal learning system. This document owns the causal information set, `C/K/k` geometry, fitted-state rules, feature and target equations, evaluation estimands, claim boundaries, sources, and limitations.

### Lineage and ownership

The manuscript *SPICE: A Predictive Framework for Cost-Optimization in Multichain Environments* describes a broader spatial, temporal, and distributed-reputation system. Its temporal experiment motivates a future minimum-block decision, an associated scalar fee prediction, the LSTM/Transformer/Transformer-LSTM comparison, chronological roles, and a weighted cross-entropy plus Smooth-L1 lineage.

KAIROS specifies the current closed-parent origins, fixed block-count geometry, causal features,
raw-integer target selection, training-fitted state, fixed training loss, exhaustive equal-origin
evaluation, durable objects, and mobile semantics.

### Closed-parent causality

A decision origin occurs immediately after block `h` closes. Facts in blocks through `h` may be inputs. Facts from `h+1` onward are outcomes and cannot influence features or fitted state available at that origin.

For context length `C` and horizon `K`:

```text
context rows:  h-C+1, ..., h
outcome rows:  h+1,   ..., h+K
actions:       k in {0, ..., K-1}
target block:  b = h+1+k
```

Block number owns geometry. Timestamp spacing may vary while the number of context and outcome rows stays fixed.

`C` and `K` are generic positive request values. Python owns no named study matrix, ordering, or staged stopping policy; external orchestration supplies actual runs, and persisted requests and artifacts record what ran.

An origin is eligible only with all `C` context rows and all `K` outcome rows. At a boundary where the next role begins at parent `V`, an earlier origin must satisfy `h+K < V`. Therefore no training outcome reaches validation, and no validation outcome reaches testing.

### Decision and target notation

For origin `i` with closed parent `h_i`, the canonical decision and scalar-target notation is:

```text
𝒦          = {0, ..., K-1}
B_i(k)     = raw base fee at h_i+1+k, for k in 𝒦
k_i*       = argmin_{k in 𝒦} B_i(k), defined as the smallest minimizing k
m_i        = B_i(k_i*) = min_{k in 𝒦} B_i(k)
u          = 1 wei/gas
ell_i      = ln(m_i / u)
mu_ell     = mean_Float64(ell_i over retained training origins)
sigma_ell  = std_Float64(ell_i over retained training origins, ddof=0)
z_i        = Float32((ell_i - mu_ell) / sigma_ell)
a_ik       = action logit for k in 𝒦
hat{k}_i   = argmax_{k in 𝒦} a_ik
hat{z}_i   = predicted standardized log minimum
hat{ell}_i = mu_ell + sigma_ell * hat{z}_i
```

Raw Int64 fee comparison defines `k_i*` and `m_i` before any floating conversion. The fitted
`sigma_ell` must be positive. Because `m_i/u` is a ratio of like units, `ell_i` and `hat{ell}_i`
are dimensionless log coordinates.

### Role ownership and fitted populations

Training alone may fit:

- feature population means and standard deviations;
- target natural-log mean and standard deviation;
- neural weights.

Validation selects the earliest best epoch and supplies candidate objectives. Testing measures only. Changing a method, feature route, horizon, context, or other scientific decision after inspecting testing would turn that measurement into selection evidence.

#### Feature state

Let raw training-support feature row `x_r ∈ R^F`. For each ordered feature `j`:

```text
mu_j    = (1/N) sum_r x_rj
sigma_j = sqrt((1/N) sum_r (x_rj - mu_j)^2)
z_rj    = (x_rj - mu_j) / sigma_j
```

Fitting uses Float64 and `ddof=0`; every `sigma_j` must be positive. Transformation returns finite float32. Training support contains each closed block row once, so overlapping model windows do not reweight feature-state fitting.

### Causal features

The request supplies a nonempty unique ordered tuple drawn from the supported names, making feature choice request-authored.

| Feature | Raw equation and unit | Domain and availability |
| --- | --- | --- |
| `log_base_fee_per_gas` | `ln(base_fee_per_gas / (1 wei/gas))` | Fee positive; closed-row header fact. |
| `gas_utilization` | `gas_used / gas_limit` | `gas_limit>0`, `0≤gas_used≤gas_limit`; known after row close. |
| `log_exact_forming_base_fee_per_gas` | `ln(exact_child_base_fee / (1 wei/gas))` | Positive; Ethereum-only parent-state recurrence. |
| `log_gas_limit` | `ln(gas_limit / (1 gas))` | Gas limit positive; closed-row header fact. |
| `log1p_tx_count` | `ln(1 + tx_count / (1 transaction))` | Transaction count nonnegative; known after row close. |
| `log1p_effective_priority_fee_per_gas_p50` | `ln(1 + effective_priority_fee_per_gas_p50 / (1 wei/gas))` | P50 nonnegative; included-transaction closed-row fact. |
| `log1p_effective_priority_fee_per_gas_p90` | `ln(1 + effective_priority_fee_per_gas_p90 / (1 wei/gas))` | P90 nonnegative; included-transaction closed-row fact. |
| `block_interval_seconds` | `timestamp_b - timestamp_{b-1}` seconds | Nonnegative; requires the real predecessor row. |
| `hour_sin` | `sin(2π hour_UTC/24)` | `hour_UTC = (timestamp//3600) mod 24`; closed timestamp. |
| `hour_cos` | `cos(2π hour_UTC/24)` | Same angle and availability. |
| `dow_sin` | `sin(2π day_UTC/7)` | `day_UTC = ((timestamp//86400)+4) mod 7`, with Sunday zero; closed timestamp. |
| `dow_cos` | `cos(2π day_UTC/7)` | Same angle and availability. |

The exact forming-fee column implements the Ethereum parent-known recurrence. Polygon and Avalanche requests use the other supported features.

#### Ethereum forming-child recurrence

For positive parent fee `f`, parent gas used `g`, and positive gas limit `L`, use Python integers throughout:

```text
t = L // 2

if g == t:
    f_child = f
elif g > t:
    f_child = f + max(f * (g - t) // t // 8, 1)
else:
    f_child = f - f * (t - g) // t // 8
```

`t` and the final child fee must be positive. Python integers carry the recurrence through the two ordered divisions; the one-wei floor applies only upward. The completed positive integer is then logged in Float64. This follows the integer ordering in [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559#specification).

### Historical tensors and targets

One lazy historical item has:

| Value | Shape | Dtype | Meaning |
| --- | --- | --- | --- |
| `inputs` | `[C,F]` | float32 | Standardized closed rows `h_i-C+1 … h_i`. |
| `label` | scalar | int64 | Canonical `k_i*`. |
| `target` | scalar | float32 | Canonical `z_i`. |
| `base_fees` | `[K]` | int64 | `[B_i(0), ..., B_i(K-1)]`. |
| `origin_block` | scalar | int64 | Closed parent `h_i`. |

Collation produces `[B,C,F]`, `[B]`, `[B]`, `[B,K]`, and `[B]`.

For origin `i`, the positive Int64 outcome vector is
`[B_i(0), ..., B_i(K-1)]`. The [canonical notation](#decision-and-target-notation) defines its
`k_i*`, `m_i`, `ell_i`, and `z_i`; NumPy [`argmin`](https://numpy.org/doc/stable/reference/generated/numpy.argmin.html)
implements that raw-integer action selection.

Target state is fitted over retained training origins only. Float64 mean and `ddof=0` population
standard deviation produce canonical `mu_ell` and positive `sigma_ell`; transformation follows
the canonical `z_i` equation exactly and returns float32.

### Targets, loss, and decode

All concrete model definitions return:

```text
action_logits: [B,K]
minimum_fee_z: [B]
```

The first head supplies canonical logits `a_ik`. The second predicts canonical `hat{z}_i`, the
standardized dimensionless log of the same horizon minimum.

#### Classification

For origin `i`, using its logits `a_i0 … a_i,K-1` and label `k_i*`:

```text
c_i = CE([a_i0, ..., a_i,K-1], k_i*)
```

Classification is native unweighted cross-entropy. It has no weighting mode, scale, fitted support, or configuration field.

#### Regression

Regression is native Smooth L1 with its default transition at one standardized-target unit. Its
error is `e_i=hat{z}_i-z_i`:

```text
smooth_l1(e_i) = 0.5 e_i^2       if |e_i| < 1
                 |e_i| - 0.5     otherwise

r_i = smooth_l1(e_i)
```

#### Total

```text
t_i = c_i + r_i
L_batch = (sum_i t_i) / B
```

The denominator is the number of origins in the batch. These are training and validation losses only. The operative functions match PyTorch's [`cross_entropy`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html) and [`smooth_l1_loss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.smooth_l1_loss.html).

Decode implements canonical `hat{k}_i` with native `argmax(action_logits, dim=-1)`. Equal maximum
logits select the first index, and decode depends on the logits alone.

#### Validation objective

For each validation origin, let `m_i=min_k B_i(k)`. The decoded action contributes:

```text
q_i = (B_i(hat{k}_i) - m_i) / m_i
```

Validation logs `mean_i q_i` as `validation_base_fee_optimality_gap`. Loss-based early stopping remains unchanged. The retained best checkpoint and Study `objective` use the smallest validation gap, so all downstream selection is economic and lower-is-better without changing gradient training.

### Model concepts

KAIROS uses a closed discriminated union of three concrete sequence models:

- LSTM recurrently summarizes the fixed context and uses its final state.
- Transformer projects each row, adds sinusoidal positions, applies self-attention, and uses the final encoded position.
- Transformer-LSTM applies the Transformer encoder, then recurrently summarizes the encoded sequence.

All three attach the same two MLP heads. Architecture capacity belongs to `ModelDefinition` or Method; target and loss meaning stays in `kairos.min_block_fee`.

### Evaluation estimands

For any validation or testing origin `i`, the canonical observation stores these direct values:

```text
hat{k}_i        predicted action
k_i*            minimum action
B_i(0)          immediate base fee
B_i(hat{k}_i)   selected base fee
P_i(0)          included-transaction effective-priority-fee P50 in block h_i+1
P_i(hat{k}_i)   included-transaction effective-priority-fee P50 in block h_i+1+hat{k}_i
m_i             minimum base fee
hat{ell}_i      predicted dimensionless log minimum
```

Evaluation de-standardizes `hat{z}_i` to `hat{ell}_i` before publication. Reduction reads the
stored facts directly; `ell_i=ln(m_i/u)` is the true dimensionless log coordinate.

Validation and testing use one observation reducer. It returns eleven scientific metrics plus four
presentation-time Gwei summaries:

```text
accuracy                = mean_i indicator[hat{k}_i = k_i*]
f1_macro                = mean_c 2 TP_c / (2 TP_c + FP_c + FN_c)
log_fee_mae             = mean_i |hat{ell}_i - ell_i|
log_fee_mse             = mean_i (hat{ell}_i - ell_i)^2
base_fee_savings        = mean_i ((B_i(0) - B_i(hat{k}_i)) / B_i(0))
mean_p50_fee_inclusive_savings
                        = mean_i (1 - (B_i(hat{k}_i) + P_i(hat{k}_i))
                                          / (B_i(0) + P_i(0)))
trimmed_mean_p50_fee_inclusive_savings
                        = the same mean after rank-removing the lowest and highest 2.5%
p25_p50_fee_inclusive_savings
                        = lower quartile of the same per-origin ratios
median_p50_fee_inclusive_savings
                        = median_i (1 - (B_i(hat{k}_i) + P_i(hat{k}_i))
                                            / (B_i(0) + P_i(0)))
p75_p50_fee_inclusive_savings
                        = upper quartile of the same per-origin ratios
base_fee_optimality_gap = mean_i ((B_i(hat{k}_i) - m_i) / m_i)
mean_immediate_base_fee_gwei
mean_selected_base_fee_gwei
mean_minimum_base_fee_gwei
mean_selected_minus_minimum_base_fee_gwei
```

`f1_macro` is standard unweighted macro-F1 over the union of action classes present in truth or predictions. Classes absent from both do not enter the mean.

Base-fee savings and Cost over optimum remain mean per-origin fractions, not ratios of fee sums. P50 fee-inclusive savings reports the P25, median, P75, and tail-sensitive arithmetic mean across per-origin ratios. Positive base fees make their denominators defined. The P50 fields are retrospective representative-cost proxies using each outcome block's included-transaction P50, not inclusion guarantees. Natural-log errors compare dimensionless coordinates relative to `u=1 wei/gas` and lower is better. Accuracy and macro-F1 are unitless and higher is better. Economic values remain fractions for later percentage formatting.

The four Gwei summaries are descriptive within one chain. Native-token value and transaction gas
use differ, so they are not pooled monetary comparisons across chains.

Immediate and deadline baselines are economic reference policies. Their rows contain only base-fee
savings, P50 fee-inclusive savings, and base-fee optimality gap. The immediate policy always
selects `k=0`; the deadline policy always selects `k=K-1`.

#### Fixed-deadline rolling comparison

The rolling comparison fixes each `K=5` origin `h` and deadline `D=h+5`. Starting at `h`, it runs `K=5`, `K=4`, `K=3`, and `K=2` exactly once in that order. After each of the first three predictions, the next smaller model runs at the same decision origin unless the current model selected its final visible block, `k=K-1`; that terminal action advances the decision origin by one block. Each smaller model replaces the preceding prediction. The `K=2` prediction is final and selects `b=t+1+k`, where `t` is its decision origin. At most three origin advances followed by a two-block prediction keep `b≤D`.

Every selected observation uses only context closed by its own decision origin. The comparison reconstructs the policy from precomputed predictions and performs no model inference or Corpus hydration.

For every architecture-chain cell, the rolling reduction uses every `K=5` testing origin at stride one and returns one-shot and rolling values for base-fee savings, P50 fee-inclusive savings, and base-fee optimality gap. Savings use the immediate action as their baseline; optimality gap uses the earliest minimum within the original five-block window. Point estimates are exact descriptive summaries for the sealed held-out period. `reduce_rolling_intervals()` resamples complete UTC-hour clusters 5,000 times with a fixed seed and returns 95% percentile intervals for one-shot, rolling, and their paired difference in the two mean economic metrics. It performs no reevaluation or model inference.

### HPO interpretation

A `TuneRequest` freezes the experiment and one finite tuple of complete Methods. An operator submits an index into that tuple. Each successful fit contributes validation base-fee optimality gap, earliest best epoch, and completed epochs in request order. Selected training names an exact result index.

The thesis protocol is staged: measure the full, individual leave-one-feature-unit-out, and
base-only configurations at reference geometry; select one feature route per chain by the lowest
mean validation objective across the three architectures among the full and leave-one-out
configurations; run the `C` study; run HPO; then run `K` sensitivity and final testing. Fit methods
use seed `2026`. This is not a full factorial design.

## Architecture and deep interfaces

The sections below place each direct owner interface beside the scientific and durable-object
contracts it serves. Exact public records, paths, commands, operator profiles, and schemas remain
in [Exact reference](#exact-reference).

### Corpus input

KAIROS consumes one immutable Blockweaver dataset. The Blockweaver UUID is the KAIROS Corpus ID.

```text
datasets/<corpus_id>/
  manifest.json
  blocks.parquet
```

`blockweaver.open_dataset()` validates the UUID-bound manifest, artifact digest, source and
verification facts, resolved range, schema, row domains, and exact two-file publication.
`open_corpus_dataset()` exposes the validated `Dataset` for metadata-only callers without
hydrating rows. `load_corpus_blocks()` reads its data path as Parquet and lets `BlockFrame` enforce
KAIROS's exact ordered eight-column scientific schema.

`BlockFrame(frame, chain_id)` is the public canonical-row interface. It stores chain identity once,
derives `first_block` and `last_block` from its nonempty rows, returns inclusive subranges through
`select_range(first_block, last_block)`, and returns an isolated native frame through `to_polars()`.
Construction checks the exact schema and nonempty extent; native access isolates caller mutation.
Range selection is positional and does not rescan rows. The value carries neither hashes nor
finality provenance.

### Temporal preparation

Temporal preparation has two direct paths: historical fixed-block examples and live closed-head inference. Both use the same ordered feature contract and persisted training-only feature state.

`prepare_fit_history(blocks, experiment)` validates complete context/outcome support, fits state from training support only, and returns training and validation `HistoricalDataset` values with `FeatureState` and `TargetState`. `prepare_historical_window(blocks, experiment, window, *, feature_state, target_state)` prepares an exact testing window with persisted state after complete validation outcomes.

Preparation keeps the first backing block, contiguous CPU float32 feature rows, and int64 base
fees. Each dataset stores its first origin row and sample count plus int64 `k_i*` labels and
float32 `z_i` targets. `HistoricalDataset.__getitem__()` derives the origin row and block, then
slices one `[C,F]` input and `[K]` outcome on demand.

The ordered feature tuple is request authority. Raw features are assembled in that order as Float64; training-support population state uses `ddof=0`, rejects constants, and transforms to finite C-contiguous float32. Outcomes remain positive int64 `B_i(k)` values. The [scientific contract](#causal-features) owns formulas, causality, target construction, and complete-outcome role boundaries.

For live inference, each Run reads one closed head and one fresh exact context, reproduces the historical feature transform, and constructs float32 `[1,C,F]`; `block_interval_seconds` requires `C+1` raw blocks. The bundled cell fixes `C`, `K`, feature order, and fitted states. Decode returns target block `h_i+1+hat{k}_i` and positive finite `u * exp(hat{ell}_i)`. Historical preparation remains the parity authority; [Mobile deployment](#mobile-deployment) owns the build-time boundary.

### Minimum-block-fee task

Top-level `kairos.min_block_fee` keeps the architecture-neutral target, loss, and decode contract. Temporal preparation supplies its targets, model families return its output, and evaluation consumes the result.

#### Owned values

`TargetState` contains canonical `mu_ell` and positive `sigma_ell`, the Float64 population state of
dimensionless `ell_i=ln(m_i/u)` over retained training origins.

`MinBlockFeeOutput` has two tensors:

```text
action_logits:  [B,K]
minimum_fee_z:  [B]
```

The scalar head predicts canonical `hat{z}_i`, the standardized dimensionless log of the horizon
minimum. Its scientific interpretation is defined in the [theory](#targets-loss-and-decode).

#### Direct functions

- `fit_target_state(raw_minima)` requires a nonempty positive int64 vector, computes Float64
  `ell_i`, `mu_ell`, and `sigma_ell` with `ddof=0`, and rejects constant targets.
- `standardize_target(raw_minima, state)` returns finite contiguous float32 `z_i` values.
- `min_block_fee_loss(...)` trusts tensors owned by model and historical-preparation internals. It
  directly returns native unweighted cross-entropy plus native default Smooth L1 per origin.
  Training takes the tensor mean for backpropagation; validation detaches and accumulates Float64
  batch means weighted by origin count.
- `decode_action(output)` applies the canonical action decode.

The exact equations are in the [theory](#targets-loss-and-decode).

#### Boundaries

Temporal preparation owns raw `[K]` `B_i(k)` outcomes, `k_i*` labels, and standardized `z_i`
targets. Model fitting owns checkpoint selection and one selected-checkpoint validation pass.
Validation and held-out evaluation share observation collection and scientific reduction.

### Study

Tuning is a bounded question over a finite tuple of complete Methods. A Study contains the exact `TuneRequest` and its ordered successful results.

#### Request and membership

`TuneRequest` fixes a Study UUID, Corpus UUID, `ExperimentSemantics`, and a nonempty tuple of unique complete Methods. Every Method uses the same model family and owns one `ModelDefinition` plus its complete fit policy. Candidate fitting resolves a validated zero-based index through `request.method_at(method_index)` and passes `TrainingDefinition(experiment=request.experiment, method=method)` directly as its checkpoint association. Canonical artifacts instead retain their full `ArtifactAssociation`.

#### Candidate run

`modeling.run_candidate(storage_root, request, method_index)` loads the request's Corpus, prepares
training history and state, fits the indexed Method through native Lightning, and retains one
successful result in the Study's indexed Servatus child workspace. After fitting, the exact
selected checkpoint runs once over the exact validation window. Candidate success publishes that
checkpoint, canonical observations, and result metadata; failure preserves `last.ckpt` for
full-state resume. Candidate checkpoints embed only the `TrainingDefinition` needed to rebuild the
candidate model.

`RetainedResult` has three fields:

- finite complete-validation base-fee optimality-gap objective;
- one-based earliest selected epoch;
- one-based completed epoch count.

The selected epoch cannot exceed completed epochs. The enclosing Study requires one result per request Method and checks completed epochs against the corresponding Method maximum.
`Study.best_result()` owns selection and returns the earliest request index when objectives tie.

#### Indexed results and publication

Each retained trial carries the full request, compact result, selected checkpoint, and validation
observations. `publish_study(storage_root, study_id)` requires exactly one retained trial per
request Method, identical requests, exact checkpoint associations, canonical observation schemas,
and objective equality. It assembles and publishes the complete object to:

```text
studies/<study_id>/
  study.json
  trials/<method_index>/
    selected.ckpt
    validation.parquet
```

Servatus preserves resumable work on failure and removes it after successful publication.

#### Selected training

A `TrainRequest` supplies the exact Study UUID and zero-based `study_result_index`. `load_selected_method()` strictly loads the canonical Study, verifies Study and Corpus associations, and returns `study.request.methods[study_result_index]`. The artifact association composes its `TrainingDefinition` from the source experiment and returned Method.

The resulting native artifact embeds the same result index and Method for later loading and evaluation.

### Evaluation

Evaluation separates canonical self-contained observations from transient metrics. Explicit UUIDs connect the request, artifact, Corpus, and observations.

#### Canonical evaluation

`evaluate(request, storage_root)` loads the exact Corpus and native artifact, requires the artifact's source Corpus to equal the evaluation Corpus, prepares the testing origin window with persisted state, and performs CUDA inference.

For every eligible origin the evaluation publisher owns construction of one ordered, nonnull observation containing `h_i`, `hat{k}_i`,
`k_i*`, `hat{ell}_i`, `B_i(0)`, `P_i(0)`, `B_i(hat{k}_i)`, `P_i(hat{k}_i)`,
`B_i(K-1)`, `P_i(K-1)`, and `m_i` under the canonical field names. One disposable Servatus
publication attempt builds and publishes the validated pair to:

```text
evaluations/<evaluation_id>/
  evaluation.json
  observations.parquet
```

The JSON is exactly the `EvaluateRequest`. The parquet schema is the canonical eleven-column contract in the [reference](#canonical-observations).

#### Transient reduction

`reduce_evaluation(storage_root, evaluation_id) -> polars.DataFrame` validates the exact Parquet schema and reduces only `observations.parquet`. Atomic publication owns its pairing with `evaluation.json`, ordered testing-origin coverage, and row values. `reduce_baselines(storage_root, evaluation_id) -> polars.DataFrame` derives the three economic metrics for the immediate and deadline policies under the same trust boundary. Neither reducer reloads the request, artifact, or Corpus or externally authenticates the horizon or source. Results have no evaluation ID, count, sums, supports, arrays, or auxiliary fields and are not persisted.

Public `reduce_rolling(storage_root, roster) -> polars.DataFrame` reads only each named Evaluation's `observations.parquet`. Its in-memory roster maps human-readable architecture-chain cell names to the required horizon `2`, `3`, `4`, and `5` Evaluation UUIDs. The final experiment runner owns that scientific association and builds the three selected chain-LSTM cells. Reduction verifies exact schemas, consecutive origins, predicted-action ranges, and required decision-origin coverage. Its six-metric rows are transient and are not persisted.

## Exact reference

This reference defines KAIROS's strict requests, completed objects, direct addresses, commands,
operator profiles, mobile bundle and runtime surfaces, and evaluation schemas.

### Scalar conventions

- Object IDs are UUIDv4.
- `PositiveInt` means strict integer `>0`; `NonNegativeInt` means strict integer `≥0`. Booleans are not integers.
- Scientific floats are finite. Positive/nonnegative bounds are stated per field.
- Block ranges and origin windows are inclusive.
- Base fees are positive Int64 wei/gas unless a field explicitly says Float64 aggregation.
- Timestamps and elapsed values are integer seconds.
- Raw JSON and durable bytes hydrate once with strict scalar parsing and unknown-field rejection. `StrictFrozenRecord` values are immutable; downstream code trusts already-typed nested Pydantic values instead of revalidating instances.

Distribution name, import root, and installed executable are `kairos`; the static distribution version is `0.1.0`.

### Requests and definitions

#### Scientific semantics

| Record | Ordered field | Type and rule |
| --- | --- | --- |
| `BlockWindow` | `first_parent_block` | NonNegativeInt |
|  | `last_parent_block` | NonNegativeInt, not before first |
| `ExperimentSemantics` | `training_window` | `BlockWindow` |
|  | `validation_window` | `BlockWindow` |
|  | `context_blocks` | PositiveInt `C` |
|  | `horizon_blocks` | PositiveInt `K` |
|  | `ordered_features` | nonempty unique tuple of supported `FeatureName` literals |

The training last parent plus `K` must be strictly less than the validation first parent.

#### Model definitions

`ModelDefinition` is a discriminated union on `family`:

| Family | Ordered fields after `family` |
| --- | --- |
| `lstm` | `hidden: PositiveInt`; `layers: PositiveInt`; `head_hidden: PositiveInt`; `dropout: 0≤float<1` |
| `transformer` | `model_width`; `attention_heads`; `transformer_layers`; `feedforward_width`; `head_hidden`: PositiveInt; `dropout: 0≤float<1` |
| `transformer_lstm` | `model_width`; `attention_heads`; `transformer_layers`; `feedforward_width`; `lstm_hidden`; `lstm_layers`; `head_hidden`: PositiveInt; `dropout: 0≤float<1` |

Only `model_width` must be even and divisible by `attention_heads`; `feedforward_width`, head widths, and LSTM widths are positive but have no such divisibility rule.

#### Method

| Record | Ordered field | Type and rule |
| --- | --- | --- |
| `FitMethod` | `learning_rate` | finite float `>0` |
|  | `weight_decay` | finite float `≥0` |
|  | `accumulation` | PositiveInt |
|  | `gradient_clip_norm` | finite float `≥0` |
|  | `seed` | NonNegativeInt |
|  | `max_epochs` | PositiveInt |
|  | `validate_every_completed_epoch` | PositiveInt |
|  | `patience` | NonNegativeInt |
|  | `min_delta` | finite float `≥0` |

Every serialized `Method` has ordered fields `model: ModelDefinition` and `fit: FitMethod`. A `TuneRequest` owns a nonempty tuple of unique complete Methods and requires every `method.model.family` to match.

#### Study, training, and workflow requests

| Record | Ordered field | Type and rule |
| --- | --- | --- |
| `TrainingDefinition` | `experiment` | `ExperimentSemantics` |
|  | `method` | complete `Method` |
| `SelectedStudySource` | `corpus_id` | UUIDv4 |
|  | `study_id` | UUIDv4 |
|  | `study_result_index` | NonNegativeInt |
|  | `experiment` | `ExperimentSemantics` |
| `TrainRequest` | `workflow` | exactly `"train"` |
|  | `artifact_id` | UUIDv4 |
|  | `source` | `SelectedStudySource` |
| `TuneRequest` | `workflow` | exactly `"tune"` |
|  | `study_id` | UUIDv4 |
|  | `corpus_id` | UUIDv4 |
|  | `experiment` | `ExperimentSemantics` |
|  | `methods` | nonempty unique tuple of complete, same-family Methods |
| `EvaluateRequest` | `workflow` | exactly `"evaluate"` |
|  | `evaluation_id` | UUIDv4 |
|  | `artifact_id` | UUIDv4 |
|  | `corpus_id` | UUIDv4 |
|  | `testing_window` | `BlockWindow`; must follow complete validation outcomes |

`WorkflowRequest` is exactly `TrainRequest | EvaluateRequest`. `TuneRequest` is intentionally separate.

Direct construction defaults each workflow discriminator and mints the destination artifact, Study, or evaluation UUIDv4 when omitted. Source and association IDs remain required.

### Durable addresses and objects

Given an explicit `storage_root`:

```text
datasets/<corpus_id>/manifest.json
datasets/<corpus_id>/blocks.parquet
experiments/{feature_ablation,c_study,hpo,k_study,held_out}/<UUID>/manifest.json
studies/<study_id>/study.json
studies/<study_id>/trials/<method_index>/selected.ckpt
studies/<study_id>/trials/<method_index>/validation.parquet
artifacts/<artifact_id>/artifact.ckpt
artifacts/<artifact_id>/validation.parquet
artifacts/<artifact_id>/result.json
evaluations/<evaluation_id>/evaluation.json
evaluations/<evaluation_id>/observations.parquet
```

IDs are lowercase UUID strings produced by `str(UUID)` and appear directly in the paths above.

#### Corpus input

The directory is one strict Blockweaver dataset. Its `manifest.json` is the sole artifact authority
for UUID, chain, resolved range, provenance, verification, schema, and output digest. KAIROS accepts
only `blocks.parquet` with this exact ordered, nonnull projection:

| # | Column | Type | Unit/rule |
| ---: | --- | --- | --- |
| 1 | `block_number` | Int64 | contiguous inclusive request range |
| 2 | `timestamp` | Int64 | nonnegative seconds; nondecreasing |
| 3 | `base_fee_per_gas` | Int64 | positive wei/gas |
| 4 | `gas_used` | Int64 | gas, `0≤used≤limit` |
| 5 | `gas_limit` | Int64 | positive gas |
| 6 | `tx_count` | Int64 | nonnegative transaction count |
| 7 | `effective_priority_fee_per_gas_p50` | Int64 | nonnegative gas-used-weighted P50 among included transactions, wei/gas |
| 8 | `effective_priority_fee_per_gas_p90` | Int64 | nonnegative gas-used-weighted P90 among included transactions, wei/gas |

Direct loader:

```python
open_corpus_dataset(storage_root: Path, corpus_id: UUID4) -> blockweaver.Dataset
load_corpus_blocks(storage_root: Path, corpus_id: UUID4) -> BlockFrame
```

Both loaders resolve `storage_root / "datasets" / str(corpus_id)` through
`blockweaver.open_dataset()`. Metadata callers consume `Dataset` facts directly. Hydrated frames
store chain identity once, not in every block row, and derive their extent from their actual rows.

#### Experiment manifest

Each `experiments/{feature_ablation,c_study,hpo,k_study,held_out}/<UUID>/manifest.json` is a
nonempty ordered flat mapping from a nonempty cell label to one canonical record UUIDv4. The
directory path identifies the experiment, and its kind defines whether each value names a Study,
artifact, or evaluation. Manifests group canonical references only; they do not duplicate metrics,
results, or scientific definitions. The completed experiment directory contains only
`manifest.json`.

`experiments/feature_ablation.py prepare STORAGE_ROOT` authors the frozen 102-cell roster directly
as sealed Servatus Tasks. Each Task contains one strict KAIROS execution envelope with its cell,
typed request, and candidate index. The Campaign is the sole pre-publication roster at
`experiments/.servatus/<kind>/<experiment_id>/`; fixed experiments seal during prepare, while HPO
appends exact suffixes until selection seals it.

`experiments/launch.py launch STORAGE_ROOT KIND EXPERIMENT_ID` loads the selected Profile, inspects
canonical results through the KAIROS probe, plans exact retry keys, and submits through public
Campaign calls. Without `--tasks-per-job`, Servatus derives feasible capacity from the Profile.
Packing remains balanced: nine pending cells at capacity four become `3 + 3 + 3`.

Closure uses result-only Campaign inspection, assembles any required Study, validates every
cell-to-record association, and publishes only the canonical manifest. Campaign state remains as
private execution history. Downstream experiments read completed manifests only; there is no
private authoring fallback or duplicate request roster. `experiments/c_study.py` loads exactly the
nine canonical feature-ablation winners, reuses their reference-geometry `C=25` Studies,
and authors the other 108 architecture-chain-context Studies for
`C={1,2,3,4,5,10,15,20,25,50,100,200,400}`. The completed manifest contains all 117 cells. For
each chain, selection averages validation Cost over optimum equally across the three architectures
and chooses the smallest tested context whose mean is at most 105% of that chain's minimum mean;
the report also shows the unconstrained best context and threshold. `C=1` is the minimum-history
baseline and `C=2` is the first context with a temporal sequence; the roster is fixed rather than
adaptively refined after inspection. `experiments/hpo.py` consumes those selections and authors the
exact nine architecture-chain Studies with their ordered nine-Method L9 rosters. Each roster
derives its capacity-zero model and nonsearched fit settings from the selected context Study, then
varies capacity, dropout, learning rate, and weight decay. Transformer and Transformer-LSTM share
one attention-capacity table; the hybrid adds its fixed recurrent tail. The final selector chooses
the earliest minimum validation objective.

`experiments/k_study.py` derives the selected LSTM HPO result for each chain and authors 27 fresh
selected-Study Train requests for `K={2,3,4,5,10,25,50,100,200}`. It publishes the K-study
manifest only after every artifact exists. `experiments/held_out.py` authors the corresponding
held-out Evaluate requests. It derives complete-outcome separation and corpus-tail support from the
largest horizon in the loaded K-study roster, opening each distinct Dataset once and retaining only
its last block, so all horizons share the same first testing origin.
The explicit `K=2…5` rolling policy remains fixed: the `K=2…4` ranges extend their last origin by
three, two, or one blocks so the fixed-deadline comparison has every reachable decision origin. Its
report commands print, but do not persist, the ordinary and rolling reductions. Closure publishes
the exact 27 evaluation references and retains only private Campaign history.

Research figures remain outside `src/kairos` and outside the experiment command flow. The five
self-contained scripts load completed manifests and canonical Studies, Artifacts, or Evaluations
through their owning KAIROS loaders, derive presentation-only values in memory, and write vector
PDFs under `outputs/figures/`:

```text
uv run python experiments/figure_feature_ablation.py STORAGE_ROOT EXPERIMENT_ID
uv run python experiments/figure_context_study.py STORAGE_ROOT EXPERIMENT_ID
uv run python experiments/figure_hpo.py STORAGE_ROOT EXPERIMENT_ID
uv run python experiments/figure_k_study.py STORAGE_ROOT EXPERIMENT_ID
uv run python experiments/figure_held_out.py STORAGE_ROOT EXPERIMENT_ID
```

`figure_style.py` owns their shared typography, architecture colors, dimensions, and deterministic
PDF metadata. The K-study script owns the predictive, full-range economic, and $K\leq25$ economic
detail validation plots from canonical Artifact observations. The held-out script owns both
horizon economics and rolling-minus-one-shot deltas. The scripts never persist derived metrics or
parse experiment work state. A manuscript may copy a selected final PDF and owns only its caption,
label, placement, and discussion.

#### Study object

`studies/<study_id>/study.json` is a strict `Study`:

```text
request: TuneRequest
trials: nonempty ordered tuple[RetainedResult, ...]
```

Each `RetainedResult` has exact ordered fields:

| Field | Type/rule |
| --- | --- |
| `objective` | finite float validation base-fee optimality gap |
| `selected_epoch` | integer `≥1` |
| `completed_epochs` | integer `≥selected_epoch` and `≤` the corresponding request Method's `fit.max_epochs` |

`trials` has exactly the same length and order as `request.methods`.

#### Native Lightning artifact

`artifacts/<artifact_id>/artifact.ckpt` is the native Lightning weights-only selected checkpoint.
Its `ArtifactAssociation` contains:

| Ordered field | Type/rule |
| --- | --- |
| `request` | exact `TrainRequest`; embedded artifact UUID must match path |
| `feature_state` | nonempty Float64 means matching the ordered feature count; nonempty positive standard deviations |
| `target_state` | Float64 finite mean and positive standard deviation |
| `method` | exact selected Method |

Fitting uses a request-bound Servatus workspace. After selection, the checkpoint runs once over the
exact validation window. KAIROS assembles `artifact.ckpt`, `validation.parquet`, and the compact
`RetainedResult` in `result.json`; Servatus publishes the complete directory without overwrite.
Failures preserve resumable work.

Direct loader:

```python
load_artifact(
    storage_root: Path,
    artifact_id: UUID,
) -> tuple[ArtifactAssociation, torch.nn.Module]
```

#### Evaluation object

`evaluation.json` is exactly the `EvaluateRequest`. `observations.parquet` is the canonical schema
below. Reductions are transient views over this directory. Failed evaluation publication is
disposable and recomputed; Artifact and Study work remain resumable.

### CLI

Three public command leaves:

```text
kairos submit [--profile NAME] [--retry] REQUEST.json ...
kairos study run [--profile NAME] [--retry]
                 TUNE_REQUEST.json METHOD_INDEX
kairos study finalize STUDY_ID
```

- `submit` accepts one or more WorkflowRequest files, opens one durable campaign per request, and
  prints each accepted Servatus receipt.
- `study run` validates one strict TuneRequest and a zero-based Method index, then opens the
  candidate's durable campaign and prints its accepted receipt.
- `study finalize` accepts standard UUID syntax, reads absolute `STORAGE_ROOT`, and publishes existing indexed results. The result files' strict TuneRequest must carry the same Study ID, and direct TuneRequest construction mints publishable Study IDs as UUIDv4.

One help-hidden generated-job leaf:

```text
kairos remote worker
```

Generated Slurm scripts call these leaves with strict JSON on standard input.

### Remote submission

`kairos.workers` owns the thin application boundary. `ExecutionTask` holds one strict Tune, Train,
or Evaluate request, an optional experiment cell, and the Tune Method index. Its `task()` method
projects that validated envelope to the unchanged stable scientific key, hidden `remote worker`
argv, and canonical JSON plus a trailing line feed. The worker validates those raw bytes once and
calls the direct KAIROS owner. Result inspection requires the exact Task key, argv, and bytes bound
to that typed envelope, then checks its scientific association with canonical KAIROS output.

The public CLI and experiment launcher load `Path.cwd() / "SERVATUS.toml"` once per command through
Servatus. The file declares complete named Profiles and `default_profile = "KAIROS"`; an explicit
`--profile NAME` overrides that label. There is no config search, environment fallback, inherited
profile, or paired-file compatibility path. The committed KAIROS Profile requests one GPU, 24 CPUs,
65536 MiB, and three days per process. Experiment launch optionally caps tasks per allocation with
`--tasks-per-job`; without a cap, Servatus derives feasible capacity from the selected Profile.
Direct request commands create and seal one Task Campaign.

Servatus owns campaign identity, packing, target ceilings, native OpenSSH/Slurm/Apptainer command
construction, scheduler observation, result-aware planning, durable receipts, ambiguity refusal,
and explicit retry. KAIROS owns typed execution bytes, its canonical result probe, committed Profile
values, and the immutable image. Each image path must remain unchanged while its jobs are queued.
The image exports `STORAGE_ROOT` from its Servatus work root and dispatches `kairos remote worker`.

`STORAGE_ROOT` is the neutral implicit environment input to current CLI, remote Python, and mobile
export paths.

### Mobile deployment

The isolated `tools/mobile-export` project pins Torch 2.11 and ExecuTorch 1.2 without changing KAIROS's Torch 2.7.1 environment. Its strict `MOBILE.yaml` roster contains exactly `ethereum`, `polygon`, and `avalanche`, each with integer horizons `2…5` mapped to artifact UUIDv4 values.

Every cell must match artifact identity, chain, horizon, shared feature contract, native output
semantics, eager-to-XNNPACK host parity, selected action, and decoded-fee tolerance. At least one
delegate across the exported program's execution plans must have exact ID `XnnpackBackend`. The
exporter opens each distinct Dataset once, retains only its chain ID, and publishes all twelve models
plus one manifest through one Servatus transaction:

```text
app/assets/models/
  manifest.json
  ethereum-k2.pte ... ethereum-k5.pte
  polygon-k2.pte  ... polygon-k5.pte
  avalanche-k2.pte ... avalanche-k5.pte
```

The manifest owns shared context and feature state plus each model's artifact UUID and target state. The app trusts this build-time bundle through typed direct lookups and twelve static `.pte` requires. It has no download, alternate runtime, or remote inference fallback.

Expo SDK 55, React Native 0.83, and React Native ExecuTorch 0.9 require a custom native build; Expo Go is unsupported. The app reads public EVM RPC for chains `1`, `137`, and `43114`, prepares one fresh exact closed-head context per Run, runs the selected `(chain,K)` model, stores unbounded local `kairos.runs` history, and derives analytics from the selected `(chain,K)` subset. Analytics resolves eligible pending outcomes only when the user presses **Refresh outcomes**: one current-head read establishes eligibility, then exact outcome blocks are read in parallel. The refresh owns its captured chain, so later network or horizon changes do not discard valid outcomes. Failed and future outcomes remain persisted and retryable on the next refresh. Viem owns HTTP batching, the ten-second timeout, and zero retries; the raw adapter requires every block to contain a positive base fee. App owns one immediate global `(chain,K)` selection for both screens. Each Run advances and captures one inference generation; every real selection change advances it again and resets presentation. Every completed valid run still enters durable history, while only the current generation may publish loading, success, or error state. One concrete run-history owner serializes initial load and complete read-transform-save mutations through one rejection-safe FIFO. It requires a successful load, saves before publication, retains committed runs after failed saves, and reports load and save failures through one storage error. One mounted inference runtime owns one model catalog, one model runtime, and one immutable RPC session per chain. Chain changes alter only operation arguments. Each React effect setup creates a fresh runtime, and its matching cleanup disposes that instance. The model runtime's local queue serializes native load, forward, copied-output completion, model replacement, and disposal. RPC, feature, native, prediction, and numeric errors propagate from their owners; inference and outcome-refresh presentation uses compact Viem `shortMessage` text and otherwise preserves direct error messages. Run-history persistence keeps its explicit workflow failure message. When the selected feature route contains priority fees, one context-wide `eth_feeHistory(...,[50,90])` call must begin at the first context block and return exactly `C` rows containing nonnegative P50 and P90 values. Avalanche uses this direct RPC path because the model context is at most 400 blocks; BigQuery is historical Corpus acquisition only.

The repository contains the final twelve-cell `MOBILE.yaml` roster, generated manifest, and twelve
`.pte` assets. Every asset passed the exporter's eager-versus-ExecuTorch parity checks on zero and
deterministic nonzero inputs. A custom native iOS Simulator Release build exercised real public-RPC
inference for Ethereum `K=5` and Polygon `K=5`, including durable run history and resolved outcomes.
This is not evidence for all twelve native cells or physical-device performance and memory. The
[README](../README.md#mobile-demo) owns build commands; the
[on-device decision](research/on-device-inference.md) owns the exact acceptance boundary.

### Execution runtime

The internal installed-executable profile fits LSTMs in `32-true`, Transformers in BF16 mixed
precision, and Transformer-LSTMs in BF16 with their recurrent layer in float32. It also fixes fit
and selected-validation batch size 64 and held-out evaluation batch size 512; four persistent
pinned-memory loader workers with prefetch factor 2; `high` float32 matrix-multiplication precision,
which owns CUDA matmul TF32; and
a separate cuDNN TF32 flag for float32 operations. Each fit calls `seed_everything(seed)` once.
Lightning owns deterministic
setup through `Trainer(deterministic=True)` and norm clipping through the configured
`gradient_clip_norm`; shuffled loading uses the seeded global Torch RNG. These are code facts, not
request, schema, roster, or public configuration surfaces.

### Evaluation API

Validation reductions are direct views over completed fit evidence:

```python
reduce_study(storage_root: Path, study_id: UUID) -> polars.DataFrame
```

Public exports from `kairos.evaluation`:

```python
evaluate(
    request: EvaluateRequest,
    storage_root: Path,
) -> None

reduce_evaluation(
    storage_root: Path,
    evaluation_id: UUID,
) -> polars.DataFrame

reduce_baselines(
    storage_root: Path,
    evaluation_id: UUID,
) -> polars.DataFrame

reduce_rolling(
    storage_root: Path,
    roster: Mapping[str, Mapping[int, UUID]],
) -> polars.DataFrame
```

#### Canonical observations

Destinations are `studies/<study_id>/trials/<method_index>/validation.parquet`,
`artifacts/<artifact_id>/validation.parquet`, and
`evaluations/<evaluation_id>/observations.parquet`. Each is canonical, ordered, nonnull, and has one
row per inclusive origin in ascending block order.

| # | Field | Type | Unit/meaning |
| ---: | --- | --- | --- |
| 1 | `origin_block` | Int64 | closed parent `h_i` |
| 2 | `predicted_action_k` | Int64 | decoded `hat{k}_i` |
| 3 | `predicted_minimum_log_base_fee` | Float64 | dimensionless predicted log-minimum coordinate `hat{ell}_i` relative to `u` |
| 4 | `minimum_action_k` | Int64 | canonical `k_i*` |
| 5 | `immediate_base_fee_per_gas` | Int64 | `B_i(0)`, wei/gas |
| 6 | `immediate_effective_priority_fee_per_gas_p50` | Int64 | `P_i(0)`, wei/gas |
| 7 | `selected_base_fee_per_gas` | Int64 | `B_i(hat{k}_i)`, wei/gas |
| 8 | `selected_effective_priority_fee_per_gas_p50` | Int64 | `P_i(hat{k}_i)`, wei/gas |
| 9 | `deadline_base_fee_per_gas` | Int64 | `B_i(K-1)`, wei/gas |
| 10 | `deadline_effective_priority_fee_per_gas_p50` | Int64 | `P_i(K-1)`, wei/gas |
| 11 | `minimum_base_fee_per_gas` | Int64 | `m_i`, wei/gas |

The file contains predictions and the observed truth needed for local reduction. Losses, timestamps, waits, horizons, standardized predictions, and derived metrics remain absent.

#### Transient reduction

Destination: none. The shared reducer validates the canonical observation schema and returns one
transient, noncanonical, nonnull row. Validation and testing call the same reducer.

| # | Field | Type | Unit/direction |
| ---: | --- | --- | --- |
| 1 | `accuracy` | Float64 | unitless; higher is better |
| 2 | `f1_macro` | Float64 | unitless; higher is better |
| 3 | `log_fee_mae` | Float64 | dimensionless natural-log error relative to `u`; lower is better |
| 4 | `log_fee_mse` | Float64 | squared dimensionless natural-log error; lower is better |
| 5 | `base_fee_savings` | Float64 | mean per-origin fraction versus immediate; higher is better |
| 6 | `mean_p50_fee_inclusive_savings` | Float64 | tail-sensitive mean per-origin representative-cost fraction; higher is better |
| 7 | `trimmed_mean_p50_fee_inclusive_savings` | Float64 | mean after removing the lowest and highest 2.5% of per-origin ratios; higher is better |
| 8 | `p25_p50_fee_inclusive_savings` | Float64 | lower-quartile representative-cost fraction; higher is better |
| 9 | `median_p50_fee_inclusive_savings` | Float64 | typical-origin representative-cost fraction; higher is better |
| 10 | `p75_p50_fee_inclusive_savings` | Float64 | upper-quartile representative-cost fraction; higher is better |
| 11 | `base_fee_optimality_gap` | Float64 | mean per-origin fraction above optimum; lower is better |
| 12 | `mean_immediate_base_fee_gwei` | Float64 | mean immediate base fee, Gwei/gas |
| 13 | `mean_selected_base_fee_gwei` | Float64 | mean selected base fee, Gwei/gas |
| 14 | `mean_minimum_base_fee_gwei` | Float64 | mean horizon-minimum base fee, Gwei/gas |
| 15 | `mean_selected_minus_minimum_base_fee_gwei` | Float64 | mean selected excess, Gwei/gas |

`accuracy` compares `predicted_action_k` (`hat{k}_i`) with `minimum_action_k` (`k_i*`). `f1_macro`
averages over the union of classes appearing in truth or predictions.
Regression compares `predicted_minimum_log_base_fee` (`hat{ell}_i`) with
`ln(minimum_base_fee_per_gas / u)` (`ell_i`). Economic fields are fractions, not percentages or
ratios of sums. All P50 summaries are retrospective and do not claim inclusion.

`reduce_baselines()` returns two rows, ordered `immediate` then `deadline`, with `policy`,
`base_fee_savings`, all five explicit P50 fee-inclusive summaries, and
`base_fee_optimality_gap`.
`experiments/held_out.py baselines` prefixes each row with its cell.

#### Rolling comparison result

Destination: none. The rolling reduction returns one row per supplied architecture-chain cell.
The held-out stage supplies the three selected chain-LSTM cells. Status: derived, transient, noncanonical,
nonnull.

| # | Field | Type | Unit/direction |
| ---: | --- | --- | --- |
| 1 | `cell` | String | operator-authored architecture-chain label |
| 2 | `one_shot_base_fee_savings` | Float64 | mean per-origin fraction versus immediate; higher is better |
| 3 | `rolling_base_fee_savings` | Float64 | mean per-origin fraction versus immediate; higher is better |
| 4 | `one_shot_mean_p50_fee_inclusive_savings` | Float64 | tail-sensitive mean representative-cost fraction; higher is better |
| 5 | `rolling_mean_p50_fee_inclusive_savings` | Float64 | tail-sensitive mean representative-cost fraction; higher is better |
| 6 | `one_shot_trimmed_mean_p50_fee_inclusive_savings` | Float64 | 2.5%-per-tail trimmed representative-cost mean; higher is better |
| 7 | `rolling_trimmed_mean_p50_fee_inclusive_savings` | Float64 | 2.5%-per-tail trimmed representative-cost mean; higher is better |
| 8 | `one_shot_p25_p50_fee_inclusive_savings` | Float64 | lower-quartile representative-cost fraction; higher is better |
| 9 | `rolling_p25_p50_fee_inclusive_savings` | Float64 | lower-quartile representative-cost fraction; higher is better |
| 10 | `one_shot_median_p50_fee_inclusive_savings` | Float64 | typical-origin representative-cost fraction; higher is better |
| 11 | `rolling_median_p50_fee_inclusive_savings` | Float64 | typical-origin representative-cost fraction; higher is better |
| 12 | `one_shot_p75_p50_fee_inclusive_savings` | Float64 | upper-quartile representative-cost fraction; higher is better |
| 13 | `rolling_p75_p50_fee_inclusive_savings` | Float64 | upper-quartile representative-cost fraction; higher is better |
| 14 | `one_shot_base_fee_optimality_gap` | Float64 | mean per-origin fraction above the five-block optimum; lower is better |
| 15 | `rolling_base_fee_optimality_gap` | Float64 | mean per-origin fraction above the five-block optimum; lower is better |

`reduce_rolling_traces()` returns long-form `cell`, `trace`, `value`, `count`, and `proportion`
rows. `k2_head_advance_blocks` has support `0..3`; `maximum_same_head_cascade_length` has
support `1..4`. `experiments/held_out.py rolling-traces` prints this transient table.

## Limitations and sources

### Claim boundary and limitations

Evaluation describes target block base fee per gas over every eligible origin in one declared historical window. Its claims are bounded as follows:

- The target and `base_fee_savings` omit priority fee and transaction gas use; the separate P50 summaries add an included-transaction proxy, not an actual transaction quote.
- Target-block intent does not guarantee inclusion at that block.
- The auxiliary head is not calibrated uncertainty or a quote.
- One seed or one time range does not establish seed, regime, or future robustness.
- Different `K` values are different classification problems; testing cannot choose a best `K`.
- Native assets, fee levels, protocol rules, and ranges differ by chain; totals are never pooled across chains.
- Exhaustive origins remove sampling within the declared range, not temporal dependence or selection bias outside it.

### Sources

- [EIP-1559 specification](https://eips.ethereum.org/EIPS/eip-1559)
- [Frozen predecessor experiment code and datasets](https://github.com/UniBO-PRISMLab/ICDCS-Model-Training/tree/bcf80b92877941e3b05a7dc5138560ffe41df27e)
- [Hochreiter and Schmidhuber, “Long Short-Term Memory”](https://direct.mit.edu/neco/article/9/8/1735/6109/Long-Short-Term-Memory)
- [Vaswani et al., “Attention Is All You Need”](https://arxiv.org/abs/1706.03762)
- [Caruana, “Multitask Learning”](https://doi.org/10.1023/A:1007379606734)
- [NumPy `argmin`](https://numpy.org/doc/stable/reference/generated/numpy.argmin.html)
- [PyTorch cross entropy](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [PyTorch Smooth L1](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.smooth_l1_loss.html)
