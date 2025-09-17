@echo off
REM Windows batch script for setting up Agent Hub

echo Setting up Agent Hub...
echo Installing dependencies with UV...

REM Check if UV is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV is not installed. Please install UV first:
    echo    Visit: https://docs.astral.sh/uv/getting-started/installation/
    echo    Or run in PowerShell:
    echo    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo UV is installed
echo Creating virtual environment...
uv venv --python 3.11

echo Installing packages...
REM Activate virtual environment (Windows path)
call .venv\Scripts\activate.bat
uv pip install -e .
REM Note: Run 'uv pip install -e ".[dev]"' if you want to install optional development dependencies (pytest, black, ruff, etc.)

echo Setup complete! Agent Hub is ready to use.
echo.
echo To use Agent Hub:
echo    .venv\Scripts\activate.bat
echo    agenthub --help
echo    # Or use in Python:
echo    python -c "import agenthub as amg; print('Agent Hub ready!')"
echo.
echo For more examples, see the examples/ directory
echo.
pause
