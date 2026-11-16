# -*- coding: utf-8 -*-
"""Publica um pacote de agentes (zip do montar.py) na Loja do OpenBot (servidor de contas próprio).

Roda num container na rede dokploy-network (fala com openbot-contas:3101):

  docker run --rm --network dokploy-network -e ADMIN_TOKEN=... -e LOJA_EMAIL=loja@empresa.local \
    -e LOJA_NOME="Loja ICTeam" -v $PWD:/w -w /w python:3.12-alpine python publicar_loja.py equipe-comercial.zip

- Cria/entra na conta da loja (o código de login vem na resposta do servidor local).
- Envia cada skill (sem repetir as iguais), aprova com o token de admin (SKILLS_ADMIN_TOKEN do OpenBot Contas).
- Publica cada agente com as skills dele e aprova.
- Guarda o progresso em loja-estado.json (pode rodar de novo: o que já foi publicado é pulado).
"""
import hashlib, io, json, os, re, sys, time, uuid, zipfile, urllib.request, urllib.error

API = os.environ.get("API", "http://openbot-contas:3101")
ADMIN = os.environ["ADMIN_TOKEN"]
EMAIL = os.environ.get("LOJA_EMAIL", "loja@openbot.local")
NOME = os.environ.get("LOJA_NOME", "Loja")
ESTADO = os.environ.get("ESTADO", "loja-estado.json")
PAUSA_UPLOAD = float(os.environ.get("PAUSA_UPLOAD", "13"))  # o servidor aceita 5 envios por minuto por conta
pacote = zipfile.ZipFile(sys.argv[1])
manifest = json.loads(pacote.read("openbot-import.json"))

estado = json.load(open(ESTADO)) if os.path.exists(ESTADO) else {"skills": {}, "agents": {}}
def salvar():
    with open(ESTADO, "w") as f:
        json.dump(estado, f, indent=1)

def req(method, path, body=None, token=None, ctype="application/json"):
    data = body if isinstance(body, (bytes, type(None))) else json.dumps(body).encode()
    h = {"content-type": ctype} if data is not None else {}
    if token:
        h["authorization"] = "Bearer " + token
    r = urllib.request.Request(API + path, data=data, method=method, headers=h)
    for tentativa in range(6):
        try:
            raw = urllib.request.urlopen(r, timeout=60).read().decode()
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            txt = e.read().decode()[:400]
            if e.code == 429:
                time.sleep(20 * (tentativa + 1)); continue
            raise SystemExit("%s %s -> %s %s" % (method, path, e.code, txt))
    raise SystemExit("limite de envios: tente de novo mais tarde")

def multipart(campos):
    b = "----loja" + uuid.uuid4().hex
    out = io.BytesIO()
    for nome, valor in campos:
        out.write(("--%s\r\n" % b).encode())
        if isinstance(valor, tuple):
            fn, ct, dados = valor
            out.write(('Content-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: %s\r\n\r\n' % (nome, fn, ct)).encode())
            out.write(dados)
        else:
            out.write(('Content-Disposition: form-data; name="%s"\r\n\r\n' % nome).encode())
            out.write(valor.encode())
        out.write(b"\r\n")
    out.write(("--%s--\r\n" % b).encode())
    return out.getvalue(), "multipart/form-data; boundary=" + b

# 1) Conta da loja
token = estado.get("token")
if not token:
    s = req("POST", "/v1/auth/email/start", {"email": EMAIL})
    v = req("POST", "/v1/auth/email/verify", {"challengeId": s["challengeId"], "code": s["developmentCode"]})
    token = v["sessionToken"]
    estado["token"] = token
    salvar()
    req("PATCH", "/v1/me/profile", {"name": NOME}, token)
print("conta da loja:", EMAIL)

def categoria(texto):
    t = texto.lower()
    if any(k in t for k in ("criativ", "design", "imagem", "vídeo", "video", "peça")): return "design"
    if any(k in t for k in ("analytic", "mensura", "pipeline", "métrica", "relatório", "precifica", "avalia")): return "data-analytics"
    if any(k in t for k in ("pesquis", "concorr", "inteligência", "mercado", "bairro")): return "research"
    if any(k in t for k in ("contrato", "proposta", "documento", "jurídic")): return "documents"
    return "productivity"

# 2) Skills (iguais em vários agentes = uma só na loja)
nomes_arquivos = pacote.namelist()
def nome_skill(md):
    m = re.search(r"^name:\s*[\"']?([^\"'\n]+)", md, re.M)
    return m.group(1).strip() if m else ""

