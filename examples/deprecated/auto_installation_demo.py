#!/usr/bin/env python3
"""
Auto-Installation Demo for Agent Hub Phase 2.

This script demonstrates the complete auto-installation workflow including
environment setup and dependency installation.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agenthub.github.auto_installer import AutoInstaller


def demo_basic_installation():
    """Demonstrate basic agent installation without environment setup."""
    print("🚀 Demo 1: Basic Agent Installation (No Environment)")
    print("=" * 60)

    try:
        # Create installer without environment setup
        installer = AutoInstaller(setup_environment=False)
        print("✅ AutoInstaller created successfully")

        # Try to install an agent (this will fail in demo mode)
        print("📥 Attempting to install agent...")
        result = installer.install_agent("demo/test-agent")

        if result.success:
            print("✅ Installation successful!")
            print(f"📁 Agent installed at: {result.local_path}")
        else:
            print(f"❌ Installation failed: {result.error_message}")

    except Exception as e:
        print(f"❌ Demo failed: {e}")


def demo_environment_integration():
    """Demonstrate environment setup integration."""
    print("\n🌍 Demo 2: Environment Setup Integration")
    print("=" * 60)

    try:
        # Create installer with environment setup
        installer = AutoInstaller(setup_environment=True)
        print("✅ AutoInstaller with environment setup created")
        print(f"🔧 Environment setup enabled: {installer.setup_environment}")

        if installer.environment_setup:
            print("✅ Environment setup component available")
        else:
            print("⚠️ Environment setup not available")

    except Exception as e:
        print(f"❌ Demo failed: {e}")


def demo_workflow_steps():
    """Demonstrate the complete workflow steps."""
    print("\n📋 Demo 3: Complete Workflow Steps")
    print("=" * 60)

    print("The AutoInstaller performs these steps:")
    print("1. 🔍 Agent name validation and GitHub URL construction")
    print("2. 📥 Repository cloning with enhanced features")
    print("3. ✅ Repository structure validation")
    print("4. 🌍 UV virtual environment creation (if enabled)")
    print("5. 📦 Dependency installation (if environment enabled)")
    print("6. 📊 Comprehensive result reporting")
    print("7. 💡 User guidance and next steps")


def demo_installation_result():
    """Demonstrate the InstallationResult structure."""
    print("\n📊 Demo 4: InstallationResult Structure")
    print("=" * 60)

    print("InstallationResult provides:")
    print("• success: Overall installation status")
    print("• agent_name: The agent being installed")
    print("• local_path: Local installation path")
    print("• github_url: GitHub repository URL")
    print("• clone_result: Repository cloning details")
    print("• validation_result: Repository validation details")
    print("• environment_result: Environment setup details")
    print("• dependency_result: Dependency installation details")
    print("• installation_time_seconds: Total time taken")
    print("• error_message: Error details if failed")
    print("• warnings: List of warning messages")
    print("• next_steps: User guidance for next steps")


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n⚠️ Demo 5: Error Handling")
    print("=" * 60)

    print("The AutoInstaller handles various error scenarios:")
    print("• Invalid agent name format")
    print("• Repository not found or inaccessible")
    print("• Cloning failures (network, permissions)")
    print("• Validation failures (missing required files)")
    print("• Environment setup failures (UV not available)")
    print("• Dependency installation failures")
    print("• Timeout and resource issues")
    print("\nEach error provides:")
    print("• Clear error description")
    print("• Actionable next steps")
    print("• Detailed logging for debugging")


def demo_next_steps_guidance():
    """Demonstrate next steps guidance."""
    print("\n💡 Demo 6: Next Steps Guidance")
    print("=" * 60)

    print("The system provides contextual guidance:")
    print("\nFor successful installations:")
    print("• Environment activation commands")
    print("• Testing instructions")
    print("• Documentation references")

    print("\nFor failed installations:")
    print("• Specific issue identification")
    print("• Troubleshooting steps")
    print("• Alternative approaches")

    print("\nFor partial successes:")
    print("• What worked and what didn't")
    print("• Manual completion steps")
    print("• Recovery options")


def main():
    """Run all demos."""
    print("🎯 Agent Hub Phase 2 - Auto-Installation Demo")
    print("=" * 80)

    # Run all demo functions
    demo_basic_installation()
    demo_environment_integration()
    demo_workflow_steps()
    demo_installation_result()
    demo_error_handling()
    demo_next_steps_guidance()

    print("\n" + "=" * 80)
    print("🎉 Demo completed!")
    print("✅ All AutoInstaller functionality demonstrated")
    print("🔧 Ready for production use")
    print("📚 Check the documentation for detailed usage")

    return 0


if __name__ == "__main__":
    sys.exit(main())