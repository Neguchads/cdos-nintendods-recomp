# Roadmap — Castlevania: Dawn of Sorrow: Recompiled (ACVE)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Done (Vertical Slice 1 — Bring-Up)
- Inspection and verification of the original USA ROM (`Castlevania - Dawn of Sorrow (USA).nds`, 64 MiB, CRC32 `135737f6`, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`).
- Project pipeline structured with `game.toml`, `tools/setup_toolchains.py`, `tools/prepare_rom.py`, `tools/build.py`, and `play.bat`.
- `RetroPortingToolKit/ndsrecomp` and `recomp-ui` isolated in sibling directories (`..\ndsrecomp` and `..\recomp-ui`).

### Done (Phase 2 — Native Execution of 49k+ Functions, DX12 & Modern Controls)
- Static promotion of `34` banks (`49,059` functions) into `generated/banks-promoted/`.
- Simultaneous keyboard mapping (`WASD + Arrows + Space = Jump (B)`), mouse input on the bottom touch screen for magic seals, and Xbox/PlayStation controller support.

### Done (Phase 3 — 60 FPS in Visible DX12 GPU Window + DXIL `ps_6_0`)
- Pre-compiled GPU fragment shaders in `dos_postprocess.frag.hlsl` -> `dos_gpu_shader_dxil.h`, automatic `SoftRenderer` outside `gl_top` (`0.00 ms` readback), and calibrated audio prebuffer (`kAudioStartFrames = 3072`).

### Done (Phase 4 — Dear ImGui `F1` Menu, 3-Screens Fix, In-Memory PT-BR, RecompLauncher & Multiplatform)
- **Dear ImGui v1.92.9b overlay menu (`F1`):** 6 tabs (*Home*, *Screen & Layout*, *HD Graphics*, *Audio*, *Controls*, *Performance & Dev*), full EN / PT-BR localization (`dos_i18n.{h,cpp}`), Latin Extended TrueType fonts (`0x0020..0x024F`), live GPU calibration (*Brightness*, *Contrast*, *Saturation*, *Vignette*), PiP size (`20..50%`), `VSync`, analog deadzone, pause/mute when unfocused, save states `1–5`, `.sav` backup, FPS Sparkline, and `F12` screenshot capture.
- **Permanent 3-screens bug fix:** suspend `SDL_SetRenderLogicalPresentation` while drawing ImGui and disable legacy `g_runtime_menu_surface` / `menu_texture`, leaving only the 2 real DS screens behind the overlay.
- **In-memory PT-BR translation (`--ptbr-patch`):** delta patch `mods/ptbr/dos-ptbr.dospatch` (`469,280 B`, `4,806` chunks, *romsportugues.com* T1.0) applied in RAM with live `EN <-> PT-BR` switching, paired with `dos_arm9`/`dos_arm7` banks generated with `--validate-live-bytes` (`59.86 FPS` in DX12 benchmark).
- **Dual DXIL + SPIR-V GPU Shaders & Multiplatform Configs:** `dos_gpu_shader_spirv.h` verified live on `vulkan-gpu` (`60.0 FPS`); `CMakePresets.json`, `tools/build_linux.sh`, and `android/` (Gradle/NDK/SDL3) structured and documented in [`docs/MULTIPLATFORM.md`](docs/MULTIPLATFORM.md).

### Done (Phase 5 — Public GitHub Release, RecompLauncher 1.0 SDK, Media Kit & Bilingual Docs)
- **Public GitHub repository (`Neguchads/cdos-nintendods-recomp`):** clean-room `.gitignore`/`.gitattributes`, **Dependabot** (`.github/dependabot.yml` for `github-actions` and `gradle` + security alerts/updates), and **GitHub Actions** (`.github/workflows/ci.yml` on Ubuntu + Windows + clean-room/shellcheck guards).
- **Full RecompLauncher 1.0 SDK & Official Media Kit:** upgraded [`recomplauncher.json`](recomplauncher.json) to named `inputs[game]` with verified USA dump (`CRC32: 135737f6`, `67,108,864` bytes), `config[0].new` (31 default INI keys), `looks`, `actions`, `system`, and `exit_codes`; generated complete artwork kit in [`assets/recomplauncher/`](assets/recomplauncher/) (`icon.png`/`icon.ico` `256x256`, `cover.png`/`cover.jpg` `600x900`, `hero.png`/`hero.jpg` `1920x620`, transparent `logo.png` `1000x500`, `wallpaper.png` `1920x1080`, `artwork.png` `1024x1024`, `catalog-entry.json`) and in-engine captures in [`assets/screenshots/`](assets/screenshots/).
- **Bilingual Documentation (`EN` -> `PT-BR`):** all project documentation (`README.md`, `docs/RECOMPLAUNCHER.md`, `docs/MULTIPLATFORM.md`, `docs/DECISIONS.md`, `docs/rom-analysis.md`, `ROADMAP.md`, `HANDOFF.md`, `NOTAS.md`) written in English first and Brazilian Portuguese second.
- **RecompLauncher `cwd = runtime/` Startup Fix (`v1.0.1`):** updated `recomplauncher.json` `start.args` to resolve `game.toml` and `mods/ptbr/dos-ptbr.dospatch` via `{install}` and `run/bios` via `{data}`, hardened `tools/package_recomplauncher.py` (`validate_manifest` path check + runtime staging ignore filters for `*.ndshp`, `*.jsonl`, `*.bmp`, `*.png`), and added unit tests covering both regressions.
- **Windows Standalone Launcher & Embedded Icon (`CastlevaniaDawnOfSorrow.exe`):** added native static Win32 GUI launcher (`launcher/launcher_win32.cpp`) and Windows resource script (`launcher/app_icon.rc`) built automatically at the end of `python tools/build.py build`, embedding `assets/recomplauncher/icon.ico` into both `CastlevaniaDawnOfSorrow.exe` and `runtime/nds_runner.exe` and bundling the launcher in Windows releases.
- **Native Mouse Combat Bindings, `Q`/`R` Defaults & Per-Key Clear (`F1` Controls):** added mappable mouse buttons (`Mouse Left` = Primary Attack `Y`, `Mouse Right` = Special Attack `A`, `Mouse Mid` = Dash `L`, plus `Mouse X1/X2`) alongside full touchscreen clicks (items, menus, Magic Seals), set `Q = L` and `R = R` natively in Key 1, and added per-key `X` clear buttons, **Clear All Mappings**, and **Restore Default Controls** in the `F1` menu.

### Done (Branch `development` — PR #15: Phase 6 P0/P1/P2)
- **P0:** Pure-Python RFC 3284 VCDIFF & IPS decoder (`tools/vcdiff_ips.py`), mod bundle classifier/importer (`tools/import_mod_bundle.py`, `mods/catalog.json`), and NitroFS/overlay semantic diff (`tools/diff_dos_mods.py`, `mods/reports/definitive-vs-ptbr.json`).
- **P1:** Semantic Definitive Edition + PT-BR composer (`tools/compose_dos_mods.py` -> `mods/definitive/dos-definitive-en.dospatch` `615 KB` + `dos-definitive-ptbr.dospatch` `752 KB`), C++ `dos_mod_profile.{h,cpp}` runtime builder with isolated saves/savestates, `F1` Content & Mods UI, full RecompLauncher + standalone launcher wiring, and complete mod author credits in [`docs/CREDITS.md`](docs/CREDITS.md).
- **P2:** Native Windows Media Foundation + SDL3 opening video player (`runner/src/dos_intro_player.{h,cpp}`) playing `mods/intro/opening.mp4` (`640x480` 30fps H.264 + AAC, zero FFmpeg DLLs), skippable with any input, toggleable/replayable in `F1`, with safe fallback when missing.

### Done (Branch `feat/campaigns-randomizer-v1` — PR #16: Stages 16A–16D Campaigns, Character Packs & Randomizer v1)
- **16A (Foundation):** Declarative [`mods/registry.json`](mods/registry.json), 3-state `ConflictEngine` (`verified` / `unverified` / `incompatible`), XDELTA1 vs VCDIFF/IPS binary signature detection, hardened ZIP limits + path-traversal guards + atomic writes, `{install}` read-only vs `{data}` writable separation, isolated saves/savestates by `profile + version + modset_hash`, and 7th `F1` ImGui tab (`Mods & Campaigns`).
- **16B (Eternity of Sorrow 1.2):** Power-of-two cartridge padding in `runner/src/io.cpp` (`68.6 MB -> 128 MiB`), SHA-256 verified community fetcher (`tools/fetch_community_mods.py`), and live proof of *Eternity of Sorrow 1.2* (`59.98 FPS`, `emu_ms=2.37 ms`, `0` dispatch misses, isolated save, soft reset OK; kept `unverified` / `boot_and_perf_probe` pending full playthrough).
- **16C (Character Packs & Manual Slots):** Mutually exclusive Julius Mode packs (*Albus Mode*, *Model ZX*, *Model Omega*) with pinned SHA-256 verification and isolated saves, plus honest `Not Installed` manual slots (*Alucard's Requiem SOTN/CV3*, *Dracula's Curse*, *Definitive+*).
- **16D (Native C++ Seed Mutator & DSVania Randomizer Importer):** Zero-dependency C++17 `dos_seed_mutator.{h,cpp}` (`xoshiro256**/SplitMix64`, `--seed`, `--seed-preset casual|standard|hard`, verified FNV-1a Enemy DNA table gate, non-progression regular enemy stats/drops only, bosses `101..117` and soul IDs untouched, atomic spoiler log) plus `tools/import_dsvrandom.py` and automatic `{data}/mods/profiles/dsvrandom-*.dospatch` discovery.

### Planned (Optional / Future)
- Native compilation on a Linux/Steam Deck runner and Android NDK environment with prebuilt SDL3 libraries.
- Optional promotion of additional dynamic blocks if late-game castle areas record new coverage addresses via `play-profile.bat`.

[Back to top / Voltar ao topo](#roadmap--castlevania-dawn-of-sorrow-recompiled-acve)

---

<a id="português-br"></a>

## Português (BR)

### Feito (Fatia Vertical 1 — Bring-Up)
- Inspeção e validação da ROM USA original (`Castlevania - Dawn of Sorrow (USA).nds`, 64 MiB, CRC32 `135737f6`, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`).
- Projeto estruturado com `game.toml`, `tools/setup_toolchains.py`, `tools/prepare_rom.py`, `tools/build.py` e `play.bat`.
- `RetroPortingToolKit/ndsrecomp` + `recomp-ui` separados em `..\ndsrecomp` e `..\recomp-ui`.

