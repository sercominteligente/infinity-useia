from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskCapability(str, Enum):
    GENERAL = "general"
    REASONING = "reasoning"
    CODING = "coding"
    RESEARCH = "research"
    SPEED = "speed"
    ECONOMY = "economy"
    VISION = "vision"
    AUDIO = "audio"


@dataclass(frozen=True)
class ModelCapability:
    model_id: str
    capabilities: frozenset[TaskCapability]
    source: str = "inferred"
    raw: dict[str, object] | None = None


class ModelCapabilityRegistry:
    """Local knowledge about propulsion-model strengths.

    The registry is advisory only. It never changes HAKHAM identity, memory or
    policy, and it does not make network requests by itself.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelCapability] = {}

    def register(self, model: ModelCapability) -> None:
        self._models[model.model_id] = model

    @staticmethod
    def infer_capabilities(model_id: str) -> frozenset[TaskCapability]:
        name = model_id.casefold()
        caps: set[TaskCapability] = {TaskCapability.GENERAL}

        if model_id == "route-llm":
            caps.update(
                {
                    TaskCapability.REASONING,
                    TaskCapability.CODING,
                    TaskCapability.RESEARCH,
                    TaskCapability.SPEED,
                    TaskCapability.ECONOMY,
                }
            )

        if any(token in name for token in ("codex", "coder", "code-fast", "code")):
            caps.add(TaskCapability.CODING)
        if any(token in name for token in ("reason", "deepseek-r1", "o3", "o4", "xhigh", "opus")):
            caps.add(TaskCapability.REASONING)
        if any(token in name for token in ("pro", "opus", "sonnet", "gpt-5", "grok-4", "deepseek-v4")):
            caps.add(TaskCapability.RESEARCH)
        if any(token in name for token in ("mini", "nano", "flash", "haiku", "fast", "8b")):
            caps.add(TaskCapability.SPEED)
            caps.add(TaskCapability.ECONOMY)
        if any(token in name for token in ("audio", "tts")):
            caps.add(TaskCapability.AUDIO)

        # Vision is intentionally conservative. Only obvious multimodal family
        # identifiers are inferred here; live catalog metadata can override it.
        if any(token in name for token in ("gpt-4o", "gemini-3", "gemini-2.5")):
            caps.add(TaskCapability.VISION)

        return frozenset(caps)

    def sync_catalog(self, items: list[dict[str, object]], *, source: str = "abacus-live") -> None:
        for item in items:
            model_id = item.get("id")
            if not isinstance(model_id, str) or not model_id.strip():
                continue
            self.register(
                ModelCapability(
                    model_id=model_id,
                    capabilities=self.infer_capabilities(model_id),
                    source=source,
                    raw=dict(item),
                )
            )

    def get(self, model_id: str) -> ModelCapability | None:
        return self._models.get(model_id)

    def all(self) -> list[ModelCapability]:
        return sorted(self._models.values(), key=lambda item: item.model_id)

    def recommend(
        self,
        capability: TaskCapability | str,
        *,
        limit: int = 3,
        include_route_llm: bool = True,
    ) -> list[ModelCapability]:
        wanted = capability if isinstance(capability, TaskCapability) else TaskCapability(capability)
        matches = [
            model
            for model in self._models.values()
            if wanted in model.capabilities and (include_route_llm or model.model_id != "route-llm")
        ]

        def rank(model: ModelCapability) -> tuple[int, int, str]:
            exact_bonus = 1 if wanted != TaskCapability.GENERAL else 0
            auto_penalty = -1 if model.model_id == "route-llm" else 0
            breadth = len(model.capabilities)
            return (exact_bonus + auto_penalty, breadth, model.model_id)

        matches.sort(key=rank, reverse=True)
        return matches[:limit]


class ModelSelector:
    """Choose a propulsion model while preserving an automatic fallback."""

    def __init__(self, registry: ModelCapabilityRegistry, fallback_model: str = "route-llm") -> None:
        self.registry = registry
        self.fallback_model = fallback_model

    def choose(self, capability: TaskCapability | str) -> str:
        recommended = self.registry.recommend(capability, limit=1, include_route_llm=False)
        return recommended[0].model_id if recommended else self.fallback_model
