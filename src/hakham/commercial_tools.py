from __future__ import annotations

import base64
import time
from typing import Any

import httpx

from .tool_gateway import EvolutionClient, PermissionLevel, ToolGateway, ToolSpec


_INSTALLED = False


def _detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            root = payload.get("response")
            if isinstance(root, dict):
                message = root.get("message")
                if isinstance(message, list):
                    return " | ".join(str(item) for item in message)[:1200]
                if message:
                    return str(message)[:1200]
            for key in ("message", "error", "detail"):
                if payload.get(key):
                    return str(payload.get(key))[:1200]
    except Exception:
        pass
    text = (response.text or "").strip()
    return text[:1200] if text else f"HTTP {response.status_code} sem detalhe"


def _connection_state(self: EvolutionClient) -> str:
    try:
        payload = self.connection_state()
        root = payload.get("instance") if isinstance(payload.get("instance"), dict) else payload
        if isinstance(root, dict):
            return str(root.get("state") or root.get("status") or "").strip().casefold()
    except Exception:
        pass
    return ""


def _send_document(
    self: EvolutionClient,
    number: str,
    media_base64: str,
    filename: str,
    caption: str = "",
    mimetype: str = "application/pdf",
) -> dict[str, Any]:
    if not self.configured:
        raise ValueError("Evolution API is not configured")
    number = "".join(ch for ch in number if ch.isdigit())
    filename = filename.strip() or "orcamento.pdf"
    caption = caption.strip()
    mimetype = mimetype.strip() or "application/pdf"
    if not number or not media_base64.strip():
        raise ValueError("number and PDF media are required")
    try:
        decoded = base64.b64decode(media_base64, validate=True)
    except Exception as exc:
        raise ValueError("invalid base64 document") from exc
    if not decoded.startswith(b"%PDF-"):
        raise ValueError("document payload is not a PDF")
    if len(decoded) > 12 * 1024 * 1024:
        raise ValueError("PDF exceeds 12 MB safety limit")

    endpoint = f"{self.base_url}/message/sendMedia/{self.instance}"
    timeout = httpx.Timeout(connect=12.0, read=75.0, write=45.0, pool=12.0)

    def attempt() -> httpx.Response:
        # Evolution's current sendMedia route accepts multipart/form-data via
        # multer upload.single('file'). This avoids sending a large PDF inside
        # a JSON/base64 body and lets Evolution populate the media buffer itself.
        data = {
            "number": number,
            "mediatype": "document",
            "mimetype": mimetype,
            "caption": caption,
            "fileName": filename,
        }
        files = {"file": (filename, decoded, mimetype)}
        with httpx.Client(timeout=timeout) as client:
            return client.post(
                endpoint,
                headers={"apikey": self.api_key},
                data=data,
                files=files,
            )

    try:
        response = attempt()
    except httpx.ReadTimeout as exc:
        raise RuntimeError(
            "Evolution demorou mais de 75s no envio do PDF. O estado da entrega ficou incerto; confira o WhatsApp antes de tentar novamente."
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Falha de comunicação com a Evolution ao enviar PDF: {type(exc).__name__}: {exc}") from exc

    if not response.is_success:
        detail = _detail(response)
        lowered = detail.casefold()

        # Retry only when Evolution explicitly says the WhatsApp socket closed.
        # For timeouts/ambiguous failures we never retry automatically to avoid
        # duplicate commercial documents.
        if response.status_code >= 500 and "connection closed" in lowered:
            state = _connection_state(self)
            if state in {"open", "connected", "online", "ready"}:
                time.sleep(1.5)
                try:
                    retry = attempt()
                except httpx.RequestError as exc:
                    raise RuntimeError(f"Evolution perdeu a conexão durante a nova tentativa do PDF: {exc}") from exc
                if retry.is_success:
                    response = retry
                else:
                    detail = _detail(retry)
                    raise RuntimeError(f"Evolution sendMedia HTTP {retry.status_code}: {detail}")
            else:
                raise RuntimeError(
                    f"Evolution sendMedia HTTP {response.status_code}: {detail}. Estado atual da instância: {state or 'desconhecido'}"
                )
        else:
            raise RuntimeError(f"Evolution sendMedia HTTP {response.status_code}: {detail}")

    try:
        body = response.json()
    except Exception:
        body = {"raw": response.text[:1200]}
    return body if isinstance(body, dict) else {"result": body}


def install_commercial_tool_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_specs = ToolGateway.specs
    original_execute = ToolGateway.execute
    setattr(EvolutionClient, "send_document", _send_document)

    def specs(self: ToolGateway) -> list[ToolSpec]:
        items = original_specs(self)
        if not any(item.id == "whatsapp.send_document" for item in items):
            items.insert(
                3,
                ToolSpec(
                    "whatsapp.send_document",
                    "Enviar PDF WhatsApp",
                    "whatsapp",
                    PermissionLevel.SENSITIVE,
                    "Enviar documento PDF via Evolution somente após aprovação explícita",
                    self.evolution.configured,
                ),
            )
        return items

    def execute(
        self: ToolGateway,
        tool_id: str,
        arguments: dict[str, Any] | None = None,
        *,
        approved: bool = False,
    ) -> dict[str, Any]:
        if tool_id != "whatsapp.send_document":
            return original_execute(self, tool_id, arguments, approved=approved)
        if not self.evolution.configured:
            raise ValueError("tool is not configured: whatsapp.send_document")
        if not approved:
            raise PermissionError("explicit approval required for whatsapp.send_document")
        arguments = arguments or {}
        return self.evolution.send_document(
            str(arguments.get("number", "")),
            str(arguments.get("media_base64", "")),
            str(arguments.get("filename", "orcamento.pdf")),
            str(arguments.get("caption", "")),
            str(arguments.get("mimetype", "application/pdf")),
        )

    ToolGateway.specs = specs
    ToolGateway.execute = execute
