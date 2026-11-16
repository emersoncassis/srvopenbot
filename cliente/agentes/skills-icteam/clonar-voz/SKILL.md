---
name: clonar-voz
description: "Clona a voz do dono da conta (com autorização) e gera narração, locução de Reels, dublagem e troca de voz com a ElevenLabs. Use quando pedirem voz clonada, narração com a minha voz, locução, voiceover, dublar um vídeo ou trocar a voz de um áudio."
---

# Voz clonada e narração (ElevenLabs)

## Antes de tudo

- **Consentimento:** só clone a voz de quem pediu e é dono da voz (o próprio usuário) ou de alguém que autorizou por escrito.
  Nunca clone voz de famoso, cliente ou terceiro sem autorização. Registre na memória quem autorizou e quando.
- **Chave da API:** precisa de `ELEVENLABS_API_KEY`. Nunca peça a chave no chat. Use a ferramenta de chave do OpenBot
  (`openbot.list_api_keys` para ver se já existe; `openbot.request_api_key` para pedir, nome `ELEVENLABS_API_KEY`) — o OpenBot abre um campo seguro.
  Outra opção: o app ElevenLabs da Loja (Loja → Apps → ElevenLabs).
- Clonagem instantânea precisa de plano pago na ElevenLabs (Starter ou maior). Avise o custo antes.

## 1. Amostra da voz

Peça 1 a 3 minutos de áudio limpo da pessoa falando (sem música, sem eco). Limpe e padronize:

```bash
ffmpeg -y -i amostra-original.m4a -ac 1 -ar 44100 -af "highpass=f=80,afftdn,loudnorm=I=-16" /data/Videos/voz/amostra.mp3
```

## 2. Criar a voz clonada (Instant Voice Cloning)

```bash
curl -s https://api.elevenlabs.io/v1/voices/add -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F name="Voz do Yago" -F "files=@/data/Videos/voz/amostra.mp3" -F remove_background_noise=true
# resposta: {"voice_id": "..."}  -> salve o voice_id como memória (não é segredo)
```

Listar vozes: `curl -s https://api.elevenlabs.io/v1/voices -H "xi-api-key: $ELEVENLABS_API_KEY"`.

## 3. Narração com a voz

```bash
curl -s "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "content-type: application/json" \
  -d '{"text":"Seu roteiro aqui.","model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.45,"similarity_boost":0.85,"style":0.2}}' \
  -o /data/Videos/<projeto>/public/narracao.mp3
```

- Português: `eleven_multilingual_v2` (mais natural) ou `eleven_flash_v2_5` (rápido e barato). Para emoção e entonação, `eleven_v3`.
- Escreva o roteiro como se fala: frases curtas, números por extenso, pontuação marcando as pausas.
- Confira a pronúncia de nomes e marcas ouvindo o resultado (`ffprobe` para duração) antes de montar.

## 4. Montar no vídeo

```bash
# narração por cima do vídeo, mantendo o som original baixo
ffmpeg -y -i video.mp4 -i narracao.mp3 -filter_complex "[0:a]volume=0.15[a0];[a0][1:a]amix=inputs=2:duration=longest[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac saida.mp4
```

Ou coloque `narracao.mp3` em `public/` do projeto Remotion e gere a legenda dela com `legendar` (skill `estudio-video`).

## Outros usos

- **Trocar a voz de um áudio** (fala com a entonação da pessoa, timbre da voz clonada): `POST /v1/speech-to-speech/$VOICE_ID` com `-F audio=@arquivo.mp3` — veja a skill `voice-changer`.
- **Dublar um vídeo** para inglês ou espanhol mantendo a voz: skill `dubbing`.
- **Efeitos sonoros e trilha**: skills `sound-effects` e `music`.
- **Transcrever**: o comando local `legendar` (grátis) ou a skill `speech-to-text`.

## Regras

- Sempre entregue a narração para aprovação antes de publicar.
- Avise quando a voz é sintética se a plataforma exigir rótulo de conteúdo gerado por IA (TikTok, Instagram e YouTube pedem).
- Futuro: clonagem local (sem custo de API) no computador com GPU do Rafael — não roda neste servidor.
