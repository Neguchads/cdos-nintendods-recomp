# Multiplatform Support / Suporte Multiplataforma

**[English](#english) | [Português (BR)](#português-br)**

---

## English

Windows 11 x64, Linux x86_64 / Steam Deck and Android ARM64 share the same static AOT recompilation core (`ARM9` / `ARM7` to C/C++, no JIT or Dynarmic) and the same pre-compiled shaders, in the two modern **SDL3 GPU** formats.

| Platform | Default backend | Embedded shader | Verification status |
|---|---|---|---|
| **Windows 11 x64** | `dx12-gpu` (Direct3D 12) | **DXIL SM 6.0 (`ps_6_0`)** | Built and tested locally (about 60 FPS) |
| **Windows 11 x64 (Vulkan)** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | Built and tested locally (`dos_render_driver=vulkan`) |
| **Linux x86_64 / Steam Deck** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | `CMakePresets.json` and `tools/build_linux.sh` are ready; **not built here** (the CI only checks the script syntax) |
| **Android ARM64-v8a** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | Gradle / NDK / SDL3 skeleton in [`android/`](../android/); **not built** (needs the Android SDK/NDK and the SDL3 Android libraries) |

### 1. Windows 11 (Direct3D 12 / Vulkan)

- Local build with LLVM-MinGW (`toolchains/`):
  ```powershell
  python tools/build.py build
  ```
- Play (settings menu on `F1`):
  ```powershell
  .\play.bat
  ```
- Through RecompLauncher: see [`RECOMPLAUNCHER.md`](RECOMPLAUNCHER.md).

### 2. Linux / SteamOS (Steam Deck)

System dependencies: `cmake >= 3.24`, `ninja`, `clang` or `gcc`, `SDL3 >= 3.2`, a Vulkan 1.1 driver (Mesa RADV / NVIDIA / Intel).

```bash
./tools/build_linux.sh
./play.sh
```

On **SteamOS / Steam Deck**:

1. Add `./play.sh` as a non-Steam game.
2. SteamInput and USB controllers are detected automatically; **Guide** or **`F1`** opens the menu (`LB` / `RB` switch tabs).

### 3. Android ARM64 (`android/`)

1. Install **Android Studio / NDK r26+** and provide **SDL3 for Android** (AAR / CMake, `SDL3Config.cmake` for `arm64-v8a`).
2. Open [`android/`](../android/) in Android Studio, or run `./gradlew assembleRelease` with the C banks already generated in `generated/banks/` and `generated/banks-promoted/`.
3. Put your original USA ROM and `dos-ptbr.dospatch` in the app's external folder (`rom/castlevania_dos_usa.nds` and `mods/ptbr/dos-ptbr.dospatch`).

### Portability notes

- Both shader payloads ([`dos_gpu_shader_dxil.h`](../../ndsrecomp/runner/src/dos_gpu_shader_dxil.h) and [`dos_gpu_shader_spirv.h`](../../ndsrecomp/runner/src/dos_gpu_shader_spirv.h)) are embedded C arrays: no `dxcompiler.dll` and no runtime shader compiler on the target machine.
- The `dos_*.{h,cpp}` runtime modules are POSIX-portable C++20 and do not include `<windows.h>`.

[Voltar ao topo / Back to top](#multiplatform-support--suporte-multiplataforma)

---

## Português (BR)

Windows 11 x64, Linux x86_64 / Steam Deck e Android ARM64 compartilham o mesmo núcleo de recompilação estática AOT (`ARM9` / `ARM7` para C/C++, sem JIT nem Dynarmic) e os mesmos shaders pré-compilados, nos dois formatos modernos da **SDL3 GPU**.

| Plataforma | Backend padrão | Shader embarcado | Status de verificação |
|---|---|---|---|
| **Windows 11 x64** | `dx12-gpu` (Direct3D 12) | **DXIL SM 6.0 (`ps_6_0`)** | Compilado e testado localmente (cerca de 60 FPS) |
| **Windows 11 x64 (Vulkan)** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | Compilado e testado localmente (`dos_render_driver=vulkan`) |
| **Linux x86_64 / Steam Deck** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | `CMakePresets.json` e `tools/build_linux.sh` prontos; **não compilado aqui** (a CI só confere a sintaxe do script) |
| **Android ARM64-v8a** | `vulkan-gpu` | **SPIR-V Vulkan 1.1** | Esqueleto Gradle / NDK / SDL3 em [`android/`](../android/); **não compilado** (precisa do Android SDK/NDK e das libs SDL3 Android) |

### 1. Windows 11 (Direct3D 12 / Vulkan)

- Compilação local com LLVM-MinGW (`toolchains/`):
  ```powershell
  python tools/build.py build
  ```
- Jogar (menu de opções no `F1`):
  ```powershell
  .\play.bat
  ```
- Pelo RecompLauncher: veja [`RECOMPLAUNCHER.md`](RECOMPLAUNCHER.md).

### 2. Linux / SteamOS (Steam Deck)

Dependências do sistema: `cmake >= 3.24`, `ninja`, `clang` ou `gcc`, `SDL3 >= 3.2`, driver Vulkan 1.1 (Mesa RADV / NVIDIA / Intel).

```bash
./tools/build_linux.sh
./play.sh
```

No **SteamOS / Steam Deck**:

1. Adicione `./play.sh` como jogo fora da Steam.
2. O SteamInput e controles USB são detectados automaticamente; **Guide** ou **`F1`** abre o menu (`LB` / `RB` trocam de aba).

### 3. Android ARM64 (`android/`)

1. Instale o **Android Studio / NDK r26+** e forneça o **SDL3 para Android** (AAR / CMake, `SDL3Config.cmake` para `arm64-v8a`).
2. Abra [`android/`](../android/) no Android Studio ou rode `./gradlew assembleRelease` com os bancos C já gerados em `generated/banks/` e `generated/banks-promoted/`.
3. Coloque a sua ROM USA original e o `dos-ptbr.dospatch` na pasta externa do app (`rom/castlevania_dos_usa.nds` e `mods/ptbr/dos-ptbr.dospatch`).

### Notas de portabilidade

- Os dois payloads de shader ([`dos_gpu_shader_dxil.h`](../../ndsrecomp/runner/src/dos_gpu_shader_dxil.h) e [`dos_gpu_shader_spirv.h`](../../ndsrecomp/runner/src/dos_gpu_shader_spirv.h)) são arrays C embarcados: sem `dxcompiler.dll` e sem compilador de shader em tempo de execução na máquina de destino.
- Os módulos `dos_*.{h,cpp}` do runtime são C++20 portável POSIX e não incluem `<windows.h>`.

[Voltar ao topo / Back to top](#multiplatform-support--suporte-multiplataforma)
