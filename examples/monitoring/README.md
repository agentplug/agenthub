# AgentHub Enhanced Monitoring Examples

Welcome to the AgentHub Enhanced Monitoring system! These examples will help you understand and use the powerful monitoring features available in AgentHub.

## 🎯 What is Enhanced Monitoring?

Enhanced monitoring gives you **real-time visibility** into what your AI agents are doing, with **smart features** that make monitoring easier and more useful.

### Key Benefits:
- **🖥️ Better Display**: Choose between incremental (preserves history) or fullscreen (clean view) modes
- **🎮 Interactive Controls**: Pause, filter, search, and customize your monitoring experience
- **🧠 Smart Analysis**: AI-powered analysis that learns from your usage patterns
- **⚡ Resource Management**: Automatic optimization to prevent performance issues
- **⚙️ Flexible Configuration**: Easy setup with presets or full customization

## 📚 Examples Overview

### 1. Basic vs Enhanced Monitoring
**File**: `01_basic_vs_enhanced_monitoring.py`
**What it shows**: The difference between basic monitoring and the new enhanced features
**Perfect for**: Understanding what you get with enhanced monitoring

### 2. Display Modes Demo
**File**: `02_display_modes_demo.py`
**What it shows**: Clear difference between incremental and fullscreen modes using real agents
**Perfect for**: Understanding which display mode works best for your needs

### 3. Interactive Controls Demo
**File**: `03_interactive_controls_demo.py`
**What it shows**: How to use interactive controls like pause, filter, and search
**Perfect for**: Learning how to customize your monitoring experience

### 4. Smart Analysis Demo
**File**: `04_smart_analysis_demo.py`
**What it shows**: How AI-powered analysis and learning work
**Perfect for**: Understanding the intelligent features

### 5. Resource Management Demo
**File**: `05_resource_management_demo.py`
**What it shows**: How the system automatically manages resources
**Perfect for**: Understanding performance optimization

### 6. Configuration Options Demo
**File**: `06_configuration_options_demo.py`
**What it shows**: All the different ways to configure monitoring
**Perfect for**: Learning how to set up monitoring for your needs

### 7. Complete Monitoring Demo
**File**: `07_complete_monitoring_demo.py`
**What it shows**: How to use all features together
**Perfect for**: Seeing the full potential of enhanced monitoring

## 🚀 Quick Start

### Easiest Way (Recommended for beginners):
```python
import agenthub as ah

# Simple monitoring - just turn it on
agent = ah.load_agent("my-agent", monitoring=True)
result = agent.analyze_text("Your question here")
```

### Better Way (Recommended for most users):
```python
import agenthub as ah
from agenthub.monitoring import MonitoringConfig

# Use a preset configuration
config = MonitoringConfig.incremental()  # or .fullscreen()
agent = ah.load_agent("my-agent", monitoring=config)
result = agent.analyze_text("Your question here")
```

### Advanced Way (For full control):
```python
import agenthub as ah
from agenthub.monitoring import MonitoringBuilder

# Custom configuration
config = (MonitoringBuilder()
         .incremental()
         .interactive()
         .memory_limit(200)
         .analysis_interval(1.5)
         .show_metrics()
         .enable_learning()
         .build())

agent = ah.load_agent("my-agent", monitoring=config)
result = agent.analyze_text("Your question here")
```

## 🎯 Choosing the Right Configuration

### For Development:
- **Display Mode**: Incremental (preserves terminal history)
- **Interactive**: Yes (for controls)
- **Learning**: Yes (to improve over time)
- **Metrics**: Yes (to see performance)

### For Production:
- **Display Mode**: Fullscreen (clean view)
- **Interactive**: No (automated)
- **Learning**: Yes (to optimize)
- **Memory Limit**: Set appropriate limit
- **Export**: Enable for logging

