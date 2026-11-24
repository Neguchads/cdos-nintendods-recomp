# Project Notes / Notas do Projeto — Castlevania: Dawn of Sorrow: Recompiled

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Verified ROM Metadata
- **Base ROM (USA):** `..\Roms\Castlevania - Dawn of Sorrow (USA).nds` — `67,108,864` bytes, CRC32 `135737f6`, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`, unmodified.
- **PT-BR Reference ROM (patch source):** `..\Roms\Castlevania - Dawn of Sorrow (BR-USA) (DE) (T1.0) (www.romsportugues.com).nds` — `67,108,864` bytes, SHA-1 `c9a1552bcdcd8fdf3c052d975e6838da7ead08d1`.
- **Measured structural differences between USA and PT-BR (`364,911` bytes total):** `7 B` header, `0 B` ARM7, `120 B` in ARM9 (`0x02008578..0x020c02f4`, accent glyph hooks), `3` overlays (`ov000`, `ov004`, `ov005`), and `88` NitroFS files (fonts/strings).
- **Generated delta patches:**
  - `mods/ptbr/dos-ptbr.dospatch` (`469,280` bytes, `4,806` chunks, Original PT-BR).
  - `mods/definitive/dos-definitive-en.dospatch` (`615,288` bytes, `dst_sha1=2333f02b22dc141f06a2d9d00824b0d3c33dc309`).
  - `mods/definitive/dos-definitive-ptbr.dospatch` (`752,796` bytes, `dst_sha1=6ffc88b8023a5dbeab0f58a8adc344fe7e158f17`, header CRC16 `0xb373`).
  - Local enhanced opening video (gitignored): `mods/intro/opening.mp4` (`11,501,616` bytes, real MP4 H.264 640x480 30fps + AAC, imported from `CVNDS_OPmovie_DoS.webm`).

### 3-Screens Bug Fix & Dear ImGui Overlay Reconstruction
- **Previous root cause:** `present_screens` rendered the 2 DS screens (`SideBySide` / `Stacked`) and then drew `menu_texture` (`512x384` containing an opaque copy of `raw_sources[hud_screen]`) centered over the canvas, producing a visible 3rd copy of the screen.
- **Applied solution:** `DosImGuiMenu` (Dear ImGui v1.92.9b) renders directly over the 2 real DS screens by temporarily suspending `SDL_SetRenderLogicalPresentation` for native 1080p+ sharpness and bypassing `menu_texture` / `g_runtime_menu_surface`.

### RecompLauncher 1.0 SDK & Media Kit (`assets/recomplauncher/`)
- **`recomplauncher.json`:** upgraded to the RecompLauncher 1.0 SDK format (`inputs[game]` with `.nds`, `check.ids = ["ACVE"]`, `dumps` CRC32 `135737f6` & size `67108864`, `config[0].new` defaults, `looks`, `actions`, `system`, `exit_codes`, and no window-opening `prepare` step). `start.args` uses `{install}/game.toml`, `{install}/mods/ptbr/dos-ptbr.dospatch`, and `{data}/run/bios` because RecompLauncher runs `runtime/nds_runner.exe` with `cwd = {install}/runtime`.
- **Media kit (`tools/prepare_media_assets.py`):** `icon.png` (`256x256`) + `icon.ico` (`256, 64, 48, 32, 16`), `cover.png`/`cover.jpg` (`600x900`), `hero.png`/`hero.jpg` (`1920x620`), transparent `logo.png` (`1000x500` RGBA), `wallpaper.png` (`1920x1080`), `artwork.png` (`1024x1024`), `catalog-entry.json` (`media_design.kind = "ds"`), plus 3 in-engine captures (`1920x1080`) in `assets/screenshots/`.

### Latest Verifications
- `ctest`: **3/3 passed** (`frontend_config_test`, `dos_enhancements_test`, `screen_layout_test`, including `dos_mod_profile` & `dos_intro_validate_mp4_file`).
- `unittest`: **34/34 passed** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `mod_pipeline`, `recomplauncher`, `launcher`).
- `prepare_media_assets.py --check-only`: **OK** (`8` images + `icon.ico` + `catalog-entry.json` + `3` screenshots).
- `package_recomplauncher.py --validate-only`: **OK** (`30` INI keys + `inputs[game]` + media kit).
- `build.py smoke`: **PASS** (`724` vblanks, `report.json`).
- **DX12 GPU PT-BR (`420` clean frames):** **`59.86 FPS`** (`emu=3.72 ms`, `pres=0.78 ms`, `rb=0.000 ms`, `underruns=0`).
- **Vulkan GPU SPIR-V PT-BR (`1920x1080`):** active in hardware (`vulkan-gpu`, `SPIR-V Vulkan`), `60.0 FPS`, `PRES:0.3MS`.

[Back to top / Voltar ao topo](#project-notes--notas-do-projeto--castlevania-dawn-of-sorrow-recompiled)

---

<a id="português-br"></a>

## Português (BR)

### Metadados das ROMs Verificados
- **ROM Base (USA):** `..\Roms\Castlevania - Dawn of Sorrow (USA).nds` — `67.108.864` bytes, CRC32 `135737f6`, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`, intacta.
- **ROM PT-BR de origem do patch:** `..\Roms\Castlevania - Dawn of Sorrow (BR-USA) (DE) (T1.0) (www.romsportugues.com).nds` — `67.108.864` bytes, SHA-1 `c9a1552bcdcd8fdf3c052d975e6838da7ead08d1`.
- **Diferenças estruturais medidas entre USA e PT-BR (`364.911` bytes no total):** `7 B` cabeçalho, `0 B` ARM7, `120 B` em ARM9 (`0x02008578..0x020c02f4`, hooks de acentuação), `3` overlays (`ov000`, `ov004`, `ov005`), e `88` arquivos NitroFS (fontes/textos).
- **Patches delta gerados:**
  - `mods/ptbr/dos-ptbr.dospatch` (`469.280` bytes, `4.806` blocos, PT-BR Original).
  - `mods/definitive/dos-definitive-en.dospatch` (`615.288` bytes, `dst_sha1=2333f02b22dc141f06a2d9d00824b0d3c33dc309`).
  - `mods/definitive/dos-definitive-ptbr.dospatch` (`752.796` bytes, `dst_sha1=6ffc88b8023a5dbeab0f58a8adc344fe7e158f17`, CRC16 `0xb373`).
  - Vídeo de abertura local (ignorado no git): `mods/intro/opening.mp4` (`11.501.616` bytes, MP4 H.264 640x480 30fps + AAC, importado de `CVNDS_OPmovie_DoS.webm`).

