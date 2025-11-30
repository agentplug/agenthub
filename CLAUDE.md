# AgentHub - Claude Code Assistant Guide

**AgentHub** is an "App Store for AI Agents" - a Python framework enabling developers to discover, install, and use AI agents with one line of code.

**Status**: Production-ready. Core features complete through Phase 3.4 (Real-time Communication).

---

## ⚠️ CRITICAL: Error Prevention

### **Top 2 Errors - 90% of Failures**

**Error 1: "Error editing file"**
- Cause: Didn't read file first OR old_string mismatch
- Fix: ALWAYS `read_file()` → Copy EXACT text → Edit

**Error 2: "No shell found with ID"**
- Cause: Assumed shell persistence (each command = NEW shell)
- Fix: Use absolute paths OR `cd /path && command` in single line

### **Pre-Action Checklist (Check BEFORE Every Action)**

| Before... | Ask Yourself... |
|-----------|-----------------|
| **Editing file** | ✅ Read file first? ✅ Exact old_string? ✅ File exists? |
| **Shell command** | ✅ Absolute paths? ✅ New shell? ✅ `cd` in same command? |
| **Implementing** | ✅ Searched codebase? ✅ Web searched unfamiliar APIs? ✅ Need TODO (>3 steps)? |

### **Common Fixes**

```bash
# "old_string not found" → Read file again, copy EXACT text
# "No shell ID" → Use: cd /Users/nguyennm/Project/agenthub && command
# "File not found" → Use write() for new files, not search_replace()
```

---

## 🧠 Decision Framework

### **Decision Tree**

```
Received request → Know codebase structure? NO → codebase_search
                   YES ↓
Know file locations? NO → grep/codebase_search
                   YES ↓
Unfamiliar library/API? YES → web_search docs
                   NO ↓
Known error pattern? YES → web_search solution
                   NO ↓
>3 steps or multiple files? YES → Create TODO
                   NO ↓
Confident? NO → Explore more
         YES → Implement
```

### **When to Web Search**

**ALWAYS search:**
- 🔍 Library docs: "FastAPI WebSocket 2024", "Pydantic v2 validators"
- 🔍 Error messages: Copy full error + library name
- 🔍 Best practices: "Python async best practices 2024"
- 🔍 API compatibility: "Pydantic v2 breaking changes"

**Tech context**: Python 3.11+, FastAPI, Pydantic v2, LlamaIndex, UV (NOT pip), MCP, WebSockets

### **When to Plan vs. Proceed**

| Proceed Directly | Create TODO First |
|------------------|-------------------|
| Single file edit | 3+ files |
| Add function | New feature/module |
| Fix linter error | Refactoring across files |
| Add docstring | Complex integration |

---

## 🤖 LLM Reasoning (6-Step Protocol)

1. **Understand**: Paraphrase request, identify goals
2. **Explore**: Search codebase for patterns
3. **Research**: Web search unfamiliar concepts
4. **Plan**: Break into steps (TODO if >3)
5. **Implement**: Follow patterns, test each step
6. **Verify**: Run tests, check linter, verify integration

**If fails**: Read error → Check assumptions → Web search → Try different approach → Ask user after 3 attempts

---

## 🚀 Development Workflow

### **5-Step Process**

1. **Understand**: Read requirements, clarify ambiguities, identify success criteria
2. **Explore**: `codebase_search` (concepts) / `grep` (exact text) / read files
3. **Plan**: Break into steps, TODO if >3 steps
4. **Implement**: Follow patterns, read before edit, test after each change
5. **Verify**: Tests pass, linter clean, integration works, cleanup done

### **Core Principles**

- **KISS** + **YAGNI**: Simple, only what's needed
- **Modify, don't create**: Edit existing files, create ONLY for new components
- **Git is backup**: No manual backups or temp implementation files
- **Test-first**: Tests immediately after functions
- **Autonomous**: Reasonable assumptions, proceed independently
- **Incremental**: Write → Test → Fix → Continue

