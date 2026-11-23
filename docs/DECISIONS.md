# Technical Decisions / Decisões Técnicas — Castlevania: Dawn of Sorrow: Recompiled

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### ADR-001: Use `RetroPortingToolKit/ndsrecomp` with FreeBIOS-only
- **Context:** We need to statically recompile `Castlevania - Dawn of Sorrow (USA)` (`ACVE`) for Windows with native execution of the ARM9 and ARM7 CPUs, without depending on extracting commercial `biosnds9.rom`, `biosnds7.rom`, or `firmware.bin` files.
- **Decision:** Adopt `RetroPortingToolKit/ndsrecomp` (commit `e4a7f419eef6610e7e29df5aed96aa7a700cd493`, with submodules `external/arm-recomp-core` `90b6c510a7471c9c7146c0e8c8f5d9e6d7b13e57` and `third_party/freebios` `6d6cfb4953924e4abdaa130aedf71826a055508e`) and `RetroPortingToolKit/recomp-ui` (commit `f3f99a9636bab1b15582c85a915c4127748611e6`) in shared sibling directories (`..\ndsrecomp` and `..\recomp-ui`, outside this repository, with automatic fallback to `framework/`) plus a minimal patch ([`patches/ndsrecomp-local.patch`](../patches/ndsrecomp-local.patch)) making retail BIOS banks optional in CMake, linking `launcher_theme_overrides.c` from `recomp-ui`, and running FreeBIOS + synthesized firmware via `--freebios --generated-firmware --boot direct`.
- **Why:** `ndsrecomp` already provides an ARMv5TE/ARMv4T static recompiler, synchronized dual-CPU runtime, 2D/3D renderer (melonDS), and safe Tier-3 interpreter fallback for dynamic code or overlays not yet promoted.
- **Reversal:** If `ndsrecomp` v0.6.12 exhibits blocking incompatibilities on Windows even after configuration tuning, migrate the frontend/runtime to the `ntr-recomp` (`phantom-hourglass-recomp`) engine or evaluate `Myth7x/ndsrecomp` for prototyping only.

### ADR-002: Portable LLVM-MinGW + SDL3 MinGW toolchain (zero system modification)
- **Context:** The host machine has VS2022 MSVC installed, but `ndsrecomp` uses GCC/Clang extensions (`__builtin_*`, POSIX headers in several modules) and compiler flags tuned for MinGW/Clang (`-O2`, `-Wno-unused-*`, `libslirp`).
- **Decision:** Install `llvm-mingw 20261020 UCRT x86_64` and `SDL3-devel 3.4.18 mingw` locally inside `toolchains/` (gitignored), reusing portable CMake 4.4.4 and Ninja.
- **Why:** Keeps the build reproducible, isolated inside the project directory, and aligned with Windows builds validated across the `ndsrecomp` community.
- **Reversal:** If official MSVC support in `ndsrecomp` eventually covers 100% of `runner` and `recompiler` without GNU/POSIX flags, switch compilers in `tools/build.py`.

### ADR-003: Pure Python stdlib `prepare_rom.py` extractor
- **Context:** Inspection of the `ACVE` ROM confirmed that the main ARM9 binary (`compressed_static_end = 0`) and all 41 ARM9 overlays (`comp = 0`) are stored uncompressed in the ROM. Neither system Python nor the local environment had `ndspy` installed.
- **Decision:** Implement [`tools/prepare_rom.py`](../tools/prepare_rom.py) using pure Python standard library (`struct`, `hashlib`, `json`, `pathlib`), validating SHA-1/SHA-256 and extracting ARM9, ARM7, and all 41 overlays (plus `overlays.json` for recompiler aliases).
- **Why:** Avoids unnecessary external dependencies (radical MVP) while keeping extraction deterministic and offline-testable.
- **Reversal:** If we later support ROMs with compressed ARM9 or overlays (e.g., *Portrait of Ruin* / *Order of Ecclesia* or recompressing ROM hacks), add BLZ (Nintendo reverse LZ77) decompression or `ndspy`.

### ADR-004: Batch promotion of 49,059 functions to eliminate the Tier-3 bottleneck
- **Context:** In the Phase 1 baseline session (`performance-20261122-073226.jsonl`), median frame rate sat at `30.5 FPS` (`emu_ms = 31.7 ms`). `hostprof` revealed `tier3_selected` consuming `66.02%` of emulation thread CPU time because resident overlays (`ov000`, `ov001`, `ov023`..`ov040`), ARM7 WRAM blocks (`0x037F8000`), and undiscovered ARM9/ITCM blocks fell back to the interpreter.
- **Decision:** Create [`tools/promote_banks.py`](../tools/promote_banks.py) combining `dsd` symbol seeds with runtime addresses captured in `saves/*-coverage-*.json` via `ingest_coverage_manifests.py`, emitting 34 content-validated banks (`--validate-live-bytes`) into `generated/banks-promoted/` and linking them into `nds_runner` via `NDS_TITLE_BANK_DIRS`. Disable `NDS_HOSTPROF=off` and `--diagnostics off` in production ([`play.bat`](../play.bat)), keeping profiling separate in [`play-profile.bat`](../play-profile.bat).
- **Why:** Native ARM9/ARM7 execution dropped `emu_ms` from `31.7 ms` to `~3.7–5.7 ms` (`59.7–60.0 FPS`) with zero behavioral changes.
- **Reversal:** If promoted banks ever cause excessive link times, binary size bloat, or symbol collisions after an upstream `ndsrecomp` update, regenerate only ARM9 + `ov000` + `ov001` + top hotspots filtered by minimum hit count in `promote_banks.py`.

