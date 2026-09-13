from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

import httpx

from .web_research import WebResearchService


class PermissionLevel(str, Enum):
    READ = "green"
    REVERSIBLE = "yellow"
    SENSITIVE = "red"


@dataclass(frozen=True)
class ToolSpec:
    id: str
    name: str
    category: str
    permission: PermissionLevel
    description: str
    configured: bool
    available: bool = True

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["permission"] = self.permission.value
        return payload


class EvolutionClient:
    def __init__(self, base_url: str, api_key: str, instance: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip()
        self.instance = instance.strip()
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.instance)

    def connection_state(self) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Evolution API is not configured")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/instance/connectionState/{self.instance}",
                headers={"apikey": self.api_key},
            )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}

    def send_text(self, number: str, text: str) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Evolution API is not configured")
        number = number.strip().replace("+", "")
        text = text.strip()
        if not number or not text:
            raise ValueError("number and text are required")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/message/sendText/{self.instance}",
                headers={"apikey": self.api_key, "Content-Type": "application/json"},
                json={"number": number, "text": text},
            )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}


class GoogleDriveClient:
    def __init__(self, access_token: str, timeout: float = 20.0) -> None:
        self.access_token = access_token.strip()
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.access_token)

    def search(self, query: str, page_size: int = 10) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Google Drive access token is not configured")
        query = query.strip()
        escaped = query.replace("'", "\\'")
        q = f"name contains '{escaped}' and trashed = false" if query else "trashed = false"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={
                    "q": q,
                    "pageSize": max(1, min(page_size, 50)),
                    "fields": "files(id,name,mimeType,modifiedTime,webViewLink),nextPageToken",
                    "orderBy": "modifiedTime desc",
                },
            )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}


class MetaGraphClient:
    def __init__(self, access_token: str, base_url: str = "https://graph.facebook.com/v26.0", timeout: float = 20.0) -> None:
        self.access_token = access_token.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.access_token)

    def accounts(self) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Meta Graph access token is not configured")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/me/accounts",
                params={
                    "fields": "id,name,tasks,instagram_business_account",
                    "access_token": self.access_token,
                },
            )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}


class GitHubClient:
    def __init__(self, token: str, repository: str = "", base_url: str = "https://api.github.com", timeout: float = 20.0) -> None:
        self.token = token.strip()
        self.repository = repository.strip().strip("/")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def status(self) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("GitHub token is not configured")
        with httpx.Client(timeout=self.timeout) as client:
            user_response = client.get(f"{self.base_url}/user", headers=self._headers())
            user_response.raise_for_status()
            user = user_response.json()
            result: dict[str, Any] = {
                "authenticated": True,
                "login": user.get("login") if isinstance(user, dict) else None,
                "repository": self.repository or None,
            }
            if self.repository:
                repo_response = client.get(
                    f"{self.base_url}/repos/{self.repository}",
                    headers=self._headers(),
                )
                repo_response.raise_for_status()
                repo = repo_response.json()
                if isinstance(repo, dict):
                    result["repo"] = {
                        "full_name": repo.get("full_name"),
                        "private": repo.get("private"),
                        "default_branch": repo.get("default_branch"),
                        "updated_at": repo.get("updated_at"),
                    }
            return result

    def repositories(self, limit: int = 20) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("GitHub token is not configured")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/user/repos",
                headers=self._headers(),
                params={"per_page": max(1, min(limit, 50)), "sort": "updated", "direction": "desc"},
            )
        response.raise_for_status()
        payload = response.json()
        repos = []
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    repos.append(
                        {
                            "full_name": item.get("full_name"),
                            "private": item.get("private"),
                            "default_branch": item.get("default_branch"),
                            "updated_at": item.get("updated_at"),
                        }
                    )
        return {"repositories": repos}