### For Debugging:
- **Display Mode**: Incremental (to see history)
- **Interactive**: Yes (for controls)
- **Learning**: Yes (to learn patterns)
- **Refresh Rate**: Fast (1.0 seconds)
- **All Features**: Enabled

### For Minimal Resources:
- **Display Mode**: Fullscreen (less memory)
- **Interactive**: No
- **Learning**: No
- **Memory Limit**: Low (50-100MB)
- **Analysis Interval**: Slow (3.0+ seconds)

## 🎮 Interactive Controls

When interactive mode is enabled, you can use these keyboard shortcuts:

- **[p]** - Pause/Resume monitoring
- **[f]** - Cycle through filters (all, errors, warnings)
- **[s]** - Search in logs
- **[m]** - Toggle metrics display
- **[c]** - Toggle compact mode
- **[t]** - Toggle timeline display
- **[e]** - Export logs
- **[h]** - Show help
- **[q]** - Quit monitoring
- **[1]** - Switch to full display mode
- **[2]** - Switch to compact display mode

## 🌍 Environment Variables

You can configure monitoring using environment variables:

```bash
export AGENTHUB_MONITORING_DISPLAY_MODE=incremental
export AGENTHUB_MONITORING_INTERACTIVE=true
export AGENTHUB_MONITORING_MEMORY_LIMIT=200
export AGENTHUB_MONITORING_ANALYSIS_INTERVAL=2.0
```

Then use in your code:
```python
config = MonitoringConfig.from_environment()
agent = ah.load_agent("my-agent", monitoring=config)
```

## 📊 What You'll See

### Basic Information:
- **Status**: What the agent is currently doing
- **Activity**: Detailed description of current activity
- **Logs**: Number of log lines captured
- **Time**: How long the agent has been running

### Enhanced Information:
- **Metrics**: Performance data (memory, CPU, execution time)
- **Timeline**: Step-by-step execution timeline
- **Errors**: Any errors that occurred
- **Suggestions**: AI-generated recommendations
- **Learning**: Patterns and insights from usage

## 🔧 Troubleshooting

### Common Issues:

**Q: Monitoring doesn't start**
A: Make sure you have the required dependencies installed:
```bash
pip install psutil
```

**Q: Display looks strange**
A: Try switching between incremental and fullscreen modes:
```python
config = MonitoringConfig.fullscreen()  # or .incremental()
```

**Q: Too much information**
A: Use minimal mode or disable some features:
```python
config = MonitoringConfig.minimal()
# or
config.show_metrics = False
config.show_timeline = False
```

**Q: Not enough information**
A: Use debug mode or enable more features:
```python
config = MonitoringConfig.debug()
# or
config.show_metrics = True
config.show_timeline = True
config.enable_learning = True
```

## 💡 Tips and Best Practices

1. **Start Simple**: Begin with basic monitoring, then add features as needed
2. **Choose the Right Mode**: Use incremental for development, fullscreen for production
3. **Enable Learning**: Let the system learn from your usage patterns
4. **Set Memory Limits**: Prevent resource issues in production
5. **Use Interactive Mode**: When you need control over the display
6. **Export Logs**: Save important monitoring data for analysis
7. **Monitor Performance**: Watch metrics to optimize your agents

## 🎉 Next Steps

1. **Try the Examples**: Run each example to see the features in action
2. **Experiment**: Try different configurations to find what works for you
3. **Customize**: Use the builder pattern to create your perfect setup
4. **Integrate**: Add monitoring to your own agents and projects
5. **Learn**: Let the system learn from your usage patterns

## 📞 Need Help?

- **Check the Examples**: Each example shows specific features
- **Read the Code**: Examples include detailed comments
- **Experiment**: Try different configurations
- **Ask Questions**: The examples are designed to be self-explanatory

---

**Happy Monitoring! 🎯**

The enhanced monitoring system is designed to make your AI agent development and deployment experience better. Start with the basic examples and gradually explore the advanced features to find what works best for your needs.