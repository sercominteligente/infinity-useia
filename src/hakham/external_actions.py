from __future__ import annotations

import re
from typing import Any

import httpx

from .external_integrations import (
    ActionMatch,
    ExternalActionCoordinator as _BaseExternalActionCoordinator,
    install_external_tool_patch as _base_install_external_tool_patch,
)
from .tool_gateway import EvolutionClient


_HARDENED_PATCH_INSTALLED = False


def _safe_offer_call(
    self: EvolutionClient,
    number: str,
    is_video: bool = False,
    call_duration: int = 15,
) -> dict[str, Any]:
    """Call Evolution only when its endpoint appears to perform a real offer.

    Evolution validates callDuration between 1 and 15 seconds. Current
    Evolution/Baileys builds can also expose /call/offer while returning the
    placeholder id "123" instead of placing a real call. Hakham must never tell
    the Ach that a call happened when the upstream route is only a stub.
    """

    if not self.configured:
        raise ValueError("Evolution API is not configured")
    digits = "".join(ch for ch in number if ch.isdigit())
    if len(digits) < 10:
        raise ValueError("WhatsApp number must include DDI and DDD")
    duration = max(1, min(int(call_duration), 15))
    with httpx.Client(timeout=max(self.timeout, 30.0)) as client:
        response = client.post(
            f"{self.base_url}/call/offer/{self.instance}",
            headers={"apikey": self.api_key, "Content-Type": "application/json"},
            json={"number": digits, "isVideo": bool(is_video), "callDuration": duration},
        )
    if not response.is_success:
        detail = (response.text or "").strip()[:1200]
        raise RuntimeError(
            f"Evolution call offer HTTP {response.status_code}: {detail or 'sem detalhe'}"
        )
    try:
        payload = response.json()
    except Exception:
        payload = {"raw": response.text[:3000]}
    result = payload.get("result", payload) if isinstance(payload, dict) else payload
    if isinstance(result, dict) and str(result.get("id") or "") == "123":
        raise RuntimeError(
            "a rota /call/offer desta versão da Evolution respondeu com o placeholder id=123. "
            "Essa implementação não realiza uma chamada real; o Hakham bloqueou a falsa confirmação."
        )
    return payload if isinstance(payload, dict) else {"result": payload}


def install_external_tool_patch() -> None:
    global _HARDENED_PATCH_INSTALLED
    _base_install_external_tool_patch()
    if _HARDENED_PATCH_INSTALLED:
        return
    _HARDENED_PATCH_INSTALLED = True
    setattr(EvolutionClient, "offer_call", _safe_offer_call)


# Install once when this hardened coordinator is imported by Hakham Core.
install_external_tool_patch()


