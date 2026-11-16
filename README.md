# OpenBot independente no Dokploy — spec e templates

OpenBot ([nightly-labs/openbot](https://github.com/nightly-labs/openbot), versão **0.71.0**) rodando numa
VPS com Dokploy, **sem depender dos servidores da OpenBot** (openbot.run): contas, login, Signal e TURN
são nossos. Cada pessoa tem o seu OpenBot, que abre no navegador e conecta no app de celular.

> Licença do OpenBot: **PolyForm Noncommercial** — uso pessoal/experimentação, não comercial.

## Estrutura

```
openbot-templates/
├── servidor/              ← sobe UMA vez por VPS
│   ├── contas/            projeto Dokploy "OpenBot Contas"  (servidor de contas/login)
│   ├── remoto/            projeto Dokploy "OpenBot Remoto"  (Signal + TURN, para o celular)
│   └── scripts/gerar-segredos.sh
└── cliente/               ← um projeto Dokploy por pessoa ("OpenBot do Fulano")
    └── novo-cliente.sh
```

## Arquitetura

```
 navegador ──https──▶ Traefik ──▶ OpenBot do Fulano (noVNC :6080, senha básica)
                                        │  socat 127.0.0.1:3100
                                        ▼
                                 OpenBot Contas (:3101, rede dokploy-network)
                                        ▲                 │ tíquetes ES256
 celular ──https (só rotas mobile)──────┘                 ▼
 celular ──wss──▶ Traefik ──▶ Signal (:8081) ◀── OpenBot do Fulano (host)
 celular ◀──UDP 3478 / 16384-65535──▶ TURN (coturn, rede host) ◀──▶ OpenBot do Fulano
```

| Peça | O que é | Endereço | RAM (aprox.) |
|---|---|---|---|
| **OpenBot Contas** | `apps/auth-api` do OpenBot compilado e rodando local (Miniflare: D1/R2 em disco). Login sem e-mail: o código aparece na tela. | interno `openbot-contas:3101`; público `contas.openbot.<dominio>` só rotas do celular | ~950 MB |
| **OpenBot Remoto** | `remote/` do OpenBot: Signal (WebSocket) + coturn | `signal.openbot.<dominio>`, `turn.openbot.<dominio>` | ~150 MB |
| **OpenBot cliente** | imagem oficial `ghcr.io/nightly-labs/openbot` em **modo desktop** + openbox + x11vnc + noVNC | `<nome>.openbot.<dominio>` | ~1 GB parado |

VPS de referência: 2 vCPU, 8 GB RAM → servidor + 3 a 4 clientes com uso leve.

## Pré-requisitos

- VPS com Docker e Dokploy (Traefik do Dokploy com certresolver `letsencrypt`, rede `dokploy-network`).
- DNS (Cloudflare, **DNS only / nuvem cinza**):
  - `*.openbot.<dominio>` → IP da VPS
  - `openbot.<dominio>` → IP da VPS
- Portas abertas na VPS: TCP 22, 80, 443, 3478; UDP 443, 3478 e **16384–65535** (relay do TURN). Ver "Firewall".

## Instalação do servidor (uma vez)

1. Na VPS: `bash servidor/scripts/gerar-segredos.sh <dominio> <ip-publico>` → imprime os dois blocos de Environment.
2. Dokploy → novo projeto **OpenBot Contas** → serviço Compose **openbot-contas** (tipo docker-compose, origem *Raw*):
   - Compose: `servidor/contas/docker-compose.yml`
   - Advanced → Mounts → *File mount*: `Dockerfile.auth` e `auth-entrypoint.sh` (caminho do arquivo = o nome)
   - Environment: bloco "OpenBot Contas" do passo 1 → **Deploy** (o build leva ~8 min).
3. Dokploy → novo projeto **OpenBot Remoto** → serviço Compose **openbot-remoto** (Raw):
   - Compose: `servidor/remoto/docker-compose.yml`
   - Mounts: `turnserver.conf` (confira as sub-redes, ver "TURN" abaixo)
   - Environment: bloco "OpenBot Remoto" → **Deploy**.
4. Conferir:
   - `https://contas.openbot.<dominio>/health/live` → `{"status":"ok"}`
   - `https://signal.openbot.<dominio>/health/live` → `{"status":"live"}`
   - `https://contas.openbot.<dominio>/v1/auth/email/start` → **404** (login por e-mail não exposto)

## Firewall (ufw)

`servidor/scripts/firewall.sh` (rodar como root na VPS) liga o ufw com:

| Porta | Para quê |
|---|---|
| 22/tcp (limit) | SSH |
| 80/tcp, 443/tcp, 443/udp | Traefik (sites, certificados, HTTP/3) |
| 3478/tcp+udp, 16384–65535/udp | TURN do celular |
| tudo de 10.0.0.0/8 e 172.16.0.0/12 | redes internas do Docker (containers falando com o host, ex. TURN) |

Fecha para fora: **3000** (painel do Dokploy sem HTTPS — o Docker publica por fora do ufw, então o bloqueio
vai na cadeia `DOCKER-USER` em `/etc/ufw/after.rules`) e as portas do Swarm (2377, 7946, 4789).
**Antes**, dê um domínio HTTPS ao painel (Dokploy → Settings → Web Server → domínio, ex.
`dokploy.openbot.<dominio>`), senão você perde o acesso ao painel.
O script agenda um **desfazer automático em 5 minutos**; depois de conferir que o SSH e os sites abrem:
`systemctl stop fw-rollback.timer`.

## Novo cliente (OpenBot de uma pessoa)

1. No Dokploy, **duplique o projeto "OpenBot Template"** (ou crie do zero: serviço Compose Raw com
   `cliente/docker-compose.yml` e os mounts `Dockerfile`, `openbot-desktop-entrypoint.sh`, `seccomp.json`).
2. Gere o Environment: `bash cliente/novo-cliente.sh <nome> <dominio>` e cole na aba Environment.
3. **Deploy**. Acesso: `https://<nome>.openbot.<dominio>` com o usuário/senha do Environment.
4. Primeiro login no OpenBot: qualquer e-mail; o código aparece em laranja na tela ("Development code").
5. Celular: OpenBot → Configurações → Conectar celular → Adicionar celular → Sim, entrar → ler o QR no app.

O DNS curinga já cobre o endereço novo; o certificado HTTPS sai sozinho pelo Traefik.

## Atualizar a versão do OpenBot

Trocar **juntos** `OPENBOT_REF` (Contas e Remoto, ex. `v0.72.0`) e `OPENBOT_TAG` (clientes, ex. `0.72.0`) e
fazer Redeploy em todos. Depois conferir se o `wrangler.json` da versão nova trouxe variáveis novas
apontando para `openbot.run` (ver "Armadilhas").

## Armadilhas resolvidas (não desfazer)

- **Modo servidor exige a conta deles.** A imagem oficial roda com `OPENBOT_SERVER=1` e só funciona logada
  em openbot.run. O cliente usa um entrypoint próprio (`openbot-desktop-entrypoint.sh`) sem essa variável,
  com tela virtual + noVNC.
- **O app só aceita servidor de contas em HTTPS ou `http://127.0.0.1`.** Por isso o cliente roda um
  `socat` que traz `openbot-contas:3101` para `127.0.0.1:3100` (`OPENBOT_AUTH_UPSTREAM`).
- **O build do auth-api traz os endereços da OpenBot** (`REMOTE_SIGNAL_HOMES`, `REMOTE_AUTH_WEBHOOK_URLS`,
  `SIGNAL_ENTRY_ZONE_ID`, `GITHUB_APP_CLIENT_ID`…). Sem sobrescrever, os OpenBots iam para
  `signal-us.openbot.run` ("tíquete remoto inválido") e eventos de login iam para os servidores deles.
  O `auth-entrypoint.sh` sobrescreve tudo no `.dev.vars`.
- **Vite bloqueia nomes de host desconhecidos.** `__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS` libera
  `openbot-contas` (Signal) e `CONTAS_HOST` (celular).
- **Vite não carrega a config sob Bun** → build e servidor rodam com Node 24. O modo `vite dev` gastava
  2,2 GB; o build + `vite preview` gasta ~1 GB.
- **TURN recusava as redes privadas** (configuração padrão), e o OpenBot roda em rede Docker → celular
  ficava "aguardando conexão". `turnserver.conf` libera só `10.0.1.0/24` (dokploy-network) e
  `172.16.1.0/24` (docker_gwbridge). **Em outra VPS, confira as sub-redes:**
  `docker network inspect dokploy-network docker_gwbridge -f '{{range .IPAM.Config}}{{.Subnet}} {{end}}'`
- **Teclado no noVNC:** x11vnc precisa de `-xkb` (senão Shift e pontuação não funcionam).
- **Dokploy regrava o `.env`** com aspas duplas e `\$`; a senha em `OPENBOT_SENHA` é sem as aspas.
- **TURN sem TLS (5349):** não há certificado para o coturn; só a porta 3478 é usada.

## Segurança

- Tela do OpenBot só com usuário/senha (basic auth no Traefik) e HTTPS.
- Login por e-mail do servidor de contas **não** fica na internet (mostra o código na resposta).
- Agentes do OpenBot têm acesso total dentro do container — um container por pessoa.
- Segredos ficam só na aba Environment do Dokploy; os `.env.example` daqui não têm valores reais.
