#!/usr/bin/env python3
"""
Complete Monitoring Demo - All Features Together

This example shows you how to use all the enhanced monitoring features
together to get the best possible monitoring experience.
"""

import sys
from pathlib import Path
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.monitoring import MonitoringConfig, MonitoringBuilder


def show_all_features():
    """Show all available features"""
    print("🎯 ALL ENHANCED MONITORING FEATURES")
    print("=" * 60)
    print()
    print("The enhanced monitoring system includes these features:")
    print()
    print("🖥️  DISPLAY MODES:")
    print("   • Incremental: Preserves terminal history")
    print("   • Fullscreen: Clean, focused view")
    print()
    print("🎮 INTERACTIVE CONTROLS:")
    print("   • Pause/Resume monitoring")
    print("   • Filter logs (all, errors, warnings)")
    print("   • Search in logs")
    print("   • Toggle metrics display")
    print("   • Toggle compact mode")
    print("   • Toggle timeline display")
    print("   • Export logs")
    print()
    print("🧠 SMART ANALYSIS:")
    print("   • AI-powered log analysis")
    print("   • Learning from usage patterns")
    print("   • Pattern recognition")
    print("   • Intelligent suggestions")
    print()
    print("⚡ RESOURCE MANAGEMENT:")
    print("   • Automatic memory management")
    print("   • Adaptive analysis frequency")
    print("   • Performance optimization")
    print("   • Resource monitoring")
    print()
    print("⚙️  FLEXIBLE CONFIGURATION:")
    print("   • Quick presets")
    print("   • Advanced customization")
    print("   • Builder pattern")
    print("   • Environment variables")
    print()


