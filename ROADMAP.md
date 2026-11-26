# Roadmap — Castlevania: Dawn of Sorrow: Recompiled (ACVE)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

[Live feature inventory and progress dashboard](docs/FEATURE_STATUS.md) · [Quality methodology](docs/FEATURE_ASSURANCE.md). The catalog does not replace the roadmap or close pending issues.

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

### Done (`v1.1.0` on `main` — PRs #15, #17, #21, #22)
- **PR #22 (RBS & Quality Gates):** Local incremental Windows build profiles (`Build.ps1`, `tools/rbs*.py`), ZIP allowlist + SHA-256 verification (`tools/rbs_artifact.py`), `CHANGELOG.md`, `docs/RBS.md`.
- **PR #15 (P0/P1/P2):** RFC 3284 VCDIFF & IPS decoder, Definitive Edition + PT-BR semantic composition (`dos-definitive-en.dospatch` / `dos-definitive-ptbr.dospatch`) as the verified default baseline, isolated saves, and opt-in native Windows Media Foundation intro player (`mods/intro/opening.mp4`, never bundled in public releases).
- **PR #17 (Stages 16A–16D — Experimental/Unverified Mods & Randomizer):** Declarative [`mods/registry.json`](mods/registry.json), 3-state `ConflictEngine` (`verified` / `unverified` / `incompatible`), power-of-two cartridge padding for expanded ROMs, *Eternity of Sorrow 1.2* (`unverified`, ~60 FPS boot/perf proven), *Albus Mode* (`unverified`, known inverted movement bug tracked in Issue #19), *Model ZX* / *Model Omega* (`unverified`), Native C++ Seed Mutator (`unverified`, non-progression regular enemy stats/drops), and `dsvrandom` importer (`tools/import_dsvrandom.py`).
- **PR #21 (Issues #16 Custom Music & #7 Widescreen 2D):**
  - **Custom Music (Verified):** Native `.wav` / `.mp3` / `.ogg` decoders (zero external DLLs), all 30 BGM tracks (`00..29`), selective Nitro SDK 2.x PXI `MUTE_TRACK` silencing (`DS BGM = 0`, `DS SFX = 100%`), in-game **`F1 -> Audio` Visual Track Mapper** (any filename -> any stage), **Global Jukebox / Playlist mode** (mute all 30 DS BGMs + Shuffle/Prev/Next), and double-clickable Windows Explorer wizard (`mods/music/Configurar_Musica.bat`).
  - **2D Widescreen (Verified Presentation):** `WidescreenTheatre` (`342×192` 16:9 canvas with 4:3 gameplay + docked 4:3 Map/Status sidebar), `SmartCrop16x9` (`OVERSCAN` 1:1 + `-24..+24 px` offset + exact touch mapping), and `Balanced16x10`.

