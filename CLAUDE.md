# AgentHub - Claude Code Assistant Guide

This file provides context and guidance for Claude Code when working with the AgentHub codebase.

---

## 🎯 Quick Context

**AgentHub** is an "App Store for AI Agents" - a Python framework that enables developers to discover, install, and use AI agents with one line of code. Think `npm install` but for AI agents.

**Current Status**: Production-ready. Core features complete through Phase 3.4 (Real-time Communication).

---

## ⚠️ CRITICAL: Error Prevention Protocol

### **Most Common Errors & How to Prevent Them**

#### **Error 1: "Error editing file"**
**Cause**: You didn't read the file first, or old_string doesn't match exactly.

**MANDATORY File Edit Protocol:**
```
1. ✅ ALWAYS read_file() FIRST
2. ✅ COPY EXACT text from read output (including whitespace)
3. ✅ Verify file exists (if unsure, use list_dir/glob_file_search)
4. ✅ Keep edits small (5-20 lines at a time, just edit big if you are very confidence about that)

❌ NEVER: Edit without reading first
❌ NEVER: Guess at file content
❌ NEVER: Assume whitespace/quotes
```

**Example Safe Workflow:**
```python
# Step 1: Read first
read_file("config.py")

# Step 2: See output has: "    model: str = 'gpt-4'"
#         Note: 4 spaces, single quotes

# Step 3: Use EXACT text
search_replace(
    file_path="config.py",
    old_string="    model: str = 'gpt-4'",  # Exact match!
    new_string="    model: str = 'gpt-4o'"
)
```

#### **Error 2: "No shell found with ID"**
**Cause**: You assumed shell persistence. Each command runs in a NEW shell.

**MANDATORY Shell Command Protocol:**
```
1. ✅ Each command = NEW shell (no persistence)
2. ✅ Use absolute paths: /Users/nguyennm/Project/agenthub/file.py
3. ✅ Include cd in same command: cd /path && command
4. ✅ NEVER reference shell IDs or assume previous state

❌ NEVER: Assume you're still in previous directory
❌ NEVER: Reference "shell 12" or previous sessions
❌ NEVER: Split cd and command into separate calls
```

**Example Safe Workflow:**
```bash
# ❌ WRONG (assumes shell persistence):
# Command 1: cd /Users/nguyennm/Project/agenthub
# Command 2: python script.py  # ERROR! Different shell!

# ✅ RIGHT (single command with full context):
cd /Users/nguyennm/Project/agenthub && python script.py

# ✅ EVEN BETTER (absolute paths):
python /Users/nguyennm/Project/agenthub/script.py
```

### **Universal Pre-Action Checklist**

**BEFORE editing ANY file:**
- [ ] Have I read this file with `read_file()`?
- [ ] Is old_string an exact copy from the read output?
- [ ] Does the file exist? (Check with `list_dir` if unsure)
- [ ] Is my edit small enough (< 20 lines)?

**BEFORE running ANY shell command:**
- [ ] Am I using absolute paths?
- [ ] Have I included `cd` in the same command if needed?
- [ ] Am I assuming this is a new shell? (Answer: YES)
- [ ] For background processes, did I set `is_background=true`?

**BEFORE implementing ANY feature:**
- [ ] Have I searched the codebase for similar patterns?
- [ ] Do I understand the existing architecture?
- [ ] Have I web searched for unfamiliar libraries/APIs?
- [ ] Do I need a TODO list (>3 steps)?

### **Common Error Messages & Fixes**

**Error: `search_replace error: old_string not found`**
```
Fix:
1. Read the file again: read_file("path/to/file")
2. Copy EXACT text from output (check spaces, tabs, quotes)
3. Include more context (3-5 lines before/after)
4. Try again with exact match
```

**Error: `No shell found with ID: XX`**
```
Fix:
1. Stop referencing old shell sessions
2. Run new command with full context
3. Use absolute paths: /Users/nguyennm/Project/agenthub/...
4. Include cd in same command: cd /path && command
```

**Error: `File not found` when editing**
```
Fix:
1. File doesn't exist yet - use `write()` instead of `search_replace()`
2. Check path with: list_dir("directory/")
3. Verify file location with: glob_file_search("filename.py")
```

---

## 🧠 Decision-Making Framework

### **When to Use Each Tool (Decision Tree)**

```
START: Received user request
  ↓
Q: Do I understand the existing codebase structure?
  NO → Use codebase_search to explore
  YES → Continue
  ↓
Q: Do I know exact file/function locations?
  NO → Use grep or codebase_search
  YES → Continue
  ↓
Q: Am I using unfamiliar libraries/APIs?
  YES → Use web_search for documentation
  NO → Continue
  ↓
Q: Is this a known error pattern?
  YES → Use web_search for solutions
  NO → Continue
  ↓
Q: Is this >3 steps or multiple files?
  YES → Create TODO list with todo_write
  NO → Proceed directly
  ↓
Q: Am I confident about the approach?
  NO → Explore more (search/read files)
  YES → Implement
```

### **When to Use Web Search**

**ALWAYS search for:**
- 🔍 **Library/Framework Documentation**
  - Example: "FastAPI WebSocket documentation 2024"
  - Example: "LlamaIndex document loader API reference"
  - Example: "Pydantic v2 BaseModel validation"

- 🔍 **Error Messages** (if unfamiliar)
  - Copy full error message
  - Include library name and version
  - Example: "Python asyncio TaskGroup error handling"

- 🔍 **Best Practices** (for new features)
  - Example: "Python async best practices 2024"
  - Example: "FastAPI WebSocket authentication patterns"
  - Example: "LlamaIndex RAG optimization techniques"

- 🔍 **API Compatibility** (version changes)
  - Example: "Pydantic v2 breaking changes from v1"
  - Example: "FastAPI 0.100 new features"

- 🔍 **Security Concerns**
  - Example: "secure WebSocket authentication patterns"
  - Example: "Python API key storage best practices"

**Search Query Patterns:**

✅ **Good queries** (specific, actionable):
- "Python asyncio TaskGroup error handling"
- "LlamaIndex local embeddings configuration"
- "FastAPI WebSocket disconnect handling"
- "Pydantic BaseModel custom validator examples"

❌ **Bad queries** (too vague):
- "Python error"
- "How to use FastAPI"
- "Fix bug"

**Technology Context for This Project:**
- Python 3.11+
- FastAPI (web framework)
- Pydantic v2 (data validation - NOT v1!)
- LlamaIndex (RAG)
- UV package manager (NOT pip!)
- MCP (Model Context Protocol)
- WebSockets (real-time communication)

**Always include version/year in searches:**
- "FastAPI WebSocket 2024" (not just "FastAPI WebSocket")
- "Pydantic v2 validators" (not just "Pydantic validators")

### **When to Proceed Autonomously**

