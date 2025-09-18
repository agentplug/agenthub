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

**Purpose**: General-purpose LLM service using AISuite for the entire AgentHub system

**Implementation**:

```python
class CoreLLMService:
    def __init__(self, aisuite_client=None, model="gpt-3.5-turbo"):
        self.aisuite = aisuite_client or self._initialize_aisuite()
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
        if not self.aisuite:
            return self._fallback_response()

        if isinstance(input_data, str):
            # Single prompt - direct processing
            if system_prompt:
                # Combine system prompt with user prompt
                full_prompt = f"System: {system_prompt}\n\nUser: {input_data}"
            else:
                full_prompt = input_data

            return self.aisuite.generate(
                prompt=full_prompt,
                model=self.model,
                return_json=return_json,
                **kwargs
            )
        elif isinstance(input_data, list):
            # Messages - organize into context and focus on current
            prompt = self._organize_messages_to_prompt(input_data, system_prompt)
            return self.aisuite.generate(
                prompt=prompt,
                model=self.model,
                return_json=return_json,
                **kwargs
            )
        else:
            raise ValueError("input_data must be string (prompt) or list (messages)")

    def _organize_messages_to_prompt(self, messages, system_prompt=None):
        """Convert conversation messages to a single prompt with context"""
        if not messages:
            return ""

        # Separate context (previous messages) from current message
        context_messages = messages[:-1] if len(messages) > 1 else []
        current_message = messages[-1]

        # Build context from previous messages (keep it concise)
        context = ""
        if context_messages:
            context = "Previous conversation:\n"
            # Limit context to last 3-4 messages to avoid overwhelming
            recent_messages = context_messages[-3:] if len(context_messages) > 3 else context_messages
            for msg in recent_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                # Truncate long messages
                if len(content) > 200:
                    content = content[:200] + "..."
                context += f"{role}: {content}\n"
            context += "\n"

        # Current request
        current_content = current_message.get("content", "")
        current_role = current_message.get("role", "user")

        # Structure: System prompt + Context + Current request + Instructions
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(f"SYSTEM INSTRUCTIONS: {system_prompt}")
            prompt_parts.append("")

        if context:
            prompt_parts.append(context)

        prompt_parts.append(f"CURRENT {current_role.upper()} REQUEST: {current_content}")
        prompt_parts.append("")

        if system_prompt:
            prompt_parts.append("Remember the system instructions above and respond accordingly.")
        else:
            prompt_parts.append("Please respond to the current request, taking into account the previous context if relevant.")

        return "\n".join(prompt_parts)

    # Usage Examples with System Prompts:
    #
    # Single prompt with system prompt:
    # response = core_llm.generate("What is the weather?", system_prompt="You are a helpful weather assistant.")
    #
    # Conversation with system prompt:
    # messages = [
    #     {"role": "user", "content": "What is Python?"},
    #     {"role": "assistant", "content": "Python is a programming language..."},
    #     {"role": "user", "content": "How do I install it?"}
    # ]
    # response = core_llm.generate(messages, system_prompt="You are a programming tutor. Be concise and practical.")
    #
    # Log analysis with custom prompt:
    # log_prompt = "Analyze these logs: {text}"
    # response = core_llm.analyze_text(logs, log_prompt, "You are an expert at analyzing logs.")

    def analyze_text(self, text, prompt_template, system_prompt=None, return_json=False):
        """Analyze any text content using AISuite with custom prompt template"""
        formatted_prompt = prompt_template.format(text=text)
        return self.generate(formatted_prompt, system_prompt=system_prompt, return_json=return_json)

    def _initialize_aisuite(self):
        """Initialize AISuite client"""
        try:
            from aisuite import AISuiteClient
            return AISuiteClient()
        except ImportError:
            print("Warning: AISuite not available, using fallback")
            return None
```

### 3. LLMAnalyzer

**Purpose**: Log analysis using the Core LLM Component

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
- ✅ Core LLM component using AISuite for system-wide use
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
