#!/usr/bin/env python3
"""
Error Handling Demo

Demonstrates the improved error handling in AgentWrapper that shows
available methods when users call non-existent methods.
"""

import agenthub as amg


def demonstrate_error_handling():
    """Demonstrate the improved error handling capabilities."""
    print("🤖 Agent Error Handling Demonstration")
    print("=" * 60)

    # Load agents
    coding_agent = amg.load_agent("agentplug/coding-agent")
    analysis_agent = amg.load_agent("agentplug/analysis-agent")

    print("✅ Agents loaded successfully!")
    print(f"📝 coding-agent methods: {coding_agent.methods}")
    print(f"📊 analysis-agent methods: {analysis_agent.methods}")

    print("\n" + "=" * 60)
    print("❌ Testing Error Handling for Non-existent Methods:")
    print("=" * 60)

    # Test 1: Call non-existent method on coding-agent
    print("\n1️⃣ Testing coding-agent.analyze_requirements():")
    try:
        result = coding_agent.analyze_requirements("Some requirements")
        print(f"   Result: {result}")
    except AttributeError as e:
        print(f"   ❌ Error caught: {e}")

    # Test 2: Call non-existent method on analysis-agent
    print("\n2️⃣ Testing analysis_agent.generate_code():")
    try:
        result = analysis_agent.generate_code("Create a function")
        print(f"   Result: {result}")
    except AttributeError as e:
        print(f"   ❌ Error caught: {e}")

    # Test 3: Call method with similar name (case sensitivity)
    print("\n3️⃣ Testing coding-agent.Generate_code() (wrong case):")
    try:
        result = coding_agent.Generate_code("Create a function")
        print(f"   Result: {result}")
    except AttributeError as e:
        print(f"   ❌ Error caught: {e}")

    # Test 4: Call method with completely wrong name
    print("\n4️⃣ Testing coding_agent.some_random_method():")
    try:
        result = coding_agent.some_random_method("Some data")
        print(f"   Result: {result}")
    except AttributeError as e:
        print(f"   ❌ Error caught: {e}")

    # Test 5: Call method that sounds similar
    print("\n5️⃣ Testing coding_agent.analyze_text() (wrong agent):")
    try:
        result = coding_agent.analyze_text("Some text to analyze")
        print(f"   Result: {result}")
    except AttributeError as e:
        print(f"   ❌ Error caught: {e}")

    print("\n" + "=" * 60)
    print("✅ Now let's test correct method calls:")
    print("=" * 60)

    # Test correct methods to show they still work
    print("\n6️⃣ Testing coding-agent.generate_code() (correct method):")
    try:
        result = coding_agent.generate_code("Create a simple function")
        print(f"   ✅ Success! Generated {len(result['result'])} characters")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    print("\n7️⃣ Testing analysis_agent.analyze_text() (correct method):")
    try:
        result = analysis_agent.analyze_text("This is a test text")
        print("   ✅ Success! Analysis completed")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    print("\n" + "=" * 60)
    print("🎯 Key Benefits of Improved Error Handling:")
    print("=" * 60)
    print("✅ Shows available methods when errors occur")
    print("✅ Provides method descriptions for better understanding")
    print("✅ Suggests similar method names when possible")
    print("✅ Makes debugging much easier for developers")
    print("✅ Professional and user-friendly error messages")
    print("✅ Helps users discover agent capabilities")


if __name__ == "__main__":
    demonstrate_error_handling()
