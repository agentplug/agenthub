#!/bin/bash
set -e

echo "🚀 Setting up Agent Hub development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ UV installed successfully"
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
uv venv

# Install dependencies
echo "📚 Installing dependencies..."
uv sync --dev

# Install pre-commit hooks
echo "🎣 Setting up pre-commit hooks..."
uv run pre-commit install

echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  uv run pytest"
echo ""
echo "To run the CLI:"
echo "  uv run python -m agentmanager.cli.main --help"