### Bug das 3 Telas e Reconstrução com Dear ImGui
- **Causa raiz anterior:** `present_screens` renderizava as 2 telas DS (`SideBySide` / `Stacked`) e depois desenhava `menu_texture` (`512x384` contendo cópia opaca de `raw_sources[hud_screen]`) por cima do centro do canvas, fazendo aparecer uma 3ª cópia da tela.
- **Solução aplicada:** `DosImGuiMenu` (Dear ImGui v1.92.9b) desenha diretamente sobre as 2 telas reais suspendendo temporariamente `SDL_SetRenderLogicalPresentation` para manter nitidez nativa (1080p+) e ignorando `menu_texture` / `g_runtime_menu_surface`.

### SDK 1.0 do RecompLauncher & Kit de Mídia (`assets/recomplauncher/`)
- **`recomplauncher.json`:** atualizado para o formato do SDK 1.0 do RecompLauncher (`inputs[game]` com `.nds`, `check.ids = ["ACVE"]`, `dumps` CRC32 `135737f6` e tamanho `67108864`, padrões em `config[0].new`, `looks`, `actions`, `system`, `exit_codes` e sem etapa `prepare` com janela). `start.args` usa `{install}/game.toml`, `{install}/mods/ptbr/dos-ptbr.dospatch` e `{data}/run/bios` porque o RecompLauncher executa `runtime/nds_runner.exe` com `cwd = {install}/runtime`.
- **Kit de mídia (`tools/prepare_media_assets.py`):** `icon.png` (`256x256`) + `icon.ico` (`256, 64, 48, 32, 16`), `cover.png`/`cover.jpg` (`600x900`), `hero.png`/`hero.jpg` (`1920x620`), `logo.png` transparente (`1000x500` RGBA), `wallpaper.png` (`1920x1080`), `artwork.png` (`1024x1024`), `catalog-entry.json` (`media_design.kind = "ds"`), mais 3 capturas reais do motor (`1920x1080`) em `assets/screenshots/`.

### Verificações Mais Recentes
- `ctest`: **3/3 passaram** (`frontend_config_test`, `dos_enhancements_test`, `screen_layout_test`, incluindo `dos_mod_profile` e `dos_intro_validate_mp4_file`).
- `unittest`: **34/34 passaram** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `mod_pipeline`, `recomplauncher`, `launcher`).
- `prepare_media_assets.py --check-only`: **OK** (`8` imagens + `icon.ico` + `catalog-entry.json` + `3` capturas).
- `package_recomplauncher.py --validate-only`: **OK** (`30` chaves INI + `inputs[game]` + kit de mídia).
- `build.py smoke`: **PASS** (`724` vblanks, `report.json`).
- **DX12 GPU PT-BR (`420` frames limpos):** **`59,86 FPS`** (`emu=3,72 ms`, `pres=0,78 ms`, `rb=0,000 ms`, `underruns=0`).
- **Vulkan GPU SPIR-V PT-BR (`1920x1080`):** ativo em hardware (`vulkan-gpu`, `SPIR-V Vulkan`), `60,0 FPS`, `PRES:0,3MS`.

[Voltar ao topo / Back to top](#project-notes--notas-do-projeto--castlevania-dawn-of-sorrow-recompiled)
