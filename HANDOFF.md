# HANDOFF — Castlevania: Dawn of Sorrow Recomp (ACVE)

## Estado técnico atual
Port atualizado com **menu gráfico Dear ImGui (`F1`)**, correção definitiva do **bug da 3ª tela**, **tradução PT-BR em memória (`DOSPATCH`)** mantendo **59,86 FPS em `dx12-gpu`**, **shader dual DXIL + SPIR-V (`vulkan-gpu` validado)** e empacotamento oficial para o **RecompLauncher** (`recomplauncher.json`).

## Arquivos adicionados / atualizados nesta entrega
- **`..\ndsrecomp\runner\third_party\imgui\`:** Dear ImGui v1.92.9b (`15` arquivos + backends `imgui_impl_sdl3` e `imgui_impl_sdlrenderer3`).
- **`..\ndsrecomp\runner\src\`:**
  - `dos_i18n.{h,cpp}`: catálogo bilíngue completo EN / PT-BR.
  - `dos_imgui_menu.{h,cpp}`: menu overlay moderno de 6 abas + toasts + Sparkline FPS + remapeamento ao vivo.
  - `dos_rom_patch.{h,cpp}`: aplicador/validador `DOSPATCH` (magic, SHA-1 origem/destino, CRC32) em RAM.
  - `dos_postprocess.frag.hlsl`, `dos_gpu_shader_dxil.h`, `dos_gpu_shader_spirv.h`, `dos_gpu_shader.{h,cpp}`: uniformes de calibração (`brightness`, `contrast`, `saturation`, `vignette`) + suporte dual **DXIL SM 6.0** e **SPIR-V Vulkan 1.1**.
  - `screen_layout.h`, `dos_enhancements.{h,cpp}`, `frontend_config.cpp`, `frontend.{h,cpp}`, `main.cpp`, `CMakeLists.txt`, `tests/{dos_enhancements_test,screen_layout_test}.cpp`: novos campos INI (`36` chaves no loader/saver), `pip_size_pct`, `hud_mode`, `vsync`, `pause_on_menu`, `pause_unfocused`, `mute_unfocused`, `stick_deadzone_pct`, `--ptbr-patch`, `--validate-live-bytes`, troca de idioma ao vivo e eliminação do `menu_texture` legado.
- **`castlevania-dos-recomp\`:**
  - `mods/ptbr/dos-ptbr.dospatch`, `tools/build_ptbr_patch.py`, `tests/test_ptbr_patch.py`.
  - `recomplauncher.json`, `tools/package_recomplauncher.py`, `tests/test_recomplauncher.py`, `docs/RECOMPLAUNCHER.md`, `dist/castlevania-dos-recomp-win64{.zip,/}`.
  - `CMakePresets.json`, `tools/build_linux.sh`, `android/`, `.github/dependabot.yml`, `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore`, `docs/MULTIPLATFORM.md`.
  - `tools/build.py`, `play.bat`, `game.toml`, `patches/ndsrecomp-local.patch`, `docs/DECISIONS.md` (`ADR-008`, `ADR-009`), `README.md`, `ROADMAP.md`, `NOTAS.md`.

## Verificações executadas após a última edição de código
- `tools/build.py banks`: `dos_arm9` (`3913` funções) e `dos_arm7` (`1268` funções) regenerados com `--validate-live-bytes`.
- `tools/build.py build`: **PASS** -> `runtime/nds_runner.exe`.
- `ctest --test-dir generated/build-runner -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure`: **3/3 passaram** (`0.21s`).
- `python -m unittest discover -s tests -v`: **14/14 passaram** (`2.510s`).
- `python tools/build.py smoke`: **PASS** (`724` vblanks em `run/smoke/report.json`).
- **Benchmark limpo `dx12-gpu` PT-BR (`420` quadros em INI isolado, `NDS_FRONTEND_AUDIO_MUTE=1`, sem captura BMP durante medição):**
  - `steady=360` -> **`59.86 FPS`**, `emu_mean=3.72ms`, `pres_mean=0.78ms` (`p95=1.24ms`), `rb_max=0.000ms`, `underruns=0`.
- **Captura visual `dx12-gpu` `SideBySide` + Menu PT-BR aberto (`frame-240.png` `1920x1080`):**
  - Apenas **2** telas reais atrás do overlay (`Licenciado pela Nintendo` visível), zero 3ª tela, textos acentuados em Português nítidos.
- **Captura visual `vulkan-gpu` SPIR-V PT-BR (`frame-240.png` `1920x1080`):**
  - `[sdl] render driver: vulkan-gpu (vsync=0)`, `[dos-gpu] HLSL shader active (SPIR-V Vulkan)`, HUD completo `FPS:60.0 EMU:2.0MS PRES:0.3MS T3:0.0K VULKAN-GPU XBR2X SIDE-BY-SIDE PT-BR` sem truncamento.
- `python tools/package_recomplauncher.py`: validou todas as 30 chaves INI e gerou `dist/castlevania-dos-recomp-win64.zip` (`71.990.144` bytes) sem ROMs `.nds`.

## Limites conhecidos
- O build Windows (`dx12-gpu` e `vulkan-gpu`) foi compilado e testado localmente; os arquivos Linux/Steam Deck e Android ARM64 estão prontos para compilação em ambiente Linux/Android NDK (não há Android SDK/NDK nem toolchain Linux SDL3 compilado nesta máquina Windows).
- `saves/dos.sav` e `saves/dos-settings.ini` do usuário foram preservados sem alteração.

## Próximos passos
1. Executar `.\play.bat` para jogar diretamente em PT-BR com menu no `F1`.
2. Para importar no **RecompLauncher**, usar `recomplauncher.json` ou o pacote gerado em `dist/castlevania-dos-recomp-win64.zip`.
