"""Advanced environment management for Python version migration and optimization."""

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agenthub.environment.environment_setup import EnvironmentSetup


@dataclass
class MigrationResult:
    """Result of environment migration operation."""

    success: bool
    source_agent: str
    target_agent: str
    source_python: str
    target_python: str
    migration_time: float
    backup_path: str | None = None
    error_message: str | None = None
    warnings: list[str] | None = None
    next_steps: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.next_steps is None:
            self.next_steps = []


@dataclass
class CloneResult:
    """Result of environment cloning operation."""

    success: bool
    source_agent: str
    target_agent: str
    clone_time: float
    source_path: str
    target_path: str
    error_message: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


@dataclass
class OptimizationResult:
    """Result of environment optimization."""

    success: bool
    agent_name: str
    original_size_mb: float
    optimized_size_mb: float
    space_saved_mb: float
    optimization_time: float
    actions_taken: list[str]
    error_message: str | None = None


class AdvancedEnvironmentManager:
    """Advanced environment management with migration, cloning, and optimization."""

    def __init__(self, base_storage_path: Path | None = None) -> None:
        self.base_storage_path = (
            base_storage_path or Path.home() / ".agenthub" / "agents"
        )
        self.env_setup = EnvironmentSetup()

    def migrate_python_version(
        self,
        agent_name: str,
        target_python_version: str,
        create_backup: bool = True,
        force: bool = False,
    ) -> MigrationResult:
        """Migrate an agent's environment to a different Python version."""
        start_time = time.time()

        try:
            # Validate agent exists
            agent_path = self._get_agent_path(agent_name)
            if not agent_path.exists():
                return MigrationResult(
                    success=False,
                    source_agent=agent_name,
                    target_agent=agent_name,
                    source_python="unknown",
                    target_python=target_python_version,
                    migration_time=time.time() - start_time,
                    error_message=f"Agent '{agent_name}' not found",
                )

            # Get current Python version
            current_version = self._get_current_python_version(agent_path)

            # Check if already on target version
            if current_version == target_python_version and not force:
                return MigrationResult(
                    success=True,
                    source_agent=agent_name,
                    target_agent=agent_name,
                    source_python=current_version,
                    target_python=target_python_version,
                    migration_time=time.time() - start_time,
                    warnings=[f"Already on Python {target_python_version}"],
                )

            # Create backup
            backup_path = None
            if create_backup:
                backup_path = self._create_backup(
                    agent_name, f"pre-migration-{target_python_version}"
                )

            # Remove existing environment
            venv_path = agent_path / ".venv"
            if venv_path.exists():
                shutil.rmtree(venv_path)

            # Set target Python version using UV_PYTHON environment variable
            import os

            original_env = os.environ.copy()
            os.environ["UV_PYTHON"] = target_python_version

            try:
                # Create new environment with target Python
                result = self.env_setup.setup_environment(str(agent_path))
            finally:
                # Restore original environment
                os.environ.clear()
                os.environ.update(original_env)

            if not result.success:
                return MigrationResult(
                    success=False,
                    source_agent=agent_name,
                    target_agent=agent_name,
                    source_python=current_version,
                    target_python=target_python_version,
                    migration_time=time.time() - start_time,
                    backup_path=backup_path,
                    error_message=result.error_message,
                    next_steps=result.next_steps or [],
                )

            # Verify new Python version
            new_version = self._get_current_python_version(agent_path)
            if new_version != target_python_version:
                return MigrationResult(
                    success=False,
                    source_agent=agent_name,
                    target_agent=agent_name,
                    source_python=current_version,
                    target_python=target_python_version,
                    migration_time=time.time() - start_time,
                    backup_path=backup_path,
                    error_message=(
                        f"Migration incomplete: expected {target_python_version}, "
                        f"got {new_version}"
                    ),
                )

            migration_time = time.time() - start_time

            return MigrationResult(
                success=True,
                source_agent=agent_name,
                target_agent=agent_name,
                source_python=current_version,
                target_python=target_python_version,
                migration_time=migration_time,
                backup_path=backup_path,
                next_steps=[
                    f"Successfully migrated from Python {current_version} to "
                    f"{target_python_version}",
                    "Environment recreated with new Python version",
                    "All dependencies reinstalled",
                ],
            )

        except Exception as e:
            return MigrationResult(
                success=False,
                source_agent=agent_name,
                target_agent=agent_name,
                source_python="unknown",
                target_python=target_python_version,
                migration_time=time.time() - start_time,
                error_message=str(e),
            )

    def clone_environment(
        self, source_agent: str, target_agent: str, include_env: bool = True
    ) -> CloneResult:
        """Clone an agent's environment to a new agent."""
        start_time = time.time()

        try:
            # Validate source agent
            source_path = self._get_agent_path(source_agent)
            if not source_path.exists():
                return CloneResult(
                    success=False,
                    source_agent=source_agent,
                    target_agent=target_agent,
                    clone_time=time.time() - start_time,
                    source_path=str(source_path),
                    target_path="",
                    error_message=f"Source agent '{source_agent}' not found",
                )

            # Check if target already exists
            target_path = self._get_agent_path(target_agent)
            if target_path.exists():
                return CloneResult(
                    success=False,
                    source_agent=source_agent,
                    target_agent=target_agent,
                    clone_time=time.time() - start_time,
                    source_path=str(source_path),
                    target_path=str(target_path),
                    error_message=f"Target agent '{target_agent}' already exists",
                )

            # Clone the agent directory
            shutil.copytree(source_path, target_path)

            # Update agent.yaml with new name
            manifest_path = target_path / "agent.yaml"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f) if manifest_path.suffix == ".json" else None

                if manifest and isinstance(manifest, dict):
                    manifest["name"] = target_agent.split("/")[-1]
                    with open(manifest_path, "w") as f:
                        json.dump(manifest, f, indent=2)

            clone_time = time.time() - start_time

            return CloneResult(
                success=True,
                source_agent=source_agent,
                target_agent=target_agent,
                clone_time=clone_time,
                source_path=str(source_path),
                target_path=str(target_path),
                warnings=["Remember to update agent-specific configurations"],
            )

        except Exception as e:
            return CloneResult(
                success=False,
                source_agent=source_agent,
                target_agent=target_agent,
                clone_time=time.time() - start_time,
                source_path=str(source_path) if "source_path" in locals() else "",
                target_path=str(target_path) if "target_path" in locals() else "",
                error_message=str(e),
            )

    def optimize_environment(self, agent_name: str) -> OptimizationResult:
        """Optimize an agent's environment for size and performance."""
        start_time = time.time()

        try:
            agent_path = self._get_agent_path(agent_name)
            if not agent_path.exists():
                return OptimizationResult(
                    success=False,
                    agent_name=agent_name,
                    original_size_mb=0,
                    optimized_size_mb=0,
                    space_saved_mb=0,
                    optimization_time=time.time() - start_time,
                    actions_taken=[],
                    error_message=f"Agent '{agent_name}' not found",
                )

            # Calculate original size
            original_size = self._calculate_directory_size(agent_path)

            actions_taken = []

            # Clean pip cache
            venv_path = agent_path / ".venv"
            if venv_path.exists():
                cache_dirs = [
                    venv_path / "__pycache__",
                    venv_path / "lib" / "python*" / "site-packages" / "__pycache__",
                ]

                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        shutil.rmtree(cache_dir)
                        actions_taken.append(f"Cleaned cache: {cache_dir}")

            # Clean build artifacts
            build_dirs = [
                agent_path / "build",
                agent_path / "dist",
                agent_path / "*.egg-info",
            ]

            for build_dir in build_dirs:
                if build_dir.exists():
                    shutil.rmtree(build_dir)
                    actions_taken.append(f"Removed build artifacts: {build_dir}")

            # Optimize with UV cache clean
            try:
                result = subprocess.run(
                    ["uv", "cache", "clean"], capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    actions_taken.append("Cleaned UV cache")
            except Exception:
                pass  # UV cache clean is optional

            optimized_size = self._calculate_directory_size(agent_path)
            space_saved = original_size - optimized_size
            optimization_time = time.time() - start_time

            return OptimizationResult(
                success=True,
                agent_name=agent_name,
                original_size_mb=original_size,
                optimized_size_mb=optimized_size,
                space_saved_mb=space_saved,
                optimization_time=optimization_time,
                actions_taken=actions_taken,
            )

        except Exception as e:
            return OptimizationResult(
                success=False,
                agent_name=agent_name,
                original_size_mb=0,
                optimized_size_mb=0,
                space_saved_mb=0,
                optimization_time=time.time() - start_time,
                actions_taken=[],
                error_message=str(e),
            )

    def analyze_dependencies(self, agent_name: str) -> dict[str, Any]:
        """Analyze agent dependencies for conflicts and issues."""
        try:
            agent_path = self._get_agent_path(agent_name)
            if not agent_path.exists():
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' not found",
                    "conflicts": [],
                    "recommendations": [],
                }

            venv_path = agent_path / ".venv"
            if not venv_path.exists():
                return {
                    "success": False,
                    "error": "No virtual environment found",
                    "conflicts": [],
                    "recommendations": ["Create environment first"],
                }

            # Get installed packages
            packages = self.env_setup._get_installed_packages(str(venv_path))

            # Check for conflicts using pip-audit or similar
            conflicts = []
            recommendations = []

            # Run pip-audit if available
            try:
                result = subprocess.run(
                    ["uv", "pip", "audit"],
                    cwd=str(venv_path),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0 and "vulnerability" in result.stdout.lower():
                    conflicts.append("Security vulnerabilities found")
                    recommendations.append("Update vulnerable packages")
            except Exception:
                pass  # pip-audit not available

            # Check for outdated packages
            try:
                result = subprocess.run(
                    ["uv", "pip", "list", "--outdated"],
                    cwd=str(venv_path),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.stdout.strip():
                    outdated_count = (
                        len(result.stdout.strip().split("\n")) - 2
                    )  # Skip headers
                    if outdated_count > 0:
                        recommendations.append(
                            f"Update {outdated_count} outdated packages"
                        )
            except Exception:
                pass

            return {
                "success": True,
                "packages": packages,
                "conflicts": conflicts,
                "recommendations": recommendations,
                "total_packages": len(packages),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "conflicts": [],
                "recommendations": [],
            }

    def list_python_versions(self) -> list[str]:
        """List available Python versions for migration."""
        try:
            result = subprocess.run(
                ["uv", "python", "list"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                versions = []
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line and not line.startswith(" ") and line.startswith("3."):
                        # Extract major.minor version (e.g., "3.11" from "3.11.0")
                        version_parts = line.split(".")
                        if len(version_parts) >= 2:
                            short_version = f"{version_parts[0]}.{version_parts[1]}"
                            if short_version not in versions:
                                versions.append(short_version)
                return versions
        except Exception:
            pass

        # Fallback versions
        return ["3.12", "3.11", "3.10", "3.9", "3.8"]

    def _get_agent_path(self, agent_name: str) -> Path:
        """Get the full path for an agent."""
        namespace, name = agent_name.split("/", 1)
        return self.base_storage_path / namespace / name

    def _get_current_python_version(self, agent_path: Path) -> str:
        """Get the current Python version for an agent."""
        try:
            venv_path = agent_path / ".venv"
            if not venv_path.exists():
                return "none"

            python_exe = venv_path / "bin" / "python"
            if not python_exe.exists():
                return "unknown"

            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip().replace("Python ", "")
        except Exception:
            pass

        return "unknown"

    def _create_backup(self, agent_name: str, suffix: str) -> str:
        """Create a backup of an agent before migration."""
        agent_path = self._get_agent_path(agent_name)
        backup_dir = Path.home() / ".agenthub" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{agent_name.replace('/', '_')}_{suffix}_{timestamp}"
        backup_path = backup_dir / backup_name

        # Remove existing backup if it exists
        if backup_path.exists():
            shutil.rmtree(backup_path)

        shutil.copytree(agent_path, backup_path)
        return str(backup_path)

    def _calculate_directory_size(self, path: Path) -> float:
        """Calculate directory size in MB."""
        try:
            total_size = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