### Done (`v1.2.0` — Multi-Pass Modern 2D Upscalers, HD-2D Bloom, Expanded Display Suite & Seamless True 2D Widescreen)
- **PR #29 (`v1.1.2` Security & Packaging Hardening):** Native MSVC 2022 `CastlevaniaDawnOfSorrow.exe` (`443 KB`, 5 OS DLLs only), explicit 4-file `runtime/` packaging allowlist, pinned `dsd.exe` SHA-256, portable `-march=x86-64 -mtune=generic` preset.
- **Sharp Bilinear + Bandlimited Pixel GPU Shaders (DXIL `ps_6_0` + SPIR-V Vulkan 1.1):** Automatic per-axis integer prescale + `fwidth` subpixel edge (`sharp-bilinear`) and C2 quintic Hermite anti-shimmer filter (`bandlimited-pixel`, `filter_mode = 5u`) for distortion-free crispness on any aspect ratio (`16:9`, `16:10`, `21:9`, non-integer windows).
- **Opt-in True 2D Widescreen `16:9` (`342×192`, Experimental):** Live-togglable in `F1 -> Screen & Layout` and `recomplauncher.json` (`dos_true_widescreen`, default `false`). Expands *Dawn of Sorrow (USA ACVE)*'s 3D-ortho BG0 + hardware 2D BG2 (`64×32` 512px tilemap) + camera centering/clamping to true `342×192` in multi-screen rooms (`g_state[0x08] == 0x02`, `width_screens >= 2`), with automatic `256×192` pillarbox on titles, prologues, pause/equip menus, and single-screen rooms, plus `wrap_x` sky-backdrop fix (`PR #32`).
- **Expanded Display & Graphics Suite (`ADR-016`):** Multi-monitor selector, `2x..6x` windowed scale presets, `21:9 Ultrawide Cinema`, `0..10%` Display Safe Zone / Overscan margin, Widescreen HUD alignment (`Edge-Anchored` vs `Centered 4:3`), 3-mode VSync (`Off`/`On`/`Adaptive`), live `120 Hz` Frame Interpolation toggle, `3D MSAA` (`Off/2x/4x/8x`), 4 one-click Visual Profiles, and 80-byte GPU post-process shader (DXIL `ps_6_0` + Vulkan 1.1 SPIR-V) adding Gamma, Color Temperature, Highlight Bloom, Display Mask Intensity, and CRT Curvature.
- **Seamless True 2D Widescreen & Curated Linear-Light Upscalers (`ADR-017`):** Fixed `1×N` HW 2D `BG2` parallax backdrop cutoff at `x = 256` (`gpu2d.cpp` modulo-256 wrap) and `x = 271` 3D atmospheric fog quad seam (`native_3d_raster.cpp` / `GPU3D.cpp`, verified `delta = (0,0,0)` on Lost Village Bridge & Plaza); replaced blurry `xBR 2x` + `Sharpen: Subtle` defaults with linear-sRGB `Pixellate` (default), `Pixel-AA`, and upgraded `Bandlimited Pixel`, moiré-free analytical `Scanlines`/`CRT`/`LCD`, center-aligned `Sharpen` (`Off` default), and a decluttered `F1 -> HD Graphics` menu.
- **Modern 2D Upscalers & Multi-Pass HD-2D Pipeline (`ADR-018`):** Multi-pass SDL3 GPU pipeline (`DosGpuShaderState::render_multipass`, DXIL `ps_6_0` + SPIR-V `-Os` compact ubershader) adding **MMPX 2×** (NVIDIA), **OmniScale**, **ScaleFX-Hybrid 3×**, **Selective Anti-Dither (GDAPT)**, **5-Pass Dual Kawase HD-2D Bloom** with CRT-aligned additive composite, and **HD-2D Remaster** / **Vector HD (ScaleFX)** one-click Visual Profiles (`<= 0.8 ms` GPU time).

