#!/usr/bin/env python3
"""
Incremental Mode Demo - Real Agent Example

This example demonstrates incremental monitoring mode using a real AgentHub agent
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
    """Demo incremental monitoring mode"""
    print("🔄 INCREMENTAL MODE DEMO")
    print("=" * 50)
    print()
    print("Incremental mode keeps previous content visible.")
    print("New monitoring information appears below existing content.")
    print()
    print("Let's run an agent with web search capabilities...")
    print()
    
    try:
        # Load agent with incremental monitoring
        print("✅ Using incremental mode")
        print()
        
        agent = ah.load_agent("agentplug/analysis-agent", monitoring="incremental")
        
        print("🚀 Running agent with web search...")
        print("(Notice how this text stays visible while monitoring updates)")
        print("(Previous content from fullscreen demo is still above)")
        print()
        
        # Run a task that will use tools for more complexity
        result = agent.analyze_text("Search for information about machine learning trends in 2024 and provide a brief overview")
        
        print("📊 Incremental mode completed!")
        print(f"   Result status: {result.get('status', 'unknown')}")
        print()
        print("✅ Key points about incremental mode:")
        print("   • Keeps previous content visible")
        print("   • Adds monitoring info below existing content")
        print("   • Preserves terminal history")
        print("   • Good for: Development, debugging, seeing history")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 This demo requires AgentHub to be properly set up.")
        print("   Make sure you have the necessary dependencies installed.")


if __name__ == "__main__":
    main()
