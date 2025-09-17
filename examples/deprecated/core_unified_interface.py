import agenthub as ah


def main():
    """Demonstrate the unified agent interface and magic methods."""
    print("🎯 Core Module: Unified Agent Interface")
    print("=" * 45)
    print("Use AI agents like native Python objects!")
    print()

    # Load agents
    coding_agent = ah.load_agent("agentplug/coding-agent")
    analysis_agent = ah.load_agent("agentplug/analysis-agent")

    print(f"📦 Loaded agents: {coding_agent.name} and {analysis_agent.name}")
    print()

    # Scenario 1: Direct method calls
    print("1. 🪄 Magic Method Execution")
    print("   Just call: agent.method_name(parameters)")
    print()

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

    # Scenario 2: Cross-agent workflow
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
                    print(f"      {key}: {value}")
            else:
                print(f"      {analysis}")
        else:
            print(f"   ❌ Analysis failed: {analysis_result.get('error')}")

    print()
    input("   Press Enter to continue...")
    print()

    # Scenario 3: Method discovery
    print("3. 🔍 Dynamic Method Discovery")
    print("   Introspect agent capabilities at runtime")
    print()

    print(f"   🤖 {coding_agent.name} capabilities:")
    print(f"      Available methods: {coding_agent.methods}")
    for method in coding_agent.methods[:2]:
        try:
            info = coding_agent.get_method_info(method)
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

    # Generate code
    idea = "Create a function to validate email addresses"
    print(f"   💡 Idea: {idea}")

    code = coding_agent.generate_code(prompt=idea)
    if "result" not in code:
        print(f"   ❌ Code generation failed: {code.get('error')}")
        return

    print(f"   ✅ Code generated ({len(code['result'])} chars)")

    # Create documentation
    doc_prompt = f"Document this code:\n{code['result']}"
    documentation = analysis_agent.summarize_content(content=doc_prompt)

    if "result" in documentation:
        print(f"   ✅ Documentation created: {documentation['result'][:100]}...")
    else:
        print(f"   ❌ Documentation failed: {documentation.get('error')}")

    # Analyze code quality
    quality_analysis = analysis_agent.analyze_text(
        text=code["result"], analysis_type="code_quality"
    )

    if "result" in quality_analysis:
        print("   ✅ Quality analysis complete")
    else:
        print(f"   ❌ Quality analysis failed: {quality_analysis.get('error')}")

    print()

    # Scenario 5: Error handling
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

    # Summary
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


if __name__ == "__main__":
    main()
