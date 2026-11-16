#!/bin/bash
# Gera as chaves e segredos do servidor OpenBot (Contas + Remoto) e imprime os dois blocos de
# Environment prontos para colar no Dokploy. Rode na VPS (precisa de docker e openssl).
#
#   bash gerar-segredos.sh seudominio.com.br 203.0.113.10
#
# Guarde a saída só no Dokploy: ela tem a chave privada dos tíquetes.
set -euo pipefail
DOMINIO=${1:?Uso: gerar-segredos.sh <dominio> <ip-publico>}
IP=${2:?Uso: gerar-segredos.sh <dominio> <ip-publico>}
KID=${KID:-openbot-proprio-1}

segredo() { openssl rand -base64 48 | tr -d '\n=/+' | cut -c1-64; }

keys=$(docker run --rm -e KID="$KID" node:24-slim node -e '
const { generateKeyPairSync } = require("node:crypto");
const meta = { kid: process.env.KID, alg: "ES256", use: "sig" };
const { privateKey, publicKey } = generateKeyPairSync("ec", { namedCurve: "P-256" });
console.log(JSON.stringify({ ...privateKey.export({ format: "jwk" }), ...meta }));
console.log(JSON.stringify({ keys: [{ ...publicKey.export({ format: "jwk" }), ...meta }] }));')
PRIV=$(echo "$keys" | sed -n 1p)
PUB=$(echo "$keys" | sed -n 2p)
WEBHOOK=$(segredo)

cat <<EOF
########## OpenBot Contas — Environment ##########
OPENBOT_REF=v0.71.0
CONTAS_HOST=contas.openbot.$DOMINIO
REMOTE_SIGNAL_URL=wss://signal.openbot.$DOMINIO/v1/signal
REMOTE_AUTH_WEBHOOK_URL=http://openbot-signal:8081/internal/auth-events
REMOTE_TICKET_KEY_ID=$KID
REMOTE_TICKET_PRIVATE_JWK='$PRIV'
REMOTE_TICKET_PUBLIC_JWKS='$PUB'
REMOTE_AUTH_WEBHOOK_SECRET=$WEBHOOK
SKILLS_ADMIN_TOKEN=$(segredo)

########## OpenBot Remoto — Environment ##########
OPENBOT_REF=v0.71.0
SIGNAL_HOST=signal.openbot.$DOMINIO
TURN_HOST=turn.openbot.$DOMINIO
TURN_PUBLIC_IP=$IP
REMOTE_TICKET_PUBLIC_JWKS='$PUB'
REMOTE_SESSION_SECRET=$(segredo)
REMOTE_AUTH_WEBHOOK_SECRET=$WEBHOOK
REMOTE_METRICS_TOKEN=$(segredo)
TURN_SHARED_SECRET=$(segredo)
EOF
