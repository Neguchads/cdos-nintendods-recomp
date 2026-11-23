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

### Latest Verifications (`feat/custom-music-widescreen` — Issues #16 & #7)
- **Custom Music Live Proof (File Select `#07 SDL_BGM_NAME_` on real Dawn of Sorrow USA ROM):**
  - All 3 formats verified live: `.wav` (built-in RIFF/WAVE), `.mp3` (`dr_mp3`), and `.ogg` (`stb_vorbis`) decoded cleanly to `32,768 Hz` stereo and triggered `[custom-music] playing track #07 Name Entry / File Select (SDL_BGM_NAME_)`.
  - **Selective Mute Mathematical Proof:** DS SPU BGM peak dropped from **`6528`** (`rms=1959.2`) without custom music to **`0`** (`rms=0.0`) with custom music, while DS menu cursor SFX still peaked at **`6304` / `2656` / `7808`** in the exact same session!
- **Widescreen Modes Live Proof (`nds_runner.exe` DX12):** `widescreen-theatre`, `smart-crop-16x9` (`crop_y=-8`), and `balanced-16x10` booted cleanly with `0` dispatch misses and exact touch-coordinate tests in `screen_layout_test`.
- `ctest`: **3/3 passed**; `unittest`: **42/42 passed**; `package_recomplauncher.py --validate-only`: **OK** (`35` INI keys); `patches/ndsrecomp-local.patch < 2 MiB`.

### Previous Verifications (PR #17 — `feat/campaigns-randomizer-v1`, 16A–16D)
- `ctest`: **3/3 passed** (`0.41s`: `frontend_config_test`, `dos_enhancements_test`, `screen_layout_test` — including `dos_mod_registry`, `dos_seed_mutator` determinism/boss-invariance/signature-rejection, and dynamic `dsvrandom-*` discovery).
- `unittest`: **39/39 passed** (`5.35s`: `prepare_rom`, `promote_banks`, `ptbr_patch`, `mod_pipeline`, `p3_p4_mods`, `recomplauncher`, `launcher`).
- `patches/ndsrecomp-local.patch`: `734.8 KiB` (`< 2 MiB`, `31` files), verified with `git apply --stat`.
- **Live DX12 E2E (all `0` dispatch misses, isolated saves):**
  - **PR #15 regression:** Original EN/PT-BR and Definitive EN/PT-BR (4/4 OK).
  - **Eternity of Sorrow 1.2 (`68.6 MB -> 128 MiB` padded):** `59.98 FPS`, `emu_ms=2.37 ms`, `present_ms=0.90 ms`, `tier3_9=20` (`72` insns), `clean_ram_rejects=0`, soft reset OK (`POST_RESET_FRAMES: 487`), isolated `profiles/eternity-of-sorrow-v1.2-59644e04/dos.sav`.
  - **Albus Mode v1.0 (`albus-mode`):** `54.37 FPS`, `emu_ms=8.08 ms`, `present_ms=0.82 ms`, `0` misses, isolated `profiles/albus-mode-v1.0-dbeb2912/dos.sav`.
  - **Model ZX v1.0.1 (`model-zx`):** clean boot, `0` misses, isolated `profiles/model-zx-v1.0.1-307a79bc/dos.sav` (`8192 B`).
  - **Model Omega v1.0.1 (`model-omega`):** `56.86 FPS`, `emu_ms=6.15 ms`, `present_ms=0.83 ms`, `0` misses, isolated `profiles/model-omega-v1.0.1-f0745f6c/dos.sav`.
  - **Native C++ Seed Mutator (`--seed CASTLE2026 --seed-preset standard`):** deterministic `modset=ec2f4db6f0ec` across repeated runs, distinct `modset=6083f5d6a8cf` for `OTHER99/hard`, `10,488 B` atomic spoiler log, bosses `101..117` untouched, and clean rejection when combined with `--campaign eternity-of-sorrow`.
- `prepare_media_assets.py --check-only`: **OK** (`8` images + `icon.ico` + `catalog-entry.json` + `3` screenshots).
- `package_recomplauncher.py --validate-only`: **OK**.

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