### ADR-005: DirectX 12 presentation with offscreen OpenGL 4.3 Compute and 2D HD CPU fallback (`xBR2x`)
- **Context:** The `presentation.gl_top = true` path in `ndsrecomp` hands the window directly to OpenGL, preventing use of SDL3's **Direct3D 12** renderer, `SDL_LOGICAL_PRESENTATION_STRETCH` full-screen scaling, and post-composition 2D sprite filters (*Castlevania: Dawn of Sorrow* is predominantly 2D pixel art with no public HD texture pack).
- **Decision:** When DX12, `Stretch`, 2D HD filters, or extended dual-screen layouts are active, keep `presentation.gl_top = false`, retaining **offscreen OpenGL 4.3 Compute** when explicitly requested and feeding the SDL3 **`direct3d12`** renderer. Implement a 256-entry color LUT (`Vivid HD` / `DS Authentic`), optimized `xBR-HD 2x` with uniform-region skipping, unsharp masking, and Post-FX in `runner/src/dos_enhancements.{h,cpp}`, plus stereo/reverb audio DSP.
- **Why:** Delivers Direct3D 12, stretched fullscreen, and 2D/3D/audio enhancements working together on Windows 11.
- **Reversal:** Once 2D xBR + Scanlines/CRT are offloaded to GPU shaders (SDL3 GPU DXIL / SPIR-V), bypass CPU pixel processing in `DosFrameProcessor` and run the GPU fragment shader directly (implemented in ADR-007 and ADR-009).

### ADR-006: Runtime menu with 7 dual-screen layouts and live input remapping
- **Context:** The upstream runtime menu only exposed mouse sensitivity and exited on `Esc`.
- **Decision:** Expand `screen_layout.h`, `frontend_config.cpp`, and `frontend.cpp` to support 7 dual-screen layouts (`pip`, `bottom-only`, `top-only`, `stacked`, `side-by-side`, `side-by-side-big`, `separate`), live key/button capture, modern **WASD + Arrows + Space = Jump (`B`)** defaults, and persistent settings in `saves/dos-settings.ini`.
- **Why:** Preserves 100% of existing framework unit tests while giving players full layout and control customization.
- **Reversal:** If a richer mouse-first multi-tab overlay UI is needed, replace only the rendering layer while keeping `DosEnhancementSettings` and `dos_{load,save}_settings_ini` (implemented in ADR-008).

### ADR-007: 2D HD pipeline in DXIL `ps_6_0` shader (`dx12-gpu`), zero-readback SoftRenderer Auto, and calibrated audio prebuffer
- **Context:** Benchmarks in a visible window with `direct3d12`, `xbr2x`, `vivid`, `subtle`, and `internal_resolution=4` exposed three combined bottlenecks: (1) startup stuck at `38.4–39.3 FPS` across frames `131..293` due to `kAudioStartFrames=57344` + `kGlideStepFrames=300` draining up to `21.2 ms/frame`; (2) `cpu_fx` taking `3.7–4.2 ms/frame` running `xBR2x`+LUT+unsharp on the CPU; and (3) `rb=2.31–6.00 ms/frame` wasted reading back offscreen OpenGL 4.3 Compute to CPU memory in non-`gl_top` mode. Furthermore, `SDL_render_gpu` in SDL 3.4.18 uses **DXIL SM 6.0** (`TEXCOORD0 = v_color`, `TEXCOORD1 = v_uv`).
- **Decision:**
  1. Offload 2D post-processing (`xBR-lv2`, `Scale2x`, `Sharp Bilinear`, `Bilinear`, `Nearest`, `Unsharp`, `Vivid HD`/`DS Authentic`, `Scanlines`/`CRT`/`LCD Grid`, and PiP opacity) to `runner/src/dos_postprocess.frag.hlsl` pre-compiled with `dxc -T ps_6_0 -E main -O3` into signed DXIL bytecode embedded in `runner/src/dos_gpu_shader_dxil.h` (`runner/src/dos_gpu_shader.{h,cpp}`), running on SDL3 `gpu` over `direct3d12` (`dx12-gpu`), uploading textures only when the raw frame changes (`dos_frame_identical`) and drawing the HUD in a separate transparent texture (`960x24`, updated only on revision changes).
  2. When `!gl_top` and `NDS_3D_RENDERER=auto`, enable `nds_gpu3d_use_soft_renderer(true)` without starting `nds_compute_host_start(nullptr)` (keeping `internal_resolution = 1` and `texture_upscale = 1` in `game.toml`) to eliminate `rb=2.3–6.0 ms/frame`.
  3. Lower `kAudioStartFrames` to `3072` (overridable via `NDS_AUDIO_START_FRAMES`) and `kGlideStepFrames` to `32`.
  4. Compile `nds_runner` with `-DNDS_LEAN_DIAGNOSTICS=ON`, `-DNDS_GX_COMMAND_CACHE=ON`, `-DNDS_CAPTURE_VIEW_REUSE=ON`, `-DNDS_3D_GEOMETRY=NATIVE`, and `-O2/-O3 -march=native` in Clang.
- **Why:** Embedded DXIL SM 6.0 bytecode pairs directly with `SDL_GPU` D3D12 pipelines without requiring `dxcompiler.dll` at runtime, cuts `pres` from `~5.0 ms` to `0.78–1.16 ms/frame`, zeroes `readback_ns` (`0.00 ms`), eliminates the initial `38.5 FPS` dip, and sustains **59.7–59.9 FPS** with `0` underruns.
- **Reversal:** To distribute a binary across older x86-64 CPUs without AVX2 or tweak 2D filters without running `dxc`, drop `-march=native` or fall back to the cached CPU path (`gpu_shader_active=false`).

