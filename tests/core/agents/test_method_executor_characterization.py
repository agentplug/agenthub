"""Characterization tests: pin MethodExecutor's current parameter-mapping
and file-path-resolution behavior.

Several pinned behaviors are known quirks the hardening program intends to
change (raw ``args`` pass-through when the interface declares no parameters,
required-parameter validation only running on the mixed args+kwargs path,
the stringly ``_looks_like_file_path`` heuristic). They are pinned so the
change is deliberate and shimmed, not accidental.
"""

import os
from unittest.mock import Mock

import pytest

from agenthub.core.agents.method_executor import MethodExecutor
from agenthub.core.tools.exceptions import AgentExecutionError


def make_wrapper(methods=None, method_info=None, runtime=None, agent_path=""):
    wrapper = Mock()
    wrapper.name = "bot"
    wrapper.namespace = "acme"
    wrapper.agent_info.methods = methods or ["summarize"]
    wrapper.agent_info.has_method.side_effect = (
        lambda m: m in wrapper.agent_info.methods
    )
    wrapper.agent_info.get_method_info.side_effect = lambda m: (
        method_info or {"description": f"Execute {m}", "parameters": {}}
    )
    wrapper.agent_info.path = agent_path
    wrapper.runtime = runtime
    wrapper.get_tool_context.return_value = {}
    return wrapper


def make_runtime():
    runtime = Mock()
    runtime.execute_agent.return_value = {"ok": True}
    return runtime


def captured_parameters(runtime):
    return runtime.execute_agent.call_args.kwargs["parameters"]


class TestUnknownMethod:
    def test_raises_with_available_methods_listed(self):
        executor = MethodExecutor(make_wrapper())
        with pytest.raises(AgentExecutionError) as exc_info:
            executor.execute("nope", {})
        assert "Method 'nope' not found in agent 'bot'" in str(exc_info.value)
        assert "Available methods: summarize" in str(exc_info.value)


class TestParameterMapping:
    def test_kwargs_pass_through_unchanged(self):
        runtime = make_runtime()
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        executor.execute("summarize", {"text": "hi", "style": "short"})
        assert captured_parameters(runtime) == {"text": "hi", "style": "short"}

    def test_positional_args_map_by_declared_order(self):
        runtime = make_runtime()
        info = {"parameters": {"text": {}, "style": {}}}
        executor = MethodExecutor(make_wrapper(method_info=info, runtime=runtime))
        executor.execute("summarize", {"args": ("hello", "formal")})
        assert captured_parameters(runtime) == {"text": "hello", "style": "formal"}

    def test_positional_args_do_not_override_kwargs(self):
        runtime = make_runtime()
        info = {"parameters": {"text": {}, "style": {}}}
        executor = MethodExecutor(make_wrapper(method_info=info, runtime=runtime))
        executor.execute("summarize", {"args": ("hello", "formal"), "style": "casual"})
        assert captured_parameters(runtime) == {
            "text": "hello",
            "style": "casual",
        }

    def test_args_pass_through_raw_when_no_schema(self):
        """Quirk: with no declared parameters, positional args reach the
        runtime as a literal ``args`` tuple. One release with a
        DeprecationWarning, then a typed error."""
        runtime = make_runtime()
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        with pytest.warns(DeprecationWarning, match="Positional arguments"):
            executor.execute("summarize", {"args": ("hello",)})
        assert captured_parameters(runtime) == {"args": ("hello",)}

    def test_mixed_args_kwargs_pass_through_raw_when_no_schema(self):
        runtime = make_runtime()
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        with pytest.warns(DeprecationWarning, match="Positional arguments"):
            executor.execute("summarize", {"args": ("hello",), "style": "short"})
        assert captured_parameters(runtime) == {
            "args": ("hello",),
            "style": "short",
        }


class TestRequiredValidation:
    def test_missing_required_raises_on_mixed_path(self):
        """The mixed path (truthy args + kwargs + declared schema) is the
        only path that validates required parameters."""
        info = {"parameters": {"text": {}, "style": {"required": True}}}
        executor = MethodExecutor(make_wrapper(method_info=info))
        with pytest.raises(AgentExecutionError, match="Missing required parameters"):
            executor.execute("summarize", {"args": ("hello",), "other": 1})

    def test_kwargs_only_path_skips_required_validation(self):
        """Quirk: required-parameter validation only runs on the mixed
        args+kwargs path; a kwargs-only call with a missing required
        parameter reaches the runtime unvalidated."""
        runtime = make_runtime()
        info = {"parameters": {"text": {"required": True}}}
        executor = MethodExecutor(make_wrapper(method_info=info, runtime=runtime))
        executor.execute("summarize", {"other": 1})
        assert captured_parameters(runtime) == {"other": 1}


