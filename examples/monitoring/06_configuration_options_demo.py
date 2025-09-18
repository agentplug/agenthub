#!/usr/bin/env python3
"""
Configuration Options Demo - Customize Your Monitoring

This example shows you all the different ways to configure
the enhanced monitoring system to match your needs.
"""

import sys
from pathlib import Path
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.monitoring import MonitoringConfig, MonitoringBuilder


def explain_configuration_options():
    """Explain what configuration options are available"""
    print("⚙️  CONFIGURATION OPTIONS EXPLAINED")
    print("=" * 50)
    print()
    print("The enhanced monitoring system offers many ways to configure it:")
    print()
    print("🎯 QUICK OPTIONS:")
    print("   • Simple boolean: monitoring=True")
    print("   • String presets: monitoring='incremental'")
    print("   • Easy to use, good for most cases")
    print()
    print("🔧 ADVANCED OPTIONS:")
    print("   • Full configuration objects")
    print("   • Builder pattern for complex setups")
    print("   • Environment variable support")
    print()
    print("📋 PRESET CONFIGURATIONS:")
    print("   • Development: Interactive, learning enabled")
    print("   • Production: Clean, resource optimized")
    print("   • Debug: High verbosity, all features")
    print("   • Minimal: Low resource usage")
    print()


def demo_quick_options():
    """Demonstrate quick configuration options"""
    print("🚀 QUICK CONFIGURATION OPTIONS")
    print("=" * 50)
    print("These are the easiest ways to configure monitoring:")
    print()
    
    # Option 1: Simple boolean
    print("1️⃣  Simple boolean (easiest):")
    print("   agent = ah.load_agent('my-agent', monitoring=True)")
    print("   # Uses default settings (incremental mode)")
    print()
    
    # Option 2: String presets
    print("2️⃣  String presets (simple):")
    print("   agent = ah.load_agent('my-agent', monitoring='incremental')")
    print("   agent = ah.load_agent('my-agent', monitoring='fullscreen')")
    print("   # Uses preset configurations")
    print()
    
    # Option 3: Preset methods
    print("3️⃣  Preset methods (recommended):")
    print("   config = MonitoringConfig.incremental()")
    print("   config = MonitoringConfig.fullscreen()")
    print("   config = MonitoringConfig.production()")
    print("   config = MonitoringConfig.debug()")
    print("   config = MonitoringConfig.minimal()")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()


def demo_advanced_configuration():
    """Demonstrate advanced configuration options"""
    print("🔧 ADVANCED CONFIGURATION OPTIONS")
    print("=" * 50)
    print("For more control, you can customize individual settings:")
    print()
    
    print("📋 DISPLAY SETTINGS:")
    print("   config = MonitoringConfig()")
    print("   config.display_mode = 'incremental'  # or 'fullscreen'")
    print("   config.interactive = True")
    print("   config.refresh_rate = 1.0  # seconds")
    print("   config.compact_mode = False")
    print()
    
    print("🧠 ANALYSIS SETTINGS:")
    print("   config.analysis_interval = 2.0  # seconds")
    print("   config.enable_learning = True")
    print("   config.adaptive_analysis = True")
    print("   config.context_window = 50  # log lines to consider")
    print()
    
    print("💾 RESOURCE SETTINGS:")
    print("   config.max_memory_mb = 200  # memory limit")
    print("   config.max_logs = 1000  # max log lines")
    print("   config.error_priority = True  # prioritize errors")
    print()
    
    print("📊 METRICS SETTINGS:")
    print("   config.show_metrics = True")
    print("   config.show_timeline = True")
    print("   config.export_format = 'json'  # or 'csv', 'txt'")
    print("   config.export_path = 'monitoring_logs.json'")
    print()


def demo_builder_pattern():
    """Demonstrate the builder pattern"""
    print("🏗️  BUILDER PATTERN")
    print("=" * 50)
    print("The builder pattern makes complex configurations easy:")
    print()
    
    print("🔨 BASIC BUILDER:")
    print("   config = (MonitoringBuilder()")
    print("            .incremental()")
    print("            .interactive()")
    print("            .build())")
    print()
    
    print("🔨 ADVANCED BUILDER:")
    print("   config = (MonitoringBuilder()")
    print("            .incremental()")
    print("            .interactive()")
    print("            .memory_limit(200)")
    print("            .analysis_interval(1.5)")
    print("            .show_metrics()")
    print("            .enable_learning()")
    print("            .export_format('json')")
    print("            .build())")
    print()
    
    print("🔨 PRODUCTION BUILDER:")
    print("   config = (MonitoringBuilder()")
    print("            .fullscreen()")
    print("            .memory_limit(100)")
    print("            .analysis_interval(3.0)")
    print("            .export_format('csv')")
    print("            .build())")
    print()


