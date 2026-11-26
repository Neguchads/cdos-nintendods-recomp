# Handoff — Castlevania: Dawn of Sorrow: Recompiled (`ACVE`)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Current Technical State (Post-`v1.2.2` — Fatia 2: Modular Stackable Patch Composition & Homepage Refresh)
- **Latest Feature (Fatia 2 — Modular Stackable Add-Ons & README Refresh):**
  - Split `mods/registry.json` into stackable `"addons"` (**Tradução PT-BR v1.1**, **Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**) and exclusive `"campaigns"`.
  - Implemented 3-way byte-diff overlay merger in memory against clean USA `base_rom` + NDS header CRC-16/MODBUS recomputation (`0x15E..0x15F`) in `dos_mod_registry.cpp`, checkboxes in `F1 -> Mods & Campaigns`, `dos_active_addons` INI persistence, isolated saves per stack (`modular-stack`), and full parity in `tools/mod_resolver.py` + C++/Python tests.
  - Refreshed `README.md` homepage (EN & PT-BR) with *Key Features at a Glance* and updated Feature Status tables.
- **Previous Release (`v1.2.2` — Fatia 1 — Issues #50, #51, #44 & `cdos-traducao-ptbr#1`):**
  - Bundled `runtime/xdelta3.exe` (Xdelta 3.1.0, Apache-2.0) via `tools/build.py`, `tools/package_recomplauncher.py`, and `tools/rbs_artifact.py` so DJW/FGK/LZMA `.xdelta` patches work out of the box (Issue #50).
  - Implemented clean-room GBA Slot-2 *Aria of Sorrow* (`A2CE`) bonus (`bus_set_gba_slot2_aria_bonus` in `bus.cpp`, `dos_gba_slot2_aria` in `F1 -> Mods` & `recomplauncher.json`) unlocking **Rare Ring** + **Mina's Doll** (Issue #51).
  - Added **Mod Info & Preview Card** inside `F1 -> Mods` (Issue #44), updated PT-BR v1.1 to **Authorized** (`leomontenegro6/cdos-traducao-ptbr#1`), added 4 modular `manual_import` slots (**Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**), credited `cdos-patcher-tool`, and added Discord (`https://discord.gg/s7CWbpZJ`).
- **Previous Release (`v1.2.1`):**
- **Latest Feature (Per-Mod Quick Patch Buttons, PT-BR v1.1 & Community `manual_import` Slots, Full Credits & Outreach):**
  - Added inline **`Patch...`** (targeted `dos_mod_import_patch_file(..., target_profile_id)` installing any user-picked `.xdelta`/`.ips`/`.dospatch` straight into that mod's slot and cleaning stale extensions) and **`Official Page`** (`https://`-only `SDL_OpenURL`) buttons beside every non-builtin mod in `F1 -> Mods & Campaigns`.
  - Added clean-room `manual_import: true` slots in `mods/registry.json` (zero files bundled/downloaded; `@OerstedLAL` mods remain permanently excluded per #43) for **Tradução PT-BR v1.1 (Vanilla & Definitive Edition)**, **Definitive Edition+**, **Eternity of Sorrow** (authorized #44), **Alucard's Requiem (SOTN/CV3)**, and **Dracula's Curse**, with complete attribution in `docs/CREDITS.md` (including `leomontenegro6/cdos-traducao-ptbr` & João13 Traduções) and ready-to-send creator permission requests in `docs/CREATOR_OUTREACH.md`.
- **Previous Feature (In-Game Patch Importer, Authorized Eternity of Sorrow Slot & Minimap HUD 16:9 — PR #47):**
  - Added native SDL3 **`Import Patch (.xdelta / .ips / .dospatch)...`** and **`Open Mods Folder`** buttons in `F1 -> Mods & Campaigns` (`dos_mod_import_patch_file` validates VCDIFF/IPS/DOSPATCH magic, slugifies creator filenames, guards reserved IDs, and installs atomically into `{data}/mods/profiles/` followed by live rescan + toast).
  - Added authorized `manual_import: true` compatibility slot for **Eternity of Sorrow** (`@Wet-Band-Aid`, Issue #44, zero files bundled/downloaded, full credit in `docs/CREDITS.md`), matching user-imported `.xdelta`/`.ips`/`.dospatch` files by slug automatically.
  - Added **`NdsScreenLayout::MinimapHud`** (`minimap-hud`, compact `24%` top-right translucent map inset, `4 px` margin, `16..50%` PiP size) + **1-Click 16:9 Metroidvania HUD** preset in `F1 -> Screen & Layout`, `F2` layout cycling, and `recomplauncher.json`.
- **Previous Feature (Native `.xdelta`/`.ips` Mod Loader & `60Hz` Pitch-Preserving VSync — PR #46, Issues #30, #39):**
  - Added built-in RFC 3284 VCDIFF (`.xdelta`/`.vcdiff`, with automatic `xdelta3.exe` fallback for DJW/LZMA) and IPS (`.ips`) decoders directly in `ndsrecomp/runner/src/dos_rom_patch.cpp`, plus auto-discovery of `.dospatch`/`.xdelta`/`.vcdiff`/`.xdelta3`/`.ips` in `{data}/mods/profiles/` with isolated saves (`saves/profiles/`).
  - Added `DosVsyncMode::Sync60Hz` (`sync60`, `F1 -> HD Graphics` & `recomplauncher.json`) combining VSync + exact `60.000 Hz` pacing with `DosPitchPreservingAudioSync` (128-sample Hann WSOLA micro-splicer — 0 crackles, 0.00% pitch shift, verified over 600 simulated frames on a 440 Hz tone).
- **Previous Refactor (Generic Local Mod Support & Creator Respect — PR #45, Issues #43, #44):**
  - Removed all bundled third-party `.dospatch` files (`mods/ptbr/`, `mods/definitive/`), `mods/catalog.json`, `mods/reports/definitive-*.json`, `tools/fetch_community_mods.py`, and every third-party community mod entry from `mods/registry.json`.
  - Generalized `ndsrecomp/runner/src/dos_mod_registry.cpp` and `tools/mod_resolver.py` to auto-discover **any** user-supplied `*.dospatch` placed in `{data}/mods/profiles/` with isolated saves (`saves/profiles/<id>-v<ver>-<hash8>/dos.sav`), added offline [`tools/import_local_mod.py`](tools/import_local_mod.py) (zero network/URLs), switched default baseline to `Original USA`, moved optional user patch args in `recomplauncher.json` to `{data}/mods/...`, and hardened `tools/package_recomplauncher.py` + `tools/rbs_artifact.py` to forbid `.dospatch`/`.xdelta`/`.ips`/`.bps` in release ZIPs.
  - Merged PR #35 (`@Xarishark`: backup `{data}/saves/definitive` & `{data}/saves/profiles`, Windows-only `system`, direct RecompLauncher game page badge) and closed Issue #7 (Widescreen, delivered in `v1.2.0`).
- **Latest Graphics Feature (Modern 2D Upscalers & Multi-Pass HD-2D Pipeline — `ADR-018`):**
  - Implemented multi-pass SDL3 GPU pipeline (`DosGpuShaderState::render_multipass` in `dos_gpu_shader.{h,cpp}`, 20-slot `SDL_GPURenderState*` pool + per-screen cached `SDL_TEXTUREACCESS_TARGET` textures) driven by a single compact ubershader (`dos_postprocess.frag.hlsl` -> `uint32_t` DXIL `ps_6_0` `56,272 B` + SPIR-V `-Os` `91,884 B`, keeping `patches/ndsrecomp-local.patch` at `1.55 MiB < 2.00 MiB`).
  - Added **MMPX 2×** (NVIDIA), **OmniScale**, **ScaleFX-Hybrid 3×**, **Selective Anti-Dither (GDAPT, `dos_anti_dither`)**, **5-Pass Dual Kawase HD-2D Bloom** with CRT-aligned additive composite, and **HD-2D Remaster** / **Vector HD (ScaleFX)** one-click Visual Profiles in `F1 -> HD Graphics` & `recomplauncher.json`, verified live at `0.6..0.8 ms` GPU time on RTX 3060 under both `dx12-gpu` and `vulkan-gpu`.
- **Previous Feature (Seamless True 2D Widescreen & Curated Linear-Light Upscalers — `ADR-017`, PR #34):**
  - Fixed `1×N` (`256 px`) hardware 2D `BG2` sky/castle backdrop black cutoff at `x = 256` (`title_patches.cpp` + `gpu2d.cpp` modulo-256 wrap) and the `x = 271` vertical mist brightness seam (`native_3d_raster.cpp` + `GPU3D.cpp` untextured fullscreen atmospheric quad expansion, verified `delta = (0,0,0)` on Lost Village Bridge `0x022DD9F8` & Plaza `0x022DFCF8`).
  - Upgraded `dos_postprocess.frag.hlsl` (`DXIL ps_6_0` `20,940 B` + `Vulkan 1.1 SPIR-V` `38,284 B`, live-verified on RTX 3060 under both `dx12-gpu` and `vulkan-gpu`) with IEC 61966-2-1 linear sRGB **`Pixellate`** (new default), **`Pixel-AA`**, upgraded TheMaister **`Bandlimited Pixel`**, moiré-free analytical cosine `Scanlines`/`CRT`/`LCD`, center-aligned `Sharpen` (`Off` default), and curated 5-filter `F1 -> HD Graphics` + `game.toml` + `recomplauncher.json`.
- **Previous Feature (Expanded Display & Graphics Suite — `ADR-016`, PR #33):**
  - Expanded `dos_postprocess.frag.hlsl` (`DosShaderParams` `80 B`, compiled to signed DXIL `ps_6_0` `16,496 B` + Vulkan 1.1 SPIR-V `33,420 B`) with live Gamma (`70..150%`), Color Temperature (`-30..+30`), 8-tap Soft Highlight Bloom (`0..50%`), Display Mask Intensity (`0..100%`), and `fwidth`-safe CRT Barrel Curvature & Bezel (`0..30%`), live-verified on RTX 3060 under both `dx12-gpu` and `vulkan-gpu`.
  - Added SDL3 multi-monitor selector (`dos_display_index`), windowed scale presets (`2x..6x`), `Ultrawide 21:9` aspect mode, overscan Safe Zone (`0..10%` with exact touch mapping), Widescreen HUD alignment (`Edge-Anchored` vs `Centered 4:3`), 3-mode VSync (`Off`/`On`/`Adaptive`), live `120 Hz` Frame Interpolation toggle, `3D MSAA` (`Off/2x/4x/8x`) persistence, and 4 one-click Visual Profiles (*Modern HD Crisp*, *Pixel Purist*, *Classic CRT*, *DS Handheld*) in `F1` + `recomplauncher.json`.
- **Previous Features (PRs #31 & #32 — Sharp Scaling + True 2D Widescreen `342×192`):**
  - Upgraded `Sharp Bilinear` (`filter_mode = 2u`, auto integer prescale + `fwidth`) and added `Bandlimited Pixel` (`filter_mode = 5u`, C2 quintic anti-shimmer + gamma-2.0 blend) in `dos_postprocess.frag.hlsl`, compiled to both signed DXIL `ps_6_0` (`14,776 B`) and Vulkan 1.1 SPIR-V (`28,840 B`) — live-verified on RTX 3060 under both `dx12-gpu` and `vulkan-gpu`.
  - Added opt-in **True 2D Widescreen `16:9` (`342×192`, Experimental)** (`dos_true_widescreen`, default `false`, live-togglable in `F1 -> Screen & Layout` and `recomplauncher.json`): 14 preflight-verified ARM9 hooks (`title_patches.cpp`) + direct `512px` BG2 wide tilemap sampling (`gpu2d.cpp`) + unsplit top-left HP/MP HUD (`center_width = 8`) + automatic `256×192` pillarbox on menus, prologues, and single-screen rooms (`g_state[0x08] == 0x02` && `width_screens >= 2`).
- **Previous Release (`v1.1.2`, VirusTotal `0/65`):** Native MSVC 2022 build for `CastlevaniaDawnOfSorrow.exe` (`443 KB`, zero MinGW `-static` stub, `RT_MANIFEST` `asInvoker`+`UTF-8`), explicit 4-file `runtime/` allowlist in `tools/package_recomplauncher.py`, pinned SHA-256 for `dsd.exe` in `tools/setup_toolchains.py`, and portable `-march=x86-64 -mtune=generic` in `CMakePresets.json`.
- **Previous Patch (`v1.1.1`):** Portable `-march=x86-64 -mtune=generic` release build, embedded Windows `app.manifest` (`asInvoker`, `supportedOS`, `PerMonitorV2`, `activeCodePage=UTF-8`) in both `CastlevaniaDawnOfSorrow.exe` and `runtime/nds_runner.exe`, UTF-8 `read_file` fallback, and clearer ROM mismatch diagnostics.
- **Merged PRs into `main`:** `#22` (RBS incremental build & artifact validation), `#15` (P0/P1/P2 Definitive Edition + PT-BR + native intro player), `#17` (16A–16D campaigns, character packs, 3-state `ConflictEngine`, Native C++ Seed Mutator), and `#21` (Issues #16 Custom Music + F1 Visual Track Mapper + Global Jukebox + Explorer wizard, and #7 2D Widescreen modes).
- **Release `v1.1.0`:** standard RecompLauncher Windows x64 package (`CastlevaniaDawnOfSorrowRecomp-v1.1.0-Windows-x64.zip` + `.sha256`), validated by both `tools/package_recomplauncher.py` (`35` INI keys, `{data}` save-path guard, zero copyrighted ROM/BIOS/intro video) and `tools/rbs_artifact.py` (strict allowlist + CRC + MZ header + SHA-256).
- **Verified Features:**
  - Definitive Edition (EN & PT-BR) and Original USA (EN & PT-BR) at ~60 FPS (`0` dispatch misses, isolated saves).
  - Native Custom Music engine (`.wav`, `.mp3`, `.ogg` — zero external DLLs) with live-verified selective ARM7 BGM muting (`DS BGM = 0`, `DS SFX = 100%`), `F1 -> Audio` Visual Track Mapper, Global Jukebox / Playlist mode, and double-clickable Windows Explorer wizard (`mods/music/Configurar_Musica.bat`).
  - 2D Widescreen presentation modes (`Widescreen Theatre`, `16:9 Smart Crop` with `-24..+24 px` vertical offset, `16:10 Balanced`) with pixel-accurate touch mapping.
- **Experimental / Unverified Features (explicitly flagged in `README.md`, `CHANGELOG.md`, and `v1.1.0` release notes):**
  - *Eternity of Sorrow 1.2* (`unverified`, boot & ~60 FPS perf verified, full playthrough pending).
  - *Albus Mode* (`unverified`, known inverted movement bug tracked in [Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
  - *Model ZX* / *Model Omega* (`unverified`, boot tested, full Julius Mode playthrough pending).
  - Native C++ Seed Mutator (`unverified`, non-progression regular enemy stats/drops only; full progression randomizer remains via `tools/import_dsvrandom.py`).
  - True 2D Widescreen `16:9` (`342×192`, opt-in Beta: seamless `BG2` wrap & atmospheric quad expansion verified on Lost Village Bridge/Plaza; full-campaign room audit ongoing).

### Verification Commands
```powershell
ctest --test-dir generated/build-runner -R "^(dos_enhancements_test|frontend_config_test|screen_layout_test)$" --output-on-failure
python -m unittest discover -s tests -v
python tools/package_recomplauncher.py --validate-only
python tools/prepare_media_assets.py --check-only
```

### Next Steps
1. Optionally cut a new GitHub Release (`v1.2.3` or `v1.3.0`) packaging Fatia 2's modular stackable add-ons and updated `nds_runner.exe`.
2. Evaluate community roadmap epics: HD Texture Packs ([Issue #36](https://github.com/Neguchads/cdos-nintendods-recomp/issues/36)), Cheat Manager ([Issue #37](https://github.com/Neguchads/cdos-nintendods-recomp/issues/37)), Advanced Music Manager ([Issue #38](https://github.com/Neguchads/cdos-nintendods-recomp/issues/38)), and European multi-language support ([Issue #40](https://github.com/Neguchads/cdos-nintendods-recomp/issues/40)).
3. Full start-to-credits audit for *True 2D Widescreen `342×192`* (Beta -> Verified) and native Linux/Steam Deck / Android builds.

---

<a id="português-br"></a>

## Português (BR)

### Estado Técnico Atual (Pós-`v1.2.2` — Fatia 2: Composição Modular Empilhável de Patches & Refresh da Homepage)
- **Última fatia (Fatia 2 — Add-Ons Modulares Combináveis & Refresh do README):**
  - `mods/registry.json` separado em `"addons"` empilháveis (**Tradução PT-BR v1.1**, **Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**) e `"campaigns"` exclusivas.
  - Implementado merger 3-way byte-diff em memória sobre a `base_rom` USA limpa + recálculo do CRC-16/MODBUS do cabeçalho NDS (`0x15E..0x15F`) em `dos_mod_registry.cpp`, checkboxes em `F1 -> Mods & Campanhas`, persistência `dos_active_addons` em INI, saves isolados por combinação (`modular-stack`) e paridade completa em `tools/mod_resolver.py` + testes C++/Python.
  - `README.md` atualizado (EN e PT-BR) com *Principais Recursos em Destaque* e tabelas de status atualizadas.
- **Release anterior (`v1.2.2` — Fatia 1 — Issues #50, #51, #44 & `cdos-traducao-ptbr#1`):**
  - `runtime/xdelta3.exe` (Xdelta 3.1.0, Apache-2.0) incluído em `tools/build.py`, `tools/package_recomplauncher.py` e `tools/rbs_artifact.py` para suportar `.xdelta` DJW/FGK/LZMA direto na release (Issue #50).
  - Bônus clean-room de Slot-2 GBA *Aria of Sorrow* (`A2CE`) em `bus.cpp` (`dos_gba_slot2_aria` no `F1 -> Mods` e `recomplauncher.json`), liberando **Rare Ring** e **Mina's Doll** (Issue #51).
  - Adicionado painel de **Detalhes e Prévia do Mod** no `F1 -> Mods` (Issue #44), PT-BR v1.1 atualizado para **Autorizado** (`leomontenegro6/cdos-traducao-ptbr#1`), 4 slots modulares `manual_import` (**Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**), créditos ao `cdos-patcher-tool` e link do Discord (`https://discord.gg/s7CWbpZJ`).
- **Release anterior (`v1.2.1`):**
- **Última fatia (Botões Rápidos de Patch por Mod, Slots PT-BR v1.1 & Créditos/Permissões):**
  - Adicionados botões inline **`Aplicar Patch...`** (`dos_mod_import_patch_file(..., target_profile_id)` instalando o `.xdelta`/`.ips`/`.dospatch` direto no slot do mod escolhido e limpando extensões antigas) e **`Site Oficial`** (`SDL_OpenURL` restrito a `https://`) ao lado de cada mod no `F1 -> Mods & Campanhas`.
  - Adicionados slots clean-room `manual_import: true` em `mods/registry.json` (zero arquivos embutidos; mods de `@OerstedLAL` mantidos fora conforme #43) para **Tradução PT-BR v1.1 (Vanilla & DE)**, **Definitive Edition+**, **Eternity of Sorrow** (autorizado #44), **Alucard's Requiem (SOTN/CV3)** e **Dracula's Curse**, com créditos completos em `docs/CREDITS.md` (incluindo `leomontenegro6/cdos-traducao-ptbr` e João13 Traduções) e pedidos prontos de permissão em `docs/CREATOR_OUTREACH.md`.
- **Fatia anterior (Importador In-Game, Slot Autorizado Eternity of Sorrow & Minimap HUD 16:9 — PR #47):**
  - Adicionados botões nativos SDL3 **`Importar Patch (.xdelta / .ips / .dospatch)...`** e **`Abrir Pasta de Mods`** em `F1 -> Mods & Campanhas` (`dos_mod_import_patch_file` valida magic bytes VCDIFF/IPS/DOSPATCH, gera slug de nomes reais de criadores, bloqueia IDs reservados e instala atomicamente em `{data}/mods/profiles/` com rescan e toast ao vivo).
  - Adicionado slot autorizado `manual_import: true` de **Eternity of Sorrow** (`@Wet-Band-Aid`, Issue #44, zero arquivos embutidos/baixados, crédito completo em `docs/CREDITS.md`), casando automaticamente `.xdelta`/`.ips`/`.dospatch` importados pelo usuário.
  - Adicionado layout **`NdsScreenLayout::MinimapHud`** (`minimap-hud`, minimapa translúcido `24%` no canto superior direito com margem `4 px`, tamanho `16..50%`) + preset **1 Clique: HUD Metroidvania 16:9** em `F1 -> Tela & Layout`, atalho `F2` e `recomplauncher.json`.
- **Fatia anterior (Decodificadores `.xdelta`/`.ips` & VSync Exato 60Hz — PR #46, Issues #30, #39):**
  - Decodificadores RFC 3284 VCDIFF (com fallback `xdelta3.exe`) e IPS nativos em `dos_rom_patch.cpp`, mais `DosVsyncMode::Sync60Hz` (`sync60`) com micro-splicer WSOLA de janela Hann (`DosPitchPreservingAudioSync`, 0 crackles, 0,00% mudança de tom).
- **Fatia anterior (Suporte Genérico a Mods Locais & Respeito aos Criadores — PR #45, Issues #43, #44):**
  - Removidos todos os `.dospatch` de terceiros embutidos (`mods/ptbr/`, `mods/definitive/`), `mods/catalog.json`, `mods/reports/definitive-*.json`, `tools/fetch_community_mods.py` e todas as entradas de mods de terceiros em `mods/registry.json`.
  - Generalizada a auto-descoberta em `ndsrecomp/runner/src/dos_mod_registry.cpp` e `tools/mod_resolver.py` para carregar qualquer `*.dospatch` colocado pelo próprio jogador em `{data}/mods/profiles/` com saves isolados (`saves/profiles/<id>-v<ver>-<hash8>/dos.sav`), adicionado importador offline [`tools/import_local_mod.py`](tools/import_local_mod.py) (zero URLs/downloads), alterado padrão para `Original USA`, movidos os argumentos opcionais de patches em `recomplauncher.json` para `{data}/mods/...` e travados `tools/package_recomplauncher.py` + `tools/rbs_artifact.py` contra `.dospatch`/`.xdelta`/`.ips`/`.bps` no ZIP.
  - PR #35 (`@Xarishark`) mergeado na `main` (`43d81e1`) e Issue #7 (Widescreen) fechada como concluída na `v1.2.0`.
- **Última fatia gráfica (Escaladores 2D Modernos & Pipeline Multi-Passe HD-2D — `ADR-018`):**
  - Implementado pipeline multi-passe SDL3 GPU (`DosGpuShaderState::render_multipass` em `dos_gpu_shader.{h,cpp}`, pool de 20 `SDL_GPURenderState*` + render targets em cache por tela) via ubershader único compacto (`dos_postprocess.frag.hlsl` -> `uint32_t` DXIL `ps_6_0` `56.272 B` + SPIR-V `-Os` `91.884 B`, mantendo `patches/ndsrecomp-local.patch` em `1,55 MiB < 2,00 MiB`).
  - Adicionados **MMPX 2×** (NVIDIA), **OmniScale**, **ScaleFX-Hybrid 3×**, **Anti-Dither Seletivo (GDAPT, `dos_anti_dither`)**, **Bloom HD-2D Dual Kawase (5 passes)** com composição aditiva alinhada à curvatura CRT, e perfis **Remaster HD-2D** / **Vetor HD (ScaleFX)** no `F1 -> Gráficos HD` e `recomplauncher.json`, validados ao vivo em `0,6..0,8 ms` na RTX 3060 em `dx12-gpu` e `vulkan-gpu`.
- **Fatia anterior (Widescreen 2D Nativo Sem Cortes & Upscalers Curados — `ADR-017`, PR #34):**
  - Corrigidos o corte preto em `x = 256` de fundos `1×N` (`256 px`) em `BG2` de hardware (`title_patches.cpp` + wrap módulo 256 em `gpu2d.cpp`) e a emenda vertical de brilho da névoa em `x = 271` (expansão de quads atmosféricos 3D sem textura em `native_3d_raster.cpp` + `GPU3D.cpp`, validado com `delta = (0,0,0)` na Ponte `0x022DD9F8` e Praça `0x022DFCF8` da Lost Village).
  - Atualizado `dos_postprocess.frag.hlsl` (`DXIL ps_6_0` `20.940 B` + `Vulkan 1.1 SPIR-V` `38.284 B`, validado ao vivo na RTX 3060 em `dx12-gpu` e `vulkan-gpu`) com **`Pixellate`** (novo padrão), **`Pixel-AA`** e **`Bandlimited Pixel`** (TheMaister) em sRGB linear IEC 61966-2-1, `Scanlines`/`CRT`/`LCD` analíticos sem moiré, `Sharpen` corrigido (`Off` padrão) e dropdown curado de 5 filtros no `F1 -> Gráficos HD`, `game.toml` e `recomplauncher.json`.
- **Fatia anterior (Suíte Expandida de Gráficos e Display — `ADR-016`, PR #33):**
  - `dos_postprocess.frag.hlsl` expandido (`DosShaderParams` `80 B`, compilado em DXIL `ps_6_0` `16.496 B` + Vulkan 1.1 SPIR-V `33.420 B`) com Gama (`70..150%`), Temperatura de Cor (`-30..+30`), Bloom Suave (`0..50%`), Intensidade da Máscara (`0..100%`) e Curvatura CRT com bezel (`0..30%`), validado ao vivo na RTX 3060 em `dx12-gpu` e `vulkan-gpu`.
  - Adicionados seletor de monitor SDL3 (`dos_display_index`), presets de escala em janela (`2x..6x`), aspecto `Ultrawide 21:9`, margem segura / overscan (`0..10%` mantendo toque exato), alinhamento de HUD widescreen (`Bordas 16:9` vs `Centralizado 4:3`), VSync 3 modos (`Desligado`/`Ligado`/`Adaptativo`), Interpolação `120 Hz` ao vivo, `3D MSAA` (`Off/2x/4x/8x`) persistente e 4 Perfis Visuais de 1 clique (*HD Moderno Nítido*, *Pixel Purista*, *CRT Clássico*, *Portátil DS*) no menu `F1` e em `recomplauncher.json`.
- **Fatias anteriores (PRs #31 e #32 — Sharp Scaling + Widescreen 2D Nativo `342×192`):**
  - Shaders GPU atualizados em `dos_postprocess.frag.hlsl` e recompilados para DXIL `ps_6_0` (`14.776 B`) e Vulkan 1.1 SPIR-V (`28.840 B`): **Sharp Bilinear** com prescale inteiro automático por eixo + **Bandlimited Pixel** (`filter_mode = 5u`, degrau quíntico C2 anti-cintilação com blend gama 2.0), validados ao vivo em `dx12-gpu` e `vulkan-gpu`.
  - Modo opt-in **Widescreen 2D Nativo `16:9` (`342×192`, Experimental)** (`dos_true_widescreen`, padrão `false`, alternável ao vivo em `F1 -> Tela & Layout` e `recomplauncher.json`): 14 ganchos ARM9 com preflight (`title_patches.cpp`) + amostragem direta de BG2 `512px` (`gpu2d.cpp`) + HUD HP/MP coeso sem corte (`center_width = 8`) + pillarbox `256×192` automático em menus, prólogo e salas de 1 tela (`g_state[0x08] == 0x02` e `width_screens >= 2`).
- **Release anterior (`v1.1.2`, VirusTotal `0/65`):** `CastlevaniaDawnOfSorrow.exe` compilado nativamente com MSVC 2022 (`443 KB`, sem stub MinGW `-static`, com `RT_MANIFEST` `asInvoker`+`UTF-8`), allowlist explícita de 4 arquivos em `runtime/` (`tools/package_recomplauncher.py`), SHA-256 travado para `dsd.exe` (`tools/setup_toolchains.py`) e `-march=x86-64 -mtune=generic` em `CMakePresets.json`.
- **Patch `v1.1.1`:** Build portátil `-march=x86-64 -mtune=generic`, manifesto Windows `app.manifest` (`asInvoker`, `supportedOS`, `PerMonitorV2`, `activeCodePage=UTF-8`) embutido em `CastlevaniaDawnOfSorrow.exe` e `runtime/nds_runner.exe`, leitura UTF-8 em `main.cpp` e mensagens claras de erro de ROM.
- **PRs integrados na `main`:** `#22` (pipeline RBS e validação de artefatos), `#15` (P0/P1/P2 Definitive Edition + PT-BR + player nativo de abertura), `#17` (16A–16D campanhas, packs de personagens, `ConflictEngine` 3 estados, Seed Mutator C++ nativo) e `#21` (Issues #16 Música Customizada + Seletor Visual no F1 + Jukebox Global + assistente Explorer, e #7 modos Widescreen 2D).
- **Release `v1.1.0`:** pacote padrão RecompLauncher Windows x64 (`CastlevaniaDawnOfSorrowRecomp-v1.1.0-Windows-x64.zip` + `.sha256`), validado por `tools/package_recomplauncher.py` (`35` chaves INI, guarda `{data}` de saves, zero ROM/BIOS/vídeo protegido) e `tools/rbs_artifact.py` (allowlist estrita + CRC + header MZ + SHA-256).
- **Recursos Verificados:**
  - Definitive Edition (EN e PT-BR) e Original USA (EN e PT-BR) a ~60 FPS (`0` dispatch misses, saves isolados).
  - Motor nativo de Música Customizada (`.wav`, `.mp3`, `.ogg` — sem DLLs externas) com mute seletivo validado ao vivo (`BGM DS = 0`, `SFX DS = 100%`), Seletor Visual por Estágio no `F1 -> Áudio`, Modo Jukebox / Playlist Global e assistente duplo-clique com Windows Explorer (`mods/music/Configurar_Musica.bat`).
  - Modos Widescreen 2D (`Widescreen Teatro`, `16:9 Smart Crop` com offset vertical `-24..+24 px`, `16:10 Equilibrado`) com mapeamento de toque exato.
- **Recursos Experimentais / Não Verificados (sinalizados no `README.md`, `CHANGELOG.md` e release `v1.1.0`):**
  - *Eternity of Sorrow 1.2* (`unverified`, boot e ~60 FPS validados, campanha completa pendente).
  - *Albus Mode* (`unverified`, bug conhecido de movimento invertido na [Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
  - *Model ZX* / *Model Omega* (`unverified`, boot testado, campanha completa pendente).
  - Mutador Nativo por Seed C++ (`unverified`, apenas stats/drops fora da progressão; randomizer completo via `tools/import_dsvrandom.py`).
  - Widescreen 2D Nativo `16:9` (`342×192`, opt-in Beta: wrap de `BG2` e expansão de névoa validados na Ponte/Praça da Lost Village; auditoria completa de salas em andamento).

### Próximos Passos
1. Avaliar publicação de nova GitHub Release (`v1.2.3` ou `v1.3.0`) com a Fatia 2 (add-ons modulares empilháveis) e `nds_runner.exe` atualizado.
2. Avaliar épicos de roadmap da comunidade: Texturas HD ([Issue #36](https://github.com/Neguchads/cdos-nintendods-recomp/issues/36)), Gerenciador de Cheats ([Issue #37](https://github.com/Neguchads/cdos-nintendods-recomp/issues/37)), Gerenciador Avançado de Música ([Issue #38](https://github.com/Neguchads/cdos-nintendods-recomp/issues/38)) e multi-idioma Europeu ([Issue #40](https://github.com/Neguchads/cdos-nintendods-recomp/issues/40)).
3. Auditoria de campanha completa para *Widescreen 2D Nativo `342×192`* (Beta -> Verificado) e builds Linux/Steam Deck e Android.
