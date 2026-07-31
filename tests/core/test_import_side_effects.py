"""Import-time side-effect pins: importing agenthub must not mutate the
importing process's global logging state.

Runs in a subprocess so the test process's own logging configuration (or
other tests calling setup_logging) cannot pollute the assertion.
"""

import subprocess
import sys


def test_import_agenthub_leaves_logging_state_alone():
    code = (
        "import logging; "
        "import agenthub; "
        "noisy = ['mcp', 'mcp.client', 'urllib3', 'httpx', 'httpcore', 'requests']; "
        "bad = [n for n in noisy if logging.getLogger(n).disabled]; "
        "assert not bad, f'loggers disabled at import: {bad}'; "
        "print('OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_setup_logging_still_suppresses_mcp_http_chatter():
    """The suppression moved, it did not disappear: opting into AgentHub's
    logging setup keeps the pre-change quiet-by-default behavior."""
    code = (
        "import logging; "
        "from agenthub.core.logging import setup_logging; "
        "setup_logging(); "
        "assert logging.getLogger('mcp').disabled; "
        "assert logging.getLogger('httpx').disabled; "
        "print('OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout
