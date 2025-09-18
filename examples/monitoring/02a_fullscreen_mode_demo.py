#!/usr/bin/env python3
"""
Fullscreen Mode Demo - Real Agent Example

This example demonstrates fullscreen monitoring mode using a real AgentHub agent
with web search capabilities for more interesting monitoring output.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.monitoring import MonitoringConfig


def main():
    """Demo fullscreen monitoring mode"""
    print("🖥️  FULLSCREEN MODE DEMO")
    print("=" * 50)
    print()
    print("Fullscreen mode clears the screen completely on each update.")
    print("You'll only see the monitoring information - no previous content.")
    print()
    print("Let's run an agent with web search capabilities...")
    print()
    
    try:
        # Load agent with fullscreen monitoring
        print("✅ Using fullscreen mode")
        print()
        
        agent = ah.load_agent("agentplug/analysis-agent", monitoring="fullscreen")
        
        print("🚀 Running agent with web search...")
        print("(Watch how the screen clears and shows only monitoring info)")
        print()
        
        # Run a task that will use tools for more complexity
        result = agent.analyze_text("Search for the latest news about artificial intelligence and summarize the top 3 stories")
        
        print("📊 Fullscreen mode completed!")
        print(f"   Result status: {result.get('status', 'unknown')}")
        print()
        print("✅ Key points about fullscreen mode:")
        print("   • Screen clears completely on each update")
        print("   • Shows only monitoring information")
        print("   • Clean, focused view")
        print("   • Good for: Presentations, production, clean monitoring")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 This demo requires AgentHub to be properly set up.")
        print("   Make sure you have the necessary dependencies installed.")


if __name__ == "__main__":
    main()
