import pytest

from hakham.tool_gateway import PermissionLevel, ToolGateway


def test_gateway_marks_unconfigured_connectors(monkeypatch):
    for name in (
        "EVOLUTION_API_URL",
        "EVOLUTION_API_KEY",
        "EVOLUTION_INSTANCE",
        "GOOGLE_DRIVE_ACCESS_TOKEN",
        "GOOGLE_DRIVE_CLIENT_ID",
        "GOOGLE_DRIVE_CLIENT_SECRET",
        "GOOGLE_DRIVE_REFRESH_TOKEN",
        "META_GRAPH_ACCESS_TOKEN",
        "META_INSTAGRAM_ACCOUNT_ID",
        "META_FACEBOOK_PAGE_ID",
        "GITHUB_TOKEN",
        "GITHUB_REPOSITORY",
        "RESEND_API_KEY",
        "EMAIL_FROM",
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
    ):
        monkeypatch.delenv(name, raising=False)

    gateway = ToolGateway()
    summary = gateway.summary()

    # Three capabilities remain usable with no external credential: public web
    # research, Instagram analysis through its public-web fallback, and the
    # browser-local webcam gate. Credential-backed connectors stay unconfigured.
    assert summary["configured"] == 3
    assert any(
        item["id"] == "web.search"
        and item["configured"] is True
        and item["permission"] == "green"
        for item in summary["items"]
    )
    assert any(item["id"] == "instagram.analyze" and item["configured"] is True for item in summary["items"])
    assert any(item["id"] == "webcam.capture" and item["configured"] is True for item in summary["items"])
    assert any(item["id"] == "whatsapp.send_text" and item["permission"] == "red" for item in summary["items"])
    assert any(item["id"] == "drive.search" and item["permission"] == "green" for item in summary["items"])
    assert any(item["id"] == "github.status" and item["permission"] == "green" for item in summary["items"])
    assert any(item["id"] == "cloudflare.status" and item["permission"] == "green" for item in summary["items"])
    assert any(item["id"] == "cloudflare.inventory" and item["permission"] == "green" for item in summary["items"])


def test_github_and_cloudflare_configuration_flags(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "github-test-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "sercominteligente/hakham-infinity")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "cloudflare-test-token")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "account-test")

    gateway = ToolGateway()
    specs = {item.id: item for item in gateway.specs()}

    assert specs["github.status"].configured is True
    assert specs["github.repositories"].configured is True
    assert specs["cloudflare.status"].configured is True
    assert specs["cloudflare.inventory"].configured is True
    assert specs["github.status"].permission is PermissionLevel.READ
    assert specs["cloudflare.inventory"].permission is PermissionLevel.READ


def test_sensitive_tool_requires_explicit_approval(monkeypatch):
    monkeypatch.setenv("EVOLUTION_API_URL", "https://example.invalid")
    monkeypatch.setenv("EVOLUTION_API_KEY", "key")
    monkeypatch.setenv("EVOLUTION_INSTANCE", "hakham")

    gateway = ToolGateway()
    with pytest.raises(PermissionError, match="explicit approval"):
        gateway.execute("whatsapp.send_text", {"number": "5585999999999", "text": "Shalom"})


def test_permission_enum_values_are_stable():
    assert PermissionLevel.READ.value == "green"
    assert PermissionLevel.REVERSIBLE.value == "yellow"
    assert PermissionLevel.SENSITIVE.value == "red"
