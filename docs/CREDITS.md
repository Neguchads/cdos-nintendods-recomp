# Credits & Acknowledgments / Créditos e Agradecimentos

> **Clean-Room & Creator Respect Policy / Política Clean-Room e Respeito aos Criadores:**
> This repository distributes **only** original configuration, documentation, launcher/build tooling, and generic local mod-loading infrastructure. It does **not** bundle, redistribute, or auto-download any commercial Nintendo DS ROM, proprietary BIOS, copyrighted video, or third-party fan mod/translation.
>
> Every community mod or translation listed below is strictly a **manual-import compatibility slot** (`manual_import: true` in [`mods/registry.json`](../mods/registry.json)): players download the official `.xdelta` / `.ips` patch directly from the original creators' release pages and import it locally in memory via **`F1 -> Mods & Campaigns -> Patch...`** (or generic **`Import Patch...`**) without modifying their USA `.nds` ROM.
>
> **Creator Opt-Out / Remoção imediata:** If you are the author of any project linked below and would like your credit, link, or manual-import compatibility slot updated or removed, please open an issue on this repository and we will honor your request immediately. Permission outreach tracking is documented in [`docs/CREATOR_OUTREACH.md`](CREATOR_OUTREACH.md).

---

## Community Translations & Mod Compatibility Slots (Manual Import Only) / Traduções e Slots de Compatibilidade da Comunidade (Apenas Importação Manual)

> **Zero mod or translation files are bundled in this repository or in any release ZIP.** All downloads go directly to the original creators' pages.

