from __future__ import annotations

import json
import shlex
from dataclasses import dataclass

from .agents import AgentRegistry
from .tool_gateway import ToolGateway


@dataclass(frozen=True)
class CommandResult:
    handled: bool
    answer: str = ""


class CommandRouter:
    """Deterministic command layer for Hakham's first real tools.

    Only read-only tools execute directly here. Sensitive actions remain behind
    the Tool Gateway approval boundary.
    """

    def __init__(self, runtime_state, agents: AgentRegistry | None = None) -> None:
        self.runtime_state = runtime_state
        self.agents = agents or AgentRegistry()

    def handle(self, message: str) -> CommandResult:
        message = message.strip()
        if not message.startswith("/"):
            return CommandResult(False)

        try:
            parts = shlex.split(message)
        except ValueError as exc:
            return CommandResult(True, f"Comando inválido: {exc}")
        if not parts:
            return CommandResult(False)

        command = parts[0].casefold()
        if command == "/tools":
            return CommandResult(True, self._tools())
        if command == "/wa-status":
            return CommandResult(True, self._whatsapp_status())
        if command == "/drive":
            query = " ".join(parts[1:]).strip()
            return CommandResult(True, self._drive_search(query))
        if command == "/social":
            return CommandResult(True, self._social_accounts())
        if command == "/github":
            action = parts[1].casefold() if len(parts) > 1 else "status"
            return CommandResult(True, self._github(action))
        if command == "/cloudflare":
            action = parts[1].casefold() if len(parts) > 1 else "status"
            return CommandResult(True, self._cloudflare(action))
        if command == "/agent":
            if len(parts) < 3:
                return CommandResult(True, "Uso: /agent <id> <missão>. Ex.: /agent serafim revisar arquitetura do painel")
            agent_id = parts[1]
            task = " ".join(parts[2:])
            return CommandResult(True, self._delegate(agent_id, task))
        if command in {"/wa-send", "/whatsapp-send"}:
            return CommandResult(
                True,
                "Envio de WhatsApp é ação vermelha. Prepare a mensagem no Tool Gateway e confirme explicitamente antes do envio.",
            )
        if command == "/help":
            return CommandResult(True, self.help_text())
        return CommandResult(True, f"Comando desconhecido: {parts[0]}. Use /help.")

    def _state(self):
        return self.runtime_state.state()

    def _tools(self) -> str:
        gateway = ToolGateway()
        lines = []
        for spec in gateway.specs():
            state = "configurada" if spec.configured else "configurar"
            availability = "ativa" if spec.available else "planejada"
            lines.append(f"- {spec.id}: {state}, {availability}, permissão {spec.permission.value}")
        return "Tool Gateway:\n" + "\n".join(lines)

    def _remember_tool_result(self, key: str, result: object, limit: int = 10_000) -> None:
        text = json.dumps(result, ensure_ascii=False, default=str)
        self._state().core.working.set(key, text[:limit])

    def _whatsapp_status(self) -> str:
        gateway = ToolGateway()
        try:
            result = gateway.execute("whatsapp.status")
        except Exception as exc:
            return f"Não consegui consultar o WhatsApp: {exc}"
        self._remember_tool_result("tool:whatsapp.status", result, 7000)
        return self._state().core.ask(
            "Interprete de forma curta o resultado atual da ferramenta WhatsApp Status que está na memória de trabalho. "
            "Diga se a instância parece conectada e destaque qualquer incerteza."
        )

    def _drive_search(self, query: str) -> str:
        gateway = ToolGateway()
        try:
            result = gateway.execute("drive.search", {"query": query, "page_size": 10})
        except Exception as exc:
            return f"Não consegui pesquisar o Drive: {exc}"
        self._remember_tool_result("tool:drive.search", result)
        q_label = query or "arquivos recentes"
        return self._state().core.ask(
            f"A ferramenta Drive Search acabou de consultar: {q_label!r}. "
            "Use exclusivamente o resultado presente na memória de trabalho para resumir os arquivos encontrados. "
            "Não invente arquivos ausentes do resultado."
        )

    def _social_accounts(self) -> str:
        gateway = ToolGateway()
        try:
            result = gateway.execute("social.accounts")
        except Exception as exc:
            return f"Não consegui consultar as contas sociais: {exc}"
        self._remember_tool_result("tool:social.accounts", result)
        return self._state().core.ask(
            "A ferramenta Contas Meta acabou de listar as páginas Facebook e contas profissionais do Instagram vinculadas. "
            "Resuma somente o que aparece no resultado da memória de trabalho. Não exponha tokens e não invente contas."
        )

    def _github(self, action: str) -> str:
        gateway = ToolGateway()
        tool_id = "github.repositories" if action in {"repos", "repositories", "repo"} else "github.status"
        try:
            result = gateway.execute(tool_id, {"limit": 20})
        except Exception as exc:
            return f"Não consegui consultar o GitHub: {exc}"
        self._remember_tool_result(f"tool:{tool_id}", result)
        if tool_id == "github.repositories":
            return self._state().core.ask(
                "A ferramenta GitHub Repositories acabou de listar repositórios acessíveis. "
                "Resuma os repositórios mais relevantes e recentes usando somente o resultado na memória de trabalho."
            )
        return self._state().core.ask(
            "A ferramenta GitHub Status acabou de validar a autenticação e o repositório principal. "
            "Resuma o estado atual usando somente o resultado da memória de trabalho e não exponha credenciais."
        )

    def _cloudflare(self, action: str) -> str:
        gateway = ToolGateway()
        tool_id = "cloudflare.inventory" if action in {"inventory", "inventario", "workers", "storage"} else "cloudflare.status"
        try:
            result = gateway.execute(tool_id)
        except Exception as exc:
            return f"Não consegui consultar a Cloudflare: {exc}"
        self._remember_tool_result(f"tool:{tool_id}", result)
        if tool_id == "cloudflare.inventory":
            return self._state().core.ask(
                "A ferramenta Cloudflare Inventory acabou de consultar Workers, D1 e R2. "
                "Resuma quantidades e nomes relevantes usando somente o resultado da memória de trabalho. "
                "Se algum módulo retornou erro de permissão, diga isso claramente."
            )
        return self._state().core.ask(
            "A ferramenta Cloudflare Status acabou de validar o token. "
            "Resuma o estado da conexão usando somente o resultado da memória de trabalho e não exponha credenciais."
        )

    def _delegate(self, agent_id: str, task: str) -> str:
        agent = self.agents.get(agent_id)
        if agent is None:
            return f"Agente desconhecido: {agent_id}. Disponíveis: " + ", ".join(a.id for a in self.agents.all())
        if agent.role == "orchestrator":
            return "Hakham já é o orquestrador. Delegue a missão para um especialista."
        state = self._state()
        prompt = self.agents.prompt_for(agent.id, task)
        answer = state.core.router.generate(state.core.provider, prompt)
        state.core.working.set(f"agent:{agent.id}", f"{agent.name}: {answer}")
        state.core.episodic.append("tool", f"Delegação para {agent.name}: {task}", session_id=state.core.session_id)
        state.core.episodic.append("tool", f"Resultado de {agent.name}: {answer}", session_id=state.core.session_id)
        return f"{agent.name} respondeu:\n\n{answer}"

    @staticmethod
    def help_text() -> str:
        return (
            "Comandos HAKHAM v0.7:\n"
            "/tools — listar ferramentas e permissões\n"
            "/wa-status — consultar a instância do WhatsApp\n"
            "/drive <busca> — pesquisar arquivos no Google Drive\n"
            "/social — listar páginas Facebook e Instagram profissional vinculados\n"
            "/github [status|repos] — consultar GitHub em modo leitura\n"
            "/cloudflare [status|inventory] — consultar Cloudflare, Workers, D1 e R2 em modo leitura\n"
            "/agent <id> <missão> — delegar para um especialista\n"
            "/wa-send — ação sensível; exige confirmação pelo Tool Gateway"
        )
