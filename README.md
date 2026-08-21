# KAIROS: Learning When to Execute Blockchain Transactions

KAIROS learns from finalized block history to choose a low-base-fee block within a short future [horizon](docs/CONTEXT.md). It compares LSTM, Transformer, and Transformer-LSTM models.

Its scientific lineage is the temporal experiment in *SPICE: A Predictive Framework for Cost-Optimization in Multichain Environments*: a future minimum-block decision paired with an auxiliary fee prediction. KAIROS's current equations and claim limits are documented in the [manual](docs/KAIROS.md#scientific-contract). The [glossary](docs/CONTEXT.md) defines its domain terms.

## Hosts and responsibilities

The Python system supports two explicit operating locations:

- A workstation consumes prepared block history, creates requests, submits work, publishes tuning results, and computes transient evaluation reductions.
- A GPU server fits, tunes, and evaluates through Slurm jobs.

The [manual](docs/KAIROS.md#remote-submission) defines remote submission and host configuration.

## Install

Python 3.11 and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv sync
```

## Quick start

Place each completed Blockweaver dataset at
`STORAGE_ROOT/datasets/<UUID>/manifest.json` and `blocks.parquet`. KAIROS uses the dataset UUID as
its Corpus ID and reads the artifact through Blockweaver's strict public loader. Create workflow
requests from the [request reference](docs/KAIROS.md#requests-and-definitions).

Submit one or more training or evaluation requests:

```bash
kairos submit REQUEST.json
```

Submit one candidate configuration from a tuning request:

```bash
kairos study run TUNE_REQUEST.json METHOD_INDEX
```

Publish the collected tuning results:

```bash
STORAGE_ROOT=/absolute/storage kairos study finalize STUDY_ID
```

The [CLI reference](docs/KAIROS.md#cli) defines the exact command contracts.

## Mobile demo

The private Expo 55 app in `app` reads the selected EVM chain directly, prepares features in
TypeScript, runs a bundled ExecuTorch model on device, and keeps history and resolved outcomes in
local storage. Analytics resolves eligible pending outcomes only when the user presses **Refresh
outcomes**; failed or future outcomes remain persisted and retryable. The app has no KAIROS
inference server or fallback.

The app uses the checked-in strict three-chain by four-horizon `MOBILE.yaml` roster and generated
model bundle. Regenerate all assets atomically when that roster changes:

```bash
STORAGE_ROOT=/absolute/storage \
uv run --project tools/mobile-export --frozen \
python tools/mobile-export/export.py MOBILE.yaml app/assets/models
```

Then install dependencies, check the Expo project, and create the custom native development build:

```bash
cd app
npm ci
npx expo-doctor
npm run ios
```

ExecuTorch is a native module, so Expo Go is unsupported. With a compatible development build
already installed and native configuration unchanged, start Metro for JavaScript or asset
iteration with:

```bash
npm start
```

The repository contains `MOBILE.yaml`, one manifest, and twelve generated `.pte` assets. The
[acceptance record](docs/research/on-device-inference.md) separates exporter parity and the exercised
iOS Simulator path from native cells and physical-device behavior that have not been tested.

## Where do I look?

| Question | Owner |
| --- | --- |
| How does one decision work end to end? | [Worked decision](docs/KAIROS.md#one-decision-end-to-end) |
| Why are the inputs causal, and what do the equations mean? | [Scientific contract](docs/KAIROS.md#scientific-contract) |
| Which module owns each object and seam? | [Architecture](docs/KAIROS.md#architecture-and-deep-interfaces) |
| What are the exact requests, paths, commands, and schemas? | [Exact reference](docs/KAIROS.md#exact-reference) |
| What does a domain term mean? | [Glossary](docs/CONTEXT.md) |
| Which architectural decisions remain active? | [ADR index](docs/adr/README.md) |
