# HAKHAM ∞

Personal AI Operating System da SER Comtec.

O HAKHAM ∞ é uma arquitetura de assistente pessoal multimodal e multiagente, projetada para combinar raciocínio, memória persistente, ferramentas, voz, automações e agentes especializados em uma única camada de orquestração.

## Objetivos da v0.1

- Hakham Core
- Model Router
- Memória persistente
- Ferramentas básicas
- Segurança e permissões
- Voz
- Painel web inicial
- Primeiros agentes especializados

## Arquitetura inicial

```text
HAKHAM ∞
│
├── core/        # Orquestração central
├── agents/      # Agentes especializados
├── memory/      # Memória e recuperação de contexto
├── models/      # Roteamento entre modelos
├── tools/       # Ferramentas e integrações
├── voice/       # STT, TTS e wake word
├── gateway/     # APIs, webhooks e canais
├── security/    # Permissões, sandbox e políticas
├── web/         # HAKHAM Control Center
├── tests/       # Testes
└── docs/        # Arquitetura e roadmap
```

## Princípios

1. O HAKHAM ∞ não depende de um único fornecedor de IA.
2. Modelos são motores substituíveis; a inteligência operacional pertence à arquitetura.
3. Memória deve ser estruturada, rastreável e recuperável por contexto.
4. Agentes possuem especialidades, ferramentas e permissões próprias.
5. Ações sensíveis exigem níveis de autoridade e confirmação apropriados.
6. Componentes open source são incorporados seletivamente, nunca por simples cópia de projeto inteiro.

## Primeira execução

Instale o projeto em um ambiente Python 3.11+:

```bash
pip install -e ".[dev]"
```

Copie `.env.example` para `.env` e mantenha credenciais reais somente no ambiente local/servidor.

Para Abacus RouteLLM:

```env
HAKHAM_MODEL_PROVIDER=abacus
HAKHAM_MODEL=route-llm
ABACUS_ROUTELLM_API_KEY=SUA_CHAVE_LOCAL
ABACUS_ROUTELLM_BASE_URL=https://routellm.abacus.ai/v1
```

Valide autenticação e catálogo sem gerar resposta:

```bash
hakham-ignite
```

Faça uma única chamada real de ignição:

```bash
hakham-ignite --live
```

Abra o Control Center:

```bash
hakham-web
```

Então acesse localmente `http://127.0.0.1:8765`.

O painel já expõe status, memória recente, busca de memória, catálogo RouteLLM e chat ligado ao Hakham Core.

## Referências técnicas

O OpenJarvis será tratado como uma das referências e possíveis fundações para componentes do núcleo, memória, agentes, ferramentas e execução local. Outros projetos estudados serão aproveitados apenas quando trouxerem valor técnico real.

## Status

- Milestone 000: concluído.
- Milestone 001: em validação final, aguardando primeira ignição real no ambiente com credencial.
- Milestone 001.5 Propulsion Layer: base implementada.
- Milestone 002 Control Center: primeira fundação executável implementada.
