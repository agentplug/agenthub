# RAG Core Refactoring Plan

## Overview
Refactor the RAG (Retrieval-Augmented Generation) core implementation to improve maintainability, testability, and performance while leveraging existing AgentHub infrastructure.

## Current State Analysis

### Issues Identified
1. **Monolithic RAGTool class** (458 lines) - handles too many concerns:
   - Configuration management
   - Document processing and caching
   - Embedding model management
   - Vector index building and storage
   - LLM operations (query rewriting, ranking)
   - Search orchestration

2. **Tight coupling**
   - Direct dependencies on file I/O
   - Global state via `Settings.embed_model`
   - Hard-coded LLM client (aisuite) with no abstraction

3. **Code quality issues**
   - Singleton pattern (`_rag_instance`)
   - Sequential embedding processing (inefficient)
   - Magic numbers (768 dimension fallback)
   - Inconsistent error handling patterns
   - Missing type hints for Paths

4. **Duplication of infrastructure**
   - Custom LLM client wrapper around aisuite (already exists in AgentHub)
   - Reinventing patterns that exist in the codebase

### Architecture Goals
- Single Responsibility Principle for all components
- Dependency injection instead of global state
- Leverage existing AgentHub services (LLM service)
- Improved performance with batch operations
- Better type safety with modern Python typing
- Comprehensive error handling
- Easy testing with mockable dependencies

## Proposed Architecture

### Module Structure

```
agenthub/builtin/tools/rag/
├── __init__.py              # Public API exports
├── config.py                # Enhanced configuration (keep existing, add improvements)
├── embeddings.py            # Embedding service (optimized RAGEmbedding extraction)
├── document_store.py        # Document loading & caching (NEW)
├── vector_index.py          # Vector index management (NEW)
└── core.py                  # Refactored RAGTool (orchestrator, ~100 lines)
```

### Component Responsibilities

#### 1. embeddings.py - EmbeddingService
**Current:** `RAGEmbedding` class embedded in core.py
**Refactored:** Standalone service with optimizations

**Responsibilities:**
- Custom embedding wrapper for UTF-8 encoding fixes
- Optimized batch processing (instead of sequential)
- Model initialization and configuration
- Error handling and fallback embeddings

**Key Improvements:**
- Replace sequential `_get_text_embeddings` with true batching
- Add configurable dimension constants
- Better logging and error recovery
- Async support for future enhancements

**Interface:**
```python
class EmbeddingService:
    def __init__(self, model_name: str, device: str = "cpu", batch_size: int = 8)
    def encode_text(self, text: str) -> List[float]
    def encode_batch(self, texts: List[str]) -> List[List[float]]
    def encode_query(self, query: str) -> List[float]
```

---

#### 2. document_store.py - DocumentStore
**Current:** Document processing in `_initialize_document_collection()` (80 lines)
**Refactored:** Dedicated document management class

**Responsibilities:**
- Scan source directories for supported file types
- Load documents using SimpleDirectoryReader
- Cache processed documents to JSON
- Validate document collections (empty, missing dirs)
- Track metadata and processing stats

**Key Improvements:**
- Clear separation of file I/O concerns
- Better validation and error messages
- Support for incremental updates (future)
- Document format registry (extensible)

**Interface:**
```python
class DocumentStore:
    def __init__(self, source_dir: Path, cache_path: Path)
    def load_documents(self, force_reload: bool = False) -> List[Document]
    def get_document_count(self) -> int
    def validate_source_directory(self) -> Tuple[bool, str]  # (is_valid, message)
    def get_supported_extensions(self) -> Set[str]
```

**Supported Formats:**
`.pdf`, `.txt`, `.docx`, `.md`, `.csv`, `.json`, `.html`, `.xml`, `.pptx`, `.xlsx`, `.xls`, `.doc`

---

#### 3. vector_index.py - VectorIndexManager
**Current:** Index building in `_build_vector_index()` (30 lines)
**Refactored:** Complete index lifecycle management

**Responsibilities:**
- Build vector indices from documents
- Load existing indices from storage
- Persist indices to disk
- Handle empty document collections
- Storage context management

**Key Improvements:**
- Clear lifecycle (build → persist → load)
- Better error handling for corrupted indices
- Separation from document processing logic
- Support for different vector stores (future)

**Interface:**
```python
class VectorIndexManager:
    def __init__(self, storage_dir: Path)
    def build_or_load(
        self,
        documents: List[Document]
    ) -> VectorStoreIndex
    def persist(self, index: VectorStoreIndex) -> None
    def index_exists(self) -> bool
    def clear_index(self) -> None
```