### Done (Post-`v1.2.0` — Generic Local Mod Support & Creator-Respect Cleanup)
- **PR #35 (`@Xarishark`):** RecompLauncher save backup paths for `{data}/saves/definitive` & `{data}/saves/profiles`, Windows-only `system` manifest, and direct game-page badge link.
- **Generic Local Mod Support (Issues #43, #44, #30):** Removed all bundled/listed third-party mods and translations (`mods/ptbr/`, `mods/definitive/`, `mods/catalog.json`, `tools/fetch_community_mods.py`, third-party entries in `mods/registry.json`), added native C++ `.xdelta`/`.vcdiff`/`.ips` decoders in `dos_rom_patch.cpp` + auto-discovery in `{data}/mods/profiles/` with isolated saves, added offline `tools/import_local_mod.py`, switched default baseline to `Original USA`, and hardened release packaging against `.dospatch`/`.xdelta`/`.ips`/`.bps` leakage.
- **Exact `60.0 Hz` Vertical Sync (`sync60`, Issue #39):** Added `DosVsyncMode::Sync60Hz` with exact `60.000 Hz` frame pacing and pitch-preserving WSOLA Hann micro-splicing in `DosPitchPreservingAudioSync` (stutter-free on 60 Hz LCDs with zero crackle and zero pitch shift).
- **In-Game Patch Importer, Quick Per-Mod Patch Buttons, PT-BR v1.1 Slots & Minimap HUD (Samus Returns 16:9):** Added inline **`Patch...`** and **`Official Page`** buttons next to every non-builtin mod slot in `F1 -> Mods & Campaigns`, clean-room `manual_import` compatibility slots (zero files bundled) with full credits & outreach tracker (`docs/CREDITS.md`, `docs/CREATOR_OUTREACH.md`) for **Tradução PT-BR v1.1 (Vanilla & DE)** (`leomontenegro6/cdos-traducao-ptbr`, João13 Traduções), **Definitive Edition+**, **Eternity of Sorrow** (`@Wet-Band-Aid`, Issue #44), **Alucard's Requiem**, and **Dracula's Curse**, generic **`Import Patch...`** + **`Open Mods Folder`**, and `NdsScreenLayout::MinimapHud` (`minimap-hud`, compact `24%` top-right map overlay + **1-Click 16:9 Metroidvania HUD** preset).

### Done (Post-`v1.2.1` — Fatia 1: DJW/LZMA `xdelta3`, GBA Slot-2 Bonus & Mod Preview Panel)
- **Issue #50 (`runtime/xdelta3.exe`):** Packaged Xdelta 3.1.0 (Apache-2.0) alongside `nds_runner.exe` (`tools/build.py`, `tools/package_recomplauncher.py`, `tools/rbs_artifact.py`) so DJW/FGK/LZMA-compressed `.xdelta` patches (*Definitive Edition+ v2.3*, *Tradução PT-BR v1.1*) load natively out of the box.
- **Issue #51 (GBA Slot-2 *Aria of Sorrow* Bonus):** Clean-room 192-byte GBA header (`A2CE`) toggleable in `F1 -> Mods` & `recomplauncher.json` unlocking the **Rare Ring** and **Mina's Doll**.
- **Issue #44 (`@Wet-Band-Aid`) & `@leomontenegro6` Feedback:** Added **Mod Info & Preview Card** inside `F1 -> Mods` before installation, authorized PT-BR v1.1 status (`leomontenegro6/cdos-traducao-ptbr#1`), modular `manual_import` slots (**Dawn of Dignity** `#3356`, **No Magic Seals** `#3408`, **Fixed Luck** `#3407`, **Voice Restore Project** `#10040`), and Discord community link (`https://discord.gg/s7CWbpZJ`).

### Done (Post-`v1.2.2` — Fatia 2: Modular Stackable Patch Composition & Homepage Refresh)
- **Modular Stackable Add-Ons (inspired by `cdos-patcher-tool` & `@leomontenegro6`):** Separated `mods/registry.json` into stackable `"addons"` (**Tradução PT-BR v1.1**, **Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**) and exclusive `"campaigns"`. Added checkboxes in `F1 -> Mods & Campaigns`, 3-way byte-diff overlay merger against clean USA `base_rom` + NDS header CRC-16/MODBUS recomputation (`0x15E..0x15F`), persistent `dos_active_addons` INI key, isolated saves per stack (`modular-stack`), and full C++/Python parity.
- **Project Homepage (`README.md`) Refresh:** Reorganized EN and PT-BR sections with a scannable feature overview and up-to-date Feature Status tables.

### Exploratory community research (not committed)

- Seek collaborators and open-source tooling for independent ports of the DS trilogy (Dominus Collection context) and the GBA trilogy (Circle of the Moon, Harmony of Dissonance, Aria of Sorrow). Assess feasibility, legal provenance, shared infrastructure and existing work first. See the [community invitation](README.md#help-us-expand-the-castlevania-recompilation-ecosystem). These are not current release milestones or verified features.

### Planned (Future)
- Full start-to-credits playthrough validation for *True 2D Widescreen `342×192`* (promote from Beta to Verified).
- Community feature requests: HD Texture Dumping/Replacement ([Issue #36](https://github.com/Neguchads/cdos-nintendods-recomp/issues/36)), Cheat Manager ([Issue #37](https://github.com/Neguchads/cdos-nintendods-recomp/issues/37)), Advanced Custom Music Manager ([Issue #38](https://github.com/Neguchads/cdos-nintendods-recomp/issues/38)), and European multi-language support ([Issue #40](https://github.com/Neguchads/cdos-nintendods-recomp/issues/40)).
- Native compilation on a Linux/Steam Deck runner and Android NDK environment with prebuilt SDL3 libraries.

[Back to top / Voltar ao topo](#roadmap--castlevania-dawn-of-sorrow-recompiled-acve)

---

<a id="português-br"></a>

## Português (BR)

[Inventário de funcionalidades e painel de progresso](docs/FEATURE_STATUS.md) · [Metodologia](docs/FEATURE_ASSURANCE.md). O catálogo não substitui o roadmap.

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

### Feito (`v1.1.0` na `main` — PRs #15, #17, #21, #22)
- **PR #22 (RBS & Portões de Qualidade):** Perfis incrementais de build Windows (`Build.ps1`, `tools/rbs*.py`), allowlist de ZIP + verificação SHA-256 (`tools/rbs_artifact.py`), `CHANGELOG.md`, `docs/RBS.md`.
- **PR #15 (P0/P1/P2):** Decodificador VCDIFF/IPS, composição semântica Definitive Edition + PT-BR (`dos-definitive-en.dospatch` / `dos-definitive-ptbr.dospatch`) como base padrão verificada, saves isolados e player nativo opcional de abertura (`mods/intro/opening.mp4`, nunca incluído no ZIP público).
- **PR #17 (Etapas 16A–16D — Mods & Randomizer Experimentais):** [`mods/registry.json`](mods/registry.json) declarativo, `ConflictEngine` de 3 estados (`verified` / `unverified` / `incompatible`), padding potência-de-2 para ROMs expandidas, *Eternity of Sorrow 1.2* (`unverified`, boot e ~60 FPS validados), *Albus Mode* (`unverified`, bug conhecido de movimento invertido na Issue #19), *Model ZX* / *Model Omega* (`unverified`), Mutador Nativo por Seed C++ (`unverified`, apenas stats/drops fora da progressão) e importador `dsvrandom` (`tools/import_dsvrandom.py`).
- **PR #21 (Issues #16 Música Customizada & #7 Widescreen 2D):**
  - **Música Customizada (Verificado):** Decodificadores nativos `.wav` / `.mp3` / `.ogg` (zero DLLs externas), catálogo das 30 BGMs (`00..29`), mute seletivo Nitro SDK 2.x PXI `MUTE_TRACK` (`BGM DS = 0`, `SFX DS = 100%`), **Seletor Visual por Estágio** no `F1 -> Áudio` (qualquer nome de arquivo -> qualquer estágio), **Modo Jukebox / Playlist Global** (muta todas as 30 BGMs + Aleatório/Anterior/Próxima) e assistente duplo-clique com Windows Explorer (`mods/music/Configurar_Musica.bat`).
  - **Widescreen 2D (Apresentação Verificada):** `WidescreenTheatre` (canvas 16:9 `342×192` com gameplay 4:3 + lateral acoplada de Mapa/Status), `SmartCrop16x9` (`OVERSCAN` 1:1 + offset vertical `-24..+24 px` + toque preciso) e `Balanced16x10`.

### Feito (`v1.2.0` — Escaladores 2D Modernos Multi-Passe, Bloom HD-2D, Suíte Expandida de Display & Widescreen 2D Nativo)
- **PR #29 (`v1.1.2` Endurecimento de Segurança e Empacotamento):** `CastlevaniaDawnOfSorrow.exe` nativo MSVC 2022 (`443 KB`, 5 DLLs do Windows), allowlist explícita de 4 arquivos em `runtime/`, SHA-256 travado em `dsd.exe`, preset portável `-march=x86-64 -mtune=generic`.
- **PRs #31 e #32 (Sharp Scaling & Widescreen 2D Nativo `342×192`):** Shaders GPU `Sharp Bilinear` (auto-integer) + `Bandlimited Pixel` (quíntico C2) em DXIL `ps_6_0` e SPIR-V Vulkan 1.1; modo opt-in Experimental `dos_true_widescreen` (`342×192`, 14 ganchos ARM9 com preflight, BG2 `512px`, HUD HP/MP coeso e correção de paralaxe `wrap_x`).
- **Suíte Expandida de Gráficos e Display (`ADR-016`):** Seletor multi-monitor SDL3, escala em janela `2x..6x`, `21:9 Ultrawide Cinema`, margem segura / overscan (`0..10%`), alinhamento do HUD widescreen (`Bordas 16:9` vs `Zona Segura 4:3`), VSync 3 modos (`Desligado`/`Ligado`/`Adaptativo`), Interpolação `120 Hz` ao vivo, `3D MSAA` (`Off/2x/4x/8x`), 4 Perfis Visuais de 1 clique e shader GPU de 80 bytes (Gama, Temperatura de Cor, Bloom Suave, Intensidade da Máscara e Curvatura CRT).
- **Widescreen 2D Nativo Sem Cortes & Upscalers em Luz Linear Curados (`ADR-017`):** Corrigidos o corte preto de fundos `1×N` em `BG2` de hardware em `x = 256` (wrap módulo 256 em `gpu2d.cpp`) e a emenda de névoa em `x = 271` (expansão de quads atmosféricos 3D em `native_3d_raster.cpp` / `GPU3D.cpp`, validado `delta = (0,0,0)` na Ponte e Praça da Lost Village); padrão `xBR 2x` + `Sharpen: Subtle` substituído por `Pixellate` (padrão), `Pixel-AA` e `Bandlimited Pixel` em sRGB linear, máscaras `Scanlines`/`CRT`/`LCD` analíticas sem moiré, `Sharpen` corrigido (`Off` padrão) e menu `F1 -> Gráficos HD` enxuto.
- **Escaladores 2D Modernos & Pipeline Multi-Passe HD-2D (`ADR-018`):** Pipeline multi-passe SDL3 GPU (`DosGpuShaderState::render_multipass`, ubershader compacto DXIL `ps_6_0` + SPIR-V `-Os`) adicionando **MMPX 2×** (NVIDIA), **OmniScale**, **ScaleFX-Hybrid 3×**, **Anti-Dither Seletivo (GDAPT)**, **Bloom HD-2D Dual Kawase (5 passes)** com composição aditiva alinhada à curvatura CRT, e perfis **Remaster HD-2D** / **Vetor HD (ScaleFX)** (`<= 0,8 ms` na GPU).

### Feito (Pós-`v1.2.0` — Suporte Genérico a Mods Locais & Respeito aos Criadores)
- **PR #35 (`@Xarishark`):** Backup de saves em `{data}/saves/definitive` e `{data}/saves/profiles`, manifesto `system` somente Windows e badge do RecompLauncher apontando direto para a página do jogo.
- **Suporte Genérico a Mods Locais (Issues #43, #44, #30):** Removidos todos os mods/traduções de terceiros embutidos ou listados (`mods/ptbr/`, `mods/definitive/`, `mods/catalog.json`, `tools/fetch_community_mods.py`, entradas de terceiros em `mods/registry.json`), adicionados decodificadores nativos C++ `.xdelta`/`.vcdiff`/`.ips` em `dos_rom_patch.cpp` + auto-descoberta em `{data}/mods/profiles/` com saves isolados, adicionado importador offline `tools/import_local_mod.py`, alterado padrão para `Original USA` e travado empacotamento contra `.dospatch`/`.xdelta`/`.ips`/`.bps`.
- **VSync Exato `60,0 Hz` (`sync60`, Issue #39):** Adicionado `DosVsyncMode::Sync60Hz` com pacing exato `60,000 Hz` e micro-splicer WSOLA de janela Hann em `DosPitchPreservingAudioSync` (sem engasgos em monitores 60 Hz, zero crackle e zero alteração de tom).
- **Botões Rápidos de Patch no `F1 -> Mods`, Slots PT-BR v1.1 & Minimap HUD (Samus Returns 16:9):** Adicionados botões rápidos **`Aplicar Patch...`** e **`Site Oficial`** em cada slot de mod no `F1 -> Mods & Campanhas`, slots `manual_import` clean-room (zero arquivos embutidos) com créditos completos e controle de permissões (`docs/CREDITS.md`, `docs/CREATOR_OUTREACH.md`) para **Tradução PT-BR v1.1 (Vanilla & DE)** (`leomontenegro6/cdos-traducao-ptbr`, João13 Traduções), **Definitive Edition+**, **Eternity of Sorrow** (`@Wet-Band-Aid`, Issue #44), **Alucard's Requiem** e **Dracula's Curse**, além de **`Importar Patch...`** genérico + **`Abrir Pasta de Mods`** e o layout `NdsScreenLayout::MinimapHud` (`minimap-hud` + preset **1 Clique: HUD Metroidvania 16:9**).

### Feito (Pós-`v1.2.1` — Fatia 1: `xdelta3` DJW/LZMA, Bônus Slot-2 GBA & Painel de Prévia de Mods)
- **Issue #50 (`runtime/xdelta3.exe`):** Empacotamento do Xdelta 3.1.0 (Apache-2.0) junto ao `nds_runner.exe` (`tools/build.py`, `tools/package_recomplauncher.py`, `tools/rbs_artifact.py`) para decodificar `.xdelta` com compressor secundário DJW/FGK/LZMA (*Definitive Edition+ v2.3*, *Tradução PT-BR v1.1*) sem configuração manual.
- **Issue #51 (Bônus Slot-2 GBA *Aria of Sorrow*):** Cabeçalho GBA clean-room de 192 bytes (`A2CE`) alternável em `F1 -> Mods` e `recomplauncher.json`, liberando **Rare Ring** e **Mina's Doll**.
- **Issue #44 (`@Wet-Band-Aid`) & Sugestões `@leomontenegro6`:** Painel de **Detalhes e Prévia do Mod** dentro do `F1 -> Mods` antes da instalação, PT-BR v1.1 marcado como autorizado (`leomontenegro6/cdos-traducao-ptbr#1`), slots modulares `manual_import` (**Dawn of Dignity** `#3356`, **No Magic Seals** `#3408`, **Fixed Luck** `#3407`, **Voice Restore Project** `#10040`) e link do Discord (`https://discord.gg/s7CWbpZJ`).

### Feito (Pós-`v1.2.2` — Fatia 2: Composição Modular Empilhável de Patches & Refresh da Homepage)
- **Add-Ons Modulares Combináveis (inspirado no `cdos-patcher-tool` & `@leomontenegro6`):** `mods/registry.json` separado em `"addons"` empilháveis (**Tradução PT-BR v1.1**, **Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**) e `"campaigns"` exclusivas. Adicionados checkboxes em `F1 -> Mods & Campanhas`, merger 3-way byte-diff em memória sobre a `base_rom` USA limpa + recálculo do CRC-16/MODBUS do cabeçalho NDS (`0x15E..0x15F`), chave INI `dos_active_addons`, saves isolados por combinação (`modular-stack`) e paridade C++/Python.
- **Refresh da Homepage (`README.md`):** Seções EN e PT-BR reorganizadas com resumo visual de destaques e tabelas de status atualizadas.

### Pesquisa comunitária exploratória (sem compromisso de entrega)

- Buscar colaboradores e ferramentas open source para ports independentes da trilogia DS (contexto Dominus Collection) e da trilogia GBA (Circle of the Moon, Harmony of Dissonance, Aria of Sorrow). Avaliar viabilidade, procedência legal, infraestrutura compartilhada e trabalhos existentes. Consulte o [convite à comunidade](README.pt-BR.md#ajude-nos-a-expandir-o-ecossistema-de-recompilação-de-castlevania). Não são metas de release atuais nem funcionalidades verificadas.

### Planejado (Futuro)
- Validação completa de campanha (do início aos créditos) para promover *Widescreen 2D Nativo `342×192`* de Beta para Verificado.
- Pedidos da comunidade: Dump/Substituição de Texturas HD ([Issue #36](https://github.com/Neguchads/cdos-nintendods-recomp/issues/36)), Gerenciador de Cheats ([Issue #37](https://github.com/Neguchads/cdos-nintendods-recomp/issues/37)), Gerenciador Avançado de Música ([Issue #38](https://github.com/Neguchads/cdos-nintendods-recomp/issues/38)) e suporte multi-idioma Europeu ([Issue #40](https://github.com/Neguchads/cdos-nintendods-recomp/issues/40)).
- Compilação nativa em runner Linux/Steam Deck e Android NDK em máquina ou workflow com bibliotecas SDL3 pré-compiladas.

[Voltar ao topo / Back to top](#roadmap--castlevania-dawn-of-sorrow-recompiled-acve)
