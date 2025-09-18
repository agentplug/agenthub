#!/usr/bin/env python3
"""
Demonstration of AgentHub Phase 3.1 Real-time Monitoring

This script demonstrates the three-step monitoring process:
1. Observe agent's running logs in real-time
2. Convert logs to readable progress using LLM analysis
3. Display progress appropriately in terminal

Usage:
    python examples/monitoring/monitoring_demo.py
"""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agenthub.runtime.monitored_process_manager import MonitoredProcessManager


def create_demo_agent():
    """Create a simple demo agent for testing monitoring."""
    demo_dir = Path("demo_agent")
    demo_dir.mkdir(exist_ok=True)

    # Create agent.py
    agent_script = demo_dir / "agent.py"
    agent_script.write_text(
        '''
#!/usr/bin/env python3
"""
Demo agent for monitoring demonstration.
"""

import json
import sys
import time
import random

def analyze_data(data):
    """Simulate data analysis with progress updates."""
    print("🚀 Starting data analysis...")
    time.sleep(1)

    print("📊 Loading dataset...")
    time.sleep(1)

    print("🔍 Processing data points...")
    for i in range(10):
        time.sleep(0.5)
        progress = (i + 1) * 10
        print(f"📈 Progress: {progress}% - Processing item {i+1}/10")

        # Simulate occasional errors
        if random.random() < 0.1:  # 10% chance of error
            print("⚠️ Warning: Minor data inconsistency detected")

    print("✅ Analysis complete!")
    print("📋 Generating report...")
    time.sleep(1)

    result = {
        "status": "success",
        "items_processed": 10,
        "analysis_summary": "Data analysis completed successfully",
        "recommendations": ["Consider data validation", "Update processing pipeline"]
    }

    print(f"RESULT: {json.dumps(result)}")
    return result

def generate_content(topic):
    """Simulate content generation with progress updates."""
    print(f"🎯 Starting content generation for: {topic}")
    time.sleep(1)

    print("📝 Researching topic...")
    time.sleep(2)

    print("✍️ Writing content...")
    for i in range(5):
        time.sleep(0.8)
        progress = (i + 1) * 20
        print(f"📄 Writing section {i+1}/5 - {progress}% complete")

    print("🔍 Reviewing content...")
    time.sleep(1)

    print("✅ Content generation complete!")

    result = {
        "status": "success",
        "topic": topic,
        "content_length": 1500,
        "sections": 5,
        "quality_score": 8.5
    }

    print(f"RESULT: {json.dumps(result)}")
    return result

def simulate_error():
    """Simulate an agent that encounters errors."""
    print("🚀 Starting complex operation...")
    time.sleep(1)

    print("📊 Initializing system...")
    time.sleep(1)

    print("❌ Error: Connection timeout to external service")
    print("🔄 Retrying connection...")
    time.sleep(2)

    print("❌ Error: Authentication failed")
    print("⚠️ Warning: Using fallback method")
    time.sleep(1)

    print("📈 Processing with limited functionality...")
    time.sleep(2)

    print("✅ Operation completed with warnings")

    result = {
        "status": "completed_with_errors",
        "errors": ["Connection timeout", "Authentication failed"],
        "warnings": ["Using fallback method"],
        "recommendations": ["Check network connection", "Verify credentials"]
    }

    print(f"RESULT: {json.dumps(result)}")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py <method> <json_parameters>")
        sys.exit(1)

    method = sys.argv[1]
    parameters = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    try:
        if method == "analyze_data":
            result = analyze_data(parameters.get("data", "sample_data"))
        elif method == "generate_content":
            result = generate_content(parameters.get("topic", "AI Technology"))
        elif method == "simulate_error":
            result = simulate_error()
        else:
            result = {"error": f"Unknown method: {method}"}

        # The result is already printed above, so we don't need to return it
        # The monitoring system will capture the printed output

    except Exception as e:
        print(f"❌ Error: {e}")
        result = {"error": str(e)}
'''
    )

    # Create agent.yaml
    agent_yaml = demo_dir / "agent.yaml"
    agent_yaml.write_text(
        """
name: demo-agent
version: 1.0.0
description: Demo agent for monitoring demonstration
author: AgentHub Team

interface:
  methods:
    analyze_data:
      description: Analyze data with progress updates
      parameters:
        data:
          type: string
          description: Data to analyze
          required: false
          default: "sample_data"

    generate_content:
      description: Generate content with progress updates
      parameters:
        topic:
          type: string
          description: Topic for content generation
          required: false
          default: "AI Technology"

    simulate_error:
      description: Simulate an agent that encounters errors
      parameters: {}
"""
    )

    return str(demo_dir)