---

#### 4. core.py - RAGTool (Refactored Orchestrator)
**Current:** 458 lines, monolithic
**Refactored:** ~100 lines, pure orchestration

**Responsibilities:**
- Coordinate between services
- Execute search workflow
- Provide public API
- Handle high-level errors

**Key Improvements:**
- **Dependency injection** of all services
- No direct file I/O or global state
- Simple, readable orchestration logic
- Clear public API

**Interface:**
```python
class RAGTool:
    def __init__(
        self,
        config: RAGConfig,
        llm_service: CoreLLMService,  # Use existing AgentHub service!
        embedding_service: EmbeddingService,
        document_store: DocumentStore,
        vector_index_manager: VectorIndexManager
    )
    def search_documents(
        self,
        query_text: str,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]
    def get_stats(self) -> Dict[str, Any]
```

**Search Flow:**
```
1. Rewrite query (optional) → LLM service
2. Retrieve candidates → Vector index
3. Rank results → LLM service
4. Truncate and return → User
```

---

#### 5. config.py - Enhanced RAGConfig
**Current:** Basic dataclass with validation
**Refactored:** Enhanced with modern types and constants

**Key Improvements:**
- Use `Path` type for directory paths
- Extract magic numbers to constants
- Enhanced validation with custom validators
- Support for environment variables (future)
- Better default values

**New Constants:**
```python
EMBEDDING_DIMENSION_DEFAULT = 768  # For EmbeddingGemma-300m
EMBEDDING_FALLBACK_VECTOR = [0.0] * EMBEDDING_DIMENSION_DEFAULT
SUPPORTED_EXTENSIONS = {...}  # Set of supported file extensions
```

**Path Conversions:**
```python
source_directory: Path = Field(default=Path("./data"))
cache_directory: Path = Field(default=Path("./storage"))
cached_docs_path: Path = Field(default=Path("./storage/processed_documents.json"))
index_storage_location: Path = Field(default=Path("./storage"))
```

---

### Integration with AgentHub LLM Service

**Current RAG Implementation:**
- Custom aisuite wrapper in `_execute_llm_request()`
- Manual message formatting
- No shared instance management
- No fallbacks or model detection

**Refactored Implementation:**
- Use `CoreLLMService` from `agenthub.core.llm.llm_service`
- Leverage `get_shared_llm_service()` for instance reuse
- Use existing `generate()` method with system prompts
- Automatic JSON response handling
- Model detection and fallbacks built-in

**Benefits:**
- ✅ Single source of truth for LLM operations
- ✅ Consistent error handling and logging
- ✅ Shared model detection and selection
- ✅ Support for local and cloud models
- ✅ No code duplication
- ✅ Future enhancements automatically available

**Usage in RAG:**
```python
from agenthub.core.llm.llm_service import CoreLLMService, get_shared_llm_service

# In RAGTool initialization
self.llm_service = llm_service or get_shared_llm_service()

# Query rewriting
rewritten_query = self.llm_service.generate(
    input_data=query,
    system_prompt=QUERY_REWRITE_PROMPT,
    temperature=0.0
)

# Ranking
ranking_response = self.llm_service.generate(
    input_data=ranking_prompt,
    return_json=True,
    temperature=0.0
)
```

---

### Updated Module: __init__.py

**Current Issues:**
- Singleton pattern (`_rag_instance`)
- Implicit tool registration
- Global state

**Refactored:**

```python
from .config import RAGConfig
from .core import RAGTool
from .embeddings import EmbeddingService
from .document_store import DocumentStore
from .vector_index import VectorIndexManager

__all__ = [
    "RAGTool",
    "RAGConfig",
    "EmbeddingService",
    "DocumentStore",
    "VectorIndexManager",
    "create_rag_tool",  # Factory function
]


def create_rag_tool(config: RAGConfig | None = None) -> RAGTool:
    """
    Factory function to create a RAG tool instance.

    This replaces the singleton pattern with explicit instance management.
    """
    from agenthub.core.llm.llm_service import get_shared_llm_service

    config = config or RAGConfig()
    llm_service = get_shared_llm_service()

    embedding_service = EmbeddingService(
        model_name=config.embedding_model,
        device="cpu",
        batch_size=config.embedding_batch_size
    )

    document_store = DocumentStore(
        source_dir=config.source_directory,
        cache_path=config.cached_docs_path
    )

    vector_index_manager = VectorIndexManager(
        storage_dir=config.index_storage_location
    )

    return RAGTool(
        config=config,
        llm_service=llm_service,
        embedding_service=embedding_service,
        document_store=document_store,
        vector_index_manager=vector_index_manager
    )


def register_rag_tools() -> None:
    """Register RAG tools with tool registry."""
    from agenthub.core.tools import tool

    @tool(
        "rag_search",
        "Search documents using RAG (Retrieval-Augmented Generation)"
    )
    def rag_search_tool(
        query: str,
        max_results: int = 5,
        source_directory: str = "./data",
    ) -> dict:
        """Search documents using RAG."""
        from .config import RAGConfig

        config = RAGConfig(source_directory=source_directory)
        rag = create_rag_tool(config=config)

        return rag.search_documents(query=query, max_results=max_results)

    @tool("rag_stats", "Get RAG tool statistics")
    def rag_stats_tool() -> dict:
        """Get RAG tool statistics."""
        rag = create_rag_tool()
        return rag.get_stats()
```

