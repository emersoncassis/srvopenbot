#!/bin/bash
# OpenBot em modo DESKTOP dentro do container (sem OPENBOT_SERVER=1, sem conta openbot.run).
# Baseado em resources/hosting/openbot-container da imagem oficial. Diferenças:
#  - não exporta OPENBOT_SERVER=1 (o app roda como desktop, contas são opcionais);
#  - a tela :0 (onde fica a janela do OpenBot) tem openbox e é servida por x11vnc + noVNC na porta 6080.
set -euo pipefail
umask 077

fail() { echo "$*" >&2; exit 1; }

size() {
  if [[ ${1:-} =~ ^([1-9][0-9]{2,3})x([1-9][0-9]{2,3})$ ]]; then echo "$1"; else echo "$2"; fi
}

[ "$(id -u)" -ne 0 ] || fail "Rode como o usuário da imagem, não como root."
[ -w "$HOME" ] || fail "Sem permissão de escrita em $HOME."
unshare --user --map-root-user true 2>/dev/null ||
  fail "Sem user namespace para o sandbox do Electron. Use --security-opt seccomp=seccomp.json."

mkdir -p "$XDG_RUNTIME_DIR"
chmod 0700 "$XDG_RUNTIME_DIR"
rm -f "$XDG_RUNTIME_DIR/control.sock"

session=$(dbus-launch --sh-syntax)
eval "$session"

SCREEN=$(size "${OPENBOT_SCREEN_SIZE:-}" 1600x900)
rm -f /tmp/.X0-lock /tmp/.X11-unix/X0 /tmp/.X1-lock /tmp/.X11-unix/X1
(Xvfb :0 -screen 0 "${SCREEN}x24" -nolisten tcp -noreset >/dev/null 2>&1 &)
(Xvfb :1 -screen 0 "$(size "${OPENBOT_DISPLAY_SIZE:-}" 1280x800)x24" -nolisten tcp -wr -noreset >/dev/null 2>&1 &)
export DISPLAY=:0 OPENBOT_AGENT_DISPLAY=:1
for display in :0 :1; do
  for _ in $(seq 1 100); do
    xdpyinfo -display "$display" >/dev/null 2>&1 && break
    sleep 0.1
  done
  xdpyinfo -display "$display" >/dev/null 2>&1 || fail "A tela virtual $display não subiu."
done
xsetroot -display :0 -solid '#1a1a1a' -cursor_name left_ptr || true
xsetroot -display :1 -cursor_name left_ptr || true

# Gerenciador de janelas nas duas telas (barra de título, foco, maximizar).
(DISPLAY=:0 bash -c 'while xdpyinfo >/dev/null 2>&1; do openbox >/dev/null 2>&1; sleep 2; done' </dev/null &)
(DISPLAY=:1 bash -c 'while xdpyinfo >/dev/null 2>&1; do openbox >/dev/null 2>&1; sleep 2; done' </dev/null &)

# VNC só em localhost; o acesso externo passa pelo noVNC (6080), que fica atrás do Traefik com senha.
(bash -c 'while true; do x11vnc -display :0 -localhost -rfbport 5900 -forever -shared -nopw -quiet -noxdamage -xkb -noxrecord -noxfixes >/dev/null 2>&1; sleep 2; done' </dev/null &)
(bash -c 'while true; do websockify --web /usr/share/novnc 6080 localhost:5900 >/dev/null 2>&1; sleep 2; done' </dev/null &)

# Servidor de contas compartilhado (projeto "OpenBot Contas"). O app so aceita http em 127.0.0.1,
# entao o socat traz o servidor para 127.0.0.1:3100 dentro deste container.
if [ -n "${OPENBOT_AUTH_UPSTREAM:-}" ]; then
  (bash -c 'while true; do socat TCP-LISTEN:3100,bind=127.0.0.1,fork,reuseaddr TCP:"$OPENBOT_AUTH_UPSTREAM"; sleep 2; done' </dev/null &)
  export OPENBOT_AUTH_API_URL=http://127.0.0.1:3100
fi

state="$HOME/.config/openbot-container"
keyrings="$HOME/.local/share/keyrings"
mkdir -p "$state" "$keyrings"
if [ ! -s "$state/keyring-password" ] && [ -e "$keyrings/login.keyring" ]; then
  fail "O keyring existe, mas falta $state/keyring-password."
fi
if [ ! -s "$state/keyring-password" ]; then
  temporary=$(mktemp "$state/keyring-password.XXXXXX")
  head -c 32 /dev/urandom | base64 | tr -d '\n' >"$temporary"
  mv -f "$temporary" "$state/keyring-password"
fi
printf login >"$keyrings/default"
unlocked=$(gnome-keyring-daemon --unlock --components=secrets <"$state/keyring-password")
eval "$unlocked"
started=$(gnome-keyring-daemon --start --components=secrets)
eval "$started"
export GNOME_KEYRING_CONTROL

chromium=()
shm=$(df --output=size -k /dev/shm 2>/dev/null | tail -n 1 | tr -d ' ') || shm=0
[ "${shm:-0}" -ge 1048576 ] 2>/dev/null || chromium+=(--disable-dev-shm-usage)

unset OPENBOT_SERVER
exec /opt/OpenBot/app/openbot --password-store=gnome-libsecret "${chromium[@]}"
