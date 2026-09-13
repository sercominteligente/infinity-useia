# HAKHAM Model Router

HAKHAM Infinity owns identity, memory, permissions, orchestration and policy. Model providers are replaceable propulsion engines.

## Providers

Initial provider contract:

- `ollama`: local/offline models
- `openai`: direct OpenAI-compatible provider
- `abacus`: Abacus.AI RouteLLM gateway

No provider may silently become a fallback for another provider. Fallback and consensus policies must be explicit and auditable.

## Abacus RouteLLM

Self-serve RouteLLM base URL:

`https://routellm.abacus.ai/v1`

HAKHAM currently uses the OpenAI-compatible Chat Completions endpoint for the first RouteLLM integration:

`POST /chat/completions`

It can either target a specific RouteLLM model ID or use `route-llm` to let Abacus choose an underlying engine. The live catalog is available through:

`GET /models`

The catalog must be queried rather than hard-coded because available model IDs can change over time.

## Environment

Never commit a real RouteLLM key.

```env
HAKHAM_MODEL_PROVIDER=abacus
HAKHAM_MODEL=route-llm
ABACUS_ROUTELLM_API_KEY=YOUR_LOCAL_SECRET
ABACUS_ROUTELLM_BASE_URL=https://routellm.abacus.ai/v1
```

Leaving `HAKHAM_MODEL` empty while `HAKHAM_MODEL_PROVIDER=abacus` also defaults to `route-llm`.

## Security rule

External engines receive only the context required for the current task. The full HAKHAM memory database, quarantine, provenance ledger and credentials must not be sent wholesale to any model provider.

Conceptually:

```text
User / Task
    |
HAKHAM Core
    |
Context Selection + Permissions
    |
Model Router
    |-------------------|-------------------|
 Ollama/local       Abacus RouteLLM       Direct APIs
    |                   |                   |
 private/local       many engines        explicit vendor
```

## Planned evolution

1. text generation through Chat Completions
2. live model catalog in Control Center
3. model capability metadata and cost/latency observations
4. explicit routing policies by task type
5. optional multi-model council/consensus mode
6. multimodal and tool-capable RouteLLM paths
7. Responses API path for agentic/reasoning workloads where appropriate

HAKHAM remains provider-independent throughout these stages.
