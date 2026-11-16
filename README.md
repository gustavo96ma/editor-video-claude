# Editor de vídeo para o Claude Code

Um plugin que transforma o Claude Code num editor de vídeo que trabalha **no seu estilo**. Na
primeira vez, ele faz algumas perguntas e pede 3 vídeos do YouTube cuja edição você gosta. Ele
baixa um trecho de cada vídeo e mede o ritmo dos cortes, a legenda, o zoom, a cor e o áudio. Com
isso, monta o seu perfil de estilo e passa a editar seguindo esse perfil.

Ele edita com o **ffmpeg**, direto nos seus arquivos, sem programa de edição. O arquivo original
nunca é alterado, e o resultado sai numa pasta `editado/` ao lado dele.

O plugin traz três peças:
- **editor-video:** monta, corta silêncios, legenda, aplica zoom, cor e áudio, e confere o arquivo final.
- **roteirista-reels:** escreve e revisa roteiros de vídeo curto (Reels, TikTok, Shorts).
- **calibrador-estilo:** lê os vídeos de referência e escreve o seu perfil de estilo.

## 1. Instale as ferramentas (uma vez só)

**Windows** (abra o PowerShell):

```powershell
winget install Gyan.FFmpeg
winget install yt-dlp.yt-dlp
winget install Python.Python.3.12
```

Depois, feche e abra o terminal de novo.

**Mac** (Terminal, com o [Homebrew](https://brew.sh)):

```bash
brew install ffmpeg yt-dlp python
```

O plugin precisa do **Claude Code**, que vem incluído no plano Pro. Funciona no terminal ou no app
desktop do Claude, na aba Code. Instruções em https://docs.claude.com/claude-code.

## 2. Instale o plugin

Dentro do Claude Code, digite:

```
/plugin marketplace add gustavo96ma/editor-video-claude
/plugin install editor-video@editor-video-claude
```

Depois, reinicie o Claude Code.

## 3. Use

Abra o Claude Code na pasta onde estão os seus vídeos e peça normalmente, por exemplo:

> edita esse vídeo para Reels: gravacao1.mp4

Na **primeira vez**, antes de editar, ele vai perguntar:
1. que tipo de vídeo você mais edita e onde publica;
2. como você grava;
3. o nome ou arroba para o fim do vídeo (pode pular);
4. **3 links do YouTube** com edição que você curte, e, se quiser, o que você gosta em cada um.

Ele analisa os vídeos, mostra um resumo do estilo ("cortes rápidos, legenda amarela palavra por
palavra no meio da tela...") e pergunta se está certo. A partir daí, toda edição segue esse perfil.

Outros pedidos que funcionam:
- "a legenda ficou grande, diminui", e ele grava o ajuste no perfil para as próximas;
- "recalibra meu estilo com esses vídeos novos";
- "escreve um roteiro de Reels sobre ...".

O perfil fica em `~/.claude/editor-video/perfil-estilo.md`. No Windows, o caminho é
`C:\Users\<você>\.claude\editor-video\perfil-estilo.md`. Você pode abrir e editar à mão.

## Bom saber

- Analisar vídeo e renderizar gasta uso do plano. Vídeos curtos, de até 1 ou 2 minutos, rendem
  mais. Os vídeos de referência são baixados só nos 3 primeiros minutos, em até 720p.
- Para atualizar o plugin, use `/plugin marketplace update editor-video-claude`.
- As referências técnicas de roteiro (fórmulas de gancho, retenção, legendas) incluem material de
  terceiros sob licença MIT. Veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
