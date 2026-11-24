# Notas de Sessão (`v1.1.0`)

## Feito
- **PRs integrados na `main`:** `#22` (RBS), `#15` (Definitive Edition EN/PT-BR + intro player), `#17` (Campanhas, Character Packs, ConflictEngine 3 estados, Seed Mutator C++) e `#21` (Issues #16 Música Customizada + Seletor Visual no F1 + Jukebox Global + `mods/music/Configurar_Musica.bat` + Issue #7 Modos Widescreen 2D).
- Removido `.github/workflows/codeql-python.yml` duplicado (mantendo `.github/workflows/codeql.yml` que já cobre `c-cpp` e `python`).
- Removido `mods/intro/opening.mp4` do staging de release pública em `tools/package_recomplauncher.py` (clean-room estrito) e liberados os arquivos `mods/music/{README.md,configurar_musica.py,Configurar_Musica.bat}` na allowlist de `tools/rbs_artifact.py`.
- Documentação atualizada para `v1.1.0` (`README.md`, `CHANGELOG.md`, `.release-please-manifest.json`, `ROADMAP.md`, `HANDOFF.md`, `NOTAS.md`, `docs/DECISIONS.md` ADR-014, `docs/CREDITS.md`).
- Pacote padrão RecompLauncher `CastlevaniaDawnOfSorrowRecomp-v1.1.0-Windows-x64.zip` + `.sha256` gerado e validado por `package_recomplauncher.py` + `rbs_artifact.py`.

## Falta / Próximos passos
- Corrigir movimento invertido no *Albus Mode* ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
- Zerar campanhas experimentais (*Eternity of Sorrow 1.2*, *Model ZX*, *Model Omega*) para promover de `unverified` para `verified`.
- Publicar comentários de encerramento/resposta nas Issues #16 e #7 após confirmação do usuário.

## Decisões
- **ADR-014:** Custom Music usa decodificadores nativos (RIFF/WAVE + `dr_mp3.h` + `stb_vorbis.c`) sem DLLs + mute seletivo PXI `MUTE_TRACK` no slot dinâmico da ARM7; Widescreen 2D entrega 3 modos honestos (Theatre, Smart Crop 16:9, Balanced 16:10) sem distorção e sem prometer câmera 2D descompilada antes da hora.
- Recursos experimentais ficam explicitamente marcados na página inicial (`README.md`), no `CHANGELOG.md` e nas notas da release `v1.1.0`.
