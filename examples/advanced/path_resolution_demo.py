#!/usr/bin/env python3
"""
Path Resolution Demo - Comprehensive examples of file path handling

This example demonstrates how AgentHub handles different types of file paths
when calling agent methods, ensuring that relative paths work correctly
even when agents run in subprocesses with different working directories.
"""

import os
import tempfile

import agenthub as ah

# Configure logging
ah.set_quiet_mode(True)


def create_test_files():
    """Create test files in different locations for demonstration."""
    test_files = {}

    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp(prefix="agenthub_test_")

    # Create test files
    test_files["current_dir"] = "test_current.txt"
    test_files["temp_dir"] = os.path.join(temp_dir, "test_temp.txt")
    test_files["subdir"] = "test_subdir/test_subdir.txt"

    # Create files
    with open(test_files["current_dir"], "w") as f:
        f.write("Test file in current directory")

    with open(test_files["temp_dir"], "w") as f:
        f.write("Test file in temporary directory")

    # Create subdirectory and file
    os.makedirs("test_subdir", exist_ok=True)
    with open(test_files["subdir"], "w") as f:
        f.write("Test file in subdirectory")

    return test_files, temp_dir


def cleanup_test_files(test_files, temp_dir):
    """Clean up test files."""
    for file_path in test_files.values():
        if os.path.exists(file_path):
            os.remove(file_path)

    # Remove subdirectory
    if os.path.exists("test_subdir"):
        os.rmdir("test_subdir")

    # Remove temp directory
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def demonstrate_path_resolution():
    """Demonstrate different path resolution scenarios."""
    print("🔬 Path Resolution Demonstration")
    print("=" * 50)

    # Create test files
    test_files, temp_dir = create_test_files()

    try:
        # Load an agent
        agent = ah.load_agent("agentplug/analysis-agent")

        print("\n📁 Test Files Created:")
        for name, path in test_files.items():
            print(f"  {name}: {path}")
            print(f"    Absolute: {os.path.abspath(path)}")

        print(f"\n📂 Current Working Directory: {os.getcwd()}")
        print(f"📂 Agent Working Directory: {agent.agent_info.get('path', 'Unknown')}")

        # Test different path scenarios
        test_scenarios = [
            {
                "name": "Relative path in current directory",
                "params": {
                    "text": "Test content",
                    "file_path": test_files["current_dir"],
                },
            },
            {
                "name": "Relative path in subdirectory",
                "params": {"text": "Test content", "file_path": test_files["subdir"]},
            },
            {
                "name": "Absolute path",
                "params": {"text": "Test content", "file_path": test_files["temp_dir"]},
            },
            {
                "name": "Multiple file parameters",
                "params": {
                    "text": "Test content",
                    "input_file": test_files["current_dir"],
                    "output_file": "output.txt",
                    "document": test_files["subdir"],
                },
            },
        ]

        print("\n🧪 Testing Path Resolution Scenarios:")
        print("-" * 50)

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. {scenario['name']}")
            print(f"   Original parameters: {scenario['params']}")

            # Test path resolution
            resolved_params = agent._resolve_file_paths(scenario["params"])
            print(f"   Resolved parameters: {resolved_params}")

            # Show which paths were changed
            changed_paths = []
            for key, value in scenario["params"].items():
                if key in resolved_params and resolved_params[key] != value:
                    changed_paths.append(f"{key}: '{value}' → '{resolved_params[key]}'")

            if changed_paths:
                print(f"   ✅ Paths resolved: {', '.join(changed_paths)}")
            else:
                print("   ℹ️  No paths needed resolution")

        print("\n🎯 Key Benefits of Automatic Path Resolution:")
        print("• ✅ Relative paths work correctly in subprocesses")
        print("• ✅ Code is more portable across different environments")
        print("• ✅ No need to manually convert paths")
        print("• ✅ Supports multiple file parameter types")
        print("• ✅ Maintains backward compatibility with absolute paths")

        print("\n💡 Best Practices:")
        print("• Use relative paths for better portability")
        print("• Place files in project directories when possible")
        print("• Use descriptive parameter names (file_path, document, etc.)")
        print("• Test with both relative and absolute paths")

    finally:
        # Clean up test files
        cleanup_test_files(test_files, temp_dir)
        print("\n🧹 Test files cleaned up")


def show_parameter_detection():
    """Show how the system detects file path parameters."""
    print("\n🔍 File Path Parameter Detection")
    print("=" * 40)

    agent = ah.load_agent("agentplug/analysis-agent")

    # Test different parameter names
    test_params = {
        "text": "Some text content",
        "file_path": "document.pdf",  # ✅ Will be resolved
        "input_file": "input.txt",  # ✅ Will be resolved
        "document": "paper.pdf",  # ✅ Will be resolved
        "paper": "research.pdf",  # ✅ Will be resolved
        "image": "photo.jpg",  # ✅ Will be resolved
        "config_file": "config.yaml",  # ✅ Will be resolved
        "data_file": "data.csv",  # ✅ Will be resolved
        "output_file": "result.txt",  # ✅ Will be resolved
        "source_file": "source.py",  # ✅ Will be resolved
        "target_file": "target.py",  # ✅ Will be resolved
        "video": "movie.mp4",  # ✅ Will be resolved
        "audio": "sound.wav",  # ✅ Will be resolved
        "regular_param": "some_value",  # ❌ Won't be resolved
        "content": "some content",  # ❌ Won't be resolved
        "absolute_path": "/absolute/path.txt",  # ❌ Won't be resolved
    }

    print("Testing parameter detection:")
    resolved_params = agent._resolve_file_paths(test_params)

    for key, original_value in test_params.items():
        resolved_value = resolved_params[key]
        if original_value != resolved_value:
            print(f"  ✅ {key}: '{original_value}' → '{resolved_value}'")
        elif (
            "file" in key.lower()
            or "path" in key.lower()
            or "document" in key.lower()
            or "paper" in key.lower()
        ):
            if os.path.isabs(original_value):
                print(f"  ℹ️  {key}: '{original_value}' (already absolute)")
            else:
                print(f"  ❓ {key}: '{original_value}' (not detected as file path)")


def main():
    """Main demonstration function."""
    print("🚀 AgentHub Path Resolution Demo")
    print("=" * 60)

    demonstrate_path_resolution()
    show_parameter_detection()

    print("\n🎉 Demo completed!")
    print("\n📚 Summary:")
    print("AgentHub automatically resolves relative file paths to absolute paths")
    print("before passing them to agent subprocesses. This ensures that:")
    print("• Your code can use relative paths for better portability")
    print("• Agents can access files correctly regardless of their working directory")
    print("• The system works seamlessly with both relative and absolute paths")


if __name__ == "__main__":
    main()
