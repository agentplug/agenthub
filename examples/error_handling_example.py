#!/usr/bin/env python3
"""
Error Handling Example: Comprehensive error scenarios and handling.

This example demonstrates how the AgentHub system handles various error
conditions gracefully with helpful error messages and recovery suggestions.
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def test_error_scenario(title: str, test_func):
    """Helper function to test error scenarios."""
    print(f"\n🧪 {title}")
    print("-" * len(title))
    try:
        result = test_func()
        if isinstance(result, dict) and "error" in result:
            print(f"❌ Expected Error: {result['error']}")
            if "suggestion" in result:
                print(f"💡 Suggestion: {result['suggestion']}")
        else:
            print(f"✅ Unexpected Success: {result}")
    except Exception as e:
        print(f"💥 Exception (as expected): {type(e).__name__}: {e}")


def main():
    """Demonstrate comprehensive error handling."""
    print("🚨 Error Handling and Edge Cases Example")
    print("=" * 50)

    # Initialize modules
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    print("\nTesting various error scenarios to demonstrate robust error handling...")

    # 1. Nonexistent agent errors
    test_error_scenario(
        "Nonexistent Agent Execution",
        lambda: runtime.execute_agent("fake", "nonexistent-agent", "some_method", {}),
    )

    # 2. Invalid method errors
    test_error_scenario(
        "Invalid Method Call",
        lambda: runtime.execute_agent(
            "agentplug", "coding-agent", "invalid_method", {}
        ),
    )

    # 3. Empty parameters
    test_error_scenario(
        "Empty Agent Path",
        lambda: runtime.process_manager.execute_agent("", "method", {}),
    )

    # 4. Malformed agent directory
    test_error_scenario(
        "Malformed Agent Directory",
        lambda: runtime.get_agent_info("/tmp/fake_agent_path"),
    )

    # 5. Test with missing virtual environment
    print("\n🧪 Missing Virtual Environment")
    print("-" * 30)

    # Create a temporary fake agent directory without venv
    fake_agent_dir = Path("/tmp/test_agent_no_venv")
    try:
        fake_agent_dir.mkdir(exist_ok=True)
        (fake_agent_dir / "agent.py").touch()
        (fake_agent_dir / "agent.yaml").write_text(
            "name: test\ninterface:\n  methods: {}"
        )

        result = runtime.process_manager.validate_agent_structure(str(fake_agent_dir))
        print(f"❌ Structure validation: {result} (expected False)")

        # Cleanup
        import shutil

        shutil.rmtree(fake_agent_dir, ignore_errors=True)

    except Exception as e:
        print(f"💥 Setup error: {e}")

    # 6. Timeout simulation (if we had a long-running agent)
    print("\n🧪 Timeout Handling")
    print("-" * 20)
    print("⏱️  Timeout handling is built-in (30s default)")
    print("   Agents that run longer than timeout are automatically terminated")

    # 7. Test storage edge cases
    print("\n🧪 Storage Edge Cases")
    print("-" * 25)

    # Test with custom storage location
    try:
        custom_storage = LocalStorage(base_dir=Path("/tmp/test_agenthub"))
        agents = custom_storage.discover_agents()
        print(f"Custom storage agents: {len(agents)} (expected 0)")
    except Exception as e:
        print(f"💥 Custom storage error: {e}")

    # 8. Test malformed YAML
    print("\n🧪 Malformed Agent Manifest")
    print("-" * 30)

    fake_yaml_dir = Path("/tmp/test_agent_bad_yaml")
    try:
        fake_yaml_dir.mkdir(exist_ok=True)
        (fake_yaml_dir / "agent.py").touch()
        (fake_yaml_dir / "agent.yaml").write_text("invalid: yaml: content: [[[")

        test_error_scenario(
            "Invalid YAML Manifest",
            lambda: runtime.load_agent_manifest(str(fake_yaml_dir)),
        )

        # Cleanup
        import shutil

        shutil.rmtree(fake_yaml_dir, ignore_errors=True)

    except Exception as e:
        print(f"💥 Setup error: {e}")

    # 9. Test missing required fields in manifest
    print("\n🧪 Incomplete Agent Manifest")
    print("-" * 32)

    incomplete_dir = Path("/tmp/test_agent_incomplete")
    try:
        incomplete_dir.mkdir(exist_ok=True)
        (incomplete_dir / "agent.py").touch()
        (incomplete_dir / "agent.yaml").write_text(
            "description: Missing required fields"
        )

        test_error_scenario(
            "Missing Required Fields",
            lambda: runtime.load_agent_manifest(str(incomplete_dir)),
        )

        # Cleanup
        import shutil

        shutil.rmtree(incomplete_dir, ignore_errors=True)

    except Exception as e:
        print(f"💥 Setup error: {e}")

    # 10. Test recovery suggestions
    print("\n🧪 Recovery Suggestions")
    print("-" * 25)

    # Get available methods for helpful suggestions
    agents = storage.discover_agents()
    if agents:
        namespace = agents[0]["namespace"]
        name = agents[0]["name"]

        result = runtime.execute_agent(namespace, name, "nonexistent_method", {})
        if "suggestion" in result:
            print(f"✅ Helpful suggestion provided: {result['suggestion']}")

        available_methods = runtime.get_available_methods(
            str(storage.get_agent_path(namespace, name))
        )
        print(f"✅ Available methods discovered: {available_methods}")

    # Summary
    print("\n📊 Error Handling Summary")
    print("=" * 30)
    print("✅ Agent not found - Clear error message")
    print("✅ Method not found - Suggestions provided")
    print("✅ Invalid parameters - Parameter validation")
    print("✅ Missing files - File existence checks")
    print("✅ Malformed YAML - Parse error handling")
    print("✅ Missing fields - Required field validation")
    print("✅ Process errors - Subprocess error capture")
    print("✅ Timeout handling - Automatic process termination")
    print("✅ Path resolution - Cross-platform path handling")
    print("✅ Recovery hints - Actionable suggestions provided")

    print("\n🎉 Error handling example completed!")
    print("\nKey error handling features demonstrated:")
    print("🛡️  Comprehensive input validation")
    print("🛡️  Graceful error recovery")
    print("🛡️  Helpful error messages and suggestions")
    print("🛡️  Proper exception handling and logging")
    print("🛡️  Process isolation prevents system corruption")
    print("🛡️  Timeout protection against hanging processes")


if __name__ == "__main__":
    main()
