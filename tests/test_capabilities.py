from hakham.capabilities import ModelCapabilityRegistry, ModelSelector, TaskCapability


def test_registry_syncs_live_catalog_shape():
    registry = ModelCapabilityRegistry()
    registry.sync_catalog(
        [
            {"id": "route-llm", "owned_by": "abacus"},
            {"id": "example-coder", "owned_by": "provider"},
            {"id": "example-fast-mini", "owned_by": "provider"},
        ]
    )

    assert registry.get("route-llm") is not None
    assert TaskCapability.CODING in registry.get("example-coder").capabilities
    assert TaskCapability.SPEED in registry.get("example-fast-mini").capabilities
    assert TaskCapability.ECONOMY in registry.get("example-fast-mini").capabilities


def test_selector_prefers_explicit_matching_engine_before_auto_route():
    registry = ModelCapabilityRegistry()
    registry.sync_catalog([{"id": "route-llm"}, {"id": "my-coder-model"}])
    selector = ModelSelector(registry)

    assert selector.choose(TaskCapability.CODING) == "my-coder-model"


def test_selector_falls_back_to_route_llm_when_no_match():
    registry = ModelCapabilityRegistry()
    registry.sync_catalog([{"id": "generic-model"}])
    selector = ModelSelector(registry)

    assert selector.choose(TaskCapability.AUDIO) == "route-llm"
