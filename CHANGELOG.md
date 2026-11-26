# Changelog

## Unreleased

### Added
- **Native `.xdelta` / `.vcdiff` & `.ips` Patch Loading in `nds_runner.exe`:** built-in RFC 3284 VCDIFF (with automatic `xdelta3.exe` fallback for DJW/FGK/LZMA secondary compressors) and IPS decoders in `dos_rom_patch.cpp`, plus automatic discovery of `.dospatch`, `.xdelta`, `.vcdiff`, `.xdelta3`, and `.ips` files dropped directly into `{data}/mods/profiles/` with isolated saves (`saves/profiles/<id>-v1.0-<hash8>/dos.sav`). Players can load any mod obtained directly from its creator without Python conversion.
- **Exact `60.0 Hz` Vertical Sync with Pitch-Preserving Audio (`sync60`, Issue #39):** added `DosVsyncMode::Sync60Hz` (`F1 -> HD Graphics -> VSync Mode -> 60Hz Exact Sync (Pitch-Preserving)` & `recomplauncher.json`), pairing VSync + exact `60.000 Hz` frame pacing with a real-time WSOLA (Waveform Similarity Overlap-Add) Hann-windowed micro-splicer so the DS's `59.8261 Hz` clock syncs stutter-free to 60 Hz LCDs without audio crackles or pitch shift.

### Changed & Removed (Creator Respect & Generic Mod Support — Issues #43, #44)
- **Removed all bundled and listed third-party mods/translations:** removed `mods/ptbr/dos-ptbr.dospatch`, `mods/definitive/dos-definitive-{en,ptbr}.dospatch`, `mods/catalog.json`, `mods/reports/definitive-*.json`, `tools/fetch_community_mods.py`, and all third-party community entries from `mods/registry.json` (`Albus Mode`, `Model ZX`, `Model Omega`, `Eternity of Sorrow`, `Alucard's Requiem`, `Dracula's Curse`, `Definitive Edition+`).
- **Generic local mod support (`F1 -> Mods & Campaigns`):** `ndsrecomp` (`dos_mod_registry.cpp`) and `tools/mod_resolver.py` now automatically discover any user-supplied `*.dospatch` placed in `{data}/mods/profiles/` with isolated saves (`saves/profiles/<id>-v<ver>-<hash8>/dos.sav`), paired with the offline local patch importer [`tools/import_local_mod.py`](tools/import_local_mod.py) (`.xdelta`/`.ips`/`.dospatch`/`.zip`, zero hardcoded URLs or network downloads).
- **Clean-room baseline default & packaging gates:** switched default content baseline to `Original USA (Retail ACVE)`, moved optional user-supplied patch arguments in `recomplauncher.json` to `{data}/mods/...`, and hardened `tools/package_recomplauncher.py` and `tools/rbs_artifact.py` to reject `.dospatch`/`.xdelta`/`.ips`/`.bps` files in release archives.
- **RecompLauncher save backups & Windows-only manifest (PR #35 by `@Xarishark`):** added `{data}/saves/definitive` and `{data}/saves/profiles` to `recomplauncher.json` `saves`, removed unshipped `system.linux`, and linked the README badge directly to `recomplauncher.com/game/cdos-nintendods-recomp`.

## 1.2.0 (2026-11-25)

### Added
- **Multi-Pass Modern 2D Upscalers & HD-2D Pipeline (ADRs 016–018 — Direct3D 12 DXIL `ps_6_0` `56,272 B` + Vulkan 1.1 SPIR-V `-Os` `91,884 B`):**
  - **8 curated 2D pixel-art & modern scalers (`<= 0.8 ms` GPU time):** IEC 61966-2-1 linear-sRGB **`Pixellate`** (exact 1.0 px analytical area box — new default), **`Pixel-AA`** (1.5 px cubic smoothstep), **`Bandlimited Pixel`** (TheMaister cosine-lobe integral), **`MMPX 2×`** (Morgan McGuire & Mara Gagiu / NVIDIA 2021 detail-preserving 2× offscreen pass), **`OmniScale`** (Lior Halphon / *SameBoy* smooth perceptual edge scaler), **`ScaleFX-Hybrid 3×`** (3× vector-curve & subtle interior reverse-AA pass), plus `Nearest` and `Bilinear` (legacy `xbr2x`/`scale2x`/`sharp-bilinear` INI keys remain backward-compatible).
  - **Selective Anti-Dither (`GDAPT`, `dos_anti_dither`):** optional pre-pass blending true 1px checkerboard and vertical-stripe dithering in linear light while leaving outlines and text untouched.
  - **5-Pass Dual Kawase HD-2D Bloom:** `1/2 -> 1/4 -> 1/8 -> 1/4 -> 1/2` bilinear pyramid + additive composite (`SDL_BLENDMODE_ADD`) aligned to CRT curvature, bezel, and vignette.
  - **Expanded Display & Graphics Suite (`F1` + `recomplauncher.json`, `49` INI defaults):** live **Monitor Selector** (multi-monitor SDL3 detection), **Windowed Scale Presets** (`Auto`, `2x..6x`), **21:9 Ultrawide Cinema**, **Display Safe Zone / Overscan Margin** (`0..10%`, preserving exact touch mapping), **Widescreen HUD Alignment** (`Edge-Anchored 16:9` vs `Centered 4:3 Safe Zone`), **3-Mode VSync** (`Off`, `On`, `Adaptive`), live **120 Hz Frame Interpolation**, persistent **3D MSAA** (`Off / 2x / 4x / 8x`), live **Gamma** (`70..150%`), **Color Temperature** (`-30..+30`), **Display Mask Intensity** (`0..100%`), **CRT Screen Curvature & Bezel** (`0..30%`), and **6 One-Click Visual Profiles** (*Modern HD Crisp*, *HD-2D Remaster (Bloom)*, *Vector HD (ScaleFX)*, *Pixel Purist*, *Classic CRT*, *DS Handheld*).
- **Opt-in True 2D Widescreen `16:9` (`342×192`, Beta, ADR-015 & ADR-017):**
  - Live-togglable in **`F1 -> Screen & Layout`** and `recomplauncher.json` (`dos_true_widescreen`, default `false`).
  - Expands *Castlevania: Dawn of Sorrow (USA ACVE)*'s hybrid 3D-ortho BG0 + hardware 2D BG2 (`64×32` 512 px tilemap) + camera centering/clamping (`0x020F7098`) to true `342×192` (`16:9`, zero sprite stretching) in multi-screen rooms (`g_state[0x08] == 0x02` and `width_screens >= 2`), keeping the HP/MP HUD unsplit (`center_width = 8`) and automatically letterboxing to native `256×192` on title screens, prologues, pause/equip menus, and single-screen/Save rooms.

### Fixed & Improved
- **Seamless True 2D Widescreen Backdrops & Mist (ADR-017):**
  - Fixed `1×N` (`256 px`) hardware 2D `BG2` parallax sky/castle backdrops cutting off to black at `x = 256` (e.g., Lost Village Bridge `0x022DD9F8` and Plaza `0x022DFCF8`) via `nds_gpu2d_set_adaptive_wide_bg_wrap_mask` modulo-256 wrapping in `gpu2d.cpp` and `wrap_x` on `1×N` 3D backdrops in `title_patches.cpp`.
  - Fixed the `x = 271` vertical mist/atmosphere brightness seam by expanding untextured axis-aligned fullscreen 3D atmospheric quads (`0..255..276 px`) to full `RenderWidth` (`342 px`) in `native_3d_raster.cpp` and melonDS `GPU3D.cpp` without mutating shared vertices (`delta(271-270) = (0, 0, 0)`).
- **Sharper Post-Processing & Decluttered `F1 -> HD Graphics` Menu (ADR-017):**
  - Replaced noisy default `xBR 2x` + `Sharpen: Subtle` with `Pixellate` + `Sharpen: Off` across `game.toml`, `recomplauncher.json`, and runtime defaults, while keeping legacy `xBR 2x`/`Scale2x` visible in the combo preview if loaded from an older `dos-settings.ini`.
  - Fixed the mid-texel split bug in GPU `Sharpen` (now samples true `±1` texel centers), upgraded `Scanlines`, `CRT Aperture`, and `NDS LCD Grid` to moiré-free analytical cosine waves aligned to texel boundaries and locked to native 192 DS lines across 2×/3× offscreen scalers, collapsed *Advanced Image Calibration*, gated *CRT Curvature* on active CRT mode, and kept PiP inset crisp (`Pixellate`).

## 1.1.2 (2026-11-24)

### Security & Release Hardening
- **Native MSVC 2022 launcher (`CastlevaniaDawnOfSorrow.exe`):** `tools/build.py` now compiles the standalone Windows launcher with Microsoft Visual Studio 2022 (`cl.exe /std:c++20 /O2 /MT` + `rc.exe`, `443 KB` vs `1.35 MB` MinGW `-static`, importing only core Windows OS DLLs) with `LLVM-MinGW` kept as fallback, eliminating the `llvm-mingw -static` PE heuristic signature (`BitDefender Gen:Variant.Lazy.751345`).
- **Explicit `runtime/` packaging allowlist:** replaced `shutil.copytree("runtime", ...)` in `tools/package_recomplauncher.py` with an explicit 4-file allowlist (`nds_runner.exe`, `SDL3.dll`, `libc++.dll`, `libunwind.dll`) so stray files in `runtime/` can never leak into a release ZIP.
- **Toolchain & preset integrity:** pinned required SHA-256 (`5917df26...`) for `dsd.exe` in `tools/setup_toolchains.py` and switched `CMakePresets.json` Windows preset from `-march=native` to portable `-march=x86-64 -mtune=generic`.

## 1.1.1 (2026-11-24)

### Fixed
- **Portable x86-64 Windows release binaries:** switched `tools/build.py` release flags from `-march=native` to portable `-march=x86-64 -mtune=generic` so `nds_runner.exe` and `CastlevaniaDawnOfSorrow.exe` run on any x64 CPU without illegal-instruction crashes (`SIGILL`).
- **Native Windows UTF-8 paths & AV manifest hardening:** embedded [`launcher/app.manifest`](launcher/app.manifest) (`requestedExecutionLevel level="asInvoker"`, Windows 10/11 `supportedOS`, `PerMonitorV2` DPI, and `<activeCodePage>UTF-8</activeCodePage>`) into both `CastlevaniaDawnOfSorrow.exe` and `runtime/nds_runner.exe`, added UTF-8 path fallback in `runner/src/main.cpp`, and stripped unused sections (`-ffunction-sections -fdata-sections -Wl,--gc-sections -fno-ident`) from `CastlevaniaDawnOfSorrow.exe` (`2.16 MB -> 1.35 MB`) to eliminate common AV false-positive heuristics (`BitDefender Gen:Variant.Lazy`).
- **Clearer ROM boot diagnostics:** `main.cpp` now logs the exact path, byte size, and expected USA dump details (`67,108,864` bytes, `ACVE`, CRC32 `135737f6`, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`) when a ROM is missing, truncated, or modified.

## 1.1.0 (2026-11-24)

### Stable / Verified
- **Definitive Edition (EN & PT-BR) built in:** semantic in-memory deltas (`dos-definitive-en.dospatch`, `dos-definitive-ptbr.dospatch`) integrating *Dawn of Dignity* portraits, *Fixed Luck*, *No Required Touch Screen*, Gergoth/Death/Abaddon 100% souls fix, Black Panther behind Throne Room, and Alucard Sword as the default baseline, with **Original USA** kept as an advanced compatibility mode in `F1 -> Mods & Campaigns`.
- **Custom Music Engine (`.wav` / `.mp3` / `.ogg`, Issue #16):** native zero-DLL decoders (built-in RIFF/WAVE + `dr_mp3.h` + `stb_vorbis.c`), automatic detection of all 30 *Dawn of Sorrow* BGM tracks (`00..29`), selective Nitro SDK 2.x PXI `MUTE_TRACK` silencing (DS BGM `0` while preserving 100% of DS SFX and `STRM` voices), in-game **`F1 -> Audio` Visual Track Mapper** (assign any audio filename to any of the 30 stages), **Global Jukebox / Playlist mode** (mute all 30 DS BGMs and play selected songs continuously with Shuffle/Prev/Next), and double-clickable Windows Explorer wizard (`mods/music/Configurar_Musica.bat`).
- **2D Widescreen Display Modes (Issue #7):** **Widescreen Theatre** (`342x192` exact 16:9 canvas with distortion-free 4:3 gameplay + docked 4:3 Map/Status sidebar), **16:9 Smart Crop** (`OVERSCAN` 1:1 square pixels + `-24..+24 px` vertical crop offset + exact touch mapping), and **16:10 Balanced**.
- **Native Opening Video Player:** optional Windows Media Foundation + SDL3 player for locally supplied `mods/intro/opening.mp4` (not bundled in clean-room releases).
- **Mod Architecture & Build Pipeline:** declarative `mods/registry.json`, 3-state `ConflictEngine` (`verified` / `unverified` / `incompatible`), isolated saves/savestates per `profile + version + modset_hash`, power-of-two cartridge padding for expanded ROMs, RecompLauncher `{data}` save-path guards, incremental RBS build/artifact verification (`Build.ps1`, `tools/rbs*.py`), and CI security/supply-chain workflows.

### Experimental / Unverified
- **Eternity of Sorrow 1.2 (Campaign):** boots and runs at ~60 FPS (`0` dispatch misses) with isolated saves; marked `unverified` pending a full playthrough from start to credits.
- **Albus Mode (Julius Mode Pack):** marked `unverified`; known inverted movement bug tracked in [Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19).
- **Model ZX / Model Omega (Julius Mode Packs):** marked `unverified`; boot-tested with isolated saves, full playthrough pending.
- **Native C++ Seed Mutator (Offline Randomizer):** mutates non-progression regular enemy stats/drops deterministically with isolated saves and spoiler log; full progression-checked item/boss randomization remains via the local **DSVania Randomizer (`dsvrandom`)** importer (`tools/import_dsvrandom.py`).
- **Widescreen Modes:** 2D presentation modes (Theatre / Smart Crop / 16:10); true ARM9 2D camera/tilemap wide-viewport decompilation remains future work (ADR-014).

## 1.0.1 (2026-11-23)

- Fix RecompLauncher startup paths, standalone launcher and mouse bindings. See [release notes](https://github.com/Neguchads/cdos-nintendods-recomp/releases/tag/v1.0.1).

## 1.0.0 (2026-11-22)

- Initial public Windows release.