**Key Changes:**
- Remove singleton pattern
- Factory function with explicit dependency injection
- Each tool call creates fresh instance (stateless)
- Clear lifecycle management

---

## Implementation Benefits

### 1. Maintainability
- **Smaller modules**: Average 80-120 lines per module
- **Single responsibility**: Each class has one clear purpose
- **Clear dependencies**: Explicit in constructors
- **Readable code**: Easy to understand and modify

### 2. Testability
```python
# Easy to mock dependencies
rag = RAGTool(
    config=mock_config,
    llm_service=mock_llm_service,  # Mock LLM
    embedding_service=mock_embedding_service,  # Mock embeddings
    document_store=mock_document_store,  # Mock documents
    vector_index_manager=mock_vector_index_manager  # Mock index
)

# Test components in isolation
def test_embedding_service():
    service = EmbeddingService(model_name="test-model")
    result = service.encode_text("test")
    assert len(result) == EMBEDDING_DIMENSION_DEFAULT

# Integration tests
def test_rag_search_flow():
    # Test full search pipeline
    pass
```

### 3. Performance Improvements
- **Batch embedding processing**: 5-10x faster than sequential
- **Reused LLM service**: No duplicate model detection
- **Optimized caching**: Better cache invalidation (future)

### 4. Flexibility
- Easy to swap implementations:
  - Different vector stores (Pinecone, Weaviate)
  - Different embedding models
  - Different document loaders
- Plugin architecture for new document formats
- Support for incremental updates

### 5. Code Quality
- **Type safety**: MyPy-compatible throughout
- **No global state**: Pure dependency injection
- **Consistent patterns**: Aligns with AgentHub standards
- **Better error handling**: Specific exceptions, clear messages
- **No code duplication**: Reuses existing services

---

## Migration Path

### Phase 1: Core Services Extraction (No Breaking Changes)
1. Create `embeddings.py` - move `RAGEmbedding` class
2. Create `document_store.py` - extract document logic
3. Create `vector_index.py` - extract index logic
4. Update imports in `core.py`
5. Tests still pass ✅

### Phase 2: LLM Service Integration
1. Refactor LLM calls to use `CoreLLMService`
2. Update `_rewrite_query()` to use `llm_service.generate()`
3. Update `_apply_intelligent_ranking()` to use `llm_service.generate(return_json=True)`
4. Tests still pass ✅

### Phase 3: Dependency Injection
1. Update `RAGTool.__init__()` to accept services
2. Refactor orchestration logic
3. Keep backward compatibility with defaults
4. Tests still pass ✅

### Phase 4: Factory Function & Cleanup
1. Create `create_rag_tool()` factory
2. Update tool registration
3. Remove singleton pattern
4. Update examples and tests
5. All tests pass ✅

---

## Testing Strategy

### Component Tests
```python
# tests/phase2.5_tool_injection/core/tools/test_rag_embeddings.py
def test_embedding_encoding():
    """Test UTF-8 encoding fixes."""
    pass

def test_batch_processing():
    """Test batch embedding performance."""
    pass

# tests/phase2.5_tool_injection/core/tools/test_rag_document_store.py
def test_document_loading():
    """Test loading documents from directory."""
    pass

def test_cache_validation():
    """Test cache loading and validation."""
    pass

# tests/phase2.5_tool_injection/core/tools/test_rag_vector_index.py
def test_index_building():
    """Test vector index creation."""
    pass

def test_index_persistence():
    """Test saving and loading indices."""
    pass
```

### Integration Tests
```python
# tests/phase2.5_tool_injection/core/tools/test_rag_integration.py
def test_full_search_pipeline():
    """Test complete RAG search flow."""
    pass

def test_llm_fallback_behavior():
    """Test RAG without LLM service."""
    pass
```

