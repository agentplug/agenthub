"""Tests for agent trust-model hardening.

Covers: symlinked agent scripts, sys.path hygiene after dynamic loading,
storage discovery of escaping symlinks, post-clone repository validation,
and knowledge-validator strictness.
"""

import os
import sys

import pytest

from agenthub.core.agents.dynamic_executor import (
    DynamicAgentExecutor,
    DynamicExecutionError,
)
from agenthub.core.knowledge.validator import KnowledgeValidator
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.storage.local_storage import LocalStorage

MINIMAL_MANIFEST = """\
name: test-agent
version: 1.0.0
description: Test fixture agent
author: tests
interface:
  methods:
    ping:
      description: Ping method
"""

AGENT_SCRIPT = """\
class Agent:
    def ping(self):
        return {"pong": True}
"""


def make_agent_dir(base, name="agent"):
    agent_dir = base / name
    agent_dir.mkdir(parents=True)
    (agent_dir / "agent.py").write_text(AGENT_SCRIPT)
    (agent_dir / "agent.yaml").write_text(MINIMAL_MANIFEST)
    return agent_dir


class TestDynamicExecutorHardening:
    def test_symlinked_script_outside_agent_dir_refused(self, tmp_path):
        outside = tmp_path / "outside.py"
        outside.write_text(AGENT_SCRIPT)
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        (agent_dir / "agent.yaml").write_text(MINIMAL_MANIFEST)
        os.symlink(outside, agent_dir / "agent.py")

        executor = DynamicAgentExecutor()
        with pytest.raises(DynamicExecutionError, match="resolves outside"):
            executor._load_agent_class(str(agent_dir))

    def test_normal_agent_loads(self, tmp_path):
        agent_dir = make_agent_dir(tmp_path)
        executor = DynamicAgentExecutor()
        agent_class = executor._load_agent_class(str(agent_dir))
        assert agent_class().ping() == {"pong": True}

    def test_sys_path_not_polluted_after_load(self, tmp_path):
        agent_dir = make_agent_dir(tmp_path)
        executor = DynamicAgentExecutor()
        executor._load_agent_class(str(agent_dir))
        assert str(agent_dir) not in sys.path

    def test_sibling_import_still_works_during_load(self, tmp_path):
        agent_dir = make_agent_dir(tmp_path)
        (agent_dir / "helper_mod_xyz.py").write_text("VALUE = 41\n")
        (agent_dir / "agent.py").write_text(
            "import helper_mod_xyz\n\n"
            "class Agent:\n"
            "    def ping(self):\n"
            "        return {'pong': helper_mod_xyz.VALUE + 1}\n"
        )
        executor = DynamicAgentExecutor()
        agent_class = executor._load_agent_class(str(agent_dir))
        assert agent_class().ping() == {"pong": 42}
        assert str(agent_dir) not in sys.path
        sys.modules.pop("helper_mod_xyz", None)


class TestStorageDiscoveryHardening:
    def test_symlinked_agent_dir_outside_storage_ignored(self, tmp_path):
        storage_base = tmp_path / "store"
        outside_agent = make_agent_dir(tmp_path, "elsewhere")
        agents_dir = storage_base / "agents" / "ns"
        agents_dir.mkdir(parents=True)
        os.symlink(outside_agent, agents_dir / "linked-agent")

        storage = LocalStorage(base_dir=storage_base)
        assert not storage._is_valid_agent_directory(agents_dir / "linked-agent")

    def test_real_agent_dir_valid(self, tmp_path):
        storage_base = tmp_path / "store"
        agents_dir = storage_base / "agents" / "ns"
        agents_dir.mkdir(parents=True)
        agent_dir = make_agent_dir(agents_dir, "real-agent")

        storage = LocalStorage(base_dir=storage_base)
        assert storage._is_valid_agent_directory(agent_dir)


class TestPostCloneValidation:
    def make_cloner(self):
        return RepositoryCloner()

    def test_valid_repository_passes(self, tmp_path):
        repo = make_agent_dir(tmp_path, "repo")
        assert self.make_cloner()._validate_cloned_repository(repo) is None

    def test_missing_config_rejected(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "agent.py").write_text(AGENT_SCRIPT)
        error = self.make_cloner()._validate_cloned_repository(repo)
        assert error is not None and "agent.yaml" in error

    def test_missing_script_rejected(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "agent.yaml").write_text(MINIMAL_MANIFEST)
        error = self.make_cloner()._validate_cloned_repository(repo)
        assert error is not None and "agent.py" in error

    def test_invalid_manifest_rejected_with_field_errors(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "agent.py").write_text(AGENT_SCRIPT)
        (repo / "agent.yaml").write_text("name: t\n")
        error = self.make_cloner()._validate_cloned_repository(repo)
        assert error is not None
        # Install-time schema validation names the missing fields.
        assert "version: Field required" in error
        assert "interface: Field required" in error

    def test_escaping_symlink_rejected(self, tmp_path):
        repo = make_agent_dir(tmp_path, "repo")
        secret = tmp_path / "secret.txt"
        secret.write_text("credentials")
        os.symlink(secret, repo / "data.txt")
        error = self.make_cloner()._validate_cloned_repository(repo)
        assert error is not None and "escapes repository" in error

    def test_internal_symlink_allowed(self, tmp_path):
        repo = make_agent_dir(tmp_path, "repo")
        (repo / "docs.md").write_text("readme")
        os.symlink(repo / "docs.md", repo / "README.md")
        assert self.make_cloner()._validate_cloned_repository(repo) is None


class TestKnowledgeValidatorStrictness:
    SUSPICIOUS = "Use subprocess to run commands for the task at hand."

    def test_default_warns(self):
        result = KnowledgeValidator().validate_knowledge(self.SUSPICIOUS)
        assert result.is_valid
        assert any("problematic" in warning for warning in result.warnings)

    def test_strict_rejects(self):
        result = KnowledgeValidator(strict=True).validate_knowledge(self.SUSPICIOUS)
        assert not result.is_valid
        assert any("problematic" in error for error in result.errors)

    def test_env_var_enables_strict(self, monkeypatch):
        monkeypatch.setenv("AGENTHUB_KNOWLEDGE_STRICT", "1")
        result = KnowledgeValidator().validate_knowledge(self.SUSPICIOUS)
        assert not result.is_valid

    def test_clean_knowledge_valid_in_strict(self):
        result = KnowledgeValidator(strict=True).validate_knowledge(
            "The capital of France is Paris and croissants are pastries."
        )
        assert result.is_valid


class TestLazySiblingImports:
    def test_method_body_import_of_sibling_works(self, tmp_path):
        """Codex P1 regression: agents deferring sibling imports into
        method bodies must still resolve them at call time."""
        agent_dir = make_agent_dir(tmp_path)
        (agent_dir / "lazy_helper_xyz.py").write_text("VALUE = 99\n")
        (agent_dir / "agent.py").write_text(
            "class Agent:\n"
            "    def ping(self):\n"
            "        import lazy_helper_xyz\n"
            "        return {'pong': lazy_helper_xyz.VALUE}\n"
        )
        executor = DynamicAgentExecutor()
        result = executor.execute_agent_method(str(agent_dir), "ping", {})
        assert result == {"result": {"pong": 99}}
        assert str(agent_dir) not in sys.path
        sys.modules.pop("lazy_helper_xyz", None)
