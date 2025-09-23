"""Knowledge validation for agents."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of knowledge validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


class KnowledgeValidator:
    """Validates knowledge content for agents."""

    def __init__(self) -> None:
        """Initialize knowledge validator."""
        self.max_knowledge_length = 10000  # 10KB limit
        self.min_knowledge_length = 10  # Minimum meaningful content

    def validate_knowledge(self, knowledge_text: str) -> ValidationResult:
        """Validate knowledge text."""
        errors: list[str] = []
        warnings: list[str] = []

        if not knowledge_text:
            errors.append("Knowledge text cannot be empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Length validation
        if len(knowledge_text) < self.min_knowledge_length:
            warnings.append(
                f"Knowledge text is very short ({len(knowledge_text)} characters). "
                f"Consider providing more detailed information."
            )

        if len(knowledge_text) > self.max_knowledge_length:
            errors.append(
                f"Knowledge text is too long ({len(knowledge_text)} characters). "
                f"Maximum allowed: {self.max_knowledge_length}"
            )

        # Content validation
        if knowledge_text.strip() != knowledge_text:
            warnings.append("Knowledge text has leading/trailing whitespace")

        # Check for potentially problematic content
        if self._contains_suspicious_content(knowledge_text):
            warnings.append("Knowledge text contains potentially problematic content")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def _contains_suspicious_content(self, text: str) -> bool:
        """Check for potentially problematic content."""
        suspicious_patterns = [
            "import os",
            "subprocess",
            "eval(",
            "exec(",
            "__import__",
            "file://",
            "http://",
            "https://",
        ]

        text_lower = text.lower()
        return any(pattern in text_lower for pattern in suspicious_patterns)

    def validate_metadata(self, metadata: dict[Any, Any]) -> ValidationResult:
        """Validate knowledge metadata."""
        errors: list[str] = []
        warnings: list[str] = []

        # Check for required fields
        if "source" not in metadata:
            warnings.append("Metadata should include 'source' field")

        if "timestamp" not in metadata:
            warnings.append("Metadata should include 'timestamp' field")

        # Validate metadata types
        for key, value in metadata.items():
            if not isinstance(key, str):
                errors.append(f"Metadata key must be string, got {type(key).__name__}")

            if not isinstance(value, str | int | float | bool | list | dict):
                errors.append(
                    f"Metadata value for '{key}' must be a basic type, "
                    f"got {type(value).__name__}"
                )

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
