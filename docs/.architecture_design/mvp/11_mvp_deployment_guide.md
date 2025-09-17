# Agent Hub MVP Deployment Guide

**Document Type**: MVP Deployment Guide
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Final
**Level**: L5 - MVP Deployment Level
**Audience**: Development Team, DevOps Team, End Users

## 🎯 **MVP Deployment Overview**

This guide provides comprehensive deployment instructions for Agent Hub MVP, covering development, testing, and production environments. The MVP is designed for **simple deployment** with minimal infrastructure requirements.

### **Deployment Goals**
- **Simple Setup**: One-command installation and setup
- **Cross-Platform**: Support for Windows, macOS, and Linux
- **Minimal Dependencies**: Only essential system requirements
- **Fast Deployment**: < 10 minutes from start to working system
- **Zero Maintenance**: Self-contained with no external services

### **Deployment Environments**
- **Development**: Local development and testing
- **Testing**: Automated testing and validation
- **Production**: End-user installation and usage

## 🏗️ **System Requirements**

### **Minimum Requirements**
- **Operating System**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: Python 3.12 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free disk space
- **Network**: Internet access for agent downloads

### **Recommended Requirements**
- **Operating System**: Latest stable release
- **Python**: Python 3.12+ with latest patch
- **Memory**: 8GB RAM or higher
- **Storage**: 5GB free disk space
- **Network**: Stable internet connection

### **Dependencies**
```bash
# Core Python packages
click>=8.0.0              # CLI framework
requests>=2.31.0           # HTTP client
PyYAML>=6.0.0             # YAML parsing
pydantic>=2.0.0            # Data validation

# Development dependencies
pytest>=7.0.0              # Testing framework
black>=23.0.0              # Code formatting
flake8>=6.0.0              # Linting
mypy>=1.0.0                # Type checking
```

## 🚀 **Development Environment Setup**

### **1. Prerequisites Installation**

#### **Python Installation**
```bash
# macOS (using Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip

# Windows
# Download from https://python.org/downloads/
# Ensure "Add Python to PATH" is checked
```

#### **UV Package Manager Installation**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### **2. Repository Setup**
```bash
# Clone repository
git clone https://github.com/your-org/agent-hub.git
cd agent-hub

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python -c "import agenthub; print('Installation successful!')"
```

### **3. Development Configuration**
```bash
# Create development configuration
mkdir -p ~/.agenthub/config
cat > ~/.agenthub/config/settings.yaml << EOF
development:
  enabled: true
  debug: true
  log_level: DEBUG

registry:
  github_token: ""  # Optional: for higher rate limits
  cache_ttl: 3600  # 1 hour

storage:
  base_path: ~/.agenthub
  max_cache_size: 100MB
EOF

# Set up pre-commit hooks
pre-commit install
```

## 🧪 **Testing Environment Setup**

### **1. Automated Testing Setup**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agenthub --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m e2e              # End-to-end tests only

# Run performance tests
pytest tests/performance/

# Run security tests
pytest tests/security/
```

### **2. Cross-Platform Testing**
```bash
# Test on different platforms
# Use GitHub Actions for automated cross-platform testing

# Local platform testing
python -c "
import platform
print(f'Platform: {platform.system()}')
print(f'Version: {platform.version()}')
print(f'Architecture: {platform.machine()}')
"
```

### **3. Test Data Setup**
```bash
# Create test agents
mkdir -p tests/data/agents/test-agent
cat > tests/data/agents/test-agent/agent.yaml << EOF
name: "test-agent"
version: "1.0.0"
description: "Test agent for testing"
author: "test"
license: "MIT"

interface:
  methods:
    test_method:
      description: "Test method"
      parameters:
        input: {type: "string", required: true}
      returns: {type: "string", description: "Test result"}

dependencies:
  python: ">=3.12"
  runtime: []
EOF

cat > tests/data/agents/test-agent/agent.py << EOF
#!/usr/bin/env python3
import sys
import json

def test_method(input_text):
    return f"Processed: {input_text}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    method = sys.argv[1]
    params = json.loads(sys.argv[2])

    if method == "test_method":
        result = test_method(params["input"])
        print(json.dumps({"result": result}))
    else:
        sys.exit(1)
EOF
```

## 🚀 **Production Deployment**

### **1. User Installation**

#### **Simple Installation (Recommended)**
```bash
# Install via pip
pip install agenthub

