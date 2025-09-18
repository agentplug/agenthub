# Phase 3.1: Integration Guide

## Overview

This document explains how the Phase 3.1 real-time monitoring feature integrates with the current AgentHub implementation. It shows the specific changes needed in existing components and how the new monitoring system fits into the current architecture.

## Current Architecture Integration Points

### 1. ProcessManager Integration

**Current Implementation** (`agenthub/runtime/process_manager.py`):

```python
class ProcessManager:
    def execute_agent_method(self, agent_path, method, parameters):
        # Current: Uses subprocess.run() with capture_output=True
        result = subprocess.run(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            capture_output=True,  # ← Captures ALL output at the END
            text=True,
            timeout=self.timeout,
        )
        return result
```

**New Implementation with Monitoring**:

```python
class ProcessManager:
    def __init__(self, monitoring_enabled=True):
        self.monitoring_enabled = monitoring_enabled
        self.llm_client = None
        if monitoring_enabled:
            self.llm_client = self._initialize_llm_client()

    def execute_agent_method(self, agent_path, method, parameters):
        if self.monitoring_enabled:
            return self._execute_with_monitoring(agent_path, method, parameters)
        else:
            return self._execute_without_monitoring(agent_path, method, parameters)

    def _execute_with_monitoring(self, agent_path, method, parameters):
        # Start subprocess with real-time monitoring
        process = subprocess.Popen(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Initialize monitoring components
        core_llm = CoreLLMService()
        streamer = LogStreamer(process)
        analyzer = LLMAnalyzer(core_llm)
        display = TerminalDisplay()

        # Start real-time monitoring
        streamer.start()
        display.start()

        # Monitor until completion
        while process.poll() is None:
            logs = streamer.get_logs()
            if logs:
                analysis = analyzer.analyze(logs)
                display.update(analysis)
            time.sleep(0.5)

        # Get final result
        stdout, stderr = process.communicate()
        display.stop()

        return subprocess.CompletedProcess(
            args=process.args,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr
        )

    def _execute_without_monitoring(self, agent_path, method, parameters):
        # Keep existing behavior for backward compatibility
        result = subprocess.run(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        return result
```

### 2. AgentWrapper Integration

**Current Implementation** (`agenthub/core/agents/wrapper.py`):

```python
class AgentWrapper:
    def method_caller(self, method_name, parameters):
        # Current: Direct execution without monitoring
        execution_data = {
            "method": method_name,
            "parameters": parameters,
            "tool_context": self.get_tool_context_json()
        }

        result = self.process_manager.execute_agent_method(
            self.agent_path, method_name, execution_data
        )
        return result
```

**New Implementation with Monitoring**:

```python
class AgentWrapper:
    def __init__(self, agent_path, process_manager=None, monitoring=True):
        self.agent_path = agent_path
        self.monitoring = monitoring
        self.process_manager = process_manager or ProcessManager(monitoring_enabled=monitoring)

    def method_caller(self, method_name, parameters):
        # Resolve file paths before execution
        parameters = self._resolve_file_paths(parameters)

        execution_data = {
            "method": method_name,
            "parameters": parameters,
            "tool_context": self.get_tool_context_json()
        }

        # Execute with monitoring if enabled
        result = self.process_manager.execute_agent_method(
            self.agent_path, method_name, execution_data
        )
        return result
```

### 3. load_agent Function Integration

**Current Implementation** (`agenthub/sdk/load_agent.py`):

```python
def load_agent(
    agent_path,
    external_tools=None,
    knowledge=None,
    installation_commands=None,
    timeout=300
):
    # Current: No monitoring parameter
    agent_wrapper = AgentWrapper(agent_path)
    return agent_wrapper
```

**New Implementation with Monitoring**:

```python
def load_agent(
    agent_path,
    external_tools=None,
    knowledge=None,
    installation_commands=None,
    timeout=300,
    monitoring=True  # ← New parameter
):
    # Create process manager with monitoring setting
    process_manager = ProcessManager(monitoring_enabled=monitoring)

    # Create agent wrapper with monitoring
    agent_wrapper = AgentWrapper(
        agent_path=agent_path,
        process_manager=process_manager,
        monitoring=monitoring
    )

    return agent_wrapper
```

