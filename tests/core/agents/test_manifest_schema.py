"""Schema tests for the agent manifest (agent.yaml)."""

from pathlib import Path

import pytest

from agenthub.core.agents.manifest import (
    AgentManifest,
    ManifestValidationError,
    load_manifest,
    parse_manifest_data,
    validate_manifest_dir,
)

TEMPLATE = {
    # the CREATING_AGENTS.md template, verbatim structure
    "name": "my-agent",
    "version": "1.0.0",
    "description": "What your agent does",
    "author": "your-username",
    "license": "MIT",
    "python_version": "3.11+",
    "installation": {"commands": ["uv venv .venv"], "description": "install"},
    "interface": {
        "methods": {
            "do_something": {
                "description": "What this method does",
                "parameters": {
                    "input": {
                        "type": "string",
                        "description": "The input text",
                        "required": True,
                    }
                },
                "returns": {"type": "string", "description": "The result"},
            }
        }
    },
    "tags": ["your-tag"],
}


class TestSchema:
    def test_creating_agents_template_validates(self):
        manifest = parse_manifest_data(TEMPLATE)
        assert manifest.name == "my-agent"
        assert manifest.interface.methods["do_something"].parameters["input"].required

    def test_missing_fields_named_precisely(self):
        with pytest.raises(ManifestValidationError) as exc_info:
            parse_manifest_data({"name": "x"})
        message = str(exc_info.value)
        for field in ("version", "description", "author", "interface"):
            assert field in message

    def test_empty_methods_rejected(self):
        data = {**TEMPLATE, "interface": {"methods": {}}}
        with pytest.raises(ManifestValidationError, match="interface.methods"):
            parse_manifest_data(data)

    def test_wrong_types_located(self):
        data = {**TEMPLATE, "tags": "not-a-list"}
        with pytest.raises(ManifestValidationError, match="tags"):
            parse_manifest_data(data)

    def test_unknown_fields_preserved(self):
        manifest = parse_manifest_data({**TEMPLATE, "custom_field": {"x": 1}})
        assert manifest.model_extra["custom_field"] == {"x": 1}

    def test_non_mapping_rejected(self):
        with pytest.raises(ManifestValidationError, match="YAML mapping"):
            parse_manifest_data(["a", "list"])
        with pytest.raises(ManifestValidationError, match="empty file"):
            parse_manifest_data(None)

    def test_schema_version_default(self):
        assert parse_manifest_data(TEMPLATE).schema_version == 1


class TestDirectoryValidation:
    def write(self, tmp_path: Path, text: str) -> Path:
        (tmp_path / "agent.yaml").write_text(text)
        return tmp_path

    def test_valid_dir(self, tmp_path):
        import yaml

        self.write(tmp_path, yaml.safe_dump(TEMPLATE))
        assert validate_manifest_dir(tmp_path) is None
        assert load_manifest(tmp_path).name == "my-agent"

    def test_missing_manifest(self, tmp_path):
        error = validate_manifest_dir(tmp_path)
        assert error is not None and "No agent.yaml" in error

    def test_broken_yaml(self, tmp_path):
        self.write(tmp_path, "name: [unclosed")
        error = validate_manifest_dir(tmp_path)
        assert error is not None and "not valid YAML" in error

    def test_agent_yml_accepted(self, tmp_path):
        import yaml

        (tmp_path / "agent.yml").write_text(yaml.safe_dump(TEMPLATE))
        assert validate_manifest_dir(tmp_path) is None


class TestModelRoundtrip:
    def test_model_is_exported_type(self):
        manifest = AgentManifest.model_validate(TEMPLATE)
        dumped = manifest.model_dump()
        assert dumped["name"] == "my-agent"
