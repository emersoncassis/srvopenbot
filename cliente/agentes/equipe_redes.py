# -*- coding: utf-8 -*-
"""Stack completa de redes sociais: um OpenBot inteiro para Instagram, Facebook, TikTok, YouTube, LinkedIn, X e WhatsApp.

Orgânico, criação (imagem e vídeo editado no servidor), tráfego pago e os bots que conectam cada rede.
Genérico: serve para qualquer cliente. Reaproveita os agentes da equipe comercial, da TI e da equipe social,
com a cadeia de comando ajustada.

  EQUIPE=equipe_redes python montar.py <fontes> equipe-redes-completa.zip

Variáveis opcionais:
  REDES_DONO    nome de quem fala com o agente principal (padrão: "dono da marca")
  REDES_LIDER   chave de um agente que já existe no OpenBot e que vira o chefe do Head de Social Media
                (ex.: boi); REDES_LIDER_NOME é o nome dele. Sem isso, o Head de Social Media é o agente principal.
"""
import os
import equipe as _com, equipe_ti as _ti, equipe_social as _soc

TZ = "America/Sao_Paulo"
CANAL_DIRETORIA = False
DONO = os.environ.get("REDES_DONO", "dono da marca")
LIDER = os.environ.get("REDES_LIDER") or None
EXTERNOS = {LIDER: os.environ.get("REDES_LIDER_NOME", LIDER)} if LIDER else {}

AREAS = {
    "social": ("Redes Sociais", "Linha editorial, calendário, pautas, textos e publicação em todas as redes, comunidade e métricas."),
    "criacao": ("Criação", "Peças, carrosséis, Reels, TikToks, Shorts e vídeos editados no servidor, com voz clonada e legenda."),
    "trafego": ("Tráfego Pago", "Anúncios no Meta (Instagram e Facebook), TikTok e YouTube/Google, verba, metas e mensuração."),
    "integracoes": ("Integrações", "Conexão e manutenção das contas: Instagram, Facebook, TikTok, YouTube, LinkedIn, X e WhatsApp."),
}

def _pega(eq, chave, area, chefe, foco_extra=""):
    a = next(x for x in eq.EQUIPE if x[0] == chave)
    k, nome, cargo, _area, _chefe, personas, skills, foco = a
    # Textos da equipe comercial citam o Rafael (dono daquele OpenBot); aqui vale o dono da marca.
    return (k, nome, cargo, area, chefe, personas, skills, foco.replace("Rafael", DONO) + foco_extra)

_head = next(x for x in _soc.EQUIPE if x[0] == "head-social")
HEAD = ("head-social", "Head de Social Media",
        "Gerente de redes sociais: comanda orgânico, criação, tráfego pago e integrações",
        "social", LIDER, _head[5], _head[6],
        "Define a estratégia e a linha editorial de cada rede (Instagram, Facebook, TikTok, YouTube, LinkedIn, X e WhatsApp), "
        "distribui o trabalho, aprova o calendário e as peças, cuida da publicação, decide com o Head de Tráfego onde vai a verba "
        "e lê as métricas. Devolve ao %s o calendário, as peças prontas para aprovar e o resumo de resultados." % (
            EXTERNOS.get(LIDER, DONO)))

