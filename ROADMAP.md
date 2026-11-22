# Roadmap — Castlevania: Dawn of Sorrow Recomp (ACVE)

## Feito (Fatia Vertical 1 — Bring-Up)
- Inspeção e validação da ROM original (`Castlevania - Dawn of Sorrow (USA).nds`, 64 MiB, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`).
- Projeto estruturado com `game.toml`, `tools/setup_toolchains.py`, `tools/prepare_rom.py`, `tools/build.py` e `play.bat`.
- `RetroPortingToolKit/ndsrecomp` + `recomp-ui` separados em `..\ndsrecomp` e `..\recomp-ui`.

## Feito (Fase 2 — Execução Nativa 49k+ Funções, DX12 & Controles Modernos)
- Promoção estática de `34` bancos (`49.059` funções) em `generated/banks-promoted/`.
- Mapeamento simultâneo `WASD + Setas + Espaço = Pulo (B)`, mouse na tela inferior para selos mágicos e controle Xbox/PlayStation.

## Feito (Fase 3 — 60 FPS em Janela Visível DX12 GPU + DXIL `ps_6_0`)
- Shaders GPU pré-compilados em `dos_postprocess.frag.hlsl` -> `dos_gpu_shader_dxil.h`, `SoftRenderer` automático fora de `gl_top` (`0,00 ms` readback) e prebuffer de áudio calibrado (`kAudioStartFrames = 3072`).

## Feito (Fase 4 — Menu Dear ImGui, Correção 3 Telas, PT-BR, RecompLauncher & Multiplataforma)
- **Menu gráfico Dear ImGui v1.92.9b (`F1`):** 6 abas inspiradas em launcher moderno (*Início*, *Tela & Layout*, *Gráficos HD*, *Áudio*, *Controles*, *Desempenho & Dev*), tradução completa PT-BR/EN (`dos_i18n.{h,cpp}`), fontes TrueType Latin Extended (`0x0020..0x024F`), calibração GPU ao vivo (`Brilho`, `Contraste`, `Saturação`, `Vinheta`), tamanho PiP (`20..50%`), `VSync`, zona morta do analógico, pausa/mudo em segundo plano, save states `1–5`, backup `.sav`, Sparkline FPS e screenshot `F12`.
- **Correção definitiva das 3 telas:** suspensão de `SDL_SetRenderLogicalPresentation` ao desenhar ImGui e desativação do caminho legado `g_runtime_menu_surface` / `menu_texture`, mantendo apenas as 2 telas reais atrás do overlay.
- **Tradução PT-BR em memória (`--ptbr-patch`):** patch delta `mods/ptbr/dos-ptbr.dospatch` (`469.280 B`, `4.806` blocos, `romsportugues.com` T1.0) aplicado em RAM com alternância ao vivo `EN <-> PT-BR`, aliado a bancos `dos_arm9`/`dos_arm7` gerados com `--validate-live-bytes` (`59,86 FPS` no benchmark DX12).
- **Integração oficial RecompLauncher:** `recomplauncher.json` (`format: 1`, 30 chaves INI, `repo` oficial), `tools/package_recomplauncher.py` (`dist/castlevania-dos-recomp-win64.zip` sem ROMs) e `docs/RECOMPLAUNCHER.md`.
- **Multiplataforma & Shader Dual DXIL + SPIR-V:** `dos_gpu_shader_spirv.h` testado ao vivo em `vulkan-gpu` no Windows; `CMakePresets.json`, `tools/build_linux.sh`, `android/` (Gradle/NDK/SDL3) e `docs/MULTIPLATFORM.md`.
- **Repositório Público GitHub (`Neguchads/cdos-nintendods-recomp`):** `.gitignore`/`.gitattributes` clean-room, **Dependabot** (`.github/dependabot.yml` para `github-actions` e `gradle`) e **GitHub Actions** (`.github/workflows/ci.yml` multi-OS + guarda clean-room + `shellcheck`).

## Em andamento
- Nenhuma pendência estrutural aberta no port base.

## Planejado (Opcional / Futuro)
- Compilação nativa em runner Linux/Steam Deck e Android NDK no GitHub Actions ou máquina com SDK/NDK Android instalado.
- Promoção opcional de futuros blocos caso sessões em áreas muito avançadas do castelo registrem novos endereços nos manifestos de cobertura (`play-profile.bat`).