### Verificações Mais Recentes (`feat/custom-music-widescreen` — Issues #16 e #7)
- **Prova ao Vivo de Música Customizada (File Select `#07 SDL_BGM_NAME_` na ROM USA real):**
  - Todos os 3 formatos verificados ao vivo: `.wav` (RIFF/WAVE nativo), `.mp3` (`dr_mp3`) e `.ogg` (`stb_vorbis`) decodificados para `32.768 Hz` estéreo disparando `[custom-music] playing track #07 Name Entry / File Select (SDL_BGM_NAME_)`.
  - **Prova Matemática do Mute Seletivo:** pico SPU de BGM caiu de **`6528`** (`rms=1959,2`) sem música customizada para **`0`** (`rms=0,0`) com música customizada, enquanto SFX do cursor continuou com pico **`6304` / `2656` / `7808`** na mesma sessão!
- **Prova ao Vivo dos Modos Widescreen (`nds_runner.exe` DX12):** `widescreen-theatre`, `smart-crop-16x9` (`crop_y=-8`) e `balanced-16x10` iniciaram limpos com `0` dispatch misses e geometria/toque verificados em `screen_layout_test`.
- `ctest`: **3/3 passaram**; `unittest`: **42/42 passaram**; `package_recomplauncher.py --validate-only`: **OK** (`35` chaves INI); `patches/ndsrecomp-local.patch < 2 MiB`.

### Verificações Anteriores (PR #17 — `feat/campaigns-randomizer-v1`, 16A–16D)
- `ctest`: **3/3 passaram** (`0,41s`: `frontend_config_test`, `dos_enhancements_test`, `screen_layout_test` — incluindo `dos_mod_registry`, determinismo/invariância de chefes/rejeição de assinatura do `dos_seed_mutator` e descoberta dinâmica de `dsvrandom-*`).
- `unittest`: **39/39 passaram** (`5,35s`: `prepare_rom`, `promote_banks`, `ptbr_patch`, `mod_pipeline`, `p3_p4_mods`, `recomplauncher`, `launcher`).
- `patches/ndsrecomp-local.patch`: `734,8 KiB` (`< 2 MiB`, `31` arquivos), validado com `git apply --stat`.
- **E2E DX12 ao vivo (todos com `0` dispatch misses e saves isolados):**
  - **Regressão PR #15:** Original EN/PT-BR e Definitive EN/PT-BR (4/4 OK).
  - **Eternity of Sorrow 1.2 (`68,6 MB -> 128 MiB` padded):** `59,98 FPS`, `emu_ms=2,37 ms`, `present_ms=0,90 ms`, `tier3_9=20` (`72` insns), `clean_ram_rejects=0`, soft reset OK (`POST_RESET_FRAMES: 487`), save isolado `profiles/eternity-of-sorrow-v1.2-59644e04/dos.sav`.
  - **Albus Mode v1.0 (`albus-mode`):** `54,37 FPS`, `emu_ms=8,08 ms`, `present_ms=0,82 ms`, `0` misses, save isolado `profiles/albus-mode-v1.0-dbeb2912/dos.sav`.
  - **Model ZX v1.0.1 (`model-zx`):** boot limpo, `0` misses, save isolado `profiles/model-zx-v1.0.1-307a79bc/dos.sav` (`8192 B`).
  - **Model Omega v1.0.1 (`model-omega`):** `56,86 FPS`, `emu_ms=6,15 ms`, `present_ms=0,83 ms`, `0` misses, save isolado `profiles/model-omega-v1.0.1-f0745f6c/dos.sav`.
  - **Seed Mutator C++ Nativo (`--seed CASTLE2026 --seed-preset standard`):** `modset=ec2f4db6f0ec` determinístico entre execuções, `modset=6083f5d6a8cf` distinto para `OTHER99/hard`, spoiler log atômico de `10.488 B`, chefes `101..117` intactos e rejeição limpa quando combinado com `--campaign eternity-of-sorrow`.
- `prepare_media_assets.py --check-only`: **OK** (`8` imagens + `icon.ico` + `catalog-entry.json` + `3` capturas).
- `package_recomplauncher.py --validate-only`: **OK**.

[Voltar ao topo / Back to top](#project-notes--notas-do-projeto--castlevania-dawn-of-sorrow-recompiled)
