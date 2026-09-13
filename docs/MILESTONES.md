# HAKHAM ∞ — Milestones iniciais

## Milestone 000 — Fundação

Status: concluído.

Entregas:
- repositório oficial inicializado;
- arquitetura v0.1 documentada;
- variáveis de ambiente padronizadas;
- regras de segurança básicas para versionamento.

## Milestone 001 — Core + modelo + memória

Status: em validação final.

Objetivo: provar o ciclo completo de conversa com persistência.

Já implementado:
- bootstrap Python e configuração;
- `ModelProvider` e `ModelRouter`;
- Ollama/local;
- OpenAI provider inicial;
- Abacus RouteLLM como motor plugável;
- memória semântica, episódica e de trabalho;
- recuperação híbrida;
- conflito, quarentena, promoção, proveniência e consolidação;
- logging operacional sem conteúdo sensível;
- testes automatizados e GitHub Actions.

Critério de aceite final:
1. usuário envia uma mensagem;
2. Hakham responde por um motor configurado;
3. uma informação relevante é salva em memória;
4. o processo é reiniciado;
5. Hakham recupera a informação corretamente em nova conversa;
6. primeira chamada real RouteLLM é validada quando uma chave local estiver disponível.

Pendência antes de declarar concluído:
- primeira ignição real com credencial local.

## Milestone 001.5 — Propulsion Layer

Status: código base concluído; aguardando primeira ignição real.

Entregas:
- `RouteLLMProvider`;
- consulta de catálogo vivo;
- health check;
- `ModelCapabilityRegistry`;
- recomendação de motor por capacidade;
- chamada de modelo explícito;
- Council Mode limitado e opt-in;
- comandos CLI `/health`, `/models`, `/recommend` e `/council`;
- documentação de setup e independência de fornecedor.

Regra: Abacus fornece propulsão. Identidade, memória, permissões e decisão pertencem ao HAKHAM Infinity.

## Milestone 002 — HAKHAM Control Center

Objetivo: primeira experiência Jarvis utilizável no navegador.

Primeira entrega:
- tela principal com identidade visual HAKHAM Infinity;
- Hakham, sábio ancião cibernético, como presença central;
- saudação e chat funcional;
- status do Core e motores;
- memória relevante e atividade recente;
- projetos/missões prioritárias;
- painel de motores e Council Mode;
- eventos básicos em tempo real.

Fase posterior:
- grafo animado das chamadas entre agentes;
- visualização da Mesa de IAs;
- auditoria visual de ferramentas e permissões.

## Milestone 003 — Voice Loop

Objetivo: conversa por voz ponta a ponta.

Fluxo:
wake word/VAD → STT → Hakham Core → TTS → áudio.

## Milestone 004 — Primeiro multiagente

Objetivo: Hakham delegar uma tarefa ao primeiro agente especializado e consolidar a resposta.

Primeiro candidato: Serafim, por permitir tarefas técnicas verificáveis.

Council Mode de modelos não substitui os agentes. Modelos são motores; agentes têm identidade operacional, ferramentas e escopo próprio.

## Milestone 005 — Tool Gateway

Objetivo: ferramentas com contratos, escopo e níveis de permissão explícitos.

Primeiras ferramentas:
- busca web;
- arquivos;
- GitHub somente leitura.

Escritas e ações destrutivas exigem níveis de permissão superiores e ficam fora da primeira entrega.

## Fora do escopo da v0.1

- trading real;
- pagamentos;
- exclusões automáticas em produção;
- autonomia irrestrita;
- acesso geral a credenciais;
- dezenas de agentes sem necessidade validada.
