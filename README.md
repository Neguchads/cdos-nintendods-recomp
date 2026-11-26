# Castlevania: Dawn of Sorrow: Recompiled

<p align="center">
  <img src="assets/recomplauncher/hero.png" alt="Castlevania: Dawn of Sorrow: Recompiled" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Neguchads/cdos-nintendods-recomp/releases/latest"><img src="https://img.shields.io/github/v/release/Neguchads/cdos-nintendods-recomp?style=for-the-badge&label=Download&color=8b2c43" alt="Download latest release"></a>
  <a href="https://recomplauncher.com/game/cdos-nintendods-recomp"><picture><source media="(prefers-color-scheme: dark)" srcset="https://recomplauncher.com/assets/press/launcher/badge-light.svg"><img src="https://recomplauncher.com/assets/press/launcher/badge-dark.svg" alt="RecompLauncher" height="28"></picture></a>
  <a href="https://discord.gg/s7CWbpZJ"><img src="https://img.shields.io/badge/Discord-Community-5865F2?style=for-the-badge" alt="Discord community"></a>
  <a href="README.pt-BR.md"><img src="assets/readme/language-ptbr.svg" alt="Read in Brazilian Portuguese" height="28"></a>
</p>

<p align="center">
  <a href="https://github.com/Neguchads/cdos-nintendods-recomp/actions/workflows/ci.yml"><img src="https://github.com/Neguchads/cdos-nintendods-recomp/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Neguchads/cdos-nintendods-recomp/actions/workflows/feature-status.yml"><img src="https://github.com/Neguchads/cdos-nintendods-recomp/actions/workflows/feature-status.yml/badge.svg" alt="Feature status validation"></a>
</p>

