"""Tests for ManifestParser class."""

from pathlib import Path

import pytest
import yaml

from agenthub.core.agents.manifest import ManifestParser, ManifestValidationError


class TestManifestParser:
    """Test cases for ManifestParser class."""

    def test_init(self):
        """Test ManifestParser initialization."""
        parser = ManifestParser()
        assert parser is not None

    def test_parse_valid_manifest(self, temp_dir: Path):
        """Test parsing a valid agent manifest."""
        parser = ManifestParser()

        # Create a valid manifest
        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "python_version": "3.11+",
            "interface": {
                "methods": {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {"input": {"type": "string", "required": True}},
                        "returns": {"type": "string"},
                    }
                }
            },
            "dependencies": ["requests>=2.31.0"],
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        result = parser.parse_manifest(str(manifest_file))

        assert result["name"] == "test-agent"
        assert result["version"] == "1.0.0"
        assert "interface" in result
        assert "methods" in result["interface"]
        assert "test_method" in result["interface"]["methods"]

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent manifest file."""
        parser = ManifestParser()

        with pytest.raises(ManifestValidationError, match="Manifest file not found"):
            parser.parse_manifest("/nonexistent/agent.yaml")

    def test_parse_invalid_yaml(self, temp_dir: Path):
        """Test parsing invalid YAML file."""
        parser = ManifestParser()

        # Create invalid YAML
        manifest_file = temp_dir / "agent.yaml"
        manifest_file.write_text("invalid: yaml: content: [[[")

        with pytest.raises(ManifestValidationError, match="Invalid YAML syntax"):
            parser.parse_manifest(str(manifest_file))

    def test_validate_missing_required_fields(self, temp_dir: Path):
        """Test validation of manifest missing required fields."""
        parser = ManifestParser()

        # Create manifest missing required fields
        manifest_data = {"description": "Missing required fields"}

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(ManifestValidationError, match="Missing required field"):
            parser.parse_manifest(str(manifest_file))

    def test_validate_invalid_interface(self, temp_dir: Path):
        """Test validation of invalid interface structure."""
        parser = ManifestParser()

        # Create manifest with invalid interface
        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "interface": {"methods": "invalid_methods_structure"},  # Should be dict
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(
            ManifestValidationError, match="Invalid interface structure"
        ):
            parser.parse_manifest(str(manifest_file))

    def test_validate_empty_methods(self, temp_dir: Path):
        """Test validation when methods are empty."""
        parser = ManifestParser()

        # Create manifest with empty methods
        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "interface": {"methods": {}},
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(ManifestValidationError, match="No methods defined"):
            parser.parse_manifest(str(manifest_file))

    def test_validate_method_structure(self, temp_dir: Path):
        """Test validation of method structure."""
        parser = ManifestParser()

        # Create manifest with invalid method structure
        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "interface": {
                "methods": {"invalid_method": "not_a_dict"}  # Should be dict
            },
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(ManifestValidationError, match="Invalid method definition"):
            parser.parse_manifest(str(manifest_file))

    def test_get_methods(self, temp_dir: Path):
        """Test getting methods from parsed manifest."""
        parser = ManifestParser()

        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "interface": {
                "methods": {
                    "method1": {"description": "First method"},
                    "method2": {"description": "Second method"},
                }
            },
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = parser.parse_manifest(str(manifest_file))
        methods = parser.get_methods(manifest)

        assert len(methods) == 2
        assert "method1" in methods
        assert "method2" in methods

    def test_get_dependencies(self, temp_dir: Path):
        """Test getting dependencies from parsed manifest."""
        parser = ManifestParser()

        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "interface": {"methods": {"test": {"description": "Test"}}},
            "dependencies": ["requests>=2.31.0", "numpy>=1.20.0"],
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = parser.parse_manifest(str(manifest_file))
        dependencies = parser.get_dependencies(manifest)

        assert len(dependencies) == 2
        assert "requests>=2.31.0" in dependencies
        assert "numpy>=1.20.0" in dependencies

    def test_get_dependencies_empty(self, temp_dir: Path):
        """Test getting dependencies when none are specified."""
        parser = ManifestParser()

        manifest_data = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "Test agent",
            "author": "Test Author",
            "interface": {"methods": {"test": {"description": "Test"}}},
        }

        manifest_file = temp_dir / "agent.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = parser.parse_manifest(str(manifest_file))
        dependencies = parser.get_dependencies(manifest)

        assert dependencies == []
