"""Enhanced Agent wrapper with tool injection capabilities."""

import os
import json
import subprocess
import sys
from typing import List, Optional, Dict, Any, Union, Callable
from pathlib import Path

from ..core.tools import ToolRegistry
from ..core.mcp import AgentToolManager, ToolInjector


class EnhancedAgent:
    """Enhanced agent wrapper that provides tool injection capabilities."""
    
    def __init__(
        self,
        base_agent: str,
        assigned_tools: List[str],
        tool_registry: ToolRegistry,
        tool_manager: AgentToolManager,
        tool_injector: ToolInjector,
        **kwargs
    ):
        """
        Initialize enhanced agent with tool capabilities.
        
        Args:
            base_agent: Path to the base agent
            assigned_tools: List of tool names assigned to this agent
            tool_registry: Tool registry instance
            tool_manager: Tool manager instance
            tool_injector: Tool injector instance
            **kwargs: Additional arguments for the agent
        """
        self.base_agent = base_agent
        self.assigned_tools = assigned_tools
        self.tool_registry = tool_registry
        self.tool_manager = tool_manager
        self.tool_injector = tool_injector
        self.kwargs = kwargs
        
        # Find agent path
        self.agent_path = self._find_agent_path(base_agent)
        if not self.agent_path:
            raise ValueError(f"Agent not found: {base_agent}")
        
        # Load agent manifest
        self.manifest = self._load_agent_manifest()
        
        # Assign tools to this agent
        if assigned_tools:
            self.tool_manager.assign_tools_to_agent(
                agent_id=base_agent,
                tool_names=assigned_tools
            )
    
    def _find_agent_path(self, agent_name: str) -> Optional[Path]:
        """Find the agent path in the agent directory."""
        # Look in the standard agent directory
        agent_dir = Path.home() / ".agenthub" / "agents"
        agent_path = agent_dir / agent_name
        
        if agent_path.exists() and agent_path.is_dir():
            return agent_path
        
        # Look for agent.py in the directory
        agent_file = agent_path / "agent.py"
        if agent_file.exists():
            return agent_path
        
        return None
    
    def _load_agent_manifest(self) -> Dict[str, Any]:
        """Load agent manifest (agent.yaml)."""
        manifest_path = self.agent_path / "agent.yaml"
        if manifest_path.exists():
            try:
                import yaml
                with open(manifest_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        
        # Return default manifest if yaml not available
        return {
            "name": self.base_agent,
            "interface": {
                "methods": {}
            }
        }
    
    def _build_tool_context(self) -> Dict[str, Any]:
        """Build tool context for the agent."""
        if not self.assigned_tools:
            return {}
        
        tool_descriptions = {}
        tool_usage_examples = {}
        
        for tool_name in self.assigned_tools:
            metadata = self.tool_registry.get_tool_metadata(tool_name)
            if metadata:
                tool_descriptions[tool_name] = metadata.description
                # Create usage examples based on function signature
                sig = metadata.parameters
                if sig:
                    param_examples = []
                    for param_name, param_type in sig.items():
                        if param_type == str:
                            param_examples.append(f'"{param_name}": "example_value"')
                        elif param_type == int:
                            param_examples.append(f'"{param_name}": 5')
                        elif param_type == float:
                            param_examples.append(f'"{param_name}": 3.14')
                        else:
                            param_examples.append(f'"{param_name}": "value"')
                    
                    example_args = "{" + ", ".join(param_examples) + "}"
                    tool_usage_examples[tool_name] = [f"{tool_name}({example_args})"]
        
        return {
            "available_tools": self.assigned_tools,
            "tool_descriptions": tool_descriptions,
            "tool_usage_examples": tool_usage_examples
        }
    
    def _execute_agent_method(self, method: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent method with tool context injection."""
        # Build tool context
        tool_context = self._build_tool_context()
        
        # Prepare input for agent
        input_data = {
            "method": method,
            "parameters": parameters,
            "tool_context": tool_context
        }
        
        # Execute agent
        try:
            result = subprocess.run(
                [sys.executable, str(self.agent_path / "agent.py")],
                input=json.dumps(input_data),
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "error": f"Agent execution failed: {result.stderr}",
                    "status": "error"
                }
            
            # Parse agent response
            response = json.loads(result.stdout)
            
            # Check if agent requested tool execution
            if "result" in response and isinstance(response["result"], dict):
                result_data = response["result"]
                if result_data.get("status") == "tool_requested" and "tool_calls" in result_data:
                    # Execute tools and return results
                    return self._execute_tools_and_continue(result_data["tool_calls"], method, parameters)
            
            return response
            
        except subprocess.TimeoutExpired:
            return {
                "error": "Agent execution timed out",
                "status": "error"
            }
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse agent response: {e}",
                "status": "error"
            }
        except Exception as e:
            return {
                "error": f"Agent execution error: {e}",
                "status": "error"
            }
    
    def _execute_tools_and_continue(self, tool_calls: List[Dict[str, Any]], method: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool calls and continue with agent processing."""
        tool_results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["tool_name"]
            arguments = tool_call.get("arguments", {})
            
            # Execute tool via MCP
            try:
                result = self.tool_manager.execute_tool(
                    agent_id=self.base_agent,
                    tool_name=tool_name,
                    arguments=arguments
                )
                tool_results.append({
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                tool_results.append({
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "result": {"error": str(e)},
                    "success": False
                })
        
        # For now, return tool results directly
        # In a full implementation, we would re-run the agent with tool results
        return {
            "tool_results": tool_results,
            "tools_used": [tr["tool_name"] for tr in tool_results if tr["success"]],
            "status": "success"
        }
    
    def __getattr__(self, name: str) -> Callable:
        """Dynamically create methods based on agent manifest."""
        if name in self.manifest.get("interface", {}).get("methods", {}):
            def method_wrapper(**kwargs):
                return self._execute_agent_method(name, kwargs)
            return method_wrapper
        
        raise AttributeError(f"Agent has no method '{name}'")
    
    def get_available_methods(self) -> List[str]:
        """Get list of available agent methods."""
        return list(self.manifest.get("interface", {}).get("methods", {}).keys())
    
    def get_assigned_tools(self) -> List[str]:
        """Get list of tools assigned to this agent."""
        return self.assigned_tools.copy()
