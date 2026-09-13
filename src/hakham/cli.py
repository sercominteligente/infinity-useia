from __future__ import annotations

from dataclasses import dataclass

from .capabilities import ModelCapabilityRegistry, ModelSelector, TaskCapability
from .config import Settings, load_settings
from .core import HakhamCore
from .council import ModelCouncil
from .logging_config import configure_logging
from .memory import MemoryStore
from .models import ModelRouter, OllamaProvider, OmniRouteProvider, OpenAIProvider, RouteLLMProvider


@dataclass(frozen=True)
class Runtime:
    core: HakhamCore
    settings: Settings
    abacus: RouteLLMProvider | None = None
    omniroute: OmniRouteProvider | None = None


def build_runtime() -> Runtime:
    settings = load_settings()
    configure_logging(settings.log_level)
    router = ModelRouter()

    # OmniRoute is always available as a local sidecar candidate. It is cheap to
    # register because no network call happens until a request or health check.
    omniroute = OmniRouteProvider(
        model=settings.omniroute_model,
        base_url=settings.omniroute_base_url,
        api_key=settings.omniroute_api_key,
        compression=settings.omniroute_compression,
    )
    router.register("omniroute", omniroute)

    # Keep Abacus registered as a premium sidecar whenever its key exists so the
    # UI can jump to Astra/Council explicitly without making it the default fuel.
    abacus: RouteLLMProvider | None = None
    if settings.abacus_routellm_api_key:
        abacus = RouteLLMProvider(
            api_key=settings.abacus_routellm_api_key,
            model="route-llm" if settings.model_provider != "abacus" else settings.model,
            base_url=settings.abacus_routellm_base_url,
        )
        router.register("abacus", abacus)

    if settings.model_provider == "ollama":
        router.register(
            "ollama",
            OllamaProvider(model=settings.model, base_url=settings.ollama_base_url),
        )
    elif settings.model_provider == "openai":
        router.register(
            "openai",
            OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.model,
                base_url=settings.openai_base_url,
            ),
        )
    elif settings.model_provider == "abacus":
        if abacus is None:
            raise ValueError("ABACUS_ROUTELLM_API_KEY is required for the Abacus provider")
        abacus.model = settings.model
    elif settings.model_provider == "omniroute":
        omniroute.model = settings.model or settings.omniroute_model

    core = HakhamCore(
        router=router,
        memory=MemoryStore(settings.memory_db),
        provider=settings.model_provider,
        model=settings.model,
    )
    return Runtime(core=core, settings=settings, abacus=abacus, omniroute=omniroute)


def build_core() -> HakhamCore:
    return build_runtime().core


def _require_abacus(runtime: Runtime) -> RouteLLMProvider:
    if runtime.abacus is None:
        raise ValueError("this command requires ABACUS_ROUTELLM_API_KEY")
    return runtime.abacus


def _print_models(provider: RouteLLMProvider) -> None:
    models = provider.list_models()
    ids = sorted(
        item["id"] for item in models if isinstance(item.get("id"), str)
    )
    print(f"RouteLLM models: {len(ids)}")
    for model_id in ids[:50]:
        print(f"- {model_id}")
    if len(ids) > 50:
        print(f"... and {len(ids) - 50} more")


def _recommend(provider: RouteLLMProvider, requested: str) -> None:
    capability = TaskCapability(requested.strip().casefold())
    registry = ModelCapabilityRegistry()
    registry.sync_catalog(provider.list_models())
    selector = ModelSelector(registry)
    chosen = selector.choose(capability)
    alternatives = registry.recommend(capability, limit=5, include_route_llm=False)
    print(f"Recommended engine for {capability.value}: {chosen}")
    if alternatives:
        print("Candidates:")
        for item in alternatives:
            print(f"- {item.model_id}")


def _run_council(runtime: Runtime, question: str) -> None:
    provider = _require_abacus(runtime)
    models = list(runtime.settings.abacus_council_models)
    if len(models) < 2:
        raise ValueError(
            "configure at least two exact model IDs in HAKHAM_COUNCIL_MODELS before using /council"
        )
    council = ModelCouncil(provider)
    result = council.deliberate(
        question,
        models=models,
        synthesis_model=runtime.settings.abacus_synthesis_model,
    )
    for voice in result.voices:
        print(f"\n[{voice.model}]\n{voice.response}")
    print(f"\n[HAKHAM synthesis via {result.synthesis_model}]\n{result.synthesis}")


def main() -> None:
    runtime = build_runtime()
    print("HAKHAM Infinity v0.20 | OmniRoute economy core | /help for commands")
    while True:
        message = input("You> ").strip()
        if not message:
            continue
        if message.lower() in {"/exit", "/quit"}:
            break
        try:
            if message == "/help":
                print("/health | /models | /recommend <capability> | /council <question> | /exit")
                print("capabilities: general reasoning coding research speed economy vision audio")
                continue
            if message == "/health":
                if runtime.core.provider == "omniroute" and runtime.omniroute is not None:
                    print(runtime.omniroute.health())
                else:
                    print(_require_abacus(runtime).health())
                continue
            if message == "/models":
                if runtime.core.provider == "omniroute" and runtime.omniroute is not None:
                    models = runtime.omniroute.list_models()
                    print(f"OmniRoute models: {len(models)}")
                    for item in models[:50]:
                        if isinstance(item.get("id"), str):
                            print(f"- {item['id']}")
                else:
                    _print_models(_require_abacus(runtime))
                continue
            if message.startswith("/recommend "):
                _recommend(_require_abacus(runtime), message.removeprefix("/recommend "))
                continue
            if message.startswith("/council "):
                _run_council(runtime, message.removeprefix("/council ").strip())
                continue
            print(f"Hakham> {runtime.core.ask(message)}")
        except Exception as exc:
            print(f"Hakham error> {exc}")


if __name__ == "__main__":
    main()
