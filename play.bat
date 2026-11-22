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
pushd "%ROOT%runtime"
"%ROOT%runtime\nds_runner.exe" "%ROOT%run\bios" ^
    --interactive ^
    --rom "%ROOT%..\Roms\Castlevania - Dawn of Sorrow (USA).nds" ^
    %PTBR_ARG% ^
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
