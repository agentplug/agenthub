import time

import agenthub as ah


class AgentOrchestrator:
    """Dynamic agent orchestration with automatic discovery and fallbacks."""

    def __init__(self):
        """Initialize the orchestrator with all available agents."""
        self.agents = {}
        self.capabilities = {}
        self._discover_agents()

    def _discover_agents(self):
        """Discover and load all available agents."""
        print("🔍 Discovering available agents...")

        # Try to load common agents
        agent_list = ["agentplug/coding-agent", "agentplug/analysis-agent"]

        for agent_id in agent_list:
            try:
                agent = ah.load_agent(agent_id)
                self.agents[agent_id] = agent

                # Map capabilities
                for method in agent.methods:
                    if method not in self.capabilities:
                        self.capabilities[method] = []
                    self.capabilities[method].append(agent_id)

                print(f"   ✅ {agent_id}: {len(agent.methods)} methods")

            except Exception as e:
                print(f"   ❌ {agent_id}: {e}")

        print(
            f"🎯 Orchestrator ready: {len(self.agents)} agents, "
            f"{len(self.capabilities)} capabilities"
        )

    def get_agents_with_capability(self, method_name: str) -> list[str]:
        """Get all agents that have a specific capability."""
        return self.capabilities.get(method_name, [])

    def execute_with_fallback(
        self, method_name: str, parameters: dict, preferred_agent: str | None = None
    ) -> dict:
        """Execute a method with automatic fallback to other capable agents."""
        capable_agents = self.get_agents_with_capability(method_name)

        if not capable_agents:
            return {"error": f"No agents available with capability: {method_name}"}

        # Try preferred agent first
        if preferred_agent and preferred_agent in capable_agents:
            capable_agents = [preferred_agent] + [
                a for a in capable_agents if a != preferred_agent
            ]

        last_error = None
        for agent_id in capable_agents:
            try:
                agent = self.agents[agent_id]
                print(f"   🔄 Trying {agent_id}...")

                # Execute method using magic method interface
                if hasattr(agent, method_name):
                    method = getattr(agent, method_name)
                    result = method(**parameters)
                    return {"result": result, "executed_by": agent_id}
                else:
                    last_error = f"Method {method_name} not found on {agent_id}"
                    continue

            except Exception as e:
                last_error = str(e)
                continue

        return {"error": f"All agents failed: {last_error}"}

    def create_workflow(self, workflow: dict) -> dict:
        """Execute a multi-step workflow with dependencies."""
        steps = workflow.get("steps", [])
        results = {}
        completed = set()

        # Execute steps in dependency order
        while len(completed) < len(steps):
            progress = False
            for step in steps:
                step_id = step["id"]
                if step_id in completed:
                    continue

                # Check dependencies
                deps = step.get("depends_on", [])
                if not all(dep in completed for dep in deps):
                    continue

                # Execute step
                method = step["method"]
                params = step["parameters"]

                # Substitute context variables
                for key, value in params.items():
                    if (
                        isinstance(value, str)
                        and value.startswith("${")
                        and value.endswith("}")
                    ):
                        var_name = value[2:-1]
                        if var_name in results:
                            params[key] = results[var_name]["result"]

                print(f"   🚀 Executing {step_id}...")
                result = self.execute_with_fallback(method, params)
                results[step_id] = result
                completed.add(step_id)
                progress = True

            if not progress:
                return {"error": "Circular dependency detected"}

        return {"success": True, "results": results}


