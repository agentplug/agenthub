#!/usr/bin/env python3
"""
Smart Analysis Demo - AI-Powered Monitoring

This example shows you how the enhanced monitoring system uses AI
to provide smarter analysis and learn from your usage patterns.
"""

import sys
from pathlib import Path
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.monitoring import MonitoringConfig


def explain_smart_analysis():
    """Explain what smart analysis is"""
    print("🧠 SMART ANALYSIS EXPLAINED")
    print("=" * 50)
    print()
    print("The enhanced monitoring system uses AI to provide smarter analysis:")
    print()
    print("🔍 CONTEXT-AWARE ANALYSIS:")
    print("   • Understands what your agent is doing")
    print("   • Provides relevant insights")
    print("   • Adapts to different types of tasks")
    print()
    print("📚 LEARNING CAPABILITIES:")
    print("   • Remembers patterns from previous runs")
    print("   • Gets better over time")
    print("   • Provides more accurate suggestions")
    print()
    print("🎯 PATTERN RECOGNITION:")
    print("   • Identifies common issues")
    print("   • Recognizes successful patterns")
    print("   • Suggests improvements")
    print()
    print("💡 INTELLIGENT SUGGESTIONS:")
    print("   • Proactive problem solving")
    print("   • Performance optimization tips")
    print("   • Best practice recommendations")
    print()


def demo_basic_analysis():
    """Demonstrate basic analysis"""
    print("📊 BASIC ANALYSIS")
    print("=" * 50)
    print("Let's see how basic monitoring analyzes your agent...")
    print()
    
    try:
        # Basic monitoring
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=True)
        
        print("✅ Basic monitoring enabled")
        print("🚀 Running a simple task...")
        print()
        
        # Run a task
        result = agent.analyze_text("What is 10 plus 5?")
        
        print("📊 Basic analysis result:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Summary: {result.get('summary', 'No summary available')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_enhanced_analysis():
    """Demonstrate enhanced analysis"""
    print("🚀 ENHANCED ANALYSIS")
    print("=" * 50)
    print("Now let's see how enhanced monitoring provides smarter analysis...")
    print()
    
    try:
        # Enhanced monitoring with learning
        config = MonitoringConfig.incremental()
        config.enable_learning = True  # Enable learning
        config.adaptive_analysis = True  # Enable adaptive analysis
        
        agent = ah.load_agent("agentplug/analysis-agent", monitoring=config)
        
        print("✅ Enhanced monitoring with learning enabled")
        print("🧠 AI will analyze and learn from this execution")
        print("🚀 Running the same task with smarter analysis...")
        print()
        
        # Run the same task
        result = agent.analyze_text("What is 10 plus 5?")
        
        print("📊 Enhanced analysis result:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Summary: {result.get('summary', 'No summary available')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_learning_capabilities():
    """Demonstrate learning capabilities"""
    print("📚 LEARNING CAPABILITIES")
    print("=" * 50)
    print("The enhanced monitoring system learns from your usage:")
    print()
    print("🔄 PATTERN LEARNING:")
    print("   • Remembers successful execution patterns")
    print("   • Identifies common error patterns")
    print("   • Learns your preferred monitoring settings")
    print()
    print("📈 IMPROVEMENT OVER TIME:")
    print("   • Gets better at predicting issues")
    print("   • Provides more relevant suggestions")
    print("   • Adapts to your specific use cases")
    print()
    print("🎯 PERSONALIZED INSIGHTS:")
    print("   • Tailored recommendations")
    print("   • Agent-specific optimizations")
    print("   • Customized monitoring preferences")
    print()


def demo_pattern_recognition():
    """Demonstrate pattern recognition"""
    print("🔍 PATTERN RECOGNITION")
    print("=" * 50)
    print("The system recognizes patterns in your agent's behavior:")
    print()
    print("✅ SUCCESS PATTERNS:")
    print("   • Identifies what works well")
    print("   • Suggests repeating successful approaches")
    print("   • Highlights best practices")
    print()
    print("❌ ERROR PATTERNS:")
    print("   • Spots recurring issues")
    print("   • Suggests preventive measures")
    print("   • Helps avoid common mistakes")
    print()
    print("⚡ PERFORMANCE PATTERNS:")
    print("   • Identifies performance bottlenecks")
    print("   • Suggests optimization opportunities")
    print("   • Tracks resource usage trends")
    print()


def demo_intelligent_suggestions():
    """Demonstrate intelligent suggestions"""
    print("💡 INTELLIGENT SUGGESTIONS")
    print("=" * 50)
    print("The system provides smart suggestions based on analysis:")
    print()
    print("🔧 PROBLEM SOLVING:")
    print("   • Suggests fixes for common issues")
    print("   • Provides troubleshooting steps")
    print("   • Offers alternative approaches")
    print()
    print("⚡ OPTIMIZATION:")
    print("   • Suggests performance improvements")
    print("   • Recommends resource optimizations")
    print("   • Identifies efficiency opportunities")
    print()
    print("📚 BEST PRACTICES:")
    print("   • Suggests industry best practices")
    print("   • Recommends configuration improvements")
    print("   • Offers usage tips and tricks")
    print()


def show_benefits():
    """Show the benefits of smart analysis"""
    print("🎯 BENEFITS OF SMART ANALYSIS")
    print("=" * 50)
    print()
    print("🚀 IMMEDIATE BENEFITS:")
    print("   • Better understanding of what's happening")
    print("   • More relevant information")
    print("   • Clearer problem identification")
    print()
    print("📈 LONG-TERM BENEFITS:")
    print("   • Improved agent performance")
    print("   • Fewer errors and issues")
    print("   • Better resource utilization")
    print()
    print("💡 LEARNING BENEFITS:")
    print("   • System gets smarter over time")
    print("   • Personalized recommendations")
    print("   • Continuous improvement")
    print()


def show_how_to_enable():
    """Show how to enable smart analysis"""
    print("⚙️  HOW TO ENABLE SMART ANALYSIS")
    print("=" * 50)
    print()
    print("1️⃣  Enable learning:")
    print("   config = MonitoringConfig.incremental()")
    print("   config.enable_learning = True")
    print("   agent = ah.load_agent('my-agent', monitoring=config)")
    print()
    print("2️⃣  Enable adaptive analysis:")
    print("   config.adaptive_analysis = True")
    print("   config.context_window = 50  # How much history to consider")
    print()
    print("3️⃣  Use preset configurations:")
    print("   config = MonitoringConfig.debug()  # Includes learning")
    print("   config = MonitoringConfig.incremental()  # Basic learning")
    print()


def main():
    """Main demonstration"""
    print("🎯 AgentHub Smart Analysis Demo")
    print("=" * 60)
    print()
    print("This demo shows you how the enhanced monitoring system")
    print("uses AI to provide smarter analysis and learn from your usage.")
    print()
    
    # Explain smart analysis
    explain_smart_analysis()
    
    # Demo basic analysis
    demo_basic_analysis()
    
    print("\n" + "="*60 + "\n")
    
    # Demo enhanced analysis
    demo_enhanced_analysis()
    
    print("\n" + "="*60 + "\n")
    
    # Demo specific capabilities
    demo_learning_capabilities()
    print()
    demo_pattern_recognition()
    print()
    demo_intelligent_suggestions()
    
    print("\n" + "="*60 + "\n")
    
    # Show benefits and how to enable
    show_benefits()
    print()
    show_how_to_enable()
    
    print("🎉 Smart Analysis Demo Complete!")
    print("=" * 60)
    print("💡 Enable learning and see how the system gets smarter over time!")


if __name__ == "__main__":
    main()
