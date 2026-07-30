"""Typed solve() error contract: engine raises, wrapper shims for one release."""

from unittest.mock import Mock, patch

import pytest

from agenthub.core.agents.solve.engine import SolveEngine
from agenthub.core.tools.exceptions import AgentHubError, AgentSolveError


def make_engine(failing=True):
    engine = SolveEngine(Mock())
    behavior = (
        {"side_effect": RuntimeError("boom")}
        if failing
        else {"return_value": {"result": 42}}
    )
    patcher = patch.object(engine.framework_handler, "solve", **behavior)
    patcher.start()
    return engine, patcher


class TestEngineRaises:
    def test_failure_raises_typed(self):
        engine, patcher = make_engine()
        try:
            with pytest.raises(AgentSolveError, match="boom") as exc_info:
                engine.solve("do it")
            assert isinstance(exc_info.value.__cause__, RuntimeError)
        finally:
            patcher.stop()

    def test_typed_error_passes_through_unwrapped(self):
        engine = SolveEngine(Mock())
        with patch.object(
            engine.framework_handler,
            "solve",
            side_effect=AgentSolveError("already typed"),
        ):
            with pytest.raises(AgentSolveError, match="already typed"):
                engine.solve("q")

    def test_success_unchanged(self):
        engine, patcher = make_engine(failing=False)
        try:
            assert engine.solve("q") == {"result": 42}
        finally:
            patcher.stop()

    def test_hierarchy(self):
        assert issubclass(AgentSolveError, AgentHubError)


class TestWrapperShim:
    def make_wrapper(self):
        from agenthub.core.agents.wrapper import AgentWrapper

        wrapper = AgentWrapper.__new__(AgentWrapper)
        wrapper.solve_engine = Mock()
        wrapper.solve_engine.solve.side_effect = AgentSolveError("nope")
        return wrapper

    def test_default_returns_dict_with_deprecation(self):
        wrapper = self.make_wrapper()
        with pytest.warns(DeprecationWarning, match="raise_errors=True"):
            result = wrapper.solve("q")
        assert result == {"error": "nope"}

    def test_opt_in_raises(self):
        wrapper = self.make_wrapper()
        with pytest.raises(AgentSolveError, match="nope"):
            wrapper.solve("q", raise_errors=True)
