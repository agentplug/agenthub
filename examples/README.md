# AgentHub Examples - Complete User Documentation

This directory contains comprehensive examples demonstrating all current capabilities of AgentHub for both programmatic usage and CLI commands.

## 🚀 Quick Start

### Run the Complete Demo
```bash
python examples/quick_start.py
```
Shows all AgentHub capabilities without requiring actual installations.

## 📋 Available Examples

### Core Examples
- **`quick_start.py`** - Complete feature demonstration
- **`interactive_demo.py`** - Step-by-step interactive guide
- **`basic_installation.py`** - Simple installation workflows
- **`environment_management.py`** - Advanced environment operations

### CLI Examples
- **`cli_usage.py`** - All CLI commands with examples
- **`batch_operations.py`** - Bulk agent management
- **`cicd_integration.py`** - CI/CD pipeline examples

## 🎯 Complete Usage Examples

### 1. Basic Agent Installation

#### Programmatic
```python
from agentmanager import load_agent

# Auto-install and use
agent = load_agent("agentplug/scientific-paper-analyzer")
result = agent.analyze_paper(pdf_path="paper.pdf")
```

#### CLI
```bash
agenthub install agentplug/scientific-paper-analyzer
```

### 2. Advanced Installation with Details

#### Programmatic
```python
from agentmanager.github.auto_installer import AutoInstaller

installer = AutoInstaller(setup_environment=True)
result = installer.install_agent("developer/agent-name")

if result.success:
    print(f"✅ Installed at: {result.local_path}")
    print(f"🌍 Environment: {result.environment_result.venv_path}")
    print(f"📦 Packages: {len(result.dependency_result.installed_packages)}")
```

#### CLI
```bash
agenthub install developer/agent-name --detailed
```

### 3. Environment Management

#### Python Version Migration
```python
from agentmanager.environment.environment_manager import AdvancedEnvironmentManager

manager = AdvancedEnvironmentManager()
result = manager.migrate_python_version(
    agent_name="developer/agent",
    target_python_version="3.11",
    create_backup=True
)
```

#### CLI
```bash
agenthub migrate developer/agent 3.11
```

#### Environment Cloning
```python
manager.clone_environment("prod/agent", "dev/agent-copy")
```

#### CLI
```bash
agenthub clone prod/agent dev/agent-copy
```

### 4. Repository Management

#### List All Agents
```python
from agentmanager.github.repository_cloner import RepositoryCloner

cloner = RepositoryCloner()
agents = cloner.list_cloned_agents()
for name, path in agents.items():
    print(f"{name}: {path}")
```

#### CLI
```bash
agenthub list --detailed
```

### 5. Backup and Recovery

#### Create Backup
```python
import shutil
from pathlib import Path

agent_path = Path.home() / ".agenthub" / "agents" / "developer" / "agent"
backup_path = Path.home() / ".agenthub" / "backups" / "agent_backup"
shutil.copytree(agent_path, backup_path)
```

#### CLI
```bash
agenthub backup developer/agent
agenthub restore /path/to/backup
```

### 6. System Maintenance

#### Environment Repair
```bash
agenthub repair developer/agent --force-reinstall-deps
```

#### Storage Optimization
```bash
agenthub optimize developer/agent
```

#### Cleanup Operations
```bash
agenthub cleanup --dry-run
agenthub cleanup --remove-broken-envs
```

### 7. Status and Analysis

#### Check Agent Status
```bash
agenthub status developer/agent
agenthub analyze-deps developer/agent
agenthub python-versions
```

## 📊 Complete Workflow Examples

### Development Team Setup
```bash
# Install base agents
agenthub install agentplug/scientific-paper-analyzer
agenthub install agentplug/coding-agent

# Clone for development
agenthub clone agentplug/scientific-paper-analyzer dev/alice-paper-analyzer
agenthub clone agentplug/coding-agent dev/bob-coding-agent

# Migrate to different Python versions
agenthub migrate dev/alice-paper-analyzer 3.11
agenthub migrate dev/bob-coding-agent 3.10

# Optimize storage
agenthub optimize dev/alice-paper-analyzer
agenthub optimize dev/bob-coding-agent
```

