@echo off
setlocal
set "ROOT=%~dp0"
if not exist "%ROOT%runtime\nds_runner.exe" (
    echo [erro] runtime\nds_runner.exe nao encontrado. Rode: python tools\build.py all
    exit /b 1
)
if not exist "%ROOT%run\bios" mkdir "%ROOT%run\bios"
if not exist "%ROOT%run\savestates" mkdir "%ROOT%run\savestates"
if not exist "%ROOT%saves" mkdir "%ROOT%saves"
set "NDS_HOSTPROF=off"
set "PTBR_ARG="
if exist "%ROOT%mods\ptbr\dos-ptbr.dospatch" set PTBR_ARG=--ptbr-patch "%ROOT%mods\ptbr\dos-ptbr.dospatch"
set "DEF_EN_ARG="
if exist "%ROOT%mods\definitive\dos-definitive-en.dospatch" set DEF_EN_ARG=--definitive-en-patch "%ROOT%mods\definitive\dos-definitive-en.dospatch"
set "DEF_PT_ARG="
if exist "%ROOT%mods\definitive\dos-definitive-ptbr.dospatch" set DEF_PT_ARG=--definitive-ptbr-patch "%ROOT%mods\definitive\dos-definitive-ptbr.dospatch"
set "INTRO_ARG="
if exist "%ROOT%mods\intro\opening.mp4" set INTRO_ARG=--intro-video "%ROOT%mods\intro\opening.mp4"
set "REG_ARG="
if exist "%ROOT%mods\registry.json" set REG_ARG=--mod-registry "%ROOT%mods\registry.json" --mod-data-dir "%ROOT%mods"
pushd "%ROOT%runtime"
"%ROOT%runtime\nds_runner.exe" "%ROOT%run\bios" ^
    --interactive ^
    --rom "%ROOT%..\Roms\Castlevania - Dawn of Sorrow (USA).nds" ^
    %PTBR_ARG% ^
    %DEF_EN_ARG% ^
    %DEF_PT_ARG% ^
    %INTRO_ARG% ^
    %REG_ARG% ^
    --config "%ROOT%game.toml" ^
    --freebios ^
    --generated-firmware ^
    --boot direct ^
    --startup-mode automatic ^
    --diagnostics off ^
    --no-coverage-manifest ^
    --runtime-settings-path "%ROOT%saves\dos-settings.ini" ^
    --savestate-dir "%ROOT%run\savestates" ^
    --save-path "%ROOT%saves\dos.sav" ^
    --firmware-state-path "%ROOT%run\firmware_state.bin"
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
