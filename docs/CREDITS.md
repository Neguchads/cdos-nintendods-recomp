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

### 6. Castlevania: Eternity of Sorrow v1.2 (Campaign Overhaul / Campanha Independente)
- **Author / Autor:** **WetBandAid**
- **Source / Fonte:** [GitHub — Wet-Band-Aid/Castlevania---Eternity-of-Sorrow](https://github.com/Wet-Band-Aid/Castlevania---Eternity-of-Sorrow)
- **What it contributes / O que traz:** Full-game sequel campaign continuing after the bad ending, using the author's official No Touch Screen final build (`SHA-256: f1ebfb44ca48796a84e5e13a7600a02e7d93c3be9ec1e463c25a8ad5446b0e72`), downloaded locally via `tools/fetch_community_mods.py` and compiled into `{data}/mods/profiles/eternity-of-sorrow.dospatch`.

### 7. Albus Mode v1.0.0 (Julius Mode Character Pack)
- **Main Hack / Autor Principal:** **Oersted**
- **Additional Credits / Créditos Adicionais:** **DeadSkullzJr** (ROM image edits), **Masked Dedede** (ASM help & Albus divekick sprites), **DevAnj** (ASM help), plus playtesters *Sleepy ass Julius Belmont*, *Pixel Cherry Ninja*, *Exorion Hagen*, *NottTheSaint*.
- **Source / Fonte:** [GameBanana Mod #435925](https://gamebanana.com/mods/435925)
- **What it contributes / O que traz:** Replaces Julius Mode with Order of Ecclesia's Albus (`SHA-256: ddbc1e450a0c50e0ff5789a679ef7aeb1c67593ba88446e6f32b0c881f210d18`), compiled locally into `{data}/mods/profiles/albus-mode.dospatch` (mutually exclusive with Model ZX / Model Omega).

### 8. Playable Model ZX & Model Omega v1.0.1 (Julius Mode Character Packs)
- **Main Hack / Autor Principal:** **Oersted**
- **Additional Credits / Créditos Adicionais:** **DevAnj** (disabling Vampire Killer whip dangle code), **Masked Dedede** (Better Superjump for Julius), **LagoLunatic** (DSVania Editor).
- **Source / Fonte:** [GameBanana Mod #430348](https://gamebanana.com/mods/430348)
- **What it contributes / O que traz:** Two standalone Julius Mode character patches — **Model ZX** (`SHA-256: 5ecdb77ead563aa976bc7dd782528d68da8fb65a65061a1603288462096ba3a7`) and **Model O / Omega** (`SHA-256: 5da254844a0883e3861619077e1e8cd340bb92936e06c6d8a6f0afe2fea3baa1`) — compiled individually into `{data}/mods/profiles/model-zx.dospatch` and `model-omega.dospatch` with pre-unlocked modes.

### 9. Manual-Import Community Campaign Slots (Optional Local Import / Importação Manual Opcional)
- **Alucard's Requiem (SOTN & CV3 Variants):** **DarkPrinceAlucard**, **Drameloch** (SOTN variant), **I am Me** (CV3 variant) — [Castlevania Modding Board Thread #1001](https://castlevaniamodding.boards.net/thread/1001/castlevania-alucards-requiem).
- **Dracula's Curse (Trevor Mode):** **Fat T-800 (Albert Edvard)** — [Romhacking.net Hack #7884](https://www.romhacking.net/hacks/7884/).
- **Definitive Edition+:** **Masked Dedede** & **DevAnj** — [Romhacking.net Hack #5610](https://www.romhacking.net/hacks/5610/) (legacy XDELTA1 patches require external conversion to VCDIFF/DOSPATCH).
- **DSVania Randomizer (`dsvrandom` v1.4.8):** **LagoLunatic** — [GitHub — LagoLunatic/dsvrandom](https://github.com/LagoLunatic/dsvrandom) (user-generated local outputs imported into `{data}/mods/profiles/dsvrandom-<seed>.dospatch` via `tools/import_dsvrandom.py`).

> **Note / Nota:** None of the third-party `.xdelta`, `.zip`, `.nds`, or `.dospatch` campaign/character packs from items 6–9 are redistributed in Git; users fetch or import them locally into `{data}/mods/`.

---

## Recompilation Engine & Open-Source Dependencies / Motor e Dependências Open Source

- **ndsrecomp / RetroPortingToolKit** — Static AOT ARM9/ARM7 recompiler and native Nintendo DS runner architecture.
- **recomp-ui** — Runtime UI toolkit integration.
- **Dear ImGui** (Omar Cornut & contributors) — Native F1 overlay menu.
- **SDL3** (Simple DirectMedia Layer) — Cross-platform windowing, Direct3D 12 / Vulkan GPU presentation, audio, keyboard/mouse/gamepad input.
- **melonDS** (Arisotura & contributors) — Hardware accuracy reference for Nintendo DS 2D/3D GPU, SPU, and cartridge I/O.
- **FreeBIOS** (BSD-2-Clause) — Open-source ARM9/ARM7 BIOS reimplementation enabling BIOS-dump-free execution.
- **ds-decomp (`dsd`)** — Nintendo DS binary analysis and overlay inspection.
- **xdelta3 (`jmacd/xdelta-gpl` v3.1.0, Apache-2.0)** by Joshua MacDonald — Optional local VCDIFF secondary-compressor decoder (`toolchains/xdelta3/xdelta3.exe`, gitignored) used by `tools/fetch_community_mods.py` and `tools/import_dsvrandom.py`.
- **RecompLauncher** — Standardized PC recompilation launcher manifest format (`recomplauncher.json`).

---

## Original Game / Jogo Original

- **Castlevania: Dawn of Sorrow** (2005, Nintendo DS) was developed and published by **Konami Computer Entertainment Tokyo (KCET) / Konami Digital Entertainment**.
- This project is an independent, non-commercial fan recompilation and preservation effort. You must supply your own legally obtained copy of *Castlevania: Dawn of Sorrow (USA, ACVE)*.