def demo_development_workflow():
    """Demonstrate development workflow"""
    print("🔄 DEVELOPMENT WORKFLOW")
    print("=" * 50)
    print("Perfect for developing and debugging agents:")
    print()
    
    try:
        # Development configuration
        config = MonitoringConfig.incremental()
        config.interactive = True
        config.enable_learning = True
        config.show_metrics = True
        config.show_timeline = True
        
        print("✅ Development configuration:")
        print(f"   Display mode: {config.display_mode}")
        print(f"   Interactive: {config.interactive}")
        print(f"   Learning enabled: {config.enable_learning}")
        print(f"   Metrics shown: {config.show_metrics}")
        print(f"   Timeline shown: {config.show_timeline}")
        print()
        
        # Load agent
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("🚀 Running development task...")
        print("(This configuration is perfect for development)")
        print()
        
        # Run a task
        result = agent.analyze_text("What is 25 plus 15?")
        
        print("📊 Development monitoring completed!")
        print(f"   Result: {result.get('status', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_production_workflow():
    """Demonstrate production workflow"""
    print("🏭 PRODUCTION WORKFLOW")
    print("=" * 50)
    print("Optimized for production environments:")
    print()
    
    try:
        # Production configuration
        config = MonitoringConfig.fullscreen()
        config.interactive = False
        config.enable_learning = True
        config.max_memory_mb = 100
        config.analysis_interval = 3.0
        config.export_format = "json"
        
        print("✅ Production configuration:")
        print(f"   Display mode: {config.display_mode}")
        print(f"   Interactive: {config.interactive}")
        print(f"   Memory limit: {config.max_memory_mb}MB")
        print(f"   Analysis interval: {config.analysis_interval}s")
        print(f"   Export format: {config.export_format}")
        print()
        
        # Load agent
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("🚀 Running production task...")
        print("(This configuration is optimized for production)")
        print()
        
        # Run a task
        result = agent.analyze_text("What is 30 times 4?")
        
        print("📊 Production monitoring completed!")
        print(f"   Result: {result.get('status', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_debug_workflow():
    """Demonstrate debug workflow"""
    print("🐛 DEBUG WORKFLOW")
    print("=" * 50)
    print("High verbosity for debugging issues:")
    print()
    
    try:
        # Debug configuration
        config = MonitoringConfig.debug()
        
        print("✅ Debug configuration:")
        print(f"   Display mode: {config.display_mode}")
        print(f"   Interactive: {config.interactive}")
        print(f"   Learning enabled: {config.enable_learning}")
        print(f"   Refresh rate: {config.refresh_rate}s")
        print(f"   Analysis interval: {config.analysis_interval}s")
        print()
        
        # Load agent
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("🚀 Running debug task...")
        print("(This configuration shows maximum detail)")
        print()
        
        # Run a task
        result = agent.analyze_text("What is 40 divided by 8?")
        
        print("📊 Debug monitoring completed!")
        print(f"   Result: {result.get('status', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_custom_workflow():
    """Demonstrate custom workflow"""
    print("🔧 CUSTOM WORKFLOW")
    print("=" * 50)
    print("Custom configuration for specific needs:")
    print()
    
    try:
        # Custom configuration using builder pattern
        config = (MonitoringBuilder()
                 .incremental()
                 .interactive()
                 .memory_limit(150)
                 .analysis_interval(1.5)
                 .show_metrics()
                 .enable_learning()
                 .export_format("csv")
                 .build())
        
        print("✅ Custom configuration:")
        print(f"   Display mode: {config.display_mode}")
        print(f"   Interactive: {config.interactive}")
        print(f"   Memory limit: {config.max_memory_mb}MB")
        print(f"   Analysis interval: {config.analysis_interval}s")
        print(f"   Learning enabled: {config.enable_learning}")
        print(f"   Export format: {config.export_format}")
        print()
        
        # Load agent
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("🚀 Running custom task...")
        print("(This configuration is tailored to specific needs)")
        print()
        
        # Run a task
        result = agent.analyze_text("What is 50 minus 12?")
        
        print("📊 Custom monitoring completed!")
        print(f"   Result: {result.get('status', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def show_workflow_recommendations():
    """Show workflow recommendations"""
    print("💡 WORKFLOW RECOMMENDATIONS")
    print("=" * 50)
    print()
    print("🎯 CHOOSE THE RIGHT WORKFLOW:")
    print()
    print("🔄 DEVELOPMENT:")
    print("   • Use incremental mode")
    print("   • Enable interactive controls")
    print("   • Enable learning")
    print("   • Show metrics and timeline")
    print("   • Good for: Coding, debugging, testing")
    print()
    print("🏭 PRODUCTION:")
    print("   • Use fullscreen mode")
    print("   • Disable interactive controls")
    print("   • Enable learning")
    print("   • Set memory limits")
    print("   • Enable export")
    print("   • Good for: Live systems, presentations")
    print()
    print("🐛 DEBUGGING:")
    print("   • Use debug preset")
    print("   • High verbosity")
    print("   • Fast updates")
    print("   • All features enabled")
    print("   • Good for: Troubleshooting, analysis")
    print()
    print("⚡ MINIMAL:")
    print("   • Use minimal preset")
    print("   • Low resource usage")
    print("   • Essential info only")
    print("   • Good for: Resource-constrained environments")
    print()


def show_integration_examples():
    """Show integration examples"""
    print("🔗 INTEGRATION EXAMPLES")
    print("=" * 50)
    print()
    print("🚀 QUICK START:")
    print("   agent = ah.load_agent('my-agent', monitoring=True)")
    print()
    print("🎯 RECOMMENDED:")
    print("   config = MonitoringConfig.incremental()")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    print("🔧 CUSTOM:")
    print("   config = (MonitoringBuilder()")
    print("            .incremental()")
    print("            .interactive()")
    print("            .memory_limit(200)")
    print("            .analysis_interval(1.5)")
    print("            .show_metrics()")
    print("            .enable_learning()")
    print("            .build())")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    print("🌍 ENVIRONMENT:")
    print("   config = MonitoringConfig.from_environment()")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()


def main():
    """Main demonstration"""
    print("🎯 AgentHub Complete Monitoring Demo")
    print("=" * 60)
    print()
    print("This demo shows you how to use all the enhanced monitoring")
    print("features together to get the best possible experience.")
    print()
    
    # Show all features
    show_all_features()
    
    print("\n" + "="*60 + "\n")
    
    # Demo different workflows
    demo_development_workflow()
    
    print("\n" + "="*60 + "\n")
    
    demo_production_workflow()
    
    print("\n" + "="*60 + "\n")
    
    demo_debug_workflow()
    
    print("\n" + "="*60 + "\n")
    
    demo_custom_workflow()
    
    print("\n" + "="*60 + "\n")
    
    # Show recommendations and examples
    show_workflow_recommendations()
    print()
    show_integration_examples()
    
    print("🎉 Complete Monitoring Demo Complete!")
    print("=" * 60)
    print("💡 Mix and match features to create your perfect monitoring setup!")


if __name__ == "__main__":
    main()
