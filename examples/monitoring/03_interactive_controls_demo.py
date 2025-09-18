#!/usr/bin/env python3
"""
Interactive Controls Demo - Take Control of Your Monitoring

This example shows you how to use interactive controls to customize
your monitoring experience in real-time.
"""

import sys
from pathlib import Path
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.monitoring import MonitoringConfig


def explain_interactive_controls():
    """Explain what interactive controls are"""
    print("🎮 INTERACTIVE CONTROLS EXPLAINED")
    print("=" * 50)
    print()
    print("Interactive controls let you customize your monitoring experience")
    print("while it's running. You can:")
    print()
    print("⏸️  PAUSE/RESUME - Stop and start monitoring")
    print("🔍 FILTER - Show only certain types of information")
    print("🔎 SEARCH - Find specific information in logs")
    print("📊 TOGGLE METRICS - Show or hide performance data")
    print("📱 COMPACT MODE - Switch between detailed and compact views")
    print("📈 TIMELINE - Show or hide execution timeline")
    print("💾 EXPORT - Save logs to a file")
    print("❓ HELP - See all available controls")
    print("🚪 QUIT - Stop monitoring completely")
    print()


def demo_basic_interactive():
    """Demonstrate basic interactive features"""
    print("🎛️  BASIC INTERACTIVE FEATURES")
    print("=" * 50)
    print("Let's see how interactive monitoring works...")
    print()
    
    try:
        # Create interactive monitoring config
        config = MonitoringConfig.incremental()
        config.interactive = True  # Enable interactive mode
        config.show_metrics = True  # Show performance metrics
        config.show_timeline = True  # Show execution timeline
        
        print("✅ Interactive monitoring enabled")
        print("🎮 Available controls:")
        print("   [p] - Pause/Resume")
        print("   [f] - Filter logs")
        print("   [s] - Search in logs")
        print("   [m] - Toggle metrics")
        print("   [c] - Toggle compact mode")
        print("   [t] - Toggle timeline")
        print("   [e] - Export logs")
        print("   [h] - Show help")
        print("   [q] - Quit")
        print()
        
        # Load agent with interactive monitoring
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("🚀 Running task with interactive monitoring...")
        print("(In a real scenario, you could press keys to control the display)")
        print()
        
        # Run a task
        result = agent.analyze_text("What is 15 plus 25?")
        
        print("📊 Interactive monitoring completed!")
        print(f"   Result: {result.get('status', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_filtering():
    """Demonstrate filtering capabilities"""
    print("🔍 FILTERING CAPABILITIES")
    print("=" * 50)
    print("Filtering lets you focus on specific types of information:")
    print()
    print("📋 Available filters:")
    print("   • all - Show everything")
    print("   • errors - Show only error messages")
    print("   • warnings - Show only warning messages")
    print("   • custom - Show only messages matching your search")
    print()
    print("💡 This is useful when:")
    print("   • You want to focus on problems")
    print("   • You're looking for specific information")
    print("   • You want to reduce visual clutter")
    print()


def demo_search():
    """Demonstrate search capabilities"""
    print("🔎 SEARCH CAPABILITIES")
    print("=" * 50)
    print("Search lets you find specific information in the logs:")
    print()
    print("🔍 You can search for:")
    print("   • Error messages")
    print("   • Specific tool names")
    print("   • Keywords")
    print("   • Any text in the logs")
    print()
    print("💡 This is useful when:")
    print("   • You're debugging a specific issue")
    print("   • You want to find when something happened")
    print("   • You're looking for patterns")
    print()


def demo_metrics_display():
    """Demonstrate metrics display"""
    print("📊 METRICS DISPLAY")
    print("=" * 50)
    print("Metrics show you performance information:")
    print()
    print("📈 Available metrics:")
    print("   • Execution time")
    print("   • Memory usage")
    print("   • CPU usage")
    print("   • Number of logs")
    print("   • Tool usage statistics")
    print()
    print("💡 This is useful when:")
    print("   • You want to monitor performance")
    print("   • You're optimizing your agents")
    print("   • You want to see resource usage")
    print()


def demo_export():
    """Demonstrate export capabilities"""
    print("💾 EXPORT CAPABILITIES")
    print("=" * 50)
    print("Export lets you save monitoring data for later analysis:")
    print()
    print("📁 Export formats:")
    print("   • JSON - Structured data for analysis")
    print("   • CSV - Spreadsheet format")
    print("   • TXT - Plain text format")
    print()
    print("💡 This is useful when:")
    print("   • You want to analyze data later")
    print("   • You need to share results with others")
    print("   • You want to keep records")
    print()


def show_how_to_use():
    """Show how to use interactive controls"""
    print("⚙️  HOW TO USE INTERACTIVE CONTROLS")
    print("=" * 50)
    print()
    print("1️⃣  Enable interactive mode:")
    print("   config = MonitoringConfig.incremental()")
    print("   config.interactive = True")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    print("2️⃣  Use keyboard shortcuts:")
    print("   • Press 'p' to pause/resume")
    print("   • Press 'f' to cycle through filters")
    print("   • Press 's' to search")
    print("   • Press 'm' to toggle metrics")
    print("   • Press 'h' for help")
    print()
    print("3️⃣  Customize your experience:")
    print("   • Choose what information to show")
    print("   • Filter out noise")
    print("   • Focus on what matters to you")
    print()


def main():
    """Main demonstration"""
    print("🎯 AgentHub Interactive Controls Demo")
    print("=" * 60)
    print()
    print("This demo shows you how to use interactive controls to")
    print("customize your monitoring experience in real-time.")
    print()
    
    # Explain interactive controls
    explain_interactive_controls()
    
    # Demo basic interactive features
    demo_basic_interactive()
    
    print("\n" + "="*60 + "\n")
    
    # Demo specific features
    demo_filtering()
    print()
    demo_search()
    print()
    demo_metrics_display()
    print()
    demo_export()
    
    print("\n" + "="*60 + "\n")
    
    # Show how to use
    show_how_to_use()
    
    print("🎉 Interactive Controls Demo Complete!")
    print("=" * 60)
    print("💡 Try interactive mode and see how much control you have!")


if __name__ == "__main__":
    main()