EQUIPE = [
    HEAD,
    # Orgânico
    _pega(_com, "pesquisador-tendencias", "social", "head-social"),
    _pega(_com, "inteligencia-mercado", "social", "head-social",
          " Foco em redes sociais: perfis de concorrentes, formatos que performam e benchmarks de engajamento."),
    _pega(_com, "estrategista-conteudo", "social", "head-social"),
    _pega(_com, "copywriter", "social", "head-social"),
    _pega(_com, "social-instagram-tiktok", "social", "head-social",
          " Cuida também da página do Facebook e do Threads (o que sai no Instagram é adaptado para lá)."),
    _pega(_soc, "social-youtube", "social", "head-social"),
    _pega(_com, "social-linkedin-x", "social", "head-social"),
    _pega(_com, "comunidade", "social", "head-social",
          " Atende comentários e DMs de todas as redes e do WhatsApp da marca, com o Bot de WhatsApp."),
    # Criação
    _pega(_com, "diretor-criativo", "criacao", "head-social"),
    _pega(_com, "designer-ia", "criacao", "diretor-criativo"),
    _pega(_com, "editor-video", "criacao", "diretor-criativo"),
    _pega(_com, "pesquisador-anuncios", "criacao", "diretor-criativo"),
    # Tráfego pago
    _pega(_com, "head-trafego", "trafego", "head-social"),
    _pega(_com, "gestor-meta-ads", "trafego", "head-trafego"),
    _pega(_com, "gestor-tiktok-ads", "trafego", "head-trafego"),
    _pega(_com, "gestor-google-ads", "trafego", "head-trafego"),
    _pega(_com, "mensuracao", "trafego", "head-trafego"),
    # Integrações
    _pega(_ti, "engenheiro-integracoes", "integracoes", "head-social",
          " Aqui você responde ao Head de Social Media e comanda os bots de integração de cada rede."),
    _pega(_ti, "bot-instagram", "integracoes", "engenheiro-integracoes",
          " Inclui a página do Facebook ligada à conta do Instagram (mesmo app da Meta)."),
    _pega(_ti, "bot-tiktok", "integracoes", "engenheiro-integracoes"),
    _pega(_ti, "bot-youtube", "integracoes", "engenheiro-integracoes"),
    _pega(_ti, "bot-linkedin", "integracoes", "engenheiro-integracoes",
          " Cuida também da conta do X (Twitter): conexão pela API do X ou pelo app de publicação."),
    _pega(_ti, "bot-whatsapp", "integracoes", "engenheiro-integracoes"),
]

_chaves = {a[0] for a in EQUIPE}
ROTINAS = {}
for _fonte in (_com.ROTINAS, _ti.ROTINAS, _soc.ROTINAS):
    for _k, _r in _fonte.items():
        if _k in _chaves:
            ROTINAS[_k] = _r
ROTINAS["pesquisador-tendencias"] = [("Radar de tendências",
    "Rode o radar da semana (skill pesquisa-tendencias) no nicho da marca e entregue ao Head de Social Media "
    "de 8 a 12 pautas com gancho, formato, rede, por que agora e referência.", {"kind": "weekly", "weekday": 4, "time": "10:00"})]

_chefe_topo = EXTERNOS.get(LIDER) if LIDER else None
MEMORIAS_COMUNS = [
    "Responda sempre em português do Brasil.",
    ("Este OpenBot cuida das redes sociais da marca: Instagram, Facebook, TikTok, YouTube, LinkedIn, X e WhatsApp. "
     "O %s fala com %s, que comanda o Head de Social Media." % (DONO, _chefe_topo)) if _chefe_topo else
    ("Este OpenBot cuida das redes sociais da marca: Instagram, Facebook, TikTok, YouTube, LinkedIn, X e WhatsApp. "
     "O %s fala com o Head de Social Media, que comanda a equipe." % DONO),
    "Antes de publicar, responder em nome da marca, mandar mensagem a cliente ou gastar com anúncio, peça aprovação ao seu gestor, que leva ao %s." % DONO,
    "Entregue resultados curtos: o que foi feito, peças prontas para aprovar, métricas e próximos passos.",
]

# A primeira regra da equipe social (publicação) cita só 3 redes; esta a substitui.
REGRAS_EXTRAS = [
    "Publicação: o app Buffer (Loja → Apps) agenda e publica no Instagram, Facebook, TikTok, YouTube, LinkedIn e X. "
    "Os bots de integração cuidam da conexão de cada rede; o WhatsApp é conectado pelo Bot de WhatsApp.",
] + _soc.REGRAS_EXTRAS[1:]