### Production Deployment
```bash
# Install with custom path
agenthub install company/production-agent --base-path /opt/agents

# Create backup
agenthub backup company/production-agent --backup-path /backups

# Validate installation
agenthub status company/production-agent

# Monitor dependencies
agenthub analyze-deps company/production-agent
```

### CI/CD Integration
```bash
#!/bin/bash
# deploy-agents.sh

# Install agents
agenthub install company/agent1 --base-path /opt/agents
agenthub install company/agent2 --base-path /opt/agents

# Validate all agents
for agent in company/agent1 company/agent2; do
    if ! agenthub status "$agent" > /dev/null 2>&1; then
        echo "❌ $agent validation failed"
        exit 1
    fi
done

echo "✅ All agents deployed successfully"
```

## 🔧 Testing Your Setup

### Validate Installation
```bash
# Check AgentHub is working
python -c "import agentmanager; print('AgentHub ready!')"

# Check CLI commands
agenthub --help
agenthub list --help
```

### Test with Mock Agent
```bash
# Create test structure
mkdir -p /tmp/test-agent
cd /tmp/test-agent

# Create required files
echo 'def test_method(): return {"status": "ok"}' > agent.py
echo 'name: test-agent' > agent.yaml
echo '# No dependencies' > requirements.txt
echo '# Test agent' > README.md

# Validate structure
python -c "
from agentmanager.github.repository_validator import RepositoryValidator
validator = RepositoryValidator()
result = validator.validate_repository('/tmp/test-agent')
print('Valid:', result.is_valid)
"
```

## 🎯 Agent Repository Structure

For agents to work with AgentHub, they must follow this structure:

```
my-agent/
├── agent.py              # Main implementation
├── agent.yaml           # Configuration
├── requirements.txt     # Dependencies
├── README.md           # Documentation
└── pyproject.toml      # Optional UV config
```

**agent.yaml example:**
```yaml
name: my-awesome-agent
version: 1.0.0
description: An awesome agent
python_version: "3.11+"
interface:
  methods:
    process_data:
      parameters:
        data: string
      returns:
        type: object
dependencies:
  - requests>=2.25.0
  - pandas>=1.3.0
```

## 📈 Performance Tips

### Storage Optimization
```bash
# Regular maintenance
agenthub optimize company/agent1
agenthub optimize company/agent2

# Batch optimization
for agent in $(agenthub list | grep -o '^[^[:space:]]*'); do
    agenthub optimize "$agent"
done
```

### Environment Management
```bash
# Check all Python versions
agenthub python-versions

# Migrate multiple agents
for agent in dev/*; do
    agenthub migrate "$agent" 3.11
done
```

## 🆘 Troubleshooting

### Common Issues

#### "Agent not found"
```bash
# Check format
agenthub install developer/agent-name  # ✅ Correct
agenthub install agent-name           # ❌ Missing developer/
```

#### "Environment creation failed"
```bash
# Check UV installation
uv --version

# Repair environment
agenthub repair developer/agent-name --force-reinstall-deps
```

#### "Dependencies failed"
```bash
# Analyze dependencies
agenthub analyze-deps developer/agent-name

# Check requirements.txt
agenthub status developer/agent-name
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from agentmanager import load_agent
agent = load_agent("developer/agent-name")
```

## 🚀 Next Steps

After exploring these examples:

1. **Choose your first real agent** to install
2. **Set up your development workflow** using environment cloning
3. **Create backup procedures** for production agents
4. **Implement monitoring** for agent health
5. **Scale to team-wide usage**

## 📚 Additional Resources

- **User Guide**: `../docs/USER_GUIDE.md`
- **API Documentation**: Check docstrings in source code
- **CLI Help**: Run `agenthub --help` or `agenthub command --help`
- **Examples**: All files in this directory are executable examples

## 💡 Quick Commands Reference

```bash
# Essential commands
agenthub install developer/agent-name     # Install agent
agenthub list --detailed                  # List all agents
agenthub status developer/agent-name      # Check agent status
agenthub repair developer/agent-name      # Fix broken environment
agenthub backup developer/agent-name      # Create backup
agenthub migrate developer/agent-name 3.11  # Upgrade Python
agenthub optimize developer/agent-name    # Clean up storage
agenthub cleanup                          # System maintenance
```

Start with `python examples/quick_start.py` to see everything in action!