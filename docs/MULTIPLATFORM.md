# Suporte Multiplataforma — Windows, Linux / Steam Deck e Android ARM64

Este projeto foi estruturado para compartilhar o mesmo núcleo de recompilação estática AOT (`ARM9` / `ARM7` para C/C++, sem JIT/Dynarmic) e shaders pré-compilados nos dois formatos modernos da **SDL3 GPU**:

| Plataforma | Backend Padrão | Shader Embarcado | Status de Verificação Local |
|---|---|---|---|
| **Windows 11 x64** | `dx12-gpu` (Direct3D 12) | **DXIL SM 6.0 (`ps_6_0`)** | Compilado e testado localmente (~60 FPS) |
| **Windows 11 x64 (Vulkan)** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | Compilado e testado localmente (`dos_render_driver=vulkan`) |
| **Linux x86_64 / Steam Deck** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | `CMakePresets.json`, `tools/build_linux.sh` e CI prontos (não compilado nesta máquina Windows) |
| **Android ARM64-v8a** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | Esqueleto Gradle/NDK/SDL3 pronto em [`android/`](../android/) (requer Android SDK/NDK + libs SDL3 Android para compilar APK) |

---

## 1. Windows 11 (Direct3D 12 / Vulkan)
- Compilação local via LLVM-MinGW (`toolchains/`):
  ```powershell
  python tools/build.py build
  ```
- Execução direta no jogo (menu ImGui no `F1`):
  ```powershell
  .\play.bat
  ```

## 2. Linux / SteamOS (Steam Deck)
Dependências no sistema: `cmake >= 3.24`, `ninja`, `clang` ou `gcc`, `SDL3 >= 3.2`, driver Vulkan 1.1 (Mesa RADV / NVIDIA / Intel).
```bash
./tools/build_linux.sh
./play.sh
```
No **SteamOS / Steam Deck**:
1. Adicione `./play.sh` como jogo não-Steam na Steam.
2. O controlador SteamInput / controle USB é detectado automaticamente; o botão **Guide** ou **`F1`** abre o menu ImGui (use `LB`/`RB` para trocar de aba).

## 3. Android ARM64 (`android/`)
1. Instale **Android Studio / NDK r26+** e precompile/forneça **SDL3 Android AAR/CMake** (`SDL3Config.cmake` para `arm64-v8a`).
2. Abra a pasta [`android/`](../android/) no Android Studio ou execute `./gradlew assembleRelease` com os bancos C já gerados em `generated/banks/` e `generated/banks-promoted/`.
3. Coloque a sua ROM USA original e `dos-ptbr.dospatch` na pasta externa do aplicativo (`rom/castlevania_dos_usa.nds` e `mods/ptbr/dos-ptbr.dospatch`).

---

## Portability Notes (EN)
- Both GPU shader payloads ([`dos_gpu_shader_dxil.h`](../../ndsrecomp/runner/src/dos_gpu_shader_dxil.h) and [`dos_gpu_shader_spirv.h`](../../ndsrecomp/runner/src/dos_gpu_shader_spirv.h)) are embedded C arrays — no `dxcompiler.dll` or runtime shader compiler is required on target machines.
- All `dos_*.{h,cpp}` runtime modules are strictly POSIX-portable C++20 without `<windows.h>` dependencies.