def demo_preset_configurations():
    """Demonstrate preset configurations"""
    print("📋 PRESET CONFIGURATIONS")
    print("=" * 50)
    print("These are ready-made configurations for common use cases:")
    print()
    
    print("🔄 DEVELOPMENT CONFIGURATION:")
    print("   config = MonitoringConfig.incremental()")
    print("   # Features: Interactive, learning, metrics, timeline")
    print("   # Use for: Development, debugging, testing")
    print()
    
    print("🏭 PRODUCTION CONFIGURATION:")
    print("   config = MonitoringConfig.fullscreen()")
    print("   # Features: Clean display, resource optimized, export")
    print("   # Use for: Production, presentations, clean monitoring")
    print()
    
    print("🐛 DEBUG CONFIGURATION:")
    print("   config = MonitoringConfig.debug()")
    print("   # Features: High verbosity, all metrics, fast updates")
    print("   # Use for: Debugging issues, detailed analysis")
    print()
    
    print("⚡ MINIMAL CONFIGURATION:")
    print("   config = MonitoringConfig.minimal()")
    print("   # Features: Low resource usage, essential info only")
    print("   # Use for: Resource-constrained environments")
    print()


def demo_environment_variables():
    """Demonstrate environment variable configuration"""
    print("🌍 ENVIRONMENT VARIABLE CONFIGURATION")
    print("=" * 50)
    print("You can configure monitoring using environment variables:")
    print()
    
    print("📝 SET ENVIRONMENT VARIABLES:")
    print("   export AGENTHUB_MONITORING_DISPLAY_MODE=incremental")
    print("   export AGENTHUB_MONITORING_INTERACTIVE=true")
    print("   export AGENTHUB_MONITORING_MEMORY_LIMIT=200")
    print("   export AGENTHUB_MONITORING_ANALYSIS_INTERVAL=2.0")
    print()
    
    print("🔧 USE IN CODE:")
    print("   config = MonitoringConfig.from_environment()")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    
    print("💡 BENEFITS:")
    print("   • No code changes needed")
    print("   • Easy to change settings")
    print("   • Good for different environments")
    print()


def demo_common_use_cases():
    """Demonstrate common use cases"""
    print("🎯 COMMON USE CASES")
    print("=" * 50)
    print("Here are some common monitoring configurations:")
    print()
    
    print("🔄 DEVELOPMENT WORKFLOW:")
    print("   config = MonitoringConfig.incremental()")
    print("   # Interactive monitoring for development")
    print("   # Keeps terminal history, shows all details")
    print()
    
    print("🏭 PRODUCTION MONITORING:")
    print("   config = MonitoringConfig.fullscreen()")
    print("   # Clean monitoring for production")
    print("   # Optimized for performance and clarity")
    print()
    
    print("🐛 DEBUGGING ISSUES:")
    print("   config = MonitoringConfig.debug()")
    print("   # High verbosity for debugging")
    print("   # Shows all information, fast updates")
    print()
    
    print("⚡ RESOURCE CONSTRAINED:")
    print("   config = MonitoringConfig.minimal()")
    print("   # Minimal resource usage")
    print("   # Essential information only")
    print()
    
    print("🎮 INTERACTIVE SESSION:")
    print("   config = (MonitoringBuilder()")
    print("            .incremental()")
    print("            .interactive()")
    print("            .show_metrics()")
    print("            .enable_learning()")
    print("            .build())")
    print("   # Full interactive experience")
    print()


def show_configuration_examples():
    """Show practical configuration examples"""
    print("💡 PRACTICAL CONFIGURATION EXAMPLES")
    print("=" * 50)
    print()
    
    print("🚀 QUICK START (easiest):")
    print("   agent = ah.load_agent('my-agent', monitoring=True)")
    print()
    
    print("🎯 RECOMMENDED (good balance):")
    print("   config = MonitoringConfig.incremental()")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    
    print("🔧 CUSTOM (full control):")
    print("   config = MonitoringConfig()")
    print("   config.display_mode = 'incremental'")
    print("   config.interactive = True")
    print("   config.enable_learning = True")
    print("   config.max_memory_mb = 200")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    
    print("🏗️  BUILDER (complex setups):")
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


def main():
    """Main demonstration"""
    print("🎯 AgentHub Configuration Options Demo")
    print("=" * 60)
    print()
    print("This demo shows you all the different ways to configure")
    print("the enhanced monitoring system to match your specific needs.")
    print()
    
    # Explain configuration options
    explain_configuration_options()
    
    # Demo different configuration methods
    demo_quick_options()
    print()
    demo_advanced_configuration()
    print()
    demo_builder_pattern()
    print()
    demo_preset_configurations()
    print()
    demo_environment_variables()
    print()
    demo_common_use_cases()
    print()
    show_configuration_examples()
    
    print("🎉 Configuration Options Demo Complete!")
    print("=" * 60)
    print("💡 Choose the configuration method that works best for you!")


if __name__ == "__main__":
    main()
