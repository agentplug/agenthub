# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- `__version__` is now derived from package metadata (`pyproject.toml` is the
  single source of truth); the duplicate versions in `setup.py` and
  `agenthub/__init__.py` are gone.
- Development dependencies are declared once in
  `[project.optional-dependencies].dev`; the diverging `[dependency-groups]`
  section was removed.
- Project URLs corrected to point at `github.com/agentplug/agenthub`.

### Removed
- Legacy packaging files: `setup.py`, `setup.sh`, `setup.bat`, `setup.ps1`,
  `requirements.txt`, `MANIFEST.in` (the project builds with hatchling from
  `pyproject.toml`; install with `pip install agenthub-sdk` or
  `pip install -e ".[dev]"` for development).
- Dead code: `agenthub/core/agents/wrapper_old.py`,
  `agenthub/runtime/_deprecated/`,
  `agenthub/runtime/process_manager/_deprecated/`.

## [0.1.4] - 2026-03-06

Latest published release. See git history for details.
