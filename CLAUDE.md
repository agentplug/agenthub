# AgentHub - Claude Code Assistant Guide

**AgentHub** is an "App Store for AI Agents" - a Python framework enabling developers to discover, install, and use AI agents with one line of code.

**Status**: Alpha. Core features work through Phase 3.4 (Real-time Communication); see README badges for the honest state.

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
| **Implementing** | ✅ Searched codebase? ✅ Tavily only if needed? ✅ Need TODO (>3 steps)? |

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
Unfamiliar library/API? YES → Tavily search (efficient!)
                   NO ↓
Known error + tried 3x? YES → Tavily search solution
                   NO ↓
>3 steps or multiple files? YES → Create TODO
                   NO ↓
Confident? NO → Check codebase first, then search if needed
         YES → Implement
```

### **When to WebSearch (Use Tavily - Be Efficient)**

**Use Tavily web search tool when:**
- 🔍 Unfamiliar library/API: "FastAPI WebSocket 2024", "Pydantic v2 validators"
- 🔍 Unknown error: Copy full error + library name
- 🔍 Best practices: "Python async best practices 2024"
- 🔍 API compatibility: "Pydantic v2 breaking changes"
- 🔍 After 3 failed bug fix attempts

**DON'T search when:**
- ❌ Info already in codebase (use `codebase_search` first)
- ❌ Standard Python features (you know this)
- ❌ Already searched same query recently
- ❌ Can infer from existing code patterns

**Efficiency tips:**
- Batch related questions in one search query
- Search once, apply broadly
- Check codebase first, search second

**Tech context**: Python 3.11+, Pydantic v2, LiteLLM, LlamaIndex (rag extra), UV (NOT pip), MCP, websockets

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
2. **Explore**: Search codebase for patterns (do this first!)
3. **Research**: If truly unfamiliar, use Tavily (batch questions, search efficiently)
4. **Plan**: Break into steps (TODO if >3)
5. **Implement**: Follow patterns, test EACH step, iterate if fails (use Iterative Development Protocol)
6. **Verify**: Run tests, check linter, verify integration

**If implementation fails**: Read error → Check assumptions → Try different approach → Check examples → Tavily (after 3 attempts) → Ask user

---

## 🚀 Development Workflow

### **5-Step Process**

1. **Understand**: Read requirements, clarify ambiguities, identify success criteria
2. **Explore**: `codebase_search` (concepts) / `grep` (exact text) / read files
3. **Plan**: Break into steps, TODO if >3 steps
4. **Implement**: Follow patterns, read before edit, **test after EACH change, iterate if fails**
5. **Verify**: Tests pass, linter clean, integration works, cleanup done

**Note**: Step 4 uses Iterative Development Protocol - implement → test → iterate until working

### **Core Principles**

- **KISS** + **YAGNI**: Simple, only what's needed
- **Modify, don't create**: Edit existing files, create ONLY for new components
- **Git is backup**: No manual backups or temp implementation files
- **Test-first**: Tests immediately after functions
- **Autonomous**: Reasonable assumptions, proceed independently
- **Iterative**: Write → Test → Iterate until works (applies to ALL code: bugs AND features)

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

### **Documentation Files (.md) - DON'T Create Unless Asked**

⚠️ **NEVER create .md files proactively:**
- ❌ README.md (unless explicitly requested)
- ❌ Documentation files
- ❌ Design docs
- ❌ Tutorial files
- ❌ CHANGELOG.md

✅ **Only create .md when user explicitly asks**: "Create a README", "Write documentation for X"

### **Non-Committable Files - Use Semantic Prefixes**

**For files that shouldn't be committed** (verification scripts, debug outputs, test data):

**Required semantic prefixes:**
- `verify_*.py` - Verification scripts
- `debug_*.py` - Debug scripts
- `test_*.json` - Test output data
- `temp_*.py` - Temporary code
- `output_*.txt` - Output files
- `result_*.json` - Result files

**Add to .gitignore:**
```gitignore
# Temporary verification and debug files
verify_*
debug_*
test_*.json
temp_*
output_*
result_*
```

**Why use prefixes:**
- Clear intent (everyone knows it's temporary)
- Easy to find and delete
- .gitignore catches them automatically
- Prevents accidental commits

**Example:**
```
✅ GOOD: verify_api_response.py (clear temporary file)
❌ BAD: check.py (unclear, might commit by accident)

