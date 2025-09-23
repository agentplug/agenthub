"""Tool metadata management for Phase 2.5."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""

    name: str
    description: str
    function: Callable | None = None
    namespace: str = "custom"
    parameters: dict[str, Any] | None = None
    return_type: str | None = None
    examples: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields after object creation."""
        if self.parameters is None and self.function is not None:
            self.parameters = self._extract_parameters()
        elif self.parameters is None:
            self.parameters = {}

        if self.return_type is None and self.function is not None:
            self.return_type = self._extract_return_type()
        elif self.return_type is None:
            self.return_type = "Any"

        if self.examples is None:
            self.examples = self._generate_examples()

    def _extract_parameters(self) -> dict[str, Any]:
        """Extract parameter information from function signature."""
        import inspect

        if self.function is None:
            return {}
        sig = inspect.signature(self.function)
        parameters = {}

        for param_name, param in sig.parameters.items():
            param_info = {
                "name": param_name,
                "type": (
                    param.annotation
                    if param.annotation != inspect.Parameter.empty
                    else "Any"
                ),
                "required": param.default == inspect.Parameter.empty,
                "default": (
                    param.default if param.default != inspect.Parameter.empty else None
                ),
            }
            parameters[param_name] = param_info

        return parameters

    def _extract_return_type(self) -> str:
        """Extract return type from function signature."""
        import inspect

        if self.function is None:
            return "Any"
        sig = inspect.signature(self.function)
        return_type = sig.return_annotation

        if return_type == inspect.Parameter.empty:
            return "Any"

        if hasattr(return_type, "__name__"):
            name = return_type.__name__
            return str(name) if name is not None else "Any"

        return str(return_type) if return_type is not None else "Any"

    def _generate_examples(self) -> list[str]:
        """Generate usage examples for the tool."""
        if not self.parameters:
            return [f"{self.name}()"]

        param_names = list(self.parameters.keys())

        if not param_names:
            return [f"{self.name}()"]

        # Generate examples based on parameter types and names
        examples = []

        # Build parameter examples based on type information
        param_examples = []
        for param_name, param_info in self.parameters.items():
            param_type = param_info.get("type", "Any")
            default_value = param_info.get("default", None)

            if default_value is not None:
                # Use the default value
                if isinstance(default_value, str):
                    param_examples.append(f'"{default_value}"')
                else:
                    param_examples.append(str(default_value))
            elif param_type == "integer":
                # Generate meaningful examples for common math operations
                if param_name in ["a", "x", "first", "num1"]:
                    param_examples.append("12")
                elif param_name in ["b", "y", "second", "num2"]:
                    param_examples.append("5")
                else:
                    param_examples.append("42")
            elif param_type == "number":
                if param_name in ["a", "x", "first", "num1"]:
                    param_examples.append("12.5")
                elif param_name in ["b", "y", "second", "num2"]:
                    param_examples.append("2.5")
                else:
                    param_examples.append("3.14")
            elif param_type == "string":
                if "name" in param_name.lower():
                    param_examples.append('"Alice"')
                elif "location" in param_name.lower():
                    param_examples.append('"New York"')
                elif "text" in param_name.lower():
                    param_examples.append('"Hello world"')
                else:
                    param_examples.append(f'"{param_name}_value"')
            else:
                param_examples.append(f'"{param_name}_value"')

        # Generate function call example
        if param_examples:
            examples.append(f"{self.name}({', '.join(param_examples)})")
        else:
            examples.append(f"{self.name}()")

        return examples

    def to_dict(self) -> dict[str, Any]:
        """Convert ToolMetadata to dictionary."""
        # Convert parameters to JSON-serializable format
        serializable_params = {}
        if self.parameters:
            for param_name, param_info in self.parameters.items():
                if isinstance(param_info, dict):
                    serialized_param = param_info.copy()
                    # Convert type objects to strings for JSON serialization
                    if "type" in serialized_param and hasattr(
                        serialized_param["type"], "__name__"
                    ):
                        serialized_param["type"] = serialized_param["type"].__name__
                    elif "type" in serialized_param:
                        serialized_param["type"] = str(serialized_param["type"])
                    serializable_params[param_name] = serialized_param
                else:
                    serializable_params[param_name] = param_info

        return {
            "name": self.name,
            "description": self.description,
            "namespace": self.namespace,
            "parameters": serializable_params,
            "return_type": self.return_type,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolMetadata":
        """Create ToolMetadata from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            function=None,  # Function cannot be serialized/deserialized
            namespace=data.get("namespace", "custom"),
            parameters=data.get("parameters"),
            return_type=data.get("return_type"),
            examples=data.get("examples"),
        )

    def validate(self) -> bool:
        """Validate the tool metadata."""
        # Check for required fields
        if not self.name or not isinstance(self.name, str) or self.name.strip() == "":
            return False

        if not self.description or not isinstance(self.description, str):
            return False

        if not self.namespace or not isinstance(self.namespace, str):
            return False

        # Additional validations can be added here
        return True
