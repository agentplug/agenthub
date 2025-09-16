# AgentHub User Guide

Complete guide for using AgentHub's auto-installation and management capabilities.

## 🚀 Overview

AgentHub is a powerful agent management system that can automatically discover, install, and manage AI agents from GitHub repositories. It uses UV-based isolated environments to ensure each agent runs in its own clean Python environment without dependency conflicts.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Programmatic API](#programmatic-api)
3. [CLI Commands](#cli-commands)
4. [Advanced Usage](#advanced-usage)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## ⚡ Quick Start

### Installation

```bash
# Install AgentHub
pip install agenthub

# Verify installation
agenthub --version
```

### Install Your First Agent

```bash
# Install an agent from GitHub
agenthub install agentplug/scientific-paper-analyzer

# Or programmatically
python -c "from agenthub import load_agent; agent = load_agent('agentplug/scientific-paper-analyzer')"
```

## 🔧 Programmatic API

### Basic Usage

```python
from agenthub import load_agent

# Auto-install and load an agent
agent = load_agent("agentplug/scientific-paper-analyzer")

# Use the agent
result = agent.analyze_paper(pdf_path="paper.pdf")
print(result)
```

### Advanced Installation

```python
from agenthub.github.auto_installer import AutoInstaller

# Create installer with environment setup
installer = AutoInstaller(setup_environment=True)

# Install agent with detailed results
result = installer.install_agent("developer/awesome-agent")

if result.success:
    print(f"Agent installed at: {result.local_path}")
    print(f"Environment created: {result.environment_result.venv_path}")
    print(f"Dependencies installed: {len(result.dependency_result.installed_packages)}")
else:
    print(f"Installation failed: {result.error_message}")
    print("Next steps:", result.next_steps)
```

### Environment Management

```python
from agenthub.environment.environment_manager import AdvancedEnvironmentManager

manager = AdvancedEnvironmentManager()

# Migrate Python version
result = manager.migrate_python_version(
    agent_name="developer/my-agent",
    target_python_version="3.11",
    create_backup=True
)

# Clone environment for testing
clone_result = manager.clone_environment(
    source_agent="production/agent",
    target_agent="dev/agent-copy"
)

# Optimize environment
opt_result = manager.optimize_environment("developer/my-agent")
print(f"Saved {opt_result.space_saved_mb} MB")
```

### Repository Management

```python
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator

# List installed agents
cloner = RepositoryCloner()
agents = cloner.list_cloned_agents()
for agent_name, path in agents.items():
    print(f"{agent_name}: {path}")

# Validate agent structure
validator = RepositoryValidator()
validation = validator.validate_repository("/path/to/agent")
if validation.is_valid:
    print("Agent structure is valid")
else:
    print("Issues found:", validation.validation_errors)
```

## 🖥️ CLI Commands

### Core Commands

#### Install Agents
```bash
# Basic installation
agenthub install developer/agent-name

# With custom path
agenthub install developer/agent-name --base-path /custom/path

# Skip environment setup (just clone)
agenthub install developer/agent-name --no-setup-environment

# Force reinstallation
agenthub install developer/agent-name --force
```

#### List Agents
```bash
# Simple list
agenthub list

# Detailed information
agenthub list --detailed

# With custom path
agenthub list --base-path /custom/path
```

#### Remove Agents
```bash
# Remove with confirmation (top-level command)
agenthub remove developer/agent-name

# Remove with confirmation (agent subcommand)
agenthub agent remove developer/agent-name

# Force removal without confirmation
agenthub remove developer/agent-name --force

# With custom path
agenthub remove developer/agent-name --base-path /custom/path
```

### Environment Management

#### Repair Broken Environments
```bash
# Interactive repair
agenthub repair developer/agent-name

# Force dependency reinstallation
agenthub repair developer/agent-name --force-reinstall-deps

# With custom path
agenthub repair developer/agent-name --base-path /custom/path
```

#### Migrate Python Versions
```bash
# Migrate to Python 3.11 with backup
agenthub migrate developer/agent-name 3.11

# Without backup
agenthub migrate developer/agent-name 3.11 --no-backup

# Force migration even if already on target
agenthub migrate developer/agent-name 3.11 --force
```

#### Clone Environments
```bash
# Clone with environment
agenthub clone production/agent dev/agent-copy

# Clone without environment
agenthub clone production/agent dev/agent-copy --no-include-env
```

#### Optimize Storage
```bash
# Optimize single agent
agenthub optimize developer/agent-name

# With custom path
agenthub optimize developer/agent-name --base-path /custom/path
```

### Backup & Restore

```bash
# Create backup
agenthub backup developer/agent-name

# Include virtual environment in backup
agenthub backup developer/agent-name --include-env

# Custom backup location
agenthub backup developer/agent-name --backup-path /backups/agents

# Restore from backup
agenthub restore /backups/agents/developer_agent_20240101_120000

# Restore with new name
agenthub restore /backups/agents/developer_agent_20240101_120000 --agent-name new/agent-name
```

### System Maintenance

#### Cleanup Operations
```bash
# Analyze what needs cleanup
agenthub cleanup --dry-run

# Remove invalid agents
agenthub cleanup --remove-invalid

# Remove broken environments
agenthub cleanup --remove-broken-envs

# Full cleanup
agenthub cleanup --remove-invalid --remove-broken-envs
```

#### Status & Analysis
```bash
# Status of all agents
agenthub status

# Status of specific agent
agenthub status developer/agent-name

# List available Python versions
agenthub python-versions

# Analyze dependencies
agenthub analyze-deps developer/agent-name
```

## 🎯 Advanced Usage

### Batch Operations

```bash
#!/bin/bash
# Batch install multiple agents
agents=(
    "agentplug/scientific-paper-analyzer"
    "agentplug/coding-agent"
    "agentplug/data-visualizer"
)

for agent in "${agents[@]}"; do
    echo "Installing $agent..."
    agenthub install "$agent" --setup-environment
    echo "---"
done
```

### Development Workflow

```python
# Development environment setup
import os
from agenthub.environment.environment_manager import AdvancedEnvironmentManager

manager = AdvancedEnvironmentManager()

# 1. Clone production agent for development
manager.clone_environment(
    source_agent="company/production-agent",
    target_agent="dev/my-user/production-agent-dev"
)

# 2. Test with different Python versions
versions = ["3.9", "3.10", "3.11"]
for version in versions:
    test_agent = f"dev/my-user/production-agent-py{version.replace('.', '')}"
    manager.clone_environment(
        source_agent="company/production-agent",
        target_agent=test_agent
    )
    manager.migrate_python_version(test_agent, version)

# 3. Optimize before deployment
manager.optimize_environment("company/production-agent")
```

### CI/CD Integration

```yaml
# .github/workflows/deploy-agents.yml
name: Deploy Agents
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install AgentHub
        run: pip install agenthub

      - name: Install required agents
        run: |
          agenthub install company/production-agent --setup-environment
          agenthub install company/monitoring-agent --setup-environment

      - name: Validate agents
        run: |
          agenthub status company/production-agent
          agenthub status company/monitoring-agent

      - name: Backup current agents
        run: |
          agenthub backup company/production-agent --backup-path /tmp/backups
          agenthub backup company/monitoring-agent --backup-path /tmp/backups
```

### Agent Repository Structure

For agents to be compatible with AgentHub, they should follow this structure:

```
my-awesome-agent/
├── agent.py              # Main agent implementation
├── agent.yaml           # Configuration and interface definition
├── requirements.txt     # Python dependencies
├── README.md           # Documentation
├── pyproject.toml      # Optional: UV project configuration
└── examples/           # Optional: Usage examples
```

**Example agent.yaml:**
```yaml
name: my-awesome-agent
version: 1.0.0
description: An awesome agent for AI tasks
python_version: "3.11+"

interface:
  methods:
    process_data:
      description: Process input data
      parameters:
        data:
          type: string
          description: Input data to process
      returns:
        type: object
        description: Processed results

dependencies:
  - openai>=1.0.0
  - requests>=2.25.0
  - pandas>=1.3.0

setup:
  commands:
    - "source .venv/bin/activate && uv sync"
    - "source .venv/bin/activate && uv pip install -e ."
    - "source .venv/bin/activate && uv pip install -r requirements.txt"
  validation:
    - "python -c 'import openai'"
    - "python -c 'import requests'"
```

## 🔍 Troubleshooting

### Common Issues

#### "Agent not found"
```bash
# Verify agent name format
agenthub install developer/agent-name  # ✅ Correct
agenthub install agent-name           # ❌ Missing developer/

# Check if agent exists on GitHub
curl -s https://api.github.com/repos/developer/agent-name | jq '.name'
```

#### "Environment creation failed"
```bash
# Check UV installation
uv --version

# Update UV
pip install -U uv

# Manual environment creation
cd ~/.agenthub/agents/developer/agent-name
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### "Dependencies failed to install"
```bash
# Check requirements.txt
agenthub analyze-deps developer/agent-name

# Repair environment
agenthub repair developer/agent-name --force-reinstall-deps

# Check Python version compatibility
agenthub python-versions
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from agenthub import load_agent
agent = load_agent("developer/agent-name")
```

### Recovery Procedures

```bash
# Complete recovery workflow
agenthub backup developer/agent-name --include-env
agenthub remove developer/agent-name --force
agenthub install developer/agent-name --setup-environment
```

## 📊 Best Practices

### 1. Agent Selection
- Use well-maintained agents from trusted developers
- Check agent repository for recent updates
- Review agent.yaml for compatibility requirements

### 2. Environment Management
- Always create backups before major changes
- Use specific Python versions (e.g., "3.11" instead of "3")
- Regular optimization with `agenthub optimize`

### 3. Team Collaboration
- Use descriptive agent names
- Document agent configurations
- Share environment clones for consistent setups

### 4. Production Deployment
- Test in development environments first
- Use pinned dependency versions
- Monitor agent performance and storage usage

### 5. Maintenance Schedule
```bash
# Weekly optimization
agenthub optimize developer/agent-name

# Monthly dependency updates
agenthub analyze-deps developer/agent-name

# Quarterly Python version reviews
agenthub python-versions
```

## 🚀 Getting Started Examples

### Scientific Paper Analysis
```bash
# Install scientific paper analyzer
agenthub install agentplug/scientific-paper-analyzer

# Use programmatically
python -c "
from agenthub import load_agent
agent = load_agent('agentplug/scientific-paper-analyzer')
result = agent.analyze_paper(pdf_path='research.pdf')
print(result['summary'])
"
```

### Code Analysis Pipeline
```bash
# Install coding agent
agenthub install agentplug/coding-agent

# Clone for team development
agenthub clone agentplug/coding-agent team/coding-agent-dev

# Migrate to Python 3.11
agenthub migrate team/coding-agent-dev 3.11
```

### Enterprise Setup
```bash
# Install and configure for enterprise use
agenthub install company/production-agent --base-path /opt/agenthub
agenthub backup company/production-agent --backup-path /opt/backups
agenthub status company/production-agent
```

This guide covers all current capabilities of AgentHub. For additional support, check the troubleshooting section or run `agenthub --help` for command-specific documentation.