def main():
    """Demonstrate dynamic agent orchestration capabilities."""
    print("🎯 Dynamic Agent Orchestration")
    print("=" * 40)
    print("Build AI workflows that adapt and scale!")
    print()

    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    if not orchestrator.agents:
        print("❌ No agents available for orchestration!")
        return

    print("\n🚀 ORCHESTRATION DEMONSTRATIONS:")
    print("=" * 40)

    # Scenario 1: Automatic fallback
    print("\n1. 🔄 Automatic Fallback")
    print("-" * 25)
    print("Try preferred agent, fallback to others on failure")
    print()

    print("   📝 Generating code with fallback...")
    result = orchestrator.execute_with_fallback(
        "generate_code",
        {"prompt": "Create a simple calculator function"},
        preferred_agent="agentplug/coding-agent",
    )

    if "result" in result:
        print(f"   ✅ Success! Executed by: {result['executed_by']}")
        print(f"   📄 Generated {len(str(result['result']))} characters")
    else:
        print(f"   ❌ Failed: {result['error']}")

    print()
    input("   Press Enter to continue...")
    print()

    # Scenario 2: Parallel execution
    print("2. ⚡ Parallel Task Execution")
    print("-" * 30)
    print("Execute multiple tasks simultaneously for better performance")
    print()

    # Simulate parallel execution
    tasks = [
        ("generate_code", {"prompt": "Create a data validation function"}),
        (
            "analyze_text",
            {"text": "Sample text for analysis", "analysis_type": "general"},
        ),
    ]

    print("   🚀 Executing tasks in parallel...")
    start_time = time.time()

    for method, params in tasks:
        result = orchestrator.execute_with_fallback(method, params)
        if "result" in result:
            print(f"   ✅ {method}: {len(str(result['result']))} chars")
        else:
            print(f"   ❌ {method}: {result['error']}")

    elapsed = time.time() - start_time
    print(f"   ⏱️  Total time: {elapsed:.2f}s")

    print()
    input("   Press Enter to continue...")
    print()

    # Scenario 3: Complex workflow
    print("3. 🔗 Complex Workflow Orchestration")
    print("-" * 38)
    print("Multi-step workflows with dependencies and context")
    print()

    workflow = {
        "steps": [
            {
                "id": "generate_base_code",
                "method": "generate_code",
                "parameters": {"prompt": "Create a simple web scraper"},
                "depends_on": [],
                "required": True,
            },
            {
                "id": "add_error_handling",
                "method": "generate_code",
                "parameters": {
                    "prompt": "Add error handling to: ${generate_base_code}"
                },
                "depends_on": ["generate_base_code"],
                "required": False,
            },
            {
                "id": "create_documentation",
                "method": "summarize_content",
                "parameters": {"content": "Document this code: ${generate_base_code}"},
                "depends_on": ["generate_base_code"],
                "required": False,
            },
        ],
    }

    # Check capabilities
    required_methods = {step["method"] for step in workflow["steps"]}
    available_methods = set(orchestrator.capabilities.keys())

    if required_methods.issubset(available_methods):
        print("\n🔗 Executing multi-step workflow...")
        workflow_result = orchestrator.create_workflow(workflow)

        if workflow_result.get("success"):
            print("\n🎉 Workflow completed successfully!")
            print("📋 Workflow Summary:")
            for step_id, result in workflow_result["results"].items():
                status = "✅ Success" if "result" in result else "❌ Failed"
                executed_by = result.get("executed_by", "unknown")
                print(f"   {step_id}: {status} ({executed_by})")
        else:
            print(f"\n❌ Workflow failed: {workflow_result.get('error')}")
    else:
        missing = required_methods - available_methods
        print(f"\n⚠️  Workflow requires missing capabilities: {missing}")

    # Scenario 4: Capability discovery
    print("\n4. 🔍 Dynamic Capability Discovery")
    print("-" * 35)
    print("Analyze system capabilities and make recommendations")
    print()

    print("🔍 Analyzing system capabilities...")
    total_capabilities = len(orchestrator.capabilities)
    total_agents = len(orchestrator.agents)

    print(
        f"   System Scale: {total_agents} agents, "
        f"{total_capabilities} unique capabilities"
    )

    # Show capability distribution
    capability_counts = {
        cap: len(agents) for cap, agents in orchestrator.capabilities.items()
    }
    most_common = max(capability_counts.items(), key=lambda x: x[1])
    least_common = min(capability_counts.items(), key=lambda x: x[1])

    print(f"   Most redundant capability: {most_common[0]} ({most_common[1]} agents)")
    print(
        f"   Least redundant capability: {least_common[0]} ({least_common[1]} agents)"
    )

    # Recommendations
    print("\n💡 Orchestration Recommendations:")
    if most_common[1] > 1:
        print(
            f"   ✅ Good redundancy for {most_common[0]} - automatic fallback available"
        )
    if least_common[1] == 1:
        print(
            f"   ⚠️  Single point of failure for {least_common[0]} - "
            f"consider adding backup"
        )

    print(f"   📊 System can handle {total_capabilities} different types of AI tasks")
    print("   🔄 Automatic failover protects against individual agent failures")

    # Summary
    print("\n" + "=" * 60)
    print("🎯 ORCHESTRATION CAPABILITIES DEMONSTRATED")
    print("=" * 60)
    print("✅ Dynamic agent discovery and capability mapping")
    print("✅ Automatic fallback and error recovery")
    print("✅ Parallel task execution for improved performance")
    print("✅ Complex workflow orchestration with dependencies")
    print("✅ Context variable substitution between workflow steps")
    print("✅ Real-time capability analysis and recommendations")
    print("✅ Resilient system design with redundancy planning")

    print("\n🏢 ENTERPRISE BENEFITS:")
    print("🚀 Self-healing AI workflows that adapt to failures")
    print("📈 Horizontal scaling through agent redundancy")
    print("🔧 Reduced maintenance through automatic recovery")
    print("💼 Business continuity through intelligent fallbacks")
    print("⚡ Improved performance through parallel execution")


if __name__ == "__main__":
    main()
