# HAKHAM Voice Loop v0.1

## Objetivo

Dar ao Control Center um primeiro ciclo de voz funcional sem adicionar uma API de voz paga nesta fase.

Fluxo atual:

```text
Ach fala
  -> reconhecimento de voz do navegador (pt-BR)
  -> campo de mensagem
  -> HAKHAM Core
  -> motor configurado (Astra/Auto/Conselho)
  -> resposta textual
  -> síntese de voz do navegador
  -> Hakham volta ao estado de espera
```

## Estados visuais

O avatar provisório do Hakham reage a quatro estados:

- `idle`: em espera
- `listening`: ouvindo o Ach
- `thinking`: aguardando resposta do Core
- `speaking`: reproduzindo a resposta por voz

A interface usa anéis, brilho e waveform para deixar o estado visível mesmo sem áudio.

## Segurança e privacidade

- O código do HAKHAM não envia o áudio bruto para o backend nesta versão.
- O reconhecimento e a síntese são gerenciados pelas APIs de voz do navegador.
- Dependendo do navegador e do sistema operacional, o próprio navegador pode usar serviços remotos do fornecedor. Portanto, esta versão não deve ser descrita como voz 100% local.
- O microfone só é solicitado após ação explícita do usuário.
- Não existe nova chave de API de voz no `.env`.

## Compatibilidade

A interface detecta em runtime:

- `SpeechRecognition` ou `webkitSpeechRecognition` para entrada de voz.
- `speechSynthesis` para saída de voz.

Quando algum recurso não está disponível, o painel marca o Voice Loop como parcial e mantém o chat por texto funcionando.

## Próxima etapa

1. Testar reconhecimento pt-BR no Chrome do ambiente real do Ach.
2. Escolher a voz pt-BR mais adequada disponível no sistema.
3. Substituir o avatar provisório pelo asset oficial aprovado do Hakham.
4. Sincronizar a imagem com os estados `listening`, `thinking` e `speaking`.
5. Avaliar uma camada de STT/TTS dedicada apenas se a qualidade do navegador não for suficiente.