An independent, unofficial native PC port of **Castlevania: Dawn of Sorrow** (Nintendo DS), built with static ARM9/ARM7 recompilation using [ndsrecomp](https://github.com/RetroPortingToolKit/ndsrecomp). Play the original game with modern graphics, customizable controls, modular mods and enhanced audio.

[Features](#features) · [How to play](#how-to-play) · [Development status](#development-status) · [Future projects](#help-us-expand-the-castlevania-recompilation-ecosystem) · [Contribute](#community-contributions-welcome) · [Credits](#credits-and-acknowledgments) · [License](#license-and-legal-notice)

## Features

| Area | Highlights |
| --- | --- |
| Native execution | Static AOT ARM9/ARM7 recompilation; documented Windows performance around 60 FPS |
| Graphics | Direct3D 12 and Vulkan, HD-2D shaders, GPU upscalers, anti-dither and bloom |
| Screen layouts | Widescreen Theatre, 16:9 Smart Crop, ultrawide and minimap HUD; true 2D widescreen is beta |
| Controls | Keyboard, mouse, gamepad remapping and touch input; in-game F1 settings |
| Mods | Stackable local IPS, XDelta and DOS patches, isolated saves and manual-import community mod slots |
| Audio | Exact 60 Hz pitch-preserving sync, WAV/MP3/OGG music replacement, BGM mapper and global jukebox |
| Extras | Save states, backups, optional custom intro video, GBA Slot-2 Aria of Sorrow bonus |
| Languages | English and Brazilian Portuguese interface; authorized PT-BR translation via local patch import |
| Distribution | Standalone Windows launcher and RecompLauncher integration |

<p align="center">
  <img src="assets/screenshots/gameplay-dx12-pip.png" alt="Gameplay with Direct3D 12 and picture-in-picture layout" width="49%">
  <img src="assets/screenshots/imgui-menu-f1.png" alt="In-game F1 settings" width="49%">
</p>

[Full feature list, controls and technical guide](README.en.md) · [Custom music guide](mods/music/README.md) · [Mod credits and official sources](docs/CREDITS.md)

## How to play

**Windows x64 is the currently built and tested platform.** Linux/Steam Deck and Android are in development or unverified; see [platform status](docs/MULTIPLATFORM.md).

1. Obtain a legally dumped copy of the original USA Nintendo DS game (game code `ACVE`, 64 MiB, CRC32 `135737f6`).
2. Install using [RecompLauncher](https://recomplauncher.com/game/cdos-nintendods-recomp), or download the [latest Windows release](https://github.com/Neguchads/cdos-nintendods-recomp/releases/latest) and extract it.
3. Start the game through RecompLauncher, or run `CastlevaniaDawnOfSorrow.exe` and select your own ROM when prompted.
4. Press **F1** for settings, controls, graphics, audio and mods.

No commercial ROM or BIOS is included. Use only official release downloads. See the [complete installation guide](README.en.md#how-to-play), [RecompLauncher guide](docs/RECOMPLAUNCHER.md) and [release notes](https://github.com/Neguchads/cdos-nintendods-recomp/releases).

## Development status

<a href="docs/FEATURE_STATUS.md">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dashboard/project-status-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dashboard/project-status.svg">
  <img alt="Feature assurance dashboard" src="assets/dashboard/project-status.svg" width="880">
</picture>
</a>

<details>
<summary>View individual subsystem progress cards</summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dashboard/subsystems-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dashboard/subsystems.svg">
  <img alt="Subsystem progress" src="assets/dashboard/subsystems.svg" width="880">
</picture>

</details>

[Feature audit](docs/FEATURE_STATUS.md) · [Roadmap](ROADMAP.md) · [Quality methodology](docs/FEATURE_ASSURANCE.md) · [Progress data](quality/progress.json)

Percentages measure the registered scope and historical documented verification, not release readiness or a new full gameplay test.

## Help us expand the Castlevania recompilation ecosystem

We want to explore future independent native recompilation projects inspired by the **Dominus Collection** and **Advance Collection**, and we would love community help to make them possible.

| Dominus Collection — Nintendo DS trilogy | Advance Collection — Game Boy Advance trilogy |
| --- | --- |
| Dawn of Sorrow | Circle of the Moon |
| Portrait of Ruin | Harmony of Dissonance |
| Order of Ecclesia | Aria of Sorrow |

The aim is to research shared recompilation pipelines, rendering, audio, input, modding and cross-platform support. We also welcome research into compatibility with legally obtained collection assets where feasible. These are exploratory goals focused on the two trilogies, not announced releases, official collection ports or delivery commitments. Dawn of Sorrow remains the primary focus here.

## Community contributions welcome

**All help is welcome.** We appreciate pull requests, code reviews, bug fixes, performance improvements, testing, technical support, documentation, translations, open-source tools, research and new ideas. You do not need to be a programmer to contribute.

[Contribution guide](CONTRIBUTING.md) · [Issues](https://github.com/Neguchads/cdos-nintendods-recomp/issues) · [Pull requests](https://github.com/Neguchads/cdos-nintendods-recomp/pulls) · [Discussions](https://github.com/Neguchads/cdos-nintendods-recomp/discussions) · [Discord](https://discord.gg/s7CWbpZJ)

**Before opening an issue:** check the feature audit, roadmap, release notes, current F1 settings and open/closed issues and PRs. If a matching issue exists, add useful information there. If a feature is incomplete or broken, describe what is missing and the version tested. Genuine new ideas and regressions are welcome.

## Documentation

| Players | Developers |
| --- | --- |
| [Complete English guide](README.en.md) | [Build instructions and verification](README.en.md#clone-and-dependencies) |
| [Brazilian Portuguese guide](README.pt-BR.md) | [Architecture decisions](docs/DECISIONS.md) |
| [Custom music](mods/music/README.md) | [Incremental build and cache](docs/RBS.md) |
| [Platform compatibility](docs/MULTIPLATFORM.md) | [CI and security automation](docs/CI_AUTOMATION.md) |
| [Release history](CHANGELOG.md) | [Contribution guidelines](CONTRIBUTING.md) |

## Credits and acknowledgments

Thank you to the developers, testers, mod authors and players who help improve this project.

- [RetroPortingToolKit](https://github.com/RetroPortingToolKit) — ndsrecomp and recomp-ui; SDL3, Dear ImGui, melonDS, FreeBIOS and the other upstream projects documented in the credits.
- [Wet-Band-Aid](https://github.com/Wet-Band-Aid) — [Eternity of Sorrow](https://github.com/Wet-Band-Aid/Castlevania---Eternity-of-Sorrow), authorized compatibility slot ([#44](https://github.com/Neguchads/cdos-nintendods-recomp/issues/44)).
- [Solid One / leomontenegro6](https://github.com/leomontenegro6) and the PT-BR v1.1 translation team — Hyllian, Neko Belmont, Mysterioso, denim, djmatheusito and victoriemini; [translation](https://github.com/leomontenegro6/cdos-traducao-ptbr) and [patcher](https://github.com/leomontenegro6/cdos-patcher-tool), with authorized manual-import support ([permission](https://github.com/leomontenegro6/cdos-traducao-ptbr/issues/1)).
- All other mod creators, tool maintainers and original game developers listed in [full credits](docs/CREDITS.md).

Third-party mods and translations are not bundled; obtain them directly from their creators.

## License and legal notice

This is an independent fan recompilation and preservation project, not affiliated with or endorsed by Konami. Original games, characters, marks and proprietary assets remain the property of their respective owners.

The repository has **no blanket MIT or other project-wide license grant**. Components retain their applicable terms; the limited MIT license covers only the two original synthetic CI scripts identified in the [licensing and provenance review](docs/LICENSE_REVIEW.md). That review documents mixed upstream terms, including GPL and PolyForm Noncommercial boundaries, and distribution obligations. See [full licensing review](docs/LICENSE_REVIEW.md), [limited CI license](.github/advanced/LICENSE), and [credits and creator policy](docs/CREDITS.md). Do not distribute commercial ROMs, proprietary BIOS, or unauthorized assets. This documentation does not certify binary redistribution compliance.