### End-to-End Tests
```python
# updates to existing test file
def test_rag_search_with_query_rewriting():
    """Test search with LLM query rewriting enabled."""
    pass

def test_rag_search_without_llm():
    """Test search without LLM (vector only)."""
    pass
```

---

## Configuration Changes

### Current Configuration
```python
@dataclass
class RAGConfig:
    source_directory: str = "./data"
    cache_directory: str = "./storage"
    cached_docs_path: str = "./storage/processed_documents.json"
    index_storage_location: str = "./storage"
    embedding_model: str = "google/embeddinggemma-300m"
    use_local_embeddings: bool = True
    embedding_batch_size: int = 8
    llm_model: str = "openai:gpt-4.1"
    api_timeout_seconds: int = 20
    default_max_results: int = 5
    similarity_top_k: int = 10
    enable_query_rewriting: bool = True
```

### Enhanced Configuration
```python
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import Set

class RAGConfig(BaseModel):  # Use Pydantic for validation
    # Paths (using Path type)
    source_directory: Path = Field(default=Path("./data"))
    cache_directory: Path = Field(default=Path("./storage"))
    cached_docs_path: Path = Field(
        default=Path("./storage/processed_documents.json")
    )
    index_storage_location: Path = Field(default=Path("./storage"))

    # Embedding settings
    embedding_model: str = "google/embeddinggemma-300m"
    use_local_embeddings: bool = True
    embedding_batch_size: int = Field(default=8, ge=1, le=128)
    embedding_device: str = "cpu"  # New: explicit device selection

    # LLM settings (now optional, uses CoreLLMService defaults)
    llm_model: Optional[str] = None  # None = use CoreLLMService auto-detection
    enable_query_rewriting: bool = True
    enable_intelligent_ranking: bool = True  # New: separate toggle

    # Search settings
    default_max_results: int = Field(default=5, ge=1, le=100)
    similarity_top_k: int = Field(default=10, ge=1, le=1000)
    max_result_length: int = Field(default=2000, ge=100, le=10000)  # New

    # Advanced settings
    supported_extensions: Set[str] = Field(default_factory=set)  # New
    num_workers: int = Field(default=1, ge=1, le=8)  # New: parallel loading

    class Config:
        env_prefix = "RAG_"  # Support env var overrides

    @validator("source_directory", "cache_directory", "index_storage_location")
    def validate_directories(cls, v: Path) -> Path:
        # Ensure directories are absolute or relative to project root
        # Create if they don't exist
        pass

    def get_effective_llm_model(self) -> str:
        """Get the LLM model to use (auto-detect if not set)."""
        return self.llm_model or "auto-detect"
```

---

## Performance Optimizations

### 1. Batch Embedding Processing
**Current:** Sequential processing in `_get_text_embeddings()`
```python
def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:  # Sequential! Slow!
        embedding = self._get_text_embedding(text)
        embeddings.append(embedding)
    return embeddings
```

**Optimized:** True batch processing
```python
def encode_batch(self, texts: List[str]) -> List[List[float]]:
    # Clean all texts
    cleaned_texts = [self._clean_text(text) for text in texts]

    # Single encode call - much faster!
    embeddings = self._model.encode(
        cleaned_texts,
        convert_to_tensor=False,
        batch_size=self.batch_size
    )

    return [emb.tolist() for emb in embeddings]
```

**Expected improvement:** 5-10x faster for large document collections

### 2. Lazy Initialization
**Current:** All services initialized in `RAGTool.__init__()`

**Optimized:** Lazy loading
```python
class RAGTool:
    def __init__(...):
        self._document_store = None
        self._vector_index = None

    @property
    def document_store(self) -> DocumentStore:
        if self._document_store is None:
            self._document_store = self.document_store_loader.load()
        return self._document_store
```

### 3. Cached Vector Index
**Current:** Rebuilds index on every tool call (when using tool registration)

**Optimized:** Persistent index with cache invalidation
```python
class VectorIndexManager:
    def build_or_load(self, documents: List[Document]) -> VectorStoreIndex:
        if self._is_cache_valid(documents):
            return self._load_from_cache()
        else:
            index = self._build_index(documents)
            self._persist(index)
            return index
```

---

## API Compatibility

### Breaking Changes
Minor breaking changes for cleaner API:

1. **Configuration type:** `str` → `Path` for directory fields
2. **Initialization:** `RAGTool()` → `create_rag_tool()` (factory pattern)
3. **Tool registration:** Manual `register_rag_tools()` call required