### ADR-008: Dear ImGui v1.92.9b overlay menu (`F1`), 3-screens bug fix, and RecompLauncher integration
- **Context:** The legacy `recomp_runtime_ui` menu rendered a `512x384` bitmap via `menu_texture` centered over the window; in dual-screen layouts (`side-by-side`, `side-by-side-big`, `stacked`), its opaque background copy of `raw_sources[hud_screen]` created a visible 3rd duplicate screen behind the menu and limited live calibration, PT-BR accented glyphs, and modern launcher ergonomics.
- **Decision:** Integrate **Dear ImGui v1.92.9b** (`imgui_impl_sdl3` + `imgui_impl_sdlrenderer3`) in `dos_imgui_menu.{h,cpp}` with full **EN / PT-BR** localization (`dos_i18n.{h,cpp}`) and Latin Extended TrueType fonts (`0x0020..0x024F`). While rendering the overlay, temporarily suspend `SDL_SetRenderLogicalPresentation` to draw at native monitor resolution (1080p+) and bypass the legacy `g_runtime_menu_surface` / `menu_texture` path completely. Boot directly into the game by default (`dos_skip_launcher=true`) with **`F1`** / `Esc` / `Guide` opening the 6-tab overlay menu (adding live GPU Brightness/Contrast/Saturation/Vignette calibration, PiP size `20..50%`, `VSync`, analog deadzone, pause/mute when unfocused, save state slots `1–5`, `.sav` backup, FPS Sparkline, and `F12` screenshots).
- **Why:** Permanently fixes the 3-screens bug, delivers a crisp 1080p+ mouse/keyboard/gamepad UI, and matches modern recomp ports.
- **Reversal:** If a future backend lacks `SDL_Renderer` support for `ImGui_ImplSDLRenderer3`, the legacy `recomp_runtime_ui` fallback remains compiled behind `!presentation.imgui_ready`.

### ADR-009: In-memory PT-BR `DOSPATCH` delta translation + `--validate-live-bytes` + dual DXIL/SPIR-V GPU shader
- **Context:** The Brazilian Portuguese fan translation modified `3` overlays (`ov000`, `ov004`, `ov005`), `88` NitroFS font/text files, and `120` bytes in `ARM9` (accent/glyph hooks). Because `dos_arm9` and `dos_arm7` previously lacked live-byte validation on dispatch, static banks compiled from USA ROM bytes could override translated ARM9 hooks; additionally, Linux/Steam Deck and Android require Vulkan SPIR-V shaders alongside Windows DXIL.
- **Decision:**
  1. Keep the original USA ROM unmodified (`SHA-1: 47530ff87e608f88105a314fdf36dc385f8dec94`) for cartridge verification and static bank registration, generating a compact binary delta patch [`mods/ptbr/dos-ptbr.dospatch`](../mods/ptbr/dos-ptbr.dospatch) (`DOSPATCH`, source/target SHA-1 + CRC32) applied strictly in RAM by `dos_rom_patch.{h,cpp}` via `--ptbr-patch` with live EN <-> PT-BR switching (`reset_machine`).
  2. Emit `dos_arm9` and `dos_arm7` with `--validate-live-bytes` in `tools/build.py` so any function modified by the translation automatically falls back while the rest of the ROM runs natively at ~60 FPS.
  3. Compile `dos_postprocess.frag.hlsl` to **SPIR-V Vulkan 1.1** (`dos_gpu_shader_spirv.h`) with automatic DXIL (`direct3d12`) or SPIR-V (`vulkan-gpu`) selection, enabling `CMakePresets.json`, `tools/build_linux.sh`, and the `android/` ARM64 skeleton.
- **Why:** Zero redistribution of copyrighted ROMs, instant in-game language switching, and portable DX12 + Vulkan GPU shaders without a runtime shader compiler.
- **Reversal:** If a future translation rewrites a large portion of `ARM9` code and reduces live-byte validation hit rates, emit a secondary static bank set indexed by the translated ROM's SHA-1 in `NDS_TITLE_BANK_DIRS`.

### ADR-010: RecompLauncher SDK v1 `inputs` manifest, procedural media kit, and bilingual EN/PT-BR documentation
- **Context:** RecompLauncher 1.0 deprecates the legacy top-level `game` object in favor of named `inputs` (`{input:game}`), requires `prepare` steps to run windowless (whereas our runner applies `dos-ptbr.dospatch` in memory at startup and needs no separate preparation step), checks `config[0].new` for first-start INI defaults, and uses 4 standard artwork slots (`icon` `256x256`, `cover` `600x900`, `hero` `1920x620`, transparent `logo` `1000x500`) plus `media_design` (`kind: "ds"`) and showcase wallpapers/artwork.
- **Decision:**
  1. Declare the cartridge in `inputs[game]` (`.nds` format, `check.ids = ["ACVE"]`, `dumps` with verified USA size `67108864` and CRC32 `135737f6`), pass `--rom {input:game}` in `start.args`, omit `prepare`, populate `config[0].new` with all 30 INI defaults, and declare `looks`, `actions`, `system`, and `exit_codes` in [`recomplauncher.json`](../recomplauncher.json).
  2. Generate an original, copyright-clean gothic media kit (`icon.png`, `icon.ico`, `cover.png`, `cover.jpg`, `hero.png`, `hero.jpg`, transparent `logo.png`, `wallpaper.png`, `artwork.png` with DS cartridge render, and `catalog-entry.json`) via [`tools/prepare_media_assets.py`](../tools/prepare_media_assets.py), paired with 3 real in-engine `1920x1080` captures in [`assets/screenshots/`](../assets/screenshots/) and stdlib-only header dimension tests in [`tests/test_recomplauncher.py`](../tests/test_recomplauncher.py).
  3. Structure all repository documentation bilingually with **English (`EN`) first** and **Português (BR) (`PT-BR`) second**.
