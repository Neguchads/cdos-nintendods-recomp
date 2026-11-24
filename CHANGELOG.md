# Changelog

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
