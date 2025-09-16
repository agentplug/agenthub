"""Tests for LocalStorage class."""

from pathlib import Path

from agenthub.storage.local_storage import LocalStorage


class TestLocalStorage:
    """Test cases for LocalStorage class."""

    def test_init_with_default_base_dir(self):
        """Test LocalStorage initialization with default base directory."""
        storage = LocalStorage()
        expected_base_dir = Path.home() / ".agenthub"
        assert storage._base_dir == expected_base_dir
        assert storage._agents_dir == expected_base_dir / "agents"
        assert storage._cache_dir == expected_base_dir / "cache"
        assert storage._config_dir == expected_base_dir / "config"
        assert storage._logs_dir == expected_base_dir / "logs"

    def test_init_with_custom_base_dir(self, temp_dir: Path):
        """Test LocalStorage initialization with custom base directory."""
        custom_base = temp_dir / "custom_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        assert storage._base_dir == custom_base
        assert storage._agents_dir == custom_base / "agents"
        assert storage._cache_dir == custom_base / "cache"
        assert storage._config_dir == custom_base / "config"
        assert storage._logs_dir == custom_base / "logs"

    def test_get_agenthub_dir_default(self):
        """Test get_agenthub_dir returns correct path with default base dir."""
        storage = LocalStorage()
        expected_path = Path.home() / ".agenthub"
        assert storage.get_agenthub_dir() == expected_path

    def test_get_agenthub_dir_custom(self, temp_dir: Path):
        """Test get_agenthub_dir returns correct path with custom base dir."""
        custom_base = temp_dir / "custom_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        assert storage.get_agenthub_dir() == custom_base

    def test_get_agents_dir_default(self):
        """Test get_agents_dir returns correct path with default base dir."""
        storage = LocalStorage()
        expected_path = Path.home() / ".agenthub" / "agents"
        assert storage.get_agents_dir() == expected_path

    def test_get_agents_dir_custom(self, temp_dir: Path):
        """Test get_agents_dir returns correct path with custom base dir."""
        custom_base = temp_dir / "custom_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        expected_path = custom_base / "agents"
        assert storage.get_agents_dir() == expected_path

    def test_initialize_storage_creates_directories(self, temp_dir: Path):
        """Test initialize_storage creates all necessary directories."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)

        # Verify directories don't exist initially
        assert not custom_base.exists()

        # Initialize storage
        storage.initialize_storage()

        # Verify all directories were created
        assert custom_base.exists()
        assert (custom_base / "agents").exists()
        assert (custom_base / "cache").exists()
        assert (custom_base / "config").exists()
        assert (custom_base / "logs").exists()

        # Verify they are directories
        assert custom_base.is_dir()
        assert (custom_base / "agents").is_dir()
        assert (custom_base / "cache").is_dir()
        assert (custom_base / "config").is_dir()
        assert (custom_base / "logs").is_dir()

    def test_initialize_storage_idempotent(self, temp_dir: Path):
        """Test initialize_storage can be called multiple times safely."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)

        # Initialize storage twice
        storage.initialize_storage()
        storage.initialize_storage()  # Should not raise error

        # Verify directories still exist
        assert custom_base.exists()
        assert (custom_base / "agents").exists()
        assert (custom_base / "cache").exists()
        assert (custom_base / "config").exists()
        assert (custom_base / "logs").exists()

    def test_initialize_storage_with_existing_directories(self, temp_dir: Path):
        """Test initialize_storage works when some directories already exist."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)

        # Create some directories manually
        custom_base.mkdir()
        (custom_base / "agents").mkdir()

        # Initialize storage - should create missing directories
        storage.initialize_storage()

        # Verify all directories exist
        assert custom_base.exists()
        assert (custom_base / "agents").exists()
        assert (custom_base / "cache").exists()
        assert (custom_base / "config").exists()
        assert (custom_base / "logs").exists()

    def test_discover_agents_empty_directory(self, temp_dir: Path):
        """Test discover_agents returns empty list when no agents are installed."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        agents = storage.discover_agents()
        assert agents == []

    def test_discover_agents_nonexistent_directory(self, temp_dir: Path):
        """Test discover_agents returns empty list when directory doesn't exist."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)

        agents = storage.discover_agents()
        assert agents == []

    def test_discover_agents_with_valid_agents(self, temp_dir: Path):
        """Test discover_agents finds valid agents."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        # Create a valid agent directory structure
        agent_dir = custom_base / "agents" / "testdev" / "test-agent"
        agent_dir.mkdir(parents=True)

        # Create required files
        (agent_dir / "agent.yaml").write_text("name: test-agent\nversion: 1.0.0")
        (agent_dir / "agent.py").write_text("# Test agent code")

        agents = storage.discover_agents()
        assert len(agents) == 1
        assert agents[0]["name"] == "test-agent"
        assert agents[0]["namespace"] == "testdev"
        assert agents[0]["path"] == str(agent_dir)
        assert agents[0]["version"] == "1.0.0"

    def test_discover_agents_with_multiple_agents(self, temp_dir: Path):
        """Test discover_agents finds multiple agents across namespaces."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        # Create multiple agents
        agents_base = custom_base / "agents"

        # Agent 1: testdev/agent1
        agent1_dir = agents_base / "testdev" / "agent1"
        agent1_dir.mkdir(parents=True)
        (agent1_dir / "agent.yaml").write_text("name: agent1\nversion: 1.0.0")
        (agent1_dir / "agent.py").write_text("# Agent 1 code")

        # Agent 2: testdev/agent2
        agent2_dir = agents_base / "testdev" / "agent2"
        agent2_dir.mkdir(parents=True)
        (agent2_dir / "agent.yaml").write_text("name: agent2\nversion: 2.0.0")
        (agent2_dir / "agent.py").write_text("# Agent 2 code")

        # Agent 3: otherdev/agent3
        agent3_dir = agents_base / "otherdev" / "agent3"
        agent3_dir.mkdir(parents=True)
        (agent3_dir / "agent.yaml").write_text("name: agent3\nversion: 1.5.0")
        (agent3_dir / "agent.py").write_text("# Agent 3 code")

        agents = storage.discover_agents()
        assert len(agents) == 3

        # Check that all agents are found
        agent_names = [agent["name"] for agent in agents]
        assert "agent1" in agent_names
        assert "agent2" in agent_names
        assert "agent3" in agent_names

        # Check namespaces
        testdev_agents = [agent for agent in agents if agent["namespace"] == "testdev"]
        otherdev_agents = [
            agent for agent in agents if agent["namespace"] == "otherdev"
        ]
        assert len(testdev_agents) == 2
        assert len(otherdev_agents) == 1

    def test_discover_agents_skips_invalid_agents(self, temp_dir: Path):
        """Test discover_agents skips agents missing required files."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        agents_base = custom_base / "agents" / "testdev"

        # Valid agent
        valid_agent = agents_base / "valid-agent"
        valid_agent.mkdir(parents=True)
        (valid_agent / "agent.yaml").write_text("name: valid-agent\nversion: 1.0.0")
        (valid_agent / "agent.py").write_text("# Valid agent code")

        # Invalid agent - missing agent.py
        invalid_agent1 = agents_base / "invalid-agent1"
        invalid_agent1.mkdir(parents=True)
        (invalid_agent1 / "agent.yaml").write_text("name: invalid-agent1")

        # Invalid agent - missing agent.yaml
        invalid_agent2 = agents_base / "invalid-agent2"
        invalid_agent2.mkdir(parents=True)
        (invalid_agent2 / "agent.py").write_text("# Invalid agent code")

        agents = storage.discover_agents()
        assert len(agents) == 1
        assert agents[0]["name"] == "valid-agent"

    def test_discover_agents_skips_hidden_directories(self, temp_dir: Path):
        """Test discover_agents skips hidden directories."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        agents_base = custom_base / "agents"

        # Valid agent
        valid_agent = agents_base / "testdev" / "valid-agent"
        valid_agent.mkdir(parents=True)
        (valid_agent / "agent.yaml").write_text("name: valid-agent")
        (valid_agent / "agent.py").write_text("# Valid agent code")

        # Hidden namespace directory
        hidden_namespace = agents_base / ".hidden-namespace"
        hidden_agent = hidden_namespace / "hidden-agent"
        hidden_agent.mkdir(parents=True)
        (hidden_agent / "agent.yaml").write_text("name: hidden-agent")
        (hidden_agent / "agent.py").write_text("# Hidden agent code")

        # Hidden agent directory
        visible_namespace = agents_base / "visible-namespace"
        hidden_agent2 = visible_namespace / ".hidden-agent"
        hidden_agent2.mkdir(parents=True)
        (hidden_agent2 / "agent.yaml").write_text("name: hidden-agent2")
        (hidden_agent2 / "agent.py").write_text("# Hidden agent code")

        agents = storage.discover_agents()
        assert len(agents) == 1
        assert agents[0]["name"] == "valid-agent"

    def test_discover_agents_handles_yaml_errors(self, temp_dir: Path):
        """Test discover_agents handles agents with invalid YAML gracefully."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        # Create agent with invalid YAML
        agent_dir = custom_base / "agents" / "testdev" / "broken-agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "agent.yaml").write_text(
            "name: broken-agent\nversion: [invalid yaml"
        )
        (agent_dir / "agent.py").write_text("# Broken agent code")

        agents = storage.discover_agents()
        assert len(agents) == 1
        assert agents[0]["name"] == "broken-agent"
        assert "version" not in agents[0]  # Version should be None due to YAML error

    def test_get_agent_path(self, temp_dir: Path):
        """Test get_agent_path returns correct path."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)

        agent_path = storage.get_agent_path("testdev", "test-agent")
        expected_path = custom_base / "agents" / "testdev" / "test-agent"
        assert agent_path == expected_path

    def test_agent_exists_with_valid_agent(self, temp_dir: Path):
        """Test agent_exists returns True for valid existing agent."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        # Create a valid agent
        agent_dir = custom_base / "agents" / "testdev" / "test-agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "agent.yaml").write_text("name: test-agent\nversion: 1.0.0")
        (agent_dir / "agent.py").write_text("# Test agent code")

        assert storage.agent_exists("testdev", "test-agent") is True

    def test_agent_exists_with_nonexistent_agent(self, temp_dir: Path):
        """Test agent_exists returns False for nonexistent agent."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        assert storage.agent_exists("testdev", "nonexistent-agent") is False

    def test_agent_exists_with_invalid_agent(self, temp_dir: Path):
        """Test agent_exists returns False for invalid agent."""
        custom_base = temp_dir / "test_agenthub"
        storage = LocalStorage(base_dir=custom_base)
        storage.initialize_storage()

        # Create an invalid agent (missing agent.py)
        agent_dir = custom_base / "agents" / "testdev" / "invalid-agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "agent.yaml").write_text("name: invalid-agent")

        assert storage.agent_exists("testdev", "invalid-agent") is False
