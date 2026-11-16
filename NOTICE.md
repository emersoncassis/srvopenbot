# Origem e licenças

Estes templates instalam e configuram o **OpenBot** da Nightly Labs
(<https://github.com/nightly-labs/openbot>), licenciado sob **PolyForm Noncommercial 1.0.0**.
O código do OpenBot não está neste repositório: os builds baixam a imagem oficial
(`ghcr.io/nightly-labs/openbot`) e o código-fonte da tag escolhida direto do GitHub.

Arquivos derivados do repositório do OpenBot:

- `cliente/openbot-desktop-entrypoint.sh` — baseado em `scripts/hosting/openbot-container`.
- `cliente/seccomp.json` — cópia de `docker/seccomp.json` (perfil padrão do Docker, moby/profiles,
  Apache-2.0, com a regra extra de `clone`/`unshare` do OpenBot).
- `servidor/remoto/turnserver.conf` — baseado em `remote/coturn/turnserver.conf`.

Uso destinado a fins **não comerciais** (pessoal/experimentação), conforme a licença do OpenBot.