class TestFilePathHeuristic:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("/abs/path", True),
            ("relative/file.txt", True),
            ("win\\path", True),
            ("report.pdf", True),
            ("a.py", False),  # quirk: len <= 4 short-circuits the extension check
            ("plain string", False),
            ("https://example.com", True),  # quirk: URLs classify as file paths
        ],
    )
    def test_truth_table(self, value, expected):
        executor = MethodExecutor(make_wrapper())
        assert executor._looks_like_file_path(value) is expected

    def test_relative_path_resolved_against_agent_path(self, tmp_path):
        """Undeclared parameter + path-like value: the legacy heuristic
        still resolves for one release, with a DeprecationWarning."""
        (tmp_path / "data.txt").write_text("x")
        runtime = make_runtime()
        executor = MethodExecutor(
            make_wrapper(runtime=runtime, agent_path=str(tmp_path))
        )
        with pytest.warns(DeprecationWarning, match="no declared"):
            executor.execute("summarize", {"file": "data.txt"})
        assert captured_parameters(runtime)["file"] == os.path.abspath(
            tmp_path / "data.txt"
        )

    def test_unresolvable_path_string_passes_through(self):
        runtime = make_runtime()
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        with pytest.warns(DeprecationWarning, match="no declared"):
            executor.execute("summarize", {"file": "/nonexistent/dir/file.txt"})
        assert captured_parameters(runtime)["file"] == "/nonexistent/dir/file.txt"

    def test_non_path_strings_untouched(self):
        runtime = make_runtime()
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        executor.execute("summarize", {"text": "just some words"})
        assert captured_parameters(runtime)["text"] == "just some words"


class TestSchemaAwarePathResolution:
    """The manifest-driven contract replacing the string heuristic:
    declared file-path types resolve, everything else passes through."""

    def file_schema_wrapper(self, runtime, agent_path=""):
        return make_wrapper(
            method_info={
                "parameters": {
                    "file": {"type": "file"},
                    "text": {"type": "string"},
                }
            },
            runtime=runtime,
            agent_path=agent_path,
        )

    def test_declared_file_type_resolves_without_warning(self, tmp_path, recwarn):
        (tmp_path / "data.txt").write_text("x")
        runtime = make_runtime()
        executor = MethodExecutor(
            self.file_schema_wrapper(runtime, agent_path=str(tmp_path))
        )
        executor.execute("summarize", {"file": "data.txt"})
        assert captured_parameters(runtime)["file"] == os.path.abspath(
            tmp_path / "data.txt"
        )
        assert not [
            w for w in recwarn.list if issubclass(w.category, DeprecationWarning)
        ]

    def test_declared_file_type_unresolvable_passes_through(self, recwarn):
        runtime = make_runtime()
        executor = MethodExecutor(self.file_schema_wrapper(runtime))
        executor.execute("summarize", {"file": "/nonexistent/dir/file.txt"})
        assert captured_parameters(runtime)["file"] == "/nonexistent/dir/file.txt"
        assert not [
            w for w in recwarn.list if issubclass(w.category, DeprecationWarning)
        ]

    def test_declared_string_type_never_rewritten(self, tmp_path, recwarn):
        """The fix at the heart of Phase 3: a parameter declared as a plain
        string keeps its value even when it looks exactly like a file path
        that exists relative to the agent."""
        (tmp_path / "data.txt").write_text("x")
        runtime = make_runtime()
        executor = MethodExecutor(
            self.file_schema_wrapper(runtime, agent_path=str(tmp_path))
        )
        executor.execute("summarize", {"text": "data.txt"})
        assert captured_parameters(runtime)["text"] == "data.txt"
        assert not [
            w for w in recwarn.list if issubclass(w.category, DeprecationWarning)
        ]


class TestExecutionContract:
    def test_tool_context_passed_to_runtime_as_dict(self):
        """The wrapper builds the tool-context document once; the runtime
        receives the dict. (Pinned as a JSON-string round-trip until Phase 2
        removed the serialize→deserialize hop between wrapper and executor.)"""
        runtime = make_runtime()
        wrapper = make_wrapper(runtime=runtime)
        wrapper.get_tool_context.return_value = {"available_tools": ["t1"]}
        executor = MethodExecutor(wrapper)
        executor.execute("summarize", {})
        tool_context = runtime.execute_agent.call_args.kwargs["tool_context"]
        assert tool_context == {"available_tools": ["t1"]}

    def test_runtime_receives_namespace_name_method(self):
        runtime = make_runtime()
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        executor.execute("summarize", {"text": "hi"})
        call = runtime.execute_agent.call_args.kwargs
        assert call["namespace"] == "acme"
        assert call["agent_name"] == "bot"
        assert call["method"] == "summarize"

    def test_no_runtime_returns_fallback_dict(self):
        executor = MethodExecutor(make_wrapper(runtime=None))
        result = executor.execute("summarize", {"text": "hi"})
        assert result == {
            "result": "Method 'summarize' executed with parameters: {'text': 'hi'}"
        }

    def test_runtime_failure_wrapped_in_agent_execution_error(self):
        runtime = make_runtime()
        runtime.execute_agent.side_effect = RuntimeError("boom")
        executor = MethodExecutor(make_wrapper(runtime=runtime))
        with pytest.raises(AgentExecutionError) as exc_info:
            executor.execute("summarize", {})
        assert "Failed to execute method 'summarize': boom" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, RuntimeError)
