cmake_minimum_required(VERSION 3.22.1)
project(castlevania_dos_android LANGUAGES C CXX)

# Esqueleto CMake para Android ARM64 (NDK + SDL3 + Vulkan SPIR-V).
# Aponta para ndsrecomp/runner e bancos C estaticos gerados localmente.
set(DOS_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../..")
set(NDSRECOMP_RUNNER_DIR "${DOS_ROOT}/../ndsrecomp/runner")

if(NOT EXISTS "${NDSRECOMP_RUNNER_DIR}/CMakeLists.txt")
    message(FATAL_ERROR "ndsrecomp/runner nao encontrado em ${NDSRECOMP_RUNNER_DIR}")
endif()

find_package(SDL3 CONFIG REQUIRED)

set(NDS_SDL_BACKEND "SDL3" CACHE STRING "" FORCE)
set(NDS_GENERATED_DIR "${DOS_ROOT}/generated/system" CACHE PATH "" FORCE)
set(NDS_RECOMP_UI_ROOT "${DOS_ROOT}/../recomp-ui" CACHE PATH "" FORCE)
set(NDS_BOOTSTRAP_FIRMWARE ON CACHE BOOL "" FORCE)
set(NDS_3D_GEOMETRY "NATIVE" CACHE STRING "" FORCE)
set(NDS_ENABLE_COMPUTE_RENDERER ON CACHE BOOL "" FORCE)
set(NDS_TITLE_BANK_DIRS "${DOS_ROOT}/generated/banks;${DOS_ROOT}/generated/banks-promoted" CACHE STRING "" FORCE)
set(NDS_TITLE_ROM_SHA1S "47530ff87e608f88105a314fdf36dc385f8dec94;47530ff87e608f88105a314fdf36dc385f8dec94" CACHE STRING "" FORCE)

add_subdirectory("${NDSRECOMP_RUNNER_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/ndsrecomp_runner" EXCLUDE_FROM_ALL)

# Nota: em Android NDK, SDL_main fornece a ponte SDLActivity -> libmain.so.
# Este alvo documenta a integracao JNI/SDL3 Vulkan (arm64-v8a) com o runtime recompilado.
add_library(dos_android_bridge INTERFACE)
target_link_libraries(dos_android_bridge INTERFACE SDL3::SDL3)
