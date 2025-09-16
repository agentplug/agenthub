import agenthub as ah


def main():
    """Demonstrate code generation workflow solving real user pain points."""
    print("💡 Code Generation Workflow")
    print("=" * 40)
    print("Transform your ideas into working code in seconds!")
    print()

    # Load coding agent
    try:
        coding_agent = ah.load_agent("agentplug/coding-agent")
    except Exception as e:
        print(f"❌ Coding agent not found: {e}")
        print("💡 Please set up seed agents first.")
        return

    # Real-world scenarios users face daily
    scenarios = [
        {
            "title": "🚀 API Client Creation",
            "pain_point": "Need REST API client with proper error handling",
            "prompt": "Create Python class for REST API calls with error handling",
            "value": "Saves hours of research and debugging",
        },
        {
            "title": "📊 Data Processing Pipeline",
            "pain_point": "Need to process CSV data but struggling with pandas syntax",
            "prompt": "Create function to read CSV, filter and export data",
            "value": "Eliminates need to search documentation",
        },
        {
            "title": "🔐 Input Validation System",
            "pain_point": "Need secure input validation with best practices",
            "prompt": "Create input validation class for email, phone, password",
            "value": "Prevents security vulnerabilities",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   Pain Point: {scenario['pain_point']}")
        print(f"   Business Value: {scenario['value']}")
        print()

        try:
            # Generate code solution
            print("   🔧 Generating solution...")
            result = coding_agent.generate_code(prompt=scenario["prompt"])

            if "result" in result:
                print("   ✅ Code generated successfully!")

                # Show first part of generated code
                code = result["result"]
                lines = code.split("\n")
                preview_lines = lines[:15]  # Show first 15 lines

                print("   📝 Generated Code Preview:")
                print("   " + "-" * 35)
                for line in preview_lines:
                    print(f"   {line}")

                if len(lines) > 15:
                    print(f"   ... ({len(lines) - 15} more lines)")

                print("   " + "-" * 35)

                # Get explanation
                print("   💭 Getting code explanation...")
                explanation_result = coding_agent.explain_code(code=code)

                if "result" in explanation_result:
                    explanation = explanation_result["result"]
                    print("   📚 Code Explanation:")
                    print("   " + "-" * 25)
                    print(f"   {explanation}")
                    print("   " + "-" * 25)
                else:
                    print(
                        f"   ❌ Explanation failed: {explanation_result.get('error')}"
                    )

                print("   🔍 Validating code...")
                validation_result = coding_agent.validate_code(
                    code=code, criteria="Handle edge cases."
                )
                print(f"   ✅ Code validation: {validation_result['result']}")

            else:
                print(f"   ❌ Code generation failed: {result.get('error')}")

        except Exception as e:
            print(f"   💥 Error during code generation: {e}")

        print()
        input("   Press Enter to continue to next scenario...")
        print()

    # Summary of capabilities
    print("🎯 CODE GENERATION CAPABILITIES DEMONSTRATED:")
    print("=" * 50)
    print("✅ API client creation with error handling")
    print("✅ Data processing pipelines with pandas")
    print("✅ Input validation systems with security")
    print("✅ Clean, documented code generation")
    print("✅ Code explanations and best practices")
    print("✅ Multiple programming languages support")
    print()

    print("💼 BUSINESS VALUE:")
    print("🚀 Transform ideas into working code in seconds")
    print("⚡ Follow security and performance best practices automatically")
    print("🔧 Eliminate blank page syndrome and reduce development time")
    print("📚 Get explanations to learn while building")
    print("⏰ Save hours of coding, research, and debugging time")

    print("\n🚀 MORE USE CASES:")
    print("• Database query builders")
    print("• Configuration file generators")
    print("• Test case generation")
    print("• Documentation templates")
    print("• Deployment scripts")
    print("• Data transformation functions")


if __name__ == "__main__":
    main()
