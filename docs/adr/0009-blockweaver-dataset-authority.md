# ADR 0009: Blockweaver Dataset Authority

## Status

Accepted. Supersedes only ADR 0006's Corpus clause.

## Context

KAIROS needs strict finalized block facts, chain identity, and an exact resolved range, but it does
not acquire or publish blockchain history. Keeping a second `corpus.json` beside externally
produced rows duplicated dataset authority and made KAIROS validate a weaker local manifest.

## Decision

Blockweaver owns each immutable Corpus artifact at
`datasets/<corpus_id>/manifest.json` plus `blocks.parquet`. Its dataset UUID is the unchanged KAIROS
`corpus_id`. KAIROS's `open_corpus_dataset()` address adapter resolves it through
`blockweaver.open_dataset()`. KAIROS accepts Parquet only and requires its exact ordered
eight-column scientific projection.

Metadata-only callers use validated `Dataset` facts directly. A hydrated `BlockFrame` stores the
dataset chain ID once rather than in every row and derives its extent from its nonempty actual rows.
KAIROS owns `BlockFrame` and all downstream scientific interpretation; Blockweaver owns artifact
provenance, verification, digest, schema, range, and immutable publication.

Study, artifact, evaluation, and experiment addresses and associations remain unchanged. Servatus
treats their destinations as opaque and has no Blockweaver responsibility.

## Consequences

There is one dataset manifest and one artifact-validation boundary. KAIROS has no local corpus
metadata record, `CorpusRequest`, `corpus.json` reader, acquisition configuration, CSV path, or
legacy `corpora/` fallback. Existing scientific requests continue to identify the same Corpus UUIDs.
