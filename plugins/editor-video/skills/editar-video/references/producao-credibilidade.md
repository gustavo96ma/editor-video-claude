# Produção e credibilidade em vídeo vertical — números operacionais

Origem: pesquisa de 22/08/2026 (148 fontes, 6 investigações de profundidade, 4 críticos
adversariais), feita para Reels com rosto e captura de tela editados em ffmpeg. O foco original
era credibilidade B2B; as partes de captura, voz, áudio, legenda e abertura valem para qualquer
vídeo falado. O estilo visual (ritmo, legenda, cor) vem do perfil de estilo da pessoa, não daqui.

Este arquivo cobre **captura e credibilidade** — câmera, luz, voz, áudio, legenda, abertura,
duração e o que faz um comprador B2B confiar. Complementa `hook-formulas-tiktok.md` (fórmulas de
hook) e `caption-skill.md` (caption por plataforma), que continuam valendo.

Todo número abaixo vem com N ou fonte. Onde não vem, está marcado como convenção de ofício.

---

## 1. Distância de câmera e punch-in

- **~1 m já resolve.** Rosto medido a 1,35 m contra 0,45 m é julgado mais confiável, competente e
  atraente. O efeito replica com deformação sintética pura, sem trocar de pessoa nem de
  enquadramento — é geometria de perspectiva, não composição. A 1 m sobra ~0,8% de distorção nasal
  residual contra ~3,7% a 45 cm; ~83% do ganho geométrico já está capturado. Recuar além disso rende
  pouco.
- **Punch-in digital é opticamente inerte.** Recortar e escalar em pós não reintroduz distorção de
  perspectiva — a geometria foi congelada na captura. No iPhone 14 Pro o próprio "2×" nativo é
  recorte do sensor Fusion, não outra lente.
- **Regra operacional: gravar longe, fechar na edição, sempre partindo do master 4K.** Um crop de
  1080×1920 sobre fonte 2160×3840 não perde resolução.

## 2. Luz e fundo

- **Olhar vale ~25× mais que luz.** No mesmo modelo experimental (Mattavelli et al. 2022, n=98):
  olhar direcionado ao observador dá χ²(1)=829,03 sobre confiabilidade percebida; iluminação dá
  χ²(2)=31,42, p<0,001. Ambos são reais; a magnitude não é comparável.
- **A alavanca barata é adesivo colorido marcando a lente**, não equipamento de luz. Olhar na lente,
  não na própria imagem na tela.
- **Rembrandt (key suave a ~45°) acima de luz chapada; luz partida é pior que chapada.** Existe faixa
  cega de 0 a 30° — girar a fonte 20° não muda nada. Acima de 60° a percepção piora.
- **Fundo com profundidade** (estante, plantas) pontua acima de fundo doméstico genérico ou parede
  nua.

## 3. Voz — o que realmente move atitude

Van Zant e Berger, 188 gravações, 2.903 avaliadores:

| Pista vocal | β | Significância |
|---|---|---|
| Volume | .09 | **significativo** |
| Variação de volume | .06 | **significativo** |
| Altura tonal | .02–.04 | não significativo |
| Entonação | .02–.04 | não significativo |
| Taxa de articulação | .02–.04 | não significativo |
| Pausas | .02–.04 | não significativo |

Leitura: as pessoas fazem as sete coisas quando tentam persuadir; **só duas funcionam**. Direção de
performance deve pedir variação de energia, não "fala mais devagar" nem "varia a entonação".

**Consequência para a cadeia de áudio:** compressão agressiva (ex. `acompressor` a 2,5:1 com limiar
baixo) achata exatamente a variação de volume — a única alavanca gratuita. Subir o limiar nos trechos
de ênfase.

## 4. Ritmo de fala

- **Fala lida em pt-BR roda 352–415 sílabas/min** (duas fontes independentes: 352–374 e 372–416).
- **Não comparar narração roteirizada contra fala espontânea.** É a régua errada, e o desvio aparente
  é artefato de comparador.
- Onde o ritmo importa de verdade: **pausa antes e depois do momento de alto envolvimento** (a regra,
  a conclusão, o número). 0,5–0,8 s antes da regra, 0,3–0,5 s antes da conclusão. Convenção de ofício
  com racional — não medido.

## 5. Áudio de captura

- **Boca a 15–30 cm do microfone** (cinco fontes independentes).
- **Reverberação captada na origem não volta atrás em pós.** É a única decisão de áudio
  verdadeiramente irreversível — tratar antes de gravar, não depois.
- **−14 LUFS é decisão defensável, não norma verificada.** `LRA=11` é inoperante em peça abaixo de
  1 minuto.

## 6. Legenda e texto na tela

- **A legenda muda por tipo de plano:**
  - sobre **rosto** — verbatim ajuda;
  - sobre **screencast denso** — palavra-chave. Verbatim ali **prejudica**; é o único caso com dano
    documentado, por competição de canal visual.