- **Why:** Achieves zero warnings in RecompLauncher's `devtools.rs` validator, displays the verified USA dump badge (`CRC32: 135737f6`), avoids third-party artwork copyright issues, and makes the repository accessible to both international and Brazilian players.
- **Reversal:** If a windowless pre-caching step (e.g., offline shader cache warmup) is added later, re-introduce `prepare` with a dedicated `--prepare` CLI flag and `prepare.done`. If commissioned artwork replaces the procedural kit, keep the exact slot filenames/resolutions and validate with `python tools/prepare_media_assets.py --check-only`.

### ADR-011: RecompLauncher `cwd = runtime/` path anchoring, standalone Win32 launcher `.exe`, EN-first defaults & mappable mouse combat buttons
- **Context:** On `v1.0.0`, RecompLauncher spawned `runtime/nds_runner.exe` with `cwd = {install}/runtime`, causing bare relative paths (`game.toml`, `mods/ptbr/dos-ptbr.dospatch`, `run/bios`) to fail at startup. Standalone Windows users also needed a double-click `.exe` with an embedded game icon (matching other PC recomps), English as primary default with PT-BR secondary, and native mouse combat bindings (`Left` = Attack, `Right` = Special, `Middle` = Dash) with per-key clearing while keeping DS bottom-screen touch intact.
- **Decision:**
  1. Anchor every `start.args` path in [`recomplauncher.json`](../recomplauncher.json) to `{install}` or `{data}` and enforce this in `tools/package_recomplauncher.py` (`validate_manifest`).
  2. Build a zero-DLL static Win32 GUI launcher (`launcher/launcher_win32.cpp` -> `CastlevaniaDawnOfSorrow.exe`) at the end of `tools/build.py build`, embedding `assets/recomplauncher/icon.ico` (`launcher/app_icon.rc`) into both `CastlevaniaDawnOfSorrow.exe` and `runtime/nds_runner.exe`. On first standalone launch, it verifies the user's USA `.nds` (`67,108,864` B, `ACVE`, CRC32 `135737f6`), installs it locally into `game/`, and offers to create a Desktop `.lnk` shortcut via COM `IShellLinkW`.
  3. Set `en` as the default `ui_language` and `game_language` in `game.toml` and `recomplauncher.json`, keeping `dos-ptbr.dospatch` loaded in RAM as the secondary option in `F1`.
  4. Encode mappable mouse buttons as virtual codes `501..505` (`< 512`, accepted natively by `nds_valid_binding` / TOML / INI), track `mouse_buttons_held` alongside bottom-screen touch in `frontend.cpp`, default Key 1/2 to `Mouse Left = Y`, `Mouse Right = A`, `Q = L`, `R = R`, `Mouse Mid = L`, and add per-cell `X` clear buttons, **Clear All Mappings**, and **Restore Default Controls** in `dos_imgui_menu.cpp`.
- **Why:** Fixes RecompLauncher startup across all Windows machines, provides 1-click PC recomp UX without violating clean-room rules, aligns international defaults, and makes mouse+keyboard combat effortless without losing touchscreen support.
- **Reversal:** If a future `ndsrecomp` update reserves scancode values above `500`, move mouse binding codes into a dedicated `dos_mouse_bindings` INI/TOML key. If RecompLauncher ever changes its `cwd` policy, explicit `{install}`/`{data}` paths remain valid regardless of `cwd`.

### Third-Party Licenses (Informational Only)
- `RetroPortingToolKit/ndsrecomp`:
  - Recompiler, finder, and tools (`LICENSE`): PolyForm Noncommercial License 1.0.0 + additional permissions in `PERMISSIONS.md` (donations/sponsorship/ads permitted provided access to software/updates remains free).
  - Runner and oracle (`LICENSE-MIT` + `LICENSE-GPL`): original code under MIT, linked against melonDS-derived components under GPL-3.0-or-later (compiled `nds_runner.exe` is a combined work under GPL-3.0-or-later).
  - `third_party/freebios`: BSD-2-Clause.
- `RetroPortingToolKit/recomp-ui`: MIT License (`../recomp-ui/LICENSE`).
- `libsdl-org/SDL` (SDL3 3.4.18): zlib License.
- `mstorsjo/llvm-mingw` (20261020): ISC / Apache-2.0 with LLVM Exception.
- `AetiasHax/ds-decomp` (`dsd` v0.12.1): MIT License.
- `ocornut/imgui` (`Dear ImGui` v1.92.9b, SDL3 + SDLRenderer3 backends): MIT License.
- Reference Brazilian Portuguese translation (*romsportugues.com* T1.0): credited to the original fan-translation team and applied strictly as an in-memory delta patch over the user-supplied USA ROM.
- Media kit in `assets/recomplauncher/`: original procedural artwork generated by `tools/prepare_media_assets.py`; screenshots in `assets/screenshots/` are direct captures from this project's runtime.