---

## 📝 File Philosophy

### **Modify vs. Create**

| Action | Modify Existing | Create New |
|--------|----------------|------------|
| Fix bug | ✅ Yes | ❌ No |
| Add feature to module | ✅ Yes | ❌ No |
| Experiment approach | ✅ Yes (git has backup) | ❌ No temp files |
| New architectural component | ❌ | ✅ Yes |
| New tool | ❌ | ✅ Yes |
| Unit tests for new feature | ❌ | ✅ Yes |

### **Temporary Verification Scripts**

**Allowed** (with strict rules):
- ✅ Quick assumption verification (e.g., check API response format)
- ✅ One-off debugging (e.g., verify embedding dimensions)

**MANDATORY rules:**
1. Delete within MINUTES (same session)
2. Name: `verify_*.py`, `debug_*.py`, `test_assumption_*.py`
3. < 50 lines
4. Run → Get answer → DELETE immediately
5. NEVER commit

**Lifecycle**: Create (1 min) → Run (30 sec) → Delete (immediate) → Apply fix to real code

**.gitignore safety net** (still must delete):
```gitignore
verify_*.py
debug_*.py
test_assumption_*.py
temp_*.py
```

---

## ✅ Quality & Definition of Done

### **After Every Change**

1. Linter: `ruff check <files>`, Type check: `mypy <files>`
2. Write + run tests: `pytest tests/path/test_file.py -v`
3. Integration check + examples
4. Delete temp scripts, remove debug prints
5. `git status` → Should be clean

### **Done = ALL True**

- ✅ Code works + tests pass + no linter errors
- ✅ Type hints + docstrings (public APIs)
- ✅ **ALL temp scripts deleted** (verify_*.py, debug_*.py)
- ✅ **`git status` clean** - only intended changes

---

## 🔧 Bug Fixing Protocol

### **Iterative Loop** (Never assume one fix works)

```
1. Understand bug (reproduce, read error, identify root cause)
   ↓
2. Plan if complex (TODO if multi-file)
   ↓
3. Apply targeted fix (read file → exact edit)
   ↓
4. Test immediately (run script that revealed bug + unit tests)
   ↓
5. Evaluate: Fixed? YES → Done | NO → Continue
   ↓
6. Analyze why fix failed (wrong assumption? deeper issue?)
   ↓
7. Try different approach (not same fix again)
   ↓
Loop to step 3 until verified fixed
```

### **Key Rules**

- ❌ Never "fix → assume it works → move on"
- ✅ Always "fix → test → verify → then move on"
- 🔄 Iterate with DIFFERENT approaches (not retry same fix)
- 🛑 After 5 attempts: Web search or ask user
- 🎯 Fix root cause, not symptoms
- 📏 Small, targeted changes only

---

## 📁 Project Structure

```
agenthub/
├── core/              # Core agent system (agents, tools, communication, llm, knowledge)
├── runtime/           # Process management, isolated execution
├── sdk/              # Public API (load_agent, solve)
├── github/           # GitHub-based agent registry
├── builtin/tools/    # Built-in tools (RAG, web_search)
├── cli/              # Command-line interface
└── storage/          # Local caching and persistence

examples/             # Usage examples
tests/               # Test suites (phase-based organization)
```

---

## 🔑 Key Patterns

### **Agent Loading**
```python
import agenthub as ah
agent = ah.load_agent("namespace/agent-name")
result = agent.solve("Natural language goal")
```

### **MCP Tools**
```python
from agenthub.core.tools import tool, run_resources

@tool(name="my_tool", description="...")
def my_tool(param: str) -> dict:
    return {"result": param}

run_resources()  # Starts MCP server
```

### **Adding New Tool**
1. Create `agenthub/builtin/tools/<tool_name>/tool.py`
2. Use `@tool` decorator
3. Export in `__init__.py`
4. Create example in `examples/builtin_tools/`
5. Write tests in `tests/phase2.5_tool_injection/`