def zip_da_skill(pasta, novo_nome=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(nomes_arquivos):
            if n.startswith(pasta + "/") and not n.endswith("/"):
                dados = pacote.read(n)
                if novo_nome and n == pasta + "/SKILL.md":
                    txt = dados.decode("utf-8")
                    txt = re.sub(r"^name:.*$", "name: " + novo_nome, txt, count=1, flags=re.M)
                    dados = txt.encode("utf-8")
                z.writestr(n[len(pasta) + 1:], dados)
    return buf.getvalue()

def da_conta(slug):
    for item in req("GET", "/v1/skills/mine", None, token):
        if item.get("slug") == slug:
            if item.get("status") == "pending":
                req("POST", "/v1/skills/admin/submissions/%s" % item["id"], {"action": "approve"}, ADMIN)
            return {"skillId": item["skillId"], "versionId": item["id"], "slug": item["slug"], "name": item["name"],
                    "version": item.get("version", 1)}
    return None

skills_por_pasta = {}
for a in manifest["agents"]:
    for pasta in a["skills"]:
        dados = zip_da_skill(pasta)
        h = hashlib.sha256(pacote.read(pasta + "/SKILL.md")).hexdigest()[:24]
        skills_por_pasta[pasta] = (h, dados)

pendentes = [(h, d, p) for p, (h, d) in skills_por_pasta.items() if h not in estado["skills"]]
vistos = set()
pendentes = [x for x in pendentes if not (x[0] in vistos or vistos.add(x[0]))]
print("skills novas para publicar:", len(pendentes))
nomes_usados = {v.get("name"): k for k, v in estado["skills"].items()}
for i, (h, dados, pasta) in enumerate(pendentes, 1):
    md = pacote.read(pasta + "/SKILL.md").decode("utf-8", "replace")
    nome = nome_skill(md)
    novo = None
    if nome in nomes_usados and nomes_usados[nome] != h:
        # Mesmo nome de outra fonte: publica como <nome>-<fonte> (ex.: content-strategy-kw)
        novo = "%s-%s" % (nome, os.path.basename(pasta).split("-", 1)[0])
        dados = zip_da_skill(pasta, novo)
    corpo, ct = multipart([("bundle", (os.path.basename(pasta) + ".zip", "application/zip", dados)),
                           ("category", categoria(md[:600])), ("showCreatorAvatar", "false")])
    try:
        r = req("POST", "/v1/skills/", corpo, token, ct)
        reg = {"skillId": r.get("skillId"), "versionId": r.get("id"), "slug": r.get("slug"), "name": r.get("name"),
               "version": r.get("version", 1)}
    except SystemExit as e:
        if "slug_taken" not in str(e):
            raise
        reg = da_conta(re.sub(r"[^a-z0-9]+", "-", (novo or nome).lower()).strip("-"))
        if not reg:
            raise
        estado["skills"][h] = reg; nomes_usados[reg["name"]] = h; salvar()
        print("  [%d/%d] skill %s (já estava na loja)" % (i, len(pendentes), reg["slug"]))
        continue
    nomes_usados[reg["name"]] = h
    if not reg["skillId"] or not reg["versionId"]:
        raise SystemExit("resposta inesperada ao enviar skill: %s" % json.dumps(r)[:500])
    req("POST", "/v1/skills/admin/submissions/%s" % reg["versionId"], {"action": "approve"}, ADMIN)
    estado["skills"][h] = reg
    salvar()
    print("  [%d/%d] skill %s" % (i, len(pendentes), reg["slug"] or reg["name"]))
    time.sleep(PAUSA_UPLOAD)

# 3) Agentes
meus_agentes = None
for i, a in enumerate(manifest["agents"], 1):
    chave = a["key"]
    desc = re.sub(r"Antes de qualquer coisa, leia imported/INSTRUCTIONS\.md[^.]*\.\s*", "", a["description"]).strip()
    skills = []
    for pasta in a["skills"]:
        reg = estado["skills"][skills_por_pasta[pasta][0]]
        if reg not in skills:
            skills.append(reg)
    snapshot = {"agentId": "loja-" + chave, "name": a["name"], "title": a.get("title") or "", "description": desc[:2000],
                "avatarSeed": "loja:" + chave, "avatarHue": None, "skills": skills, "routines": a.get("routines", [])}
    assinatura = hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    antes = estado["agents"].get(chave)
    if isinstance(antes, dict) and antes.get("hash") == assinatura:
        continue
    campos = [("snapshot", json.dumps(snapshot, ensure_ascii=False)),
              ("category", categoria(a.get("title", "") + " " + desc)), ("showCreatorAvatar", "false")]
    if antes:
        # Agente já está na loja e mudou: publica uma versão nova do mesmo agente.
        loja_id = antes.get("agentId") if isinstance(antes, dict) else None
        if not loja_id:
            if meus_agentes is None:
                meus_agentes = req("GET", "/v1/marketplace/agents/mine", None, token)
                if isinstance(meus_agentes, dict):
                    meus_agentes = next((v for v in meus_agentes.values() if isinstance(v, list)), [])
            loja_id = next((x["agentId"] for x in meus_agentes if x.get("name") == a["name"]), None)
        if loja_id:
            campos.append(("agentId", loja_id))
    corpo, ct = multipart(campos)
    r = req("POST", "/v1/marketplace/agents/", corpo, token, ct)
    vid = r.get("id")
    if not vid:
        raise SystemExit("resposta inesperada ao publicar agente: %s" % json.dumps(r)[:500])
    req("PATCH", "/v1/marketplace/agents/admin/submissions/%s" % vid, {"status": "approved"}, ADMIN)
    estado["agents"][chave] = {"versionId": vid, "agentId": r.get("agentId"), "hash": assinatura}
    salvar()
    print("  [%d/%d] agente %s%s" % (i, len(manifest["agents"]), a["name"], " (versão nova)" if antes else ""))
    time.sleep(PAUSA_UPLOAD)
print("pronto:", len(estado["skills"]), "skills e", len(estado["agents"]), "agentes na loja")
