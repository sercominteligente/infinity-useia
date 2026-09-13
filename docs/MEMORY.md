# HAKHAM Memory v0.10

HAKHAM Memory is split into distinct cognitive layers and now includes a consolidation stage that can detect repeated patterns in episodic conversation without silently turning them into durable truth.

## Cognitive layers

### Episodic memory

`EpisodicStore` keeps ordered conversational events such as user, assistant, tool and system turns. It is session-aware and optimized for short temporal continuity.

Raw conversational turns are no longer used as the primary durable semantic memory path.

### Semantic memory

`MemoryStore` keeps durable extracted knowledge: facts, projects, decisions, preferences, tasks and entities. It remains source-aware, conflict-aware, auditable and compatible with quarantine/promotion.

`recent()` means chronological recency. `important()` handles importance-ranked retrieval.

### Working memory

`WorkingMemory` is a small bounded volatile store for the current task. It is intentionally not persisted and can be cleared at task boundaries.

The Hakham Core builds context from:

`working task context -> relevant semantic memory -> recent episodic conversation`

## Memory consolidation

`MemoryConsolidator` scans recent user episodes and looks for repeated extractable semantic statements. A candidate is emitted only when it reaches the configured evidence threshold.

Each consolidation candidate records:

- semantic content
- memory kind
- boosted importance based on repetition
- source `episodic-consolidation`
- evidence count
- exact episode IDs that support the candidate

The consolidator never writes directly to semantic memory.

## Safety rule for learned patterns

Repeated conversation is a signal, not proof. `MemoryGuard` therefore routes every `episodic-consolidation` candidate to quarantine by default, even when no active semantic memory exists yet.

This prevents repetition, conversational loops or model echo from becoming durable truth automatically.

The safe flow is:

`episodic repetition -> consolidator -> candidate + evidence IDs -> memory guard -> quarantine -> review -> promotion -> semantic memory`

## Hybrid semantic retrieval

Semantic retrieval combines lexical scoring, vector similarity when an `EmbeddingProvider` is available, and memory importance. `HashEmbeddingProvider` remains the zero-dependency local fallback.

## Provenance, conflict and quarantine

Durable semantic memories continue through the protection pipeline:

`candidate -> extractor -> conflict resolver -> memory guard -> quarantine/review -> promotion -> active semantic memory -> provenance ledger`

Historical imports, open-web claims about mutable subjects and learned episodic patterns remain evidence rather than automatic truth.

## ChatGPT export pipeline

`export -> parser -> conversation chunks -> episodic staging -> extractor -> classifier -> deduplicator -> conflict resolver -> provenance -> memory guard -> quarantine -> review -> promotion -> semantic memory`

Imported raw conversations must not be blindly injected into active prompts.

## Design rule

A conversation event answers: "what happened?"

A consolidation candidate answers: "what pattern might be worth remembering?"

A semantic memory answers: "what should Hakham know?"

Working memory answers: "what matters for the task right now?"

Keeping those questions separate is a core architectural rule of HAKHAM Infinity.
