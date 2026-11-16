# -*- coding: utf-8 -*-
"""Equipe de redes sociais (Instagram, TikTok, YouTube): um OpenBot só de postagem e conteúdo.

O Boi (agente que o Yago criou no OpenBot dele) é o líder de todos os bots: o Head de Social Media responde ao Boi
e comanda a equipe. Mude LIDER/EXTERNOS para outro OpenBot. Reaproveita os agentes da equipe comercial
e os bots de integração da TI, com a cadeia de comando ajustada. O resto continua na Loja.
"""
import equipe as _com, equipe_ti as _ti

TZ = "America/Sao_Paulo"
CANAL_DIRETORIA = False
LIDER = "boi"
EXTERNOS = {LIDER: "Boi"}
DONO = "Yago"

AREAS = {"social": ("Redes Sociais", "Postagens, Reels, TikToks, YouTube/Shorts, roteiros, peças e métricas.")}

def _pega(eq, chave, chefe, foco_extra=""):
    a = next(x for x in eq.EQUIPE if x[0] == chave)
    k, nome, cargo, _area, _chefe, personas, skills, foco = a
    return (k, nome, cargo, "social", chefe, personas, skills, foco + foco_extra)

EQUIPE = [
    ("head-social", "Head de Social Media", "Gerente de redes sociais: responde ao Boi e comanda a equipe",
     "social", LIDER,
     ["marketing/marketing-social-media-strategist.md", "marketing/marketing-multi-platform-publisher.md"],
     [("mk", "social"), ("kw", "small-business/skills/social-content-engine"), ("cs", "marketing-skill/social-media-manager"),
      ("cs", "marketing-skill/social-media-analyzer")],
     "Define a linha editorial do Instagram, TikTok e YouTube, distribui o trabalho, aprova o calendário, cuida da publicação "
     "e lê as métricas. Recebe as ordens do Boi e devolve a ele o calendário, as peças prontas para aprovar e o resumo das métricas."),
    _pega(_com, "pesquisador-tendencias", "head-social"),
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
    "pesquisador-tendencias": [("Radar de tendências",
                     "Rode o radar da semana (skill pesquisa-tendencias) no nicho do Yago e entregue ao Head de Social Media "
                     "de 8 a 12 pautas com gancho, formato, por que agora e referência.", {"kind": "weekly", "weekday": 4, "time": "10:00"})],
}

MEMORIAS_COMUNS = [
    "Responda sempre em português do Brasil.",
    "Este é o OpenBot do Yago, focado em redes sociais: Instagram, TikTok e YouTube.",
    "O Boi é o líder de todos os bots, sempre: o Yago fala com o Boi, o Boi comanda o Head de Social Media e a equipe.",
    "Antes de publicar, responder em nome da marca ou gastar com anúncio, peça aprovação ao Yago (pelo Boi).",
    "Entregue resultados curtos: o que foi feito, peças prontas para aprovar, métricas e próximos passos.",
]

REGRAS_EXTRAS = [
    "Publicação: o caminho padrão é o app Buffer (Loja → Apps), que agenda e publica no Instagram, TikTok e YouTube. "
    "Os bots de integração cuidam da conexão de cada rede.",
    "Edição de vídeo é feita no próprio servidor pelo Editor (estúdio com Remotion, ffmpeg e legenda automática: "
    "comandos novo-video, legendar, cortar-silencio e renderizar). Voz clonada e narração: ElevenLabs.",
    "Imagem ou vídeo gerado do zero por IA precisa de um gerador conectado (Higgsfield, Runway ou fal, na Loja → Apps).",
]
