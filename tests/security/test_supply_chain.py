"""Supply-chain tests: install provenance recording and ref-pinned installs.

Uses a real local git repository as the 'remote' (file:// clone), so git
behavior is genuine end to end.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from agenthub.github.repository_cloner import CloneError, RepositoryCloner
from agenthub.github.url_parser import parse_agent_spec


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


@pytest.fixture
def agent_repo(tmp_path):
    """A two-commit agent repository; returns (repo_path, sha_v1, sha_v2)."""
    repo = tmp_path / "src-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    git(repo, "config", "user.email", "test@test.invalid")
    git(repo, "config", "user.name", "Test")
    (repo / "agent.yaml").write_text(
        "name: pinned-agent\nversion: 1.0.0\n"
        "description: Pinned test agent\nauthor: tests\n"
        "interface:\n  methods:\n    ping:\n      description: Ping\n"
    )
    (repo / "agent.py").write_text("VERSION = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "v1")
    sha_v1 = git(repo, "rev-parse", "HEAD")
    (repo / "agent.py").write_text("VERSION = 2\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "v2")
    sha_v2 = git(repo, "rev-parse", "HEAD")
    return repo, sha_v1, sha_v2


@pytest.fixture
def cloner(tmp_path, agent_repo):
    repo, _, _ = agent_repo
    instance = RepositoryCloner(base_storage_path=str(tmp_path / "store"))
    patcher = patch.object(
        instance.url_parser, "build_github_url", return_value=str(repo)
    )
    patcher.start()
    yield instance
    patcher.stop()


class TestParseAgentSpec:
    def test_plain_name(self):
        assert parse_agent_spec("user/agent") == ("user/agent", None)

    def test_pinned_sha(self):
        assert parse_agent_spec("user/agent@a1b2c3d") == ("user/agent", "a1b2c3d")

    def test_tag_with_dots_and_slashes(self):
        assert parse_agent_spec("u/a@release/v1.2") == ("u/a", "release/v1.2")

    def test_empty_or_malformed_ref_rejected(self):
        with pytest.raises(ValueError):
            parse_agent_spec("user/agent@")
        with pytest.raises(ValueError):
            parse_agent_spec("user/agent@ bad ref")


class TestInstallProvenance:
    def test_install_records_resolved_sha(self, cloner, agent_repo):
        _, _, sha_v2 = agent_repo
        result = cloner.clone_agent("user/pinned-agent")
        assert result.success
        assert result.commit_sha == sha_v2

        metadata = cloner.get_install_metadata("user/pinned-agent")
        assert metadata is not None
        assert metadata["commit_sha"] == sha_v2
        assert metadata["requested_ref"] is None
        assert metadata["agent_name"] == "user/pinned-agent"

    def test_pinned_install_checks_out_exact_commit(self, cloner, agent_repo):
        _, sha_v1, sha_v2 = agent_repo
        result = cloner.clone_agent(f"user/pinned-agent@{sha_v1}")
        assert result.success
        assert result.commit_sha == sha_v1
        assert result.commit_sha != sha_v2

        # The working tree is the pinned version, not HEAD.
        agent_py = Path(result.local_path) / "agent.py"
        assert agent_py.read_text() == "VERSION = 1\n"

        metadata = cloner.get_install_metadata("user/pinned-agent")
        assert metadata["requested_ref"] == sha_v1
        # Storage path carries no @ref suffix.
        assert "@" not in result.local_path

    def test_unresolvable_ref_fails_and_removes_clone(self, cloner, tmp_path):
        with pytest.raises(CloneError, match="could not be checked out"):
            cloner.clone_agent("user/pinned-agent@deadbeef123456")
        assert not (tmp_path / "store" / "user" / "pinned-agent").exists()

    def test_metadata_absent_for_unknown_agent(self, cloner):
        assert cloner.get_install_metadata("user/never-installed") is None

    def test_metadata_file_not_a_validation_hazard(self, cloner):
        """The provenance file must not break structure validation."""
        result = cloner.clone_agent("user/pinned-agent")
        assert cloner._validate_cloned_repository(Path(result.local_path)) is None
