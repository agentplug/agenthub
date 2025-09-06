"""Tool metadata management for Phase 2.5."""

from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    description: str
    function: Callable
    namespace: str = "custom"
    parameters: Optional[Dict[str, Any]] = None
    return_type: Optional[str] = None
    examples: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize derived fields after object creation."""
        if self.parameters is None:
            self.parameters = self._extract_parameters()
        
        if self.return_type is None:
            self.return_type = self._extract_return_type()
        
        if self.examples is None:
            self.examples = self._generate_examples()
    
    def _extract_parameters(self) -> Dict[str, Any]:
        """Extract parameter information from function signature."""
        import inspect
        sig = inspect.signature(self.function)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            param_info = {
                "name": param_name,
                "type": param.annotation if param.annotation != inspect.Parameter.empty else "Any",
                "required": param.default == inspect.Parameter.empty,
                "default": param.default if param.default != inspect.Parameter.empty else None
            }
            parameters[param_name] = param_info
        
        return parameters
    
    def _extract_return_type(self) -> str:
        """Extract return type from function signature."""
        import inspect
        sig = inspect.signature(self.function)
        return_type = sig.return_annotation
        
        if return_type == inspect.Parameter.empty:
            return "Any"
        
        if hasattr(return_type, '__name__'):
            return return_type.__name__
        
        return str(return_type)
    
    def _generate_examples(self) -> List[str]:
        """Generate usage examples for the tool."""
        param_names = list(self.parameters.keys())
        
        if not param_names:
            return [f"{self.name}()"]
        
        # Generate simple examples
        examples = []
        
        # Example with all parameters
        if len(param_names) == 1:
            examples.append(f"{self.name}('example_value')")
        elif len(param_names) == 2:
            examples.append(f"{self.name}('param1', 'param2')")
        else:
            # For more complex tools, show key parameters
            key_params = param_names[:2]  # First 2 parameters
            example_args = ', '.join([f"'{name}_value'" for name in key_params])
            examples.append(f"{self.name}({example_args})")
        
        return examples
