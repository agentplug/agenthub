"""Extraction of structured data from LLM text output.

Shared by the service layer (generate_structured), the decision maker, and
monitoring: one implementation of "find the JSON object in this response".
"""

import json
import re
from typing import Any

# A JSON object, tolerating one level of nesting.
_JSON_OBJECT_RE = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", re.DOTALL)
# A JSON array, tolerating one level of nesting.
_JSON_ARRAY_RE = re.compile(r"\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]", re.DOTALL)


def extract_json_from_text(text: str) -> dict[str, Any]:
    """Extract the first parseable JSON object from text with extra prose.

    LLMs asked for JSON often wrap it in explanation or code fences; this
    finds and parses the first JSON object (or object inside an array).

    Args:
        text: Raw LLM response.

    Returns:
        The parsed JSON dictionary.

    Raises:
        json.JSONDecodeError: If no valid JSON object can be extracted.
    """
    # Fast path: the whole response is valid JSON.
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    for match in _JSON_OBJECT_RE.findall(text):
        try:
            result = json.loads(match)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            continue

    for match in _JSON_ARRAY_RE.findall(text):
        try:
            result = json.loads(match)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError("No valid JSON object found in response", text, 0)