### Feito (Fase 2 — Execução Nativa 49k+ Funções, DX12 & Controles Modernos)
- Promoção estática de `34` bancos (`49.059` funções) em `generated/banks-promoted/`.
- Mapeamento simultâneo `WASD + Setas + Espaço = Pulo (B)`, mouse na tela inferior para selos mágicos e controle Xbox/PlayStation.

### Feito (Fase 3 — 60 FPS em Janela Visível DX12 GPU + DXIL `ps_6_0`)
- Shaders GPU pré-compilados em `dos_postprocess.frag.hlsl` -> `dos_gpu_shader_dxil.h`, `SoftRenderer` automático fora de `gl_top` (`0,00 ms` readback) e prebuffer de áudio calibrado (`kAudioStartFrames = 3072`).

### Feito (Fase 4 — Menu Dear ImGui `F1`, Correção 3 Telas, PT-BR, RecompLauncher & Multiplataforma)
- **Menu gráfico Dear ImGui v1.92.9b (`F1`):** 6 abas (*Início*, *Tela & Layout*, *Gráficos HD*, *Áudio*, *Controles*, *Desempenho & Dev*), tradução completa EN / PT-BR (`dos_i18n.{h,cpp}`), fontes TrueType Latin Extended (`0x0020..0x024F`), calibração GPU ao vivo (*Brilho*, *Contraste*, *Saturação*, *Vinheta*), tamanho PiP (`20..50%`), `VSync`, zona morta do analógico, pausa/mudo em segundo plano, save states `1–5`, backup `.sav`, Sparkline FPS e screenshot `F12`.
- **Correção definitiva das 3 telas:** suspensão de `SDL_SetRenderLogicalPresentation` ao desenhar ImGui e desativação do caminho legado `g_runtime_menu_surface` / `menu_texture`, mantendo apenas as 2 telas reais atrás do overlay.
- **Tradução PT-BR em memória (`--ptbr-patch`):** patch delta `mods/ptbr/dos-ptbr.dospatch` (`469.280 B`, `4.806` blocos, *romsportugues.com* T1.0) aplicado em RAM com alternância ao vivo `EN <-> PT-BR`, aliado a bancos `dos_arm9`/`dos_arm7` gerados com `--validate-live-bytes` (`59,86 FPS` no benchmark DX12).
- **Multiplataforma & Shader Dual DXIL + SPIR-V:** `dos_gpu_shader_spirv.h` testado ao vivo em `vulkan-gpu` (`60,0 FPS`); `CMakePresets.json`, `tools/build_linux.sh` e `android/` (Gradle/NDK/SDL3) estruturados e documentados em [`docs/MULTIPLATFORM.md`](docs/MULTIPLATFORM.md).

