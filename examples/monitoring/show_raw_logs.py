#!/usr/bin/env python3
"""
Show raw logs from agent execution without any analysis.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah  # noqa: E402


def show_raw_logs():
    """Show raw logs from agent execution."""
    print("=" * 80)
    print("🔍 Raw Agent Logs Demonstration")
    print("=" * 80)
    print()
    print("This shows the raw logs directly from the agent without any analysis.")
    print()

    try:
        # Load agent with monitoring
        print("🔧 Loading agent with monitoring...")
        agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["multiply", "add"],
            monitoring=True,
        )

        print("✅ Agent loaded successfully!")
        print()

        # Execute agent method
        print("🚀 Executing agent method...")
        question = "Calculate 12 times 5, then add 8"
        print(f"📄 Input: {question}")
        print()

        result = agent.analyze_text(question)

        print("=" * 80)
        print("📋 RAW LOGS FROM AGENT (No Analysis)")
        print("=" * 80)

        if "raw_logs" in result:
            raw_logs = result["raw_logs"]
            print(f"📊 Total raw log lines: {len(raw_logs)}")
            print()

            for i, log_line in enumerate(raw_logs, 1):
                print(f"{i:3d}: {log_line}")
        else:
            print("❌ No raw logs found in result")
            print("Available keys:", list(result.keys()))

        print()
        print("=" * 80)
        print("🎉 Raw Logs Display Complete!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    show_raw_logs()
