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
pushd "%ROOT%runtime"
"%ROOT%runtime\nds_runner.exe" "%ROOT%run\bios" ^
    --interactive ^
    --rom "%ROOT%..\Roms\Castlevania - Dawn of Sorrow (USA).nds" ^
    --config "%ROOT%game.toml" ^
    --freebios ^
    --generated-firmware ^
    --boot direct ^
    --startup-mode automatic ^
    --diagnostics on ^
    --diagnostics-dir "%ROOT%runtime" ^
    --runtime-settings-path "%ROOT%saves\dos-settings.ini" ^
    --savestate-dir "%ROOT%run\savestates" ^
    --save-path "%ROOT%saves\dos.sav" ^
    --firmware-state-path "%ROOT%run\firmware_state.bin"
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
