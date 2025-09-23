# Phase 3.1: Simple Real-time Monitoring User Guide

## Overview

Phase 3.1 provides simple, real-time monitoring that shows you what your agents are doing. It works out of the box with no configuration needed.

## Quick Start

### Basic Usage

Monitoring is **automatically enabled by default**:

```python
import agenthub as ah

# Load an agent (monitoring enabled by default)
agent = ah.load_agent("agentplug/scientific-paper-analyzer")

# Execute with automatic monitoring
result = agent.analyze_paper("sample.pdf")
```

### What You'll See

Instead of waiting in silence, you'll see simple updates:

```
🚀 Starting...
📊 Processing...
✅ Complete
```

### Disable Monitoring (Optional)

```python
# Disable monitoring if needed
agent = ah.load_agent("agentplug/scientific-paper-analyzer", monitoring=False)
result = agent.analyze_paper("sample.pdf")
# [Silent execution - no monitoring output]
```

## How It Works

### LLM-Powered Analysis

The system uses AI to intelligently analyze agent logs and provide meaningful insights:

- **🚀 Starting...** - When agent begins execution
- **📊 Processing document: sample.pdf** - Specific activity identification
- **🔍 Using tool 'web_search'** - Tool usage detection
- **❌ Error: File not found** - Detailed error analysis with context
- **✅ Complete: Found 15 insights** - Detailed completion summary
- **⚠️ Warning: API rate limit** - Proactive issue detection

### Real-time Updates

Updates appear every 0.5 seconds in your terminal, showing the current status of your agent.

## Examples

### Example 1: Basic Agent Execution

```python
import agenthub as ah

# Load agent with default monitoring
agent = ah.load_agent("agentplug/scientific-paper-analyzer")

# Execute with monitoring
result = agent.analyze_paper("sample.pdf")
```

**Terminal Output**:

```
🚀 Starting agent execution...
📊 Processing document: sample.pdf
🔍 Using tool 'web_search' to find related research
✅ Tool execution successful (2.3s)
🎯 Analysis complete! Found 15 key insights
```

### Example 2: Error Detection

```python
import agenthub as ah

# Load agent
agent = ah.load_agent("agentplug/scientific-paper-analyzer")

# Execute with error
result = agent.analyze_paper("missing.pdf")
```

**Terminal Output**:

```
🚀 Starting agent execution...
❌ Error: File 'missing.pdf' not found
💡 Suggestion: Check if the file path is correct
```

### Example 3: Batch Processing

```python
import agenthub as ah

# Load agent
agent = ah.load_agent("agentplug/scientific-paper-analyzer")

# Process multiple documents
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for doc in documents:
    print(f"Processing {doc}...")
    result = agent.analyze_paper(doc)
    # Terminal shows: 🚀 Starting... 📊 Processing... ✅ Complete
```

## Configuration

### Environment Variables (Optional)

You can set these environment variables to customize behavior:

```bash
# Update frequency (seconds)
export AGENTHUB_MONITORING_UPDATE_FREQUENCY=0.5

# Enable/disable monitoring globally
export AGENTHUB_MONITORING_ENABLED=true
```

### Default Settings

- **Update frequency**: 0.5 seconds
- **Monitoring**: Enabled by default
- **Display**: Simple terminal updates
- **Pattern matching**: LLM-powered intelligent analysis

## Troubleshooting

### Common Issues

#### 1. No Monitoring Output

**Problem**: No updates are shown
**Solution**:

- Check if monitoring is enabled: `export AGENTHUB_MONITORING_ENABLED=true`
- Verify terminal compatibility

#### 2. Slow Updates

**Problem**: Updates are delayed
**Solution**:

- Reduce update frequency: `export AGENTHUB_MONITORING_UPDATE_FREQUENCY=0.2`

#### 3. Inaccurate Status

**Problem**: Status messages don't match what agent is doing
**Solution**:

- This is normal - the system uses simple pattern matching
- Focus on the fact that the agent is working, not exact status

### Debug Mode

Enable debug mode for troubleshooting:

```bash
export AGENTHUB_MONITORING_DEBUG=true
```

## Best Practices

### 1. Default Usage

For most users, the default settings work perfectly:

```python
# Just use the defaults
agent = ah.load_agent("agentplug/scientific-paper-analyzer")
result = agent.analyze_paper("sample.pdf")
```

### 2. Batch Processing

For batch processing, you might want to disable monitoring:

```python
# Disable monitoring for batch processing
agent = ah.load_agent("agentplug/scientific-paper-analyzer", monitoring=False)

for doc in documents:
    result = agent.analyze_paper(doc)
```

### 3. Long-Running Operations

For operations that take more than 5 minutes:

```bash
# Reduce update frequency to avoid spam
export AGENTHUB_MONITORING_UPDATE_FREQUENCY=1.0
```

## FAQ

### Q: Does monitoring affect performance?

A: Monitoring adds minimal overhead (< 5% CPU, < 10MB memory) and provides significant value in understanding agent behavior.

### Q: Can I disable monitoring?

A: Yes, use `monitoring=False` in `load_agent()` or set `AGENTHUB_MONITORING_ENABLED=false`.

### Q: What terminals are supported?

A: The system works with most modern terminals including bash, zsh, PowerShell, and Windows Terminal.

### Q: How accurate are the status messages?

A: Status messages use simple pattern matching and may not be 100% accurate. Focus on the fact that the agent is working rather than exact status.

### Q: Can I customize the status messages?

A: Not in this simple version. The system uses basic keyword matching for common patterns.

### Q: What happens if the agent crashes?

A: The monitoring system will detect the crash and show "❌ Error detected".

## Integration

### With Existing Code

The monitoring system integrates seamlessly with existing code:

```python
import agenthub as ah

# Your existing code works unchanged
agent = ah.load_agent("agentplug/scientific-paper-analyzer")

# Monitoring is automatically enabled
result = agent.analyze_paper("sample.pdf")
```

### With Other Tools

The monitoring system works with any tool that uses AgentHub:

```python
# Works with any agent
agent = ah.load_agent("agentplug/code-reviewer")
result = agent.review_code("code.py")

# Works with any method
agent = ah.load_agent("agentplug/data-processor")
result = agent.process_data("data.csv")
```

## Conclusion

Phase 3.1 simple monitoring provides immediate value with zero configuration. You can see what your agents are doing in real-time, which helps build confidence in your agent-based workflows.

The system is designed to be simple, reliable, and unobtrusive while providing the core value of real-time visibility into agent execution.
