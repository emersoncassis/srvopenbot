# syntax=docker/dockerfile:1.7
# OpenBot em modo desktop (sem conta openbot.run), com a tela acessível pelo navegador via noVNC.
# Base: imagem oficial. Acrescenta janela (openbox), VNC (x11vnc) e noVNC (websockify)
# e o ESTÚDIO DE VÍDEO que os agentes usam pelo terminal:
#   ffmpeg, ImageMagick, Remotion (Node 22 + Chrome headless), legendas automáticas (faster-whisper),
#   yt-dlp e a pesquisa de tendências last30days. Comandos: novo-video, renderizar, legendar, cortar-silencio,
#   baixar-referencia, tendencias. Detalhes: /opt/estudio-video/LEIA-ME.md
ARG OPENBOT_TAG=latest
FROM ghcr.io/nightly-labs/openbot:${OPENBOT_TAG}
USER root
RUN apt-get update \
  && apt-get install --yes --no-install-recommends openbox x11vnc novnc websockify python3-numpy socat \
       ffmpeg imagemagick python3-venv xz-utils fonts-noto-core fonts-noto-color-emoji fonts-roboto fonts-open-sans \
  && rm -rf /var/lib/apt/lists/*
COPY openbot-desktop-entrypoint.sh /usr/local/bin/openbot-desktop-entrypoint
RUN chmod 0755 /usr/local/bin/openbot-desktop-entrypoint \
  && printf '<!doctype html><meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=1&resize=scale&reconnect=1">' >/usr/share/novnc/index.html

# ---------- Estúdio de vídeo ----------
ARG NODE_VERSION=22.12.0
ARG REMOTION_SKILLS_COMMIT=3e20ac7
ARG LAST30DAYS_COMMIT=f32f440
RUN curl -fsSL https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz | tar -xJ -C /opt \
  && mv /opt/node-v${NODE_VERSION}-linux-x64 /opt/node
ENV PATH=/opt/node/bin:/opt/ferramentas/venv/bin:$PATH

# Python: legendas (faster-whisper, modelo "small" já baixado) e yt-dlp
RUN python3 -m venv /opt/ferramentas/venv \
  && /opt/ferramentas/venv/bin/pip install --no-cache-dir faster-whisper yt-dlp \
  && /opt/ferramentas/venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8', download_root='/opt/ferramentas/modelos')"

# Pesquisa de tendências (MIT, github.com/mvanhorn/last30days-skill) e skills oficiais do Remotion (github.com/remotion-dev/skills)
RUN git clone -q https://github.com/mvanhorn/last30days-skill /opt/ferramentas/last30days \
  && git -C /opt/ferramentas/last30days checkout -q ${LAST30DAYS_COMMIT} \
  && rm -rf /opt/ferramentas/last30days/.git /opt/ferramentas/last30days/skills/last30days/assets \
  && git clone -q https://github.com/remotion-dev/skills /opt/estudio-video/skills-remotion \
  && git -C /opt/estudio-video/skills-remotion checkout -q ${REMOTION_SKILLS_COMMIT} \
  && rm -rf /opt/estudio-video/skills-remotion/.git

# Modelo Remotion: Reels/TikTok/Shorts 1080x1920 com legenda animada, e o vídeo horizontal 1920x1080
COPY <<'EOF' /opt/estudio-video/modelo/package.json
{
  "name": "video",
  "private": true,
  "scripts": { "studio": "remotion studio", "render": "remotion render" }
}
EOF
COPY <<'EOF' /opt/estudio-video/modelo/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022", "module": "ES2022", "moduleResolution": "bundler", "jsx": "react-jsx",
    "strict": true, "skipLibCheck": true, "esModuleInterop": true, "lib": ["DOM", "ES2022"]
  },
  "include": ["src"]
}
EOF
COPY <<'EOF' /opt/estudio-video/modelo/remotion.config.ts
import { Config } from "@remotion/cli/config";
Config.setVideoImageFormat("jpeg");
Config.setConcurrency(1);
Config.setOverwriteOutput(true);
EOF
COPY <<'EOF' /opt/estudio-video/modelo/src/index.ts
import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";
registerRoot(RemotionRoot);
EOF
COPY <<'EOF' /opt/estudio-video/modelo/src/Root.tsx
import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
import { VideoLegendado, Props } from "./VideoLegendado";

const FPS = 30;
const metadados: CalculateMetadataFunction<Props> = ({ props }) => ({
  durationInFrames: Math.max(1, Math.ceil((props.duracaoSeg || 5) * FPS)),
});
const padrao: Props = {
  video: "entrada.mp4", legendas: "legendas.json", duracaoSeg: 5,
  titulo: "", corDestaque: "#FFD400", posicaoLegenda: 0.72, musica: "", volumeMusica: 0.12,
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Reels" component={VideoLegendado} fps={FPS} width={1080} height={1920}
      defaultProps={padrao} calculateMetadata={metadados} />
    <Composition id="Horizontal" component={VideoLegendado} fps={FPS} width={1920} height={1080}
      defaultProps={{ ...padrao, posicaoLegenda: 0.8 }} calculateMetadata={metadados} />
  </>
);
EOF
COPY <<'EOF' /opt/estudio-video/modelo/src/VideoLegendado.tsx
import React, { useEffect, useState } from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, continueRender, delayRender,
  interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { Caption, createTikTokStyleCaptions } from "@remotion/captions";

export type Props = {
  video: string; legendas: string; duracaoSeg: number; titulo: string;
  corDestaque: string; posicaoLegenda: number; musica: string; volumeMusica: number;
};

const Pagina: React.FC<{ tokens: { text: string; fromMs: number; toMs: number }[]; inicioMs: number; cor: string }> = ({ tokens, inicioMs, cor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const agoraMs = inicioMs + (frame / fps) * 1000;
  const entrada = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 6 });
  return (
    <div style={{ transform: `scale(${interpolate(entrada, [0, 1], [0.85, 1])})`, textAlign: "center", padding: "0 60px",
      fontFamily: "Montserrat, 'Noto Sans', sans-serif", fontWeight: 900, fontSize: 84, lineHeight: 1.1,
      textTransform: "uppercase", whiteSpace: "pre-wrap", color: "white",
      textShadow: "0 0 12px rgba(0,0,0,.9), 0 6px 0 rgba(0,0,0,.85)", WebkitTextStroke: "3px black" }}>
      {tokens.map((t, i) => {
        const ativa = t.fromMs <= agoraMs && t.toMs > agoraMs;
        return <span key={i} style={{ color: ativa ? cor : "white" }}>{t.text}</span>;
      })}
    </div>
  );
};

export const VideoLegendado: React.FC<Props> = (p) => {
  const { fps } = useVideoConfig();
  const [legendas, setLegendas] = useState<Caption[] | null>(null);
  const [handle] = useState(() => delayRender("carregando legendas"));
  useEffect(() => {
    if (!p.legendas) { setLegendas([]); continueRender(handle); return; }
    fetch(staticFile(p.legendas)).then((r) => (r.ok ? r.json() : [])).catch(() => [])
      .then((j) => { setLegendas(j as Caption[]); continueRender(handle); });
  }, [handle, p.legendas]);
  const { pages } = createTikTokStyleCaptions({ captions: legendas ?? [], combineTokensWithinMilliseconds: 900 });
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {p.video ? <OffthreadVideo src={staticFile(p.video)} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : null}
      {p.musica ? <Audio src={staticFile(p.musica)} volume={p.volumeMusica} /> : null}
      {p.titulo ? (
        <Sequence durationInFrames={Math.round(2.5 * fps)}>
          <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 160 }}>
            <div style={{ background: p.corDestaque, color: "black", fontFamily: "Montserrat, 'Noto Sans', sans-serif",
              fontWeight: 900, fontSize: 64, padding: "18px 36px", borderRadius: 18, maxWidth: "85%", textAlign: "center" }}>{p.titulo}</div>
          </AbsoluteFill>
        </Sequence>
      ) : null}
      {pages.map((pg, i) => {
        const prox = pages[i + 1]?.startMs ?? pg.startMs + pg.durationMs;
        const de = Math.round((pg.startMs / 1000) * fps);
        const dur = Math.max(1, Math.round(((Math.min(prox, pg.startMs + pg.durationMs + 400) - pg.startMs) / 1000) * fps));
        return (
          <Sequence key={i} from={de} durationInFrames={dur}>
            <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", top: `${p.posicaoLegenda * 100}%` }}>
              <Pagina tokens={pg.tokens} inicioMs={pg.startMs} cor={p.corDestaque} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
EOF
RUN mkdir -p /opt/estudio-video/modelo/public && cd /opt/estudio-video/modelo \
  && V=$(npm view remotion version) \
  && npm install --no-audit --no-fund --loglevel=error remotion@$V @remotion/cli@$V @remotion/captions@$V \
       @remotion/media-utils@$V @remotion/transitions@$V @remotion/google-fonts@$V @remotion/renderer@$V react@19 react-dom@19 typescript \
  && npx remotion browser ensure \
  && echo "$V" >/opt/estudio-video/REMOTION_VERSION

# Comandos do estúdio
COPY <<'EOF' /usr/local/bin/novo-video
#!/bin/bash
# novo-video <nome> [arquivo-de-video]  -> cria /data/Videos/<nome> (projeto Remotion pronto) e copia o vídeo como public/entrada.mp4
set -euo pipefail
[ -n "${1:-}" ] || { echo "uso: novo-video <nome> [video]"; exit 1; }
D="/data/Videos/$1"; mkdir -p "$D/public" "$D/saida"
cp -r --update=none /opt/estudio-video/modelo/src /opt/estudio-video/modelo/package.json /opt/estudio-video/modelo/tsconfig.json /opt/estudio-video/modelo/remotion.config.ts "$D/"
ln -sfn /opt/estudio-video/modelo/node_modules "$D/node_modules"
if [ -n "${2:-}" ]; then ffmpeg -loglevel error -y -i "$2" -c:v libx264 -preset veryfast -crf 20 -c:a aac -movflags +faststart "$D/public/entrada.mp4"; fi
echo "Projeto: $D  (edite src/, coloque mídia em public/, rode: renderizar $1)"
EOF
COPY <<'EOF' /usr/local/bin/renderizar
#!/bin/bash
# renderizar <nome> [Reels|Horizontal] [props-json-extra]  -> /data/Videos/<nome>/saida/<nome>-<composição>.mp4
set -euo pipefail
N="${1:?uso: renderizar <nome> [Reels|Horizontal] [props]}"; C="${2:-Reels}"; X="${3:-}"; [ -n "$X" ] || X='{}'
D="/data/Videos/$N"; cd "$D"
DUR=5; [ -f public/entrada.mp4 ] && DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 public/entrada.mp4)
PROPS=$(python3 -c 'import json,sys; p={"duracaoSeg": float(sys.argv[1])}; p.update(json.loads(sys.argv[2])); print(json.dumps(p))' "$DUR" "$X")
nice -n 10 npx remotion render src/index.ts "$C" "saida/$N-$C.mp4" --props="$PROPS" --concurrency=1 --log=error
echo "Pronto: $D/saida/$N-$C.mp4"
EOF
COPY <<'EOF' /usr/local/bin/legendar
#!/opt/ferramentas/venv/bin/python
"""legendar <video-ou-audio> [saida-sem-extensão] [idioma]
Gera <saida>.json (legendas palavra a palavra no formato do Remotion @remotion/captions) e <saida>.srt.
Padrão: ao lado do arquivo; idioma pt. Para um projeto: legendar /data/Videos/x/public/entrada.mp4 /data/Videos/x/public/legendas"""
import json, os, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
if len(sys.argv) < 2: sys.exit(__doc__)
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0]; lang = sys.argv[3] if len(sys.argv) > 3 else "pt"
# áudio lido pelo ffmpeg (16 kHz mono), sem depender da versão do PyAV
pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8", download_root="/opt/ferramentas/modelos", cpu_threads=2)
segs, _ = m.transcribe(audio, language=lang, word_timestamps=True, vad_filter=True)
caps, srt = [], []
def ts(s): h, r = divmod(s, 3600); mi, se = divmod(r, 60); return "%02d:%02d:%06.3f" % (h, mi, se)
for i, s in enumerate(segs, 1):
    srt.append("%d\n%s --> %s\n%s\n" % (i, ts(s.start).replace(".", ","), ts(s.end).replace(".", ","), s.text.strip()))
    for w in (s.words or []):
        caps.append({"text": (" " if caps else "") + w.word.strip(), "startMs": int(w.start * 1000), "endMs": int(w.end * 1000),
                     "timestampMs": int((w.start + w.end) * 500), "confidence": round(w.probability, 3)})
json.dump(caps, open(out + ".json", "w", encoding="utf-8"), ensure_ascii=False)
open(out + ".srt", "w", encoding="utf-8").write("\n".join(srt))
print("ok:", out + ".json", out + ".srt", len(caps), "palavras")
EOF
COPY <<'EOF' /usr/local/bin/cortar-silencio
#!/bin/bash
# cortar-silencio <entrada> <saida> [limiar-dB=-35] [min-seg=0.45]  -> remove pausas (estilo jump cut)
set -euo pipefail
I="${1:?uso: cortar-silencio entrada saida}"; O="${2:?}"; T="${3:--35}"; M="${4:-0.45}"
python3 - "$I" "$O" "$T" "$M" <<'PY'
import re, subprocess, sys
i, o, t, m = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", i, "-af", "silencedetect=noise=%sdB:d=%s" % (t, m), "-f", "null", "-"], capture_output=True, text=True).stderr
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", i]).decode())
ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
keep, cur = [], 0.0
for a, b in zip(ini, fim + [dur]):
    if a - cur > 0.05: keep.append((cur, a + 0.08))
    cur = max(b - 0.08, 0)
if dur - cur > 0.05: keep.append((cur, dur))
sel = "+".join("between(t,%.3f,%.3f)" % k for k in keep) or "1"
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", i, "-vf", "select='%s',setpts=N/FRAME_RATE/TB" % sel,
                "-af", "aselect='%s',asetpts=N/SR/TB" % sel, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", o], check=True)
print("ok: %s (%d trechos mantidos de %.1fs)" % (o, len(keep), dur))
PY
EOF
COPY <<'EOF' /usr/local/bin/baixar-referencia
#!/bin/bash
# baixar-referencia <url> [pasta=/data/Videos/referencias]  -> baixa vídeo público (TikTok, Reels, YouTube) para estudar a edição.
# Use só como referência; não repostar conteúdo de terceiros.
set -euo pipefail
U="${1:?uso: baixar-referencia <url> [pasta]}"; P="${2:-/data/Videos/referencias}"; mkdir -p "$P"
yt-dlp -q --no-playlist -f "bv*[height<=1920]+ba/b" --merge-output-format mp4 -o "$P/%(extractor)s-%(id)s.%(ext)s" --write-info-json "$U"
ls -t "$P" | head -3
EOF
COPY <<'EOF' /usr/local/bin/tendencias
#!/bin/bash
# tendencias "<assunto>"  -> roda a pesquisa last30days (Reddit, YouTube, TikTok, X, HN, web) sobre o assunto.
# Para o fluxo completo (síntese, comparação), leia /opt/ferramentas/last30days/skills/last30days/SKILL.md
export SKILL_DIR=/opt/ferramentas/last30days/skills/last30days LAST30DAYS_PYTHON=/usr/bin/python3
exec /usr/bin/python3 "$SKILL_DIR/scripts/last30days.py" "$@"
EOF
COPY <<'EOF' /opt/estudio-video/LEIA-ME.md
# Estúdio de vídeo do OpenBot

Tudo roda pelo terminal deste servidor. Projetos e vídeos ficam em /data/Videos (persistente).

| Comando | O que faz |
|---|---|
| `novo-video <nome> [video]` | Cria /data/Videos/<nome> com o modelo Remotion (Reels 1080x1920 e Horizontal 1920x1080, legenda animada) |
| `legendar <video> [saida] [pt]` | Transcreve com faster-whisper (modelo small, CPU) e gera legendas palavra a palavra (.json do Remotion) e .srt |
| `cortar-silencio <in> <out>` | Tira as pausas (jump cut) |
| `renderizar <nome> [Reels\|Horizontal] '{"titulo":"..."}'` | Renderiza com Remotion para /data/Videos/<nome>/saida |
| `baixar-referencia <url>` | Baixa um vídeo público para estudar a edição (yt-dlp) |
| `tendencias "<assunto>"` | Pesquisa o que está em alta nos últimos 30 dias |
| `ffmpeg`, `ffprobe`, `convert` (ImageMagick) | Corte, junção, áudio, formatos, imagens, thumbnails |

Fluxo de um Reels: `novo-video aula1 /data/Downloads/bruto.mp4` → `cortar-silencio` (opcional; depois copie para public/entrada.mp4)
→ `legendar /data/Videos/aula1/public/entrada.mp4 /data/Videos/aula1/public/legendas` → `renderizar aula1 Reels '{"titulo":"3 erros que..."}'`.

Props do modelo: video, legendas, titulo, corDestaque (#FFD400), posicaoLegenda (0-1), musica (arquivo em public/), volumeMusica.
Para animações e cenas novas, edite src/ seguindo as skills oficiais em /opt/estudio-video/skills-remotion/skills/*/SKILL.md
(comece por remotion-best-practices). Renderizar é pesado: um vídeo por vez.
Voz (narração, clonagem, dublagem, efeitos, música): ElevenLabs pela API (chave no Vault, nunca no chat).
Licença: o Remotion é grátis para pessoas físicas e empresas de até 3 pessoas; acima disso precisa de licença (remotion.pro).
EOF
RUN chmod 0755 /usr/local/bin/novo-video /usr/local/bin/renderizar /usr/local/bin/legendar /usr/local/bin/cortar-silencio \
       /usr/local/bin/baixar-referencia /usr/local/bin/tendencias \
  && chown -R openbot:openbot /opt/estudio-video /opt/ferramentas/modelos
ENV NPM_CONFIG_UPDATE_NOTIFIER=false NPM_CONFIG_FUND=false REMOTION_DISABLE_TELEMETRY=1
USER openbot
EXPOSE 6080
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/openbot-desktop-entrypoint"]
