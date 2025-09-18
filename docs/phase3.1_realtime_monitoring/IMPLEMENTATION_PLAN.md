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
    def __init__(self, aisuite_client=None, model="openai:gpt-3.5-turbo"):
        self.client = aisuite_client or self._initialize_aisuite()
        self.model = model
        self.cache = {}

    def generate(self, input_data, system_prompt=None, return_json=False, **kwargs):
        """Adaptive LLM generation using AISuite

        Args:
            input_data: Either a string (single prompt) or list of messages (conversation)
            system_prompt: Optional system prompt to define AI behavior and context
            return_json: If True, request JSON response from AISuite
            **kwargs: Additional parameters for AISuite
        """
        if not self.client:
            return self._fallback_response()

        try:
            if isinstance(input_data, str):
                # Single prompt - convert to messages format
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": input_data})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content

            elif isinstance(input_data, list):
                # Messages - organize into context and focus on current
                messages = self._organize_messages_to_aisuite_format(input_data, system_prompt)

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
            else:
                raise ValueError("input_data must be string (prompt) or list (messages)")
        except Exception as e:
            print(f"AISuite generation failed: {e}")
            return self._fallback_response()

    def _organize_messages_to_aisuite_format(self, messages, system_prompt=None):
        """Convert conversation messages to AISuite messages format with context management"""
        if not messages:
            return []

        # Separate context (previous messages) from current message
        context_messages = messages[:-1] if len(messages) > 1 else []
        current_message = messages[-1]

        # Build messages list for AISuite
        aisuite_messages = []

        # Add system prompt if provided
        if system_prompt:
            aisuite_messages.append({"role": "system", "content": system_prompt})

        # Add context messages (limit to last 3-4 to avoid overwhelming)
        if context_messages:
            recent_messages = context_messages[-3:] if len(context_messages) > 3 else context_messages
            for msg in recent_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                # Truncate long messages
                if len(content) > 200:
                    content = content[:200] + "..."
                aisuite_messages.append({"role": role, "content": content})

        # Add current message
        current_content = current_message.get("content", "")
        current_role = current_message.get("role", "user")
        aisuite_messages.append({"role": current_role, "content": current_content})

        return aisuite_messages

    def analyze_text(self, text, prompt_template, system_prompt=None, return_json=False):
        """Analyze any text content using AISuite with custom prompt template"""
        formatted_prompt = prompt_template.format(text=text)

        # If JSON response is requested, modify the prompt to request JSON format
        if return_json:
            json_instruction = "\n\nPlease respond with valid JSON only, no additional text."
            formatted_prompt += json_instruction

        return self.generate(formatted_prompt, system_prompt=system_prompt)

    def _initialize_aisuite(self):
        """Initialize AISuite client"""
        try:
            import aisuite as ai
            return ai.Client()
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
        self.log_analysis_prompt = self._get_log_analysis_prompt()

    def analyze(self, logs):
        # Use Core LLM Component for log analysis with custom prompt and system prompt
        log_text = '\n'.join(logs)
        system_prompt = "You are an expert at analyzing agent execution logs. Focus on identifying what the agent is doing, detecting errors, and providing actionable insights."
        response = self.core_llm.analyze_text(log_text, self.log_analysis_prompt, system_prompt, return_json=True)
        return self._parse_log_analysis_response(response)

    def _parse_log_analysis_response(self, response) -> LogAnalysis:
        """Parse log analysis response (handles both JSON objects and strings)"""
        try:
            # If AISuite returns JSON object directly
            if isinstance(response, dict):
                data = response
            else:
                # If AISuite returns JSON string, parse it
                data = json.loads(response)

            return LogAnalysis(
                summary=data.get("summary", "Working..."),
                progress=data.get("progress", 0),
                status=data.get("status", "working"),
                errors=data.get("errors", []),
                suggestions=data.get("suggestions", [])
            )
        except (json.JSONDecodeError, TypeError):
            return self._fallback_analysis([])

    def _fallback_analysis(self, logs: List[str]) -> LogAnalysis:
        """Fallback analysis when AISuite is not available"""
        log_text = ' '.join(logs).lower()

        if any(word in log_text for word in ['error', 'failed', 'exception']):
            return LogAnalysis("❌ Error detected", 0, "error", ["Error found"], ["Check logs"])
        elif any(word in log_text for word in ['processing', 'analyzing', 'working']):
            return LogAnalysis("📊 Processing...", 50, "working", [], [])
        elif any(word in log_text for word in ['complete', 'finished', 'done']):
            return LogAnalysis("✅ Complete", 100, "complete", [], [])
        else:
            return LogAnalysis("🔄 Working...", 25, "working", [], [])

    def _get_log_analysis_prompt(self):
        """Get log analysis prompt template"""
        return """
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
        """
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
