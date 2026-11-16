#!/bin/bash
# Firewall da VPS do OpenBot/Dokploy. Liga o ufw e bloqueia a porta 3000 (painel Dokploy sem HTTPS).
# Com desfazer automático em 5 minutos (cancelado depois que o acesso for confirmado).
set -euo pipefail

# Desfazer automático: desliga o ufw e libera a 3000 de novo se ninguém cancelar.
systemctl stop fw-rollback.timer fw-rollback.service 2>/dev/null || true
systemd-run --quiet --unit=fw-rollback --on-active=300 /bin/sh -c \
  'ufw --force disable; iptables -D DOCKER-USER -i eth0 -p tcp -m conntrack --ctorigdstport 3000 --ctdir ORIGINAL -j DROP 2>/dev/null; true'

sed -i 's/^IPV6=.*/IPV6=yes/' /etc/default/ufw
ufw --force reset >/dev/null

# Bloqueio da 3000 para fora (o Docker publica portas por fora do ufw; por isso vai na DOCKER-USER).
for f in /etc/ufw/after.rules; do
  cat >>"$f" <<'EOF'

# --- OpenBot/Dokploy: painel na porta 3000 so por dentro (acesso pelo dominio HTTPS) ---
*filter
:DOCKER-USER - [0:0]
-A DOCKER-USER -i eth0 -p tcp -m conntrack --ctorigdstport 3000 --ctdir ORIGINAL -j DROP
-A DOCKER-USER -j RETURN
COMMIT
EOF
done

ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw limit 22/tcp comment 'SSH' >/dev/null
ufw allow 80/tcp comment 'HTTP (Traefik e certificados)' >/dev/null
ufw allow 443/tcp comment 'HTTPS (Traefik)' >/dev/null
ufw allow 443/udp comment 'HTTP/3 (Traefik)' >/dev/null
ufw allow 3478/tcp comment 'OpenBot TURN' >/dev/null
ufw allow 3478/udp comment 'OpenBot TURN' >/dev/null
ufw allow 16384:65535/udp comment 'OpenBot TURN relay' >/dev/null
ufw allow from 10.0.0.0/8 comment 'Redes internas Docker' >/dev/null
ufw allow from 172.16.0.0/12 comment 'Redes internas Docker' >/dev/null
ufw --force enable >/dev/null
ufw status numbered
iptables -S DOCKER-USER