### Tradução Português do Brasil (PT-BR) v1.1 (`cdos-ptbr-v1-1` & `cdos-ptbr-de-v1-1`)
- **Official Repository / Repositório Oficial:** [leomontenegro6/cdos-traducao-ptbr](https://github.com/leomontenegro6/cdos-traducao-ptbr) (`v1.1`, released `2025-09-27` — `cdos_1.1.xdelta` Vanilla & `cdos_de_1.1.xdelta` Definitive Edition) & [leomontenegro6/cdos-patcher-tool](https://github.com/leomontenegro6/cdos-patcher-tool)
- **Reference & Community Showcase / Referência e Divulgação:** [João13 | Traduções & Dublagens — Castlevania: Dawn Of Sorrow v1.1](https://joao13traducoes.com/2018/02/nds-castlevania-dawn-of-sorrow-varios-autores/)
- **Translators & Contributors / Equipe de Tradução:**
  - **Hyllian** — Original PT-BR translation (2008) / Tradução original (2008)
  - **Solid One (Leonardo Montenegro / `@leomontenegro6`)** — General ROM hacking, graphics, review & testing / Romhacking geral, gráficos, revisão e testes
  - **Neko Belmont** — Review, graphics & bestiary suggestions / Revisão, gráficos e sugestões do bestiário
  - **Mysterioso** — Text review / Revisão textual
  - **denim** — Credits ROM hacking / Romhacking dos créditos
  - **djmatheusito** — `CDOS Patcher Tool` development assistance / Ajuda na criação da ferramenta `CDOS Patcher Tool`
  - **victoriemini** — Cover art / Artes de capa
- **Status:** Manual-import compatibility slot only (no files bundled; creator permission outreach prepared in [`docs/CREATOR_OUTREACH.md`](CREATOR_OUTREACH.md)).

### Castlevania: Eternity of Sorrow v1.2 (`eternity-of-sorrow`)
- **Author / Autor:** **Wet-Band-Aid** (`@Wet-Band-Aid`)
- **Official Release / Página Oficial:** [github.com/Wet-Band-Aid/Castlevania---Eternity-of-Sorrow](https://github.com/Wet-Band-Aid/Castlevania---Eternity-of-Sorrow)
- **Status:** **Authorized compatibility slot** — explicit author permission granted in [Issue #44](https://github.com/Neguchads/cdos-nintendods-recomp/issues/44) (manual import only; zero `.xdelta` / `.dospatch` / ROM files redistributed).

### Castlevania: Dawn of Sorrow — Definitive Edition & Definitive Edition+ (`definitive-plus`)
- **Authors & Contributors / Autores e Contribuidores:**
  - **Masked Dedede** — Lead developer (*Definitive Edition+*)
  - **DevAnj** — Hacking & custom ASM patches
  - **Thirteen 1355** — Original *Definitive Edition* creator
  - **ShadowOne333** & **acediez** — *Dawn of Dignity* gothic portrait overhaul
  - **LagoLunatic** — *No Required Touch Screen*, DSVEdit & ASM patches
- **Official Page / Página Oficial:** [romhacking.net/hacks/5610/](https://www.romhacking.net/hacks/5610/)
- **Status:** Manual-import compatibility slot only (no files bundled; creator permission outreach prepared in [`docs/CREATOR_OUTREACH.md`](CREATOR_OUTREACH.md)).

### Castlevania: Alucard's Requiem (`alucards-requiem-sotn` & `alucards-requiem-cv3`)
- **Authors / Autores:** **DarkPrinceAlucard**, **Drameloch** (SOTN variant), **I am Me** (CV3 variant)
- **Official Release Thread / Tópico Oficial:** [castlevaniamodding.boards.net/thread/1001/castlevania-alucards-requiem](https://castlevaniamodding.boards.net/thread/1001/castlevania-alucards-requiem)
- **Status:** Manual-import compatibility slot only (no files bundled; creator permission outreach prepared in [`docs/CREATOR_OUTREACH.md`](CREATOR_OUTREACH.md)).

### Castlevania: Dracula's Curse — Trevor Mode (`draculas-curse`)
- **Author / Autor:** **Fat T-800 (Albert Edvard)**
- **Official Page / Página Oficial:** [romhacking.net/hacks/7884/](https://www.romhacking.net/hacks/7884/)
- **Status:** Manual-import compatibility slot only (no files bundled; creator permission outreach prepared in [`docs/CREATOR_OUTREACH.md`](CREATOR_OUTREACH.md)).

---

## Recompilation Engine & Open-Source Dependencies / Motor e Dependências Open Source

- **ndsrecomp / RetroPortingToolKit** — Static AOT ARM9/ARM7 recompiler and native Nintendo DS runner architecture.
- **recomp-ui** — Runtime UI toolkit integration.
- **Dear ImGui** (Omar Cornut & contributors) — Native F1 overlay menu.
- **SDL3** (Simple DirectMedia Layer) — Cross-platform windowing, Direct3D 12 / Vulkan GPU presentation, audio, native file dialogs, keyboard/mouse/gamepad input.
- **melonDS** (Arisotura & contributors) — Hardware accuracy reference for Nintendo DS 2D/3D GPU, SPU, and cartridge I/O.
- **FreeBIOS** (BSD-2-Clause) — Open-source ARM9/ARM7 BIOS reimplementation enabling BIOS-dump-free execution.
- **ds-decomp (`dsd`)** — Nintendo DS binary analysis and overlay inspection.
- **xdelta3 (`jmacd/xdelta-gpl` v3.1.0, Apache-2.0)** by Joshua MacDonald — Optional local VCDIFF secondary-compressor decoder (`toolchains/xdelta3/xdelta3.exe`, gitignored) used for DJW/LZMA `.xdelta` patches alongside our built-in RFC 3284 VCDIFF & IPS decoders.
- **`dr_mp3` (`mackron/dr_libs`, MIT-0 / Public Domain)** by David Reid & **`stb_vorbis` (`nothings/stb`, MIT / Public Domain)** by Sean Barrett — Single-header native `.mp3` and `.ogg` (Vorbis) decoders powering `{data}/mods/music/` Custom Music replacement alongside the built-in RIFF/WAVE decoder.
- **RecompLauncher** — Standardized PC recompilation launcher manifest format (`recomplauncher.json`).

---

## Original Game / Jogo Original

- **Castlevania: Dawn of Sorrow** (2005, Nintendo DS) was developed and published by **Konami Computer Entertainment Tokyo (KCET) / Konami Digital Entertainment**.
- This project is an independent, non-commercial fan recompilation and preservation effort. You must supply your own legally obtained copy of *Castlevania: Dawn of Sorrow (USA, ACVE)*.
