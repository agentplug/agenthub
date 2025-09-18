# Phase 3.1: Simple Implementation Plan (KISS & YAGNI)

## Overview

This is a simplified implementation plan following KISS and YAGNI principles. We deliver 80% of the value with 20% of the complexity.

## Simple Implementation (5 Weeks)

### Week 1: LogStreamer

**Goal**: Capture real-time logs from agent subprocesses

**Deliverables**:

- `LogStreamer` class with threaded log reading
- Integration with `ProcessManager`
- Basic error handling

**Implementation**:

```python
class LogStreamer:
    def __init__(self, process):
        self.process = process
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self):
        for line in iter(self.process.stdout.readline, ''):
            if not self.running:
                break
            self.stdout_queue.put(line.strip())

    def get_logs(self):
        logs = []
        while not self.stdout_queue.empty():
            logs.append(self.stdout_queue.get())
        return logs
```

### Week 2: Core LLM Component

**Goal**: General-purpose LLM service using AISuite for system-wide use

**Deliverables**:

- `CoreLLMService` class with AISuite integration
- General-purpose LLM operations (generate, analyze_text)
- Support for multiple analysis types
- Caching and error handling
- Fallback support when AISuite unavailable

**Implementation**:

```python
class CoreLLMService:
    def __init__(self, aisuite_client=None, model="gpt-3.5-turbo"):
        self.aisuite = aisuite_client or self._initialize_aisuite()
        self.model = model
        self.cache = {}

    def generate(self, input_data, **kwargs):
        """Adaptive LLM generation using AISuite

        Args:
            input_data: Either a string (single prompt) or list of messages (conversation)
            **kwargs: Additional parameters for AISuite
        """
        if not self.aisuite:
            return self._fallback_response()

        if isinstance(input_data, str):
            # Single prompt - direct processing
            return self.aisuite.generate(
                prompt=input_data,
                model=self.model,
                **kwargs
            )
        elif isinstance(input_data, list):
            # Messages - organize into context and focus on current
            prompt = self._organize_messages_to_prompt(input_data)
            return self.aisuite.generate(
                prompt=prompt,
                model=self.model,
                **kwargs
            )
        else:
            raise ValueError("input_data must be string (prompt) or list (messages)")

    def _organize_messages_to_prompt(self, messages):
        """Convert conversation messages to a single prompt with context"""
        if not messages:
            return ""

        # Separate context (previous messages) from current message
        context_messages = messages[:-1] if len(messages) > 1 else []
        current_message = messages[-1]

        # Build context from previous messages
        context = ""
        if context_messages:
            context = "Previous conversation context:\n"
            for msg in context_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"{role}: {content}\n"
            context += "\n"

        # Focus on current message
        current_content = current_message.get("content", "")
        current_role = current_message.get("role", "user")

        # Create focused prompt
        prompt = f"{context}Current {current_role} request: {current_content}\n\nPlease respond to the current request, taking into account the previous context if relevant."

        return prompt

    def analyze_text(self, text, analysis_type="general"):
        """Analyze any text content using AISuite"""
        prompt = self._get_analysis_prompt(analysis_type)
        formatted_prompt = prompt.format(text=text)

        return self.generate(formatted_prompt)

    def _get_analysis_prompt(self, analysis_type):
        """Get appropriate prompt template for analysis type"""
        prompts = {
            "log_analysis": """
                Analyze these agent execution logs and provide a concise summary:

                {text}

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
            """,
            "general": """
                Analyze the following text and provide insights:

                {text}
            """
        }
        return prompts.get(analysis_type, prompts["general"])

    def _initialize_aisuite(self):
        """Initialize AISuite client"""
        try:
            from aisuite import AISuiteClient
            return AISuiteClient()
        except ImportError:
            print("Warning: AISuite not available, using fallback")
            return None
```

### Week 3: LLMAnalyzer

**Goal**: Log analysis using the Core LLM Component

**Deliverables**:

- `LLMAnalyzer` class using Core LLM Component
- Intelligent activity identification
- Smart progress estimation and error detection

**Implementation**:

```python
class LLMAnalyzer:
    def __init__(self, core_llm_service):
        self.core_llm = core_llm_service
        self.cache = {}

    def analyze(self, logs):
        # Use Core LLM Component for log analysis
        log_text = '\n'.join(logs)
        return self.core_llm.analyze_text(log_text, analysis_type="log_analysis")
```

### Week 4: TerminalDisplay

**Goal**: Simple terminal display for real-time updates

**Deliverables**:

- `TerminalDisplay` class with basic terminal updates
- Simple progress indicators
- Clear status messages

**Implementation**:

```python
class TerminalDisplay:
    def __init__(self):
        self.last_message = ""

    def update(self, message):
        if message != self.last_message:
            print(f"\r{message}", end="", flush=True)
            self.last_message = message

    def finish(self, message):
        print(f"\r{message}")
```

### Week 5: Integration and Testing

**Goal**: Integrate all components and test

**Deliverables**:

- Complete integration with `ProcessManager`
- Basic testing
- Documentation

**Implementation**:

```python
class ProcessManager:
    def execute_agent(self, agent_path, method, parameters, monitoring=True):
        if monitoring:
            return self._execute_with_monitoring(agent_path, method, parameters)
        else:
            return self._execute_without_monitoring(agent_path, method, parameters)

    def _execute_with_monitoring(self, agent_path, method, parameters):
        # Start subprocess
        process = subprocess.Popen([...])

        # Initialize monitoring
        core_llm = CoreLLMService()
        streamer = LogStreamer(process)
        analyzer = LLMAnalyzer(core_llm)
        display = TerminalDisplay()

        # Start monitoring
        streamer.start()

        # Monitor execution
        while process.poll() is None:
            logs = streamer.get_logs()
            if logs:
                message = analyzer.analyze(logs)
                display.update(message)
            time.sleep(0.5)

        # Finish
        display.finish("✅ Execution complete")
        return result
```

## What We're NOT Building (YAGNI)

- ❌ Complex LLM integration
- ❌ Advanced error processing
- ❌ Progress tracking
- ❌ Caching systems
- ❌ Configuration management
- ❌ Multi-agent monitoring
- ❌ Performance metrics
- ❌ Error recovery
- ❌ Custom display components
- ❌ Complex testing
- ❌ Advanced documentation

## What We ARE Building (KISS)

- ✅ Real-time log streaming
- ✅ Simple pattern matching
- ✅ Basic terminal display
- ✅ Default monitoring behavior
- ✅ Simple on/off control
- ✅ Basic testing
- ✅ Simple documentation

## Success Criteria

- ✅ Real-time log streaming works
- ✅ Simple activity identification works
- ✅ Clear terminal updates work
- ✅ Default monitoring behavior works
- ✅ < 5% performance overhead
- ✅ 100% backward compatibility
- ✅ 4-week delivery timeline

## Risk Mitigation

- **Simple approach**: Fewer moving parts = fewer things to break
- **Incremental delivery**: Each week delivers working functionality
- **Minimal dependencies**: No external LLM APIs or complex libraries
- **Easy testing**: Simple components are easy to test

## Future Enhancements (If Needed)

Only add these if users actually request them:

- Advanced error analysis
- Progress tracking
- Performance metrics
- Configuration options
- Multi-agent monitoring

## Conclusion

This simple approach delivers the core value (real-time monitoring) quickly and reliably, following KISS and YAGNI principles. We can always add complexity later if users actually need it.
