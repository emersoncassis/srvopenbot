# -*- coding: utf-8 -*-
"""Monta o pacote de agentes (formato openbot-agent-import v1) a partir de equipe.py e das fontes.

  python montar.py <pasta-das-fontes> <saida.zip>

<pasta-das-fontes> tem os clones: agency-agents, marketingskills, knowledge-work-plugins, claude-skills.
Importe o zip no OpenBot em: Configurações do servidor > Importar.
"""
import importlib, json, os, re, shutil, subprocess, sys, tempfile, zipfile, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# EQUIPE=equipe (comercial, padrão) ou EQUIPE=equipe_imobiliario
_eq = importlib.import_module(os.environ.get("EQUIPE", "equipe"))
AREAS, EQUIPE, ROTINAS, MEMORIAS_COMUNS, TZ = _eq.AREAS, _eq.EQUIPE, _eq.ROTINAS, _eq.MEMORIAS_COMUNS, _eq.TZ
REGRAS_EXTRAS = getattr(_eq, "REGRAS_EXTRAS", [])
CANAL_DIRETORIA = getattr(_eq, "CANAL_DIRETORIA", True)

# SO_AGENTES=chave1,chave2: monta só esses agentes (para completar um OpenBot que já tem o resto da equipe)
SO_AGENTES = set(filter(None, os.environ.get("SO_AGENTES", "").split(",")))
SRC = sys.argv[1]
OUT = sys.argv[2]
FONTES = {
    "ag": ("agency-agents", "", "msitarzewski/agency-agents", "MIT"),
    "mk": ("marketingskills", "skills", "coreyhaines31/marketingskills", "MIT"),
    "kw": ("knowledge-work-plugins", "", "anthropics/knowledge-work-plugins", "Apache-2.0"),
    "cs": ("claude-skills", "", "alirezarezvani/claude-skills", "MIT"),
    "re": ("real-estate-agents", "", "hoangtng/real-estate-agents", "MIT"),
    "dl": ("imobiliario-diligence", "", "neimaciel/imobiliario-diligence", "MIT"),
    "zt": ("ai-realestate-claude", "", "zubair-trabzada/ai-realestate-claude", "MIT"),
    "cr": ("cre-agent-skills", "", "ahacker-1/cre-agent-skills", "Apache-2.0"),
    "pr": ("prosperity-real-estate-skills", "", "TheProsperityAgent/prosperity-real-estate-skills", "MIT"),
}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "dist", "build"}

def commit(repo):
    return subprocess.check_output(["git", "-C", os.path.join(SRC, repo), "rev-parse", "--short", "HEAD"]).decode().strip()

def licenca(repo):
    for n in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        p = os.path.join(SRC, repo, n)
        if os.path.exists(p):
            return open(p, encoding="utf-8", errors="replace").read()
    return ""

