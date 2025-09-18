#!/usr/bin/env python3
"""
Basic vs Enhanced Monitoring - Clear Comparison

This example shows you the difference between basic monitoring and the new enhanced monitoring.
Perfect for users who want to understand what improvements they get.
"""

import sys
from pathlib import Path
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah


def show_basic_monitoring():
    """Show how basic monitoring works"""
    print("🔍 BASIC MONITORING")
    print("=" * 50)
    print("This is what you get with basic monitoring:")
    print("• Simple on/off switch")
    print("• Basic progress display")
    print("• Limited information")
    print()
    
    try:
        # Basic monitoring - just turn it on
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=True)
        
        print("✅ Agent loaded with basic monitoring")
        print("🚀 Running a simple task...")
        print()
        
        # Run a simple task
        result = agent.analyze_text("What is 5 plus 3?")
        
        print("📊 Basic monitoring result:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Summary: {result.get('summary', 'No summary available')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def show_enhanced_monitoring():
    """Show how enhanced monitoring works"""
    print("🚀 ENHANCED MONITORING")
    print("=" * 50)
    print("This is what you get with enhanced monitoring:")
    print("• Smart display modes (incremental vs fullscreen)")
    print("• Interactive controls (pause, filter, search)")
    print("• Better analysis with learning")
    print("• Resource management")
    print("• More detailed information")
    print()
    
    try:
        from agenthub.monitoring import MonitoringConfig
        
        # Enhanced monitoring with configuration
        config = MonitoringConfig.incremental()  # Choose display mode
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("✅ Agent loaded with enhanced monitoring")
        print("🚀 Running the same task with better monitoring...")
        print()
        
        # Run the same task but with enhanced monitoring
        result = agent.analyze_text("What is 5 plus 3?")
        
        print("📊 Enhanced monitoring result:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Summary: {result.get('summary', 'No summary available')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main demonstration"""
    print("🎯 AgentHub Monitoring: Basic vs Enhanced")
    print("=" * 60)
    print()
    print("This demo shows you the difference between basic and enhanced monitoring.")
    print("You'll see how the enhanced version gives you much more control and information.")
    print()
    
    # Show basic monitoring
    show_basic_monitoring()
    
    print("\n" + "="*60 + "\n")
    
    # Show enhanced monitoring
    show_enhanced_monitoring()
    
    print("🎉 Key Benefits of Enhanced Monitoring:")
    print("=" * 50)
    print("✅ Better display options (incremental vs fullscreen)")
    print("✅ Interactive controls (pause, filter, search)")
    print("✅ Smarter analysis that learns from your usage")
    print("✅ Automatic resource management")
    print("✅ More detailed progress information")
    print("✅ Flexible configuration options")
    print()
    print("💡 Next: Try the other examples to see specific features!")


if __name__ == "__main__":
    main()