class CloudflareClient:
    def __init__(self, token: str, account_id: str = "", base_url: str = "https://api.cloudflare.com/client/v4", timeout: float = 20.0) -> None:
        self.token = token.strip()
        self.account_id = account_id.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.token)

    @property
    def inventory_configured(self) -> bool:
        return bool(self.token and self.account_id)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    @staticmethod
    def _unwrap(payload: Any) -> Any:
        if isinstance(payload, dict) and "result" in payload:
            return payload.get("result")
        return payload

    def status(self) -> dict[str, Any]:
        if not self.configured:
            raise ValueError("Cloudflare API token is not configured")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}/user/tokens/verify", headers=self._headers())
        response.raise_for_status()
        payload = response.json()
        result = self._unwrap(payload)
        return {
            "authenticated": bool(isinstance(payload, dict) and payload.get("success", True)),
            "account_id_configured": bool(self.account_id),
            "token_status": result.get("status") if isinstance(result, dict) else None,
        }

    def inventory(self) -> dict[str, Any]:
        if not self.inventory_configured:
            raise ValueError("Cloudflare token and account id are required for inventory")
        endpoints = {
            "workers": f"/accounts/{self.account_id}/workers/scripts",
            "d1": f"/accounts/{self.account_id}/d1/database",
            "r2": f"/accounts/{self.account_id}/r2/buckets",
        }
        inventory: dict[str, Any] = {"account_id": self.account_id}
        with httpx.Client(timeout=self.timeout) as client:
            for name, endpoint in endpoints.items():
                try:
                    response = client.get(f"{self.base_url}{endpoint}", headers=self._headers())
                    response.raise_for_status()
                    payload = response.json()
                    result = self._unwrap(payload)
                    if name == "r2" and isinstance(result, dict):
                        values = result.get("buckets", [])
                    else:
                        values = result if isinstance(result, list) else []
                    cleaned = []
                    for item in values[:50]:
                        if isinstance(item, dict):
                            cleaned.append(
                                {
                                    "id": item.get("id") or item.get("uuid") or item.get("name"),
                                    "name": item.get("name") or item.get("id"),
                                }
                            )
                    inventory[name] = {"count": len(cleaned), "items": cleaned}
                except Exception as exc:
                    inventory[name] = {"count": None, "items": [], "error": str(exc)}
        return inventory


