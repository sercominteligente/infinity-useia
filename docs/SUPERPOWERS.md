# HAKHAM Infinity: busca, avatar e utilitários

## Instalação e acesso

Esta entrega é uma extensão do Control Center v20, não uma substituição do chat. Foi publicada na branch `upgrade/superpowers-avatar-search`; não altera a branch principal nem faz deploy no servidor automaticamente.

No clone local, com alterações pessoais já salvas:

```bash
git fetch origin
git switch --track origin/upgrade/superpowers-avatar-search
pip install -e ".[dev]"
python -m pytest tests/test_superpowers.py
hakham-web
```

Se a branch local já existir, use `git switch upgrade/superpowers-avatar-search`. Mantenha seu `.env` local. Nenhuma credencial nova é necessária para este painel. Para o chat, continuam valendo as credenciais anteriores.

Abra http://127.0.0.1:8765/superpowers ou clique em **Superpoderes: busca + avatar** no painel principal. Pare e reinicie o processo antigo antes de iniciar a versão nova. A porta padrão permanece 8765.

## Ferramentas

| Ferramenta | Como acessar | O que faz |
|---|---|---|
| Pesquisa ampliada | Campo de pesquisa > Pesquisar | Consulta pública sem API paga adicional |
| Fontes e documentação | Seletor de modo | Três consultas em paralelo, incluindo documentação e estudos |
| Comparar alternativas | Seletor de modo | Três consultas com vantagens, limitações e alternativas |
| Exportação de evidências | Exportar pesquisa .md | Salva consulta, data de coleta, trechos e URLs |
| Avatar com áudio | Escolher arquivo > Play | Mede energia do áudio e anima a abertura da boca |
| Leitura de texto | Colar texto > Ler texto | Usa as vozes disponíveis no navegador e animação aproximada |
| Ditado | Ditar | Solicita microfone e transcreve para o campo de texto, quando suportado |
| Pergunta por voz | Ditar > Usar na busca > Pesquisar | Permite conferir o texto antes de consultar |
| Notas | Salvar localmente / Baixar .txt | Armazenamento manual neste navegador e exportação |
| JSON | Validar e formatar | Validação e indentação local, sem executar conteúdo |

## Escopo e limitações importantes

- Avatar procedural 2D com olhos animados. O áudio usa análise real de intensidade, NÃO visemas/fonemas, captura facial ou personagem 3D. Música e ruído também movimentam a boca.
- A leitura de texto tem animação aproximada durante a fala. Para voz do chat, cole a resposta no campo de leitura; não há captura automática das respostas do chat nesta versão.
- Arquivos de áudio não são enviados ao servidor. Voz sintetizada e reconhecimento de fala podem depender de serviços do navegador. O microfone só é solicitado por ação explícita.
- Respeita a preferência de movimento reduzido, desativando os movimentos faciais.
- A pesquisa reaproveita o adaptador público DuckDuckGo já existente; pode retornar vazio por bloqueio do provedor. Não promete cobertura completa, notícias em tempo real ou verificação de fatos.
- O modo fontes usa variantes de consulta: não é garantia de que todo resultado seja oficial ou científico.
- Esta pesquisa não invoca Gemini/Abacus nem substitui a busca que já existia no chat. Não há novas cobranças de API pelo painel; serviços de voz do navegador têm políticas próprias.
- Sem busca arbitrária do conteúdo das páginas, execução de comandos ou ações em contas externas. Conteúdo externo é exibido como texto, não HTML executável.
- URLs duplicadas são combinadas por ranking recíproco. Caminhos e parâmetros das URLs são preservados para não fundir documentos diferentes.
- Até duas pesquisas simultâneas por processo e três consultas por pesquisa; excesso recebe 429. Isso não substitui autenticação, limite por usuário ou proteção de produção.
- Execute em 127.0.0.1. Não publique diretamente na internet; para acesso remoto, configure autenticação, HTTPS e limitação de requisições no proxy. As rotas novas não implementam login próprio.
- Notas ficam em localStorage sem criptografia. Não coloque senhas ou dados sensíveis ali.

## Validação antes de integrar à branch principal

Os testes adicionados usam mocks, não dependem de credenciais nem fazem buscas reais. Eles cobrem URLs, combinação e deduplicação, consultas, validação HTTP, erro sanitizado, liberação de capacidade e entrega do painel. Precisam ser executados no seu ambiente; não foram executados durante a edição remota.

```bash
python -m pytest tests/test_superpowers.py
python -m pytest
```

Teste manualmente no navegador: busca simples e ampliada, fontes clicáveis, exportação, arquivo de áudio com pausas, pausa/retomada, voz em português, interrupção, ditado permitido e negado, movimento reduzido, notas e JSON inválido. Confirme também que chat, voz e demais funções antigas continuam funcionando.

## Reversão

Pare o servidor, volte à sua branch anterior com `git switch -`, reinstale com `pip install -e ".[dev]"` e reinicie `hakham-web`. Esta versão não altera banco de dados nem requer migração.
