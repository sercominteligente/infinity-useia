from __future__ import annotations

import argparse

from .config import load_settings
from .logging_config import configure_logging
from .models import RouteLLMProvider


def build_provider() -> RouteLLMProvider:
    settings = load_settings()
    configure_logging(settings.log_level)
    if settings.model_provider != "abacus":
        raise ValueError("first ignition requires HAKHAM_MODEL_PROVIDER=abacus")
    return RouteLLMProvider(
        api_key=settings.abacus_routellm_api_key,
        model=settings.model,
        base_url=settings.abacus_routellm_base_url,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="HAKHAM Infinity first Abacus ignition")
    parser.add_argument(
        "--live",
        action="store_true",
        help="perform one real text-generation call after health/catalog validation",
    )
    args = parser.parse_args()

    provider = build_provider()
    health = provider.health()
    print(
        "ABACUS HEALTH OK | "
        f"models={health['model_count']} | configured_model={health['configured_model']}"
    )

    if not args.live:
        print("Dry ignition complete. No text-generation call was made.")
        print("Run `hakham-ignite --live` when you are ready for the first real engine call.")
        return

    answer = provider.generate(
        "You are an external propulsion engine being tested by HAKHAM Infinity. "
        "Reply in one short sentence confirming that the engine is online."
    )
    print(f"LIVE ENGINE RESPONSE: {answer}")


if __name__ == "__main__":
    main()
