# AgentHub Evaluation Examples

This directory contains examples demonstrating how to use the AgentHub evaluation framework with real AgentHub agents to assess agent performance and capabilities.

## 📁 Examples Overview

### 1. Real Agent Evaluation Demo (`real_agent_evaluation_demo.py`)
**Purpose**: Comprehensive demonstration with real agents  
**Difficulty**: Beginner  
**Duration**: 10-15 minutes  

This example shows:
- Loading real AgentHub agents (analysis-agent, coding-agent, scientific-paper-analyzer)
- Running demo evaluations with actual agent implementations
- Testing individual agent methods
- Generating detailed evaluation reports
- Real agent execution via subprocess

**Run it:**
```bash
python examples/evaluation/real_agent_evaluation_demo.py
```

### 2. Real Agent Test Suite (`test_real_agents.py`)
**Purpose**: Comprehensive testing of real agents  
**Difficulty**: Intermediate  
**Duration**: 5-10 minutes  

This example demonstrates:
- Automated testing of all real agents
- Error handling and recovery
- Performance measurement
- Success rate calculation
- Combined reporting

**Run it:**
```bash
python examples/evaluation/test_real_agents.py
```

## 🤖 Available Test Agents

The examples use real AgentHub agents located in `test_agents/`:

### Analysis Agent (`agentplug/analysis-agent`)
- **Methods**: `analyze_text`, `summarize_text`
- **Purpose**: Text analysis and content processing
- **Features**: Sentiment analysis, topic extraction, readability scoring

### Coding Agent (`agentplug/coding-agent`)
- **Methods**: `generate_code`, `review_code`
- **Purpose**: Code generation and programming assistance
- **Features**: Multi-language support, code review, style preferences

### Scientific Paper Analyzer (`agentplug/scientific-paper-analyzer`)
- **Methods**: `analyze_paper`, `extract_abstract`
- **Purpose**: Scientific paper analysis and research document processing
- **Features**: Comprehensive analysis, abstract extraction, metadata extraction

## 🚀 Quick Start

### Basic Real Agent Evaluation
```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.evaluation.test_real_agents import load_real_agent, evaluate_real_agent

# Load a real agent
agent = load_real_agent("agentplug/analysis-agent")

# Run evaluation
results = evaluate_real_agent(agent, sample_count=5)

# Check results
print(f"Success rate: {results.summary_metrics['success_rate']:.2%}")
print(f"Duration: {results.duration:.2f}s")
```

### Testing Individual Agent Methods
```python
# Test specific methods
result = agent.execute("analyze_text", {"text": "Sample text for analysis"})
print(f"Analysis result: {result}")

# Check available methods
print(f"Available methods: {agent.methods}")
```

## 🏗️ Agent Structure

Each test agent follows the AgentHub standard structure:

```
test_agents/agentplug/analysis-agent/
├── agent.yaml          # Agent manifest with interface definition
├── agent.py            # Main agent implementation
└── requirements.txt    # Dependencies (optional)
```

### Agent Manifest (agent.yaml)
```yaml
name: "analysis-agent"
version: "1.0.0"
description: "AI agent for text analysis and content processing"
author: "agentplug"
license: "MIT"

interface:
  methods:
    analyze_text:
      description: "Analyze text content and provide insights"
      parameters:
        text:
          type: "string"
          description: "Text to analyze"
          required: true
      returns:
        type: "object"
        description: "Analysis results with insights and confidence score"
```

### Agent Implementation (agent.py)
```python
class AnalysisAgent:
    def __init__(self):
        self.manifest = {...}
    
    def get_interface(self):
        return {...}
    
    def analyze_text(self, text: str):
        # Implementation here
        return {"success": True, "result": {...}}
```

## 📊 Evaluation Results

The evaluation framework provides comprehensive results:

### Summary Metrics
- **Success Rate**: Percentage of successful evaluations
- **Average Quality**: Mean quality score across all samples
- **Duration**: Total evaluation time
- **Sample Count**: Number of samples evaluated