- **Teto de camadas de texto simultâneas.** Quatro camadas ao mesmo tempo (texto nativo da tela
  capturada + rótulos + legenda queimada) satura. Contar as camadas por frame, não por elemento
  adicionado.
- **Zona segura — as fontes divergem, declare a escolha.** Uma fonte marca os 280 px inferiores como
  zona de perigo; outra recomenda evitar os 20–25% inferiores (384–480 px em 1920). Medir a base real
  do bloco de legenda no arquivo publicado, não confiar no preview do editor.
- **Identificação do falante precisa ser legível.** Arroba/nome no card final com contraste real e
  ≥1,5 s na tela. A peça precisa dizer quem fala.

## 7. Abertura — estilo por watch ratio

Dataset de 346 Reels, 108 contas, por **estilo de abertura**:

| Estilo | Watch ratio | Engajamento |
|---|---|---|
| Rosto direto para a câmera | **38,2%** | 9,0% |
| B-roll / cinematográfico | **27,7%** (pior do conjunto) | — |

Screencast de abertura é estruturalmente b-roll. **Recomendação híbrida:** manter o screencast como
prova imediata, mas trazer o rosto para **antes de 1,5 s** — ou compor o rosto em canto sobre a
rolagem já no primeiro segundo.

Ressalva de transferência: o dataset é de contas com rosto disponível. Série 100% animada (Manim) não
está no escopo desse recorte — ver conflito registrado no agent `reel-roteirista-manim`.

## 8. Duração — a contradição se dissolve na métrica

| Fonte | Base | Métrica | Pico |
|---|---|---|---|
| Socialinsider | 6M Reels | engajamento e mediana de views (10.374) | **45–60 s** |
| Highviz | 346 Reels, 108 contas | watch ratio | **<15 s** |

**Não é conflito — são métricas diferentes.** Declare a métrica-alvo antes de escolher a duração. Se
o alvo é alcance frio por compartilhamento, o corte sai do bloco de problema, não do bloco de prova.

**Ninguém mediu compartilhamento contra duração** — dez fontes checadas, bases de 6 e 24 milhões de
posts. E compartilhamento é o sinal nº 1 declarado pela Instagram para Reels. **A Instagram passou a
expor Taxa de Compartilhamento no Insights por volta de abril de 2026** — a própria série vira a
régua que a literatura não tem.

## 9. Credibilidade B2B sem prova social

- Estudo com 850+ tomadores de decisão B2B brasileiros: **competência percebida pesa mais que
  preço**, e o construto de desconfiança medido é **exagero não verificável**, não fraude.
- **58% citam aparência visual amadora** como gatilho de suspeita — medido em nível de **perfil e
  identidade visual**, não de transação. Não estender números brasileiros de medo de golpe a
  conteúdo orgânico B2B; o escopo não transfere.
- **Fechar visualmente uma evidência que está logicamente aberta é a falha que custa cliente.** Usar
  um proxy (contagem de avaliações, ausência aparente de um elemento na tela) para afirmar conclusão
  categórica é exatamente o construto medido. Se a evidência mostrada não fecha o argumento, a
  narração não pode fechar.
- **Anonimização parcial não compra nada.** Tarja em um plano com o mesmo dado legível em outro plano
  paga o custo de censura visível sem entregar a proteção. Ou protege em toda a peça, ou não protege.
- **Fluência perceptual é multiplicador condicional.** Polir é ganho direto em toda a peça —
  **exceto** onde o polimento está fechando evidência aberta: o multiplicador é anulado quando o
  espectador identifica de onde vem a facilidade (Whittlesea, Jacoby e Girard). Ordem de operações,
  não escolha entre polir e não polir.
- **Informalidade de cenário ≠ descuido de execução.** No próprio material da Meta, cenário informal
  vence em engajamento, mas produção de estúdio vence reconhecimento de marca em 97% das vezes.

## 10. Higiene de fonte neste campo (obrigatória)

**Seis casos de lavagem de citação confirmados por verificação direta.** Nesta literatura, rastrear a
origem de cada número antes de usá-lo não é preciosismo. Números que circulam e **não existem na
fonte que os nomeia**:

- "2,25× de alcance dos Reels" — ausente do relatório Socialinsider que é citado como fonte;
- "limiar de 70% de completion" — ausente do artigo Buffer citado;
- "63%" e "71%" atribuídos ao mesmo estudo sem link, no mesmo artigo;
- "pico de 25% de unfollow acima de 7 posts/semana" — **contradito** pelo próprio dataset de 2,1M
  posts do Buffer;
- estatística de recall de anúncio atribuída à Meta ("1,0 unidade de lift, 1,1 milhão de anúncios,
  junho–julho de 2021") — **não existe no texto da Meta**.

Se um número não tem N e fonte primária conferida, ele não entra no roteiro nem na justificativa de
uma decisão de produção.