### Feito (Fase 5 — Publicação GitHub, SDK 1.0 do RecompLauncher, Kit de Mídia & Docs Bilíngues)
- **Repositório Público GitHub (`Neguchads/cdos-nintendods-recomp`):** `.gitignore`/`.gitattributes` clean-room, **Dependabot** (`.github/dependabot.yml` para `github-actions` e `gradle` + alertas de segurança) e **GitHub Actions** (`.github/workflows/ci.yml` em Ubuntu + Windows + guarda clean-room e `shellcheck`).
- **SDK 1.0 do RecompLauncher & Kit de Mídia Oficial:** [`recomplauncher.json`](recomplauncher.json) atualizado para `inputs[game]` com dump USA verificado (`CRC32: 135737f6`, `67.108.864` bytes), `config[0].new` (31 chaves INI padrão), `looks`, `actions`, `system` e `exit_codes`; kit completo de artes gerado em [`assets/recomplauncher/`](assets/recomplauncher/) (`icon.png`/`icon.ico` `256x256`, `cover.png`/`cover.jpg` `600x900`, `hero.png`/`hero.jpg` `1920x620`, `logo.png` transparente `1000x500`, `wallpaper.png` `1920x1080`, `artwork.png` `1024x1024`, `catalog-entry.json`) e capturas reais em [`assets/screenshots/`](assets/screenshots/).
- **Documentação Bilíngue (`EN` -> `PT-BR`):** toda a documentação do projeto (`README.md`, `docs/RECOMPLAUNCHER.md`, `docs/MULTIPLATFORM.md`, `docs/DECISIONS.md`, `docs/rom-analysis.md`, `ROADMAP.md`, `HANDOFF.md`, `NOTAS.md`) organizada primeiro em Inglês e depois em Português (BR).
- **Correção de Inicialização no RecompLauncher com `cwd = runtime/` (`v1.0.1`):** `start.args` de `recomplauncher.json` atualizado para resolver `game.toml` e `mods/ptbr/dos-ptbr.dospatch` via `{install}` e `run/bios` via `{data}`, validação reforçada em `tools/package_recomplauncher.py` (bloqueio a caminhos relativos + exclusão de `*.ndshp`, `*.jsonl`, `*.bmp`, `*.png` no staging de `runtime/`) e novos testes unitários para ambas as regressões.
- **Executável Windows Standalone & Ícone Embutido (`CastlevaniaDawnOfSorrow.exe`):** launcher nativo Win32 GUI estático (`launcher/launcher_win32.cpp`) e recurso Windows (`launcher/app_icon.rc`) compilados automaticamente ao final de `python tools/build.py build`, embutindo `assets/recomplauncher/icon.ico` em `CastlevaniaDawnOfSorrow.exe` e `runtime/nds_runner.exe` e incluindo o executável no pacote Windows.
- **Cliques do Mouse em Combate, `Q`/`R` Nativos & Limpar por Tecla (`F1` Controles):** botões do mouse mapeáveis (`Mouse Left` = Ataque Padrão `Y`, `Mouse Right` = Ataque Especial `A`, `Mouse Mid` = Dash `L`, além de `Mouse X1/X2`) mantendo cliques na tela inferior (itens, menus, selos mágicos), `Q = L` e `R = R` nativos na Tecla 1, botão `X` para limpar por tecla, **Limpar Mapeamento** e **Restaurar Padrão** no menu `F1`.

