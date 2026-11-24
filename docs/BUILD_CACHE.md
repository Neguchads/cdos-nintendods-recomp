# Incremental compilation with sccache (opt-in)

The native runner is compiled against an external `ndsrecomp` checkout and
generated source from the user's legally supplied game. **No ROM, saves,
generated game sources or game binaries belong in CI or the shared cache.**

## Windows (PowerShell)

Install [Mozilla sccache](https://github.com/mozilla/sccache) and ensure
`sccache.exe` is on PATH. Enable the wrapper just for the current shell:

```powershell
$env:NDS_SCCACHE = "1"
python tools/build.py --help
# Run your normal build.py subcommand after preparing your local toolchains and game.
sccache --show-stats
```

With `NDS_SCCACHE=1`, `tools/build.py` adds the CMake
`CMAKE_C_COMPILER_LAUNCHER` and `CMAKE_CXX_COMPILER_LAUNCHER` options.
Without it, the existing build is unchanged. If the variable is enabled and
sccache is missing, the build exits with an explicit error.

## Linux

```bash
export NDS_SCCACHE=1
bash tools/build_linux.sh  # requires the existing generated banks and sibling SDK
sccache --show-stats
```

To disable: `unset NDS_SCCACHE`.

**Limitations:** the first build is not faster, different compiler flags can
invalidate entries, and local cache hits are not guaranteed. CI runs only
source-only static analysis, Python regression tests and manifest/patch
validation; it cannot construct the proprietary native game build.
