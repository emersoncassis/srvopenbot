# Stack completa de redes sociais (24 agentes)

Pacote `equipe-redes-completa.zip` para importar em qualquer OpenBot: Instagram, Facebook, TikTok, YouTube, LinkedIn, X e WhatsApp,
do orgânico ao tráfego pago, com o estúdio de vídeo e os bots que conectam cada rede.

Importar: Configurações do servidor > Importar > Grok Bot > escolha o zip. Rotinas vêm desligadas.

Gerar de novo (outro dono ou outro líder):

```bash
EQUIPE=equipe_redes REDES_DONO="Nome do dono" python montar.py <fontes> equipe-redes-completa.zip
# com um agente que já existe no OpenBot como chefe de tudo (ex.: Boi do Yago):
EQUIPE=equipe_redes REDES_LIDER=boi REDES_LIDER_NOME=Boi REDES_DONO=Yago python montar.py <fontes> equipe-redes-completa.zip
```

## Cadeia de comando

```
Dono da marca
└─ Head de Social Media
   ├─ Pesquisador de Tendências
   ├─ Inteligência de Mercado
   ├─ Estrategista de Conteúdo
   ├─ Copywriter
   ├─ Social Instagram e TikTok
   ├─ Social YouTube
   ├─ Social LinkedIn e X
   ├─ Gestor de Comunidade
   ├─ Diretor de Criação
   │  ├─ Designer de Peças (IA)
   │  ├─ Editor e Roteirista de Vídeo
   │  └─ Pesquisador de Anúncios
   ├─ Head de Tráfego Pago
   │  ├─ Gestor de Meta Ads
   │  ├─ Gestor de TikTok Ads
   │  ├─ Gestor de Google Ads
   │  └─ Analista de Mensuração
   └─ Engenheiro de Integrações
      ├─ Bot de Integração Instagram
      ├─ Bot de Integração TikTok
      ├─ Bot de Integração YouTube
      ├─ Bot de Integração LinkedIn
      └─ Bot de Integração WhatsApp
```

## Canais

| Canal | Líder | Membros |
|---|---|---|
| Redes Sociais | Head de Social Media | Head de Social Media, Pesquisador de Tendências, Inteligência de Mercado, Estrategista de Conteúdo, Copywriter, Social Instagram e TikTok, Social YouTube, Social LinkedIn e X, Gestor de Comunidade |
| Criação | Diretor de Criação | Diretor de Criação, Designer de Peças (IA), Editor e Roteirista de Vídeo, Pesquisador de Anúncios |
| Tráfego Pago | Head de Tráfego Pago | Head de Tráfego Pago, Gestor de Meta Ads, Gestor de TikTok Ads, Gestor de Google Ads, Analista de Mensuração |
| Integrações | Engenheiro de Integrações | Engenheiro de Integrações, Bot de Integração Instagram, Bot de Integração TikTok, Bot de Integração YouTube, Bot de Integração LinkedIn, Bot de Integração WhatsApp |

## Agentes

