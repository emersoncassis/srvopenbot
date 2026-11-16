---
name: pesquisa-tendencias
description: "Pesquisa o que está em alta agora (TikTok, Instagram, YouTube, Reddit, X, notícias) no nicho do cliente e transforma em pautas prontas: gancho, formato, por que agora e referências. Use para radar de tendências, ideias de conteúdo, o que postar, assuntos virais, concorrentes e trends de áudio e formato."
---

# Radar de tendências e pautas novas

Seu trabalho é **trazer conteúdo novo** toda semana, não só reagir a pedidos.

## Fontes e ferramentas

1. **Pesquisa dos últimos 30 dias** (Reddit, YouTube, TikTok, X, Hacker News, web):
   `tendencias "<assunto do nicho>"`. Para o método completo da ferramenta (síntese, comparação, descoberta de trends),
   leia `/opt/ferramentas/last30days/skills/last30days/SKILL.md` e siga, com `SKILL_DIR=/opt/ferramentas/last30days/skills/last30days`.
   TikTok e Instagram completos pedem a chave `SCRAPECREATORS_API_KEY` (peça pelo `openbot.request_api_key`, nunca no chat); sem ela, use o resto.
2. **YouTube** sem chave: `yt-dlp --flat-playlist -J "ytsearch20:<termo>"` (títulos, views, duração) e
   `yt-dlp --skip-download --write-auto-subs --sub-langs pt --sub-format vtt -o /tmp/ref "<url>"` para ler o roteiro de um vídeo que bombou.
3. **Web**: `openbot.web_search` e o navegador (`openbot.browser`) para TikTok Creative Center (hashtags, músicas e criadores em alta, região Brasil),
   Google Trends (Brasil, últimos 7 dias), aba Explorar/Reels do Instagram, Biblioteca de Anúncios do Meta e perfis de concorrentes.
4. **Referência visual**: `baixar-referencia <url>` para o Editor estudar o ritmo de um vídeo (nunca repostar).

## Entrega (radar semanal)

Para cada pauta (traga de 8 a 12, ordenadas pelo potencial):

- **Gancho** (primeira frase falada ou texto na tela, até 12 palavras)
- **Formato** (Reels/TikTok falado, carrossel, tutorial, trend de áudio, bastidor, reação, lista, antes/depois) e rede principal
- **Por que agora** (o dado: views, crescimento, comentários, data comemorativa, notícia) com o link da referência
- **Roteiro em 3 tópicos** e CTA
- **Esforço** (baixo, médio, alto) e se precisa de gravação do dono

Feche com: 3 trends de áudio/formato da semana, 3 assuntos que os concorrentes postaram e performaram, e 1 ideia ousada.

## Regras

- Sempre com fonte: nada de "está em alta" sem número ou link.
- Adapte ao nicho, ao público e ao tom do cliente (salve isso como memória na primeira conversa).
- Descarte trend polêmica, com risco de marca ou que use conteúdo de terceiros sem direito.
- Entregue ao Head de Social Media (ou ao seu gestor), que aprova e passa para o Estrategista, Copy e Editor.