### Migration Guide
```python
# Before
from agenthub.builtin.tools.rag import RAGTool

rag = RAGTool()
results = rag.search_documents("query")

# After
from agenthub.builtin.tools.rag import create_rag_tool

rag = create_rag_tool()
results = rag.search_documents("query")

# For custom config
from agenthub.builtin.tools.rag import RAGConfig, create_rag_tool

config = RAGConfig(source_directory="./my-docs")
rag = create_rag_tool(config=config)
```

### Backward Compatibility Layer (Optional)
```python
# In __init__.py
_rag_singleton = None

def get_rag_tool() -> RAGTool:  # Deprecated
    """Deprecated: Use create_rag_tool() instead."""
    import warnings
    warnings.warn(
        "get_rag_tool() is deprecated, use create_rag_tool() instead",
        DeprecationWarning
    )
    global _rag_singleton
    if _rag_singleton is None:
        _rag_singleton = create_rag_tool()
    return _rag_singleton
```

---

## Timeline & Effort

### Estimated Effort: 2-3 days

**Day 1:** Core service extraction
- embeddings.py (3 hours)
- document_store.py (4 hours)
- vector_index.py (3 hours)

**Day 2:** LLM service integration and orchestration
- Refactor RAGTool to use CoreLLMService (4 hours)
- Update orchestration logic (4 hours)

**Day 3:** Polish and testing
- Factory function and cleanup (2 hours)
- Update tests (4 hours)
- Documentation and examples (2 hours)

### Risk Mitigation
- ✅ All changes are internal - no external API changes initially
- ✅ Tests ensure existing functionality preserved
- ✅ Gradual migration path
- ✅ Can be done incrementally

---

## Success Criteria

### Functional
- [ ] All existing tests pass
- [ ] RAG search returns same results as before
- [ ] All document formats supported
- [ ] Query rewriting works
- [ ] Intelligent ranking works
- [ ] Statistics endpoint works

### Quality
- [ ] Code coverage > 90%
- [ ] MyPy type checking passes
- [ ] Ruff formatting and linting pass
- [ ] No code duplication

### Performance
- [ ] Embedding batch processing ~5-10x faster
- [ ] No regression in search latency
- [ ] Memory usage remains stable

### Maintainability
- [ ] Average module size < 150 lines
- [ ] Clear separation of concerns
- [ ] Comprehensive docstrings
- [ ] Example usage in docstrings

---

## Future Enhancements (Post-Refactor)

### Incremental Document Updates
```python
class DocumentStore:
    def add_document(self, path: Path) -> None
    def remove_document(self, path: Path) -> void
    def update_document(self, path: Path) -> None
```

### Multiple Vector Stores
```python
class VectorIndexManager:
    def __init__(self, storage: VectorStore)  # Pinecone, Weaviate, etc.
```

### Search Filters
```python
def search_documents(
    self,
    query: str,
    file_type: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None
) -> Dict[str, Any]
```

### Streaming Support
```python
async def search_documents_stream(
    self,
    query: str
) -> AsyncGenerator[str, None]
```

### Metadata Enrichment
```python
class DocumentStore:
    def enrich_metadata(self, document: Document) -> Document
        # Extract titles, summaries, keywords
```

---

## References

### Existing Files
- `agenthub/builtin/tools/rag/core.py` - Current implementation
- `agenthub/builtin/tools/rag/config.py` - Current configuration
- `agenthub/builtin/tools/rag/__init__.py` - Current exports
- `agenthub/core/llm/llm_service.py` - Reusable LLM service
- `agenthub/core/interfaces/llm_interfaces.py` - LLM protocols

### Related Documentation
- `docs/RAG_TOOL_GUIDE.md` - User documentation (update after refactor)
- `examples/builtin_tools/rag_example.py` - Simple example
- `examples/tools/rag_comprehensive_example.py` - Advanced examples

### Test Files
- `tests/phase2.5_tool_injection/core/tools/test_rag_tool.py` - Update for refactored architecture

---

## Conclusion

This refactoring transforms the monolithic RAG implementation into a clean, modular architecture that:

1. ✅ Follows SOLID principles (especially Single Responsibility)
2. ✅ Leverages existing AgentHub infrastructure (LLM service)
3. ✅ Improves performance with batch processing
4. ✅ Enables comprehensive testing
5. ✅ Provides clear extension points
6. ✅ Maintains backward compatibility (with deprecation path)
7. ✅ Reduces code duplication
8. ✅ Improves type safety

The refactoring is incremental, low-risk, and provides immediate benefits in maintainability and performance while setting the foundation for future enhancements.
