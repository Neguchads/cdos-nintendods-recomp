# HANDOFF — Castlevania: Dawn of Sorrow: Recompiled (ACVE)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Current Technical State
Native static AOT recompilation port featuring **Dear ImGui v1.92.9b (`F1`) overlay menu**, permanent **3-screens bug fix**, **in-memory PT-BR translation (`DOSPATCH`)** sustaining **59.86 FPS on `dx12-gpu`**, **dual DXIL + SPIR-V GPU shaders (`vulkan-gpu` verified at 60.0 FPS)**, **full RecompLauncher 1.0 SDK integration (`recomplauncher.json` with `inputs`, verified `dumps`, `config.new`, `looks`, `actions`)**, **complete RecompLauncher media kit (`assets/recomplauncher/` & `assets/screenshots/`)**, **bilingual EN -> PT-BR documentation**, and public GitHub repository [`Neguchads/cdos-nintendods-recomp`](https://github.com/Neguchads/cdos-nintendods-recomp) with **Dependabot** and **GitHub Actions CI**.

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
  - `assets/recomplauncher/{icon.png,icon.ico,cover.png,cover.jpg,hero.png,hero.jpg,logo.png,wallpaper.png,artwork.png,catalog-entry.json}` and `assets/screenshots/{gameplay-dx12-pip.png,imgui-menu-f1.png,vulkan-spirv-ptbr.png}`.
  - `mods/ptbr/dos-ptbr.dospatch`, `tools/build_ptbr_patch.py`, `tests/test_ptbr_patch.py`.
  - `CMakePresets.json`, `tools/build_linux.sh`, `android/`, `.github/dependabot.yml`, `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore`, `docs/MULTIPLATFORM.md`.
  - `tools/build.py`, `play.bat`, `game.toml`, `patches/ndsrecomp-local.patch`, `docs/DECISIONS.md` (`ADR-001`..`ADR-010`), `docs/rom-analysis.md`, `README.md`, `ROADMAP.md`, `NOTAS.md`.

### Verifications Executed
- `ctest --test-dir generated/build-runner -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure`: **3/3 passed** (`0.21s`).
- `python tools/prepare_media_assets.py --check-only`: **OK** (`8` RecompLauncher images + `icon.ico` + `catalog-entry.json` + `3` in-engine screenshots validated).
- `python -m unittest discover -s tests -v`: **22/22 passed** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `recomplauncher` including media kit header dimension checks, `{install}`/`{data}` `start.args` guards, and runtime artifact staging exclusions).
- `python tools/package_recomplauncher.py --validate-only`: **OK** (all 30 INI keys + `inputs[game]` + verified dump `CRC32: 135737f6` + `{install}`/`{data}` `start.args` + media kit validated).
- **End-to-end RecompLauncher simulation (`cwd = {install}/runtime`, `RECOMPLAUNCHER=1`, `RECOMPLAUNCHER_DATA={data}`):** boots cleanly from staged zip, loads `{install}/game.toml` and `{install}/mods/ptbr/dos-ptbr.dospatch`, activates `dx12-gpu` + `DXIL ps_6_0`, writes BIOS/firmware/save only inside `{data}`, zero files created inside `{install}/runtime`.
- `python tools/build.py smoke`: **PASS** (`724` vblanks in `run/smoke/report.json`).
- **Clean `dx12-gpu` PT-BR benchmark (`420` frames, isolated INI, `NDS_FRONTEND_AUDIO_MUTE=1`):** **`59.86 FPS`**, `emu_mean=3.72ms`, `pres_mean=0.78ms`, `rb_max=0.000ms`, `underruns=0`.
- **Visual `vulkan-gpu` SPIR-V PT-BR capture (`1920x1080`):** `[sdl] render driver: vulkan-gpu (vsync=0)`, `[dos-gpu] HLSL shader active (SPIR-V Vulkan)`, full HUD `FPS:60.0 EMU:2.0MS PRES:0.3MS T3:0.0K VULKAN-GPU XBR2X SIDE-BY-SIDE PT-BR`.

### Known Limits
- Windows (`dx12-gpu` and `vulkan-gpu`) is compiled and verified locally; Linux/Steam Deck and Android ARM64 files are ready for compilation in a Linux or Android SDK/NDK environment (not compiled on this Windows machine).
- User `saves/dos.sav` and `saves/dos-settings.ini` remain untouched.

