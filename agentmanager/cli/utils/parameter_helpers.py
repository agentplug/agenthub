"""Parameter handling utilities for CLI commands."""

from typing import Any

from rich import print as rprint
from rich.prompt import Prompt


def interactive_parameter_input(method_name: str) -> dict[str, Any]:
    """Interactive parameter input for user-friendly experience."""
    params = {}

    rprint("📝 [cyan]Let's set up the parameters step by step...[/cyan]")

    if "generate" in method_name.lower() or "code" in method_name.lower():
        prompt = Prompt.ask("What code would you like me to generate?", default="")
        if prompt:
            params["prompt"] = prompt

    elif "analyze" in method_name.lower():
        text = Prompt.ask("What text would you like me to analyze?", default="")
        if text:
            params["text"] = text
            analysis_type = Prompt.ask(
                "What type of analysis?",
                choices=["general", "sentiment", "code_quality", "business"],
                default="general",
            )
            params["analysis_type"] = analysis_type

    elif "summarize" in method_name.lower():
        content = Prompt.ask("What content would you like me to summarize?", default="")
        if content:
            params["content"] = content

    elif "explain" in method_name.lower():
        code = Prompt.ask("What code would you like me to explain?", default="")
        if code:
            params["code"] = code

    else:
        # Generic input
        user_input = Prompt.ask(f"Please provide input for {method_name}", default="")
        if user_input:
            params["input"] = user_input

    return params


def smart_parameter_mapping(method_name: str, user_input: str) -> dict[str, Any]:
    """Intelligently map simple string input to appropriate parameters."""
    if "generate" in method_name.lower() or "code" in method_name.lower():
        return {"prompt": user_input}
    elif "analyze" in method_name.lower():
        return {"text": user_input, "analysis_type": "general"}
    elif "summarize" in method_name.lower():
        return {"content": user_input}
    elif "explain" in method_name.lower():
        return {"code": user_input}
    else:
        return {"input": user_input}
