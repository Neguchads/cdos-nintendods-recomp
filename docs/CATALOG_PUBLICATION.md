# RecompLauncher — developer hub publication fields

Prepared for the existing listing, not a new submission. Verified GitHub release: [v1.3.0](https://github.com/Neguchads/cdos-nintendods-recomp/releases/tag/v1.3.0). The public catalog is managed separately in the authenticated [Developer Hub](https://recomplauncher.com/dev); this file is not an SDK manifest or automatic import contract.

## Description

Experience Castlevania: Dawn of Sorrow through an independent native PC recompilation of the original Nintendo DS game. Enjoy HD-2D graphics, Direct3D 12 and Vulkan, customizable widescreen and dual-screen layouts, modern controls, modular mods, custom soundtracks and an in-game F1 settings menu. Windows x64 is the tested platform. Bring your own legally dumped USA ROM; optional translation and community patches are obtained separately.

## What's included (one per line)

- Native static ARM9/ARM7 recompilation; approximately 60 FPS in documented Windows tests
- Direct3D 12 and Vulkan rendering
- HD-2D GPU upscaling, anti-dithering, bloom and visual presets
- Widescreen Theatre, ultrawide, customizable dual-screen layouts and minimap HUD
- Experimental true 2D widescreen
- Keyboard, mouse, Xbox and PlayStation controller support
- In-game F1 settings menu
- Modular stackable IPS, XDelta and DOS patches with isolated saves
- Custom WAV, MP3 and OGG music, per-stage mapping and global jukebox
- Independent audio controls, save states and screenshots
- English and Brazilian Portuguese interface; optional authorized PT-BR v1.1 patch
- Optional GBA Slot-2 Aria of Sorrow bonus (no GBA ROM required)
- RecompLauncher Easy Setup integration

## Around the web

Leave blank until real YouTube, Reddit or X links are verified.

## What players need

Windows 10 or newer (64-bit); compatible Direct3D 12 or Vulkan 1.1 graphics device recommended. Your own legally dumped, unmodified USA Nintendo DS ROM (.nds, ACVE, 67,108,864 bytes, CRC32 135737F6, SHA-1 47530ff87e608f88105a314fdf36dc385f8dec94). No commercial BIOS or additional emulator required. Optional third-party mods and translations must be obtained separately from their authors.

## Credits

Neguchads — development and maintenance. RetroPortingToolKit — ndsrecomp and recomp-ui. SDL3, Dear ImGui, melonDS, FreeBIOS and other upstream projects. Wet-Band-Aid — Eternity of Sorrow; ShadowOne333 and acediez — Dawn of Dignity; LagoLunatic — ROM hacking tools and mods. Solid One (leomontenegro6), Hyllian, Neko Belmont, Mysterioso, denim, djmatheusito and victoriemini — authorized PT-BR v1.1 manual-import compatibility and translation/patching contributions. RecompLauncher — launcher integration. Konami — original game. Special thanks to contributors, testers, modders and players. Full credits: https://github.com/Neguchads/cdos-nintendods-recomp/blob/main/docs/CREDITS.md. Independent unofficial project; no affiliation with Konami.

## Tags (8 maximum)

Widescreen, 60 FPS, Mods, HD-2D, Custom Music, Controller Support, Save States, Native PC

## Setup steps

1. Install the recomp through RecompLauncher or add the official release ZIP.
2. In Easy Setup, select your unmodified USA Nintendo DS ROM (ACVE).
3. Allow the launcher to verify the game file and press Play.
4. Press F1 to customize graphics, controls, layouts, audio and mods.
5. Optionally import compatible community patches or custom music; no manual compilation or ROM modification is required.

## Existing listing settings

- Repository: https://github.com/Neguchads/cdos-nintendods-recomp
- Windows release file: `CastlevaniaDawnOfSorrowRecomp-*-Windows-x64.zip`
- Published release: v1.3.0 (review dynamically for future releases).
- Platform: Windows x64; do not advertise Linux or Android as released.
- Preserve the existing game ID, reports, comments, statistics and current AI-assistance disclosure.
- Refresh GitHub README/release data in the developer hub if supported; otherwise contact the platform team. Do not resubmit as a new game.

## Maintenance

The repository media generator writes `assets/recomplauncher/catalog-entry.json`. The public listing still requires an authenticated update unless RecompLauncher explicitly documents an import mechanism. Update this publication checklist and JSON when verified features or release information changes.
