# Castlevania: Dawn of Sorrow — Recompilação Estática (ACVE)

[![CI](https://github.com/Neguchads/cdos-nintendods-recomp/actions/workflows/ci.yml/badge.svg)](https://github.com/Neguchads/cdos-nintendods-recomp/actions/workflows/ci.yml)

Port nativo baseado em [`RetroPortingToolKit/ndsrecomp`](https://github.com/RetroPortingToolKit/ndsrecomp) (ARM9/ARM7 estático para C/C++, sem JIT/Dynarmic), com shaders GPU **DXIL `ps_6_0`** (Direct3D 12) e **SPIR-V** (Vulkan 1.1), menu gráfico **Dear ImGui (`F1`)** bilíngue, patch **Português (BR)** em memória e integração oficial com **RecompLauncher**.

> **Aviso legal:** Este repositório não contém ROMs proprietárias, BIOS comerciais ou binários de terceiros protegidos por direitos autorais. Forneça sua cópia legal de `Castlevania - Dawn of Sorrow (USA).nds` (64 MiB, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`) em `..\Roms\`.

## Destaques Atuais
- **Execução estática AOT a ~60 FPS (`dx12-gpu` / `vulkan-gpu`):** `34` bancos promovidos (`49.059` funções) + bancos `dos_arm9`/`dos_arm7` com `--validate-live-bytes` (validando código em RAM para compatibilidade com traduções). Medição limpa PT-BR em janela visível DX12: **`59,86 FPS`** (`emu=3,72 ms`, `pres=0,78 ms`, `readback=0,00 ms`, `underruns=0`).
- **Menu gráfico Dear ImGui v1.92.9b (`F1` / `Esc` / botão `Guide`):** estilo moderno com 6 abas (*Início*, *Tela & Layout*, *Gráficos HD*, *Áudio*, *Controles*, *Desempenho & Dev*), tradução completa **PT-BR / EN**, renderizado nativamente sobre as 2 telas reais (corrigindo o bug da 3ª tela copiada).
  - Inicialização direta no jogo (`dos_skip_launcher=true`), abrindo o menu pelo botão **`F1`**.
  - Calibração ao vivo na GPU (`Brilho`, `Contraste`, `Saturação`, `Vinheta`), tamanho do PiP (`20..50%`), `VSync`, zona morta do analógico, pausar/silenciar fora de foco, *Save States* (slots `1–5`), backup de `.sav`, gráfico Sparkline de FPS e captura `F12`.
- **Tradução Português (BR) em memória:** gerada a partir da tradução *romsportugues.com* (T1.0) via [`mods/ptbr/dos-ptbr.dospatch`](mods/ptbr/dos-ptbr.dospatch) (`DOSPATCH` com verificação SHA-1 + CRC32), permitindo alternar `EN <-> PT-BR` pelo menu `F1` sem modificar o arquivo `.nds` original.
- **RecompLauncher & Multiplataforma:** manifesto [`recomplauncher.json`](recomplauncher.json) (`format: 1`), empacotador [`tools/package_recomplauncher.py`](tools/package_recomplauncher.py), presets [`CMakePresets.json`](CMakePresets.json), build Linux/Steam Deck ([`tools/build_linux.sh`](tools/build_linux.sh)), esqueleto Android ARM64 ([`android/`](android/)) e CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)). Veja [`docs/RECOMPLAUNCHER.md`](docs/RECOMPLAUNCHER.md) e [`docs/MULTIPLATFORM.md`](docs/MULTIPLATFORM.md).

## Controles e Atalhos Padrão
| Ação (DS) | Teclado Principal (WASD) | Teclado Secundário | Controle (Xbox / PS) |
|---|---|---|---|
| Mover | `W` / `A` / `S` / `D` | Setas | Analógico Esq. / D-Pad |
| **Pular (`B`)** | **`Espaço`** | **`Espaço`** | **`A` / Cruz** |
| Atacar (`Y`) | `J` | `Z` | `X` / Quadrado |
| Esquiva (`L`) | `Shift Esq.` | `X` | `LB` / `L1` |
| Alma Guardiã (`R`) | `K` | `C` | `RB` / `R1` |
| Ação / Confirmar (`A`) | `E` | `V` | `B` / Círculo |
| Trocar Alma/Build (`X`) | `Q` | `F` | `Y` / Triângulo |
| Menu (`Start`) / Mapa (`Select`) | `Enter` / `Tab` | `Enter` / `Backspace` | `Start` / `Back` |

**Atalhos Globais:** `F1` ou botão `Guide` abre o menu ImGui | `F2` alterna o layout de tela | `F3` inverte tela principal/miniatura | `F4` liga/desliga o HUD | `F5`/`F8` salva/carrega Slot 1 | `F6`/`` ` `` alterna Turbo | `F11`/`Alt+Enter` Tela Cheia | `F12` Captura de tela (`screenshots/`).

## Clone & Dependências
```powershell
git clone https://github.com/Neguchads/cdos-nintendods-recomp.git
cd cdos-nintendods-recomp
```
Este repositório espera as pastas irmãs no mesmo diretório pai (`..`):
- `../ndsrecomp` (`RetroPortingToolKit/ndsrecomp` commit `e4a7f419`, aplicando [`patches/ndsrecomp-local.patch`](patches/ndsrecomp-local.patch) e com **Dear ImGui v1.92.9b** em `runner/third_party/imgui/`).
- `../recomp-ui` (`RetroPortingToolKit/recomp-ui` commit `f3f99a96`).
- CI automatizada no **GitHub Actions** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) e atualizações monitoradas pelo **Dependabot** ([`.github/dependabot.yml`](.github/dependabot.yml)).

## Como Montar, Rodar e Empacotar (Windows)
```powershell
python tools/setup_toolchains.py
python tools/build.py prepare
python tools/build.py banks
python tools/build.py promote
python tools/build.py ptbr-patch
python tools/build.py build
.\play.bat
```
Para gerar o pacote distribuível limpo para o **RecompLauncher** em `dist/`:
```powershell
python tools/package_recomplauncher.py
```

## Verificação
```powershell
ctest --test-dir generated/build-runner -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure
python -m unittest discover -s tests -v
python tools/build.py smoke
```
