"""
Tool validation utilities for ensuring agents only use available tools.
"""

from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ToolValidationError(Exception):
    """Raised when tool validation fails."""
    pass


def validate_tool_call(tool_name: str, tool_context: Dict[str, Any]) -> bool:
    """
    Validate that a tool call is allowed based on the tool context.
    
    Args:
        tool_name: Name of the tool being called
        tool_context: Tool context from the agent
        
    Returns:
        bool: True if tool call is valid, False otherwise
        
    Raises:
        ToolValidationError: If tool call is explicitly forbidden
    """
    if not tool_context:
        return True
        
    available_tools = tool_context.get("available_tools", [])
    tool_constraints = tool_context.get("tool_constraints", {})
    
    # Check if tool is in available tools
    if tool_name not in available_tools:
        forbidden_tools = tool_constraints.get("forbidden_tools", [])
        if tool_name in forbidden_tools:
            raise ToolValidationError(
                f"Tool '{tool_name}' is explicitly forbidden. "
                f"Available tools: {available_tools}"
            )
        else:
            raise ToolValidationError(
                f"Tool '{tool_name}' is not available. "
                f"Available tools: {available_tools}"
            )
    
    return True


def validate_tool_calls(tool_calls: List[Dict[str, Any]], tool_context: Dict[str, Any]) -> List[str]:
    """
    Validate multiple tool calls and return list of invalid tool names.
    
    Args:
        tool_calls: List of tool call dictionaries
        tool_context: Tool context from the agent
        
    Returns:
        List of invalid tool names (empty if all valid)
    """
    invalid_tools = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("tool_name")
        if tool_name:
            try:
                validate_tool_call(tool_name, tool_context)
            except ToolValidationError as e:
                invalid_tools.append(tool_name)
                logger.warning(f"Invalid tool call: {e}")
    
    return invalid_tools


def redirect_tool_calls(tool_calls: List[Dict[str, Any]], tool_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Redirect invalid tool calls to valid alternatives based on tool mappings.
    
    Args:
        tool_calls: List of tool call dictionaries
        tool_context: Tool context from the agent
        
    Returns:
        List of redirected tool calls
    """
    redirected_calls = []
    tool_mappings = tool_context.get("tool_mappings", {})
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("tool_name")
        
        # Check if tool needs redirection
        if tool_name in tool_mappings:
            redirected_tool = tool_mappings[tool_name]
            redirected_call = tool_call.copy()
            redirected_call["tool_name"] = redirected_tool
            redirected_calls.append(redirected_call)
            logger.info(f"Redirected tool call from '{tool_name}' to '{redirected_tool}'")
        else:
            redirected_calls.append(tool_call)
    
    return redirected_calls


def create_tool_validation_instructions(tool_context: Dict[str, Any]) -> str:
    """
    Create explicit instructions for agents about tool usage.
    
    Args:
        tool_context: Tool context from the agent
        
    Returns:
        String with tool usage instructions
    """
    available_tools = tool_context.get("available_tools", [])
    tool_constraints = tool_context.get("tool_constraints", {})
    forbidden_tools = tool_constraints.get("forbidden_tools", [])
    
    instructions = [
        "TOOL USAGE INSTRUCTIONS:",
        f"✅ You can ONLY use these tools: {', '.join(available_tools)}",
        f"❌ You CANNOT use these tools: {', '.join(forbidden_tools)}" if forbidden_tools else "",
        "⚠️  Use individual tools for best results: web_search, web_scrape, web_analyze, web_summarize",
        "⚠️  For comprehensive analysis, chain tools: search → scrape → analyze → summarize",
        "",
        "IMPORTANT: Any attempt to use unavailable tools will result in execution failure."
    ]
    
    return "\n".join(filter(None, instructions))


def enhance_tool_context_with_validation(tool_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance tool context with validation information.
    
    Args:
        tool_context: Original tool context
        
    Returns:
        Enhanced tool context with validation info
    """
    if not tool_context:
        return tool_context
        
    # Add validation instructions
    tool_context["validation_instructions"] = create_tool_validation_instructions(tool_context)
    
    # Add explicit tool mapping for common cases
    available_tools = tool_context.get("available_tools", [])
    if "web_search" in available_tools and "web_scrape" in available_tools:
        tool_context["tool_mappings"] = {
            "combo_tool": "web_search"
        }
    
    return tool_context