class ExternalActionCoordinator(_BaseExternalActionCoordinator):
    """v0.16 hardened natural-language action classifier.

    The execution logic remains in external_integrations. This subclass tightens
    parsing of side-effecting commands so destination metadata never leaks into
    the message body by accident.
    """

    @classmethod
    def classify(cls, message: str) -> ActionMatch | None:
        text = message.strip()
        low = text.casefold()
        phone_match = cls.PHONE_RE.search(text)

        if ("whatsapp" in low or "whats" in low) and cls._contains_any(
            low, ("ligue", "ligar", "ligação", "chamada")
        ):
            if not phone_match:
                return ActionMatch("whatsapp.call.missing_number", {})
            duration_match = re.search(r"\b(\d{1,2})\s*(?:s|seg|segundos?)\b", low)
            requested_duration = int(duration_match.group(1)) if duration_match else 15
            return ActionMatch(
                "whatsapp.call",
                {
                    "number": "".join(ch for ch in phone_match.group(0) if ch.isdigit()),
                    "is_video": "vídeo" in low or "video" in low,
                    "call_duration": max(1, min(requested_duration, 15)),
                },
            )

        # Side effects require an explicit send verb. Merely mentioning a
        # "mensagem do WhatsApp" must never trigger an outbound message.
        if ("whatsapp" in low or "whats" in low) and cls._contains_any(
            low, ("envie", "enviar", "mande", "mandar")
        ):
            if not phone_match:
                return ActionMatch("whatsapp.send.missing_number", {})
            number = "".join(ch for ch in phone_match.group(0) if ch.isdigit())
            # Parse only what appears AFTER the destination number. This avoids
            # treating the command phrase "envie uma mensagem pelo WhatsApp..."
            # itself as customer-facing content.
            tail = text[phone_match.end() :].strip()
            body = ""
            body_match = re.search(
                r"(?:\bdizendo\b|\b(?:mensagem|texto)\s*[:=-])\s*(.+)$",
                tail,
                re.I,
            )
            if body_match:
                body = body_match.group(1).strip()
            else:
                colon_match = re.match(r"^\s*[:=-]\s*(.+)$", tail)
                if colon_match:
                    body = colon_match.group(1).strip()
            body = body.strip(" \t\r\n\"'“”")
            if not body:
                return ActionMatch("whatsapp.send.missing_text", {"number": number})
            return ActionMatch("whatsapp.send", {"number": number, "text": body})

        if "drive" in low and cls._contains_any(
            low, ("procure", "buscar", "busque", "encontre", "localize", "abra", "leia", "pesquise")
        ):
            cleaned = re.sub(
                r"(?i)\b(?:hakham|ach|no|nosso|google|drive|procure|buscar|busque|encontre|localize|abra|leia|pesquise|por|o|a|os|as|arquivo|pasta)\b",
                " ",
                text,
            )
            query = re.sub(r"\s+", " ", cleaned).strip(" ,.;:-")
            return ActionMatch(
                "drive.search",
                {"query": query, "read_first": bool(re.search(r"\b(?:abra|leia)\b", low))},
            )

        if "github" in low and cls._contains_any(
            low,
            (
                "abra",
                "acesse",
                "procure",
                "encontre",
                "veja",
                "analise",
                "analisa",
                "projeto",
                "repositório",
                "repositorio",
            ),
        ):
            cleaned = re.sub(
                r"(?i)\b(?:hakham|no|github|abra|acesse|procure|encontre|veja|analise|analisa|o|a|os|as|projeto|repositório|repositorio)\b",
                " ",
                text,
            )
            query = re.sub(r"\s+", " ", cleaned).strip(" ,.;:-")
            return ActionMatch("github.project", {"query": query})

        if "instagram" in low or re.search(r"(?<!\w)@[A-Za-z0-9._]{2,30}\b", text):
            if cls._contains_any(
                low,
                ("analise", "analisa", "pesquise", "pesquisa", "audite", "auditoria", "veja", "perfil"),
            ):
                user_match = re.search(r"@([A-Za-z0-9._]{2,30})", text)
                if not user_match:
                    user_match = re.search(r"instagram(?:\.com)?[/\s]+([A-Za-z0-9._]{2,30})", low)
                username = user_match.group(1) if user_match else ""
                return ActionMatch("instagram.analyze", {"username": username})

        if cls._contains_any(
            low,
            (
                "ative a webcam",
                "ativar webcam",
                "ligue a webcam",
                "abrir webcam",
                "abra a webcam",
                "ative a câmera",
                "ative a camera",
                "ligue a câmera",
                "ligue a camera",
            ),
        ):
            return ActionMatch("webcam.activate", {})

        if ("email" in low or "e-mail" in low) and cls._contains_any(
            low, ("envie", "enviar", "mande", "mandar")
        ):
            email_match = cls.EMAIL_RE.search(text)
            if not email_match:
                return ActionMatch("email.send.missing_recipient", {})
            subject_match = re.search(
                r"(?:assunto)\s*[:=-]?\s*(.+?)(?=\s+(?:mensagem|texto|corpo|dizendo)\b|$)",
                text,
                re.I,
            )
            body_match = re.search(
                r"(?:mensagem|texto|corpo|dizendo)\s*[:=-]?\s*(.+)$",
                text,
                re.I,
            )
            return ActionMatch(
                "email.send",
                {
                    "to": email_match.group(0),
                    "subject": subject_match.group(1).strip(" ,.;") if subject_match else "",
                    "text": body_match.group(1).strip() if body_match else "",
                },
            )

        return None
