"""Unit tests for tool metadata functionality."""

from agenthub.core.tools.metadata import ToolMetadata


class TestToolMetadata:
    """Test cases for ToolMetadata functionality."""

    def test_tool_metadata_creation(self):
        """Test basic ToolMetadata creation."""

        def test_function(param: str) -> str:
            return f"result: {param}"

        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            function=test_function,
            namespace="custom",
        )

        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool description"
        assert metadata.function == test_function
        assert metadata.namespace == "custom"
        assert metadata.parameters is not None
        assert metadata.return_type is not None
        assert metadata.examples is not None

    def test_tool_metadata_with_none_function(self):
        """Test ToolMetadata creation with None function (for MCP tools)."""
        metadata = ToolMetadata(
            name="mcp_tool",
            description="MCP tool description",
            function=None,
            namespace="mcp",
        )

        assert metadata.name == "mcp_tool"
        assert metadata.description == "MCP tool description"
        assert metadata.function is None
        assert metadata.namespace == "mcp"
        assert metadata.parameters == {}
        assert metadata.return_type == "Any"
        assert len(metadata.examples) > 0

    def test_parameter_extraction(self):
        """Test parameter extraction from function signature."""

        def test_function(
            required: str, optional: int = 42, keyword_only: str = "default"
        ) -> dict:
            """Test function with various parameter types."""
            return {
                "required": required,
                "optional": optional,
                "keyword_only": keyword_only,
            }

        metadata = ToolMetadata(
            name="param_tool",
            description="Tool with parameters",
            function=test_function,
            namespace="custom",
        )

        # Check parameters
        assert "required" in metadata.parameters
        assert "optional" in metadata.parameters
        assert "keyword_only" in metadata.parameters

        # Check parameter details
        required_param = metadata.parameters["required"]
        assert required_param["name"] == "required"
        assert required_param["required"] is True
        assert required_param["default"] is None

        optional_param = metadata.parameters["optional"]
        assert optional_param["name"] == "optional"
        assert optional_param["required"] is False
        assert optional_param["default"] == 42

        keyword_param = metadata.parameters["keyword_only"]
        assert keyword_param["name"] == "keyword_only"
        assert keyword_param["required"] is False
        assert keyword_param["default"] == "default"

    def test_parameter_extraction_with_type_annotations(self):
        """Test parameter extraction with type annotations."""

        def typed_function(param1: str, param2: int, param3: bool = True) -> dict:
            return {"param1": param1, "param2": param2, "param3": param3}

        metadata = ToolMetadata(
            name="typed_tool",
            description="Tool with type annotations",
            function=typed_function,
            namespace="custom",
        )

        # Check type annotations
        assert metadata.parameters["param1"]["type"] is str
        assert metadata.parameters["param2"]["type"] is int
        assert metadata.parameters["param3"]["type"] is bool

    def test_return_type_extraction(self):
        """Test return type extraction from function signature."""

        def string_function() -> str:
            return "string"

        def dict_function() -> dict:
            return {"key": "value"}

        def list_function() -> list:
            return [1, 2, 3]

        def no_annotation_function():
            return "no annotation"

        # Test string return type
        metadata1 = ToolMetadata(
            name="string_tool",
            description="String return type",
            function=string_function,
            namespace="custom",
        )
        assert metadata1.return_type == "str"

        # Test dict return type
        metadata2 = ToolMetadata(
            name="dict_tool",
            description="Dict return type",
            function=dict_function,
            namespace="custom",
        )
        assert metadata2.return_type == "dict"

        # Test list return type
        metadata3 = ToolMetadata(
            name="list_tool",
            description="List return type",
            function=list_function,
            namespace="custom",
        )
        assert metadata3.return_type == "list"

        # Test no annotation
        metadata4 = ToolMetadata(
            name="no_annotation_tool",
            description="No return type annotation",
            function=no_annotation_function,
            namespace="custom",
        )
        assert metadata4.return_type == "Any"

    def test_examples_generation(self):
        """Test usage examples generation."""

        def single_param_function(param: str) -> str:
            return f"result: {param}"

        def multi_param_function(param1: str, param2: int) -> str:
            return f"result: {param1}, {param2}"

        def no_param_function() -> str:
            return "no params"

        # Test single parameter
        metadata1 = ToolMetadata(
            name="single_param_tool",
            description="Single parameter tool",
            function=single_param_function,
            namespace="custom",
        )
        assert len(metadata1.examples) > 0
        assert any("single_param_tool" in example for example in metadata1.examples)

        # Test multiple parameters
        metadata2 = ToolMetadata(
            name="multi_param_tool",
            description="Multiple parameter tool",
            function=multi_param_function,
            namespace="custom",
        )
        assert len(metadata2.examples) > 0
        assert any("multi_param_tool" in example for example in metadata2.examples)

        # Test no parameters
        metadata3 = ToolMetadata(
            name="no_param_tool",
            description="No parameter tool",
            function=no_param_function,
            namespace="custom",
        )
        assert len(metadata3.examples) > 0
        assert any("no_param_tool()" in example for example in metadata3.examples)

    def test_examples_generation_with_none_function(self):
        """Test examples generation with None function."""
        metadata = ToolMetadata(
            name="mcp_tool", description="MCP tool", function=None, namespace="mcp"
        )

        assert len(metadata.examples) > 0
        assert any("mcp_tool()" in example for example in metadata.examples)

    def test_metadata_equality(self):
        """Test ToolMetadata equality comparison."""

        def test_function(param: str) -> str:
            return f"result: {param}"

        metadata1 = ToolMetadata(
            name="test_tool",
            description="Test tool",
            function=test_function,
            namespace="custom",
        )

        metadata2 = ToolMetadata(
            name="test_tool",
            description="Test tool",
            function=test_function,
            namespace="custom",
        )

        # Should be equal
        assert metadata1 == metadata2

        # Different name should not be equal
        metadata3 = ToolMetadata(
            name="different_tool",
            description="Test tool",
            function=test_function,
            namespace="custom",
        )
        assert metadata1 != metadata3

    def test_metadata_string_representation(self):
        """Test ToolMetadata string representation."""

        def test_function(param: str) -> str:
            return f"result: {param}"

        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            function=test_function,
            namespace="custom",
        )

        str_repr = str(metadata)
        assert "test_tool" in str_repr
        assert "Test tool description" in str_repr
        assert "custom" in str_repr

    def test_metadata_dict_conversion(self):
        """Test converting ToolMetadata to dictionary."""

        def test_function(param: str) -> str:
            return f"result: {param}"

        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            function=test_function,
            namespace="custom",
        )

        metadata_dict = metadata.to_dict()

        assert metadata_dict["name"] == "test_tool"
        assert metadata_dict["description"] == "Test tool description"
        assert metadata_dict["namespace"] == "custom"
        assert "parameters" in metadata_dict
        assert "return_type" in metadata_dict
        assert "examples" in metadata_dict

    def test_metadata_from_dict(self):
        """Test creating ToolMetadata from dictionary."""
        metadata_dict = {
            "name": "dict_tool",
            "description": "Tool from dict",
            "namespace": "custom",
            "parameters": {
                "param": {
                    "name": "param",
                    "type": str,
                    "required": True,
                    "default": None,
                }
            },
            "return_type": "str",
            "examples": ["dict_tool('example')"],
        }

        metadata = ToolMetadata.from_dict(metadata_dict)

        assert metadata.name == "dict_tool"
        assert metadata.description == "Tool from dict"
        assert metadata.namespace == "custom"
        assert metadata.return_type == "str"
        assert len(metadata.examples) > 0

    def test_metadata_validation(self):
        """Test ToolMetadata validation."""

        # Valid metadata
        def valid_function(param: str) -> str:
            return f"result: {param}"

        valid_metadata = ToolMetadata(
            name="valid_tool",
            description="Valid tool",
            function=valid_function,
            namespace="custom",
        )
        assert valid_metadata.validate() is True

        # Invalid metadata (empty name)
        invalid_metadata = ToolMetadata(
            name="",
            description="Invalid tool",
            function=valid_function,
            namespace="custom",
        )
        assert invalid_metadata.validate() is False

    def test_metadata_serialization(self):
        """Test ToolMetadata serialization for JSON."""

        def test_function(param: str) -> str:
            return f"result: {param}"

        metadata = ToolMetadata(
            name="serialize_tool",
            description="Tool for serialization",
            function=test_function,
            namespace="custom",
        )

        # Should be JSON serializable
        import json

        json_str = json.dumps(metadata.to_dict())
        assert json_str is not None

        # Should be deserializable
        loaded_dict = json.loads(json_str)
        assert loaded_dict["name"] == "serialize_tool"
        assert loaded_dict["description"] == "Tool for serialization"

    def test_metadata_with_complex_types(self):
        """Test ToolMetadata with complex parameter types."""

        def complex_function(
            string_list: list[str],
            int_dict: dict[str, int],
            optional_param: str | None = None,
            union_param: str | int = "default",
        ) -> dict[str, str | int | list[str]]:
            return {
                "string_list": string_list,
                "int_dict": int_dict,
                "optional_param": optional_param,
                "union_param": union_param,
            }

        metadata = ToolMetadata(
            name="complex_tool",
            description="Tool with complex types",
            function=complex_function,
            namespace="custom",
        )

        # Check that complex types are handled
        assert "string_list" in metadata.parameters
        assert "int_dict" in metadata.parameters
        assert "optional_param" in metadata.parameters
        assert "union_param" in metadata.parameters

        # Check return type
        assert "Dict" in metadata.return_type or "dict" in metadata.return_type

    def test_metadata_with_async_function(self):
        """Test ToolMetadata with async function."""
        import asyncio

        async def async_function(param: str) -> str:
            await asyncio.sleep(0.01)
            return f"async_result: {param}"

        metadata = ToolMetadata(
            name="async_tool",
            description="Async tool",
            function=async_function,
            namespace="custom",
        )

        assert metadata.name == "async_tool"
        assert metadata.function == async_function
        assert metadata.parameters["param"]["name"] == "param"
