#!/usr/bin/env python3
"""
Simple test to verify the pre-built agents work
"""

import sys
import json
import subprocess
from pathlib import Path

def test_agent(agent_name, method, parameters):
    """Test a single agent method."""
    agenthub_agents_dir = Path.home() / ".agenthub" / "agents" / "agentplug"
    agent_dir = agenthub_agents_dir / agent_name
    agent_script = agent_dir / "agent.py"
    
    if not agent_script.exists():
        print(f"❌ Agent script not found: {agent_script}")
        return False
    
    input_data = {
        "method": method,
        "parameters": parameters
    }
    
    try:
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(agent_dir)
        )
        
        print(f"Agent: {agent_name}")
        print(f"Method: {method}")
        print(f"Parameters: {parameters}")
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        print("-" * 50)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error testing {agent_name}: {e}")
        return False

def main():
    """Test all pre-built agents."""
    print("🧪 Testing Pre-built AgentHub Agents")
    print("=" * 50)
    
    # Test coding agent
    success1 = test_agent("coding-agent", "generate_code", {"prompt": "hello world"})
    
    # Test analysis agent
    success2 = test_agent("analysis-agent", "analyze_text", {"text": "test", "analysis_type": "general"})
    
    # Test scientific paper analyzer
    success3 = test_agent("scientific-paper-analyzer", "analyze_paper", {"paper_path": "test.pdf"})
    
    print(f"\nResults:")
    print(f"Coding Agent: {'✅' if success1 else '❌'}")
    print(f"Analysis Agent: {'✅' if success2 else '❌'}")
    print(f"Scientific Agent: {'✅' if success3 else '❌'}")

if __name__ == "__main__":
    main()
