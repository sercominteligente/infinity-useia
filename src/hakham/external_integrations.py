from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import quote

import httpx

from .tool_gateway import EvolutionClient, PermissionLevel, ToolGateway, ToolSpec
from .web_research import WebResearchService


DEFAULT_DRIVE_ROOT = "1nsRNUkNtCEM4BiFJ4xVgQXg65dNiE4vU"
_INSTALLED = False


def _digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _json_response(response: httpx.Response) -> dict[str, Any]:
    response.raise_for_status()
    try:
        payload = response.json()
    except Exception:
        return {"raw": response.text[:5000]}
    return payload if isinstance(payload, dict) else {"result": payload}


def _clip(value: Any, limit: int = 18000) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= limit else text[:limit] + "…"


class DriveAccessClient:
    """Read-only Google Drive access with optional OAuth refresh support.

    The root folder defaults to the shared SER project folder. No create, edit,
    move or delete operation exists in this client by design.
    """

    def __init__(self) -> None:
        self.access_token = os.getenv("GOOGLE_DRIVE_ACCESS_TOKEN", "").strip()
        self.client_id = os.getenv("GOOGLE_DRIVE_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET", "").strip()
        self.refresh_token = os.getenv("GOOGLE_DRIVE_REFRESH_TOKEN", "").strip()
        self.root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID", DEFAULT_DRIVE_ROOT).strip() or DEFAULT_DRIVE_ROOT
        self.timeout = 30.0

    @property
    def configured(self) -> bool:
        return bool(self.access_token or (self.client_id and self.client_secret and self.refresh_token))

    def _refresh_access_token(self) -> str:
        if not (self.client_id and self.client_secret and self.refresh_token):
            raise ValueError("Google Drive OAuth refresh credentials are not configured")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
        payload = _json_response(response)
        token = str(payload.get("access_token") or "").strip()
        if not token:
            raise RuntimeError("Google OAuth did not return an access token")
        self.access_token = token
        return token

    def _token(self) -> str:
        if self.access_token:
            return self.access_token
        return self._refresh_access_token()

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if not self.configured:
            raise ValueError("Google Drive is not configured")
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["Authorization"] = f"Bearer {self._token()}"
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.request(method, url, headers=headers, **kwargs)
        if response.status_code == 401 and self.client_id and self.client_secret and self.refresh_token:
            headers["Authorization"] = f"Bearer {self._refresh_access_token()}"
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.request(method, url, headers=headers, **kwargs)
        return response

    def _children(self, folder_id: str, page_size: int = 100) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        token = ""
        while True:
            params: dict[str, Any] = {
                "q": f"'{folder_id}' in parents and trashed = false",
                "pageSize": max(1, min(page_size, 100)),
                "fields": "nextPageToken,files(id,name,mimeType,modifiedTime,webViewLink,size,parents)",
                "orderBy": "folder,name",
            }
            if token:
                params["pageToken"] = token
            response = self._request("GET", "https://www.googleapis.com/drive/v3/files", params=params)
            payload = _json_response(response)
            page = payload.get("files") or []
            files.extend(item for item in page if isinstance(item, dict))
            token = str(payload.get("nextPageToken") or "")
            if not token:
                break
        return files

    def search(self, query: str, limit: int = 20) -> dict[str, Any]:
        query = query.strip().casefold()
        limit = max(1, min(int(limit), 50))
        queue: list[tuple[str, str]] = [(self.root_folder_id, "SER Projetos")]
        matches: list[dict[str, Any]] = []
        scanned = 0
        max_scan = max(100, min(int(os.getenv("GOOGLE_DRIVE_MAX_SCAN", "900")), 5000))
        seen: set[str] = set()

        while queue and scanned < max_scan and len(matches) < limit:
            folder_id, folder_path = queue.pop(0)
            if folder_id in seen:
                continue
            seen.add(folder_id)
            for item in self._children(folder_id):
                scanned += 1
                name = str(item.get("name") or "")
                mime = str(item.get("mimeType") or "")
                path = f"{folder_path}/{name}"
                if mime == "application/vnd.google-apps.folder":
                    queue.append((str(item.get("id") or ""), path))
                if not query or query in name.casefold() or query in path.casefold():
                    matches.append({**item, "path": path})
                    if len(matches) >= limit:
                        break
                if scanned >= max_scan:
                    break

        return {
            "root_folder_id": self.root_folder_id,
            "query": query,
            "count": len(matches),
            "scanned": scanned,
            "truncated": bool(queue and scanned >= max_scan),
            "files": matches,
        }

    def read(self, file_id: str, max_chars: int = 22000) -> dict[str, Any]:
        file_id = file_id.strip()
        if not file_id:
            raise ValueError("Drive file id is required")
        meta_response = self._request(
            "GET",
            f"https://www.googleapis.com/drive/v3/files/{quote(file_id, safe='')}",
            params={"fields": "id,name,mimeType,modifiedTime,webViewLink,size,parents"},
        )
        meta = _json_response(meta_response)
        mime = str(meta.get("mimeType") or "")
        export_mime = ""
        if mime == "application/vnd.google-apps.document":
            export_mime = "text/plain"
        elif mime == "application/vnd.google-apps.spreadsheet":
            export_mime = "text/csv"
        elif mime == "application/vnd.google-apps.presentation":
            export_mime = "text/plain"

        if export_mime:
            response = self._request(
                "GET",
                f"https://www.googleapis.com/drive/v3/files/{quote(file_id, safe='')}/export",
                params={"mimeType": export_mime},
            )
        elif not mime.startswith("application/vnd.google-apps."):
            response = self._request(
                "GET",
                f"https://www.googleapis.com/drive/v3/files/{quote(file_id, safe='')}",
                params={"alt": "media"},
            )
        else:
            return {"metadata": meta, "readable_text": False, "reason": f"Google file type not text-exportable: {mime}"}

        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if export_mime or content_type.startswith("text/") or "json" in content_type or "xml" in content_type:
            text = response.text
            return {
                "metadata": meta,
                "readable_text": True,
                "content": text[:max_chars],
                "truncated": len(text) > max_chars,
            }
        return {
            "metadata": meta,
            "readable_text": False,
            "reason": f"binary content ({content_type or mime})",
            "bytes": len(response.content),
        }


