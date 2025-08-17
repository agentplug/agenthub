#!/bin/bash

echo "🚀 Setting up Scientific Paper Analyzer Agent..."
echo "📦 Installing dependencies with UV..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment and install dependencies
echo "🔧 Creating virtual environment..."
uv venv --python 3.11

echo "📦 Installing packages..."
source .venv/bin/activate
uv pip install -e .

echo "✅ Setup complete! Agent is ready to use."
echo ""
echo "🎯 To run the agent:"
echo "   source .venv/bin/activate"
echo "   python agent.py '{\"method\": \"get_info\", \"parameters\": {}}'"
echo ""
echo "📚 For more examples, see the examples/ directory"
