# Phase 3.1: Simple Real-time Monitoring Architecture

## KISS & YAGNI Principles

This design follows **Keep It Simple, Stupid (KISS)** and **You Aren't Gonna Need It (YAGNI)** principles.

## Simple Architecture

```
Agent Subprocess → LogStreamer → LLMAnalyzer → Terminal Display
                                    ↓
                              Core LLM Component
```

## Core Components (4 Components)

### 1. LogStreamer

**Purpose**: Capture real-time logs from agent subprocesses

**Simple Implementation**:

```python
class LogStreamer:
    def __init__(self, process):
        self.process = process
        self.running = False

    def start(self):
        # Start reading stdout/stderr in threads
        pass

    def get_logs(self):
        # Return recent log lines
        pass
```

### 2. Core LLM Component

**Purpose**: Centralized LLM service for the entire AgentHub system

**Implementation**:

```python
class CoreLLMService:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.client = self._initialize_client(api_key)
        self.model = model
        self.cache = {}

    def analyze_logs(self, logs, prompt_template=None):
        """Analyze logs with custom prompt template"""
        if not self.client:
            return self._fallback_analysis(logs)

        prompt = prompt_template or self._default_log_analysis_prompt()
        formatted_prompt = prompt.format(logs='\n'.join(logs))

        return self._call_llm(formatted_prompt)

    def _default_log_analysis_prompt(self):
        return """
        Analyze these agent execution logs and provide a concise summary:

        {logs}

        Please provide:
        1. What the agent is currently doing (max 50 characters)
        2. Any errors or issues detected
        3. Progress estimation (0-100%)
        4. Actionable suggestions if errors found

        Format as JSON:
        {{
            "summary": "...",
            "progress": 75,
            "status": "working",
            "errors": ["..."],
            "suggestions": ["..."]
        }}
        """
```

### 3. LLMAnalyzer

**Purpose**: Log analysis using the Core LLM Component

**Implementation**:

```python
class LLMAnalyzer:
    def __init__(self, core_llm_service):
        self.core_llm = core_llm_service
        self.cache = {}

    def analyze(self, logs):
        # Use Core LLM Component for analysis
        return self.core_llm.analyze_logs(logs)
```

### 4. TerminalDisplay

**Purpose**: Show updates in terminal

**Simple Implementation**:

```python
class TerminalDisplay:
    def update(self, message):
        print(f"\r{message}", end="", flush=True)
```

## Integration

### ProcessManager Integration

```python
class ProcessManager:
    def execute_agent(self, agent_path, method, parameters, monitoring=True):
        if monitoring:
            return self._execute_with_monitoring(agent_path, method, parameters)
        else:
            return self._execute_without_monitoring(agent_path, method, parameters)

    def _execute_with_monitoring(self, agent_path, method, parameters):
        # Start subprocess
        process = subprocess.Popen(...)

        # LLM-powered monitoring
        core_llm = CoreLLMService()
        streamer = LogStreamer(process)
        analyzer = LLMAnalyzer(core_llm)
        display = TerminalDisplay()

        streamer.start()

        while process.poll() is None:
            logs = streamer.get_logs()
            message = analyzer.analyze(logs)
            display.update(message)
            time.sleep(0.5)

        return result
```

## What We Removed (YAGNI)

- ❌ Complex configuration management
- ❌ Multi-agent monitoring
- ❌ Advanced performance metrics
- ❌ Error recovery automation
- ❌ Custom display components
- ❌ Complex caching systems

## What We Kept (KISS)

- ✅ Real-time log streaming
- ✅ Core LLM component for system-wide use
- ✅ LLM-powered log analysis
- ✅ Intelligent error detection
- ✅ Basic terminal display
- ✅ Default monitoring behavior
- ✅ Simple on/off control

## Benefits

1. **Simple to implement** - Only 4 components
2. **Easy to understand** - Clear, straightforward code
3. **Fast to develop** - No complex integrations
4. **Reliable** - Fewer moving parts
5. **Maintainable** - Simple code is easier to maintain

## User Experience

```python
# Works out of the box
agent = ah.load_agent("agentplug/scientific-paper-analyzer")
result = agent.analyze_paper("sample.pdf")

# Terminal shows:
# 🔄 Working...
# 📊 Processing...
# ✅ Complete
```

## Implementation Timeline

- **Week 1**: LogStreamer (real-time log capture)
- **Week 2**: SimpleAnalyzer (basic pattern matching)
- **Week 3**: TerminalDisplay (simple terminal updates)
- **Week 4**: Integration and testing

**Total: 4 weeks instead of 12 weeks**

## Success Criteria

- ✅ Real-time log streaming
- ✅ Simple activity identification
- ✅ Clear terminal updates
- ✅ Default monitoring behavior
- ✅ < 5% performance overhead
- ✅ 100% backward compatibility

This simple design delivers 80% of the value with 20% of the complexity.
