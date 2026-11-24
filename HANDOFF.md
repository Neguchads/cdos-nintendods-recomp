# HANDOFF — Castlevania: Dawn of Sorrow: Recompiled (ACVE)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Current Technical State (Branch `development`)
Branch `development` extends `v1.0.1` (`main` `332b293`) with **P0 (Mod Bundle Importer & Semantic NDS Diff)**, **P1 (Definitive Edition + PT-BR Semantic Composition, Isolated Profile Saves/Savestates & `F1` Content/Mods UI)**, **P2 (Native Windows Media Foundation + SDL3 Opening Video Player)**, and **full researched author credits** in [`docs/CREDITS.md`](docs/CREDITS.md).

### Newly Added / Updated on `development`
- **Python Pipeline & Tests (`castlevania-dos-recomp/`):**
  - `tools/vcdiff_ips.py`: pure-Python RFC 3284 VCDIFF and IPS decoders.
  - `tools/import_mod_bundle.py`: magic-byte + SHA-256 classifier rejecting Dominus PC / Portrait of Ruin files and importing compatible DoS mods + `mods/intro/opening.mp4` (`mods/catalog.json`).
  - `tools/diff_dos_mods.py`: NDS Header/ARM9/ARM7/41 Overlays/NitroFS FNT+FAT semantic diff (`mods/reports/definitive-vs-ptbr.json`).
  - `tools/compose_dos_mods.py`: semantic merger producing `mods/definitive/dos-definitive-en.dospatch` (`615 KB`) and `mods/definitive/dos-definitive-ptbr.dospatch` (`752 KB`) with recomputed header CRC16 (`mods/reports/definitive-composition.json`).
  - `tests/test_mod_pipeline.py` (5 new unit tests -> **34/34** Python tests passing).
  - `game.toml`, `recomplauncher.json`, `tools/package_recomplauncher.py`, `tools/build.py`, `play.bat`, `launcher/launcher_win32.cpp`, `tests/test_recomplauncher.py`, `docs/CREDITS.md`, `docs/DECISIONS.md` (ADR-012), `README.md`, `ROADMAP.md`, `NOTAS.md`, `patches/ndsrecomp-local.patch` (`656.6 KiB`).
