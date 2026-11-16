# OpenBot em modo desktop (sem conta openbot.run), com a tela acessível pelo navegador via noVNC.
# Base: imagem oficial. Acrescenta janela (openbox), VNC (x11vnc) e noVNC (websockify).
ARG OPENBOT_TAG=latest
FROM ghcr.io/nightly-labs/openbot:${OPENBOT_TAG}
USER root
RUN apt-get update \
  && apt-get install --yes --no-install-recommends openbox x11vnc novnc websockify python3-numpy socat \
  && rm -rf /var/lib/apt/lists/*
COPY openbot-desktop-entrypoint.sh /usr/local/bin/openbot-desktop-entrypoint
RUN chmod 0755 /usr/local/bin/openbot-desktop-entrypoint \
  && printf '<!doctype html><meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=1&resize=scale&reconnect=1">' >/usr/share/novnc/index.html
USER openbot
EXPOSE 6080
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/openbot-desktop-entrypoint"]