✅ GOOD: output_test_results.json (clear output file)
❌ BAD: results.json (might look like production data)
```

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
# Temporary scripts and output files (STILL MUST DELETE!)
verify_*
debug_*
test_assumption_*
temp_*
output_*
result_*
test_*.json
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
- ✅ **ALL temp scripts deleted** (verify_*, debug_*, output_*, result_*)
- ✅ **No .md files created** unless explicitly asked
- ✅ **`git status` clean** - only intended changes

---

## 🔧 Iterative Development Protocol

**Applies to**: Bug fixes AND new features/code

### **Iterative Loop** (Never assume it works on first try)

```
1. Understand requirement (bug to fix OR feature to add)
   ↓
2. Plan if complex (TODO if multi-file)
   ↓
3. Apply change (read file → exact edit → small, focused)
   ↓
4. Test immediately (run relevant script + unit tests)
   ↓
5. Evaluate: Works correctly? YES → Done | NO → Continue
   ↓
6. Analyze why failed (wrong approach? missing edge case? integration issue?)
   ↓
7. Try different approach (not same change again)
   ↓
Loop to step 3 until verified working
```

### **Key Rules (For ALL Code Changes)**

- ❌ Never "implement → assume it works → move on"
- ✅ Always "implement → test → verify → then move on"
- 🔄 Iterate with DIFFERENT approaches (not retry same thing)
- 🛑 After 3 attempts: Check codebase examples → After 5: Tavily search or ask user
- 🎯 For bugs: Fix root cause, not symptoms
- 🎯 For features: Meet requirements, don't over-engineer
- 📏 Small, targeted changes only
- 🧪 Test after EVERY iteration, not just at the end

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

**Dependencies**: UV (fast package manager), Click, Rich, Pydantic v2, MCP, LiteLLM, websockets; LlamaIndex via the rag extra

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

**Error Recovery**: Don't retry → Read error → Verify assumptions → Check codebase examples → Tavily (if still stuck) → Ask after 5 attempts

---

## 🔍 Debugging

**Enable**: `export AGENTHUB_LOG_LEVEL=DEBUG && export AGENTHUB_SUPPRESS_HTTP=false`

**Workflow**: Reproduce → Enable debug logging → Read logs (first error) → Check examples/ → Tavily (if needed) → Isolate → Fix → Verify

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
- [ ] **All temp files deleted** (verify_*, debug_*, output_*, result_*)
- [ ] **No .md files created** (unless explicitly requested)
- [ ] **Non-committable files use semantic prefixes**
- [ ] **`git status` clean** - only intended changes
- [ ] Examples work (if modified)
- [ ] Documentation updated (if needed)

**Self-review**: Simplest solution? Follows patterns? Clear names? Error handling? Edge cases? Understandable in 6 months?

---

## 💡 Remember (Top Rules)

1. ⚠️ **Read files before editing** (prevents 90% errors)
2. ⚠️ **Each shell = new shell** (prevents shell ID errors)
3. ⚠️ **Modify existing, don't create temp implementations** (git is backup)
4. ⚠️ **Delete temp files immediately** (verify_*, debug_*, output_*, result_*)
5. ⚠️ **Don't create .md files** unless explicitly asked
6. ⚠️ **Use semantic prefixes** for non-committable files
7. ⚠️ **Test after every change** (bugs AND features - catches errors early)
8. ⚠️ **Iterate until verified working** (ALL code: implement → test → iterate)
9. ⚠️ **Tavily search unfamiliar APIs** (only when needed, be efficient)
10. ⚠️ **`git status` clean before done** (no orphan files)

### **Quick Reference**

| When... | Do... |
|---------|-------|
| Can't find code | `codebase_search` or `grep` |
| Unfamiliar library | Tavily `web_search` for docs (be efficient) |
| Code doesn't work after 3 tries | Check examples → Tavily → Ask user (iterate!) |
| Create new file? | Only if new architectural component |
| Create .md file? | NEVER - unless explicitly asked |
| Temp/output files? | Use semantic prefixes (verify_*, debug_*, output_*) |
| Keep temp script? | NO - delete immediately |
| Task complete? | Check `git status` is clean |

**Success = Working Code + Passing Tests + Clean Workspace**

---

**Simple, working code beats complex, perfect code. Test early, test often, clean up always.**