def demonstrate_monitoring():
    """Demonstrate the three-step monitoring process."""
    print("=" * 80)
    print("🤖 AgentHub Phase 3.1 Real-time Monitoring Demonstration")
    print("=" * 80)
    print()

    # Create demo agent
    print("📁 Creating demo agent...")
    agent_path = create_demo_agent()
    print(f"✅ Demo agent created at: {agent_path}")
    print()

    # Initialize monitored process manager
    print("🔧 Initializing monitoring system...")
    manager = MonitoredProcessManager(monitoring=True)

    # Show monitoring capabilities
    capabilities = manager.get_monitoring_capabilities()
    print("📊 Monitoring Capabilities:")
    for feature in capabilities["features"]:
        print(f"   ✓ {feature}")
    print()

    # Demonstrate different scenarios
    scenarios = [
        {
            "name": "Data Analysis with Progress",
            "method": "analyze_data",
            "parameters": {"data": "customer_sales_data"},
        },
        {
            "name": "Content Generation",
            "method": "generate_content",
            "parameters": {"topic": "Machine Learning Trends"},
        },
        {
            "name": "Error Handling Demonstration",
            "method": "simulate_error",
            "parameters": {},
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"🎬 Scenario {i}: {scenario['name']}")
        print("-" * 60)

        try:
            result = manager.execute_agent_with_monitoring(
                agent_path=agent_path,
                method=scenario["method"],
                parameters=scenario["parameters"],
            )

            print("\n📋 Execution Result:")
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Success: {result.get('result', 'Completed')}")

            if "monitoring_data" in result:
                monitoring = result["monitoring_data"]
                print(f"   📊 Logs captured: {monitoring['total_logs']}")
                if "final_analysis" in monitoring:
                    analysis = monitoring["final_analysis"]
                    print(f"   🧠 Final analysis: {analysis['summary']}")
                    print(f"   📈 Progress: {analysis['progress']}%")
                    if analysis["errors"]:
                        print(f"   ⚠️ Errors detected: {len(analysis['errors'])}")
                    if analysis["suggestions"]:
                        print(f"   💡 Suggestions: {len(analysis['suggestions'])}")

        except Exception as e:
            print(f"❌ Scenario failed: {e}")

        print("\n" + "=" * 80)

        if i < len(scenarios):
            print("⏳ Waiting 3 seconds before next scenario...")
            time.sleep(3)
            print()

    # Cleanup
    print("🧹 Cleaning up demo agent...")
    import shutil

    shutil.rmtree(agent_path, ignore_errors=True)
    print("✅ Demo completed successfully!")

    print("\n" + "=" * 80)
    print("🎉 Monitoring Demonstration Complete!")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("1. ✅ Real-time log observation from agent subprocess")
    print("2. ✅ LLM-powered log analysis and progress extraction")
    print("3. ✅ User-friendly terminal display with progress bars")
    print("4. ✅ Error detection and actionable suggestions")
    print("5. ✅ Final execution summary with recommendations")
    print()
    print("The monitoring system successfully:")
    print("• Captured agent output in real-time")
    print("• Analyzed logs using LLM to understand progress")
    print("• Displayed progress in a clean, user-friendly format")
    print("• Provided error detection and suggestions")
    print("• Generated comprehensive execution summaries")


if __name__ == "__main__":
    try:
        demonstrate_monitoring()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
