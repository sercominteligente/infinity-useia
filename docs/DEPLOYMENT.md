# HAKHAM Infinity — Deploy 24/7

O Core foi empacotado para rodar em qualquer host com Docker e volume persistente.

## Arquitetura recomendada

```text
Internet
  |
HTTPS / reverse proxy
  |
HAKHAM Control Center (FastAPI)
  |
Hakham Core + Model Router
  |
SQLite persistente em volume
  |
Abacus RouteLLM / outros motores
```

## Por que não colocar o Core inteiro em um Cloudflare Worker

O HAKHAM usa runtime Python, estado persistente e SQLite local nesta fase. Workers são excelentes para gateway, autenticação, roteamento e borda, mas não são o melhor local para o núcleo persistente atual.

A arquitetura alvo é:

```text
Cloudflare DNS / Access / Gateway
          |
          v
Docker host sempre ligado
          |
HAKHAM Core + memória persistente
```

## Subir com Docker Compose

1. Crie `.env` a partir de `.env.example`.
2. Insira credenciais somente no `.env` do servidor.
3. Para Abacus:

```env
HAKHAM_MODEL_PROVIDER=abacus
HAKHAM_MODEL=route-llm
ABACUS_ROUTELLM_API_KEY=SUA_CHAVE_LOCAL
ABACUS_ROUTELLM_BASE_URL=https://routellm.abacus.ai/v1
```

4. Execute:

```bash
docker compose up -d --build
```

5. O Control Center responderá em:

```text
http://SEU_SERVIDOR:8765
```

## Persistência

O volume `hakham-data` mantém `/app/data/hakham.db` fora do ciclo de vida do container. Rebuilds e reinícios não devem apagar a memória.

## Segurança antes de exposição pública

A porta 8765 não deve ficar aberta diretamente para a internet em produção. Antes de publicar:

- colocar HTTPS/reverse proxy na frente;
- adicionar autenticação ao Control Center;
- limitar origem/acesso;
- manter `.env` fora do Git;
- configurar backups do volume de memória;
- usar Cloudflare Access ou camada equivalente para acesso administrativo.

## Primeira ignição no servidor

Dentro do container/ambiente, valide primeiro o catálogo sem geração e depois faça uma única chamada real:

```bash
hakham-ignite
hakham-ignite --live
```

Depois valide o painel e o chat antes de ativar integrações adicionais.