[Back to top / Voltar ao topo](#technical-decisions--decisões-técnicas--castlevania-dawn-of-sorrow-recompiled)

---

<a id="português-br"></a>

## Português (BR)

### ADR-001: Uso do `RetroPortingToolKit/ndsrecomp` com FreeBIOS-only
- **Contexto:** Precisamos recompilar `Castlevania - Dawn of Sorrow (USA)` (`ACVE`) para Windows com execução nativa das CPUs ARM9 e ARM7, sem depender da extração prévia de `biosnds9.rom`, `biosnds7.rom` ou `firmware.bin` comerciais.
- **Decisão:** Adotar `RetroPortingToolKit/ndsrecomp` (commit `e4a7f419eef6610e7e29df5aed96aa7a700cd493`, com submódulos `external/arm-recomp-core` `90b6c510a7471c9c7146c0e8c8f5d9e6d7b13e57` e `third_party/freebios` `6d6cfb4953924e4abdaa130aedf71826a055508e`) e `RetroPortingToolKit/recomp-ui` (commit `f3f99a9636bab1b15582c85a915c4127748611e6`) em pastas compartilhadas na raiz (`..\ndsrecomp` e `..\recomp-ui`, fora deste repositório, com fallback automático para `framework/`) com um patch mínimo ([`patches/ndsrecomp-local.patch`](../patches/ndsrecomp-local.patch)) para tornar opcionais os bancos de BIOS retail no CMake, linkar `launcher_theme_overrides.c` do `recomp-ui` e usar FreeBIOS + firmware sintetizado via `--freebios --generated-firmware --boot direct`.
- **Por quê:** `ndsrecomp` já possui recompiler ARMv5TE/ARMv4T, runtime dual-CPU sincronizado, renderer 2D/3D (melonDS) e fallback seguro via interpretador Tier-3 para código dinâmico ou overlays ainda não promovidos.
- **Reversal:** Se `ndsrecomp` v0.6.12 apresentar incompatibilidades bloqueantes no bring-up ou na compilação no Windows mesmo após ajustes de configuração, migrar o frontend/runtime para o motor de `ntr-recomp` (`phantom-hourglass-recomp`) ou avaliar `Myth7x/ndsrecomp` apenas para prototipagem.

### ADR-002: Toolchain portável LLVM-MinGW + SDL3 MinGW (sem alterar o sistema)
- **Contexto:** A máquina tem VS2022 MSVC instalado, mas `ndsrecomp` utiliza extensões GCC/Clang (`__builtin_*`, headers POSIX em alguns módulos) e configurações otimizadas para MinGW/Clang (`-O2`, `-Wno-unused-*`, `libslirp`).
- **Decisão:** Instalar `llvm-mingw 20261020 UCRT x86_64` e `SDL3-devel 3.4.18 mingw` localmente na pasta `toolchains/` (ignorada no git), reaproveitando CMake 4.4.4 e Ninja portáteis.
- **Por quê:** Mantém o build reproduzível, isolado na pasta do projeto e alinhado aos builds Windows já validados em projetos da comunidade `ndsrecomp`.
- **Reversal:** Se o suporte oficial MSVC do `ndsrecomp` passar a cobrir 100% do `runner` e `recompiler` sem flags GNU/POSIX, pode-se alternar os compiladores em `tools/build.py`.

### ADR-003: Extrator `prepare_rom.py` em Python stdlib pura
- **Contexto:** A inspeção da ROM `ACVE` confirmou que a imagem ARM9 (`compressed_static_end = 0`) e todos os 41 overlays ARM9 (`comp = 0`) estão descomprimidos na ROM. O Python do sistema não tinha `ndspy` instalado.
- **Decisão:** Implementar [`tools/prepare_rom.py`](../tools/prepare_rom.py) com Python stdlib pura (`struct`, `hashlib`, `json`, `pathlib`) validando SHA-1/SHA-256 e extraindo ARM9, ARM7 e os 41 overlays (além de `overlays.json` para aliases do recompilador).
- **Por quê:** Evita dependência externa desnecessária (MVP radical) enquanto mantém extração determinística e testável offline.
- **Reversal:** Se formos suportar ROMs com ARM9 ou overlays comprimidos (ex.: *Portrait of Ruin* / *Order of Ecclesia* ou patches que recomprimam), adicionar suporte a descompressão BLZ (LZ77 reverso Nintendo) ou `ndspy`.

### ADR-004: Promoção em lote de 49.059 funções para eliminar o gargalo Tier-3
- **Contexto:** Na sessão real da Fase 1 (`performance-20261122-073226.jsonl`), a mediana ficou em `30.5 FPS` (`emu_ms = 31.7 ms`). O `hostprof` mostrou `tier3_selected` consumindo `66,02%` do tempo de CPU da thread de emulação, pois overlays residentes (`ov000`, `ov001`, `ov023`..`ov040`), blocos de WRAM do ARM7 (`0x037F8000`) e trechos não descobertos do ARM9/ITCM caíam no interpretador.
- **Decisão:** Criar [`tools/promote_banks.py`](../tools/promote_banks.py) combinando seeds do `dsd` com endereços gravados em `saves/*-coverage-*.json` via `ingest_coverage_manifests.py`, emitindo 34 bancos validados por conteúdo (`--validate-live-bytes`) em `generated/banks-promoted/` e ligando-os ao `nds_runner` via `NDS_TITLE_BANK_DIRS`. Em produção ([`play.bat`](../play.bat)), desabilitar `NDS_HOSTPROF=off` e `--diagnostics off`, deixando o profiling separado em [`play-profile.bat`](../play-profile.bat).
- **Por quê:** Execução ARM9/ARM7 nativa derrubou `emu_ms` de `31.7 ms` para `~3.7–5.7 ms` (`59.7–60.0 FPS`) com zero alterações de comportamento no jogo.
- **Reversal:** Se bancos promovidos causarem aumento excessivo de tempo de link/tamanho ou colisões após atualização grande do `ndsrecomp`, regenerar apenas ARM9 + `ov000` + `ov001` + top hotspots filtrando por contagem mínima de hits no `promote_banks.py`.

### ADR-005: DirectX 12 com OpenGL 4.3 Compute offscreen e pipeline 2D HD em CPU (`xBR2x`)
- **Contexto:** O caminho `presentation.gl_top = true` do `ndsrecomp` entrega a janela diretamente ao contexto OpenGL, impedindo uso do backend **Direct3D 12** do SDL3, apresentação `SDL_LOGICAL_PRESENTATION_STRETCH` (imagem esticada preenchendo toda a tela) e filtros 2D pós-composição em sprites (*Castlevania: Dawn of Sorrow* é majoritariamente pixel art 2D sem pack público de texturas HD).
- **Decisão:** Quando opções DX12, `Stretch`, filtros 2D HD ou layouts estendidos estiverem ativos, manter `presentation.gl_top = false`, alimentando o renderer SDL3 **`direct3d12`**. Aplicar LUT de cores 256 entradas (`Vivid HD`/`DS Authentic`), `xBR-HD 2x` otimizado com skip de regiões uniformes, nitidez unsharp e Post-FX na superfície 2D em `runner/src/dos_enhancements.{h,cpp}`, além de DSP estéreo/reverb no áudio.
- **Por quê:** Entrega DX12 + fullscreen esticado + upscaling 2D/3D/Áudio funcionando juntos no Windows 11.
- **Reversal:** Portar os shaders de 2D xBR + Scanlines/CRT diretamente para GPU (SDL3 GPU DXIL / SPIR-V) e manter o caminho CPU apenas como fallback (implementado nos ADR-007 e ADR-009).

### ADR-006: Menu de runtime com 7 layouts e remapeamento ao vivo
- **Contexto:** O menu nativo anterior tinha apenas sensibilidade de mouse e encerrava no `Esc`.
- **Decisão:** Expandir `screen_layout.h`, `frontend_config.cpp` e `frontend.cpp` para suportar 7 layouts (`pip`, `bottom-only`, `top-only`, `stacked`, `side-by-side`, `side-by-side-big`, `separate`), capturar novas teclas/botões ao vivo, manter layout moderno **WASD + Setas + Espaço = Pulo (`B`)**, e persistir preferências em `saves/dos-settings.ini`.
- **Por quê:** Preserva 100% dos testes unitários existentes do framework e entrega customização completa de telas e controles.
- **Reversal:** Se precisarmos de UI mouse-first multi-abas mais rica, substituir apenas a camada de desenho mantendo `DosEnhancementSettings` e `dos_{load,save}_settings_ini` (implementado no ADR-008).

### ADR-007: Pipeline 2D HD em Shader DXIL `ps_6_0` (`dx12-gpu`), SoftRenderer Auto sem readback e arranque de áudio calibrado
- **Contexto:** Benchmarks na janela visível com `direct3d12`, `xbr2x`, `vivid`, `subtle` e `internal_resolution=4` revelaram três gargalos combinados: (1) arranque preso em `38,4–39,3 FPS` nos quadros `131..293` devido a `kAudioStartFrames=57344` + `kGlideStepFrames=300` drenando até `21,2 ms/f`; (2) `cpu_fx` de `3,7–4,2 ms/f` aplicando `xBR2x`+LUT+unsharp na CPU a cada frame; e (3) `rb=2,31–6,00 ms/f` desperdiçados com OpenGL 4.3 Compute offscreen lido de volta para CPU mesmo no modo SDL não-`gl_top`. Além disso, os vertex shaders embutidos do `SDL_render_gpu` (`SDL 3.4.18`) usam **DXIL SM 6.0** (`TEXCOORD0 = v_color`, `TEXCOORD1 = v_uv`).
- **Decisão:**
  1. Migrar o pós-processamento 2D (`xBR-lv2`, `Scale2x`, `Sharp Bilinear`, `Bilinear`, `Nearest`, `Unsharp`, `Vivid HD`/`DS Authentic`, `Scanlines`/`CRT`/`LCD Grid` e opacidade do PiP via `render_states[2]`) para o shader HLSL `runner/src/dos_postprocess.frag.hlsl` pré-compilado com `dxc -T ps_6_0 -E main -O3` em bytecode assinado DXIL embarcado em `runner/src/dos_gpu_shader_dxil.h` (`runner/src/dos_gpu_shader.{h,cpp}`), rodado sobre o backend SDL3 `gpu` em `direct3d12` (`dx12-gpu`) com upload apenas quando o quadro raw mudar (`dos_frame_identical`) e HUD em textura separada (`960x24`, atualizada só quando `revision` muda).
  2. Quando `!gl_top` e `NDS_3D_RENDERER=auto`, forçar `nds_gpu3d_use_soft_renderer(true)` sem inicializar `nds_compute_host_start(nullptr)` (mantendo `internal_resolution = 1` e `texture_upscale = 1` no `game.toml`) para eliminar `rb=2,3–6,0 ms/f`.
  3. Reduzir `kAudioStartFrames` para `3072` (sobrescrevível via `NDS_AUDIO_START_FRAMES`) e `kGlideStepFrames` para `32`.
  4. Compilar o `nds_runner` com `-DNDS_LEAN_DIAGNOSTICS=ON`, `-DNDS_GX_COMMAND_CACHE=ON`, `-DNDS_CAPTURE_VIEW_REUSE=ON`, `-DNDS_3D_GEOMETRY=NATIVE` e `-O2/-O3 -march=native` no Clang.
- **Por quê:** Bytecode DXIL SM 6.0 embarcado casa diretamente com os pipelines `SDL_GPU` D3D12 sem depender de `dxcompiler.dll` em runtime, reduz `pres` de `~5,0 ms` para `0,78–1,16 ms/f`, zera `readback_ns` (`0,00 ms`), elimina a queda inicial para `38,5 FPS` e mantém **59,7–59,9 FPS** com `0` underruns.
- **Reversal:** Se precisarmos distribuir um binário portátil entre microarquiteturas x86-64 sem AVX2 ou editar efeitos 2D em runtime sem rodar `dxc`, remover `-march=native` de `tools/build.py` ou trocar `dos_gpu_shader` pelo caminho CPU (`gpu_shader_active=false`).

### ADR-008: Menu gráfico Dear ImGui v1.92.9b (`F1`), correção de 3 telas e integração RecompLauncher
- **Contexto:** O menu anterior em `recomp_runtime_ui` renderizava um bitmap `512x384` via `menu_texture` sobre o centro da janela; em layouts duplos (`side-by-side`, `side-by-side-big`, `stacked`), a cópia de fundo criava uma 3ª tela aparente atrás do menu, além de limitar calibração ao vivo, fontes com acentuação PT-BR e navegação estilo launcher moderno.
- **Decisão:** Integrar **Dear ImGui v1.92.9b** (`imgui_impl_sdl3` + `imgui_impl_sdlrenderer3`) em `dos_imgui_menu.{h,cpp}` com tradução completa **PT-BR / EN** (`dos_i18n.{h,cpp}`) e fontes TrueType com faixa estendida (`0x0020..0x024F`). Durante o draw do overlay, suspender temporariamente `SDL_SetRenderLogicalPresentation` para desenhar na resolução nativa do monitor e pular completamente o caminho legado `g_runtime_menu_surface` / `menu_texture`. Por padrão o jogo abre direto (`dos_skip_launcher=true`) com acesso via **`F1`** / `Esc` / botão `Guide`, adicionando calibração GPU ao vivo (Brilho, Contraste, Saturação, Vinheta), tamanho do PiP (`20..50%`), `VSync`, zona morta do analógico, pausa/mudo em foco, save states slots `1–5`, backup de `.sav` e captura `F12`.
- **Por quê:** Elimina definitivamente o bug visual da 3ª tela, entrega UI nítida de port moderno em 1080p+ com mouse/teclado/controle e garante compatibilidade direta com o ecossistema RecompLauncher.
- **Reversal:** Se algum backend futuro sem `SDL_Renderer` SDL3 não suportar `ImGui_ImplSDLRenderer3`, o fallback legado `recomp_runtime_ui` continua compilado sob `!presentation.imgui_ready`.

### ADR-009: Tradução PT-BR via patch delta `DOSPATCH` em memória + `--validate-live-bytes` + GPU Shader dual DXIL/SPIR-V
- **Contexto:** A tradução em Português (BR) da ROM alterou `3` overlays (`ov000`, `ov004`, `ov005`), `88` arquivos de fontes/textos no NitroFS e `120` bytes no `ARM9` (rotinas de glifos/acentos). Como `dos_arm9` e `dos_arm7` não tinham validação de bytes vivos no dispatch, bancos recompilados com bytes da ROM USA poderiam interceptar funções traduzidas; além disso, Linux/Steam Deck e Android exigem shaders Vulkan SPIR-V ao lado do DXIL Windows.
- **Decisão:**
  1. Manter a ROM USA original intacta (`SHA-1: 47530ff87e608f88105a314fdf36dc385f8dec94`) para verificação do título e registro de bancos nativos, gerando um patch delta compacto [`mods/ptbr/dos-ptbr.dospatch`](../mods/ptbr/dos-ptbr.dospatch) (`DOSPATCH`, SHA-1 de origem/destino + CRC32) aplicado somente em RAM por `dos_rom_patch.{h,cpp}` via `--ptbr-patch` com alternância EN <-> PT-BR em tempo de execução (`reset_machine`).
  2. Emitir `dos_arm9` e `dos_arm7` com `--validate-live-bytes` em `tools/build.py` para que funções alteradas pela tradução entrem em fallback automático mantendo todo o restante da ROM em código C nativo a ~60 FPS.
  3. Compilar `dos_postprocess.frag.hlsl` também para **SPIR-V Vulkan 1.1** (`dos_gpu_shader_spirv.h`) com detecção automática DXIL (`direct3d12`) ou SPIR-V (`vulkan-gpu`), habilitando presets CMake, script Linux (`tools/build_linux.sh`) e esqueleto Android ARM64 (`android/`).
- **Por quê:** Zero redistribuição de ROM modificada, troca limpa de idioma sem reinicialização externa e suporte portátil DX12 + Vulkan sem depender de compilador de shader em runtime.
- **Reversal:** Caso futuras traduções reescrevam grande parte do código principal ARM9 e reduzam o acerto de validação em RAM, gerar um segundo conjunto de bancos nativos indexado pelo SHA-1 da ROM traduzida em `NDS_TITLE_BANK_DIRS`.

### ADR-010: Manifesto do SDK do RecompLauncher com `inputs`, kit de mídia procedural e documentação bilíngue
- **Contexto:** O `recomplauncher.json` anterior usava o campo legado `game` e um `prepare` que abria o runner interativo (com janela), mas a etapa `prepare` do SDK precisa rodar sem janela e o RecompLauncher 1.0 deixa de ler `game`. A página inicial e o launcher também pediam arte (`icon` `256x256`, `cover` `600x900`, `hero` `1920x620`, `logo` transparente `1000x500`, `wallpaper` `1920x1080`, `artwork` `1024x1024`), e a documentação estava só em PT-BR.
- **Decisão:**
  1. Declarar o jogo em `inputs[game]` (só `.nds`, `check.ids = ["ACVE"]`, `dumps` com tamanho `67108864` e CRC32 `135737f6`, calculados da ROM USA local) e passar a ROM por `{input:game}` em [`recomplauncher.json`](../recomplauncher.json), removendo `prepare` e preenchendo `config[0].new` com todos os 30 padrões INI, além de `looks`, `actions`, `system` e `exit_codes`.
  2. Gerar o kit de mídia completo (`icon.png`, `icon.ico`, `cover.png`, `cover.jpg`, `hero.png`, `hero.jpg`, `logo.png` transparente, `wallpaper.png`, `artwork.png` com cartucho DS e `catalog-entry.json`) de forma procedural em [`tools/prepare_media_assets.py`](../tools/prepare_media_assets.py), acompanhado de 3 capturas reais `1920x1080` em [`assets/screenshots/`](../assets/screenshots/) e testes de cabeçalho PNG/JPEG/ICO em stdlib pura em [`tests/test_recomplauncher.py`](../tests/test_recomplauncher.py).
  3. Estruturar toda a documentação de forma bilíngue com **Inglês (`EN`) primeiro** e **Português (BR) (`PT-BR`) depois**.
- **Por quê:** Elimina avisos no verificador `devtools.rs` do RecompLauncher, exibe o selo de dump USA verificado (`CRC32: 135737f6`), evita risco de direitos autorais em artes de terceiros e torna o repositório acessível internacionalmente e em português.
- **Reversal:** Se o runner ganhar um modo `--prepare` sem janela (por exemplo, para aquecer cache de shaders), adicionar `prepare` com `done`. Se arte comissionada substituir a procedural, manter os tamanhos exatos e validar com `python tools/prepare_media_assets.py --check-only`.

### ADR-011: Caminhos ancorados em `{install}`/`{data}`, executável Win32 standalone, padrão EN principal e mouse em combate
- **Contexto:** Na `v1.0.0`, o RecompLauncher iniciava `runtime/nds_runner.exe` com `cwd = {install}/runtime`, quebrando caminhos relativos (`game.toml`, `mods/ptbr/dos-ptbr.dospatch`, `run/bios`). Jogadores Windows fora do launcher também precisavam de um `.exe` de duplo clique com ícone embutido, idioma padrão em Inglês (`en`) com PT-BR secundário e cliques do mouse mapeáveis em combate (`Esquerdo` = Ataque, `Direito` = Especial, `Meio` = Dash) com limpeza por tecla e toque na tela inferior intacto.
- **Decisão:**
  1. Ancorar todos os caminhos de `start.args` em [`recomplauncher.json`](../recomplauncher.json) com `{install}` ou `{data}` e travar isso no `validate_manifest` de `tools/package_recomplauncher.py`.
  2. Compilar um launcher Win32 GUI estático sem DLLs extras (`launcher/launcher_win32.cpp` -> `CastlevaniaDawnOfSorrow.exe`) no final de `tools/build.py build`, embutindo `assets/recomplauncher/icon.ico` (`launcher/app_icon.rc`) tanto em `CastlevaniaDawnOfSorrow.exe` quanto em `runtime/nds_runner.exe`. Na primeira execução standalone, valida a ROM USA (`67.108.864` B, `ACVE`, CRC32 `135737f6`), instala em `game/` e oferece criar o atalho `.lnk` na Área de Trabalho via COM `IShellLinkW`.
  3. Definir `en` como padrão de `ui_language` e `game_language` em `game.toml` e `recomplauncher.json`, mantendo `dos-ptbr.dospatch` pronto em RAM como opção secundária no `F1`.
  4. Codificar botões do mouse em `501..505` (`< 512`, aceitos nativamente por `nds_valid_binding` / TOML / INI), acompanhar `mouse_buttons_held` em paralelo ao toque da tela inferior em `frontend.cpp`, definir o padrão (`Mouse Left = Y`, `Mouse Right = A`, `Q = L`, `R = R`, `Mouse Mid = L`) e adicionar botão `X` por célula, **Limpar Mapeamento** e **Restaurar Padrão** em `dos_imgui_menu.cpp`.
- **Por quê:** Elimina a falha de inicialização no RecompLauncher em qualquer PC Windows, entrega experiência de port nativo com 1 clique mantendo regras clean-room, alinha o idioma padrão internacional e torna o combate com mouse + teclado natural sem perder os cliques de toque em menus e selos mágicos.
- **Reversal:** Se uma versão futura do `ndsrecomp` reservar códigos de scancode acima de `500`, mover o mapeamento do mouse para uma chave INI/TOML dedicada (`dos_mouse_bindings`). Os caminhos `{install}`/`{data}` continuam válidos mesmo que o RecompLauncher altere seu `cwd`.

### Licenças de Terceiros (Apenas Informativo)
- `RetroPortingToolKit/ndsrecomp`:
  - Recompiler, finder e ferramentas (`LICENSE`): PolyForm Noncommercial License 1.0.0 + permissões adicionais em `PERMISSIONS.md` (doações/patrocínio/anúncios permitidos desde que acesso ao software/updates seja gratuito).
  - Runner e oracle (`LICENSE-MIT` + `LICENSE-GPL`): código próprio em MIT, linkado contra código derivado do melonDS sob GPL-3.0-or-later (`nds_runner.exe` compilado é uma obra combinada sob GPL-3.0-or-later).
  - `third_party/freebios`: BSD-2-Clause.
- `RetroPortingToolKit/recomp-ui`: MIT License (`../recomp-ui/LICENSE`).
- `libsdl-org/SDL` (SDL3 3.4.18): zlib License.
- `mstorsjo/llvm-mingw` (20261020): ISC / Apache-2.0 with LLVM Exception.
- `AetiasHax/ds-decomp` (`dsd` v0.12.1): MIT License.
- `ocornut/imgui` (`Dear ImGui` v1.92.9b, SDL3 + SDLRenderer3 backends): MIT License.
- Tradução Português (BR) de referência (*romsportugues.com* T1.0): creditada ao projeto original de tradução de fãs e aplicada apenas como patch delta em memória sobre ROM USA fornecida pelo usuário.
- Kit de mídia em `assets/recomplauncher/`: arte procedural original gerada por `tools/prepare_media_assets.py`; capturas em `assets/screenshots/` extraídas diretamente do runtime deste projeto.

[Voltar ao topo / Back to top](#technical-decisions--decisões-técnicas--castlevania-dawn-of-sorrow-recompiled)
