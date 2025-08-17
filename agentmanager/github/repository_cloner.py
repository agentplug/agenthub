"""Repository Cloner for GitHub Integration.

This module provides functionality to clone GitHub repositories containing agents.
"""

import os
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .url_parser import URLParser

logger = logging.getLogger(__name__)


@dataclass
class CloneResult:
    """Result of a repository clone operation."""
    success: bool
    local_path: str
    agent_name: str
    github_url: str
    error_message: Optional[str] = None
    clone_time_seconds: Optional[float] = None


class CloneError(Exception):
    """Exception raised when repository cloning fails."""
    pass


class RepositoryNotFoundError(CloneError):
    """Exception raised when the repository is not found on GitHub."""
    pass


class GitNotAvailableError(CloneError):
    """Exception raised when git is not available on the system."""
    pass


class RepositoryCloner:
    """Clone GitHub repositories containing agents."""
    
    def __init__(self, base_storage_path: Optional[str] = None):
        """
        Initialize the repository cloner.
        
        Args:
            base_storage_path: Base directory where agents will be stored.
                              Defaults to '~/.agenthub/agents' in user's home directory.
        """
        self.url_parser = URLParser()
        # Use ~/.agenthub/agents as default storage path
        default_path = Path.home() / ".agenthub" / "agents"
        self.base_storage_path = Path(base_storage_path or default_path)
        
        # Ensure base storage directory exists
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"RepositoryCloner initialized with storage path: {self.base_storage_path}")
    
    def _check_git_available(self) -> bool:
        """
        Check if git is available on the system.
        
        Returns:
            bool: True if git is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            available = result.returncode == 0
            logger.debug(f"Git availability check: {available}")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Git not available on system")
            return False
    
    def _get_agent_storage_path(self, agent_name: str) -> Path:
        """
        Get the local storage path for an agent.
        
        Args:
            agent_name: Agent name in format "developer/agent-name"
            
        Returns:
            Path: Local path where the agent should be stored
        """
        # Replace slash with underscore for directory name to avoid path issues
        safe_name = agent_name.replace("/", "_")
        return self.base_storage_path / safe_name
    
    def _execute_git_clone(self, github_url: str, target_path: Path) -> subprocess.CompletedProcess:
        """
        Execute git clone command.
        
        Args:
            github_url: GitHub repository URL to clone
            target_path: Local path where repository should be cloned
            
        Returns:
            subprocess.CompletedProcess: Result of git clone command
        """
        cmd = ["git", "clone", github_url, str(target_path)]
        logger.debug(f"Executing git clone: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for large repositories
            )
            return result
        except subprocess.TimeoutExpired as e:
            logger.error(f"Git clone timed out after 5 minutes: {github_url}")
            raise CloneError(f"Clone operation timed out for {github_url}")
    
    def clone_agent(self, agent_name: str, target_path: Optional[str] = None) -> CloneResult:
        """
        Clone an agent repository from GitHub.
        
        Args:
            agent_name: Agent name in format "developer/agent-name"
            target_path: Optional custom path where to clone the repository.
                        If not provided, uses default storage path.
                        
        Returns:
            CloneResult: Result of the clone operation
            
        Raises:
            ValueError: If agent name format is invalid
            GitNotAvailableError: If git is not available on the system
            RepositoryNotFoundError: If the repository is not found
            CloneError: If cloning fails for other reasons
            
        Example:
            >>> cloner = RepositoryCloner()
            >>> result = cloner.clone_agent("user/awesome-agent")
            >>> if result.success:
            ...     print(f"Agent cloned to: {result.local_path}")
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting clone operation for agent: {agent_name}")
        
        # Validate agent name format
        if not self.url_parser.is_valid_agent_name(agent_name):
            error_msg = f"Invalid agent name format: {agent_name}. Expected format: 'developer/agent-name'"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if git is available
        if not self._check_git_available():
            error_msg = "Git is not available on this system. Please install git to clone repositories."
            logger.error(error_msg)
            raise GitNotAvailableError(error_msg)
        
        # Determine target path
        if target_path:
            local_path = Path(target_path)
        else:
            local_path = self._get_agent_storage_path(agent_name)
        
        # Check if directory already exists
        if local_path.exists():
            if local_path.is_dir() and any(local_path.iterdir()):
                error_msg = f"Directory already exists and is not empty: {local_path}"
                logger.warning(error_msg)
                # For now, we'll remove and re-clone. In production, we might want to update instead
                shutil.rmtree(local_path)
                logger.info(f"Removed existing directory: {local_path}")
        
        # Get GitHub URL
        github_url = self.url_parser.build_github_url(agent_name)
        logger.debug(f"GitHub URL: {github_url}")
        
        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Execute git clone
            result = self._execute_git_clone(github_url, local_path)
            clone_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned {agent_name} to {local_path} in {clone_time:.2f}s")
                return CloneResult(
                    success=True,
                    local_path=str(local_path),
                    agent_name=agent_name,
                    github_url=github_url,
                    clone_time_seconds=clone_time
                )
            else:
                # Check for specific error types
                stderr_lower = result.stderr.lower()
                
                if "repository not found" in stderr_lower or "not found" in stderr_lower:
                    error_msg = f"Repository not found: {github_url}"
                    logger.error(error_msg)
                    raise RepositoryNotFoundError(error_msg)
                
                # Generic clone error
                error_msg = f"Git clone failed: {result.stderr.strip()}"
                logger.error(error_msg)
                raise CloneError(error_msg)
                
        except (RepositoryNotFoundError, CloneError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            error_msg = f"Unexpected error during clone: {str(e)}"
            logger.error(error_msg)
            raise CloneError(error_msg)
    
    def is_agent_cloned(self, agent_name: str) -> bool:
        """
        Check if an agent is already cloned locally.
        
        Args:
            agent_name: Agent name in format "developer/agent-name"
            
        Returns:
            bool: True if agent is cloned locally, False otherwise
        """
        if not self.url_parser.is_valid_agent_name(agent_name):
            return False
        
        local_path = self._get_agent_storage_path(agent_name)
        exists = local_path.exists() and local_path.is_dir() and any(local_path.iterdir())
        
        logger.debug(f"Agent {agent_name} cloned status: {exists} (path: {local_path})")
        return exists
    
    def get_agent_path(self, agent_name: str) -> Optional[str]:
        """
        Get the local path of a cloned agent.
        
        Args:
            agent_name: Agent name in format "developer/agent-name"
            
        Returns:
            Optional[str]: Local path if agent is cloned, None otherwise
        """
        if self.is_agent_cloned(agent_name):
            return str(self._get_agent_storage_path(agent_name))
        return None
    
    def list_cloned_agents(self) -> Dict[str, str]:
        """
        List all cloned agents and their local paths.
        
        Returns:
            Dict[str, str]: Mapping of agent names to their local paths
        """
        cloned_agents = {}
        
        if not self.base_storage_path.exists():
            return cloned_agents
        
        for item in self.base_storage_path.iterdir():
            if item.is_dir() and any(item.iterdir()):  # Non-empty directory
                # Convert safe directory name back to agent name
                agent_name = item.name.replace("_", "/", 1)  # Only replace first underscore
                if self.url_parser.is_valid_agent_name(agent_name):
                    cloned_agents[agent_name] = str(item)
        
        logger.debug(f"Found {len(cloned_agents)} cloned agents")
        return cloned_agents
    
    def remove_agent(self, agent_name: str) -> bool:
        """
        Remove a cloned agent from local storage.
        
        Args:
            agent_name: Agent name in format "developer/agent-name"
            
        Returns:
            bool: True if agent was removed, False if not found
        """
        if not self.url_parser.is_valid_agent_name(agent_name):
            logger.warning(f"Invalid agent name for removal: {agent_name}")
            return False
        
        local_path = self._get_agent_storage_path(agent_name)
        
        if local_path.exists():
            try:
                shutil.rmtree(local_path)
                logger.info(f"Removed agent {agent_name} from {local_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to remove agent {agent_name}: {e}")
                return False
        else:
            logger.debug(f"Agent {agent_name} not found for removal")
            return False
