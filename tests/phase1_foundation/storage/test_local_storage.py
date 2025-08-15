"""Tests for LocalStorage class."""

from pathlib import Path

from agentmanager.storage.local_storage import LocalStorage


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
