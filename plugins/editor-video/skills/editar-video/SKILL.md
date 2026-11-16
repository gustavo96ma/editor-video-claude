---
name: editar-video
description: >
  Edita vídeo (Reels, TikTok, Shorts, YouTube, aula, vlog, tutorial de tela) em ffmpeg no estilo
  pessoal de quem usa, calibrado a partir de vídeos do YouTube que a pessoa gosta. Na primeira vez,
  faz perguntas e pede 3 links de referência antes de editar. Use quando a pessoa pedir para editar,
  montar, cortar, legendar ou finalizar um vídeo, escrever roteiro de vídeo curto, "calibrar" ou
  "recalibrar meu estilo", ou trocar as referências de edição.
---

# Editar vídeo no estilo da pessoa

Esta skill é a porta de entrada. Ela confere as ferramentas, garante que existe um **perfil de
estilo** calibrado e só então chama os agentes do plugin: `editor-video:calibrador-estilo`,
`editor-video:editor-video` e `editor-video:roteirista-reels` (abaixo, citados sem o prefixo).
Fale em pt-BR, de forma simples: a pessoa pode não ser programadora.

Caminhos usados (o diretório base desta skill aparece quando ela carrega; chame-o de `<skill>`):
- Referências técnicas: `<skill>/references/`
- Script de análise: `<skill>/scripts/analisar_referencia.py`
- **Perfil de estilo:** `~/.claude/editor-video/perfil-estilo.md` (fora do plugin, para sobreviver
  às atualizações). No Windows é `C:\Users\<usuário>\.claude\editor-video\perfil-estilo.md`.
- Análises das referências: `~/.claude/editor-video/referencias/ref1`, `ref2`, `ref3`.

## Passo 0: ferramentas

Rode `ffmpeg -version`, `ffprobe -version` e `yt-dlp --version` (se o último falhar, tente
`python -m yt_dlp --version` e `py -m yt_dlp --version`). Descubra o comando de Python que existe
(`python`, `python3` ou `py`). Se faltar algo, **pare** e mostre só o que falta:

| Falta | Windows (PowerShell) | Mac |
|---|---|---|
| ffmpeg/ffprobe | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |
| yt-dlp | `winget install yt-dlp.yt-dlp` | `brew install yt-dlp` |
| Python | `winget install Python.Python.3.12` | `brew install python` |

Depois de instalar no Windows, é preciso fechar e abrir o terminal (e o Claude) para o PATH novo
valer. Não tente instalar sozinho sem a pessoa concordar.

## Passo 1: perfil existe?

Leia `~/.claude/editor-video/perfil-estilo.md`.
- **Existe** e o pedido não é recalibrar: vá ao Passo 3.
- **Não existe**, ou a pessoa pediu "recalibrar", "trocar referências" ou "mudar meu estilo":
  faça o Passo 2 **antes de qualquer edição**, mesmo que ela tenha chegado com um vídeo para editar.
  Explique numa frase: "Antes da primeira edição, vou aprender o seu estilo. São umas perguntas
  rápidas e 3 vídeos do YouTube cuja edição você curte."

## Passo 2: onboarding e calibração (primeira vez)

Pergunte em blocos curtos (use a ferramenta de perguntas com opções quando existir; senão, texto).
Não pergunte o que ela já disse.

1. **O que você mais vai editar?** Reels/TikTok/Shorts com rosto, vídeo de aula ou YouTube
   horizontal, vlog, tutorial com tela gravada, outro.
2. **Onde publica** e **como grava** (celular, câmera, gravação de tela; vertical ou horizontal;
   resolução se souber).
3. **Como você quer aparecer no fim do vídeo?** Nome ou arroba para o card final (pode pular).
4. **Três links do YouTube** cuja edição ela gosta. Para cada um, uma frase opcional: "o que você
   gosta nesse?" (ritmo, legenda, zoom, cor, música, grafismos...). Shorts valem. Se mandar menos de
   3, aceite 2 e avise que o perfil fica menos preciso.

Para cada link, rode (troque `python` pelo comando que existe):

```bash
python "<skill>/scripts/analisar_referencia.py" "<link>" "~/.claude/editor-video/referencias/refN" --max-seconds 180
```

O script baixa só os 3 primeiros minutos em até 720p e grava `metricas.json` e `frames/`. Se um
link falhar (vídeo privado, bloqueio de idade), peça outro em vez de seguir com dois sem avisar.

Então chame o agente **`calibrador-estilo`** passando: as respostas do onboarding (com as frases de
"o que você gosta"), as pastas `ref1..ref3`, o caminho do perfil a escrever e `<skill>/references/`.

Quando ele terminar, mostre à pessoa um **resumo do perfil em até 8 linhas, em linguagem comum**
(ex.: "cortes rápidos, um a cada 2 segundos; legenda grande, amarela, palavra por palavra, no meio
da tela; zoom leve nas frases importantes; música baixa por baixo da voz") e pergunte se é isso ou
se quer ajustar algo. Ajustes vão para o perfil, na seção "Ajustes pedidos".

## Passo 3: trabalho

- **Editar, montar, cortar, legendar, finalizar ou conferir um vídeo** → agente `editor-video`.
  Passe: os caminhos dos arquivos brutos, o objetivo do vídeo, o caminho do perfil e
  `<skill>/references/`. Peça que entregue o arquivo final numa pasta `editado/` ao lado dos brutos,
  nunca sobrescrevendo o original.
- **Escrever ou revisar roteiro** de vídeo curto → agente `roteirista-reels`, com o perfil e
  `<skill>/references/`.
- Pedido de ajuste de gosto depois de uma edição ("legenda menor", "menos zoom") → aplique no vídeo
  **e** registre no perfil (seção "Ajustes pedidos", com a data), para valer nas próximas.

## Regras

- O original nunca é alterado. Tudo sai em `editado/`.
- Arquivos grandes: trabalhe com o caminho, não copie vídeo para dentro de pastas do plugin.
- Antes de uma operação demorada (render longo, muitas referências), diga quanto tempo deve levar.
  O plano Pro tem limite de uso: prefira poucos frames de conferência e respostas curtas.
- Não publique em rede social nem envie arquivo a ninguém: entregue o arquivo e diga onde está.