**Proceed WITHOUT asking if:**
- ✅ Task follows established patterns in codebase
- ✅ Requirements are clear from context
- ✅ Standard library usage (no external docs needed)
- ✅ Simple CRUD operations
- ✅ Following existing test patterns
- ✅ Adding docstrings/comments
- ✅ Fixing linter errors
- ✅ Simple refactoring (rename, extract function)

**ALWAYS ask if:**
- ❌ Ambiguous requirements (multiple valid interpretations)
- ❌ Potential breaking changes to public APIs
- ❌ Security-sensitive decisions
- ❌ Major architectural changes
- ❌ Unclear which approach user prefers

### **When to Plan vs. Process Directly**

**PROCESS DIRECTLY (no TODO needed):**
- ✅ Single file edit with clear location
- ✅ Reading/exploring codebase
- ✅ Running existing tests
- ✅ Adding a single function to existing file
- ✅ Fixing specific linter errors
- ✅ Simple grep/search operations
- ✅ Adding docstrings or type hints

**CREATE TODO LIST FIRST:**
- ❌ Task involves 3+ files
- ❌ Multiple logical steps required
- ❌ Creating new feature/module from scratch
- ❌ Refactoring across multiple locations
- ❌ User provides multiple requirements
- ❌ Need to explore codebase first
- ❌ Complex integration work

**Confidence Decision Matrix:**

| Situation | Confidence | Action |
|-----------|------------|--------|
| Know exact file & change | HIGH | Direct edit |
| Know file, unsure of content | MEDIUM | Read first, then edit |
| Don't know file location | LOW | Search, then read, then edit |
| Unfamiliar library/API | LOW | Web search, then implement |
| 3+ files to change | N/A | Create TODO list |
| Known pattern in codebase | HIGH | Follow pattern directly |
| Novel architecture decision | LOW | Explore, plan, then implement |

---

## 🤖 LLM Reasoning Protocol

### **Before Taking Action - Mental Checklist**

**Use this reasoning pattern for moderate LLMs:**

1. **Understand**: What is the user asking for?
   - Paraphrase the request to yourself
   - Identify the main goal and sub-goals
   - Example: "User wants to add local embeddings to RAG config"

2. **Explore**: What exists already?
   - Search codebase for similar implementations
   - Check for existing patterns and conventions
   - Example: "Search for embedding configuration patterns"

3. **Research**: What do I need to learn?
   - Identify unfamiliar concepts/libraries
   - Web search for documentation and best practices
   - Example: "Search for 'LlamaIndex local embeddings setup'"

4. **Plan**: How will I implement this?
   - Break into steps (use TODO if >3 steps)
   - Identify files to modify/create
   - Consider edge cases
   - Example: "1) Read config.py, 2) Update embedding setting, 3) Test"

5. **Implement**: Write the code
   - Follow existing patterns
   - Write tests alongside code
   - Verify each step before continuing

6. **Verify**: Does it work?
   - Run tests
   - Check linter
   - Test integration

### **Self-Correction Pattern**

If something fails:
1. **Read error message carefully**
2. **Check assumptions**: Did I read the file? Is path correct?
3. **Web search** the error if unfamiliar
4. **Check similar working code** in codebase
5. **Try fix** with corrected approach
6. If still fails after 2 attempts: **Explain issue to user**

❌ **NEVER**: Retry same approach 3+ times without changing strategy

### **Self-Narration for Complex Tasks**

For complex tasks, narrate your plan before executing:

**Example:**
```
"I need to update config.py to use local embeddings.
Let me think through this:
1. First, I'll read config.py to see current structure
2. Then I'll search for local embedding configuration in docs
3. Then I'll copy the exact line for embedding_model
4. Then I'll do search_replace with exact match
5. Finally, I'll verify the change and run tests

Now executing step 1..."
```

This helps catch errors before they happen.

---

## 🚀 Development Workflow

### **Standard Development Process**

**For Every Task:**

1. **Understand**
   - Read requirements carefully
   - Clarify ambiguities before starting
   - Identify success criteria

2. **Explore**
   - Use `codebase_search` for concepts: "How does authentication work?"
   - Use `grep` for exact text: Find "class RAGConfig"
   - Read relevant files to understand patterns

3. **Plan** (if complex)
   - Break into steps
   - Create TODO list if >3 steps
   - Identify files to modify

