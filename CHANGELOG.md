# Changelog

## Unreleased

### Added
- **Anti-shimmer GPU scaling shaders (Direct3D 12 DXIL `ps_6_0` + Vulkan 1.1 SPIR-V):**
  - Upgraded **Sharp Bilinear** (`sharp-bilinear`) to automatic per-axis integer prescaling with `fwidth` subpixel edge blending so stretching to any aspect ratio (`16:9`, `16:10`, `21:9`, arbitrary window sizes) stays crisp without blur or uneven pixel widths.
  - Added **Bandlimited Pixel** (`bandlimited-pixel` / `filter_mode = 5u`), a C2-continuous quintic Hermite anti-shimmer filter with gamma-2.0 linear blending to eliminate scrolling shimmer and dark halos at non-integer scales.
- **Opt-in True 2D Widescreen `16:9` (`342×192`, Experimental):**
  - Live-togglable in **`F1 -> Screen & Layout`** and `recomplauncher.json` (`dos_true_widescreen`, default `false`).
  - Expands *Castlevania: Dawn of Sorrow (USA ACVE)*'s hybrid 3D-ortho BG0 + hardware 2D BG2 (`64×32` 512px tilemap) + camera centering/clamping (`0x020F7098`) to true `342×192` (`16:9`, zero sprite stretching) in multi-screen rooms (`g_state[0x08] == 0x02` and `width_screens >= 2`), while keeping the HP/MP HUD unsplit at top-left (`center_width = 8`) and automatically letterboxing to native `256×192` on title screens, prologues, pause/equip menus, and single-screen/Save rooms.

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