- **C++ Runtime (`..\ndsrecomp\runner\src\`):**
  - `dos_mod_profile.{h,cpp}`: `DosRomPatchSet`, `dos_mod_load_patch_set`, `dos_build_active_rom`, `dos_profile_savestate_dir`, `dos_profile_save_path`.
  - `dos_intro_player.{h,cpp}`: `dos_intro_validate_mp4_file`, `dos_play_intro_video` (Windows Media Foundation `IMFSourceReader` + SDL3 texture/audio, zero FFmpeg DLLs).
  - Wired into `dos_enhancements.{h,cpp}`, `dos_i18n.{h,cpp}`, `dos_imgui_menu.{h,cpp}`, `frontend_config.cpp`, `frontend.{h,cpp}`, `main.cpp`, `CMakeLists.txt`, and `tests/dos_enhancements_test.cpp`.

### Verifications Executed on `development`
- `ctest --test-dir generated/build-runner -R "^(dos_enhancements_test|frontend_config_test|screen_layout_test)$" --output-on-failure`: **3/3 passed** (`0.37s`).
- `python -m unittest discover -s tests -v`: **34/34 passed** (`2.848s`).
- `python tools/import_mod_bundle.py "C:\Users\Desktop\Downloads\CDOS NDS"`: `inspecionados=17 aceitos=3 rejeitados=8`.
- `python tools/compose_dos_mods.py`: roundtrip-verified `dos-definitive-en.dospatch` (`615,288 B`) + `dos-definitive-ptbr.dospatch` (`752,796 B`).
- **Live E2E (`nds_runner.exe`):**
  - `P2_INTRO_AND_DEFINITIVE_EN`: `[content] active ROM: Definitive Edition (English) (modset=2333f02b22dc)`, `[intro-video] playing ...\mods\intro\opening.mp4 (640x480, audio=off)` -> `finished (frames=53, skipped=1, quit=0)` -> clean DX12 boot.
  - `P1_DEFINITIVE_PTBR` + Audio ON: `[content] active ROM: Definitive Edition (PT-BR) (modset=6ffc88b8023a)`, `[intro-video] playing ... (640x480, audio=on)` -> `finished (frames=35, skipped=1, quit=0)`, isolated `definitive/dos.sav`, `present=0.66ms`.
  - `P2_FALLBACK_MISSING_INTRO`: clean Original USA boot with zero errors when `opening.mp4` is absent.
- `git apply --stat patches/ndsrecomp-local.patch`: **26 files**, `656.6 KiB` (`< 2 MiB` CI limit).

### Files Added / Updated
- **`..\ndsrecomp\runner\third_party\imgui\`:** Dear ImGui v1.92.9b (`15` source files + `imgui_impl_sdl3` and `imgui_impl_sdlrenderer3` backends).
- **`..\ndsrecomp\runner\src\`:**
  - `dos_i18n.{h,cpp}`: full EN / PT-BR bilingual string catalog.
  - `dos_imgui_menu.{h,cpp}`: 6-tab overlay menu + toasts + FPS Sparkline + live input remapping.
  - `dos_rom_patch.{h,cpp}`: in-RAM `DOSPATCH` validator and applier (magic, source/target SHA-1, payload CRC32).
  - `dos_postprocess.frag.hlsl`, `dos_gpu_shader_dxil.h`, `dos_gpu_shader_spirv.h`, `dos_gpu_shader.{h,cpp}`: live calibration uniforms (`brightness`, `contrast`, `saturation`, `vignette`) + dual **DXIL SM 6.0** and **SPIR-V Vulkan 1.1** support.
  - `screen_layout.h`, `dos_enhancements.{h,cpp}`, `frontend_config.cpp`, `frontend.{h,cpp}`, `main.cpp`, `CMakeLists.txt`, `tests/{dos_enhancements_test,screen_layout_test}.cpp`: new INI settings (`36` loader/saver keys), `pip_size_pct`, `hud_mode`, `vsync`, `pause_on_menu`, `pause_unfocused`, `mute_unfocused`, `stick_deadzone_pct`, `--ptbr-patch`, `--validate-live-bytes`, live language switching, and removal of legacy `menu_texture`.
- **`castlevania-dos-recomp\`:**
  - `recomplauncher.json`, `tools/package_recomplauncher.py`, `tools/prepare_media_assets.py`, `tests/test_recomplauncher.py`, `docs/RECOMPLAUNCHER.md`.
  - `launcher/launcher_win32.cpp`, `launcher/app_icon.rc`, `tests/test_launcher.py` (compiles `CastlevaniaDawnOfSorrow.exe` and embeds `assets/recomplauncher/icon.ico` into both `CastlevaniaDawnOfSorrow.exe` and `runtime/nds_runner.exe` at the end of `tools/build.py build`).
  - `assets/recomplauncher/{icon.png,icon.ico,cover.png,cover.jpg,hero.png,hero.jpg,logo.png,wallpaper.png,artwork.png,catalog-entry.json}` and `assets/screenshots/{gameplay-dx12-pip.png,imgui-menu-f1.png,vulkan-spirv-ptbr.png}`.
  - `mods/ptbr/dos-ptbr.dospatch`, `tools/build_ptbr_patch.py`, `tests/test_ptbr_patch.py`.
  - `CMakePresets.json`, `tools/build_linux.sh`, `android/`, `.github/dependabot.yml`, `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore`, `docs/MULTIPLATFORM.md`.
  - `tools/build.py`, `play.bat`, `game.toml`, `patches/ndsrecomp-local.patch`, `docs/DECISIONS.md` (`ADR-001`..`ADR-010`), `docs/rom-analysis.md`, `README.md`, `ROADMAP.md`, `NOTAS.md`.

### Verifications Executed
- `ctest --test-dir generated/build-runner -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure`: **3/3 passed** (`0.21s`).
- `python tools/prepare_media_assets.py --check-only`: **OK** (`8` RecompLauncher images + `icon.ico` + `catalog-entry.json` + `3` in-engine screenshots validated).
- `python -m unittest discover -s tests -v`: **29/29 passed** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `recomplauncher`, and `launcher` including mouse combat + `Q`/`R` defaults, EN-first language defaults, PE `.rsrc` `RT_ICON`/`RT_GROUP_ICON` checks, `ACVE`/CRC32 setup validation, local `game/` install, and COM `.lnk` shortcut creation).
- `python tools/package_recomplauncher.py --validate-only`: **OK** (all 30 INI keys + `inputs[game]` + verified dump `CRC32: 135737f6` + `{install}`/`{data}` `start.args` + media kit validated).
- **End-to-end RecompLauncher simulation (`cwd = {install}/runtime`, `RECOMPLAUNCHER=1`, `RECOMPLAUNCHER_DATA={data}`):** boots cleanly from staged zip, loads `{install}/game.toml` and `{install}/mods/ptbr/dos-ptbr.dospatch`, activates `dx12-gpu` + `DXIL ps_6_0`, writes BIOS/firmware/save only inside `{data}`, zero files created inside `{install}/runtime`.
- `python tools/build.py smoke`: **PASS** (`724` vblanks in `run/smoke/report.json`).
- **Clean `dx12-gpu` PT-BR benchmark (`420` frames, isolated INI, `NDS_FRONTEND_AUDIO_MUTE=1`):** **`59.86 FPS`**, `emu_mean=3.72ms`, `pres_mean=0.78ms`, `rb_max=0.000ms`, `underruns=0`.
- **Visual `vulkan-gpu` SPIR-V PT-BR capture (`1920x1080`):** `[sdl] render driver: vulkan-gpu (vsync=0)`, `[dos-gpu] HLSL shader active (SPIR-V Vulkan)`, full HUD `FPS:60.0 EMU:2.0MS PRES:0.3MS T3:0.0K VULKAN-GPU XBR2X SIDE-BY-SIDE PT-BR`.

### Known Limits
- Windows (`dx12-gpu` and `vulkan-gpu`) is compiled and verified locally; Linux/Steam Deck and Android ARM64 files are ready for compilation in a Linux or Android SDK/NDK environment (not compiled on this Windows machine).
- User `saves/dos.sav` and `saves/dos-settings.ini` remain untouched.

### Next Steps
1. Run `.\CastlevaniaDawnOfSorrow.exe` (or `.\play.bat` fallback) to play in **English (`en`)** by default or switch to **PT-BR** live inside the **`F1`** Dear ImGui menu.
2. Publish GitHub Release **`v1.0.1`** (`--latest`) with `dist/CastlevaniaDawnOfSorrowRecomp-v1.0.1-Windows-x64.zip` + `.sha256` so RecompLauncher updates players automatically.

[Back to top / Voltar ao topo](#handoff--castlevania-dawn-of-sorrow-recompiled-acve)

---

<a id="português-br"></a>

## Português (BR)

### Estado Técnico Atual (Branch `development`)
A branch `development` estende a `v1.0.1` (`main` `332b293`) com **P0 (Importador de Pacote de Mods & Diff Semântico NDS)**, **P1 (Composição Semântica Definitive Edition + PT-BR, Isolamento de Saves/Savestates por Perfil e UI de Conteúdo/Mods no `F1`)**, **P2 (Player Nativo de Abertura Windows Media Foundation + SDL3)** e **créditos completos pesquisados** em [`docs/CREDITS.md`](docs/CREDITS.md).

### Adicionado / Atualizado em `development`
- **Pipeline Python & Testes (`castlevania-dos-recomp/`):** `tools/vcdiff_ips.py`, `tools/import_mod_bundle.py`, `tools/diff_dos_mods.py`, `tools/compose_dos_mods.py`, `tests/test_mod_pipeline.py`, `mods/definitive/dos-definitive-{en,ptbr}.dospatch`, `mods/catalog.json`, `mods/reports/*.json`, `game.toml`, `recomplauncher.json`, `tools/package_recomplauncher.py`, `tools/build.py`, `play.bat`, `launcher/launcher_win32.cpp`, `docs/CREDITS.md`, `docs/DECISIONS.md` (ADR-012) e `patches/ndsrecomp-local.patch` (`656,6 KiB`).
- **Runtime C++ (`..\ndsrecomp\runner\src\`):** `dos_mod_profile.{h,cpp}`, `dos_intro_player.{h,cpp}` (Windows Media Foundation + SDL3, zero FFmpeg), integrados em `dos_enhancements.{h,cpp}`, `dos_i18n.{h,cpp}`, `dos_imgui_menu.{h,cpp}`, `frontend_config.cpp`, `frontend.{h,cpp}`, `main.cpp`, `CMakeLists.txt` e `tests/dos_enhancements_test.cpp`.

### Verificações Executadas em `development`
- `ctest`: **3/3 passaram** (`0.37s`).
- `unittest`: **34/34 passaram** (`2.848s`).
- **E2E ao vivo (`nds_runner.exe`):** abertura `opening.mp4` decodificada nativamente em 640x480 (`53` frames com `audio=off` e `35` frames com `audio=on`), boot limpo em `Definitive Edition (English)` (`modset=2333f02b22dc`), `Definitive Edition (PT-BR)` (`modset=6ffc88b8023a`) com `definitive/dos.sav` isolado, e fallback silencioso quando `opening.mp4` está ausente.

### Arquivos Adicionados / Atualizados
- **`..\ndsrecomp\runner\third_party\imgui\`:** Dear ImGui v1.92.9b (`15` arquivos + backends `imgui_impl_sdl3` e `imgui_impl_sdlrenderer3`).
- **`..\ndsrecomp\runner\src\`:**
  - `dos_i18n.{h,cpp}`: catálogo bilíngue completo EN / PT-BR.
  - `dos_imgui_menu.{h,cpp}`: menu overlay moderno de 6 abas + toasts + Sparkline FPS + remapeamento ao vivo.
  - `dos_rom_patch.{h,cpp}`: aplicador/validador `DOSPATCH` (magic, SHA-1 origem/destino, CRC32) em RAM.
  - `dos_postprocess.frag.hlsl`, `dos_gpu_shader_dxil.h`, `dos_gpu_shader_spirv.h`, `dos_gpu_shader.{h,cpp}`: uniformes de calibração (`brightness`, `contrast`, `saturation`, `vignette`) + suporte dual **DXIL SM 6.0** e **SPIR-V Vulkan 1.1**.
  - `screen_layout.h`, `dos_enhancements.{h,cpp}`, `frontend_config.cpp`, `frontend.{h,cpp}`, `main.cpp`, `CMakeLists.txt`, `tests/{dos_enhancements_test,screen_layout_test}.cpp`: novos campos INI (`36` chaves no loader/saver), `pip_size_pct`, `hud_mode`, `vsync`, `pause_on_menu`, `pause_unfocused`, `mute_unfocused`, `stick_deadzone_pct`, `--ptbr-patch`, `--validate-live-bytes`, troca de idioma ao vivo e eliminação do `menu_texture` legado.
- **`castlevania-dos-recomp\`:**
  - `recomplauncher.json`, `tools/package_recomplauncher.py`, `tools/prepare_media_assets.py`, `tests/test_recomplauncher.py`, `docs/RECOMPLAUNCHER.md`.
  - `launcher/launcher_win32.cpp`, `launcher/app_icon.rc`, `tests/test_launcher.py` (compila `CastlevaniaDawnOfSorrow.exe` e embute `assets/recomplauncher/icon.ico` tanto em `CastlevaniaDawnOfSorrow.exe` quanto em `runtime/nds_runner.exe` ao final de `tools/build.py build`).
  - `assets/recomplauncher/{icon.png,icon.ico,cover.png,cover.jpg,hero.png,hero.jpg,logo.png,wallpaper.png,artwork.png,catalog-entry.json}` e `assets/screenshots/{gameplay-dx12-pip.png,imgui-menu-f1.png,vulkan-spirv-ptbr.png}`.
  - `mods/ptbr/dos-ptbr.dospatch`, `tools/build_ptbr_patch.py`, `tests/test_ptbr_patch.py`.
  - `CMakePresets.json`, `tools/build_linux.sh`, `android/`, `.github/dependabot.yml`, `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore`, `docs/MULTIPLATFORM.md`.
  - `tools/build.py`, `play.bat`, `game.toml`, `patches/ndsrecomp-local.patch`, `docs/DECISIONS.md` (`ADR-001`..`ADR-010`), `docs/rom-analysis.md`, `README.md`, `ROADMAP.md`, `NOTAS.md`.

### Verificações Executadas
- `ctest --test-dir generated/build-runner -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure`: **3/3 passaram** (`0.21s`).
- `python tools/prepare_media_assets.py --check-only`: **OK** (`8` imagens RecompLauncher + `icon.ico` + `catalog-entry.json` + `3` capturas reais validadas).
- `python -m unittest discover -s tests -v`: **29/29 passaram** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `recomplauncher` e `launcher` incluindo padrão mouse em combate + `Q`/`R`, padrão EN principal com PT-BR secundário, checagem de recursos PE `RT_ICON`/`RT_GROUP_ICON`, validação `ACVE`/CRC32 no setup, instalação local em `game/` e criação de atalho `.lnk` via COM).
- `python tools/package_recomplauncher.py --validate-only`: **OK** (todas as 30 chaves INI + `inputs[game]` + dump verificado `CRC32: 135737f6` + caminhos `{install}`/`{data}` + kit de mídia validados).
- **Simulação ponta a ponta do RecompLauncher (`cwd = {install}/runtime`, `RECOMPLAUNCHER=1`, `RECOMPLAUNCHER_DATA={data}`):** inicia sem erro a partir do zip empacotado, carrega `{install}/game.toml` e `{install}/mods/ptbr/dos-ptbr.dospatch`, ativa `dx12-gpu` + `DXIL ps_6_0`, grava BIOS/firmware/save apenas em `{data}` e não cria nenhum arquivo em `{install}/runtime`.
- `python tools/build.py smoke`: **PASS** (`724` vblanks em `run/smoke/report.json`).
- **Benchmark limpo `dx12-gpu` PT-BR (`420` quadros em INI isolado, `NDS_FRONTEND_AUDIO_MUTE=1`):** **`59.86 FPS`**, `emu_mean=3.72ms`, `pres_mean=0.78ms`, `rb_max=0.000ms`, `underruns=0`.
- **Captura visual `vulkan-gpu` SPIR-V PT-BR (`1920x1080`):** `[sdl] render driver: vulkan-gpu (vsync=0)`, `[dos-gpu] HLSL shader active (SPIR-V Vulkan)`, HUD completo `FPS:60.0 EMU:2.0MS PRES:0.3MS T3:0.0K VULKAN-GPU XBR2X SIDE-BY-SIDE PT-BR`.

### Limites Conhecidos
- O build Windows (`dx12-gpu` e `vulkan-gpu`) foi compilado e testado localmente; os arquivos Linux/Steam Deck e Android ARM64 estão prontos para compilação em ambiente Linux/Android NDK (não compilados nesta máquina Windows).
- `saves/dos.sav` e `saves/dos-settings.ini` do usuário foram preservados sem alteração.

### Próximos Passos
1. Executar `.\CastlevaniaDawnOfSorrow.exe` (ou `.\play.bat` como alternativa) para jogar em **Inglês (`en`)** por padrão ou alternar para **PT-BR** ao vivo no menu Dear ImGui (**`F1`**).
2. Publicar a GitHub Release **`v1.0.1`** (`--latest`) com `dist/CastlevaniaDawnOfSorrowRecomp-v1.0.1-Windows-x64.zip` + `.sha256` para o RecompLauncher atualizar os jogadores automaticamente.

[Voltar ao topo / Back to top](#handoff--castlevania-dawn-of-sorrow-recompiled-acve)
