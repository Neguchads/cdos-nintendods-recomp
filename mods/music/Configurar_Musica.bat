@echo off
setlocal
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0configurar_musica.py"
) else (
    python "%~dp0configurar_musica.py"
    if errorlevel 1 pause
)
