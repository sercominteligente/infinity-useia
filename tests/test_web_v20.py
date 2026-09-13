def test_omniroute_provider_allows_keyless_localhost() -> None:
    from hakham.models import OmniRouteProvider

    provider = OmniRouteProvider(model="auto", base_url="http://127.0.0.1:20128/v1")
    assert provider.configured is True
    assert provider.model == "auto"
    assert "Authorization" not in provider._headers
    assert provider._headers["Content-Type"] == "application/json"


def test_omniroute_provider_adds_optional_auth_and_compression() -> None:
    from hakham.models import OmniRouteProvider

    provider = OmniRouteProvider(
        model="auto/cheap",
        api_key="local-key",
        compression="adaptive",
    )
    assert provider._headers["Authorization"] == "Bearer local-key"
    assert provider._headers["X-OmniRoute-Compression"] == "adaptive"


def test_settings_accept_omniroute_as_default(monkeypatch) -> None:
    from hakham.config import load_settings

    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "omniroute")
    monkeypatch.delenv("HAKHAM_MODEL", raising=False)
    monkeypatch.setenv("OMNIROUTE_MODEL", "auto")
    settings = load_settings()
    assert settings.model_provider == "omniroute"
    assert settings.model == "auto"
    assert settings.omniroute_model == "auto"
    assert settings.omniroute_base_url.endswith("/v1")


def test_web_v20_keeps_field_vision_and_context_cards() -> None:
    from hakham import web_v20

    html = web_v20.CONTROL_CENTER_HTML
    assert "v0.20 OMNIROUTE ECONOMY" in html
    assert "fieldCameraBtn" in html
    assert "contextWorkspace" in html
    assert "omnirouteChip" in html
    assert "/api/omniroute/status" in html


def test_latest_points_to_v20() -> None:
    from hakham import web_latest

    assert "v0.20 OMNIROUTE ECONOMY" in web_latest.CONTROL_CENTER_HTML
