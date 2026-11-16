# Equipe comercial de agentes (OpenBot)

Pacote pronto para importar num OpenBot cliente: **32 agentes em 8 grupos**, focado na parte comercial
inteira — marketing, tráfego pago, criativos, social media, vendas, clientes/feedback e administrativo.

**Importar:** copie `equipe-comercial.zip` para o OpenBot (pasta Downloads) → Configurações do servidor →
**Importar → Grok Bot → Escolher arquivo de exportação** → Importar.

## Hierarquia

O **Rafael** fala com o **Diretor Comercial** (agente principal), que coordena os gerentes. Cada gerente
comanda os especialistas da área e devolve o resultado à Diretoria. Cada grupo virou um **canal** com o
gerente como líder.

| Grupo (canal) | Gerente (líder) | Especialistas |
|---|---|---|
| **Diretoria Comercial** | Diretor Comercial | os 7 gerentes abaixo |
| **Marketing** | CMO | Estrategista de Conteúdo, Copywriter, Especialista em SEO, Especialista em E-mail e CRM, Inteligência de Mercado |
| **Tráfego Pago** | Head de Tráfego Pago | Gestor de Meta Ads, Gestor de Google Ads, Gestor de TikTok Ads, Analista de Mensuração |
| **Criativos** | Diretor de Criação | Designer de Peças (IA), Editor e Roteirista de Vídeo, Pesquisador de Anúncios |
| **Social Media** | Head de Social Media | Social Instagram e TikTok, Social LinkedIn e X, Gestor de Comunidade |
| **Vendas** | Head de Vendas | SDR de Prospecção, Coach de Vendas, Analista de Pipeline e CRM, Especialista em Propostas |
| **Clientes e Feedback** | Head de Clientes | Pesquisador de Clientes (conversa com clientes e time e traz o feedback), Agente de Reuniões (pauta, ata e follow-up) |
| **Administrativo Comercial** | Head Administrativo-Comercial | Analista de Precificação, Analista de Contratos, Analista Financeiro-Comercial |

Cada agente tem:
- **instruções** em português, com cargo, a quem responde, quem comanda e as regras (aprovação antes de gastar
  verba, publicar, falar com cliente ou mudar preço) em `imported/INSTRUCTIONS.md`;
- **persona de método** (referência em inglês) de agency-agents;
- **skills** (métodos de trabalho) — 113 no total;
- **memórias** comuns e, nos gerentes, **rotinas** (relatório semanal, checagem diária de campanhas, calendário,
  revisão de funil, rodada mensal de feedback) — **desligadas**: ligue em Rotinas depois de conectar o provedor de IA.

## Fontes (licenças livres; a licença vai junto de cada skill)

| Fonte | Licença | Usado para |
|---|---|---|
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | MIT | personas (paid-media, sales, marketing, design, specialized) |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | MIT | skills de marketing e tráfego (ads, ad-creative, copywriting, social, video, conversion-tracking…) |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Apache-2.0 | skills de vendas, small-business, jurídico, atendimento |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | MIT | skills de C-level (CMO, CRO, CFO), propostas, social |

Pesquisado e **não usado**: a loja oficial do Grok Bot (x.ai/bot/marketplace) não publica o texto dos
modelos nem a licença; o catálogo do OpenBot tem licença ambígua; skills do ClawHub de anúncios têm alerta
de segurança.

## Limites

- Os agentes **não entram sozinhos em reuniões** de vídeo: o Agente de Reuniões trabalha com a transcrição
  (Granola, Fireflies, Meet/Zoom) ou anotações. Para gravar automaticamente, conecte um MCP de reuniões.
- Para falar com pessoas, conecte WhatsApp/Telegram/Slack no OpenBot (Configurações → Mensagens) ou use
  formulários; o Pesquisador de Clientes prepara roteiro e perguntas e pede aprovação antes de contatar.
- Contas de anúncios, CRM, Canva etc. precisam de plugins/MCP conectados (Marketplace do OpenBot).

## Regenerar o pacote

```bash
git clone --depth 1 https://github.com/msitarzewski/agency-agents fontes/agency-agents
git clone --depth 1 https://github.com/coreyhaines31/marketingskills fontes/marketingskills
git clone --depth 1 https://github.com/anthropics/knowledge-work-plugins fontes/knowledge-work-plugins
git clone --depth 1 https://github.com/alirezarezvani/claude-skills fontes/claude-skills
python montar.py fontes equipe-comercial.zip
```

A equipe (cargos, hierarquia, skills, rotinas) fica em `equipe.py`.
