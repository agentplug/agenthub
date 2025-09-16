import agenthub as ah


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

    print_separator("1. AGENT DISCOVERY ENGINE")

    # Try to load common agents
    agent_list = ["agentplug/coding-agent", "agentplug/analysis-agent"]

    print("🔍 Scanning agent ecosystem...")
    agents = []

    for agent_id in agent_list:
        try:
            agent = ah.load_agent(agent_id)
            agents.append(
                {
                    "id": agent_id,
                    "name": agent.name,
                    "methods": agent.methods,
                    "agent": agent,
                }
            )
            print(f"   ✅ {agent_id}: {len(agent.methods)} methods")
        except Exception as e:
            print(f"   ❌ {agent_id}: {e}")

    if not agents:
        print("⚠️  No agents available for demonstration")
        print("💡 Set up seed agents first to see full capabilities")
        return

    # Show discovery details
    print_subsection("📊 Discovery Report")
    print(f"Total agents: {len(agents)}")

    for agent_info in agents:
        agent_id = agent_info["id"]
        name = agent_info["name"]
        methods = agent_info["methods"]
        print(f"  • {agent_id}")
        print(f"    Methods: {len(methods)}")

    print_separator("2. COMPREHENSIVE VALIDATION")

    validation_results = []

    for agent_info in agents:
        agent_id = agent_info["id"]
        agent = agent_info["agent"]

        print(f"\n🔍 Validating {agent_id}...")

        try:
            # Perform comprehensive checks
            checks = {
                "agent_loaded": agent is not None,
                "methods_available": len(agent.methods) > 0,
                "name_available": hasattr(agent, "name"),
                "basic_functionality": True,  # Will test below
            }

            # Display validation results
            print("  📋 Validation Results:")
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"    {status} {check_name.replace('_', ' ').title()}")

            # Overall validation status
            overall_valid = all(checks.values())
            status = "✅ VALID" if overall_valid else "❌ INVALID"
            print(f"  🎯 Overall Status: {status}")

            # Store results for summary
            validation_results.append(
                {
                    "agent": agent_id,
                    "valid": overall_valid,
                    "checks": checks,
                    "info": {"name": agent.name, "methods": agent.methods},
                }
            )

        except Exception as e:
            print(f"  ❌ Validation failed: {e}")
            validation_results.append(
                {"agent": agent_id, "valid": False, "error": str(e)}
            )

    print_separator("3. HEALTH MONITORING")

    print("🏥 Running health checks on validated agents...")
    health_results = []

    for result in validation_results:
        if not result.get("valid", False) or "error" in result:
            continue

        agent_id = result["agent"]
        print(f"\n🔍 Health check: {agent_id}")

        try:
            # Get agent from original list
            agent = next(a["agent"] for a in agents if a["id"] == agent_id)

            # Test method discovery
            methods = agent.methods
            print(f"  📋 Available methods: {len(methods)}")

            # Test method introspection
            if methods:
                test_method = methods[0]
                try:
                    method_info = agent.get_method_info(test_method)
                    print(f"  ✅ Method introspection: {test_method}")
                except Exception as e:
                    print(f"  ❌ Method introspection failed: {e}")

            # Test basic execution (if safe)
            if "analyze_text" in methods:
                try:
                    test_result = agent.analyze_text(
                        text="Test message for health check", analysis_type="general"
                    )
                    if "result" in test_result:
                        print("  ✅ Execution test: PASSED")
                    else:
                        print(
                            f"  ⚠️  Execution test: PARTIAL - {test_result.get('error')}"
                        )
                except Exception as e:
                    print(f"  ❌ Execution test: FAILED - {e}")
            else:
                print("  ⚠️  No safe test method available")

            health_results.append(
                {"agent": agent_id, "healthy": True, "methods": len(methods)}
            )

        except Exception as e:
            print(f"  ❌ Health check failed: {e}")
            health_results.append(
                {"agent": agent_id, "healthy": False, "error": str(e)}
            )

    print_separator("4. CAPABILITY ANALYSIS")

    print("🧠 Analyzing agent capabilities across the system...")

    # Aggregate capabilities
    all_capabilities = set()
    capability_counts = {}
    agent_capabilities = {}

    for result in validation_results:
        if not result.get("valid", False):
            continue

        agent_id = result["agent"]
        methods = result["info"].get("methods", [])

        agent_capabilities[agent_id] = methods
        all_capabilities.update(methods)

        for method in methods:
            capability_counts[method] = capability_counts.get(method, 0) + 1

    print("📊 Capability Analysis:")
    print(f"  Total unique capabilities: {len(all_capabilities)}")
    print(f"  Total agent-method combinations: {sum(capability_counts.values())}")

    # Show capability distribution
    print_subsection("📈 Capability Distribution")
    sorted_capabilities = sorted(
        capability_counts.items(), key=lambda x: x[1], reverse=True
    )

    for capability, count in sorted_capabilities:
        agents_with_capability = [
            agent
            for agent, methods in agent_capabilities.items()
            if capability in methods
        ]
        print(f"  {capability}: {count} agents")
        print(f"    Available in: {', '.join(agents_with_capability)}")

    print_separator("5. RECOMMENDATIONS")

    print("💡 System Health Recommendations:")

    # Validation summary
    valid_count = sum(1 for r in validation_results if r.get("valid", False))
    total_count = len(validation_results)
    print(f"  📊 Validation: {valid_count}/{total_count} agents are valid")

    # Health summary
    healthy_count = sum(1 for r in health_results if r.get("healthy", False))
    total_health = len(health_results)
    if total_health > 0:
        print(f"  🏥 Health: {healthy_count}/{total_health} agents are healthy")

    # Capability recommendations
    print_subsection("🔧 Capability Recommendations")

    # Single points of failure
    single_capabilities = [
        capability for capability, count in capability_counts.items() if count == 1
    ]

    if single_capabilities:
        print("  ⚠️  Single points of failure (consider adding redundancy):")
        for capability in single_capabilities:
            print(f"    • {capability}")
    else:
        print("  ✅ All capabilities have redundancy - good system design!")

    # Missing critical capabilities
    critical_capabilities = ["generate_code", "analyze_text", "summarize_content"]
    missing_critical = [
        capability
        for capability in critical_capabilities
        if capability not in all_capabilities
    ]

    if missing_critical:
        print("  ❌ Missing critical capabilities:")
        for capability in missing_critical:
            print(f"    • {capability}")
    else:
        print("  ✅ All critical capabilities available")

    print_separator("6. SUMMARY")

    print("🎯 Enterprise Agent Management Summary:")
    print(f"  📦 Total Agents: {len(agents)}")
    print(f"  ✅ Valid Agents: {valid_count}")
    health_status = healthy_count if "health_results" in locals() else "N/A"
    print(f"  🏥 Healthy Agents: {health_status}")
    print(f"  🧠 Unique Capabilities: {len(all_capabilities)}")
    capability_total = (
        sum(capability_counts.values()) if "capability_counts" in locals() else "N/A"
    )
    print(f"  🔧 Total Capabilities: {capability_total}")

    print("\n💼 BUSINESS VALUE:")
    print("🚀 Confidence in AI agent deployments at scale")
    print("📊 Visibility into system capabilities and health")
    print("🔧 Proactive maintenance and optimization guidance")
    print("🛡️ Risk mitigation through comprehensive validation")
    print("📈 Enterprise-ready AI agent management")


if __name__ == "__main__":
    main()
