@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."

set "PYTHON_BIN=python"
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_BIN=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_BIN=.venv\Scripts\python.exe"
)

"%PYTHON_BIN%" -c "import fpdf" >nul 2>&1
if errorlevel 1 (
    echo Setting up local Python environment in Helpers\.venv...
    python -m venv "%SCRIPT_DIR%.venv"
    set "PYTHON_BIN=%SCRIPT_DIR%.venv\Scripts\python.exe"
    "%PYTHON_BIN%" -m pip install -r "%SCRIPT_DIR%requirements.txt"
)

"%PYTHON_BIN%" "%SCRIPT_DIR%generate_pdf.py" %*
echo.
pause
