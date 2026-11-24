# Handoff — Castlevania: Dawn of Sorrow: Recompiled (`ACVE`)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Current Technical State (`v1.1.1` — `main`)
- **Latest Patch (`v1.1.1`):** Portable `-march=x86-64 -mtune=generic` release build, embedded Windows `app.manifest` (`asInvoker`, `supportedOS`, `PerMonitorV2`, `activeCodePage=UTF-8`) in both `CastlevaniaDawnOfSorrow.exe` (`1.35 MB` with `--gc-sections`) and `runtime/nds_runner.exe`, UTF-8 `read_file` fallback, and clearer ROM mismatch diagnostics.
- **Merged PRs into `main`:** `#22` (RBS incremental build & artifact validation), `#15` (P0/P1/P2 Definitive Edition + PT-BR + native intro player), `#17` (16A–16D campaigns, character packs, 3-state `ConflictEngine`, Native C++ Seed Mutator), and `#21` (Issues #16 Custom Music + F1 Visual Track Mapper + Global Jukebox + Explorer wizard, and #7 2D Widescreen modes).
- **Release `v1.1.0`:** standard RecompLauncher Windows x64 package (`CastlevaniaDawnOfSorrowRecomp-v1.1.0-Windows-x64.zip` + `.sha256`), validated by both `tools/package_recomplauncher.py` (`35` INI keys, `{data}` save-path guard, zero copyrighted ROM/BIOS/intro video) and `tools/rbs_artifact.py` (strict allowlist + CRC + MZ header + SHA-256).
- **Verified Features:**
  - Definitive Edition (EN & PT-BR) and Original USA (EN & PT-BR) at ~60 FPS (`0` dispatch misses, isolated saves).
  - Native Custom Music engine (`.wav`, `.mp3`, `.ogg` — zero external DLLs) with live-verified selective ARM7 BGM muting (`DS BGM = 0`, `DS SFX = 100%`), `F1 -> Audio` Visual Track Mapper, Global Jukebox / Playlist mode, and double-clickable Windows Explorer wizard (`mods/music/Configurar_Musica.bat`).
  - 2D Widescreen presentation modes (`Widescreen Theatre`, `16:9 Smart Crop` with `-24..+24 px` vertical offset, `16:10 Balanced`) with pixel-accurate touch mapping.
- **Experimental / Unverified Features (explicitly flagged in `README.md`, `CHANGELOG.md`, and `v1.1.0` release notes):**
  - *Eternity of Sorrow 1.2* (`unverified`, boot & ~60 FPS perf verified, full playthrough pending).
  - *Albus Mode* (`unverified`, known inverted movement bug tracked in [Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
  - *Model ZX* / *Model Omega* (`unverified`, boot tested, full Julius Mode playthrough pending).
  - Native C++ Seed Mutator (`unverified`, non-progression regular enemy stats/drops only; full progression randomizer remains via `tools/import_dsvrandom.py`).
  - Widescreen 2D presentation (true ARM9 2D camera wide-viewport decompilation tracked in ADR-014 as future work).

### Verification Commands
```powershell
ctest --test-dir generated/build-runner -R "^(dos_enhancements_test|frontend_config_test|screen_layout_test)$" --output-on-failure
python -m unittest discover -s tests -v
python tools/package_recomplauncher.py --validate-only
python tools/prepare_media_assets.py --check-only
```

### Next Steps
1. Fix *Albus Mode* inverted movement bug ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
2. Complete full playthroughs for *Eternity of Sorrow 1.2*, *Model ZX*, and *Model Omega* to promote them to `verified`.
3. Evaluate native Linux / Steam Deck and Android builds with prebuilt SDL3.

---

<a id="português-br"></a>

## Português (BR)

### Estado Técnico Atual (`v1.1.1` — `main`)
- **Patch `v1.1.1`:** Build portátil `-march=x86-64 -mtune=generic`, manifesto Windows `app.manifest` (`asInvoker`, `supportedOS`, `PerMonitorV2`, `activeCodePage=UTF-8`) embutido em `CastlevaniaDawnOfSorrow.exe` (`1,35 MB` com `--gc-sections`) e `runtime/nds_runner.exe`, leitura UTF-8 em `main.cpp` e mensagens claras de erro de ROM.
- **PRs integrados na `main`:** `#22` (pipeline RBS e validação de artefatos), `#15` (P0/P1/P2 Definitive Edition + PT-BR + player nativo de abertura), `#17` (16A–16D campanhas, packs de personagens, `ConflictEngine` 3 estados, Seed Mutator C++ nativo) e `#21` (Issues #16 Música Customizada + Seletor Visual no F1 + Jukebox Global + assistente Explorer, e #7 modos Widescreen 2D).
- **Release `v1.1.0`:** pacote padrão RecompLauncher Windows x64 (`CastlevaniaDawnOfSorrowRecomp-v1.1.0-Windows-x64.zip` + `.sha256`), validado por `tools/package_recomplauncher.py` (`35` chaves INI, guarda `{data}` de saves, zero ROM/BIOS/vídeo protegido) e `tools/rbs_artifact.py` (allowlist estrita + CRC + header MZ + SHA-256).
- **Recursos Verificados:**
  - Definitive Edition (EN e PT-BR) e Original USA (EN e PT-BR) a ~60 FPS (`0` dispatch misses, saves isolados).
  - Motor nativo de Música Customizada (`.wav`, `.mp3`, `.ogg` — sem DLLs externas) com mute seletivo validado ao vivo (`BGM DS = 0`, `SFX DS = 100%`), Seletor Visual por Estágio no `F1 -> Áudio`, Modo Jukebox / Playlist Global e assistente duplo-clique com Windows Explorer (`mods/music/Configurar_Musica.bat`).
  - Modos Widescreen 2D (`Widescreen Teatro`, `16:9 Smart Crop` com offset vertical `-24..+24 px`, `16:10 Equilibrado`) com mapeamento de toque exato.
- **Recursos Experimentais / Não Verificados (sinalizados no `README.md`, `CHANGELOG.md` e release `v1.1.0`):**
  - *Eternity of Sorrow 1.2* (`unverified`, boot e ~60 FPS validados, campanha completa pendente).
  - *Albus Mode* (`unverified`, bug conhecido de movimento invertido na [Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
  - *Model ZX* / *Model Omega* (`unverified`, boot testado, campanha completa pendente).
  - Mutador Nativo por Seed C++ (`unverified`, apenas stats/drops fora da progressão; randomizer completo via `tools/import_dsvrandom.py`).
  - Widescreen 2D de apresentação (descompilação de câmera 2D nativa ARM9 registrada no ADR-014 como trabalho futuro).

### Próximos Passos
1. Investigar e corrigir movimento invertido no *Albus Mode* ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
2. Validar campanhas completas (*Eternity of Sorrow 1.2*, *Model ZX*, *Model Omega*) para promoção a `verified`.
3. Avaliar builds Linux / Steam Deck e Android com SDL3 pré-compilado.