### Feito (Branch `development` — PR #15: Fase 6 P0/P1/P2)
- **P0:** Decodificador VCDIFF (RFC 3284) e IPS em Python puro (`tools/vcdiff_ips.py`), importador/classificador de pacotes (`tools/import_mod_bundle.py`, `mods/catalog.json`) e diff semântico NitroFS/overlays (`tools/diff_dos_mods.py`, `mods/reports/definitive-vs-ptbr.json`).
- **P1:** Compositor semântico Definitive Edition + PT-BR (`tools/compose_dos_mods.py` -> `mods/definitive/dos-definitive-en.dospatch` `615 KB` + `dos-definitive-ptbr.dospatch` `752 KB`), builder C++ `dos_mod_profile.{h,cpp}` com isolamento de saves/savestates, UI de Conteúdo & Mods no `F1`, integração completa no RecompLauncher e launcher standalone, e créditos completos em [`docs/CREDITS.md`](docs/CREDITS.md).
- **P2:** Player nativo de abertura Windows Media Foundation + SDL3 (`runner/src/dos_intro_player.{h,cpp}`) reproduzindo `mods/intro/opening.mp4` (`640x480` 30fps H.264 + AAC, sem DLLs de FFmpeg), pulável por qualquer tecla/clique/botão, configurável/reproduzível no `F1` e com fallback seguro quando ausente.