4. **Implement**
   - Follow existing patterns (don't reinvent)
   - Write small, focused changes
   - Read files before editing (MANDATORY)
   - Test after each change

5. **Verify**
   - Run tests (write if don't exist)
   - Check linter: `ruff check <files>`
   - Verify integration works
   - Clean up temporary files

### **Core Development Principles**

- **KISS**: Keep it simple. Avoid over-engineering
- **YAGNI**: Build only what's needed now, not for hypothetical futures
- **Incremental validation**: Write → Test → Fix → Continue (don't write everything then test)
- **Modify, don't create**: Always modify existing files. Create new files ONLY for new components
- **Test-first**: Write tests immediately after writing functions
- **Autonomous**: Make reasonable assumptions, proceed independently
- **Pattern matching**: Follow existing codebase patterns
- **Git is backup**: Trust version control, not manual backups or temp files

### **Workspace Rules Integration**

This project follows strict workspace rules:

#### **1. Incremental Modification Principle**
- ✅ Modify existing files, don't rewrite from scratch
- ✅ Preserve existing functionality while improving
- ✅ Document what changed and why
- ❌ Don't create "new_version" or "backup" files

#### **2. Autonomous Implementation Principle**
- ✅ Make reasonable assumptions based on codebase patterns
- ✅ Proceed independently unless truly unclear
- ✅ Document assumptions in code comments
- ❌ Don't ask for every implementation detail

#### **3. Test-First Development Principle**
- ✅ Write tests IMMEDIATELY after writing functions
- ✅ All tests must pass before continuing
- ✅ Aim for 80%+ test coverage
- ❌ Never skip testing "for now"

#### **4. Criteria-Based Completion Principle**
- ✅ Define acceptance criteria at start
- ✅ Mark complete only when all criteria met
- ✅ Use checklists to validate completion
- ❌ Don't over-engineer beyond requirements

#### **5. RAG Implementation Principle** (Project-Specific)
- ✅ Use mock data first for testing
- ✅ Implement real retrieval with LlamaIndex after validation
- ✅ Document the transition from mock to real

#### **6. Code Quality Standards**
- ✅ Follow PEP 8 (Python style guide)
- ✅ Use meaningful variable/function names
- ✅ Add appropriate comments and documentation
- ✅ Keep functions focused and single-purpose
- ✅ Handle errors gracefully with proper exception handling

#### **7. Security Principle**
- ✅ Validate and sanitize all inputs
- ✅ Use parameterized queries to prevent injection
- ✅ Implement proper authentication/authorization
- ✅ Follow principle of least privilege
- ✅ Keep dependencies updated

---

## 📝 File Creation vs Modification Philosophy

### **CRITICAL: Don't Create Unnecessary Files**

**Core Principle**: Git is your version control. Modify existing files directly. Create new files ONLY when architecturally necessary.

### **The Problem with File Proliferation**

❌ **BAD Practice** (file chaos):
```
repo/
├── embeddings.py
├── embeddings_v2.py
├── embeddings_new.py
├── embeddings_backup.py
├── temp_test_embeddings.py
├── embeddings_working.py
└── embeddings_final.py  # Which one is real?!
```

✅ **GOOD Practice** (single source of truth):
```
repo/
├── embeddings.py  # One source of truth
└── (git history has all versions)
```

### **Wrong vs Right Approach**

#### **❌ WRONG: Create Temp Files for Testing**

```
User: "Fix the embedding calculation bug"

AI Approach (WRONG):
1. Create temp_embedding_test.py
2. Copy code to temp file
3. Try fix in temp file
4. Test in temp file
5. If works, copy back to embeddings.py
6. Delete temp_embedding_test.py

Problems:
- Wastes time with extra steps
- Creates file clutter
- Extra cleanup needed
- Doesn't test in real context
- Risk of forgetting to delete temp file
```

#### **✅ RIGHT: Modify Existing Files Directly**

```
User: "Fix the embedding calculation bug"

AI Approach (RIGHT):
1. Read embeddings.py
2. Understand the bug
3. Apply fix directly to embeddings.py
4. Test with real script
5. If fails, modify embeddings.py again (iterate)
6. Continue until working

Benefits:
- Direct and efficient
- Tests in real context
- Git tracks all changes
- No cleanup needed
- Maintains code quality throughout
```

### **When to CREATE New Files**

**CREATE new file ONLY when:**

✅ **New architectural component needed**
- Example: Adding new tool → `agenthub/builtin/tools/sentiment_analysis/tool.py`
- Example: New service layer → `agenthub/core/services/cache_service.py`
- Reason: Extends architecture with new functionality

✅ **New test suite required**
- Example: Testing new feature → `tests/phase3/test_websocket_auth.py`
- Reason: Tests new functionality

✅ **New example to demonstrate feature**
- Example: `examples/tools/sentiment_analysis_example.py`
- Reason: Documents how to use new feature

✅ **Configuration or data file needed**
- Example: `config/production_settings.yaml`
- Example: `data/mock_documents.json`
- Reason: Separate data from code

✅ **New module in existing package**
- Example: `agenthub/core/tools/validators.py` (if validators don't exist)
- Reason: Logical separation of concerns

### **When to MODIFY Existing Files**

**MODIFY existing file when:**

✅ **Fixing bugs** - Always modify the buggy file directly
✅ **Refactoring code** - Improve existing code in place
✅ **Adding functions to existing module** - Extend current file
✅ **Updating configuration** - Change existing config
✅ **Improving existing feature** - Enhance what's there
✅ **Experimenting with approaches** - Try directly, git has your back
✅ **Optimizing performance** - Improve existing implementation
✅ **Updating dependencies** - Modify requirements.txt
✅ **Adding type hints** - Annotate existing code
✅ **Adding docstrings** - Document existing code

### **Code Modification Best Practices**

When modifying existing files, maintain quality:

#### **1. Preserve Architecture**
```python
# ❌ BAD: File has classes, you add loose functions
class EmbeddingManager:
    def calculate(self): ...

# Don't add this:
def calculate_embedding():  # Breaks pattern!
    pass

# ✅ GOOD: Follow existing pattern
class EmbeddingManager:
    def calculate(self): ...

    def calculate_batch(self):  # Consistent with class structure
        pass
```

#### **2. Maintain Code Quality**
```python
# ❌ BAD: Existing code has type hints, you don't add them
def existing_function(x: int) -> str:
    return str(x)

def your_new_function(x):  # Missing types!
    return str(x)

# ✅ GOOD: Match existing quality standards
def existing_function(x: int) -> str:
    return str(x)

def your_new_function(x: int) -> str:  # Consistent!
    return str(x)
```

#### **3. Follow Existing Patterns**
```python
# If file uses:
# - Dataclasses → Use dataclasses
# - Pydantic models → Use Pydantic
# - Type hints → Add type hints
# - Docstrings → Add docstrings
# - Error handling → Handle errors same way
```

#### **4. Keep Similar Functions Together**
```python
# ✅ GOOD: Group related functionality
class DocumentStore:
    # Indexing methods
    def index_document(self): ...
    def index_batch(self): ...
    def reindex(self): ...

    # Retrieval methods
    def search(self): ...
    def get_by_id(self): ...
    def get_similar(self): ...
```

#### **5. Use Git for Safety, Not Manual Backups**
```bash
# ❌ WRONG: Manual backups
cp embeddings.py embeddings_backup.py
# ... make changes to embeddings.py

# ✅ RIGHT: Git tracks everything
# Just modify embeddings.py
# Git history has all versions
# Can revert anytime: git checkout HEAD -- embeddings.py
```

### **Incremental Modification Workflow**

**For ANY modification:**

1. **Read the file first**
   ```python
   read_file("module.py")
   ```

2. **Understand the structure**
   - What patterns does it use?
   - What's the code style?
   - How is it organized?

3. **Make small, focused changes**
   - Change 5-20 lines at a time
   - Test after each change
   - Don't rewrite entire functions

4. **Preserve existing functionality**
   - Don't break working code
   - Add, don't replace (unless fixing bugs)
   - Test that old features still work

5. **Maintain consistency**
   - Match naming conventions
   - Follow existing patterns
   - Keep same style

### **Examples: Real Scenarios**

#### **Scenario 1: Adding New Feature**
```
Task: "Add support for custom embedding models"

❌ WRONG:
- Create custom_embeddings.py
- Duplicate code from embeddings.py
- Implement feature in new file

✅ RIGHT:
- Read agenthub/builtin/tools/rag/embeddings.py
- Add custom model support to existing EmbeddingManager class
- Extend existing patterns
- Update existing configuration
```

#### **Scenario 2: Fixing Bug**
```
Task: "Fix the RAG search returning empty results"

❌ WRONG:
- Create test_rag_search.py to experiment
- Try fixes in test file
- Copy working version to real file

✅ RIGHT:
- Read agenthub/builtin/tools/rag/rag_tool.py
- Identify bug in search_documents method
- Fix directly in rag_tool.py
- Test with examples/builtin_tools/rag_simple_example.py
- Iterate until fixed
```

#### **Scenario 3: Refactoring**
```
Task: "Extract common validation logic"

❌ WRONG:
- Create validators_new.py
- Move logic to new file
- Keep old file around "just in case"

✅ RIGHT:
- If validators.py exists → modify it
- If doesn't exist → create validators.py (new component)
- Update imports in existing files
- Delete old validation code
- Test all affected modules
```

### **Anti-Patterns to Avoid**

❌ **Never create:**
- `old_*.py` or `*_old.py`
- `backup_*.py` or `*_backup.py`
- `temp_*.py` or `*_temp.py` (unless truly temporary and deleted within same session)
- `new_*.py` or `*_new.py`
- `*_v2.py`, `*_v3.py`, etc.
- `*_working.py`, `*_test.py` (for experiments)
- `*_final.py`, `*_really_final.py`

✅ **Instead:**
- Modify the original file
- Commit frequently to git
- Use git branches for experiments
- Trust version control

### **Exception: Temporary Verification Scripts (With STRICT Rules)**

**Sometimes you need a quick script to verify an assumption or test something:**

✅ **Acceptable temporary files:**
- Quick scripts to verify assumptions (e.g., "Does this API return JSON?")
- One-off data exploration (e.g., "What dimension are these embeddings?")
- Debugging scripts (e.g., "Why is this value wrong?")

⚠️ **BUT with MANDATORY rules:**

1. **Must be deleted IMMEDIATELY after use** (same session, within minutes)
2. **Name clearly as temporary**: `verify_*.py`, `test_assumption_*.py`, `debug_*.py`
3. **NEVER commit to git** (even by accident)
4. **Keep tiny** (< 50 lines - if bigger, it's not temporary)
5. **Delete before marking task complete**

#### **Example: Temporary Verification Script Lifecycle**

✅ **CORRECT Workflow:**
```
Task: "Fix embedding dimension mismatch"

1. Create verification script:
   File: verify_dimensions.py
   ---
   from agenthub.builtin.tools.rag import EmbeddingManager

   manager = EmbeddingManager()
   print(f"Model dimension: {manager.get_dimension()}")
   print(f"Config dimension: {config.embedding_dim}")
   ---

2. Run it immediately:
   $ python verify_dimensions.py
   Output: Model dimension: 384
           Config dimension: 1536
   Result: MISMATCH CONFIRMED!

3. Got the answer → DELETE IMMEDIATELY:
   $ rm verify_dimensions.py

4. Apply fix to actual code:
   Read agenthub/builtin/tools/rag/config.py
   Fix: embedding_dim = 384

5. Test with proper unit tests:
   $ pytest tests/test_rag.py -v

6. Verify cleanup:
   $ git status
   Should NOT show verify_dimensions.py ✅

Result:
- Assumption verified ✅
- Fix applied ✅
- Temporary file deleted ✅
- Workspace clean ✅
```

❌ **WRONG Workflow:**
```
Task: "Fix embedding dimension mismatch"

1. Create test_dimensions.py
2. Run it, find the issue
3. Fix the actual code
4. Leave test_dimensions.py in workspace ❌
5. Mark task complete
6. Commit includes test_dimensions.py ❌

Result:
- Codebase cluttered with orphan scripts ❌
- Confusion for other developers ❌
- Not done by definition of done ❌
```

#### **Verification Scripts vs Implementation Files**

**Key distinction:**

| Purpose | File Type | Lifetime | Example |
|---------|-----------|----------|---------|
| Verify assumption | Temporary script | Minutes | `verify_api_format.py` |
| Test implementation | Unit test (keep!) | Permanent | `tests/test_api.py` |
| Try new approach | Modify real file | N/A | Edit `api_handler.py` directly |
| Debug issue | Temporary script | Minutes | `debug_indexing.py` |

#### **Safety Net: .gitignore (But Still Delete!)**

**Add to `.gitignore` as safety net:**
```gitignore
# Temporary verification scripts (BUT STILL DELETE THEM!)
verify_*.py
test_assumption_*.py
debug_*.py
temp_*.py
```

⚠️ **IMPORTANT**:
- `.gitignore` prevents accidental commits
- **BUT you must still DELETE the files**
- `.gitignore` is a safety net, NOT permission to leave files
- Check `git status` should show clean workspace

**Think of it like this:**
- `.gitignore` = seatbelt (prevents accidents)
- Deleting files = driving safely (your responsibility)
- You need BOTH!

### **Summary: The One-File Principle**

> **"One feature, one file. One fix, one file. Git remembers, you don't need backups. Temporary scripts live minutes, not forever."**

- 📝 **Modify existing code directly** (don't create temp implementations)
- ✅ **Temporary verification scripts OK** (but delete within minutes)
- 🗑️ **Delete all temporary files immediately** (don't leave for "later")
- 🔒 **Trust git for version control** (not manual backups)
- 🎯 **Create new files only for new components** (architectural decisions)
- 🧹 **Keep workspace clean** (git status should be clean)
- 🛡️ **Use .gitignore as safety net** (but still delete files!)

---

## ✅ Quality Assurance Checklist

### **After Every Code Change**

1. **Immediate Verification**
   ```bash
   # Run linter
   ruff check <modified_files>

   # Type check
   mypy <modified_files>
   ```

2. **Test Execution**
   - Write unit test IMMEDIATELY after writing function
   - Run test: `pytest tests/path/to/test_file.py -v`
   - ❌ ALL tests must pass before continuing

3. **Integration Check**
   - Does it work with existing code?
   - Are there import errors?
   - Run related example if exists

4. **Code Review (Self)**
   - Are variable names clear?
   - Is code self-documenting?
   - Are there comments for non-obvious logic?
   - Are type hints complete?

5. **Cleanup (MANDATORY)**
   - Delete ALL temporary verification scripts (verify_*.py, test_*.py, debug_*.py, temp_*.py)
   - Remove debug print statements
   - Remove commented-out code
   - Check workspace: `git status` should be clean
   - No orphan scripts left behind

### **Definition of "Done"**

A task is complete ONLY when:
- ✅ Code written and working
- ✅ Unit tests written and passing (in `tests/` directory)
- ✅ No linter errors (`ruff check` passes)
- ✅ Type hints added (where appropriate)
- ✅ Docstrings added (for public APIs)
- ✅ Related example updated (if applicable)
- ✅ **ALL temporary verification scripts DELETED** (verify_*.py, test_*.py, debug_*.py)
- ✅ **Git status clean** - no unintended files
- ✅ Integration verified

❌ **NOT done if**:
- Tests failing
- Linter errors present
- No documentation for public APIs
- **Temporary files still exist** (verify_*.py, debug_*.py, etc.)
- **Git status shows untracked files** (check with `git status`)
- Workspace not clean

**Before marking done, ALWAYS run:**
```bash
git status
# Should NOT show any temporary scripts
# Should NOT show unintended files
```

### **Post-Action Validation**

**After every file edit:**
```python
# 1. Verify edit worked
read_file("edited_file.py", offset=X, limit=10)  # Check changed lines

# 2. Check for syntax errors
run_terminal_cmd("python -m py_compile edited_file.py")

# 3. Run related tests if exist
run_terminal_cmd("cd /Users/nguyennm/Project/agenthub && pytest tests/test_related.py -v")
```

**After shell commands:**
- Check exit status (success/error)
- Verify expected output appears
- Don't assume success without verification

---

## 🔧 Bug Fixing Protocol

### **Iterative Bug Fix Loop**

Fixing bugs requires an iterative, test-driven approach. NEVER fix once and assume it works.

### **The Bug Fix Workflow**

```
1. UNDERSTAND the bug
   ↓
2. PLANNING (if needed)
   ↓
3. APPLY the fix
   ↓
4. TEST by running appropriate script
   ↓
5. EVALUATE results
   ↓
6. If problem persists → ANALYZE what went wrong
   ↓
7. LOOP back to step 3 with new approach
   ↓
8. Continue until bug is FIXED and VERIFIED
```

### **Step-by-Step Bug Fixing Process**

#### **Step 1: Understand the Bug**

**Actions:**
- Read error message and full stack trace carefully
- Reproduce the bug consistently (must be reproducible)
- Identify the root cause, not just symptoms
- Web search the error if unfamiliar

**Questions to ask:**
- What is the expected behavior?
- What is the actual behavior?
- When does it fail? (always, sometimes, specific conditions?)
- What changed recently that might have caused this?

**Example:**
```
Bug Report: "RAG search returns empty results"

Understanding:
- Expected: Return relevant documents
- Actual: Returns empty list
- When: Always fails with new documents
- Recent change: Updated embedding model
- Root cause: Likely embedding dimension mismatch
```

#### **Step 2: Planning (If Needed)**

**Simple bug** (1 file, clear fix):
- ✅ No planning needed, proceed directly to fix

**Complex bug** (multiple files, unclear cause):
- ❌ Create TODO list to track investigation
- Break into investigation steps
- List files that might need changes

**Example of when to plan:**
```
Simple: "Typo in variable name" → No planning, fix directly
Complex: "Authentication fails intermittently" → Plan investigation
```

#### **Step 3: Apply the Fix**

**MANDATORY Rules:**
- Read the file first (don't guess)
- Make targeted change (don't rewrite everything)
- Change only what's needed to fix the bug
- Don't change unrelated code ("while I'm here" syndrome)
- Add comments explaining the fix if non-obvious

**Example:**
```python
# Read first
read_file("agenthub/builtin/tools/rag/embeddings.py")

# Apply targeted fix
search_replace(
    file_path="agenthub/builtin/tools/rag/embeddings.py",
    old_string="    embedding_dim = 1536  # Old dimension",
    new_string="    embedding_dim = 384  # Fixed for local model"
)
```

#### **Step 4: Test the Fix (MANDATORY - Never Skip)**

**You MUST test every fix. No exceptions.**

**Testing strategy:**
1. **Run the specific test/script that revealed the bug**
   ```bash
   # If bug found in example
   cd /Users/nguyennm/Project/agenthub && python examples/builtin_tools/rag_simple_example.py
   ```

2. **Run related unit tests**
   ```bash
   cd /Users/nguyennm/Project/agenthub && pytest tests/phase2.5_tool_injection/test_rag.py -v
   ```

3. **Verify fix doesn't break other functionality**
   ```bash
   # Run broader test suite
   cd /Users/nguyennm/Project/agenthub && pytest tests/phase2.5_tool_injection/ -v
   ```

**What to test:**
- ✅ Original bug is fixed
- ✅ No new errors introduced
- ✅ Related functionality still works
- ✅ Edge cases handled

#### **Step 5: Evaluate Results**

**Three possible outcomes:**

✅ **Bug fixed completely**
- All tests pass
- Original issue resolved
- No new issues introduced
→ Mark complete, clean up, move on

⚠️ **Bug persists (same error)**
- Fix didn't work
- Wrong approach or incomplete fix
→ Continue to Step 6

❌ **New bug appeared (different error)**
- Fix broke something else
- Need different approach
→ Continue to Step 6

#### **Step 6: Analyze & Iterate**

**If fix didn't work, ask:**
- Was my assumption about the root cause wrong?
- Did I fix the symptom instead of the cause?
- Is there a deeper issue I missed?
- Do I need to web search for more information?

**Decision tree:**
```
Bug still exists?
  ↓
Q: Same error as before?
  YES → Approach was wrong, try different fix
  NO → Created new bug, need to revert or adjust
  ↓
Q: Have I tried 2+ different approaches?
  YES → Web search for solutions or similar issues
  NO → Try alternative approach
  ↓
Q: Still stuck after 3+ attempts?
  YES → Explain situation to user, ask for guidance
  NO → Loop back to Step 3 with new approach
```

**Example iteration:**
```
Attempt 1: Changed embedding dimension → Still empty results
Analysis: Dimension was correct, issue is elsewhere

Attempt 2: Check if documents are indexed → Found they're not
Analysis: Indexing step is failing silently

Attempt 3: Add error logging to indexing → See actual error
Fix: Add try-catch and handle edge case

Test: Now works! ✅
```

#### **Step 7: Loop Back**

**When to iterate:**
- Bug not fixed → Try different approach (Step 3)
- New bug created → Revert or adjust fix (Step 3)
- Partial fix → Complete the fix (Step 3)

**When to stop:**
- ✅ Bug is fixed
- ✅ All tests pass
- ✅ No new issues introduced
- ✅ Verified with appropriate tests

### **Bug Fix Anti-Patterns**

#### **❌ ANTI-PATTERN 1: Fix and Forget**

```
WRONG Approach:
1. Apply fix
2. "I think this should work"
3. Mark as complete
4. Move on

Problem: No verification, bug might still exist
```

✅ **RIGHT Approach:**
```
1. Apply fix
2. Test immediately
3. Verify bug is fixed
4. Run related tests
5. Then mark complete
```

#### **❌ ANTI-PATTERN 2: Retry Same Approach**

```
WRONG Approach:
Attempt 1: Try fix A → Fails
Attempt 2: Try fix A slightly modified → Fails
Attempt 3: Try fix A with minor change → Fails
Attempt 4: Try fix A again... → Still fails!

Problem: Insanity - doing same thing expecting different result
```

✅ **RIGHT Approach:**
```
Attempt 1: Try fix A → Fails
Analysis: Why didn't it work? What assumption was wrong?
Attempt 2: Try completely different fix B → Fails
Analysis: Web search for similar issues
Attempt 3: Try approach C based on research → Works! ✅
```

#### **❌ ANTI-PATTERN 3: Fix Everything at Once**

```
WRONG Approach:
1. See bug in module A
2. "While I'm here, let me also refactor B, optimize C, update D..."
3. Change 500 lines
4. Something breaks
5. Can't tell what caused the break

Problem: Mixed concerns, hard to debug
```

✅ **RIGHT Approach:**
```
1. See bug in module A
2. Fix ONLY the bug in A
3. Test the fix
4. Verify it works
5. THEN (if needed) do other improvements separately
```

### **Iteration Limits & Getting Help**

**Set reasonable limits:**

- **After 3 failed attempts with different approaches:**
  - Web search for the error message
  - Look for similar issues in project history
  - Check if it's a known issue

- **After 5 attempts total:**
  - Explain the situation clearly to user
  - Describe what you've tried
  - Ask for guidance or clarification
  - Don't keep trying blindly

**Example of asking for help:**
```
"I've attempted to fix the RAG empty results bug with 5 different approaches:

1. Changed embedding dimensions (384, 1536) - still empty
2. Verified documents are indexed - they are indexed
3. Added logging to search - query embedding is generated correctly
4. Checked vector store - vectors exist but search returns nothing
5. Tried different similarity metrics - no improvement

The issue seems to be in the similarity search step, but I can't identify
why valid vectors aren't matching. Could you provide more context about
how the vector store is configured or any recent changes to the search logic?"
```

### **Testing Specificity**

**Be specific about which tests to run:**

#### **Unit Tests:**
```bash
# Test specific function
cd /Users/nguyennm/Project/agenthub && pytest tests/phase2.5_tool_injection/test_rag.py::test_search_documents -v

# Test specific module
cd /Users/nguyennm/Project/agenthub && pytest tests/phase2.5_tool_injection/test_rag.py -v
```

#### **Integration Tests:**
```bash
# Run example that demonstrates the feature
cd /Users/nguyennm/Project/agenthub && python examples/builtin_tools/rag_simple_example.py

# Run client test
cd /Users/nguyennm/Project/agenthub && python examples/clients/rag_client.py
```

#### **Manual Verification:**
```python
# Quick verification script
from agenthub.builtin.tools.rag import create_rag_tool, RAGConfig

config = RAGConfig(source_directory="./sample_docs")
rag = create_rag_tool(config=config)

# Test the specific bug
results = rag.search_documents("test query", max_results=5)
print(f"Results: {len(results)}")  # Should not be 0
```

### **Bug Fix Success Checklist**

**A bug is FIXED when:**
- [ ] Original bug no longer occurs
- [ ] Test that revealed bug now passes
- [ ] Related unit tests pass
- [ ] No new bugs introduced
- [ ] Edge cases considered and handled
- [ ] Fix is minimal and targeted
- [ ] Code quality maintained
- [ ] Comments added if fix is non-obvious

**NOT fixed if:**
- ❌ "It should work but didn't test"
- ❌ "Fixed one case but others still fail"
- ❌ "Fixed bug but broke something else"
- ❌ "Can't reproduce anymore" (without understanding why)

### **Example: Complete Bug Fix**

```
Bug Report: "RAG search returns empty results for new documents"

1. UNDERSTAND:
   - Read error logs
   - Reproduce: Add document, search → empty results
   - Root cause investigation needed

2. PLANNING:
   - Multi-step investigation needed
   - TODO: Check indexing, embeddings, search logic

3. APPLY FIX (Iteration 1):
   - Hypothesis: Documents not indexed
   - Added logging to see index contents

4. TEST:
   - Run: python examples/builtin_tools/rag_simple_example.py
   - Result: Documents ARE indexed

5. EVALUATE:
   - Bug persists, hypothesis wrong

6. ANALYZE:
   - Documents indexed but not returned
   - Might be similarity threshold too high

7. LOOP - APPLY FIX (Iteration 2):
   - Lowered similarity threshold from 0.8 to 0.5

8. TEST:
   - Run: python examples/builtin_tools/rag_simple_example.py
   - Result: NOW RETURNS RESULTS! ✅

9. VERIFY:
   - Run: pytest tests/phase2.5_tool_injection/test_rag.py -v
   - All tests pass ✅
   - Check examples still work ✅

10. COMPLETE:
    - Bug fixed
    - Tests pass
    - No new issues
    - Mark done ✅
```

### **Summary: The Bug Fixing Mindset**

> **"Fix → Test → Verify → Iterate. Never assume, always verify."**

- 🐛 **Understand deeply** before fixing
- 🎯 **Fix specifically**, not broadly
- ✅ **Test immediately** after every change
- 🔄 **Iterate** when fix doesn't work
- 📊 **Verify** with multiple tests
- 🛑 **Stop** after reasonable attempts and ask for help
- 📝 **Document** non-obvious fixes

**Remember**: The goal is not to "write a fix", it's to "eliminate the bug" - you only know you've succeeded by testing.

---

## 📁 Project Structure

```
agenthub/
├── core/              # Core agent system
│   ├── agents/        # Agent loading, execution, lifecycle
│   ├── tools/         # Tool registry, MCP integration
│   ├── communication/ # WebSocket, inter-agent messaging
│   ├── llm/          # LLM service abstraction
│   └── knowledge/     # RAG and knowledge base
├── runtime/           # Process management, isolated execution
├── sdk/              # Public API (load_agent, solve)
├── github/           # GitHub-based agent registry
├── builtin/tools/    # Built-in tools (RAG, web_search)
├── cli/              # Command-line interface
└── storage/          # Local caching and persistence

examples/             # Usage examples and demos
tests/               # Comprehensive test suites
```

---

## 🔑 Key Architecture Patterns

### **1. Agent Loading & Execution**

```python
import agenthub as ah

# Load from GitHub
agent = ah.load_agent("namespace/agent-name")

# Universal solve method
result = agent.solve("Natural language goal")
```

**Key Files**:
- `agenthub/sdk/load_agent.py` - Main entry point
- `agenthub/core/agents/base.py` - Base agent interface
- `agenthub/runtime/agent_runtime.py` - Isolated execution

### **2. MCP Tool Integration**

Tools use the Model Context Protocol (MCP) for standardized execution.

**Key Files**:
- `agenthub/core/tools/registry.py` - Tool registration
- `agenthub/core/tools/base.py` - Tool base classes
- `agenthub/core/mcp/` - MCP server implementation

**Pattern**: Create tools with `@tool` decorator, run with `run_resources()`
```python
from agenthub.core.tools import tool, run_resources

@tool(name="my_tool", description="...")
def my_tool(param: str) -> dict:
    return {"result": param}

run_resources()  # Starts MCP server
```

### **3. Process Isolation with UV**

Each agent runs in an isolated subprocess using UV (10x faster than pip).

**Key Files**:
- `agenthub/runtime/environment_manager.py`
- `agenthub/runtime/process_manager/`

### **4. Real-time Communication**

WebSocket-based inter-agent communication and real-time updates.

**Key Files**:
- `agenthub/core/communication/server.py`
- `agenthub/core/communication/router.py`

---

## 🛠 Common Development Tasks

### **Adding New Built-in Tools**

1. Create tool in `agenthub/builtin/tools/<tool_name>/`
2. Use `@tool` decorator for functions
3. Add to `__init__.py` exports
4. Create example in `examples/builtin_tools/`
5. Write tests in `tests/phase2.5_tool_injection/`

**Example:**
```python
# agenthub/builtin/tools/my_tool/my_tool.py
from agenthub.core.tools import tool

@tool(name="my_tool", description="Does something useful")
def my_tool(input: str) -> dict:
    return {"result": f"Processed: {input}"}
```

### **Creating Examples**

- **Simple examples**: In `examples/getting_started/`
- **Tool examples**: In `examples/builtin_tools/`
- **Client examples**: In `examples/clients/`
- Keep examples minimal, focused on one concept
- Include clear comments and docstrings

**Example structure:**
```python
"""
Brief description of what this example demonstrates.
"""

# Setup
# ...

# Main logic (with comments)
# ...

# Cleanup
# ...
```

### **Writing Tests**

- Follow phase-based organization: `tests/phase{X}_*/`
- Use pytest fixtures from `conftest.py`
- Test both success and error cases
- Run with: `pytest tests/phase2.5_tool_injection/ -v`

**Test pattern:**
```python
def test_feature_success():
    """Test successful case with clear assertions."""
    result = function_under_test(valid_input)
    assert result.success
    assert result.data == expected_value

def test_feature_error():
    """Test error handling."""
    with pytest.raises(ExpectedException):
        function_under_test(invalid_input)
```

---

## ⚙️ Technical Details

### **Dependencies**

- **UV**: Fast package manager (core requirement)
- **Click**: CLI framework
- **Rich**: Terminal UI
- **Pydantic**: Data validation (v2)
- **MCP**: Model Context Protocol
- **FastAPI**: For MCP servers
- **WebSockets**: Real-time communication
- **LlamaIndex**: RAG functionality

### **Environment Variables**

```bash
AGENTHUB_DIR=/custom/path              # Installation directory
AGENTHUB_MCP_HOST=localhost           # MCP server host
AGENTHUB_MCP_PORT=8000               # MCP server port
AGENTHUB_LOG_LEVEL=DEBUG             # Logging level
AGENTHUB_SUPPRESS_HTTP=true          # Suppress HTTP logs
```

### **Code Style**

- **Formatter**: Black (line length: 88)
- **Linter**: Ruff
- **Type checking**: MyPy (strict)
- **Imports**: Organized with isort

**Run before committing:**
```bash
ruff check agenthub/
mypy agenthub/
pytest tests/ -v
```

### **CLI Commands**

```bash
# Agent management
agenthub agent install agentplug/agent-name
agenthub agent list
agenthub agent info agentplug/agent-name
agenthub agent remove agentplug/agent-name

# Execution
agenthub agent exec agentplug/agent-name method_name "parameters"
```

---

## 🎨 Built-in Tools Development

### **RAG Tool**

**Location**: `agenthub/builtin/tools/rag/`

**Key Files**:
- `rag_tool.py` - Main RAG implementation
- `document_store.py` - Document indexing and retrieval
- `config.py` - RAG configuration
- `embeddings.py` - Embedding model management

**Usage Pattern**:
```python
from agenthub.builtin.tools.rag import create_rag_tool, RAGConfig

config = RAGConfig(source_directory="./docs")
rag = create_rag_tool(config=config)
results = rag.search_documents(query_text="query", max_results=5)
```

### **Web Search Tool**

**Location**: `agenthub/builtin/tools/web_search/`

**Simple MCP Server Pattern**:
```python
from agenthub.core.tools import tool, run_resources

@tool(name="tool_name", description="...")
def tool_function(param: str) -> dict:
    # Implementation
    return {"result": param}

run_resources()  # Start MCP server
```

---

## 🐛 Error Patterns Library

### **Known Issues & Workarounds**

#### **MCP Connection Testing**
**Issue**: Connection test may fail with TaskGroup errors, but tool calls still work.

**Error message:**
```
TaskGroup error during connection test
```

**Workaround**: Return success=True from connection tests, allow tool calls to proceed.

**Example**: See `examples/clients/rag_client.py` for handling pattern.

#### **UV Environment Isolation**
**Issue**: Some packages don't install cleanly in UV environments.

**Error message:**
```
Package not found in isolated environment
```

**Workaround**:
- Add explicit dependencies to agent.yaml
- Use standard PyPI packages
- Check UV compatibility: Web search "UV Python [package_name] installation"

#### **WebSocket Connections**
**Issue**: WebSocket sessions need proper cleanup.

**Error message:**
```
WebSocket connection not closed properly
```

**Workaround**:
- Use context managers
- Explicit close() calls in teardown
- Always handle disconnect events

**Example:**
```python
async with websocket_client() as ws:
    # Use websocket
    pass
# Automatically cleaned up
```

#### **File Edit Failures**
**Issue**: old_string doesn't match file content.

**Error message:**
```
search_replace error: old_string not found
```

**Solution**:
1. Read the file first: `read_file("path")`
2. Copy EXACT text from output
3. Check whitespace (spaces vs tabs)
4. Check quotes (single vs double)
5. Include more context lines

#### **Import Errors After Adding Code**
**Issue**: New code imports don't resolve.

**Error message:**
```
ImportError: No module named 'xyz'
```

**Solution**:
1. Check if package in requirements.txt
2. Verify package installed in environment
3. Check for circular imports
4. Verify __init__.py exports

### **Error Recovery Workflow**

**When any tool fails:**
1. ❌ **Don't retry immediately** with same input
2. ✅ **Read error message** carefully
3. ✅ **Verify assumptions**:
   - File exists?
   - Path correct?
   - Exact string match?
4. ✅ **Web search error** if unfamiliar
5. ✅ **Check similar working code** in codebase
6. ✅ **Try different approach** if 2+ failures
7. ✅ **Ask user** if still stuck after 3 attempts

---

## 🔍 Debugging Tips

### **Enable Debug Logging**

```bash
export AGENTHUB_LOG_LEVEL=DEBUG
export AGENTHUB_SUPPRESS_HTTP=false
```

### **Common Issues & Solutions**

**Agent not found**
- Check GitHub URL format
- Verify agent.yaml exists in repo
- Check network connection

**Tool not registered**
- Verify `@tool` decorator is used
- Check MCP server is running
- Verify imports in __init__.py

**Import errors**
- Check UV environment: `uv pip list`
- Verify dependencies in agent.yaml or requirements.txt
- Try reinstalling: `uv pip install -r requirements.txt`

**WebSocket errors**
- Check port availability: `lsof -i :8000`
- Verify server is running
- Check firewall settings

### **Useful Debug Commands**

```python
# Check agent installation
import agenthub as ah
ah.list_installed_agents()

# Verify tool registration
from agenthub.core.tools.registry import get_tool_registry
registry = get_tool_registry()
print(registry.list_tools())

# Test MCP connection
# See examples/clients/ for client patterns
```

### **Debug Workflow**

1. **Reproduce the error** consistently
2. **Enable debug logging** (see above)
3. **Read logs carefully** - look for first error, not last
4. **Web search error message** if unfamiliar
5. **Check similar working code** in examples/
6. **Isolate the problem** - test component separately
7. **Fix and verify** - ensure fix actually works

---

## 📝 Documentation Guidelines

### **Code Documentation**

- Add docstrings to all public functions/classes
- Include type hints for all parameters and returns
- Explain **why**, not just **what**
- Document exceptions and edge cases

**Example:**
```python
def calculate_embedding(text: str, model: str = "default") -> list[float]:
    """
    Calculate embedding vector for input text.

    Uses the configured embedding model to generate a dense vector
    representation. Defaults to text-embedding-3-small if model not specified.

    Args:
        text: Input text to embed. Must be non-empty.
        model: Embedding model name. Defaults to "default".

    Returns:
        List of float values representing the embedding vector.
        Length depends on model (typically 384 or 1536).

    Raises:
        ValueError: If text is empty or model is invalid.
        ConnectionError: If embedding service is unavailable.

    Example:
        >>> embedding = calculate_embedding("Hello world")
        >>> len(embedding)
        1536
    """
```

### **Examples**

- Keep examples minimal and focused
- One concept per example file
- Include comments for key steps
- Show both basic and advanced usage
- Add error handling examples

**Example structure:**
```python
"""
Example: Using RAG tool with local embeddings

This example demonstrates:
1. Configuring RAG with local embeddings
2. Indexing documents
3. Performing similarity search
"""

from agenthub.builtin.tools.rag import create_rag_tool, RAGConfig

# 1. Configure RAG
config = RAGConfig(
    source_directory="./docs",
    embedding_model="local"
)

# 2. Create and initialize tool
rag = create_rag_tool(config=config)

# 3. Search for documents
results = rag.search_documents(
    query_text="How to install agents?",
    max_results=5
)

# 4. Process results
for result in results:
    print(f"Score: {result.score}")
    print(f"Text: {result.text}")
```

### **Comments**

- Explain non-obvious decisions
- Link to relevant issues/PRs when applicable
- Mark TODOs with context: `# TODO(username): description`
- Don't comment obvious code
- Focus on "why", not "what"

**Good comments:**
```python
# Use asyncio.TaskGroup for structured concurrency (PEP 654)
# This ensures all tasks are awaited even if one fails
async with asyncio.TaskGroup() as tg:
    tg.create_task(fetch_data())
```

**Bad comments:**
```python
# Create a loop
for i in range(10):  # Loop 10 times
    print(i)  # Print i
```

---

## 🎯 Current Focus Areas

### **Priorities**

1. **Tool ecosystem expansion** - More built-in tools
2. **Agent examples** - Showcase real-world use cases
3. **Documentation** - User guides, API docs
4. **Performance** - Optimize agent loading and execution

### **What Works Well**

✅ Agent loading and execution
✅ MCP tool integration
✅ Process isolation with UV
✅ WebSocket communication
✅ GitHub-based registry
✅ RAG and web search tools

### **What Needs Care**

⚠️ Complex multi-agent orchestration (new territory)
⚠️ Large-scale tool injection (test thoroughly)
⚠️ Cross-platform compatibility (focus on Unix first)
⚠️ Error handling edge cases (validate thoroughly)

---

## 📚 Additional Resources

- **Main README**: `/Users/nguyennm/Project/agenthub/README.md`
- **Examples**: `/Users/nguyennm/Project/agenthub/examples/`
- **Tests**: `/Users/nguyennm/Project/agenthub/tests/`
- **User Guide**: `/Users/nguyennm/Project/agenthub/docs/USER_GUIDE.md`

---

## 🤝 Contributing Guidelines

When implementing features:

1. **Follow existing patterns** in the codebase
2. **Write tests alongside code** (test-first when possible)
3. **Keep changes focused** and atomic
4. **Update examples** if adding new functionality
5. **Run linters and type checking** before completion
6. **Clean up** any temporary files or experiments
7. **Document** public APIs with docstrings
8. **Verify integration** with existing code

### **Pre-Commit Checklist**

Before marking work as complete:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linter errors: `ruff check agenthub/`
- [ ] Type checking passes: `mypy agenthub/`
- [ ] Documentation updated (if needed)
- [ ] Examples work (if modified)
- [ ] **ALL temporary verification scripts deleted** (verify_*.py, test_*.py, debug_*.py)
- [ ] **Git status clean**: Run `git status` - should show ONLY intended changes
- [ ] No orphan files, no accidental files, no test scripts

**Final verification command:**
```bash
git status

# Should show:
# - Only files you intended to modify
# - NO verify_*.py, test_*.py, debug_*.py, temp_*.py
# - Clean working directory
```

### **Code Review (Self)**

Ask yourself:
- Is this the simplest solution?
- Does it follow existing patterns?
- Are names clear and descriptive?
- Is error handling appropriate?
- Are edge cases covered?
- Would I understand this code in 6 months?

---

## 💡 Remember

**Simple, working code is better than complex, perfect code.**

### **Core Philosophy**
- Start simple, iterate based on needs
- Test early and often
- Follow existing patterns
- Document as you go
- Clean up as you work
- Ask when truly uncertain

### **Most Important Rules**

1. ⚠️ **Read files before editing** (prevents 90% of errors)
2. ⚠️ **Each shell command is new shell** (prevents shell ID errors)
3. ⚠️ **Modify, don't create temp implementations** (git is your version control)
4. ⚠️ **Delete temporary verification scripts immediately** (workspace must stay clean)
5. ⚠️ **Test after every change** (catches errors early)
6. ⚠️ **Web search unfamiliar APIs** (prevents implementation errors)
7. ⚠️ **Iterate until bug is fixed** (don't assume one fix works)
8. ⚠️ **Follow existing patterns** (maintains consistency)
9. ⚠️ **Check git status before marking done** (no orphan files)

### **Key Workflows to Follow**

- 📝 **File Philosophy**: Modify existing files, create new ones ONLY for new components
- 🔧 **Bug Fixing**: Understand → Fix → Test → Evaluate → Iterate (until verified fixed)
- ✅ **Quality**: Every change needs tests, linting, and verification
- 🧠 **Decision Making**: Explore → Research → Plan → Implement → Verify

### **When in Doubt**

- 🔍 **Can't find code?** → Use `codebase_search` or `grep`
- 🌐 **Unfamiliar library?** → Use `web_search` for documentation
- 🐛 **Bug persists after 3 tries?** → Web search error or ask user
- 📂 **Create new file?** → Ask: Is this a new architectural component?
- 🧪 **Skip testing?** → NO! Always test after changes
- 🗑️ **Keep temporary script?** → NO! Delete immediately after use
- ✅ **Task complete?** → Check `git status` is clean first

### **Success = Working Code + Tests Passing + Clean Workspace**
