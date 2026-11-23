# Credits & Acknowledgments / Créditos e Agradecimentos

> **Important / Importante:** This repository distributes **only** binary delta patches (`DOSPATCH`), configuration, documentation, and original tooling. It does **not** redistribute any commercial Nintendo DS ROM, proprietary BIOS, or copyrighted video files. Every community mod integrated in the `development` / Definitive pipeline belongs to its respective authors credited below.

---

## Community Mods & Patches / Mods e Patches da Comunidade

### 1. Castlevania: Dawn of Sorrow — Definitive Edition
- **Original Author / Autor Original:** **Thirteen 1355**
- **Community Expansion & ASM Fixes / Expansão e Correções ASM:** **Masked Dedede** and **DevAnj** (*Definitive+*)
- **What it contributes / O que traz:**
  - Combines *Dawn of Dignity*, *Fixed Luck*, and *No Required Touch Screen* into a unified baseline.
  - Fixes 100% soul-drop edge cases for Gergoth, Death, and Abaddon.
  - Places Black Panther soul access behind the Throne Room and makes the Alucard Sword obtainable in-game.
- **Integration / Integração:** Composed non-destructively in RAM via `mods/definitive/dos-definitive-en.dospatch` and semantically merged with PT-BR in `mods/definitive/dos-definitive-ptbr.dospatch` without modifying the user's original USA `.nds` dump (`tools/compose_dos_mods.py`).

### 2. Dawn of Dignity (Gothic Portraits / Retratos Estilo Ayami Kojima)
- **Lead & ROM Insertion / Liderança e Inserção:** **ShadowOne333**
- **Original Portraits / Retratos Originais:** **acediez**
- **Additional Art & Polish / Arte Adicional e Polimento:** **JohannGralog**, **Justin3009**, **DarkSamus993**
- **Artistic Inspiration / Inspiração Artística:** Based on the classic gothic illustrations of **Ayami Kojima**.
- **What it contributes / O que traz:** Replaces anime-style character portraits with gothic portraits faithful to the classic *Castlevania* aesthetic (42 portrait files).

### 3. No Required Touch Screen v1.1 & Fixed Luck
- **Author / Autor:** **LagoLunatic**
- **Project / Ferramentas:** [DSVEdit](https://github.com/LagoLunatic/DSVEdit)
- **What it contributes / O que traz:**
  - *No Required Touch Screen v1.1*: Removes mandatory stylus magic seals on bosses, ice-block breaking touch dependency, and name-entry touch lock.
  - *Fixed Luck*: Fixes the original game's broken Luck stat formula so Luck meaningfully improves soul and item drop rates.

### 4. Castlevania Dominus AI Intro Video (Enhanced Opening / Abertura Aprimorada)
- **Author / Autor:** **Joedu22256**
- **Source / Fonte:** [Nexus Mods — Castlevania Dominus Collection Mod #12](https://www.nexusmods.com/castlevaniadominuscollection/mods/12)
- **What it contributes / O que traz:** AI-upscaled opening video (`CVNDS_OPmovie_DoS.webm`, MP4 H.264 640x480 @ 30fps + AAC, 58.8s), imported locally via `tools/import_mod_bundle.py` into `mods/intro/opening.mp4` and decoded natively inside `nds_runner.exe` using Windows Media Foundation + SDL3.
- **Distribution Note / Nota de Distribuição:** The video binary (`11.5 MB`) is intentionally **not** committed to Git; players import it locally with `python tools/import_mod_bundle.py "<bundle-dir>"`.

### 5. Portuguese (Brazil) Translation T1.0 / Tradução PT-BR T1.0
- **Author / Equipe:** **romsportugues.com** fan translation team
- **What it contributes / O que traz:** Complete Brazilian Portuguese translation of dialogue, menus, item/soul descriptions, accented fonts, ARM9 accent hooks, and credits (`mods/ptbr/dos-ptbr.dospatch` and merged into `mods/definitive/dos-definitive-ptbr.dospatch`).

---

## Recompilation Engine & Open-Source Dependencies / Motor e Dependências Open Source

- **ndsrecomp / RetroPortingToolKit** — Static AOT ARM9/ARM7 recompiler and native Nintendo DS runner architecture.
- **recomp-ui** — Runtime UI toolkit integration.
- **Dear ImGui** (Omar Cornut & contributors) — Native F1 overlay menu.
- **SDL3** (Simple DirectMedia Layer) — Cross-platform windowing, Direct3D 12 / Vulkan GPU presentation, audio, keyboard/mouse/gamepad input.
- **melonDS** (Arisotura & contributors) — Hardware accuracy reference for Nintendo DS 2D/3D GPU, SPU, and cartridge I/O.
- **FreeBIOS** (BSD-2-Clause) — Open-source ARM9/ARM7 BIOS reimplementation enabling BIOS-dump-free execution.
- **ds-decomp (`dsd`)** — Nintendo DS binary analysis and overlay inspection.
- **RecompLauncher** — Standardized PC recompilation launcher manifest format (`recomplauncher.json`).

---

## Original Game / Jogo Original

- **Castlevania: Dawn of Sorrow** (2005, Nintendo DS) was developed and published by **Konami Computer Entertainment Tokyo (KCET) / Konami Digital Entertainment**.
- This project is an independent, non-commercial fan recompilation and preservation effort. You must supply your own legally obtained copy of *Castlevania: Dawn of Sorrow (USA, ACVE)*.
