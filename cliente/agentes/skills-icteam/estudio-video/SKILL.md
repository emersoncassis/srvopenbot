---
name: estudio-video
description: "Edita vídeo de verdade no servidor do OpenBot: corta, tira pausas, legenda automática palavra a palavra, título, música, formatos Reels/TikTok/Shorts (1080x1920) e YouTube (1920x1080), animações com Remotion e ffmpeg. Use sempre que pedirem para editar, cortar, legendar, montar, renderizar ou exportar um vídeo."
---

# Estúdio de vídeo (Remotion + ffmpeg + legendas)

Você edita vídeos rodando comandos no terminal deste servidor. Não diga que não consegue editar: as ferramentas estão instaladas.
Guia rápido: `cat /opt/estudio-video/LEIA-ME.md`.

## Ferramentas

| Comando | Uso |
|---|---|
| `novo-video <nome> [video]` | Cria o projeto em `/data/Videos/<nome>` (modelo Remotion pronto) e converte o bruto para `public/entrada.mp4` |
| `cortar-silencio <in> <out> [-35] [0.45]` | Jump cut: remove pausas e respiros |
| `legendar <video> <saida-sem-ext> [pt]` | Transcreve (faster-whisper) e gera `.json` (legenda palavra a palavra do Remotion) e `.srt` |
| `renderizar <nome> [Reels\|Horizontal] '<props>'` | Renderiza para `/data/Videos/<nome>/saida/` |
| `baixar-referencia <url>` | Baixa um vídeo público para estudar ritmo e edição (não repostar) |
| `ffmpeg` / `ffprobe` / `convert` (ImageMagick) | Qualquer outra coisa: cortar trechos, juntar, acelerar, normalizar áudio, thumbnail, GIF, formatos |

Props do modelo: `titulo` (aparece 2,5 s no início), `corDestaque` (palavra falada; padrão `#FFD400`), `posicaoLegenda` (0 a 1),
`musica` (arquivo em `public/`), `volumeMusica` (0.08 a 0.2), `video`, `legendas`.

## Fluxo padrão de um Reels/TikTok/Shorts

1. Pegue o bruto (o usuário manda pelo chat ou ele está em `/data/Downloads`). Veja duração e formato: `ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 <arquivo>`.
2. `novo-video <nome> <bruto>`.
3. Pausas: `cortar-silencio /data/Videos/<nome>/public/entrada.mp4 /tmp/c.mp4 && mv /tmp/c.mp4 /data/Videos/<nome>/public/entrada.mp4`.
4. Legenda: `legendar /data/Videos/<nome>/public/entrada.mp4 /data/Videos/<nome>/public/legendas`. Leia o `.srt` e corrija nomes e termos errados no `.json` (campo `text`) antes de renderizar.
5. Gancho: escreva um título curto (até 6 palavras) que prenda nos 3 primeiros segundos.
6. `renderizar <nome> Reels '{"titulo":"...","corDestaque":"#FFD400"}'`. Para YouTube horizontal use `Horizontal`.
7. Confira: `ffprobe` na saída e tire 3 quadros para olhar (`ffmpeg -ss 1 -i saida.mp4 -frames:v 1 /tmp/q1.jpg`, idem no meio e no fim).
8. Entregue o arquivo no chat (anexe a saída) com: duração, o que foi feito e 2 opções de legenda do post.

## Mais do que o modelo

- Animações, telas de título, B-roll, transições, gráficos, zoom em palavra-chave: edite `src/` do projeto em React/Remotion.
  Antes, leia as skills oficiais do Remotion em `/opt/estudio-video/skills-remotion/skills/` — comece por `remotion-best-practices/SKILL.md`
  (e `remotion-captions`, `remotion-multimedia`, `remotion-render` quando for o caso).
- Cortes por tempo: `ffmpeg -ss 00:00:05 -to 00:00:20 -i in.mp4 -c:v libx264 -c:a aac out.mp4`.
- Juntar clipes: arquivo `lista.txt` com `file 'a.mp4'` por linha e `ffmpeg -f concat -safe 0 -i lista.txt -c:v libx264 -c:a aac out.mp4`.
- Vertical a partir de horizontal: `-vf "crop=ih*9/16:ih,scale=1080:1920"`.
- Áudio: normalizar `-af loudnorm=I=-14:TP=-1.5:LRA=11` (padrão de redes); tirar ruído `-af afftdn`.
- Thumbnail do YouTube: `convert` (ImageMagick) com quadro do vídeo + texto grande (1280x720).
- Narração, voz clonada, dublagem, efeitos e música: skill `clonar-voz` e as skills da ElevenLabs. Mixe a narração com `ffmpeg -filter_complex amix`.
- Imagem ou vídeo gerado por IA (cenas que não existem): apps Higgsfield, Runway ou fal (Loja → Apps).

## Regras

- Renderizar é pesado (servidor de 2 núcleos): um vídeo por vez, avise que leva alguns minutos.
- Nunca publique sozinho: entregue para aprovação. Publicação é com o Head de Social Media e os bots de integração.
- Não use música ou trecho de terceiros com direitos autorais; prefira a biblioteca do próprio app da rede ou música gerada (ElevenLabs Music).
- Guarde o bruto original; trabalhe em cópias dentro de `/data/Videos/<nome>`.
- Licença do Remotion: grátis para pessoa física e empresa de até 3 pessoas.