## New Components Integration

### 1. LogStreamer Component

**Location**: `agenthub/monitoring/log_streamer.py`

```python
import threading
import queue
import subprocess
from typing import List, Optional

class LogStreamer:
    def __init__(self, process: subprocess.Popen):
        self.process = process
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.running = False
        self.stdout_thread = None
        self.stderr_thread = None

    def start(self):
        """Start real-time log streaming"""
        self.running = True
        self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self.stdout_thread.start()
        self.stderr_thread.start()

    def _read_stdout(self):
        """Read stdout in real-time"""
        for line in iter(self.process.stdout.readline, ''):
            if not self.running:
                break
            self.stdout_queue.put(line.strip())

    def _read_stderr(self):
        """Read stderr in real-time"""
        for line in iter(self.process.stderr.readline, ''):
            if not self.running:
                break
            self.stderr_queue.put(line.strip())

    def get_logs(self) -> List[str]:
        """Get recent log lines"""
        logs = []
        while not self.stdout_queue.empty():
            logs.append(self.stdout_queue.get())
        while not self.stderr_queue.empty():
            logs.append(self.stderr_queue.get())
        return logs

    def stop(self):
        """Stop log streaming"""
        self.running = False
        if self.stdout_thread:
            self.stdout_thread.join(timeout=1)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=1)
```

### 2. Core LLM Component

**Location**: `agenthub/core/llm/llm_service.py`

```python
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class LogAnalysis:
    summary: str
    progress: int
    status: str
    errors: List[str]
    suggestions: List[str]

class CoreLLMService:
    def __init__(self, aisuite_client=None, model="gpt-3.5-turbo"):
        self.aisuite = aisuite_client or self._initialize_aisuite()
        self.model = model
        self.cache = {}

    def _initialize_aisuite(self):
        """Initialize AISuite client"""
        try:
            from aisuite import AISuiteClient
            return AISuiteClient()
        except ImportError:
            print("Warning: AISuite not available, using fallback")
            return None

    def generate(self, input_data, system_prompt=None, **kwargs) -> str:
        """Adaptive LLM generation using AISuite

        Args:
            input_data: Either a string (single prompt) or list of messages (conversation)
            system_prompt: Optional system prompt to define AI behavior and context
            **kwargs: Additional parameters for AISuite
        """
        if not self.aisuite:
            return self._fallback_response()

        try:
            if isinstance(input_data, str):
                # Single prompt - direct processing
                if system_prompt:
                    # Combine system prompt with user prompt
                    full_prompt = f"System: {system_prompt}\n\nUser: {input_data}"
                else:
                    full_prompt = input_data

                response = self.aisuite.generate(
                    prompt=full_prompt,
                    model=self.model,
                    **kwargs
                )
                return response
            elif isinstance(input_data, list):
                # Messages - organize into context and focus on current
                prompt = self._organize_messages_to_prompt(input_data, system_prompt)
                response = self.aisuite.generate(
                    prompt=prompt,
                    model=self.model,
                    **kwargs
                )
                return response
            else:
                raise ValueError("input_data must be string (prompt) or list (messages)")
        except Exception as e:
            print(f"AISuite generation failed: {e}")
            return self._fallback_response()

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

    # Usage Examples:
    #
    # Single prompt:
    # response = core_llm.generate("What is the weather today?")
    #
    # Single prompt with system prompt:
    # response = core_llm.generate("What is the weather?", system_prompt="You are a helpful weather assistant.")
    #
    # Conversation messages:
    # messages = [
    #     {"role": "user", "content": "What is Python?"},
    #     {"role": "assistant", "content": "Python is a programming language..."},
    #     {"role": "user", "content": "How do I install it?"}
    # ]
    # response = core_llm.generate(messages)
    #
    # Conversation with system prompt:
    # response = core_llm.generate(messages, system_prompt="You are a programming tutor. Be concise and practical.")
    #
    # Example output structure:
    # SYSTEM INSTRUCTIONS: You are a programming tutor. Be concise and practical.
    #
    # Previous conversation:
    # user: What is Python?
    # assistant: Python is a programming language...
    #
    # CURRENT USER REQUEST: How do I install it?
    #
    # Remember the system instructions above and respond accordingly.

    def analyze_text(self, text: str, analysis_type: str = "general", system_prompt: str = None) -> Any:
        """Analyze any text content using AISuite"""
        if not text:
            return self._fallback_analysis([])

        prompt = self._get_analysis_prompt(analysis_type)
        formatted_prompt = prompt.format(text=text)

        response = self.generate(formatted_prompt, system_prompt=system_prompt)

        if analysis_type == "log_analysis":
            return self._parse_log_analysis_response(response)
        else:
            return response

    def _get_analysis_prompt(self, analysis_type: str) -> str:
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
            """,
            "error_analysis": """
                Analyze this error and provide suggestions:

                {text}

                Provide:
                1. Error type and cause
                2. Possible solutions
                3. Prevention tips
            """
        }
        return prompts.get(analysis_type, prompts["general"])

    def _parse_log_analysis_response(self, response: str) -> LogAnalysis:
        """Parse log analysis response"""
        try:
            data = json.loads(response)
            return LogAnalysis(
                summary=data.get("summary", "Working..."),
                progress=data.get("progress", 0),
                status=data.get("status", "working"),
                errors=data.get("errors", []),
                suggestions=data.get("suggestions", [])
            )
        except json.JSONDecodeError:
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

    def _fallback_response(self) -> str:
        """Fallback response when AISuite is not available"""
        return "AISuite not available"
```