# Verify installation
agenthub --version
agenthub --help
```

#### **Development Installation**
```bash
# Install from source
git clone https://github.com/your-org/agent-hub.git
cd agent-hub
pip install -e .

# Verify installation
agenthub --version
```

### **2. First-Time Setup**
```bash
# Initialize Agent Hub
agenthub init

# This creates:
# ~/.agenthub/
# ├── agents/
# ├── cache/
# ├── config/
# └── logs/

# Install first agent
agenthub install meta/coding-agent

# Verify installation
agenthub list --installed
```

### **3. Configuration**
```bash
# Create user configuration
mkdir -p ~/.agenthub/config
cat > ~/.agenthub/config/settings.yaml << EOF
# Agent Hub Configuration
registry:
  cache_ttl: 3600          # Cache TTL in seconds
  max_retries: 3           # Maximum retry attempts

storage:
  max_cache_size: 500MB    # Maximum cache size
  cleanup_interval: 86400  # Cleanup interval in seconds

logging:
  level: INFO              # Log level (DEBUG, INFO, WARNING, ERROR)
  file: ~/.agenthub/logs/agenthub.log

performance:
  max_concurrent_agents: 5 # Maximum concurrent agent executions
  timeout: 300             # Default timeout in seconds
EOF
```

## 🔧 **Configuration Management**

### **Configuration File Structure**
```yaml
# ~/.agenthub/config/settings.yaml
# Agent Hub MVP Configuration

# Registry settings
registry:
  # GitHub registry configuration
  github_token: ""           # Optional: GitHub token for higher rate limits
  cache_ttl: 3600           # Cache TTL in seconds (1 hour)
  max_retries: 3            # Maximum retry attempts for network operations
  user_agent: "Agent-Hub/1.0.0"  # User agent string

# Storage settings
storage:
  base_path: "~/.agenthub"  # Base storage path
  max_cache_size: "500MB"   # Maximum cache size
  cleanup_interval: 86400   # Cleanup interval in seconds (24 hours)
  backup_enabled: true      # Enable automatic backups

# Logging settings
logging:
  level: "INFO"             # Log level (DEBUG, INFO, WARNING, ERROR)
  file: "~/.agenthub/logs/agenthub.log"  # Log file path
  max_size: "10MB"          # Maximum log file size
  backup_count: 5           # Number of backup log files

# Performance settings
performance:
  max_concurrent_agents: 5  # Maximum concurrent agent executions
  timeout: 300              # Default timeout in seconds
  memory_limit: "1GB"       # Memory limit per agent
  cpu_limit: 100            # CPU limit percentage

# Security settings
security:
  process_isolation: true   # Enable process isolation
  file_access_control: true # Enable file access control
  dependency_isolation: true # Enable dependency isolation
  max_file_size: "100MB"   # Maximum file size for uploads
```

### **Environment Variables**
```bash
# Environment variable overrides
export AGENTHUB_REGISTRY_CACHE_TTL=7200        # Override cache TTL
export AGENTHUB_STORAGE_BASE_PATH=/custom/path # Override storage path
export AGENTHUB_LOGGING_LEVEL=DEBUG            # Override log level
export AGENTHUB_GITHUB_TOKEN=your_token        # Set GitHub token
```

## 📦 **Package Distribution**

### **1. PyPI Package**
```bash
# Build package
python -m build

