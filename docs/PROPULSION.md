# HAKHAM Infinity Propulsion Layer

HAKHAM Infinity owns identity, memory, policy, orchestration and tool permissions. External LLM providers are replaceable propulsion engines.

## Architecture

```text
HAKHAM Core
    |
SER Model Router
    |
    +-- Ollama/local
    +-- Abacus RouteLLM
    +-- direct providers
```

No provider receives the whole memory database by default. HAKHAM retrieves and sends only the context needed for the current task.

## Abacus RouteLLM

Self-service base URL:

`https://routellm.abacus.ai/v1`

Current integration uses the OpenAI-compatible Chat Completions endpoint for text generation and `GET /v1/models` for the live model catalog.

`route-llm` means Abacus may choose the underlying engine. HAKHAM can also call an exact model ID returned by the live catalog.

## Local configuration

Copy `.env.example` to `.env` and configure locally:

```env
HAKHAM_MODEL_PROVIDER=abacus
HAKHAM_MODEL=route-llm
ABACUS_ROUTELLM_API_KEY=YOUR_LOCAL_KEY
ABACUS_ROUTELLM_BASE_URL=https://routellm.abacus.ai/v1
```

Never commit a real API key.

## First ignition checklist

1. Start the CLI.
2. Run `/health` to validate authentication and catalog access.
3. Run `/models` to inspect the current live model IDs.
4. Ask a normal HAKHAM question with `HAKHAM_MODEL=route-llm`.
5. Run `/recommend coding`, `/recommend reasoning` or another capability to inspect HAKHAM's advisory registry.
6. Only after checking exact live IDs, optionally configure Council Mode.

## Capability Registry

`ModelCapabilityRegistry` builds a local advisory view of model strengths from the live catalog. The first implementation uses conservative name-based inference for capabilities such as:

- general
- reasoning
- coding
- research
- speed
- economy
- vision
- audio

This registry is not a truth oracle. Provider capabilities change, so the live catalog remains the source of model IDs and future catalog metadata should progressively replace heuristics.

## Council Mode

Council Mode is opt-in and bounded because it uses multiple model calls.

Configure at least two exact live model IDs:

```env
HAKHAM_COUNCIL_MODELS=model-a,model-b,model-c
HAKHAM_COUNCIL_SYNTHESIS_MODEL=route-llm
```

Then:

```text
/council Should we use architecture A or B?
```

Each member answers independently. HAKHAM then asks a synthesis model to compare agreements, disagreements, unsupported claims, risks and the recommended next action.

Council outputs are advisory only. They do not bypass HAKHAM permissions and cannot directly execute tools, production deployments, payments, trading or destructive actions.

## Cost discipline

Normal chat can use one routed call. Council Mode can use N member calls plus one synthesis call, so it must remain explicit rather than automatic.

## Independence rule

If Abacus is unavailable, HAKHAM must remain architecturally capable of switching to local or direct providers without losing identity or memory.
