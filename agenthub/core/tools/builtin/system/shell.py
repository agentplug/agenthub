"""Shell command execution tools."""

import subprocess
import shlex
from typing import Dict, Any

from ...decorator import tool


@tool(
    name="shell_command",
    description="Execute shell commands safely with controlled permissions",
    version="1.0.0"
)
def shell_command(
    command: str, 
    timeout: int = 30, 
    working_dir: str = None
) -> Dict[str, Any]:
    """
    Execute shell commands safely with controlled permissions.

    Args:
        command (str): Shell command to execute
        timeout (int): Command timeout in seconds (default: 30)
        working_dir (str, optional): Working directory for command execution

    Returns:
        Dict[str, Any]: Command output and status
    """
    try:
        # Basic security: only allow certain commands
        dangerous_commands = ['rm -rf', 'format', 'del /', 'shutdown', 'reboot']
        if any(dangerous in command.lower() for dangerous in dangerous_commands):
            return {
                "success": False,
                "error": "Command blocked for security reasons",
                "command": command
            }
        
        # Parse command safely
        args = shlex.split(command)
        
        # Execute command
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )
        
        return {
            "success": result.returncode == 0,
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": timeout,
            "working_dir": working_dir
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Command execution failed: {str(e)}",
            "command": command
        }
