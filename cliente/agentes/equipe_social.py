# -*- coding: utf-8 -*-
"""Equipe de redes sociais (Instagram, TikTok, YouTube): um OpenBot só de postagem e conteúdo.

O Head de Social Media é o agente principal (a pessoa fala com ele). Reaproveita os agentes da equipe comercial
e os bots de integração da TI, com a cadeia de comando ajustada. O resto continua na Loja.
"""
import equipe as _com, equipe_ti as _ti

TZ = "America/Sao_Paulo"
CANAL_DIRETORIA = False
EXTERNOS = {}
DONO = "Yago"

AREAS = {"social": ("Redes Sociais", "Postagens, Reels, TikToks, YouTube/Shorts, roteiros, peças e métricas.")}

def _pega(eq, chave, chefe, foco_extra=""):
    a = next(x for x in eq.EQUIPE if x[0] == chave)
    k, nome, cargo, _area, _chefe, personas, skills, foco = a
    return (k, nome, cargo, "social", chefe, personas, skills, foco + foco_extra)

EQUIPE = [
    ("head-social", "Head de Social Media", "Agente principal: fala com o Yago e comanda a equipe de redes sociais",
     "social", None,
     ["marketing/marketing-social-media-strategist.md", "marketing/marketing-multi-platform-publisher.md"],
     [("mk", "social"), ("kw", "small-business/skills/social-content-engine"), ("cs", "marketing-skill/social-media-manager"),
      ("cs", "marketing-skill/social-media-analyzer")],
     "Define a linha editorial do Instagram, TikTok e YouTube, distribui o trabalho, aprova o calendário, cuida da publicação "
     "e lê as métricas. Devolve ao Yago o calendário, as peças prontas para aprovar e o resumo das métricas."),
    _pega(_com, "estrategista-conteudo", "head-social"),
    _pega(_com, "copywriter", "head-social"),
    _pega(_com, "social-instagram-tiktok", "head-social"),
    ("social-youtube", "Social YouTube", "Canal do YouTube: vídeos longos, Shorts, títulos, thumbnails e SEO",
     "social", "head-social",
     ["marketing/marketing-video-optimization-specialist.md"],
     [("mk", "video"), ("mk", "social"), ("cs", "marketing-skill/youtube-full")],
     "Planeja e prepara o YouTube: pautas, roteiros, títulos e descrições com SEO, capítulos, thumbnails e Shorts a partir "
     "dos vídeos longos, e lê as métricas de retenção e cliques."),
    _pega(_com, "designer-ia", "head-social"),
    _pega(_com, "editor-video", "head-social"),
    _pega(_com, "comunidade", "head-social"),
    _pega(_ti, "bot-instagram", "head-social"),
    _pega(_ti, "bot-tiktok", "head-social"),
    _pega(_ti, "bot-youtube", "head-social"),
]

ROTINAS = {
    "head-social": [("Calendário da semana",
                     "Monte com o Estrategista de Conteúdo o calendário da próxima semana para Instagram, TikTok e YouTube "
                     "(tema, formato, legenda, horário) e envie para aprovação.", {"kind": "weekly", "weekday": 4, "time": "15:00"}),
                    ("Métricas da semana",
                     "Junte as métricas da semana de cada rede (alcance, engajamento, seguidores, melhores e piores posts) e "
                     "mande um resumo curto com 3 ajustes para a próxima semana.", {"kind": "weekly", "weekday": 1, "time": "09:00"})],
}

MEMORIAS_COMUNS = [
    "Responda sempre em português do Brasil.",
    "Este é o OpenBot do Yago, focado em redes sociais: Instagram, TikTok e YouTube.",
    "Antes de publicar, responder em nome da marca ou gastar com anúncio, peça aprovação ao Yago.",
    "Entregue resultados curtos: o que foi feito, peças prontas para aprovar, métricas e próximos passos.",
]

REGRAS_EXTRAS = [
    "Publicação: o caminho padrão é o app Buffer (Loja → Apps), que agenda e publica no Instagram, TikTok e YouTube. "
    "Os bots de integração cuidam da conexão de cada rede.",
    "Imagem e vídeo prontos de verdade precisam de um gerador conectado (Higgsfield, Runway ou fal, na Loja → Apps); "
    "sem ele, entregue roteiro, prompt e briefing.",
]