### 3. LLMAnalyzer Component

**Location**: `agenthub/monitoring/llm_analyzer.py`

```python
from agenthub.core.llm.llm_service import CoreLLMService, LogAnalysis
from typing import List

class LLMAnalyzer:
    def __init__(self, core_llm_service: CoreLLMService):
        self.core_llm = core_llm_service
        self.cache = {}

    def analyze(self, logs: List[str]) -> LogAnalysis:
        """Analyze logs using Core LLM Component"""
        log_text = '\n'.join(logs)
        system_prompt = "You are an expert at analyzing agent execution logs. Focus on identifying what the agent is doing, detecting errors, and providing actionable insights."
        return self.core_llm.analyze_text(log_text, analysis_type="log_analysis", system_prompt=system_prompt)
```

### 4. TerminalDisplay Component

**Location**: `agenthub/monitoring/terminal_display.py`

```python
import sys
import time
from typing import Optional
from .llm_analyzer import LogAnalysis

class TerminalDisplay:
    def __init__(self):
        self.running = False
        self.last_update = ""
        self.start_time = None

    def start(self):
        """Start terminal display"""
        self.running = True
        self.start_time = time.time()
        print("\n🚀 Starting agent execution...")

    def update(self, analysis: LogAnalysis):
        """Update terminal display with new analysis"""
        if not self.running:
            return

        # Create update message
        elapsed = time.time() - self.start_time if self.start_time else 0
        progress_bar = self._create_progress_bar(analysis.progress)

        update_message = f"\r{analysis.summary} {progress_bar} ({elapsed:.1f}s)"

        # Only update if message changed
        if update_message != self.last_update:
            sys.stdout.write(update_message)
            sys.stdout.flush()
            self.last_update = update_message

        # Show errors and suggestions
        if analysis.errors:
            print(f"\n❌ Errors: {', '.join(analysis.errors)}")
        if analysis.suggestions:
            print(f"💡 Suggestions: {', '.join(analysis.suggestions)}")

    def _create_progress_bar(self, progress: int) -> str:
        """Create simple progress bar"""
        bar_length = 20
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"[{bar}] {progress}%"

    def stop(self):
        """Stop terminal display"""
        self.running = False
        print("\n✅ Agent execution completed")
```

## Integration Flow

### 1. User Code Integration

**Before (Current)**:

```python
import agenthub as ah

# Load agent without monitoring
agent = ah.load_agent("agentplug/scientific-paper-analyzer")
result = agent.analyze_paper("sample.pdf")
# [Long silence...]
print(result)
```

**After (With Monitoring)**:

```python
import agenthub as ah

# Load agent with monitoring (default: True)
agent = ah.load_agent("agentplug/scientific-paper-analyzer")
result = agent.analyze_paper("sample.pdf")
# 🚀 Starting agent execution...
# 📊 Processing document: sample.pdf
# 🔍 Using tool 'web_search' to find related research
# ✅ Tool execution successful (2.3s)
# 🎯 Analysis complete! Found 15 key insights
print(result)
```

### 2. Backward Compatibility

**Disable Monitoring**:

```python
import agenthub as ah

# Load agent without monitoring (backward compatible)
agent = ah.load_agent("agentplug/scientific-paper-analyzer", monitoring=False)
result = agent.analyze_paper("sample.pdf")
# [Silent execution - no monitoring output]
print(result)
```

## File Structure Changes

### New Files Added

```
agenthub/core/llm/
├── __init__.py
└── llm_service.py

agenthub/monitoring/
├── __init__.py
├── log_streamer.py
├── llm_analyzer.py
├── terminal_display.py
└── integration.py
```

### Modified Files

```
agenthub/runtime/process_manager.py          # Add monitoring support
agenthub/core/agents/wrapper.py             # Add monitoring parameter
agenthub/sdk/load_agent.py                  # Add monitoring parameter
agenthub/__init__.py                        # Update exports
```

## Dependencies

### New Dependencies

```python
# requirements.txt additions
aisuite>=1.0.0
```

### Existing Dependencies Used

```python
# Already available
threading
queue
subprocess
json
time
sys
```

## Configuration

### Environment Variables

```bash
# Optional: AISuite configuration (if not set, falls back to simple analysis)
export AISUITE_API_KEY="your-api-key-here"
export AISUITE_MODEL="gpt-3.5-turbo"

# Optional: Monitoring settings
export AGENTHUB_MONITORING_ENABLED="true"
export AGENTHUB_MONITORING_UPDATE_INTERVAL="0.5"
```

### Default Settings

```python
# Default configuration
MONITORING_ENABLED = True
UPDATE_INTERVAL = 0.5  # seconds
AISUITE_MODEL = "gpt-3.5-turbo"
CACHE_SIZE = 100
```

## Testing Integration

### Unit Tests

```python
# tests/monitoring/test_log_streamer.py
# tests/monitoring/test_llm_analyzer.py
# tests/monitoring/test_terminal_display.py
```

### Integration Tests

```python
# tests/monitoring/test_integration.py
def test_monitoring_integration():
    agent = ah.load_agent("test-agent", monitoring=True)
    # Test monitoring functionality
```

## Migration Guide

### For Existing Users

1. **No code changes required** - monitoring is enabled by default
2. **Optional**: Set `monitoring=False` to disable
3. **Optional**: Set `OPENAI_API_KEY` for enhanced analysis

### For Developers

1. **Update imports** if using ProcessManager directly
2. **Add monitoring parameter** to custom agent wrappers
3. **Test with monitoring enabled/disabled**

## Performance Considerations

### Overhead

- **LLM calls**: ~200-500ms per analysis
- **Threading**: Minimal overhead
- **Memory**: ~10MB for log buffering

### Optimization

- **Caching**: LLM responses cached to reduce API calls
- **Batching**: Multiple log lines analyzed together
- **Fallback**: Simple analysis when LLM unavailable

## Error Handling

### AISuite Failures

- **Fallback to simple analysis** when AISuite unavailable
- **Graceful degradation** without breaking agent execution
- **Clear error messages** for debugging

### Monitoring Failures

- **Continue agent execution** even if monitoring fails
- **Log monitoring errors** for debugging
- **Fallback to silent mode** if critical errors occur

## Security Considerations

### API Keys

- **Environment variables** for AISuite API key
- **No hardcoded credentials** in code
- **Optional feature** - works without API key

### Log Content

- **No sensitive data** sent to AISuite
- **Local processing** for sensitive logs
- **Configurable filtering** for sensitive information

This integration guide shows how the Phase 3.1 real-time monitoring feature seamlessly integrates with the existing AgentHub architecture while maintaining backward compatibility and providing enhanced user experience.