### Next Steps
1. Run `.\play.bat` to play directly in PT-BR or EN with the **`F1`** Dear ImGui menu.
2. In **RecompLauncher**, import `recomplauncher.json` (or `dist/castlevania-dos-recomp-win64.zip`) and use the artwork in `assets/recomplauncher/` via **Customize** or [`recompstore.com/hub`](https://recompstore.com/hub).

[Back to top / Voltar ao topo](#handoff--castlevania-dawn-of-sorrow-recompiled-acve)

---

<a id="português-br"></a>

## Português (BR)

### Estado Técnico Atual
Port nativo de recompilação estática AOT atualizado com **menu gráfico Dear ImGui v1.92.9b (`F1`)**, correção definitiva do **bug da 3ª tela**, **tradução PT-BR em memória (`DOSPATCH`)** mantendo **59,86 FPS em `dx12-gpu`**, **shader dual DXIL + SPIR-V (`vulkan-gpu` validado a 60,0 FPS)**, **integração completa com o SDK 1.0 do RecompLauncher (`recomplauncher.json` com `inputs`, `dumps` verificados, `config.new`, `looks`, `actions`)**, **kit de mídia oficial do RecompLauncher (`assets/recomplauncher/` e `assets/screenshots/`)**, **documentação bilíngue EN -> PT-BR** e repositório público [`Neguchads/cdos-nintendods-recomp`](https://github.com/Neguchads/cdos-nintendods-recomp) com **Dependabot** e **GitHub Actions CI**.

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
  - `assets/recomplauncher/{icon.png,icon.ico,cover.png,cover.jpg,hero.png,hero.jpg,logo.png,wallpaper.png,artwork.png,catalog-entry.json}` e `assets/screenshots/{gameplay-dx12-pip.png,imgui-menu-f1.png,vulkan-spirv-ptbr.png}`.
  - `mods/ptbr/dos-ptbr.dospatch`, `tools/build_ptbr_patch.py`, `tests/test_ptbr_patch.py`.
  - `CMakePresets.json`, `tools/build_linux.sh`, `android/`, `.github/dependabot.yml`, `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore`, `docs/MULTIPLATFORM.md`.
  - `tools/build.py`, `play.bat`, `game.toml`, `patches/ndsrecomp-local.patch`, `docs/DECISIONS.md` (`ADR-001`..`ADR-010`), `docs/rom-analysis.md`, `README.md`, `ROADMAP.md`, `NOTAS.md`.

### Verificações Executadas
- `ctest --test-dir generated/build-runner -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure`: **3/3 passaram** (`0.21s`).
- `python tools/prepare_media_assets.py --check-only`: **OK** (`8` imagens RecompLauncher + `icon.ico` + `catalog-entry.json` + `3` capturas reais validadas).
- `python -m unittest discover -s tests -v`: **22/22 passaram** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `recomplauncher` incluindo validação de dimensões de cabeçalho do kit de mídia, bloqueio a caminhos relativos em `start.args` e exclusão de artefatos locais no staging de `runtime/`).
- `python tools/package_recomplauncher.py --validate-only`: **OK** (todas as 30 chaves INI + `inputs[game]` + dump verificado `CRC32: 135737f6` + caminhos `{install}`/`{data}` + kit de mídia validados).
- **Simulação ponta a ponta do RecompLauncher (`cwd = {install}/runtime`, `RECOMPLAUNCHER=1`, `RECOMPLAUNCHER_DATA={data}`):** inicia sem erro a partir do zip empacotado, carrega `{install}/game.toml` e `{install}/mods/ptbr/dos-ptbr.dospatch`, ativa `dx12-gpu` + `DXIL ps_6_0`, grava BIOS/firmware/save apenas em `{data}` e não cria nenhum arquivo em `{install}/runtime`.
- `python tools/build.py smoke`: **PASS** (`724` vblanks em `run/smoke/report.json`).
- **Benchmark limpo `dx12-gpu` PT-BR (`420` quadros em INI isolado, `NDS_FRONTEND_AUDIO_MUTE=1`):** **`59.86 FPS`**, `emu_mean=3.72ms`, `pres_mean=0.78ms`, `rb_max=0.000ms`, `underruns=0`.
- **Captura visual `vulkan-gpu` SPIR-V PT-BR (`1920x1080`):** `[sdl] render driver: vulkan-gpu (vsync=0)`, `[dos-gpu] HLSL shader active (SPIR-V Vulkan)`, HUD completo `FPS:60.0 EMU:2.0MS PRES:0.3MS T3:0.0K VULKAN-GPU XBR2X SIDE-BY-SIDE PT-BR`.

### Limites Conhecidos
- O build Windows (`dx12-gpu` e `vulkan-gpu`) foi compilado e testado localmente; os arquivos Linux/Steam Deck e Android ARM64 estão prontos para compilação em ambiente Linux/Android NDK (não compilados nesta máquina Windows).
- `saves/dos.sav` e `saves/dos-settings.ini` do usuário foram preservados sem alteração.

### Próximos Passos
1. Executar `.\play.bat` para jogar diretamente em PT-BR ou EN com o menu Dear ImGui no **`F1`**.
2. No **RecompLauncher**, importar `recomplauncher.json` (ou `dist/castlevania-dos-recomp-win64.zip`) e aplicar as artes de `assets/recomplauncher/` via **Customize** ou [`recompstore.com/hub`](https://recompstore.com/hub).

[Voltar ao topo / Back to top](#handoff--castlevania-dawn-of-sorrow-recompiled-acve)
