from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import httpx

from .tool_gateway import PermissionLevel, ToolGateway, ToolSpec
from .web_research import WebResearchService


_INSTALLED = False


def _json(response: httpx.Response) -> dict[str, Any]:
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, dict) else {"result": payload}


def _clean_username(value: str) -> str:
    value = value.strip().lstrip("@").split("/")[0].casefold()
    if not re.fullmatch(r"[a-z0-9._]{1,30}", value):
        raise ValueError("invalid Instagram username")
    return value


@dataclass(frozen=True)
class InstagramAccount:
    key: str
    username: str
    account_id: str
    access_token: str

    @property
    def configured(self) -> bool:
        return bool(self.username and self.access_token)


class InstagramDirectClient:
    """Read-only Instagram API with Instagram Login.

    This client intentionally exposes only profile/media reads for accounts
    explicitly authenticated by the owner. It does not publish, comment,
    message, follow or mutate Instagram state.
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("META_INSTAGRAM_BASE_URL", "https://graph.instagram.com").rstrip("/")
        self.api_version = os.getenv("META_INSTAGRAM_API_VERSION", "v24.0").strip().strip("/")
        self.timeout = 30.0
        self.accounts = self._load_accounts()

    def _load_accounts(self) -> dict[str, InstagramAccount]:
        rows: list[InstagramAccount] = []

        def add(key: str, default_username: str, prefix: str) -> None:
            token = os.getenv(f"{prefix}_ACCESS_TOKEN", "").strip()
            account_id = os.getenv(f"{prefix}_ACCOUNT_ID", "").strip()
            username = os.getenv(f"{prefix}_USERNAME", default_username).strip().lstrip("@").casefold()
            if token:
                rows.append(InstagramAccount(key, username, account_id, token))

        add("ser_comtec", "ser.com.tec", "META_INSTAGRAM_SER_COMTEC")
        add("ser_visual", "ser.com.visual", "META_INSTAGRAM_SER_VISUAL")

        # Backward-compatible single-account slot.
        legacy_token = os.getenv("META_INSTAGRAM_ACCESS_TOKEN", "").strip() or os.getenv("META_GRAPH_ACCESS_TOKEN", "").strip()
        legacy_id = os.getenv("META_INSTAGRAM_ACCOUNT_ID", "").strip()
        legacy_username = os.getenv("META_INSTAGRAM_USERNAME", "").strip().lstrip("@").casefold()
        if legacy_token and not any(item.access_token == legacy_token for item in rows):
            rows.append(InstagramAccount("default", legacy_username, legacy_id, legacy_token))

        return {item.key: item for item in rows}

    @property
    def configured(self) -> bool:
        return any(item.configured for item in self.accounts.values())

    def status(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "mode": "instagram_login_read_only",
            "base_url": self.base_url,
            "accounts": [
                {
                    "key": account.key,
                    "username": account.username or None,
                    "account_id_configured": bool(account.account_id),
                    "token_configured": bool(account.access_token),
                }
                for account in self.accounts.values()
            ],
        }

    def _resolve(self, username: str) -> InstagramAccount | None:
        wanted = _clean_username(username)
        for account in self.accounts.values():
            if account.username and account.username.casefold() == wanted:
                return account
        # If only one account is configured and its username was omitted from
        # .env, allow the API to identify it and verify below.
        configured = [item for item in self.accounts.values() if item.configured]
        if len(configured) == 1 and not configured[0].username:
            return configured[0]
        return None

    def _get(self, account: InstagramAccount, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not account.configured:
            raise ValueError("Instagram account is not configured")
        url = f"{self.base_url}/{self.api_version}/{path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {account.access_token}"}
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(url, headers=headers, params=params or {})
        return _json(response)

    def _profile(self, account: InstagramAccount) -> dict[str, Any]:
        rich_fields = "id,username,name,biography,website,profile_picture_url,followers_count,follows_count,media_count"
        try:
            return self._get(account, "me", {"fields": rich_fields})
        except httpx.HTTPStatusError:
            return self._get(account, "me", {"fields": "id,username"})

    def _media(self, account: InstagramAccount, limit: int) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 25))
        rich_fields = "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,like_count,comments_count"
        try:
            payload = self._get(account, "me/media", {"fields": rich_fields, "limit": limit})
        except httpx.HTTPStatusError:
            payload = self._get(account, "me/media", {"fields": "id,caption,media_type,media_url,permalink,timestamp", "limit": limit})
        data = payload.get("data")
        return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []

    def analyze_owned(self, username: str, media_limit: int = 12) -> dict[str, Any]:
        account = self._resolve(username)
        if account is None:
            raise KeyError(username)
        profile = self._profile(account)
        actual_username = str(profile.get("username") or account.username or "").casefold()
        wanted = _clean_username(username)
        if actual_username and actual_username != wanted:
            raise ValueError(f"configured token belongs to @{actual_username}, not @{wanted}")
        media = self._media(account, media_limit)
        return {
            "source": "instagram_graph_direct",
            "read_only": True,
            "account_key": account.key,
            "profile": profile,
            "media": media,
            "media_count_returned": len(media),
        }

    def analyze(self, username: str, media_limit: int = 12) -> dict[str, Any]:
        username = _clean_username(username)
        try:
            return self.analyze_owned(username, media_limit)
        except KeyError:
            research = WebResearchService()
            return {
                "source": "public_web",
                "read_only": True,
                "warning": (
                    "This Instagram account is not authenticated in HAKHAM. "
                    "Instagram Login does not provide Business Discovery for arbitrary accounts, "
                    "so this result uses public web research only."
                ),
                "username": username,
                "research": research.search(f"Instagram @{username} perfil posts empresa", max_results=8),
            }


def _client(gateway: ToolGateway) -> InstagramDirectClient:
    client = getattr(gateway, "_hakham_instagram_direct", None)
    if client is None:
        client = InstagramDirectClient()
        setattr(gateway, "_hakham_instagram_direct", client)
    return client


def install_instagram_direct_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_specs = ToolGateway.specs
    original_execute = ToolGateway.execute

    def specs(self: ToolGateway) -> list[ToolSpec]:
        client = _client(self)
        items = list(original_specs(self))
        out: list[ToolSpec] = []
        replaced = False
        for item in items:
            if item.id == "instagram.analyze":
                out.append(
                    ToolSpec(
                        "instagram.analyze",
                        "Analisar Instagram",
                        "social",
                        PermissionLevel.READ,
                        "Ler contas Instagram autenticadas; demais perfis usam pesquisa pública. Nunca publica ou altera dados.",
                        True,
                    )
                )
                replaced = True
            else:
                out.append(item)
        if not replaced:
            out.append(ToolSpec("instagram.analyze", "Analisar Instagram", "social", PermissionLevel.READ, "Análise Instagram somente leitura", True))
        if not any(item.id == "instagram.status" for item in out):
            out.append(ToolSpec("instagram.status", "Instagram Status", "social", PermissionLevel.READ, "Verificar contas Instagram configuradas sem expor tokens", client.configured))
        return out

    def execute(self: ToolGateway, tool_id: str, arguments: dict[str, Any] | None = None, *, approved: bool = False) -> dict[str, Any]:
        if tool_id == "instagram.status":
            return _client(self).status()
        if tool_id == "instagram.analyze":
            arguments = arguments or {}
            username = str(arguments.get("username", "")).strip()
            if not username:
                raise ValueError("Instagram username is required")
            return _client(self).analyze(username, int(arguments.get("media_limit", 12)))
        return original_execute(self, tool_id, arguments, approved=approved)

    ToolGateway.specs = specs
    ToolGateway.execute = execute