class GitHubAccessClient:
    """Read-only GitHub project browser."""

    def __init__(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN", "").strip()
        self.base_url = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com").rstrip("/")
        self.timeout = 30.0

    @property
    def configured(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not self.configured:
            raise ValueError("GitHub token is not configured")
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(f"{self.base_url}{path}", headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    def find_repository(self, query: str, limit: int = 20) -> dict[str, Any]:
        payload = self._get("/user/repos", {"per_page": 100, "sort": "updated", "direction": "desc"})
        words = [part for part in re.split(r"\s+", query.casefold().strip()) if part]
        rows: list[tuple[int, dict[str, Any]]] = []
        if isinstance(payload, list):
            for item in payload:
                if not isinstance(item, dict):
                    continue
                haystack = " ".join(
                    str(item.get(key) or "") for key in ("name", "full_name", "description")
                ).casefold()
                score = sum(3 if word in str(item.get("name") or "").casefold() else 1 for word in words if word in haystack)
                if not words:
                    score = 1
                if score:
                    rows.append((score, item))
        rows.sort(key=lambda row: (row[0], str(row[1].get("updated_at") or "")), reverse=True)
        repos = [
            {
                "full_name": item.get("full_name"),
                "description": item.get("description"),
                "private": item.get("private"),
                "default_branch": item.get("default_branch"),
                "updated_at": item.get("updated_at"),
                "html_url": item.get("html_url"),
            }
            for _, item in rows[: max(1, min(int(limit), 50))]
        ]
        return {"query": query, "count": len(repos), "repositories": repos}

    def tree(self, repository: str, path: str = "") -> dict[str, Any]:
        repository = repository.strip().strip("/")
        path = path.strip().strip("/")
        if not repository or "/" not in repository:
            raise ValueError("repository must be owner/name")
        suffix = f"/{quote(path, safe='/')}" if path else ""
        payload = self._get(f"/repos/{repository}/contents{suffix}")
        if isinstance(payload, list):
            items = [
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "type": item.get("type"),
                    "size": item.get("size"),
                    "html_url": item.get("html_url"),
                }
                for item in payload
                if isinstance(item, dict)
            ]
        elif isinstance(payload, dict):
            items = [{"name": payload.get("name"), "path": payload.get("path"), "type": payload.get("type"), "size": payload.get("size")}]
        else:
            items = []
        return {"repository": repository, "path": path or "/", "items": items, "count": len(items)}

    def read_file(self, repository: str, path: str, max_chars: int = 30000) -> dict[str, Any]:
        repository = repository.strip().strip("/")
        path = path.strip().strip("/")
        if not repository or "/" not in repository or not path:
            raise ValueError("repository owner/name and file path are required")
        payload = self._get(f"/repos/{repository}/contents/{quote(path, safe='/')}")
        if not isinstance(payload, dict) or payload.get("type") != "file":
            raise ValueError("GitHub path is not a file")
        encoded = str(payload.get("content") or "").replace("\n", "")
        if payload.get("encoding") != "base64" or not encoded:
            return {
                "repository": repository,
                "path": path,
                "readable_text": False,
                "size": payload.get("size"),
                "html_url": payload.get("html_url"),
            }
        raw = base64.b64decode(encoded)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return {"repository": repository, "path": path, "readable_text": False, "size": len(raw), "html_url": payload.get("html_url")}
        return {
            "repository": repository,
            "path": path,
            "readable_text": True,
            "content": text[:max_chars],
            "truncated": len(text) > max_chars,
            "html_url": payload.get("html_url"),
        }


class InstagramResearchClient:
    """Read-only Instagram professional account/business discovery client."""

    def __init__(self) -> None:
        self.access_token = os.getenv("META_GRAPH_ACCESS_TOKEN", "").strip()
        self.account_id = os.getenv("META_INSTAGRAM_ACCOUNT_ID", "").strip()
        self.base_url = os.getenv("META_GRAPH_BASE_URL", "https://graph.facebook.com/v26.0").rstrip("/")
        self.timeout = 30.0

    @property
    def configured(self) -> bool:
        return bool(self.access_token and self.account_id)

    def analyze(self, username: str, media_limit: int = 12) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Instagram Graph read-only access is not configured")
        username = username.strip().lstrip("@").split("/")[0]
        if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", username):
            raise ValueError("invalid Instagram username")
        media_limit = max(1, min(int(media_limit), 25))
        fields = (
            f"business_discovery.username({username})"
            "{username,name,biography,website,followers_count,follows_count,media_count,profile_picture_url,"
            f"media.limit({media_limit}){{id,caption,media_type,permalink,timestamp,like_count,comments_count}}}}"
        )
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/{self.account_id}",
                params={"fields": fields, "access_token": self.access_token},
            )
        payload = _json_response(response)
        discovery = payload.get("business_discovery")
        return discovery if isinstance(discovery, dict) else payload


class ResendEmailClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("RESEND_API_KEY", "").strip()
        self.from_email = os.getenv("EMAIL_FROM", "").strip()
        self.from_name = os.getenv("EMAIL_FROM_NAME", "SER Comtec").strip() or "SER Comtec"
        self.reply_to = os.getenv("EMAIL_REPLY_TO", "").strip()
        self.timeout = 30.0

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.from_email)

    def status(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "provider": "resend",
            "from": self.from_email or None,
            "from_name": self.from_name,
            "reply_to_configured": bool(self.reply_to),
        }

    def send(self, to: str, subject: str, text: str, html: str = "") -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Email sender is not configured. Set RESEND_API_KEY and EMAIL_FROM")
        to = to.strip()
        subject = subject.strip()
        text = text.strip()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", to):
            raise ValueError("invalid recipient email")
        if not subject or not text:
            raise ValueError("email subject and text are required")
        payload: dict[str, Any] = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [to],
            "subject": subject,
            "text": text,
        }
        if html.strip():
            payload["html"] = html.strip()
        if self.reply_to:
            payload["reply_to"] = self.reply_to
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
        return _json_response(response)


