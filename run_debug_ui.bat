@echo off
setlocal

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "debug\debug_launcher.py"
) else (
    python "debug\debug_launcher.py"
)

endlocal