class ToolGateway:
    """Permissioned external-tool gateway.

    Green actions are read-only. Yellow actions must remain reversible. Red
    actions require an explicit approved=True signal from the caller. The
    gateway never hides missing credentials or pretends an action succeeded.
    """

    def __init__(self) -> None:
        self.web = WebResearchService()
        self.evolution = EvolutionClient(
            os.getenv("EVOLUTION_API_URL", ""),
            os.getenv("EVOLUTION_API_KEY", ""),
            os.getenv("EVOLUTION_INSTANCE", ""),
        )
        self.drive = GoogleDriveClient(os.getenv("GOOGLE_DRIVE_ACCESS_TOKEN", ""))
        self.meta = MetaGraphClient(
            os.getenv("META_GRAPH_ACCESS_TOKEN", ""),
            os.getenv("META_GRAPH_BASE_URL", "https://graph.facebook.com/v26.0"),
        )
        self.github = GitHubClient(
            os.getenv("GITHUB_TOKEN", ""),
            os.getenv("GITHUB_REPOSITORY", "sercominteligente/hakham-infinity"),
            os.getenv("GITHUB_API_BASE_URL", "https://api.github.com"),
        )
        self.cloudflare = CloudflareClient(
            os.getenv("CLOUDFLARE_API_TOKEN", ""),
            os.getenv("CLOUDFLARE_ACCOUNT_ID", ""),
            os.getenv("CLOUDFLARE_API_BASE_URL", "https://api.cloudflare.com/client/v4"),
        )
        self.meta_publish_configured = bool(
            self.meta.configured
            and (
                os.getenv("META_INSTAGRAM_ACCOUNT_ID", "").strip()
                or os.getenv("META_FACEBOOK_PAGE_ID", "").strip()
            )
        )

    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec("web.search", "Pesquisa Web", "research", PermissionLevel.READ, "Pesquisar a internet pública e retornar fontes atuais", True),
            ToolSpec("whatsapp.status", "WhatsApp Status", "whatsapp", PermissionLevel.READ, "Consultar estado da instância Evolution", self.evolution.configured),
            ToolSpec("whatsapp.send_text", "Enviar WhatsApp", "whatsapp", PermissionLevel.SENSITIVE, "Enviar texto via Evolution API com aprovação explícita", self.evolution.configured),
            ToolSpec("drive.search", "Buscar no Drive", "drive", PermissionLevel.READ, "Pesquisar arquivos no Google Drive", self.drive.configured),
            ToolSpec("social.accounts", "Contas Meta", "social", PermissionLevel.READ, "Listar páginas e Instagram profissional vinculados", self.meta.configured),
            ToolSpec("github.status", "GitHub Status", "devops", PermissionLevel.READ, "Validar autenticação e repositório principal", self.github.configured),
            ToolSpec("github.repositories", "Repositórios GitHub", "devops", PermissionLevel.READ, "Listar repositórios recentes acessíveis ao token", self.github.configured),
            ToolSpec("cloudflare.status", "Cloudflare Status", "cloud", PermissionLevel.READ, "Validar o API token da Cloudflare", self.cloudflare.configured),
            ToolSpec("cloudflare.inventory", "Cloudflare Inventory", "cloud", PermissionLevel.READ, "Listar Workers, D1 e R2 do account configurado", self.cloudflare.inventory_configured),
            ToolSpec("instagram.publish", "Publicar Instagram", "social", PermissionLevel.SENSITIVE, "Publicação via Meta Graph API", self.meta_publish_configured, available=False),
            ToolSpec("facebook.publish", "Publicar Facebook", "social", PermissionLevel.SENSITIVE, "Publicação via Meta Graph API", self.meta_publish_configured, available=False),
        ]

    def summary(self) -> dict[str, Any]:
        items = [spec.as_dict() for spec in self.specs()]
        return {
            "items": items,
            "configured": sum(1 for item in items if item["configured"]),
            "available": sum(1 for item in items if item["available"]),
        }

    def execute(self, tool_id: str, arguments: dict[str, Any] | None = None, *, approved: bool = False) -> dict[str, Any]:
        arguments = arguments or {}
        spec = next((item for item in self.specs() if item.id == tool_id), None)
        if spec is None:
            raise ValueError(f"unknown tool: {tool_id}")
        if not spec.available:
            raise ValueError(f"tool not implemented yet: {tool_id}")
        if not spec.configured:
            raise ValueError(f"tool is not configured: {tool_id}")
        if spec.permission is PermissionLevel.SENSITIVE and not approved:
            raise PermissionError(f"explicit approval required for {tool_id}")

        if tool_id == "web.search":
            return self.web.search(
                str(arguments.get("query", "")),
                int(arguments.get("max_results", self.web.max_results)),
            )
        if tool_id == "whatsapp.status":
            return self.evolution.connection_state()
        if tool_id == "whatsapp.send_text":
            return self.evolution.send_text(str(arguments.get("number", "")), str(arguments.get("text", "")))
        if tool_id == "drive.search":
            return self.drive.search(str(arguments.get("query", "")), int(arguments.get("page_size", 10)))
        if tool_id == "social.accounts":
            return self.meta.accounts()
        if tool_id == "github.status":
            return self.github.status()
        if tool_id == "github.repositories":
            return self.github.repositories(int(arguments.get("limit", 20)))
        if tool_id == "cloudflare.status":
            return self.cloudflare.status()
        if tool_id == "cloudflare.inventory":
            return self.cloudflare.inventory()
        raise ValueError(f"no executor registered for {tool_id}")