# Upload to PyPI (for maintainers)
python -m twine upload dist/*

# Install from PyPI
pip install agenthub
```

### **2. Standalone Distribution**
```bash
# Create standalone executable
pyinstaller --onefile --name agenthub agenthub/cli/main.py

# Create distribution package
mkdir -p dist/agent-hub
cp dist/agenthub dist/agent-hub/
cp -r docs dist/agent-hub/
cp README.md dist/agent-hub/
cp LICENSE dist/agent-hub/

# Create archive
tar -czf agent-hub-v1.0.0.tar.gz -C dist agent-hub
```

### **3. Docker Container**
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up Agent Hub
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Install application
RUN pip install -e .

# Create user
RUN useradd -m -s /bin/bash agenthub
USER agenthub

# Set up Agent Hub directory
RUN mkdir -p /home/agenthub/.agenthub

# Expose volume for persistence
VOLUME /home/agenthub/.agenthub

# Default command
CMD ["agenthub", "--help"]
```

## 🔍 **Monitoring & Logging**

### **1. Log Configuration**
```python
# agenthub/utils/logging.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(config):
    """Set up logging configuration."""
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
    log_file = config.get('logging', {}).get('file', '~/.agenthub/logs/agenthub.log')

    # Create log directory
    log_path = Path(log_file).expanduser().parent
    log_path.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

### **2. Health Checks**
```bash
# Health check commands
agenthub doctor              # Check system health
agenthub status             # Show system status
agenthub logs               # Show recent logs
agenthub cache --info       # Show cache information
```

### **3. Performance Monitoring**
```python
# agenthub/utils/monitoring.py
import time
import logging
from functools import wraps

def monitor_performance(func):
    """Simple performance monitoring decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time

            # Log performance metrics (only in debug mode)
            if logging.getLogger().level <= logging.DEBUG:
                logging.debug(f"{func.__name__}: {execution_time:.3f}s")

    return wrapper
```

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **1. Installation Issues**
```bash
# Python version issues
python --version  # Should be 3.12+
python3.12 --version  # Alternative check

# Permission issues
sudo pip install agenthub  # On Linux/macOS
pip install --user agenthub  # User installation

# Dependency conflicts
pip install --upgrade pip setuptools wheel
pip install agenthub --force-reinstall
```

#### **2. Runtime Issues**
```bash
# Virtual environment issues
agenthub doctor  # Check system health
agenthub cache --clear  # Clear cache

# Permission issues
chmod +x ~/.agenthub/agents/*/agent.py  # Fix agent permissions

# Dependency issues
agenthub reinstall <agent-path>  # Reinstall agent
```

#### **3. Network Issues**
```bash
# GitHub API issues
agenthub registry --refresh  # Refresh registry
agenthub cache --clear      # Clear cache

# Proxy issues
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

### **Debug Mode**
```bash
# Enable debug mode
export AGENTHUB_DEBUG=1
agenthub --verbose install meta/coding-agent

# Check logs
tail -f ~/.agenthub/logs/agenthub.log
```

## 🔄 **Updates & Maintenance**

### **1. Application Updates**
```bash
# Update Agent Hub
pip install --upgrade agenthub

# Update specific version
pip install agenthub==1.1.0

# Check for updates
pip list --outdated | grep agenthub
```

### **2. Agent Updates**
```bash
# Update specific agent
agenthub update meta/coding-agent

# Update all agents
agenthub update --all

# Check for agent updates
agenthub list --updates-available
```

### **3. System Maintenance**
```bash
# Clean up old cache
agenthub cache --cleanup

# Backup configuration
cp -r ~/.agenthub ~/.agenthub.backup.$(date +%Y%m%d)

# Restore configuration
cp -r ~/.agenthub.backup.20250628 ~/.agenthub
```

## 🎯 **Deployment Checklist**

### **Pre-Deployment**
- [ ] System requirements verified
- [ ] Python 3.12+ installed
- [ ] UV package manager installed
- [ ] Network access confirmed
- [ ] Disk space available

### **Development Setup**
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] Configuration created

### **Production Deployment**
- [ ] Agent Hub installed
- [ ] Configuration created
- [ ] First agent installed
- [ ] Basic functionality tested
- [ ] User documentation provided

### **Post-Deployment**
- [ ] Monitoring configured
- [ ] Logging verified
- [ ] Performance validated
- [ ] User training completed
- [ ] Support processes established

## 🎯 **MVP Deployment Summary**

### **Deployment Benefits**
- ✅ **Simple Setup**: One-command installation
- ✅ **Cross-Platform**: Windows, macOS, Linux support
- ✅ **Minimal Dependencies**: Only essential requirements
- ✅ **Fast Deployment**: < 10 minutes setup time
- ✅ **Zero Maintenance**: Self-contained operation

### **Key Deployment Features**
1. **Automated Installation**: pip-based installation
2. **Configuration Management**: YAML-based configuration
3. **Health Monitoring**: Built-in health checks
4. **Troubleshooting Tools**: Comprehensive debugging support
5. **Update Management**: Simple update process

### **Expected Deployment Outcomes**
- **Development**: Fast setup for development team
- **Testing**: Automated testing environment
- **Production**: Reliable end-user deployment
- **Maintenance**: Simple update and maintenance process

This deployment guide provides **comprehensive instructions** for setting up Agent Hub MVP in any environment, ensuring successful deployment and operation across all target platforms.
