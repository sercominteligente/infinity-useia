from hakham.external_actions import ExternalActionCoordinator, install_external_tool_patch
from hakham.tool_gateway import ToolGateway


def test_classifies_whatsapp_call_and_message() -> None:
    call = ExternalActionCoordinator.classify(
        "Hakham, faça uma ligação pelo WhatsApp para 5585988104302 por 15 segundos"
    )
    assert call is not None
    assert call.kind == "whatsapp.call"
    assert call.data["number"] == "5585988104302"
    assert call.data["call_duration"] == 15

    message = ExternalActionCoordinator.classify(
        "Hakham, envie uma mensagem pelo WhatsApp para 5585988104302 dizendo orçamento aprovado"
    )
    assert message is not None
    assert message.kind == "whatsapp.send"
    assert message.data["number"] == "5585988104302"
    assert message.data["text"] == "orçamento aprovado"


def test_classifies_read_only_integrations() -> None:
    drive = ExternalActionCoordinator.classify("Hakham procure no nosso Drive Portal Luna")
    assert drive is not None and drive.kind == "drive.search"
    assert "Portal Luna" in drive.data["query"]

    github = ExternalActionCoordinator.classify("Hakham abra no GitHub o projeto SERhub")
    assert github is not None and github.kind == "github.project"
    assert "SERhub" in github.data["query"]

    instagram = ExternalActionCoordinator.classify("Hakham analise o Instagram @ser.com.visual")
    assert instagram is not None and instagram.kind == "instagram.analyze"
    assert instagram.data["username"] == "ser.com.visual"


def test_classifies_webcam_and_email() -> None:
    camera = ExternalActionCoordinator.classify("Hakham ative a webcam")
    assert camera is not None and camera.kind == "webcam.activate"

    email = ExternalActionCoordinator.classify(
        "Hakham envie um email para cliente@example.com assunto: Proposta mensagem: Segue nossa proposta comercial"
    )
    assert email is not None and email.kind == "email.send"
    assert email.data["to"] == "cliente@example.com"
    assert email.data["subject"] == "Proposta"
    assert email.data["text"] == "Segue nossa proposta comercial"


def test_gateway_exposes_all_six_capability_groups(monkeypatch) -> None:
    monkeypatch.setenv("EVOLUTION_API_URL", "https://example.invalid")
    monkeypatch.setenv("EVOLUTION_API_KEY", "key")
    monkeypatch.setenv("EVOLUTION_INSTANCE", "SER-INTELIGENTE")
    monkeypatch.setenv("GOOGLE_DRIVE_ACCESS_TOKEN", "drive-token")
    monkeypatch.setenv("GITHUB_TOKEN", "github-token")
    monkeypatch.setenv("META_GRAPH_ACCESS_TOKEN", "meta-token")
    monkeypatch.setenv("META_INSTAGRAM_ACCOUNT_ID", "123")
    monkeypatch.setenv("RESEND_API_KEY", "resend-token")
    monkeypatch.setenv("EMAIL_FROM", "atendimento@example.com")

    install_external_tool_patch()
    ids = {spec.id for spec in ToolGateway().specs()}
    expected = {
        "whatsapp.send_text",
        "whatsapp.call",
        "drive.search",
        "drive.read",
        "github.find_repository",
        "github.tree",
        "github.read_file",
        "instagram.analyze",
        "webcam.capture",
        "email.status",
        "email.send",
    }
    assert expected.issubset(ids)


def test_webcam_gateway_requires_explicit_approval() -> None:
    install_external_tool_patch()
    gateway = ToolGateway()
    try:
        gateway.execute("webcam.capture", {}, approved=False)
    except PermissionError:
        pass
    else:
        raise AssertionError("webcam.capture must require explicit approval")

    result = gateway.execute("webcam.capture", {}, approved=True)
    assert result["action"] == "browser_camera"
    assert result["audio"] is False
