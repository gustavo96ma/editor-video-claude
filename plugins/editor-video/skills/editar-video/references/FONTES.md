# Origem das referências (vendorizadas em 2026-08-21)

Todas MIT. Reverificar upstream a cada ~3 meses — algoritmo muda.

> ⚠️ **Auditoria de 01/09/2026.** Três números que este arquivo carregava como lastro foram checados e **não têm estudo por trás**: "3s hold ≥60% = 5-10× reach", "share por DM pesa 3-5× mais que like" e "share supera comment ~12:1". Nenhum é erro de digitação — são números fabricados ou mal atribuídos que sustentavam recomendações inteiras, e a mesma lavagem de citação aparece catalogada no relatório `final_report_reel-vertical-b2b-credibilidade-38afaf` (§6.A, seis casos confirmados). Ficam abaixo marcados, não apagados, porque vão ser reencontrados na primeira busca que alguém fizer. **Não usar como régua.**

| Arquivo | Origem | Nota |
|---|---|---|
| `hook-formulas-tiktok.md` | github.com/sergebulaev/tiktok-skills (`references/hook-formulas.md`) | 10 fórmulas de hook em 3 camadas (falado / texto na tela / visual), mapeadas por sinal-alvo. ⚠️ A validação alegada — "corpus de 263 vídeos business, share supera comment ~12:1" — não tem metodologia publicada. **Usar as fórmulas, ignorar o número.** |
| `shorts-playbook.md` | github.com/AgriciDaniel/claude-youtube | Dados YouTube Shorts: completion 70%+ = promoção agressiva; swipe-away <60% = refazer abertura; picos bimodais 13s/60s; loop = replay pesado. Transferível pra Reels com cautela |
| `retention-scripting-guide.md` | github.com/AgriciDaniel/claude-youtube | Retenção e pattern interrupt. ⚠️ Metade é long-form YouTube (CTA em 1min/4min, mid-roll) — pra Reels usar só: hook 0-5s, interrupt a cada 2-3s em shorts, diagnóstico de curva de retenção, princípios MrBeast (entregar a promessa imediatamente, payoff final) |
| `caption-skill.md` | github.com/rediumvex/social-media-caption-generator-claude (criador @theromanknox, 280K IG) | Regras de caption por plataforma, anti-patterns, fórmulas de caption. ⚠️ A "hierarquia de sinais (share DM ~10× like)" é folclore, **e contradiz o ~3-5× que este mesmo arquivo afirmava embaixo** — dois números incompatíveis, nenhum rastreado. Ignorar os dois. |

Complemento de pesquisa própria (ago/2026):
- Instagram lançou linked Reels/Series (ago/2025) — substituto oficial do "part 1" em caption. Série = recurso nativo ao publicar, NUNCA numeração em texto.
- ~~3s hold ≥60% = 5-10× reach (opus.pro)~~ — ⚠️ **FOLCLORE, checado em 01/09: sem estudo citado.** O mesmo vale pro "~1.7s pra prender antes do swipe". Não usar.
- ~40% assiste sem som — legenda queimada obrigatória.
- ~~Share por DM pesa 3-5× mais que like na distribuição de Reels.~~ — ⚠️ **FOLCLORE, checado em 01/09.**

**O que substitui, com fonte (levantado em 01/09/2026):**
- **Fonte primária da plataforma:** `about.instagram.com/blog/announcements/instagram-ranking-explained` (atualizada 31/05/2023) lista 4 sinais de Reels, e **3 deles são inacessíveis a conta nova** (atividade do espectador, histórico com o criador, popularidade de quem publica). Sobra "informação sobre o reel". A janela de gancho de ~3s também é declarada pela plataforma.
- **Régua da própria conta, e a melhor que existe:** o painel de Insights de cada Reel traz o bloco "O que afeta suas visualizações" com o texto literal *"as taxas são listadas em ordem de importância para o alcance"*. A ordem observada é **reels pulados, compartilhamentos, curtidas, salvamentos, repost, comentários**. Isso é ordinal, vem da plataforma e é específico da conta — usar isto no lugar de qualquer múltiplo inventado.
- **Levantamento com N declarado:** Highviz Instagram Reels Report, 346 Reels / 108 contas, atualizado 20/08/2026, reportado em **medianas**. Baseline: 344 views por reel, watch ratio 31,4%, engajamento por view 4,3%. Por estilo de abertura: rosto direto 38,2% de watch ratio e 9,0% de engajamento/view; b-roll ou cinematográfico 27,7% (o pior); silencioso ou só música 48,4% de watch mas 3,3% de engajamento. Split por frame: overlay de texto **sobe** engajamento (7,6% contra 5,7%) e **derruba** watch ratio (36,6% contra 45,8%). O decil superior por engajamento tem presença humana **menor** (41,0 contra 61,3), com clareza visual igual.
- **Encaminhamento:** Berger e Milkman, *Journal of Marketing Research* — o que faz encaminhar é excitação, não valência. Valor prático +30%, raiva +34%, admiração +30%, tristeza −16% (desativadora). O efeito de valor prático **inverte em canal de broadcast público**: favorece envio privado.
- **Curiosidade:** *Scientific Reports*, 06/01/2025, registered report, meta-análise de 8.977 experimentos de headline (arquivo Upworthy). Relação **curvilínea** entre concretude e clique — vago demais perde tanto quanto concreto demais. Derruba "abre loop e não entrega" como regra.
- **Teto de previsibilidade:** Martin, Hofman, Sharma, Anderson e Watts (WWW 2016), 852 milhões de tweets — melhor modelo atinge R² de 0,48; teto teórico ~0,60 com qualidade variando 15%. Roteiro move a média, não produz o viral.
