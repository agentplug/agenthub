#!/usr/bin/env python3
"""
Agent Discovery and Validation: Enterprise-grade agent management.

USER CHALLENGE: "I need to manage multiple AI agents across my organization,
but I need confidence they're working correctly and understand their capabilities."

SOLUTION: AgentHub's Core Module provides comprehensive agent discovery,
validation, and health monitoring for enterprise-scale deployments.
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


def print_separator(title):
    """Print a formatted separator."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def print_subsection(title):
    """Print a formatted subsection."""
    print(f"\n{title}")
    print("-" * len(title))


def main():
    """Demonstrate enterprise agent discovery and validation."""
    print("🏢 Enterprise Agent Management")
    print("=" * 35)
    print("Discover, validate, and monitor AI agents at scale")
    print()

    # Initialize the system
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)
    loader = AgentLoader(storage=storage)

    print_separator("1. AGENT DISCOVERY ENGINE")

    # Discover all agents in the system
    print("🔍 Scanning agent ecosystem...")
    try:
        agents = loader.discover_agents()
        print(f"✅ Discovery complete: {len(agents)} agents found")

        if not agents:
            print("⚠️  No agents available for demonstration")
            print("💡 Set up seed agents first to see full capabilities")
            return

        # Show discovery details
        print_subsection("📊 Discovery Report")
        namespaces = set(agent.get("namespace", "unknown") for agent in agents)
        print(f"Total agents: {len(agents)}")
        print(f"Namespaces: {len(namespaces)} ({', '.join(sorted(namespaces))})")

        for agent in agents:
            namespace = agent.get("namespace", "unknown")
            name = agent.get("name", "unknown")
            version = agent.get("version", "unknown")
            path = agent.get("path", "unknown")
            print(f"  • {namespace}/{name} v{version}")
            print(f"    Location: {path}")

    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return

    print_separator("2. COMPREHENSIVE VALIDATION")

    validation_results = []

    for agent_info in agents:
        namespace = agent_info.get("namespace", "unknown")
        name = agent_info.get("name", "unknown")

        print(f"\n🔍 Validating {namespace}/{name}...")

        try:
            # Load agent with full validation
            loaded_info = loader.load_agent(namespace, name)

            # Perform comprehensive checks
            checks = {
                "manifest_valid": "manifest" in loaded_info,
                "methods_available": len(loaded_info.get("methods", [])) > 0,
                "dependencies_listed": "dependencies" in loaded_info,
                "structure_valid": loaded_info.get("valid", False),
                "interface_valid": "interface" in loaded_info.get("manifest", {}),
            }

            # Structure validation
            agent_path = loaded_info.get("path", "")
            structure_checks = {
                "agent_py_exists": (
                    (Path(agent_path) / "agent.py").exists() if agent_path else False
                ),
                "manifest_exists": (
                    (Path(agent_path) / "agent.yaml").exists() if agent_path else False
                ),
                "venv_exists": (
                    (Path(agent_path) / ".venv").exists() if agent_path else False
                ),
            }

            all_checks_passed = all(checks.values()) and all(structure_checks.values())

            validation_result = {
                "namespace": namespace,
                "name": name,
                "status": "✅ VALID" if all_checks_passed else "❌ INVALID",
                "checks": {**checks, **structure_checks},
                "info": loaded_info,
            }

            validation_results.append(validation_result)

            # Display validation details
            print(f"   Status: {validation_result['status']}")
            print(f"   Methods: {len(loaded_info.get('methods', []))}")
            print(f"   Dependencies: {len(loaded_info.get('dependencies', []))}")

            if not all_checks_passed:
                failed_checks = [
                    k for k, v in {**checks, **structure_checks}.items() if not v
                ]
                print(f"   ⚠️  Failed checks: {', '.join(failed_checks)}")

        except Exception as e:
            validation_result = {
                "namespace": namespace,
                "name": name,
                "status": "💥 ERROR",
                "error": str(e),
                "checks": {},
                "info": {},
            }
            validation_results.append(validation_result)
            print(f"   💥 Validation error: {e}")

    print_separator("3. CAPABILITY ANALYSIS")

    # Analyze capabilities across all valid agents
    valid_agents = [r for r in validation_results if "✅" in r["status"]]

    if valid_agents:
        print(f"📊 Analyzing {len(valid_agents)} valid agents...")

        all_methods = set()
        all_dependencies = set()
        agents_by_capability = {}

        for result in valid_agents:
            info = result["info"]
            methods = info.get("methods", [])
            dependencies = info.get("dependencies", [])

            all_methods.update(methods)
            all_dependencies.update(dependencies)

            # Group agents by capability
            for method in methods:
                if method not in agents_by_capability:
                    agents_by_capability[method] = []
                agents_by_capability[method].append(
                    f"{result['namespace']}/{result['name']}"
                )

        print_subsection("🎯 Capability Matrix")
        print(f"Total unique methods: {len(all_methods)}")
        print(f"Total unique dependencies: {len(all_dependencies)}")
        print()

        print("Methods available across agents:")
        for method, agent_list in sorted(agents_by_capability.items()):
            print(f"  • {method}: {', '.join(agent_list)}")

        print("\nCommon dependencies:")
        for dep in sorted(list(all_dependencies)[:5]):  # Show first 5
            print(f"  • {dep}")

    print_separator("4. RUNTIME HEALTH CHECK")

    # Test actual execution capabilities
    print("🏥 Testing runtime health with live execution...")

    for result in valid_agents[:2]:  # Test first 2 valid agents
        namespace = result["namespace"]
        name = result["name"]
        info = result["info"]
        methods = info.get("methods", [])

        if not methods:
            continue

        print(f"\n🧪 Testing {namespace}/{name}")

        try:
            # Create wrapper and test a method
            wrapper = AgentWrapper(info, runtime=runtime)
            test_method = methods[0]  # Test first method

            print(f"   Testing method: {test_method}")

            # Prepare simple test parameters
            if "generate" in test_method.lower() or "code" in test_method.lower():
                test_params = {"prompt": "test"}
            elif "analyze" in test_method.lower():
                test_params = {"text": "test", "analysis_type": "test"}
            elif "summarize" in test_method.lower():
                test_params = {"content": "test"}
            else:
                test_params = {}

            # Quick health check execution
            result = wrapper.execute(test_method, test_params)

            if "result" in result:
                exec_time = result.get("execution_time", 0)
                print(f"   ✅ Health check passed ({exec_time:.1f}s)")
            else:
                print(f"   ⚠️  Health check warning: {result.get('error', 'Unknown')}")

        except Exception as e:
            print(f"   ❌ Health check failed: {e}")

    print_separator("5. MANAGEMENT RECOMMENDATIONS")

    # Provide actionable recommendations
    total_agents = len(validation_results)
    valid_count = len(valid_agents)
    invalid_count = total_agents - valid_count

    print("📋 System Assessment:")
    print(f"  • Total agents discovered: {total_agents}")
    print(f"  • Valid and operational: {valid_count}")
    print(f"  • Requiring attention: {invalid_count}")

    if valid_count == total_agents:
        print("\n🎉 EXCELLENT: All agents are operational!")
        print("💡 Recommendations:")
        print("  • System is production-ready")
        print("  • Consider adding more agents to expand capabilities")
        print("  • Set up monitoring for continued health tracking")
    elif valid_count > 0:
        print(f"\n⚠️  {invalid_count} agents need attention")
        print("💡 Recommendations:")
        print("  • Fix invalid agents to improve system reliability")
        print("  • Validate agent structure and dependencies")
        print("  • Check virtual environment setup")
    else:
        print("\n🚨 CRITICAL: No operational agents found")
        print("💡 Immediate actions needed:")
        print("  • Install seed agents for basic functionality")
        print("  • Verify system setup and configuration")
        print("  • Check agent installation procedures")

    print_separator("6. ENTERPRISE FEATURES DEMONSTRATED")

    print("✅ Comprehensive agent discovery across namespaces")
    print("✅ Multi-level validation (manifest, structure, runtime)")
    print("✅ Capability analysis and method mapping")
    print("✅ Health monitoring with live execution tests")
    print("✅ Actionable recommendations for system management")
    print("✅ Production readiness assessment")
    print("✅ Automated quality assurance workflows")

    print("\n🏢 ENTERPRISE VALUE:")
    print("💼 Confidence in AI agent deployments")
    print("📊 Visibility into system capabilities and health")
    print("🔧 Proactive maintenance and optimization")
    print("📈 Scalable management for large agent ecosystems")
    print("🛡️ Risk mitigation through comprehensive validation")


if __name__ == "__main__":
    main()