| Agente | Função | Responde a | Skills |
|---|---|---|---|
| **Head de Social Media** | Gerente de redes sociais: comanda orgânico, criação, tráfego pago e integrações | Dono da marca | social, social-content-engine, social-media-manager, social-media-analyzer |
| **Pesquisador de Tendências** | Radar do que está em alta e pautas novas toda semana | Head de Social Media | pesquisa-tendencias, marketing-ideas, content-strategy, competitor-profiling, social-media-analyzer |
| **Inteligência de Mercado** | Concorrentes, tendências e estudo de estratégias de marketing | Head de Social Media | competitor-profiling, competitors, reverse-engineer-marketing, competitive-brief, competitive-intelligence |
| **Estrategista de Conteúdo** | Pautas, calendário editorial e funil de conteúdo | Head de Social Media | content-strategy, lead-magnets, content-creation, marketing-ideas |
| **Copywriter** | Textos de anúncios, páginas, posts, e-mails e roteiros | Head de Social Media | copywriting, copy-editing, marketing-psychology, draft-content, brand-review |
| **Social Instagram e TikTok** | Feed, Reels, Stories e TikTok orgânico | Head de Social Media | social, video |
| **Social YouTube** | Canal do YouTube: vídeos longos, Shorts, títulos, thumbnails e SEO | Head de Social Media | video, social, youtube-full |
| **Social LinkedIn e X** | Conteúdo de autoridade no LinkedIn e no X | Head de Social Media | social, x-twitter-growth |
| **Gestor de Comunidade** | Comentários, DMs, reputação e influenciadores | Head de Social Media | community-marketing, influencer-marketing, review-reputation |
| **Diretor de Criação** | Gerente de Criativos: conceitos, testes de criativo e padrão de marca | Head de Social Media | ad-creative, brand-style, brand-guidelines |
| **Designer de Peças (IA)** | Imagens, carrosséis e peças estáticas para redes e anúncios | Diretor de Criação | image, canva-creator |
| **Editor e Roteirista de Vídeo** | Edita de verdade (Remotion, ffmpeg, legenda automática), voz clonada e roteiros de Reels/TikTok/Shorts | Diretor de Criação | estudio-video, clonar-voz, ffmpeg, video-design, text-to-speech, speech-to-text, voice-changer, dubbing, sound-effects, music, video, cinematic-shot-prompting |
| **Pesquisador de Anúncios** | Biblioteca de anúncios, swipe file e análise de criativos | Diretor de Criação | reverse-engineer-marketing, competitor-profiling, ad-creative |
| **Head de Tráfego Pago** | Gerente de Tráfego: verba, canais, metas de CPA/ROAS e auditoria | Head de Social Media | ads, ad-manager, paid-ads, ab-testing |
| **Gestor de Meta Ads** | Campanhas de Facebook e Instagram Ads | Head de Tráfego Pago | ads, ad-creative |
| **Gestor de TikTok Ads** | Campanhas e criativos nativos para TikTok | Head de Tráfego Pago | ads, video |
| **Gestor de Google Ads** | Pesquisa, Performance Max, YouTube e termos de busca | Head de Tráfego Pago | ads |
| **Analista de Mensuração** | Pixel, CAPI, GA4, UTMs, atribuição e relatórios de tráfego | Head de Tráfego Pago | conversion-tracking, attribution, analytics, campaign-analytics |
| **Engenheiro de Integrações** | WhatsApp, Instagram, anúncios, CRM, APIs externas e servidores MCP | Head de Social Media | mcp-server-builder, mcp-oauth-triage, api-design-reviewer |
| **Bot de Integração Instagram** | Conecta e mantém o Instagram: posts, Reels, métricas, DMs e anúncios | Engenheiro de Integrações | browser-automation, mcp-oauth-triage |
| **Bot de Integração TikTok** | Conecta o TikTok: posts, métricas e anúncios | Engenheiro de Integrações | browser-automation, mcp-oauth-triage |
| **Bot de Integração YouTube** | Conecta o YouTube: vídeos, Shorts, métricas e anúncios | Engenheiro de Integrações | browser-automation, mcp-oauth-triage |
| **Bot de Integração LinkedIn** | Conecta o LinkedIn: posts do perfil e da página, métricas e anúncios | Engenheiro de Integrações | browser-automation, mcp-oauth-triage |
| **Bot de Integração WhatsApp** | Conecta e mantém o WhatsApp: número, contatos autorizados e atendimento | Engenheiro de Integrações | browser-automation, mcp-oauth-triage |

## Rotinas (vêm desligadas)

| Agente | Rotina | Quando |
|---|---|---|
| Head de Social Media | Calendário da semana | quinta 15:00 |
| Head de Social Media | Métricas da semana | segunda 09:00 |
| Pesquisador de Tendências | Radar de tendências | quinta 10:00 |
| Head de Tráfego Pago | Checagem diária das campanhas | {"kind": "weekdays", "time": "08:30"} |

## O que conectar depois de importar

- **Provedor de IA** para os agentes (Configurações do servidor > Provedores).
- **Buffer** (Loja > Apps): agenda e publica no Instagram, Facebook, TikTok, YouTube, LinkedIn e X.
- **Contas de cada rede**: os bots de integração guiam a conexão; o WhatsApp precisa de um número dedicado.
- **ElevenLabs** (voz clonada, narração, dublagem): chave `ELEVENLABS_API_KEY`, pedida pelo próprio Editor em campo seguro.
- **ScrapeCreators** (opcional, tendências completas do TikTok e Instagram): chave `SCRAPECREATORS_API_KEY`.
- **Geradores de imagem e vídeo por IA** (opcional): Higgsfield, Runway ou fal, na Loja > Apps.
- **Contas de anúncio** (Meta, TikTok, Google): pelo Head de Tráfego e pelo Engenheiro de Integrações.

O Editor de Vídeo usa o estúdio instalado na imagem do OpenBot da ICTeam (Remotion, ffmpeg, legenda automática).
Em um OpenBot sem essa imagem, ele só escreve roteiros e orienta a edição.
Nenhum agente publica, responde em nome da marca ou gasta verba sem aprovação.
