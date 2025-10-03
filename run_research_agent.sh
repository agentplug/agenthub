#!/bin/bash

# Helper script to run research agent with WebSocket support
# This ensures the WebSocket port is clean before running

echo "🧹 Cleaning up WebSocket port 38765..."
lsof -ti:38765 | xargs kill -9 2>/dev/null || true
sleep 1

echo "🚀 Starting research agent with WebSocket support..."
python examples/advanced/research_agent.py
