#!/bin/bash
# Gera o bloco de Environment de um OpenBot cliente novo, com senha aleatória e o hash dela.
#
#   bash novo-cliente.sh fulano seudominio.com.br
#
# Cole a saída na aba Environment do serviço "openbot" do projeto novo (duplicado do OpenBot Template).
set -euo pipefail
NOME=${1:?Uso: novo-cliente.sh <nome> <dominio>}
DOMINIO=${2:?Uso: novo-cliente.sh <nome> <dominio>}
[[ $NOME =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] || { echo "Nome: só minúsculas, números e hífen." >&2; exit 1; }

SENHA=$(openssl rand -base64 30 | tr -dc 'A-Za-z0-9' | cut -c1-20)
HASH=$(openssl passwd -apr1 "$SENHA")

cat <<EOF
INSTANCIA=$NOME
OPENBOT_HOST=$NOME.openbot.$DOMINIO
OPENBOT_TAG=0.71.0
OPENBOT_SCREEN_SIZE=1600x900
OPENBOT_USUARIO=$NOME
OPENBOT_SENHA=$SENHA
OPENBOT_BASIC_AUTH='$NOME:$HASH'
OPENBOT_REMOTE_SIGNAL_URL=wss://signal.openbot.$DOMINIO/v1/signal
OPENBOT_MOBILE_AUTH_API_URL=https://contas.openbot.$DOMINIO
EOF
