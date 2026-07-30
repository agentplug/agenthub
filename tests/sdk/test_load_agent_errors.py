"""Error-path tests for the SDK load_agent entry point.

Pins the typed auto-install trigger: a missing agent raises
AgentNotFoundError (caught to auto-install); an invalid agent raises
plain AgentLoadError (no install attempt) — no message-text matching.
"""

from unittest.mock import patch

import pytest

import agenthub as ah
from agenthub.core.agents.loader import AgentLoadError, AgentNotFoundError


class TestAutoInstallTrigger:
    def test_missing_agent_triggers_auto_install(self):
        with (
            patch(
                "agenthub.sdk.load_agent._load_agent_from_yaml",
                side_effect=AgentNotFoundError("Agent not found: ns/missing"),
            ),
            patch(
                "agenthub.sdk.load_agent._auto_install_agent",
                side_effect=RuntimeError("install attempted"),
            ) as install,
        ):
            with pytest.raises(AgentLoadError, match="Failed to auto-install"):
                ah.load_agent("ns/missing")
            install.assert_called_once_with("ns/missing")

    def test_invalid_agent_does_not_trigger_install(self):
        """A structurally invalid agent must surface its error, not be
        re-installed over — even if its message happens to contain the
        words 'not found' (the old string-matching bug)."""
        with (
            patch(
                "agenthub.sdk.load_agent._load_agent_from_yaml",
                side_effect=AgentLoadError("agent.py not found in manifest"),
            ),
            patch("agenthub.sdk.load_agent._auto_install_agent") as install,
        ):
            with pytest.raises(AgentLoadError, match="not found in manifest"):
                ah.load_agent("ns/broken")
            install.assert_not_called()

    def test_not_found_is_a_load_error(self):
        # Existing except AgentLoadError handlers keep catching it.
        assert issubclass(AgentNotFoundError, AgentLoadError)