---

## ⚙️ Technical Details

**Dependencies**: UV (fast package manager), Click, Rich, Pydantic v2, MCP, FastAPI, WebSockets, LlamaIndex

**Code Style**: Black (88 chars), Ruff, MyPy (strict), isort

**Env Vars**: `AGENTHUB_DIR`, `AGENTHUB_MCP_HOST/PORT`, `AGENTHUB_LOG_LEVEL`, `AGENTHUB_SUPPRESS_HTTP`

**Pre-commit**: `ruff check agenthub/ && mypy agenthub/ && pytest tests/ -v`

---

## 🐛 Error Patterns Library

| Error | Cause | Solution |
|-------|-------|----------|
| MCP TaskGroup error | Connection test fails | Return success=True, tool calls work anyway |
| Package not in UV env | Missing dependency | Add to agent.yaml or requirements.txt |
| WebSocket disconnect | No cleanup | Use context managers, explicit close() |
| Import error | Missing package or circular import | Check requirements.txt, verify __init__.py exports |

**Error Recovery**: Don't retry immediately → Read error → Verify assumptions → Web search → Try different approach → Ask after 3 attempts

---

## 🔍 Debugging

**Enable**: `export AGENTHUB_LOG_LEVEL=DEBUG && export AGENTHUB_SUPPRESS_HTTP=false`

**Workflow**: Reproduce → Enable debug logging → Read logs (first error) → Web search → Check examples/ → Isolate → Fix → Verify

**Commands**:
```python
ah.list_installed_agents()
from agenthub.core.tools.registry import get_tool_registry
get_tool_registry().list_tools()
```

---

## 📝 Documentation

**Code**: Docstrings (public APIs), type hints, explain WHY not WHAT, document exceptions

**Example structure**:
```python
"""Brief description of what this demonstrates."""
# Setup
# Main logic (commented)
# Cleanup
```

**Comments**: Non-obvious decisions, link to issues/PRs, `# TODO(user): description`

---

## 🎯 Current Focus

**Works well**: ✅ Agent loading, MCP tools, UV isolation, WebSockets, GitHub registry, RAG/web search

**Needs care**: ⚠️ Multi-agent orchestration, large-scale tool injection, cross-platform compatibility

---

## 🤝 Contributing

### **Pre-Commit Checklist**

- [ ] Tests pass: `pytest tests/ -v`
- [ ] No linter errors: `ruff check agenthub/`
- [ ] Type checking: `mypy agenthub/`
- [ ] **All temp scripts deleted** (verify_*.py, debug_*.py)
- [ ] **`git status` clean** - only intended changes
- [ ] Examples work (if modified)
- [ ] Documentation updated (if needed)

**Self-review**: Simplest solution? Follows patterns? Clear names? Error handling? Edge cases? Understandable in 6 months?

---

## 💡 Remember (Top Rules)

1. ⚠️ **Read files before editing** (prevents 90% errors)
2. ⚠️ **Each shell = new shell** (prevents shell ID errors)
3. ⚠️ **Modify existing, don't create temp implementations** (git is backup)
4. ⚠️ **Delete temp verification scripts immediately** (minutes, not forever)
5. ⚠️ **Test after every change** (catches errors early)
6. ⚠️ **Iterate until bug verified fixed** (don't assume)
7. ⚠️ **Web search unfamiliar APIs** (prevents implementation errors)
8. ⚠️ **`git status` clean before done** (no orphan files)

### **Quick Reference**

| When... | Do... |
|---------|-------|
| Can't find code | `codebase_search` or `grep` |
| Unfamiliar library | `web_search` for docs |
| Bug after 3 tries | Web search error or ask user |
| Create new file? | Only if new architectural component |
| Keep temp script? | NO - delete immediately |
| Task complete? | Check `git status` is clean |

**Success = Working Code + Passing Tests + Clean Workspace**

---

**Simple, working code beats complex, perfect code. Test early, test often, clean up always.**
