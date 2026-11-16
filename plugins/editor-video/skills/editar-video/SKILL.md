---
name: editar-video
description: >
  Edita vídeo (Reels, TikTok, Shorts, YouTube, aula, vlog, tutorial de tela) em ffmpeg no estilo
  pessoal de quem usa, calibrado a partir de vídeos de referência que a pessoa gosta. Na primeira
  vez, faz perguntas e pede 3 links de referência antes de editar. Use quando a pessoa pedir para
  editar, montar, cortar, legendar, transcrever ou finalizar um vídeo, escrever roteiro de vídeo
  curto, "calibrar" ou "recalibrar meu estilo", ou trocar as referências de edição.
---

# Editar vídeo no estilo da pessoa

Esta skill é a porta de entrada. Ela confere o ambiente e as ferramentas, garante que existe um
**perfil de estilo** calibrado e só então chama os agentes do plugin: `editor-video:calibrador-estilo`,
`editor-video:editor-video` e `editor-video:roteirista-reels` (abaixo, citados sem o prefixo).
Fale em pt-BR, de forma simples: a pessoa pode não ser programadora. Quem usa pode ser designer:
respeite o vocabulário dela (fonte, peso, entrelinha, paleta, LUT) e não reduza estilo a números.

Caminhos usados (o diretório base desta skill aparece quando ela carrega; chame-o de `<skill>`):
- Referências técnicas: `<skill>/references/`
- Scripts: `<skill>/scripts/analisar_referencia.py` e `<skill>/scripts/transcrever.py`
- **Pasta da pessoa:** `~/.claude/editor-video/` (fora do plugin, para sobreviver às atualizações).
  No Windows é `C:\Users\<usuário>\.claude\editor-video\`. Dentro dela:
  - `perfil-estilo.md` (o perfil)
  - `referencias/ref1..ref3` (análises)
  - `marca/` (fontes .ttf/.otf, logo, LUT .cube, efeitos sonoros que ela mandar)

## Passo 0: ambiente e ferramentas

**Ambiente.** Se o sistema for Linux sem `winget` nem `brew` e a pasta de trabalho for uma montagem
de outra máquina (sinal de Cowork ou sandbox), pare e explique: "Este editor precisa rodar no
Claude Code (aba Code do app Claude, ou terminal). No Cowork ele não acessa o YouTube nem guarda o
seu estilo." Não siga com a calibração ali.

**Ferramentas.** Rode `ffmpeg -version`, `ffprobe -version` e `yt-dlp --version` (se o último
falhar, tente `python -m yt_dlp --version` e `py -m yt_dlp --version`). Descubra o comando de Python
que existe (`py`, `python` ou `python3`). Confira os filtros do ffmpeg:
- Bash: `ffmpeg -hide_banner -filters | grep -E " (subtitles|ass|drawtext|zscale|lut3d|vidstabdetect) "`
- PowerShell: `ffmpeg -hide_banner -filters | Select-String " (subtitles|ass|drawtext|zscale|lut3d|vidstabdetect) "`

Sem `subtitles` a legenda animada não sai; no Mac isso é o ffmpeg padrão do Homebrew, e a troca é
pelo `ffmpeg-full`.

Se faltar algo, mostre **só o que falta** e ofereça rodar a instalação depois que ela concordar
(no Windows, cada `winget` abre uma janela de permissão do sistema; ela clica em Sim):

| Falta | Windows (PowerShell) | Mac |
|---|---|---|
| ffmpeg completo | `winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements` | `brew install ffmpeg-full` e depois `echo 'export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"' >> ~/.zshrc` |
| yt-dlp | `winget install --id yt-dlp.yt-dlp -e --accept-source-agreements --accept-package-agreements` | `brew install yt-dlp` |
| Python | `winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements` | `brew install python` |
| Git (Windows) | `winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements` | já vem |
| Transcrição | `py -m pip install faster-whisper` | `python3 -m pip install faster-whisper` |

A transcrição só é necessária para legenda; se ela não quiser legenda, pule. Depois de instalar
no Windows, é preciso fechar e abrir de novo o Claude (o app inteiro ou o terminal) para o PATH
novo valer. Se o `yt-dlp` avisar de "JavaScript runtime", instale o Deno
(`winget install --id DenoLand.Deno -e`).

**Permissões.** Na primeira vez, explique uma única vez: "Vou pedir licença para rodar ffmpeg,
ffprobe, yt-dlp e python, que são as ferramentas de vídeo. Pode escolher 'Yes, and don't ask again'
para cada uma." Nunca peça para ela aprovar comando que apague arquivo fora de `editado/_tmp/`.

## Passo 1: perfil existe?

Leia `~/.claude/editor-video/perfil-estilo.md`.
- **Existe** e o pedido não é recalibrar: vá ao Passo 3.
- **Não existe**, ou ela pediu "recalibrar", "trocar referências" ou "mudar meu estilo": faça o
  Passo 2 **antes de qualquer edição**, mesmo que tenha chegado com um vídeo. Explique numa frase:
  "Antes da primeira edição, vou aprender o seu estilo: umas perguntas rápidas e 3 vídeos cuja
  edição você curte."

## Passo 2: onboarding e calibração (primeira vez)

Pergunte em blocos curtos (use a ferramenta de perguntas com opções quando existir; senão, texto).
Não pergunte o que ela já disse, e não pergunte o que dá para medir (resolução, fps: o `ffprobe`
do bruto responde).

1. **O que você mais vai editar e onde publica?** Reels/TikTok/Shorts com rosto, aula ou YouTube
   horizontal, vlog, tutorial com tela gravada, outro. **Como grava?** (celular vertical, câmera,
   tela).
2. **Como você trabalha hoje?** Edita em algum programa (CapCut, Premiere, DaVinci, nenhum)? Quer
   receber o vídeo **pronto**, ou pronto **mais os arquivos editáveis** (legenda .srt, lista de
   cortes) para finalizar no programa dela?
3. **Sua identidade visual** (tudo opcional, pode mandar depois):
   - fontes que usa (o arquivo .ttf/.otf, ou o nome);
   - cores em hex (texto, destaque, fundo);
   - LUT ou preset de cor (.cube);
   - logo em PNG com fundo transparente;
   - pasta de efeitos sonoros que costuma usar.
   Copie o que ela mandar para `~/.claude/editor-video/marca/`.
4. **Fim do vídeo:** nome ou arroba para o card final (pode pular).
5. **Três links** cuja edição ela admira. YouTube e Shorts são o mais garantido; Instagram e TikTok
   costumam funcionar. Para cada um, pergunte **o que ela gosta e em que momento** ("a legenda
   dos 0:05", "a transição dos 0:12"); um print ajuda. Se mandar 2, aceite e avise que o perfil
   fica menos preciso.

Para cada link, rode (troque `python` pelo comando que existe; diga que leva 1 a 2 minutos por vídeo):

```bash
python "<skill>/scripts/analisar_referencia.py" "<link>" "~/.claude/editor-video/referencias/refN" --max-seconds 120
```

O script baixa os 2 primeiros minutos em até 720p e grava `metricas.json` e folhas de quadros em
`frames/`. Se um link falhar (vídeo privado, bloqueio de idade, rede social sem suporte), peça
outro em vez de seguir sem avisar. Falha só na legenda não é falha: a análise segue sem a fala.

Então chame o agente **`calibrador-estilo`** passando: as respostas do onboarding (com o que ela
gosta em cada referência e os momentos citados), as pastas `ref1..ref3`, a pasta `marca/`, o
caminho do perfil a escrever e `<skill>/references/`.

Quando ele terminar:
1. Mostre o **resumo do perfil em até 8 linhas, em linguagem comum** (ex.: "cortes rápidos, um a
   cada 2 segundos; legenda branca em caixa alta, 2 a 3 palavras por vez, destaque em amarelo;
   zoom leve nas frases importantes").
2. Faça as **perguntas da seção "Lacunas"** do perfil (o que os quadros parados não mostram:
   animação da legenda, transições, efeitos sonoros, música). Até 4 perguntas, com opções.
3. Grave as respostas no perfil e pergunte se está certo. Ajustes vão para "Ajustes pedidos".

## Passo 3: trabalho

- **Editar, montar, cortar, legendar, finalizar ou conferir um vídeo** → agente `editor-video`.
  Passe: os caminhos dos brutos, o objetivo do vídeo, o perfil, a pasta `marca/`, `<skill>/scripts/`
  e `<skill>/references/`. A saída vai para uma pasta `editado/` ao lado dos brutos.
  - Na **primeira edição** depois da calibração, peça ao editor uma **prova de estilo de 8 a 10 s**
    (gancho com legenda, um corte, um zoom) antes do vídeo inteiro. Ela aprova ou ajusta, e só então
    o editor renderiza tudo. Isso economiza uso do plano.
  - Com legenda, o editor transcreve e **mostra o texto para ela revisar** antes de queimar.
- **Escrever ou revisar roteiro** de vídeo curto → agente `roteirista-reels`, com o perfil e
  `<skill>/references/`.
- Pedido de ajuste de gosto depois de uma edição ("legenda menor", "menos zoom") → aplique no vídeo
  **e** registre no perfil (seção "Ajustes pedidos", com a data), para valer nas próximas.

Os agentes não conversam com ela: se o editor devolver uma pergunta (texto da transcrição, escolha
entre duas opções), faça a pergunta e passe a resposta adiante.

## Regras

- O original nunca é alterado. Tudo sai em `editado/`.
- Arquivo de vídeo é grande: trabalhe com o caminho, não copie vídeo para dentro do plugin.
- Se ela não souber o caminho, ela pode arrastar o arquivo para a janela do Claude.
- Antes de uma operação demorada (render longo, muitas referências), diga quanto tempo deve levar.
  O plano Pro tem limite de uso: prefira poucas imagens de conferência e respostas curtas.
- Não publique em rede social nem envie arquivo a ninguém: entregue os arquivos e diga onde estão.
- Música de terceiros pode bloquear o vídeo por direitos autorais (Content ID); avise se ela
  pedir trilha comercial.