def consertar_cabecalho(caminho):
    """Algumas skills de origem têm YAML inválido no cabeçalho (ex.: ':' sem aspas na description).
    A Loja do OpenBot rejeita. Coloca name/description entre aspas só quando o YAML não abre. Devolve True se mudou."""
    import yaml
    txt = open(caminho, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if not m:
        return False
    try:
        v = yaml.safe_load(m.group(1))
        if isinstance(v, dict) and isinstance(v.get("name"), str) and isinstance(v.get("description"), str):
            return False
    except Exception:
        pass
    linhas = []
    for l in m.group(1).split("\n"):
        k = re.match(r"^(name|description):\s*(.*)$", l)
        if k and not k.group(2).startswith(('"', "'")):
            l = "%s: %s" % (k.group(1), json.dumps(k.group(2).strip(), ensure_ascii=False))
        linhas.append(l)
    novo = txt[:m.start(1)] + "\n".join(linhas) + txt[m.end(1):]
    yaml.safe_load(re.match(r"^---\s*\n(.*?)\n---", novo, re.S).group(1))
    open(caminho, "w", encoding="utf-8", newline="\n").write(novo)
    return True

def src_path(fonte, rel):
    repo, base, _, _ = FONTES[fonte]
    return os.path.join(SRC, repo, base, rel)

def resolve_skill(fonte, rel):
    p = src_path(fonte, rel)
    if os.path.isdir(p) and os.path.exists(os.path.join(p, "SKILL.md")):
        return p
    # claude-skills: <grupo>/skills/<nome>
    grupo, _, nome = rel.partition("/")
    alt = src_path(fonte, "%s/skills/%s" % (grupo, nome))
    if os.path.exists(os.path.join(alt, "SKILL.md")):
        return alt
    # claude-skills às vezes tem a skill um nível abaixo
    for root, dirs, files in os.walk(p):
        if "SKILL.md" in files:
            return root
    raise SystemExit("skill não encontrada: %s %s" % (fonte, rel))

nomes = dict(getattr(_eq, "EXTERNOS", {}))
nomes.update({a[0]: a[1] for a in EQUIPE})
subordinados = {}
for a in EQUIPE:
    if a[4]:
        subordinados.setdefault(a[4], []).append(a[0])

tmp = tempfile.mkdtemp()
manifest_agents, avisos = [], []
for key, nome, cargo, area, chefe, personas, skills, foco in EQUIPE:
    if SO_AGENTES and key not in SO_AGENTES:
        continue
    base = os.path.join(tmp, "agents", key)
    os.makedirs(os.path.join(base, "files"), exist_ok=True)
    # Skills
    skill_paths, usados = [], set()
    for fonte, rel in skills:
        p = resolve_skill(fonte, rel)
        nome_pasta = "%s-%s" % (fonte, os.path.basename(p.rstrip("/\\")))
        if nome_pasta in usados:
            continue
        usados.add(nome_pasta)
        n_files = sum(len(f) for _, _, f in os.walk(p))
        size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)
        if n_files > 190 or size > 9_000_000:
            avisos.append("skill grande demais, ignorada: %s" % nome_pasta); continue
        dst = os.path.join(base, "skills", nome_pasta)
        shutil.copytree(p, dst, ignore=shutil.ignore_patterns(*SKIP_DIRS, ".env*", "*private*key*", "*.zip", "*.tar", "*.gz", "*.7z", "*.rar"))
        repo, _, slug, lic = FONTES[fonte]
        ajuste = consertar_cabecalho(os.path.join(dst, "SKILL.md"))
        with open(os.path.join(dst, "SOURCE.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("Fonte: https://github.com/%s (commit %s), licença %s. %s\n" % (
                slug, commit(repo), lic,
                "Único ajuste: cabeçalho YAML do SKILL.md (texto entre aspas)." if ajuste else "Copiado sem alterações."))
        with open(os.path.join(dst, "LICENSE-ORIGEM.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(licenca(repo))
        skill_paths.append("agents/%s/skills/%s" % (key, nome_pasta))
    # Instruções completas (cadeia de comando + personas)
    linhas = ["# %s — %s" % (nome, cargo), "", "## Seu papel", foco, "", "## Cadeia de comando"]
    if chefe:
        linhas.append("- Você responde a **%s**. Entregue seus resultados a ele (send_message), não direto ao Rafael, "
                      "a menos que o Rafael fale com você." % nomes[chefe])
    else:
        linhas.append("- Você é o agente principal: o **Rafael** fala com você. Você coordena os gerentes abaixo e devolve a ele resumos e decisões.")
    if key in subordinados:
        linhas.append("- Você comanda: %s. Delegue a eles o que é da área de cada um (openbot.list_agents e send_message), "
                      "cobre o resultado e consolide antes de entregar." % ", ".join("**%s**" % nomes[s] for s in subordinados[key]))
    if key == "diretor-comercial":
        linhas.append("- Gerentes: %s." % ", ".join("**%s** (%s)" % (nomes[k], AREAS[a[3]][0]) for a in EQUIPE for k in [a[0]] if a[4] == "diretor-comercial"))
    linhas += ["- Algo de outra área: peça ao gerente daquela área, não faça por ele.", "",
               "## Regras", *["- " + m for m in MEMORIAS_COMUNS],
               *["- " + r for r in REGRAS_EXTRAS],
               "- Use as suas skills (pasta skills) como método de trabalho. Muitas estão em inglês; responda em português.",
               "- Contexto da empresa (produto, público, metas, tom de voz): pergunte ao Diretor Comercial ou ao Rafael e salve como memória.", ""]
    for item in personas:
        fp, rel = item if isinstance(item, tuple) else ("ag", item)
        repo_p, _, slug_p, lic_p = FONTES[fp]
        p = src_path(fp, rel)
        txt = open(p, encoding="utf-8").read()
        txt = re.sub(r"^---\n.*?\n---\n", "", txt, flags=re.S)
        linhas += ["---", "", "## Referência de método (persona em inglês, de %s, %s, commit %s): %s"
                   % (slug_p, lic_p, commit(repo_p), os.path.basename(rel)), "", txt.strip(), ""]
    with open(os.path.join(base, "files", "INSTRUCTIONS.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas))
    # Descrição curta (<= 2000)
    desc = "%s. %s " % (cargo, foco)
    desc += ("Você responde a %s. " % nomes[chefe]) if chefe else "Você é o agente principal e fala com o Rafael. "
    if key in subordinados:
        desc += "Você comanda: %s. " % ", ".join(nomes[s] for s in subordinados[key])
    desc += ("Antes de qualquer coisa, leia imported/INSTRUCTIONS.md (cadeia de comando, regras e método). "
             "Responda em português do Brasil. Peça aprovação antes de gastar verba, publicar, enviar mensagem a cliente ou mudar preço.")
    assert len(desc) <= 2000, key
    rotinas = [{"name": n, "instruction": i, "active": False, "timezone": TZ, "schedule": s} for n, i, s in ROTINAS.get(key, [])]
    manifest_agents.append({"key": key, "name": nome, "title": cargo[:120], "description": desc, "avatar": None,
                            "skills": skill_paths[:32], "routines": rotinas, "memories": MEMORIAS_COMUNS,
                            "files": "agents/%s/files" % key})

channels = []
if SO_AGENTES:
    AREAS = {}  # pacote parcial (só alguns agentes): sem canais
for area, (nome_area, topico) in AREAS.items():
    if area == "diretoria" and not CANAL_DIRETORIA:
        continue
    if area == "diretoria":
        membros = ["diretor-comercial"] + [a[0] for a in EQUIPE if a[4] == "diretor-comercial"]
        lead = "diretor-comercial"
        instr = ("Diretoria comercial. O Rafael fala aqui com o Diretor Comercial e os gerentes de cada área. "
                 "O Diretor Comercial coordena; cada gerente responde pela sua área e traz números e decisões pendentes.")
    else:
        membros = [a[0] for a in EQUIPE if a[3] == area]
        lead = next(a[0] for a in EQUIPE if a[3] == area and a[4] not in [b[0] for b in EQUIPE if b[3] == area])
        instr = ("Área de %s: %s O gerente (%s) distribui as tarefas, revisa as entregas e leva o resultado à Diretoria."
                 % (nome_area, topico, nomes[lead]))
    channels.append({"key": area, "name": nome_area, "title": topico[:120], "instructions": instr[:2000],
                     "members": membros, "lead": lead, "routines": [], "memories": MEMORIAS_COMUNS[:3]})

manifest = {"format": "openbot-agent-import", "version": 1,
            "source": {"app": "grok-bot", "exportedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
            "agents": manifest_agents, "channels": channels}
with open(os.path.join(tmp, "openbot-import.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(tmp):
        for fn in files:
            full = os.path.join(root, fn)
            z.write(full, os.path.relpath(full, tmp).replace(os.sep, "/"))
n_files = sum(len(f) for _, _, f in os.walk(tmp))
print("agentes:", len(manifest_agents), "canais:", len(channels), "skills:", sum(len(a["skills"]) for a in manifest_agents),
      "arquivos:", n_files, "zip:", round(os.path.getsize(OUT) / 1e6, 1), "MB")
for a in avisos:
    print("AVISO:", a)
shutil.rmtree(tmp)
