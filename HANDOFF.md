# Handoff — Castlevania: Dawn of Sorrow: Recompiled (`ACVE`)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

### Current Technical State (`main` post-`v1.1.2` — Expanded Display/Graphics Suite, Sharp Scaling & True 2D Widescreen `342×192`)
- **Latest Feature (Expanded Display & Graphics Suite — `ADR-016`):**
  - Expanded `dos_postprocess.frag.hlsl` (`DosShaderParams` `80 B`, compiled to signed DXIL `ps_6_0` `16,496 B` + Vulkan 1.1 SPIR-V `33,420 B`) with live Gamma (`70..150%`), Color Temperature (`-30..+30`), 8-tap Soft Highlight Bloom (`0..50%`), Display Mask Intensity (`0..100%`), and `fwidth`-safe CRT Barrel Curvature & Bezel (`0..30%`), live-verified on RTX 3060 under both `dx12-gpu` and `vulkan-gpu`.
  - Added SDL3 multi-monitor selector (`dos_display_index`), windowed scale presets (`2x..6x`), `Ultrawide 21:9` aspect mode, overscan Safe Zone (`0..10%` with exact touch mapping), Widescreen HUD alignment (`Edge-Anchored` vs `Centered 4:3`), 3-mode VSync (`Off`/`On`/`Adaptive`), live `120 Hz` Frame Interpolation toggle, `3D MSAA` (`Off/2x/4x/8x`) persistence, and 4 one-click Visual Profiles (*Modern HD Crisp*, *Pixel Purist*, *Classic CRT*, *DS Handheld*) in `F1` + `recomplauncher.json`.