### Feito (Branch `feat/campaigns-randomizer-v1` — PR #16: Etapas 16A–16D Campanhas, Packs de Personagens & Randomizer v1)
- **16A (Fundação):** [`mods/registry.json`](mods/registry.json) declarativo, `ConflictEngine` de 3 estados (`verified` / `unverified` / `incompatible`), detecção binária XDELTA1 vs VCDIFF/IPS, limites ZIP + proteção contra path traversal + escrita atômica, separação `{install}` somente leitura vs `{data}` gravável, isolamento de saves/savestates por `perfil + versão + modset_hash` e 7ª aba `Mods & Campanhas` no `F1`.
- **16B (Eternity of Sorrow 1.2):** Padding potência-de-2 em `runner/src/io.cpp` (`68,6 MB -> 128 MiB`), fetcher verificado por SHA-256 (`tools/fetch_community_mods.py`) e prova ao vivo de *Eternity of Sorrow 1.2* (`59,98 FPS`, `emu_ms=2,37 ms`, `0` dispatch misses, save isolado, soft reset OK; mantido `unverified` / `boot_and_perf_probe` aguardando validação completa).
- **16C (Packs de Personagens & Slots Manuais):** Packs mutuamente exclusivos de Julius Mode (*Albus Mode*, *Model ZX*, *Model Omega*) com SHA-256 travado e saves isolados, além de slots manuais honestos (`Não instalado`: *Alucard's Requiem SOTN/CV3*, *Dracula's Curse*, *Definitive+*).
- **16D (Seed Mutator C++ Nativo & Importador DSVania Randomizer):** `dos_seed_mutator.{h,cpp}` offline em C++17 (`xoshiro256**/SplitMix64`, `--seed`, `--seed-preset casual|standard|hard`, assinatura FNV-1a verificada na tabela Enemy DNA, apenas stats/drops não-progressão de inimigos regulares, chefes `101..117` e `soul_id`s intactos, spoiler log atômico) mais `tools/import_dsvrandom.py` e descoberta automática de `{data}/mods/profiles/dsvrandom-*.dospatch`.

### Planejado (Opcional / Futuro)
- Compilação nativa em runner Linux/Steam Deck e Android NDK em máquina ou workflow com bibliotecas SDL3 pré-compiladas.
- Promoção opcional de futuros blocos caso sessões em áreas muito avançadas do castelo registrem novos endereços nos manifestos de cobertura (`play-profile.bat`).

[Voltar ao topo / Back to top](#roadmap--castlevania-dawn-of-sorrow-recompiled-acve)
