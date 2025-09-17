# PowerShell script for setting up Agent Hub on Windows

Write-Host "Setting up Agent Hub..." -ForegroundColor Green
Write-Host "Installing dependencies with UV..." -ForegroundColor Cyan

# Check if UV is installed
try {
    $uvVersion = uv --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "UV is installed: $uvVersion" -ForegroundColor Green
    } else {
        throw "UV command failed"
    }
} catch {
    Write-Host "UV is not installed. Please install UV first:" -ForegroundColor Red
    Write-Host "   Visit: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
    Write-Host "   Or run in PowerShell:" -ForegroundColor Yellow
    Write-Host "   powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor White
    exit 1
}

# Create virtual environment and install dependencies
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
uv venv --python 3.11

Write-Host "Installing packages..." -ForegroundColor Cyan
# Activate virtual environment (Windows path)
& ".venv\Scripts\Activate.ps1"
uv pip install -e .
# Note: Run 'uv pip install -e ".[dev]"' if you want to install optional development dependencies (pytest, black, ruff, etc.)

Write-Host "Setup complete! Agent Hub is ready to use." -ForegroundColor Green
Write-Host ""
Write-Host "To use Agent Hub:" -ForegroundColor Yellow
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   agenthub --help" -ForegroundColor White
Write-Host "   # Or use in Python:" -ForegroundColor Gray
Write-Host "   python -c \"import agenthub as amg; print('Agent Hub ready!')\"" -ForegroundColor White
Write-Host ""
Write-Host "For more examples, see the examples/ directory" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: If you get execution policy errors, run:" -ForegroundColor Yellow
Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
