#!/bin/bash
# Sobe o servidor de contas local. As contas ficam em /state (volume auth-state).
# As chaves e segredos do acesso remoto (celular) vêm da aba Environment do Dokploy.
set -euo pipefail
cd /src/apps/auth-api
mkdir -p /state .wrangler
rm -rf .wrangler/state
ln -sfn /state .wrangler/state

secret_file=/state/site-report-hash-secret
[ -s "$secret_file" ] || head -c 48 /dev/urandom | base64 | tr -d '\n=/+' >"$secret_file"

# Variaveis do Worker local. Os campos de e-mail vazios desligam o envio de e-mail.
{
  echo "AUTH_EXPOSE_DEVELOPMENT_CODE=true"
  echo "EMAIL_SMTP_HOST="
  echo "EMAIL_SMTP_PORT="
  echo "EMAIL_SMTP_USERNAME="
  echo "EMAIL_SMTP_PASSWORD="
  echo "EMAIL_FROM="
  echo "EMAIL_LICENSE_FROM="
  echo "SITE_REPORT_HASH_SECRET=$(cat "$secret_file")"
  echo "HOSTED_SERVERS_ENABLED=false"
  echo "SITE_PUBLISH_ENABLED=false"
  # O build traz os enderecos dos servidores da OpenBot (Signal, webhooks, Cloudflare, GitHub App).
  # Aqui tudo aponta para o Signal proprio (projeto OpenBot Remoto) ou fica vazio.
  echo "REMOTE_SIGNAL_HOMES='a=${REMOTE_SIGNAL_URL:-}'"
  echo "REMOTE_SIGNAL_HOME_LOCATIONS="
  echo "REMOTE_AUTH_WEBHOOK_URLS='${REMOTE_AUTH_WEBHOOK_URL:-}'"
  echo "SIGNAL_ENTRY_ZONE_ID="
  echo "GITHUB_APP_CLIENT_ID="
  echo "HOSTED_SERVERS_ALLOWED_USER_IDS="
  for key in REMOTE_TICKET_KEY_ID REMOTE_TICKET_PRIVATE_JWK REMOTE_TICKET_PUBLIC_JWKS REMOTE_SIGNAL_URL \
    REMOTE_AUTH_WEBHOOK_URL REMOTE_AUTH_WEBHOOK_SECRET SKILLS_ADMIN_TOKEN; do
    value="${!key:-}"
    [ -n "$value" ] && printf "%s='%s'\n" "$key" "$value"
  done
} >dist/server/.dev.vars

node /src/node_modules/wrangler/bin/wrangler.js d1 migrations apply openbot-auth --local

# Escuta na rede interna do Dokploy. Os OpenBots chegam em openbot-contas:3101.
# Na internet ficam so os caminhos do celular (labels do Traefik no compose); o login por e-mail nao.
# Nomes aceitos alem de localhost: o nome interno (Signal) e o endereco publico (celular).
export __VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS="openbot-contas${CONTAS_HOST:+,$CONTAS_HOST}"
exec node /src/node_modules/vite/bin/vite.js preview --host 0.0.0.0 --port 3101 --strictPort
