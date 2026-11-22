#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORK_DIR="${NDSRECOMP_DIR:-$(cd "$ROOT/.." && pwd)/ndsrecomp}"
RECOMP_UI_DIR="${RECOMP_UI_DIR:-$(cd "$ROOT/.." && pwd)/recomp-ui}"
BUILD_DIR="${ROOT}/generated/build-linux"
SYSTEM_DIR="${ROOT}/generated/system"
BANKS_DIR="${ROOT}/generated/banks"
PROMOTED_DIR="${ROOT}/generated/banks-promoted"
RUNTIME_DIR="${ROOT}/runtime"
JOBS="${JOBS:-$(nproc)}"

if [[ ! -f "${FRAMEWORK_DIR}/runner/CMakeLists.txt" ]]; then
  echo "[erro] ndsrecomp/runner nao encontrado em ${FRAMEWORK_DIR}" >&2
  exit 1
fi
if [[ ! -f "${BANKS_DIR}/dos_arm9_dispatch.c" ]]; then
  echo "[erro] bancos C nao gerados em ${BANKS_DIR}. Execute prepare/banks antes." >&2
  exit 1
fi

CC_BIN="${CC:-$(command -v clang || command -v gcc)}"
CXX_BIN="${CXX:-$(command -v clang++ || command -v g++)}"

cmake -S "${FRAMEWORK_DIR}/runner" -B "${BUILD_DIR}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="${CC_BIN}" \
  -DCMAKE_CXX_COMPILER="${CXX_BIN}" \
  -DNDSRECOMP_COMPILER_CACHE=OFF \
  -DNDS_SDL_BACKEND=SDL3 \
  -DNDS_GENERATED_DIR="${SYSTEM_DIR}" \
  -DNDS_RECOMP_UI_ROOT="${RECOMP_UI_DIR}" \
  -DNDS_BOOTSTRAP_FIRMWARE=ON \
  -DNDS_LEAN_DIAGNOSTICS=ON \
  -DNDS_GX_COMMAND_CACHE=ON \
  -DNDS_CAPTURE_VIEW_REUSE=ON \
  -DNDS_3D_GEOMETRY=NATIVE \
  -DNDS_ENABLE_COMPUTE_RENDERER=ON \
  -DCMAKE_C_FLAGS_RELEASE="-O2 -DNDEBUG" \
  -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG" \
  -DNDS_TITLE_BANK_DIRS="${BANKS_DIR};${PROMOTED_DIR}" \
  -DNDS_TITLE_ROM_SHA1S="47530ff87e608f88105a314fdf36dc385f8dec94;47530ff87e608f88105a314fdf36dc385f8dec94"

cmake --build "${BUILD_DIR}" --target nds_runner dos_enhancements_test frontend_config_test screen_layout_test --parallel "${JOBS}"

ctest --test-dir "${BUILD_DIR}" -R "screen_layout_test|frontend_config_test|dos_enhancements_test" --output-on-failure

mkdir -p "${RUNTIME_DIR}" "${ROOT}/run/bios" "${ROOT}/run/savestates" "${ROOT}/saves"
cp "${BUILD_DIR}/nds_runner" "${RUNTIME_DIR}/nds_runner"
chmod +x "${RUNTIME_DIR}/nds_runner"

cat > "${ROOT}/play.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PTBR_ARGS=()
if [[ -f "${ROOT}/mods/ptbr/dos-ptbr.dospatch" ]]; then
  PTBR_ARGS=(--ptbr-patch "${ROOT}/mods/ptbr/dos-ptbr.dospatch")
fi
export NDS_HOSTPROF=off
cd "${ROOT}/runtime"
exec "./nds_runner" "${ROOT}/run/bios" \
  --interactive \
  --rom "${ROOT}/../Roms/Castlevania - Dawn of Sorrow (USA).nds" \
  "${PTBR_ARGS[@]}" \
  --config "${ROOT}/game.toml" \
  --freebios \
  --generated-firmware \
  --boot direct \
  --startup-mode automatic \
  --diagnostics off \
  --no-coverage-manifest \
  --runtime-settings-path "${ROOT}/saves/dos-settings.ini" \
  --savestate-dir "${ROOT}/run/savestates" \
  --save-path "${ROOT}/saves/dos.sav" \
  --firmware-state-path "${ROOT}/run/firmware_state.bin"
EOF
chmod +x "${ROOT}/play.sh"
echo "[linux] OK: ${RUNTIME_DIR}/nds_runner e ${ROOT}/play.sh prontos (Vulkan SPIR-V)."