def _offer_call(self: EvolutionClient, number: str, is_video: bool = False, call_duration: int = 20) -> dict[str, Any]:
    if not self.configured:
        raise ValueError("Evolution API is not configured")
    number = _digits(number)
    if len(number) < 10:
        raise ValueError("WhatsApp number must include DDI and DDD")
    call_duration = max(5, min(int(call_duration), 60))
    with httpx.Client(timeout=max(self.timeout, 30.0)) as client:
        response = client.post(
            f"{self.base_url}/call/offer/{self.instance}",
            headers={"apikey": self.api_key, "Content-Type": "application/json"},
            json={"number": number, "isVideo": bool(is_video), "callDuration": call_duration},
        )
    return _json_response(response)


def _external_clients(gateway: ToolGateway) -> dict[str, Any]:
    cache = getattr(gateway, "_hakham_external_clients", None)
    if cache is None:
        cache = {
            "drive": DriveAccessClient(),
            "github": GitHubAccessClient(),
            "instagram": InstagramResearchClient(),
            "email": ResendEmailClient(),
        }
        setattr(gateway, "_hakham_external_clients", cache)
    return cache


def install_external_tool_patch() -> None:
    """Extend the existing ToolGateway without replacing its stable tools."""

    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_specs = ToolGateway.specs
    original_execute = ToolGateway.execute
    setattr(EvolutionClient, "offer_call", _offer_call)

    def specs(self: ToolGateway) -> list[ToolSpec]:
        clients = _external_clients(self)
        items = list(original_specs(self))
        replacements = {
            "drive.search": ToolSpec(
                "drive.search", "Buscar no Drive SER", "drive", PermissionLevel.READ,
                "Pesquisar recursivamente no Drive compartilhado de projetos SER", clients["drive"].configured,
            ),
        }
        new_items = [
            ToolSpec("whatsapp.call", "Ligação WhatsApp", "whatsapp", PermissionLevel.SENSITIVE, "Iniciar chamada de áudio ou vídeo via Evolution após solicitação explícita", self.evolution.configured),
            ToolSpec("drive.read", "Ler arquivo Drive", "drive", PermissionLevel.READ, "Abrir conteúdo textual de arquivo encontrado no Drive", clients["drive"].configured),
            ToolSpec("github.find_repository", "Localizar projeto GitHub", "devops", PermissionLevel.READ, "Encontrar repositório acessível pelo nome do projeto", clients["github"].configured),
            ToolSpec("github.tree", "Explorar projeto GitHub", "devops", PermissionLevel.READ, "Listar arquivos e pastas de um repositório", clients["github"].configured),
            ToolSpec("github.read_file", "Ler arquivo GitHub", "devops", PermissionLevel.READ, "Abrir arquivo textual de um projeto GitHub", clients["github"].configured),
            ToolSpec("instagram.analyze", "Analisar Instagram", "social", PermissionLevel.READ, "Consultar perfil profissional e publicações para análise, sem publicar ou alterar nada", clients["instagram"].configured or True),
            ToolSpec("webcam.capture", "Webcam", "vision", PermissionLevel.SENSITIVE, "Abrir câmera somente com gesto explícito no navegador e enviar quadro para visão do Hakham", True),
            ToolSpec("email.status", "E-mail Status", "email", PermissionLevel.READ, "Verificar configuração do canal de e-mail", clients["email"].configured),
            ToolSpec("email.send", "Enviar e-mail", "email", PermissionLevel.SENSITIVE, "Enviar e-mail via Resend quando destinatário, assunto e conteúdo forem explicitamente solicitados", clients["email"].configured),
        ]
        merged: list[ToolSpec] = []
        seen: set[str] = set()
        for item in items:
            item = replacements.get(item.id, item)
            if item.id not in seen:
                merged.append(item)
                seen.add(item.id)
        for item in new_items:
            if item.id not in seen:
                merged.append(item)
                seen.add(item.id)
        return merged

    def execute(
        self: ToolGateway,
        tool_id: str,
        arguments: dict[str, Any] | None = None,
        *,
        approved: bool = False,
    ) -> dict[str, Any]:
        arguments = arguments or {}
        clients = _external_clients(self)

        if tool_id == "whatsapp.call":
            if not self.evolution.configured:
                raise ValueError("tool is not configured: whatsapp.call")
            if not approved:
                raise PermissionError("explicit approval required for whatsapp.call")
            return self.evolution.offer_call(
                str(arguments.get("number", "")),
                bool(arguments.get("is_video", False)),
                int(arguments.get("call_duration", 20)),
            )
        if tool_id == "drive.search":
            return clients["drive"].search(str(arguments.get("query", "")), int(arguments.get("page_size", 20)))
        if tool_id == "drive.read":
            return clients["drive"].read(str(arguments.get("file_id", "")), int(arguments.get("max_chars", 22000)))
        if tool_id == "github.find_repository":
            return clients["github"].find_repository(str(arguments.get("query", "")), int(arguments.get("limit", 20)))
        if tool_id == "github.tree":
            return clients["github"].tree(str(arguments.get("repository", "")), str(arguments.get("path", "")))
        if tool_id == "github.read_file":
            return clients["github"].read_file(str(arguments.get("repository", "")), str(arguments.get("path", "")), int(arguments.get("max_chars", 30000)))
        if tool_id == "instagram.analyze":
            username = str(arguments.get("username", "")).strip().lstrip("@")
            if clients["instagram"].configured:
                return {"source": "meta_graph", "profile": clients["instagram"].analyze(username, int(arguments.get("media_limit", 12)))}
            research = WebResearchService()
            return {
                "source": "public_web",
                "warning": "Meta Graph Business Discovery is not configured; analysis is based on public web research only.",
                "research": research.search(f"Instagram @{username} perfil posts empresa", max_results=8),
            }
        if tool_id == "webcam.capture":
            if not approved:
                raise PermissionError("explicit browser gesture required for webcam.capture")
            return {"action": "browser_camera", "requires_user_gesture": True, "audio": False}
        if tool_id == "email.status":
            return clients["email"].status()
        if tool_id == "email.send":
            if not clients["email"].configured:
                raise ValueError("tool is not configured: email.send")
            if not approved:
                raise PermissionError("explicit approval required for email.send")
            return clients["email"].send(
                str(arguments.get("to", "")),
                str(arguments.get("subject", "")),
                str(arguments.get("text", "")),
                str(arguments.get("html", "")),
            )
        return original_execute(self, tool_id, arguments, approved=approved)

    ToolGateway.specs = specs
    ToolGateway.execute = execute


