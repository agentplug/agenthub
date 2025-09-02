"""Parameter handling utilities for CLI commands."""

import json
from typing import Any, Dict, List, Optional

from rich import print as rprint
from rich.prompt import Prompt, Confirm


def interactive_parameter_input(agent_info: dict, method_name: str) -> dict[str, Any]:
    """
    Interactive parameter input for user-friendly experience.
    
    Args:
        agent_info: Agent information containing manifest and interface
        method_name: Name of the method to get parameters for
        
    Returns:
        Dictionary of parameter values
    """
    params = {}
    
    # Get method definition from agent interface
    method_def = _get_method_definition(agent_info, method_name)
    if not method_def:
        rprint(f"❌ [red]Method '{method_name}' not found in agent interface[/red]")
        return {}
    
    parameters = method_def.get("parameters", {})
    if not parameters:
        rprint("ℹ️  [dim]This method doesn't require any parameters[/dim]")
        return {}
    
    rprint("📝 [cyan]Let's set up the parameters step by step...[/cyan]")
    rprint(f"🎯 [dim]Method: {method_name}[/dim]")
    rprint(f"📖 [dim]Description: {method_def.get('description', 'No description')}[/dim]")
    
    # Process each parameter
    for param_name, param_def in parameters.items():
        param_type = param_def.get("type", "string")
        param_desc = param_def.get("description", f"Parameter: {param_name}")
        required = param_def.get("required", False)
        default_value = param_def.get("default")
        
        # Create prompt text
        prompt_text = f"{param_desc}"
        if required:
            prompt_text += " [bold red](required)[/bold red]"
        else:
            prompt_text += " [dim](optional)[/dim]"
        
        # Handle different parameter types
        if param_type == "boolean":
            value = Confirm.ask(prompt_text, default=default_value or False)
        elif param_type == "integer":
            while True:
                try:
                    user_input = Prompt.ask(prompt_text, default=str(default_value) if default_value is not None else "")
                    if not user_input and not required:
                        break
                    value = int(user_input)
                    break
                except ValueError:
                    rprint("❌ [red]Please enter a valid integer[/red]")
        elif param_type == "number" or param_type == "float":
            while True:
                try:
                    user_input = Prompt.ask(prompt_text, default=str(default_value) if default_value is not None else "")
                    if not user_input and not required:
                        break
                    value = float(user_input)
                    break
                except ValueError:
                    rprint("❌ [red]Please enter a valid number[/red]")
        elif param_type == "array" or param_type == "list":
            user_input = Prompt.ask(f"{prompt_text} (comma-separated values)", default="")
            if user_input:
                value = [item.strip() for item in user_input.split(",")]
            else:
                value = default_value or []
        elif param_type == "object" or param_type == "dict":
            user_input = Prompt.ask(f"{prompt_text} (JSON format)", default="")
            if user_input:
                try:
                    value = json.loads(user_input)
                except json.JSONDecodeError:
                    rprint("❌ [red]Invalid JSON format[/red]")
                    value = default_value or {}
            else:
                value = default_value or {}
        else:  # string or unknown type
            value = Prompt.ask(prompt_text, default=default_value or "")
        
        # Only add parameter if it has a value or is required
        if value or required:
            params[param_name] = value
    
    return params


def smart_parameter_mapping(agent_info: dict, method_name: str, user_input: str) -> dict[str, Any]:
    """
    Intelligently map simple string input to appropriate parameters based on agent interface.
    
    Args:
        agent_info: Agent information containing manifest and interface
        method_name: Name of the method to map parameters for
        user_input: Simple string input from user
        
    Returns:
        Dictionary of parameter values
    """
    # Get method definition from agent interface
    method_def = _get_method_definition(agent_info, method_name)
    if not method_def:
        return {"input": user_input}  # Fallback to generic input
    
    parameters = method_def.get("parameters", {})
    if not parameters:
        return {}  # No parameters needed
    
    # Find the best parameter to map the input to
    param_name = _find_best_parameter_for_input(parameters, user_input)
    
    if param_name:
        params = {param_name: user_input}
        
        # Add default values for other parameters if they exist
        for param, param_def in parameters.items():
            if param != param_name and param_def.get("default") is not None:
                params[param] = param_def["default"]
        
        return params
    else:
        # Fallback: try to map to first required parameter or first parameter
        for param_name, param_def in parameters.items():
            if param_def.get("required", False):
                return {param_name: user_input}
        
        # If no required parameters, use first parameter
        if parameters:
            first_param = list(parameters.keys())[0]
            return {first_param: user_input}
        
        return {"input": user_input}  # Final fallback


def _get_method_definition(agent_info: dict, method_name: str) -> Optional[dict]:
    """Get method definition from agent interface."""
    manifest = agent_info.get("manifest", {})
    interface = manifest.get("interface", {})
    methods = interface.get("methods", {})
    return methods.get(method_name)


def _find_best_parameter_for_input(parameters: dict, user_input: str) -> Optional[str]:
    """
    Find the best parameter to map user input to based on parameter descriptions and types.
    
    Args:
        parameters: Parameter definitions from agent interface
        user_input: User input string
        
    Returns:
        Best parameter name to use, or None if no good match
    """
    # Score parameters based on how well they match the input
    param_scores = {}
    
    for param_name, param_def in parameters.items():
        score = 0
        param_desc = param_def.get("description", "").lower()
        param_type = param_def.get("type", "string")
        
        # Prefer string parameters for text input
        if param_type == "string":
            score += 10
        
        # Boost score for required parameters
        if param_def.get("required", False):
            score += 5
        
        # Boost score based on description keywords
        description_keywords = [
            "text", "content", "input", "prompt", "query", "message", 
            "data", "value", "string", "description"
        ]
        for keyword in description_keywords:
            if keyword in param_desc:
                score += 2
        
        # Boost score for parameters that seem to be the "main" input
        main_input_keywords = ["prompt", "text", "content", "input", "query"]
        for keyword in main_input_keywords:
            if keyword in param_name.lower() or keyword in param_desc:
                score += 3
        
        param_scores[param_name] = score
    
    # Return the parameter with the highest score
    if param_scores:
        return max(param_scores, key=param_scores.get)
    
    return None
