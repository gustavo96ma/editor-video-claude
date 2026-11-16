# Editor de vídeo para o Claude

Um plugin que transforma o Claude num editor de vídeo que trabalha **no seu estilo**. Na primeira
vez, ele faz algumas perguntas (o que você edita, suas fontes e cores, como quer receber) e pede 3
vídeos cuja edição você admira. Ele baixa um trecho de cada um, mede o ritmo dos cortes, a fala,
o áudio e a cor, olha os quadros e monta o seu perfil de estilo. A partir daí, edita seguindo esse
perfil.

Ele edita com o **ffmpeg**, direto nos seus arquivos. O original nunca é alterado, e o resultado
sai numa pasta `editado/` ao lado dele.

## O que esperar

- **Faz bem:** corte de silêncios e erros, legenda palavra por palavra com a sua fonte e as suas
  cores, zoom nas frases de ênfase, cor (inclusive com o seu LUT), áudio no volume certo para
  redes, card final, e um pacote para você finalizar no seu programa (vídeo sem legenda, legenda
  `.srt` e lista de cortes para Premiere ou DaVinci).
- **Faz com ajuda sua:** animações e transições. Ele não vê movimento nos vídeos de referência,
  então pergunta como você gosta. Na primeira edição ele mostra uma **prova de 8 a 10 segundos**
  antes de fazer o vídeo inteiro.
- **Não faz:** motion design elaborado, grafismos desenhados à mão, trilha sonora. Para isso, use o
  pacote editável no seu programa.
- Gasta uso do plano. Vídeos de até 1 ou 2 minutos rendem mais.

## 0. Tenha o Claude Code

O plugin roda no **Claude Code**, que vem no plano Pro. Use **uma** destas opções:

- **Sem terminal (recomendado):** baixe o app do Claude em https://claude.com/download, entre com a
  sua conta e abra a aba **Code**.
- **Terminal:** siga https://code.claude.com/docs/en/setup.

**Não use o Cowork.** Ele roda isolado: não acessa o YouTube e não guarda o seu estilo.

## 1. Instale as ferramentas (uma vez só)

O jeito mais fácil é colar o pedido abaixo no Claude (aba Code) e deixar ele conferir e instalar o
que falta. Ele vai pedir licença antes de cada comando.

> Confira se este computador tem ffmpeg (versão completa, com libass), yt-dlp, Python e, no
> Windows, Git. Instale o que faltar e depois instale o pacote de transcrição faster-whisper com o
> pip. Me explique cada passo em uma frase.

Se preferir fazer à mão:

**Windows** (PowerShell):

```powershell
winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
winget install --id yt-dlp.yt-dlp -e --accept-source-agreements --accept-package-agreements
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
py -m pip install faster-whisper
```

**Mac** (Terminal, com o [Homebrew](https://brew.sh)):

```bash
brew install ffmpeg-full yt-dlp python
echo 'export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"' >> ~/.zshrc
python3 -m pip install faster-whisper
```

Depois de instalar, **feche o Claude inteiro e abra de novo** (no Windows, isso faz ele enxergar os
programas novos).

## 2. Instale o plugin

**No app (aba Code):** digite `/plugin` e aperte Enter. Vá em **Marketplaces**, adicione
`gustavo96ma/editor-video-claude`, depois instale o **editor-video**. Na pergunta de onde instalar,
escolha **para você (user scope)**, não "só este projeto".

Ou digite estas duas linhas, uma de cada vez:

```
/plugin marketplace add gustavo96ma/editor-video-claude
/plugin install editor-video@editor-video-claude
```

Se aparecer "Run /reload-plugins", digite `/reload-plugins`.

## 3. Use

**Antes da primeira vez, separe 3 links** de vídeos cuja edição você admira (YouTube e Shorts são
o mais garantido; Instagram e TikTok costumam funcionar) e, se tiver, os arquivos das suas fontes,
as cores em hex, o seu LUT e o seu logo.

Abra a **pasta dos seus vídeos**:
- **App:** na aba Code, escolha a pasta ao iniciar a sessão.
- **Terminal no Windows:** no Explorador de Arquivos, abra a pasta, clique com o botão direito num
  espaço vazio, escolha **Abrir no Terminal** e digite `claude`.

Peça normalmente (pode arrastar o arquivo para a janela em vez de digitar o nome):

> edita esse vídeo para Reels: gravacao1.mp4

**Permissões:** o Claude pede licença para rodar programas como `ffmpeg`, `ffprobe`, `yt-dlp` e
`python`. São as ferramentas de vídeo. Escolha **"Yes, and don't ask again"** para cada uma, e ele
para de perguntar.

Na **primeira vez**, antes de editar, ele pergunta o que você edita, como gosta de receber, sua
identidade visual e os 3 links. Ele analisa os vídeos, mostra um resumo ("cortes rápidos, legenda
em caixa alta com destaque amarelo...") e faz 2 a 4 perguntas sobre o que não dá para ver em
quadros parados (animação, transições, som). Antes de queimar a legenda, ele mostra a transcrição
para você corrigir.

Outros pedidos que funcionam:
- "a legenda ficou grande, diminui", e ele grava o ajuste no perfil para as próximas;
- "me manda também a versão sem legenda e o .srt";
- "recalibra meu estilo com esses vídeos novos";
- "escreve um roteiro de Reels sobre ...".

O perfil fica em `~/.claude/editor-video/perfil-estilo.md` (no Windows,
`C:\Users\<você>\.claude\editor-video\perfil-estilo.md`). Você pode abrir e editar à mão.

## Atualizar

Digite `/plugin`, vá em **Marketplaces**, escolha `editor-video-claude` e clique em **Update**.
Para receber as atualizações sozinha, ative **Enable auto-update** ali mesmo.

## Créditos

As referências de roteiro (fórmulas de gancho, retenção, legendas) incluem material de terceiros
sob licença MIT. Veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