- **Previous Features (PRs #31 & #32 — Sharp Scaling + True 2D Widescreen `342×192`):**
  - Upgraded `Sharp Bilinear` (`filter_mode = 2u`, auto integer prescale + `fwidth`) and added `Bandlimited Pixel` (`filter_mode = 5u`, C2 quintic anti-shimmer + gamma-2.0 blend) in `dos_postprocess.frag.hlsl`, compiled to both signed DXIL `ps_6_0` (`14,776 B`) and Vulkan 1.1 SPIR-V (`28,840 B`) — live-verified on RTX 3060 under both `dx12-gpu` and `vulkan-gpu`.
  - Added opt-in **True 2D Widescreen `16:9` (`342×192`, Experimental)** (`dos_true_widescreen`, default `false`, live-togglable in `F1 -> Screen & Layout` and `recomplauncher.json`): 14 preflight-verified ARM9 hooks (`title_patches.cpp`) + direct `512px` BG2 wide tilemap sampling (`gpu2d.cpp`) + unsplit top-left HP/MP HUD (`center_width = 8`) + automatic `256×192` pillarbox on menus, prologues, and single-screen rooms (`g_state[0x08] == 0x02` && `width_screens >= 2`).
- **Latest Release (`v1.1.2`):** Native MSVC 2022 build for `CastlevaniaDawnOfSorrow.exe` (`443 KB`, zero MinGW `-static` stub, `RT_MANIFEST` `asInvoker`+`UTF-8`), explicit 4-file `runtime/` allowlist in `tools/package_recomplauncher.py`, pinned SHA-256 for `dsd.exe` in `tools/setup_toolchains.py`, and portable `-march=x86-64 -mtune=generic` in `CMakePresets.json`.
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
  - Widescreen 2D presentation (true ARM9 2D camera wide-viewport decompilation tracked in ADR-014 as future work).

### Verification Commands
```powershell
ctest --test-dir generated/build-runner -R "^(dos_enhancements_test|frontend_config_test|screen_layout_test)$" --output-on-failure
python -m unittest discover -s tests -v
python tools/package_recomplauncher.py --validate-only
python tools/prepare_media_assets.py --check-only
```

### Next Steps
1. Fix *Albus Mode* inverted movement bug ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
2. Complete full playthroughs for *Eternity of Sorrow 1.2*, *Model ZX*, and *Model Omega* to promote them to `verified`.
3. Evaluate native Linux / Steam Deck and Android builds with prebuilt SDL3.

---

<a id="português-br"></a>

## Português (BR)

### Estado Técnico Atual (`main` pós-`v1.1.2` — Suíte Expandida de Gráficos/Display, Sharp Scaling & Widescreen 2D Nativo `342×192`)
- **Nova fatia (Suíte Expandida de Gráficos e Display — `ADR-016`):**
  - `dos_postprocess.frag.hlsl` expandido (`DosShaderParams` `80 B`, compilado em DXIL `ps_6_0` `16.496 B` + Vulkan 1.1 SPIR-V `33.420 B`) com Gama (`70..150%`), Temperatura de Cor (`-30..+30`), Bloom Suave (`0..50%`), Intensidade da Máscara (`0..100%`) e Curvatura CRT com bezel (`0..30%`), validado ao vivo na RTX 3060 em `dx12-gpu` e `vulkan-gpu`.
  - Adicionados seletor de monitor SDL3 (`dos_display_index`), presets de escala em janela (`2x..6x`), aspecto `Ultrawide 21:9`, margem segura / overscan (`0..10%` mantendo toque exato), alinhamento de HUD widescreen (`Bordas 16:9` vs `Centralizado 4:3`), VSync 3 modos (`Desligado`/`Ligado`/`Adaptativo`), Interpolação `120 Hz` ao vivo, `3D MSAA` (`Off/2x/4x/8x`) persistente e 4 Perfis Visuais de 1 clique (*HD Moderno Nítido*, *Pixel Purista*, *CRT Clássico*, *Portátil DS*) no menu `F1` e em `recomplauncher.json`.
- **Fatias anteriores (PRs #31 e #32 — Sharp Scaling + Widescreen 2D Nativo `342×192`):**
  - Shaders GPU atualizados em `dos_postprocess.frag.hlsl` e recompilados para DXIL `ps_6_0` (`14.776 B`) e Vulkan 1.1 SPIR-V (`28.840 B`): **Sharp Bilinear** com prescale inteiro automático por eixo + **Bandlimited Pixel** (`filter_mode = 5u`, degrau quíntico C2 anti-cintilação com blend gama 2.0), validados ao vivo em `dx12-gpu` e `vulkan-gpu`.
  - Modo opt-in **Widescreen 2D Nativo `16:9` (`342×192`, Experimental)** (`dos_true_widescreen`, padrão `false`, alternável ao vivo em `F1 -> Tela & Layout` e `recomplauncher.json`): 14 ganchos ARM9 com preflight (`title_patches.cpp`) + amostragem direta de BG2 `512px` (`gpu2d.cpp`) + HUD HP/MP coeso sem corte (`center_width = 8`) + pillarbox `256×192` automático em menus, prólogo e salas de 1 tela (`g_state[0x08] == 0x02` e `width_screens >= 2`).
- **Release atual (`v1.1.2`):** `CastlevaniaDawnOfSorrow.exe` compilado nativamente com MSVC 2022 (`443 KB`, sem stub MinGW `-static`, com `RT_MANIFEST` `asInvoker`+`UTF-8`), allowlist explícita de 4 arquivos em `runtime/` (`tools/package_recomplauncher.py`), SHA-256 travado para `dsd.exe` (`tools/setup_toolchains.py`) e `-march=x86-64 -mtune=generic` em `CMakePresets.json`.
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
  - Widescreen 2D de apresentação (descompilação de câmera 2D nativa ARM9 registrada no ADR-014 como trabalho futuro).

### Próximos Passos
1. Investigar e corrigir movimento invertido no *Albus Mode* ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
2. Validar campanhas completas (*Eternity of Sorrow 1.2*, *Model ZX*, *Model Omega*) para promoção a `verified`.
3. Avaliar builds Linux / Steam Deck e Android com SDL3 pré-compilado.
