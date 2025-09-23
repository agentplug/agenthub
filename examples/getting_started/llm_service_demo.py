#!/usr/bin/env python3
"""
LLM Service Demo - Comprehensive Usage Examples

This demonstrates how to use the standardized CoreLLMService
for any agent or application in AgentHub.
"""

from agenthub.core.llm.llm_service import CoreLLMService

service = CoreLLMService()

print(service.get_current_model())

# Basic generation
print(service.generate("Hello, world!"))

# Generation with parameters (temperature, max_tokens, etc.)
print(service.generate("Tell me a creative story", temperature=0.8, max_tokens=200))

# JSON response example with messages and parameters
messages = [
    {
        "role": "user",
        "content": (
            "List 3 programming languages in JSON format with a 'languages' array"
        ),
    }
]
print(service.generate(messages, return_json=True, temperature=0.3))
