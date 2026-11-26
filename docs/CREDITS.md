# Credits & Acknowledgments / Créditos e Agradecimentos

> **Clean-Room & Creator Respect Policy / Política Clean-Room e Respeito aos Criadores:**
> This repository distributes **only** original configuration, documentation, launcher/build tooling, and generic local mod-loading infrastructure. It does **not** bundle, redistribute, or auto-download any commercial Nintendo DS ROM, proprietary BIOS, copyrighted video, or third-party fan mod/translation without explicit permission from the original author.
>
> Players who obtain community mods or translations directly from their original authors can load them locally in memory using our generic mod support (`python tools/import_local_mod.py` → `{data}/mods/profiles/*.dospatch`, or `{data}/mods/music/` for custom audio) without modifying their original USA `.nds` file. Any future official compatibility listing or bundled integration will only be added with **explicit creator permission** and full attribution.

---

## Recompilation Engine & Open-Source Dependencies / Motor e Dependências Open Source

- **ndsrecomp / RetroPortingToolKit** — Static AOT ARM9/ARM7 recompiler and native Nintendo DS runner architecture.
- **recomp-ui** — Runtime UI toolkit integration.
- **Dear ImGui** (Omar Cornut & contributors) — Native F1 overlay menu.
- **SDL3** (Simple DirectMedia Layer) — Cross-platform windowing, Direct3D 12 / Vulkan GPU presentation, audio, keyboard/mouse/gamepad input.
- **melonDS** (Arisotura & contributors) — Hardware accuracy reference for Nintendo DS 2D/3D GPU, SPU, and cartridge I/O.
- **FreeBIOS** (BSD-2-Clause) — Open-source ARM9/ARM7 BIOS reimplementation enabling BIOS-dump-free execution.
- **ds-decomp (`dsd`)** — Nintendo DS binary analysis and overlay inspection.
- **xdelta3 (`jmacd/xdelta-gpl` v3.1.0, Apache-2.0)** by Joshua MacDonald — Optional local VCDIFF secondary-compressor decoder (`toolchains/xdelta3/xdelta3.exe`, gitignored) used by `tools/import_local_mod.py` and `tools/import_dsvrandom.py`.
- **`dr_mp3` (`mackron/dr_libs`, MIT-0 / Public Domain)** by David Reid & **`stb_vorbis` (`nothings/stb`, MIT / Public Domain)** by Sean Barrett — Single-header native `.mp3` and `.ogg` (Vorbis) decoders powering `{data}/mods/music/` Custom Music replacement alongside the built-in RIFF/WAVE decoder.
- **RecompLauncher** — Standardized PC recompilation launcher manifest format (`recomplauncher.json`).

---

## Original Game / Jogo Original

- **Castlevania: Dawn of Sorrow** (2005, Nintendo DS) was developed and published by **Konami Computer Entertainment Tokyo (KCET) / Konami Digital Entertainment**.
- This project is an independent, non-commercial fan recompilation and preservation effort. You must supply your own legally obtained copy of *Castlevania: Dawn of Sorrow (USA, ACVE)*.
