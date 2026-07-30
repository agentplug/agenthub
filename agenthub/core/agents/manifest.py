"""Agent manifest (agent.yaml) schema and validation.

The manifest is the contract between agent authors and AgentHub. Schema
v1 is defined as pydantic models with precise, human-readable errors: a
malformed manifest fails with a message naming the exact field, instead
of somewhere deep in the loader.

``ManifestParser`` keeps its historical API (used by the loader); the
model layer underneath is shared with install-time validation in the
repository cloner.
"""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..tools.exceptions import AgentHubError

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1


class ManifestValidationError(AgentHubError):
    """Raised when agent manifest validation fails."""

    pass


class ParameterSpec(BaseModel):
    """A single method parameter declaration."""

    model_config = ConfigDict(extra="allow")

    type: str = "string"
    description: str = ""
    required: bool = False


class MethodSpec(BaseModel):
    """A method exposed through ``interface.methods``."""

    model_config = ConfigDict(extra="allow")

    description: str
    parameters: dict[str, ParameterSpec] | None = None
    returns: dict[str, Any] | None = None


class InterfaceSpec(BaseModel):
    """The agent's public interface. At least one method is required."""

    model_config = ConfigDict(extra="allow")

    methods: dict[str, MethodSpec] = Field(min_length=1)


class AgentManifest(BaseModel):
    """Schema v1 of agent.yaml.

    Mirrors the historical validation rules exactly, so no previously
    valid agent becomes invalid. Unknown fields are preserved. Tighten
    in future schema versions, not by breaking v1.
    """

    model_config = ConfigDict(extra="allow")

    schema_version: int = SCHEMA_VERSION
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    description: str
    author: str
    license: str = ""
    python_version: str = ""
    installation: dict[str, Any] | None = None
    interface: InterfaceSpec
    tags: list[str] = Field(default_factory=list)
    dependencies: list[str] | None = None


def _friendly_validation_message(error: ValidationError) -> str:
    lines = []
    for issue in error.errors():
        location = ".".join(str(part) for part in issue["loc"]) or "<root>"
        lines.append(f"  - {location}: {issue['msg']}")
    plural = "s" if len(lines) != 1 else ""
    return f"{len(lines)} manifest error{plural}:\n" + "\n".join(lines)


def parse_manifest_data(data: Any, source: str = "agent.yaml") -> AgentManifest:
    """Validate already-parsed YAML data into an AgentManifest.

    Raises:
        ManifestValidationError: With a per-field message when invalid.
    """
    if not isinstance(data, dict):
        raise ManifestValidationError(
            f"{source} must contain a YAML mapping, got "
            f"{'an empty file' if data is None else type(data).__name__}"
        )
    try:
        return AgentManifest.model_validate(data)
    except ValidationError as e:
        raise ManifestValidationError(
            f"Invalid {source}: {_friendly_validation_message(e)}",
            suggestions=[
                "See CREATING_AGENTS.md for the manifest format",
                "Required: name, version, description, author, and "
                "interface.methods with at least one described method",
            ],
        ) from e


def load_manifest(agent_dir: Path) -> AgentManifest:
    """Load and validate the manifest from an agent directory.

    Accepts ``agent.yaml`` or ``agent.yml``.

    Raises:
        ManifestValidationError: If missing, unreadable, or invalid.
    """
    for candidate in ("agent.yaml", "agent.yml"):
        path = agent_dir / candidate
        if path.exists():
            break
    else:
        raise ManifestValidationError(
            f"No agent.yaml found in {agent_dir}",
            suggestions=["Every agent needs an agent.yaml manifest"],
        )

    try:
        data = yaml.safe_load(path.read_text())
    except OSError as e:
        raise ManifestValidationError(f"Could not read {path}: {e}") from e
    except yaml.YAMLError as e:
        raise ManifestValidationError(f"{path.name} is not valid YAML: {e}") from e

    return parse_manifest_data(data, source=path.name)


def validate_manifest_dir(agent_dir: Path) -> str | None:
    """Validation-check an agent directory's manifest.

    Returns:
        A human-readable error string, or None if the manifest is valid.
    """
    try:
        load_manifest(agent_dir)
    except ManifestValidationError as e:
        return str(e)
    return None


class ManifestParser:
    """Parse and validate agent manifest files (historical API).

    The loader consumes this; validation is delegated to the schema
    models above.
    """

    def __init__(self) -> None:
        """Initialize the manifest parser."""

    def parse_manifest(self, manifest_path: str) -> dict[str, Any]:
        """
        Parse and validate an agent manifest file.

        Args:
            manifest_path: Path to the agent.yaml file

        Returns:
            dict: Parsed and validated manifest data (raw mapping, with
            unknown fields preserved)

        Raises:
            ManifestValidationError: If manifest is invalid or missing
        """
        manifest_file = Path(manifest_path)

        if not manifest_file.exists():
            raise ManifestValidationError(f"Manifest file not found: {manifest_path}")

        try:
            data = yaml.safe_load(manifest_file.read_text())
        except yaml.YAMLError as e:
            raise ManifestValidationError(f"Invalid YAML syntax: {e}") from e
        except OSError as e:
            raise ManifestValidationError(f"Error reading manifest: {e}") from e

        parse_manifest_data(data, source=manifest_file.name)
        # Callers work with the raw mapping; the model is the validator.
        return data  # type: ignore[no-any-return]

    def get_methods(self, manifest: dict) -> list[str]:
        """
        Get list of method names from manifest.

        Args:
            manifest: Parsed manifest data

        Returns:
            List of method names
        """
        if "interface" not in manifest or "methods" not in manifest["interface"]:
            return []

        return list(manifest["interface"]["methods"].keys())

    def get_dependencies(self, manifest: dict) -> list[str]:
        """
        Get list of dependencies from manifest.

        Args:
            manifest: Parsed manifest data

        Returns:
            List of dependency specifications
        """
        dependencies = manifest.get("dependencies", [])
        if dependencies is None:
            return []

        return dependencies if isinstance(dependencies, list) else []