### Individual Results
- **Input/Output**: Original input and agent response
- **Method Used**: Which agent method was called
- **Metadata**: Additional information about the evaluation
- **Quality Score**: Individual quality assessment

### Report Generation
- **HTML Reports**: Rich, interactive web reports
- **JSON Data**: Machine-readable evaluation data
- **Text Reports**: Simple text-based summaries

## 🔧 Customization

### Adding New Test Agents
1. Create agent directory: `test_agents/your-namespace/your-agent/`
2. Add `agent.yaml` manifest file
3. Add `agent.py` implementation
4. Update examples to include your agent

### Custom Evaluation Samples
```python
# Modify sample data in evaluate_real_agent function
if "analysis" in agent.agent_name:
    samples = [
        "Your custom text sample 1",
        "Your custom text sample 2",
        # Add more samples...
    ]
```

### Custom Metrics
```python
# Add custom metrics to evaluation
metric_result = MetricResult(
    metric_type="custom_metric",
    value=calculated_value,
    confidence=0.9
)
```

## 🐛 Troubleshooting

### Common Issues

1. **Agent Loading Errors**
   - Check that agent directory exists
   - Verify agent.yaml and agent.py files are present
   - Ensure agent follows the standard interface

2. **Subprocess Execution Errors**
   - Check Python path and dependencies
   - Verify agent script is executable
   - Check for timeout issues

3. **Import Errors**
   - Ensure you're running from the correct directory
   - Check that all required modules are available
   - Verify path setup in examples

### Debug Mode
Enable debug output by modifying the evaluation functions:
```python
# Add debug prints
print(f"Executing method: {method_name}")
print(f"Parameters: {parameters}")
print(f"Result: {result}")
```

## 📈 Performance Considerations

### Agent Execution
- Each agent runs in a separate subprocess
- Timeout is set to 30 seconds per execution
- Memory usage is monitored and limited

### Evaluation Scaling
- Start with small sample counts (3-5)
- Increase sample count as needed
- Monitor total evaluation time

### Resource Management
- Agents are loaded fresh for each evaluation
- No persistent agent state between evaluations
- Clean subprocess execution

## 🎯 Best Practices

### 1. Start Simple
Begin with the demo examples to understand the framework:
```bash
python real_agent_evaluation_demo.py
```

### 2. Test Individual Methods
Verify agent methods work correctly before full evaluation:
```python
result = agent.execute("method_name", {"param": "value"})
```

### 3. Use Appropriate Sample Data
Choose sample data that matches your agent's intended use case:
- Analysis agents: Text samples
- Coding agents: Code generation prompts
- Scientific agents: Paper file paths

### 4. Monitor Performance
Track evaluation metrics over time:
- Success rates
- Response times
- Quality scores

### 5. Generate Reports
Use different report formats for different purposes:
- HTML for human review
- JSON for programmatic analysis
- Text for quick summaries

## 🔄 Integration with Full AgentHub

These examples work with the full AgentHub system when available:

```python
# Full AgentHub integration
import agentmanager as amg
from agentmanager.evaluation import evaluate_demo

# Load agent from registry
agent = amg.load_agent("agentplug/analysis-agent")

# Run evaluation
results = evaluate_demo(agent)
```

## 📚 Next Steps

1. **Run the Examples**: Start with the demo to understand the framework
2. **Create Custom Agents**: Add your own agents to the test suite
3. **Extend Evaluation**: Add custom metrics and sample data
4. **Integrate with Workflows**: Use evaluation in your development process
5. **Monitor Performance**: Set up continuous evaluation and monitoring

## 🤝 Contributing

To contribute to the evaluation examples:

1. Follow the existing code style and structure
2. Add comprehensive docstrings and comments
3. Include error handling and validation
4. Test examples with different agent types
5. Update this README with new examples
6. Ensure agents follow the AgentHub standard

---

**Note**: These examples demonstrate the evaluation framework with real agent implementations. The agents are designed to work independently and follow the AgentHub agent interface standards.