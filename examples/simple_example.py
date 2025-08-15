#!/usr/bin/env python3
"""
Simple Example: Load coding agent and generate backpropagation code.

This example shows how easy it is for users to:
1. Load an AI coding agent
2. Generate complex code (backpropagation algorithm)
3. Get production-ready results

USER PERSPECTIVE: "I need to implement backpropagation but I'm not sure about the math.
Let me use AgentHub's coding agent to generate it for me!"
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.core.agent_loader import AgentLoader  # noqa: E402
from agentmanager.core.agent_wrapper import AgentWrapper  # noqa: E402
from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Simple example: Load coding agent and generate backpropagation code."""
    print("🎯 Simple AgentHub Example")
    print("=" * 30)
    print("Generate backpropagation algorithm using AI coding agent")
    print()

    try:
        # Step 1: Initialize AgentHub system (simple setup)
        print("📋 Step 1: Setting up AgentHub...")
        storage = LocalStorage()
        runtime = AgentRuntime(storage=storage)
        loader = AgentLoader(storage=storage)

        # Step 2: Load the coding agent
        print("🤖 Step 2: Loading coding agent...")
        agent_info = loader.load_agent("agentplug", "coding-agent")
        coding_agent = AgentWrapper(agent_info, runtime=runtime)

        print(f"✅ Loaded: {coding_agent.name} v{agent_info.get('version', '1.0.0')}")
        print(f"📋 Available methods: {coding_agent.methods}")
        print()

        # Step 3: Generate backpropagation code
        print("💻 Step 3: Generating backpropagation algorithm...")
        print("🔄 Asking AI to write the code...")

        # Simple prompt - user just describes what they want
        prompt = """
        Create a simple backpropagation algorithm implementation in Python.
        Include:
        - A simple neural network class
        - Forward pass method
        - Backpropagation method with gradient calculation
        - Training loop example
        - Comments explaining the math

        Make it educational and easy to understand.
        """

        # Call the agent using the simple method call
        result = coding_agent.generate_code(prompt=prompt)

        if "result" in result:
            generated_code = result["result"]
            execution_time = result.get("execution_time", 0)

            print(f"✅ Code generated successfully! ({execution_time:.1f}s)")
            print(f"📄 Generated {len(generated_code)} characters of code")
            print()

            # Step 4: Display the generated code
            print("🎉 Step 4: Your Backpropagation Implementation:")
            print("=" * 60)
            print(generated_code)
            print("=" * 60)
            print()

            # Step 5: Explain what happened
            print("🎓 What just happened:")
            print("✅ AgentHub loaded the coding agent automatically")
            print("✅ AI generated a complete backpropagation implementation")
            print("✅ Code includes neural network, training, and comments")
            print("✅ Ready to use in your machine learning projects!")
            print()

            # Bonus: Get explanation of the code
            print("📚 Bonus: Getting code explanation...")
            explanation_result = coding_agent.explain_code(code=generated_code[:500])

            if "result" in explanation_result:
                explanation = explanation_result["result"]
                print("💡 Code Explanation:")
                print("-" * 30)
                print(explanation)
                print()

        else:
            error_msg = result.get("error", "Unknown error")
            print(f"❌ Error generating code: {error_msg}")
            return

        # Step 6: Show how easy it was
        print("🚀 Success! Here's how simple it was:")
        print()
        print("1️⃣ Load agent:   agent = AgentWrapper(agent_info, runtime)")
        print("2️⃣ Call method:  result = agent.generate_code(prompt=your_request)")
        print("3️⃣ Get result:   code = result['result']")
        print()
        print("💡 That's it! No complex APIs, no configuration - just simple Python!")
        print()

        # Show other available capabilities
        print("🎯 Other things you can do with this agent:")
        for method in coding_agent.methods:
            if method != "generate_code":
                print(f"   • agent.{method}() - {method.replace('_', ' ').title()}")

        print()
        print("🎉 Ready to build amazing AI-powered applications!")

    except Exception as e:
        print(f"❌ Error in example: {e}")
        print()
        print("💡 Make sure you have:")
        print("   • AgentHub properly installed")
        print("   • Seed agents set up (coding-agent)")
        print("   • OpenAI API key configured")


if __name__ == "__main__":
    main()