@dataclass(frozen=True)
class ActionMatch:
    kind: str
    data: dict[str, Any]


class ExternalActionCoordinator:
    """Conservative natural-language bridge for the six external capabilities.

    It only executes side effects when the user's sentence itself contains a
    clear imperative plus all critical destination data. Read-only research can
    be handled more liberally. Ambiguous requests fall back to normal Hakham.
    """

    PHONE_RE = re.compile(r"\+?\d[\d\s().-]{8,}\d")
    EMAIL_RE = re.compile(r"[^\s<>@]+@[^\s<>@]+\.[A-Za-z]{2,}")

    def __init__(
        self,
        *,
        working: Any,
        generate: Callable[[str], str] | None = None,
        web: WebResearchService | None = None,
    ) -> None:
        install_external_tool_patch()
        self.working = working
        self.generate = generate
        self.web = web or WebResearchService()

    @staticmethod
    def _contains_any(text: str, words: tuple[str, ...]) -> bool:
        lowered = text.casefold()
        return any(word in lowered for word in words)

    @classmethod
    def classify(cls, message: str) -> ActionMatch | None:
        text = message.strip()
        low = text.casefold()
        phone_match = cls.PHONE_RE.search(text)

        if ("whatsapp" in low or "whats" in low) and cls._contains_any(low, ("ligue", "ligar", "ligação", "chamada")):
            if not phone_match:
                return ActionMatch("whatsapp.call.missing_number", {})
            duration_match = re.search(r"\b(\d{1,2})\s*(?:s|seg|segundos?)\b", low)
            return ActionMatch(
                "whatsapp.call",
                {
                    "number": _digits(phone_match.group(0)),
                    "is_video": "vídeo" in low or "video" in low,
                    "call_duration": int(duration_match.group(1)) if duration_match else 20,
                },
            )

        if ("whatsapp" in low or "whats" in low) and cls._contains_any(low, ("envie", "enviar", "mande", "mandar", "mensagem")):
            if not phone_match:
                return ActionMatch("whatsapp.send.missing_number", {})
            body_match = re.search(r"(?:dizendo|mensagem\s*[:=-]?|texto\s*[:=-]?|:\s*)(.+)$", text, re.I)
            body = body_match.group(1).strip() if body_match else ""
            if not body:
                return ActionMatch("whatsapp.send.missing_text", {"number": _digits(phone_match.group(0))})
            return ActionMatch("whatsapp.send", {"number": _digits(phone_match.group(0)), "text": body})

        if "drive" in low and cls._contains_any(low, ("procure", "buscar", "busque", "encontre", "localize", "abra", "leia", "pesquise")):
            cleaned = re.sub(r"(?i)\b(?:hakham|ach|no|nosso|google|drive|procure|buscar|busque|encontre|localize|abra|leia|pesquise|por|o|a|os|as|arquivo|pasta)\b", " ", text)
            query = re.sub(r"\s+", " ", cleaned).strip(" ,.;:-")
            return ActionMatch("drive.search", {"query": query, "read_first": bool(re.search(r"\b(?:abra|leia)\b", low))})

        if "github" in low and cls._contains_any(low, ("abra", "acesse", "procure", "encontre", "veja", "analise", "analisa", "projeto", "repositório", "repositorio")):
            cleaned = re.sub(r"(?i)\b(?:hakham|no|github|abra|acesse|procure|encontre|veja|analise|analisa|o|a|os|as|projeto|repositório|repositorio)\b", " ", text)
            query = re.sub(r"\s+", " ", cleaned).strip(" ,.;:-")
            return ActionMatch("github.project", {"query": query})

        if "instagram" in low or re.search(r"(?<!\w)@[A-Za-z0-9._]{2,30}\b", text):
            if cls._contains_any(low, ("analise", "analisa", "pesquise", "pesquisa", "audite", "auditoria", "veja", "perfil")):
                user_match = re.search(r"@([A-Za-z0-9._]{2,30})", text)
                if not user_match:
                    user_match = re.search(r"instagram(?:\.com)?[/\s]+([A-Za-z0-9._]{2,30})", low)
                username = user_match.group(1) if user_match else ""
                return ActionMatch("instagram.analyze", {"username": username})

        if cls._contains_any(low, ("ative a webcam", "ativar webcam", "ligue a webcam", "abrir webcam", "abra a webcam", "ative a câmera", "ative a camera", "ligue a câmera", "ligue a camera")):
            return ActionMatch("webcam.activate", {})

        if ("email" in low or "e-mail" in low) and cls._contains_any(low, ("envie", "enviar", "mande", "mandar")):
            email_match = cls.EMAIL_RE.search(text)
            if not email_match:
                return ActionMatch("email.send.missing_recipient", {})
            subject_match = re.search(r"(?:assunto)\s*[:=-]?\s*(.+?)(?=\s+(?:mensagem|texto|corpo|dizendo)\b|$)", text, re.I)
            body_match = re.search(r"(?:mensagem|texto|corpo|dizendo)\s*[:=-]?\s*(.+)$", text, re.I)
            return ActionMatch(
                "email.send",
                {
                    "to": email_match.group(0),
                    "subject": subject_match.group(1).strip(" ,.;") if subject_match else "",
                    "text": body_match.group(1).strip() if body_match else "",
                },
            )
        return None

    def _remember(self, key: str, value: Any) -> None:
        self.working.set(key, _clip(value))

    def _summarize(self, instruction: str, data: Any) -> str:
        self._remember("tool:external:last", data)
        if self.generate is None:
            return _clip(data, 5000)
        prompt = (
            "Você é HAKHAM Infinity. Use exclusivamente o resultado de ferramenta abaixo. "
            "Não invente dados, credenciais, arquivos, métricas ou ações. Responda em português do Brasil.\n\n"
            f"INSTRUÇÃO: {instruction}\n\nRESULTADO DA FERRAMENTA:\n{_clip(data, 18000)}\n\nHAKHAM:"
        )
        return self.generate(prompt)

    def handle(self, message: str) -> str | None:
        match = self.classify(message)
        if match is None:
            return None
        gateway = ToolGateway()

        if match.kind == "whatsapp.call.missing_number":
            return "Ach, consigo iniciar a ligação pelo WhatsApp, mas preciso do número com DDI e DDD."
        if match.kind == "whatsapp.call":
            try:
                result = gateway.execute("whatsapp.call", match.data, approved=True)
            except Exception as exc:
                return f"Ach, não consegui iniciar a chamada pelo WhatsApp: {exc}"
            self._remember("tool:whatsapp.call", result)
            return (
                f"Ach, a solicitação de chamada {'de vídeo' if match.data['is_video'] else 'de áudio'} para "
                f"{match.data['number']} foi aceita pela Evolution. Isso inicia a oferta de chamada; não vou afirmar que o destinatário atendeu sem confirmação do canal."
            )

        if match.kind == "whatsapp.send.missing_number":
            return "Ach, preciso do número do WhatsApp com DDI e DDD para enviar a mensagem."
        if match.kind == "whatsapp.send.missing_text":
            return f"Ach, tenho o WhatsApp {match.data['number']}, mas falta o texto exato que devo enviar."
        if match.kind == "whatsapp.send":
            try:
                result = gateway.execute("whatsapp.send_text", match.data, approved=True)
            except Exception as exc:
                return f"Ach, não consegui enviar a mensagem pelo WhatsApp: {exc}"
            self._remember("tool:whatsapp.send_text", result)
            return f"Mensagem aceita pela Evolution para {match.data['number']}. A entrega final depende do estado confirmado pelo WhatsApp/Evolution."

        if match.kind == "drive.search":
            query = str(match.data.get("query") or "")
            try:
                result = gateway.execute("drive.search", {"query": query, "page_size": 20})
            except Exception as exc:
                return (
                    f"Ach, não consegui acessar o Drive: {exc}. Para o Hakham local, o conector desta conversa não transfere credenciais automaticamente; "
                    "configure GOOGLE_DRIVE_ACCESS_TOKEN ou OAuth com refresh token no .env."
                )
            files = result.get("files") if isinstance(result, dict) else None
            if match.data.get("read_first") and isinstance(files, list) and len(files) == 1 and isinstance(files[0], dict):
                try:
                    opened = gateway.execute("drive.read", {"file_id": files[0].get("id"), "max_chars": 22000})
                    return self._summarize(f"Leia e resuma o arquivo {files[0].get('name')!r} encontrado no Drive SER.", opened)
                except Exception as exc:
                    self._remember("tool:drive.search", result)
                    return f"Encontrei o arquivo no Drive, mas não consegui abrir seu conteúdo textual: {exc}"
            return self._summarize(f"Resuma os arquivos encontrados no Drive SER para a busca {query!r}, destacando caminho e nome.", result)

        if match.kind == "github.project":
            query = str(match.data.get("query") or "").strip()
            if not query:
                return "Ach, diga o nome do projeto que devo localizar no GitHub."
            try:
                found = gateway.execute("github.find_repository", {"query": query, "limit": 8})
                repos = found.get("repositories") if isinstance(found, dict) else []
                if not repos:
                    return f"Não encontrei repositório acessível no GitHub para {query!r}."
                repo = str(repos[0].get("full_name") or "")
                tree = gateway.execute("github.tree", {"repository": repo, "path": ""})
            except Exception as exc:
                return f"Ach, não consegui acessar o projeto no GitHub: {exc}"
            combined = {"match": repos[0], "root_tree": tree}
            return self._summarize(
                f"O Ach pediu acesso ao projeto GitHub {query!r}. Identifique o repositório localizado e descreva a estrutura raiz. Não altere nada.",
                combined,
            )

        if match.kind == "instagram.analyze":
            username = str(match.data.get("username") or "").strip().lstrip("@")
            if not username:
                return "Ach, diga o @usuário do Instagram que devo analisar."
            try:
                result = gateway.execute("instagram.analyze", {"username": username, "media_limit": 12})
            except Exception as exc:
                return f"Ach, não consegui pesquisar o Instagram @{username}: {exc}"
            return self._summarize(
                f"Faça uma análise objetiva do Instagram @{username}: posicionamento, bio, sinais de consistência, conteúdo recente, oportunidades e limitações dos dados. Somente leitura e pesquisa.",
                result,
            )

        if match.kind == "webcam.activate":
            return (
                "Ach, a webcam precisa de autorização explícita do navegador. Use o botão WEBCAM no bloco VISÃO; "
                "quando estiver ativa o painel mostrará VISÃO AO VIVO e nenhum áudio será capturado."
            )

        if match.kind == "email.send.missing_recipient":
            return "Ach, preciso do endereço de e-mail do destinatário."
        if match.kind == "email.send":
            to = str(match.data.get("to") or "")
            subject = str(match.data.get("subject") or "")
            body = str(match.data.get("text") or "")
            if not subject:
                return f"Ach, tenho o destinatário {to}, mas preciso do assunto do e-mail."
            if not body:
                return f"Ach, tenho destinatário e assunto, mas preciso do texto exato do e-mail para {to}."
            try:
                result = gateway.execute("email.send", {"to": to, "subject": subject, "text": body}, approved=True)
            except Exception as exc:
                return f"Ach, não consegui enviar o e-mail: {exc}"
            self._remember("tool:email.send", result)
            message_id = result.get("id") if isinstance(result, dict) else None
            return f"E-mail aceito pelo provedor para {to}" + (f" · ID {message_id}." if message_id else ".")

        return None
