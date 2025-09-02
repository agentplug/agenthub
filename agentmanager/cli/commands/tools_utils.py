"""Shared utilities for CLI tool management commands."""

import json
import time
from typing import Optional

import requests
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def get_service_url(host: str = "127.0.0.1", port: int = 8000) -> str:
    """Get the service URL."""
    return f"http://{host}:{port}"


def check_service_health(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Check if the tool service is healthy."""
    try:
        response = requests.get(f"{get_service_url(host, port)}/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_service_info(host: str = "127.0.0.1", port: int = 8000) -> Optional[dict]:
    """Get service information."""
    try:
        response = requests.get(f"{get_service_url(host, port)}/tools/", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def wait_for_service_ready(host: str, port: int, max_wait: int = 10) -> bool:
    """Wait for service to be ready with progress indicator."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting service...", total=None)
        
        wait_time = 0
        while wait_time < max_wait:
            if check_service_health(host, port):
                progress.update(task, description="✅ Service started successfully!")
                return True
            time.sleep(0.5)
            wait_time += 0.5
        
        progress.update(task, description="❌ Service failed to start")
        return False


def ensure_service_running(host: str, port: int) -> None:
    """Ensure service is running, exit if not."""
    if not check_service_health(host, port):
        rprint(f"❌ [red]Tool service is not running on {get_service_url(host, port)}[/red]")
        rprint("💡 [dim]Use 'agenthub tools start' to start the service[/dim]")
        import sys
        sys.exit(1)


def output_json_or_rich(data: dict, error_msg: str = "Operation failed") -> None:
    """Output data in JSON format or show error."""
    try:
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
