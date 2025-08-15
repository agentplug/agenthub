#!/usr/bin/env python3
"""
Core Module Unified Interface: Work with AI agents like native Python objects.

USER BREAKTHROUGH: "I want to use AI agents as easily as calling regular Python functions,
without worrying about complex setup or technical details."

SOLUTION: AgentHub's Core Module provides a unified interface where agents become
native Python objects with magic method support - just call agent.method_name()!
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
    """Demonstrate the unified agent interface and magic methods."""
    print("🎯 Core Module: Unified Agent Interface")
    print("=" * 45)
    print("Use AI agents like native Python objects!")
    print()

    # Initialize the complete system
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)
    loader = AgentLoader(storage=storage)

    # Check if agents are available
    agents = loader.discover_agents()
    if not agents:
        print("❌ No agents found! Please set up seed agents first.")
        return

    print("🚀 BREAKTHROUGH: Magic Method Interface")
    print("-" * 40)
    print("Call AI agents like regular Python functions!")
    print()

    try:
        # Load and wrap agents
        coding_info = loader.load_agent("agentplug", "coding-agent")
        coding_agent = AgentWrapper(coding_info, runtime=runtime)

        analysis_info = loader.load_agent("agentplug", "analysis-agent")
        analysis_agent = AgentWrapper(analysis_info, runtime=runtime)

        print(f"📦 Loaded agents: {coding_agent.name} and {analysis_agent.name}")
        print()

        # Scenario 1: Direct method calls (magic methods)
        print("1. 🪄 Magic Method Execution")
        print("   Just call: agent.method_name(parameters)")
        print()

        # Generate code using magic method
        print("   💻 Generating API client code...")
        code_result = coding_agent.generate_code(
            prompt="Create a REST API client class with GET and POST methods"
        )

        if "result" in code_result:
            generated_code = code_result["result"]
            print(f"   ✅ Generated {len(generated_code)} characters of code!")
            print("   📄 Code preview:")
            lines = generated_code.split("\n")[:8]
            for line in lines:
                print(f"      {line}")
            print("      ... (complete implementation)")
        else:
            print(f"   ❌ Error: {code_result.get('error')}")

        print()
        input("   Press Enter to continue...")
        print()

        # Scenario 2: Analyze the generated code
        print("2. 🔍 Cross-Agent Workflow")
        print("   Chain multiple agents seamlessly")
        print()

        if "result" in code_result:
            print("   📊 Analyzing the generated code...")
            analysis_result = analysis_agent.analyze_text(
                text=generated_code, analysis_type="code_quality"
            )

            if "result" in analysis_result:
                print("   ✅ Analysis complete!")
                analysis = analysis_result["result"]
                if isinstance(analysis, dict):
                    for key, value in analysis.items():
                        if key == "result":
                            print(f"   📋 {key}: {str(value)[:100]}...")
                        else:
                            print(f"   📋 {key}: {value}")
                else:
                    print(f"   📋 Analysis: {str(analysis)[:200]}...")
            else:
                print(f"   ❌ Analysis error: {analysis_result.get('error')}")

        print()
        input("   Press Enter to continue...")
        print()

        # Scenario 3: Method introspection
        print("3. 🔍 Agent Introspection")
        print("   Discover capabilities dynamically")
        print()

        print(f"   🤖 {coding_agent.name} capabilities:")
        print(f"      Available methods: {coding_agent.methods}")
        print(f"      Has generate_code: {coding_agent.has_method('generate_code')}")
        print(f"      Has invalid_method: {coding_agent.has_method('invalid_method')}")

        # Get detailed method info
        try:
            method_info = coding_agent.get_method_info("generate_code")
            print(f"      Method description: {method_info.get('description', 'N/A')}")
        except Exception as e:
            print(f"      Method info error: {e}")

        print()

        print(f"   🤖 {analysis_agent.name} capabilities:")
        print(f"      Available methods: {analysis_agent.methods}")
        for method in analysis_agent.methods[:2]:  # Show first 2 methods
            try:
                info = analysis_agent.get_method_info(method)
                print(f"      {method}: {info.get('description', 'No description')}")
            except Exception:
                print(f"      {method}: Error getting info")

        print()
        input("   Press Enter to continue...")
        print()

        # Scenario 4: Agent composition
        print("4. 🔗 Agent Composition")
        print("   Combine multiple agents for complex workflows")
        print()

        print("   🎯 Workflow: Idea → Code → Documentation → Analysis")

        # Step 1: Generate code for a specific task
        idea = "Create a function to validate email addresses"
        print(f"   💡 Idea: {idea}")

        code = coding_agent.generate_code(prompt=idea)
        if "result" not in code:
            print(f"   ❌ Code generation failed: {code.get('error')}")
            return

        print(f"   ✅ Code generated ({len(code['result'])} chars)")

        # Step 2: Create documentation
        doc_prompt = f"Document this code:\n{code['result']}"
        documentation = analysis_agent.summarize_content(content=doc_prompt)

        if "result" in documentation:
            print(f"   ✅ Documentation created: {documentation['result'][:100]}...")
        else:
            print(f"   ❌ Documentation failed: {documentation.get('error')}")

        # Step 3: Analyze code quality
        quality_analysis = analysis_agent.analyze_text(
            text=code["result"], analysis_type="code_quality"
        )

        if "result" in quality_analysis:
            print("   ✅ Quality analysis complete")
        else:
            print(f"   ❌ Quality analysis failed: {quality_analysis.get('error')}")

        print()

        # Scenario 5: Error handling demonstration
        print("5. 🛡️ Robust Error Handling")
        print("   Graceful handling of various error scenarios")
        print()

        # Test invalid method
        try:
            result = coding_agent.invalid_method(test="parameter")
            print(f"   Unexpected success: {result}")
        except AttributeError as e:
            print(f"   ✅ Invalid method caught: {e}")

        # Test method validation
        try:
            info = coding_agent.get_method_info("nonexistent_method")
            print(f"   Unexpected info: {info}")
        except Exception as e:
            print(f"   ✅ Method validation works: {type(e).__name__}")

        print()

        # Summary of capabilities
        print("🎯 CORE MODULE CAPABILITIES DEMONSTRATED:")
        print("=" * 50)
        print("✅ Magic method interface - agent.method_name()")
        print("✅ Seamless cross-agent workflows")
        print("✅ Dynamic method discovery and introspection")
        print("✅ Agent composition for complex tasks")
        print("✅ Robust error handling and validation")
        print("✅ Native Python object experience")
        print("✅ No complex setup or configuration needed")
        print()

        print("💡 BUSINESS IMPACT:")
        print("🚀 Transform AI from complex APIs into simple function calls")
        print("⚡ Rapid prototyping and development acceleration")
        print("🔗 Easy integration into existing Python workflows")
        print("🛡️ Enterprise-grade reliability and error handling")
        print("📈 Scale AI capabilities across entire organization")

    except Exception as e:
        print(f"❌ Error in demonstration: {e}")


if __name__ == "__main__":
    main()
