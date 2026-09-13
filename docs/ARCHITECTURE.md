# HAKHAM ∞ — Arquitetura v0.1

## Visão

O HAKHAM ∞ será um sistema operacional pessoal de IA, multimodal e multiagente. A arquitetura será híbrida: execução local quando privacidade, latência ou acesso ao dispositivo forem importantes; serviços em nuvem quando escala, disponibilidade ou modelos externos forem necessários.

```text
User / Voice / Web / WhatsApp
            │
            ▼
        Gateway
            │
            ▼
       HAKHAM Core
            │
    ┌───────┼────────┐
    ▼       ▼        ▼
 Memory   Models    Tools
    │       │        │
    └───────┼────────┘
            ▼
      Orchestrator
            │
   ┌────────┼─────────┐
   ▼        ▼         ▼
Serafim  Arcanum    Delta
   │
SER Master / Luna / Shadow / futuros agentes
```

## Camadas

### core/
Responsável por sessão, interpretação de intenção, planejamento, orquestração, ciclo de ferramentas e consolidação de respostas.

### models/
Abstração de modelos. Deve suportar múltiplos provedores sem acoplar o Core a uma API específica. Primeira meta: OpenAI + Ollama/local.

### memory/
Memória conversacional, episódica, semântica e operacional. Toda memória relevante deve possuir origem, data e metadados de confiança quando aplicável.

### agents/
Agentes especializados com identidade funcional, ferramentas permitidas, escopo e nível de autoridade definidos.

### tools/
Ferramentas de busca, arquivos, APIs, código, GitHub, Cloudflare e demais integrações futuras. Ferramentas não devem possuir acesso global por padrão.

### security/
Políticas de execução, classificação de ações, proteção de segredos, sandbox, auditoria e autorização.

### gateway/
Entrada unificada para web, voz, WhatsApp, webhooks e APIs.

### voice/
Pipeline independente de wake word, VAD, STT, TTS e reprodução de áudio.

### web/
HAKHAM Control Center. Futuramente exibirá sessões, memória, ferramentas, agentes e grafo de atividade multiagente em tempo real.

## Modelo de autoridade

- Nível 0 — somente raciocínio, sem ferramentas.
- Nível 1 — consultas e leituras.
- Nível 2 — ações reversíveis e de baixo risco.
- Nível 3 — ações sensíveis que exigem confirmação explícita.
- Nível 4 — ações críticas ou financeiras com políticas específicas e isolamento adicional.

Nenhum agente deve herdar automaticamente todas as permissões do Hakham Core.

## Estratégia OpenJarvis

OpenJarvis será tratado como upstream de referência e potencial fonte de componentes. O objetivo não é copiar toda a árvore do projeto. Cada módulo será avaliado individualmente por utilidade, licença, dependências, maturidade, segurança e custo de manutenção.

## Arquitetura híbrida

Cloudflare e serviços web podem atuar como gateway, autenticação e camada pública. O núcleo que exigir processos persistentes, modelos locais, shell, arquivos do dispositivo ou hardware deve rodar em host adequado, como Linux/WSL2, servidor dedicado ou máquina local.
