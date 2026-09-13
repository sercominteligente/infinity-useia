# HAKHAM Infinity — sequência de integrações externas

Esta sequência entra depois da consolidação visual da v0.15 Open Core.

## Princípios obrigatórios

- Toda ação que cause efeito externo deve exigir autorização explícita do Ach no momento da execução.
- Credenciais ficam em `.env` ou cofre apropriado, nunca em prompt, memória conversacional ou frontend.
- Leitura e escrita devem ter permissões separadas sempre que o serviço permitir.
- Logs devem registrar intenção, ferramenta, alvo, resultado e erro sem gravar segredos.
- O Hakham não deve afirmar que executou uma ação se não houver confirmação técnica da ferramenta.

## 1. WhatsApp — mensagens e ligações sob solicitação

Objetivo: permitir que o Hakham envie mensagens e inicie ligações quando solicitado pelo Ach.

Regras:
- envio de mensagem exige confirmação explícita antes da chamada da Evolution;
- mostrar destinatário e conteúdo antes de enviar quando a intenção puder gerar ambiguidade;
- ligação exige confirmação explícita separada;
- detectar sessão degradada da Evolution/Baileys antes de ações sensíveis;
- nunca repetir automaticamente uma ação de efeito externo quando o resultado for incerto.

## 2. Google Drive — acesso ao Drive compartilhado

Objetivo: permitir pesquisa e leitura dos projetos e arquivos compartilhados com o Hakham quando solicitado.

Fase inicial:
- listar e pesquisar arquivos;
- ler conteúdo e metadados;
- baixar/analisar arquivos quando necessário.

Escrita, criação, edição, movimentação e exclusão ficam bloqueadas até uma fase posterior com confirmação explícita.

## 3. GitHub — acesso aos projetos

Objetivo: permitir que o Hakham abra o projeto solicitado, leia arquitetura, encontre arquivos e proponha ou aplique alterações autorizadas.

Regras:
- leitura pode ser direta quando solicitada;
- qualquer commit, criação, edição ou exclusão deve ser claramente apresentada como ação externa;
- operações destrutivas ou irreversíveis exigem confirmação explícita;
- preferir mudanças pequenas e testáveis, preservando histórico.

## 4. Instagram — análise e pesquisa somente

Objetivo: analisar presença digital, conteúdo, posicionamento, frequência, identidade e oportunidades.

Nesta fase:
- somente leitura, pesquisa e análise;
- nenhuma publicação, comentário, direct, exclusão ou edição;
- separar fatos observados de inferências estratégicas.

## 5. Webcam — visão local sob comando

Objetivo: permitir visão em tempo real ou captura pontual quando o Ach ativar explicitamente.

Regras:
- webcam desligada por padrão;
- indicador visual inequívoco quando estiver ativa;
- nenhuma captura oculta;
- memória visual só é criada quando a política de captura permitir;
- botão físico/lógico de parar visão imediatamente.

## 6. E-mail — leitura e envio sob solicitação

Objetivo: permitir que o Hakham componha e envie e-mails depois de validação do Ach.

Regras:
- mostrar destinatários, assunto, corpo e anexos antes de enviar;
- envio exige confirmação explícita;
- anexos devem ser validados;
- nenhum disparo em massa nesta primeira fase;
- registrar confirmação técnica do provedor.

## Próxima etapa

Depois dessas seis integrações, conectar produtos do ecossistema SER, começando por SERhub e SER IA Master, usando APIs e permissões separadas por produto.
