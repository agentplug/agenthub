# Offline Document Retrieval MCP Tool - Design Specification

## **Purpose & Vision**

### **Core Purpose**
Create a **specialized offline document retrieval tool** that focuses exclusively on finding, retrieving, and providing access to documents from local sources. This tool should be **agent-agnostic** and work effectively with any AI agent, from simple to sophisticated.

### **Primary Use Cases**
- **Document Discovery**: Find relevant documents based on queries
- **Content Retrieval**: Extract and return document content
- **Metadata Access**: Provide document properties and information
- **Source Attribution**: Track document origins and relationships
- **Context Provision**: Supply documents as context for other tools

## **Functional Requirements**

### **1. Core Document Operations**
- **Search**: Find documents by content, metadata, or both
- **Retrieve**: Get full document content or specific sections
- **List**: Enumerate documents matching criteria
- **Get Metadata**: Extract document properties and information
- **Get Snippets**: Return relevant text excerpts with context

### **2. Document Format Support** (Focused List)
- **Text Documents**: TXT, MD, RST, AsciiDoc
- **Office Documents**: DOCX, XLSX, PPTX, ODT
- **PDFs**: Text extraction and metadata
- **Web Archives**: HTML, MHTML (offline web pages)
- **Structured Data**: JSON, XML, YAML (as documents)
- **Code Files**: Source code (as text documents)

### **3. Search Capabilities** (Document-Focused)
- **Content Search**: Full-text search within documents
- **Metadata Search**: Search by file properties, dates, authors
- **Semantic Search**: Find conceptually similar documents
- **Hybrid Search**: Combine content and metadata search
- **Filtered Search**: Filter by document type, size, date range
- **Fuzzy Search**: Handle typos in document content

### **4. Agent-Friendly Interface**
- **Simple Queries**: Natural language document requests
- **Structured Responses**: Consistent JSON output format
- **Error Handling**: Graceful failure with helpful messages
- **Batch Operations**: Handle multiple document requests
- **Context Preservation**: Maintain document relationships

## **Excluded Functionality** (Delegated to Other Tools)

### **❌ Not Included**
- **Code Execution**: Handled by Code Generation tool
- **Data Analysis**: Handled by Tabular Analysis tool
- **Web Search**: Handled by Web Search tool
- **External APIs**: Handled by External Resources tool
- **Document Processing**: Focus on retrieval, not analysis
- **Content Generation**: Focus on finding, not creating
- **Real-time Data**: Focus on static documents only

## **Core MCP Tool Function**

### **Single Unified Tool: `document_retrieval`**

Based on agentHub's tool execution patterns, we use a single, unified tool that handles all document operations through intelligent parameter detection:

```python
@tool(
    name="document_retrieval",
    description="Search and retrieve documents from your local collection. Use this tool to find relevant documents, get their content, or list available documents. Works with any query - just describe what you're looking for."
)
def document_retrieval(
    query: str,
    operation: str = "search",
    limit: int = 5,
    include_content: bool = True,
    **kwargs
) -> dict:
    """
    Universal document retrieval tool that works with any agent.
    
    Args:
        query: What you're looking for (e.g., "AI trends", "Python tutorials", "meeting notes")
        operation: What to do ("search", "list", "get", "find") - defaults to "search"
        limit: How many results to return (1-20, default 5)
        include_content: Whether to include document content (default True)
        **kwargs: Additional filters (optional)
    
    Returns:
        Dictionary with search results, document info, and clear status
    """
```

### **Operation Detection Logic**

The tool automatically detects the intended operation from the query:

```python
def _detect_operation(query: str, operation: str) -> str:
    """Auto-detect operation from query if not specified."""
    if operation == "search":
        if any(word in query.lower() for word in ["list", "show", "all", "available"]):
            return "list"
        elif any(word in query.lower() for word in ["get", "fetch", "retrieve", "download"]):
            return "get"
        elif any(word in query.lower() for word in ["find", "search", "look for"]):
            return "search"
    return operation
```

### **Response Format**

All operations return a consistent, agent-friendly response:

```python
{
    "status": "success" | "error",
    "operation": "search" | "list" | "get",
    "query": "original query",
    "total_found": 3,
    "documents": [
        {
            "id": "doc_001",
            "title": "Document Title",
            "type": "pdf",
            "path": "/path/to/document.pdf",
            "relevance_score": 0.95,
            "summary": "Document summary...",
            "content": "Full content..." if include_content else None,
            "metadata": {
                "author": "John Doe",
                "created": "2024-01-01T00:00:00Z",
                "size": 1024000,
                "tags": ["research", "ai"]
            }
        }
    ],
    "message": "Found 3 documents matching 'AI trends'",
    "suggestions": [
        "Use 'get' operation with document ID for full content",
        "Try more specific search terms to narrow results"
    ]
}
```

### **Usage Examples for Agents**

```python
# Simple search
document_retrieval("AI trends")

# List all documents
document_retrieval("show all documents", operation="list")

# Get specific document
document_retrieval("Python tutorial", operation="get")

# Search with filters
document_retrieval("meeting notes", limit=3, document_type="pdf")
```

## **Agent Integration Design**

### **1. AgentHub Tool Context Integration**

The tool integrates seamlessly with agentHub's tool context system:

```python
# Tool description for agent's system prompt
tool_context = {
    "available_tools": ["document_retrieval"],
    "tool_descriptions": {
        "document_retrieval": "Search and retrieve documents from your local collection. Use this tool to find relevant documents, get their content, or list available documents. Works with any query - just describe what you're looking for."
    },
    "tool_usage_examples": {
        "document_retrieval": [
            '{"tool_call": {"tool_name": "document_retrieval", "arguments": {"query": "AI trends"}}}',
            '{"tool_call": {"tool_name": "document_retrieval", "arguments": {"query": "Python tutorials", "operation": "search", "limit": 3}}}',
            '{"tool_call": {"tool_name": "document_retrieval", "arguments": {"query": "show all documents", "operation": "list"}}}'
        ]
    }
}
```

### **2. Agent-Friendly Design Principles**

#### **Simple Query Interface**
- **Natural Language**: Accept conversational queries like "find AI documents"
- **Minimal Parameters**: Only `query` is required, everything else has defaults
- **Auto-Detection**: Automatically figures out what the agent wants to do
- **Error Recovery**: Provides helpful suggestions when things go wrong

#### **Consistent Response Format**
```python
# All responses follow this structure
{
    "status": "success" | "error",
    "operation": "search" | "list" | "get",
    "query": "original query",
    "total_found": 3,
    "documents": [...],
    "message": "Human-readable status message",
    "suggestions": ["Helpful tips for the agent"]
}
```

#### **Intelligent Defaults**
- **Reasonable Limits**: Default to 5 results, max 20
- **Content Inclusion**: Include content by default for better agent experience
- **Error Messages**: Clear, actionable error messages
- **Fallback Behavior**: Graceful degradation when features unavailable

#### **Context Preservation**
- **Document Relationships**: Track document connections
- **Source Attribution**: Always include document source information
- **Version Tracking**: Handle document versions and updates
- **Change Detection**: Notify when documents are modified

### **3. Why This Design Works for "Dumb" Agents**

#### **Single Tool Interface**
- Only one tool to remember: `document_retrieval`
- No complex parameter structures to learn
- Works with any description of what the agent wants

#### **Natural Language Processing**
- Agent can say "find AI documents" or "show me Python tutorials"
- Tool automatically figures out the best search strategy
- No need to understand technical search parameters

#### **Intelligent Suggestions**
- When no results: "Try broader terms, use 'list' to see available docs"
- When one result: "Use 'get' to get full content"
- When many results: "Try more specific terms"

#### **Error Recovery**
- Graceful handling of mistakes
- Clear explanations of what went wrong
- Actionable suggestions for fixing the problem

### **4. Agent Learning and Adaptation**

The tool helps agents learn and improve over time:

```python
# Agent's first attempt
document_retrieval("quantum computing algorithms")
# Returns: 0 results + suggestions

# Agent learns and tries again
document_retrieval("algorithms")  # Broader term
# Returns: 3 results + suggestions

# Agent learns about operations
document_retrieval("show all documents", operation="list")
# Returns: All available documents
```

## **Implementation Architecture**

### **1. Tool Execution Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT RETRIEVAL TOOL FLOW                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   AGENT     │    │   TOOL      │    │   SEARCH    │    │   RESULTS   │
│             │    │             │    │   ENGINE    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │ 1. Call           │                   │                   │
       │ document_retrieval│                   │                   │
       │ ("AI trends")     │                   │                   │
       ├──────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │ 2. Process Query  │                   │
       │                   │ - Extract terms   │                   │
       │                   │ - Choose strategy │                   │
       │                   ├──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │ 3. Search Docs    │
       │                   │                   │ - Keyword search  │
       │                   │                   │ - Score results   │
       │                   │                   ├──────────────────►│
       │                   │                   │                   │
       │                   │                   │ 4. Process Results│
       │                   │                   │ - Add metadata    │
       │                   │                   │ - Format response │
       │                   │                   ├──────────────────►│
       │                   │                   │                   │
       │                   │ 5. Generate       │                   │
       │                   │ Suggestions       │                   │
       │                   │ - Analyze results │                   │
       │                   │ - Create tips     │                   │
       │                   ├──────────────────►│                   │
       │                   │                   │                   │
       │ 6. Return Response│                   │                   │
       │ - Status          │                   │                   │
       │ - Documents       │                   │                   │
       │ - Suggestions     │                   │                   │
       │◄──────────────────┤                   │                   │
```

### **2. Search Engine Implementation**

#### **Query Processing**
```python
def _process_query(query: str) -> dict:
    """Process and normalize the search query."""
    normalized_query = query.lower().strip()
    key_terms = _extract_key_terms(normalized_query)
    query_type = _detect_query_type(normalized_query)
    filters = _extract_filters(normalized_query)
    
    return {
        "original": query,
        "normalized": normalized_query,
        "key_terms": key_terms,
        "type": query_type,  # "question", "keyword", "phrase", "boolean"
        "filters": filters
    }
```

#### **Search Strategy Selection**
```python
def _select_search_strategy(processed_query: dict) -> str:
    """Select the best search strategy based on query characteristics."""
    query_type = processed_query["type"]
    key_terms = processed_query["key_terms"]
    
    # For questions, use semantic search
    if query_type == "question":
        return "semantic"
    
    # For short keyword queries, use keyword search
    elif query_type == "keyword" and len(key_terms) <= 2:
        return "keyword"
    
    # For complex queries, use hybrid approach
    elif len(key_terms) > 3 or query_type == "phrase":
        return "hybrid"
    
    # Default to semantic search
    else:
        return "semantic"
```

#### **Search Implementations**
- **Semantic Search**: Uses vector embeddings for conceptual similarity
- **Keyword Search**: Traditional full-text search with term matching
- **Hybrid Search**: Combines semantic and keyword approaches
- **Fallback Search**: Simple text matching when other methods fail

### **3. Suggestion Generation**

The tool generates intelligent suggestions to guide agent behavior:

```python
def _generate_suggestions(query: str, results: list) -> list:
    """Generate helpful suggestions based on search results."""
    suggestions = []
    
    if len(results) == 0:
        suggestions.extend([
            "Try broader search terms (e.g., 'AI' instead of 'artificial intelligence')",
            "Use 'list' operation to see available documents",
            "Check if documents are properly indexed"
        ])
    elif len(results) == 1:
        suggestions.extend([
            "Use 'get' operation with document ID to retrieve full content",
            "Try related search terms for more results"
        ])
    elif len(results) > 5:
        suggestions.extend([
            "Use more specific search terms to narrow results",
            "Add filters like document type or date range"
        ])
    
    return suggestions
```

### **4. Storage Strategy (MVP: JSON-Based)**

#### **A. MVP Storage Architecture**
For the initial implementation, we use a simple JSON-based storage approach:

```
data/
├── documents.json          # Main document metadata
├── search_index.json       # Search terms → document IDs mapping
└── documents/              # Document files
    ├── doc_001_example.txt
    └── doc_002_ai_trends.pdf
```

#### **B. JSON File Structure**

**documents.json** - Contains all document metadata:
```json
{
  "documents": {
    "doc_001": {
      "id": "doc_001",
      "title": "AI Trends 2024",
      "file_path": "./data/documents/doc_001_ai_trends.pdf",
      "file_type": ".pdf",
      "file_size": 1024000,
      "created_at": "2024-01-15T10:30:00Z",
      "modified_at": "2024-01-15T10:30:00Z",
      "summary": "Comprehensive analysis of AI trends...",
      "author": "John Doe",
      "tags": ["AI", "trends", "2024"],
      "metadata": {"pages": 25, "language": "en"}
    }
  },
  "metadata": {
    "total_documents": 1,
    "last_updated": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

**search_index.json** - Contains search term mappings:
```json
{
  "index": {
    "ai": ["doc_001"],
    "trends": ["doc_001"],
    "2024": ["doc_001"],
    "comprehensive": ["doc_001"],
    "analysis": ["doc_001"]
  },
  "metadata": {
    "last_indexed": "2024-01-15T10:30:00Z",
    "total_terms": 5
  }
}
```

#### **C. Storage Operations**

**Document Addition Process:**
1. Extract text content from document
2. Generate unique document ID
3. Copy file to `documents/` directory
4. Store metadata in `documents.json`
5. Update search index in `search_index.json`

**Search Process:**
1. Extract search terms from query
2. Look up terms in `search_index.json`
3. Get matching document IDs
4. Fetch full details from `documents.json`
5. Calculate relevance scores and rank results

#### **D. Benefits of JSON Approach**
- **No Database**: Pure file-based, no SQLite or external DB
- **Human Readable**: All data in JSON, easy to inspect and debug
- **Portable**: Just copy the data directory
- **Simple**: No database setup or configuration
- **Version Control Friendly**: JSON files can be tracked in git
- **Fast Development**: Can be built in minutes

#### **E. Future Storage Enhancements**
The JSON-based approach serves as the MVP foundation. Future versions will support:
- **SQLite Database**: For better performance and ACID compliance
- **Vector Embeddings**: FAISS index for semantic search
- **Advanced Caching**: Redis for high-performance scenarios
- **Distributed Storage**: For enterprise deployments
- **Encryption**: For sensitive document collections

### **5. Performance Optimization (MVP)**
- **Simple Indexing**: Basic term-based search index
- **File-based Caching**: Store frequently accessed data in memory
- **Lazy Loading**: Load document content only when needed
- **Batch Operations**: Process multiple documents efficiently

## **Non-Functional Requirements**

### **Performance**
- **Response Time**: < 500ms for typical queries
- **Indexing Speed**: 1000+ documents per minute
- **Memory Efficiency**: Optimized for local resource constraints
- **Storage Efficiency**: Compressed indices and embeddings

### **Privacy & Security**
- **Zero Network**: No external API calls or data transmission
- **Local Processing**: All computation happens locally
- **Data Encryption**: Optional local encryption of indices
- **Access Control**: File system permissions integration
- **Audit Logging**: Local activity tracking

### **Reliability**
- **Offline Resilience**: Works without internet connection
- **Data Integrity**: Consistent local storage
- **Backup Support**: Integration with local backup systems
- **Error Recovery**: Graceful handling of corrupted documents

## **Quality Metrics**

### **1. Retrieval Quality**
- **Precision@K**: Accuracy of top-K results
- **Recall@K**: Coverage of relevant documents
- **Query Response Time**: < 500ms for typical queries
- **Indexing Speed**: 1000+ documents per minute

### **2. Agent Usability**
- **Query Success Rate**: 95%+ successful queries
- **Error Recovery**: Helpful error messages and suggestions
- **Response Consistency**: Uniform response format
- **Document Coverage**: 99%+ of supported formats indexed

### **3. System Performance**
- **Memory Usage**: RAM consumption during operation
- **Storage Efficiency**: Index size vs. document collection size
- **Query Throughput**: Queries per second
- **Error Rate**: Failed requests percentage

## **Success Criteria**

### **Phase 1: MVP**
- Support 5 document formats (PDF, DOCX, TXT, MD, HTML)
- Basic full-text and metadata search
- < 500ms response time
- 10,000+ document collection support

### **Phase 2: Enhanced**
- Support 10+ document formats
- Semantic search capabilities
- Advanced filtering and ranking
- Real-time indexing

### **Phase 3: Advanced**
- Multi-language support
- Document relationship mapping
- Advanced caching strategies
- Enterprise features

## **Deployment Considerations**

### **Local Installation**
- **Standalone Binary**: Single executable with all dependencies
- **Python Package**: pip installable with local dependencies
- **Docker Container**: Containerized deployment option
- **System Integration**: Native OS integration where possible

### **Resource Requirements**
- **Minimum**: 4GB RAM, 2GB storage, 2 CPU cores
- **Recommended**: 8GB RAM, 10GB storage, 4 CPU cores
- **Storage**: 1GB per 10,000 documents (approximate)
- **Memory**: 2GB base + 0.1GB per 1000 documents

## **Implementation Notes**

### **Technology Stack (MVP)**
- **Python**: Primary implementation language
- **JSON**: Data storage and serialization
- **File System**: Document storage and organization
- **PyPDF2/pdfplumber**: PDF processing (optional)
- **python-docx**: Office document processing (optional)
- **beautifulsoup4**: HTML processing (optional)

### **Key Dependencies (MVP)**
```
# Core dependencies (required)
json>=2.0.9  # Built-in Python module
pathlib>=1.0.1  # Built-in Python module
hashlib>=1.0  # Built-in Python module
re>=2.2.1  # Built-in Python module
datetime>=1.0  # Built-in Python module

# Optional document processing
PyPDF2>=3.0.0  # For PDF files
python-docx>=0.8.11  # For DOCX files
beautifulsoup4>=4.11.0  # For HTML files
```

### **Future Technology Stack**
- **FAISS**: Vector similarity search
- **Whoosh**: Full-text search engine
- **SQLite**: Metadata and configuration storage
- **sentence-transformers**: Local embedding generation
- **Redis**: High-performance caching

### **File Structure (MVP)**
```
offline_document_retrieval/
├── src/
│   ├── document_retrieval/
│   │   ├── __init__.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── json_storage.py      # JSON-based storage implementation
│   │   │   └── document_processor.py # Document text extraction
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   └── tools.py             # MCP tool implementation
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── search.py            # Search and ranking logic
│   │       └── helpers.py           # Utility functions
├── data/                            # Runtime data directory
│   ├── documents.json               # Document metadata
│   ├── search_index.json            # Search index
│   └── documents/                   # Document files
│       ├── doc_001_example.txt
│       └── doc_002_ai_trends.pdf
├── tests/
├── docs/
├── requirements.txt
└── setup.py
```

### **Future File Structure**
```
offline_document_retrieval/
├── src/
│   ├── document_retrieval/
│   │   ├── storage/
│   │   │   ├── json_storage.py      # MVP implementation
│   │   │   ├── sqlite_storage.py    # Future: SQLite implementation
│   │   │   ├── vector_storage.py    # Future: Vector search
│   │   │   └── cache_storage.py     # Future: Redis caching
│   │   ├── search/
│   │   │   ├── text_search.py       # Text-based search
│   │   │   ├── semantic_search.py   # Future: Semantic search
│   │   │   └── hybrid_search.py     # Future: Hybrid search
│   │   └── mcp/
│   │       └── tools.py
├── data/
└── ...
```

## **Document Addition Solutions**

### **1. Programmatic API (Best for Developers)**

```python
class DocumentIndexAPI:
    def add_file(self, file_path: str, metadata: dict = None) -> str:
        """Add single file with full control."""
        content = self._extract_content(file_path)
        return self.storage.add_document(file_path, content, metadata)
    
    def add_directory(self, directory_path: str, recursive: bool = True) -> dict:
        """Add all files from directory."""
        results = {"successful": [], "failed": [], "skipped": []}
        for file_path in Path(directory_path).glob("**/*" if recursive else "*"):
            if file_path.is_file():
                try:
                    doc_id = self.add_file(str(file_path))
                    results["successful"].append({"file": str(file_path), "doc_id": doc_id})
                except Exception as e:
                    results["failed"].append({"file": str(file_path), "error": str(e)})
        return results
    
    def add_from_url(self, url: str, metadata: dict = None) -> str:
        """Add document from URL."""
        response = requests.get(url)
        temp_path = self._save_temp_file(response.content, url)
        try:
            return self.add_file(temp_path, metadata)
        finally:
            Path(temp_path).unlink()
```

**Benefits:**
- Full programmatic control
- Robust error handling and logging
- Supports files, directories, and URLs
- Easy integration with other systems

### **2. Smart Auto-Discovery (Best for End Users)**

```python
class SmartDocumentDiscovery:
    def __init__(self, storage):
        self.storage = storage
        self.watched_directories = []
        self.supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.html']
    
    def setup_auto_discovery(self):
        """Set up intelligent document discovery."""
        # Watch common document directories
        common_dirs = [
            Path.home() / "Documents",
            Path.home() / "Downloads", 
            Path.cwd() / "documents"
        ]
        
        for directory in common_dirs:
            if directory.exists():
                self.watch_directory(directory)
    
    def watch_directory(self, directory: Path):
        """Watch directory for new files."""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class DocumentHandler(FileSystemEventHandler):
            def on_created(self, event):
                if not event.is_directory:
                    self._process_new_file(event.src_path)
        
        observer = Observer()
        observer.schedule(DocumentHandler(), str(directory), recursive=True)
        observer.start()
    
    def _process_new_file(self, file_path: str):
        """Process newly created file."""
        file_path = Path(file_path)
        if self._should_index_file(file_path):
            try:
                doc_id = self.storage.add_document(
                    str(file_path),
                    self._extract_content(file_path),
                    self._generate_metadata(file_path)
                )
                print(f"✅ Auto-indexed: {file_path.name}")
            except Exception as e:
                print(f"❌ Failed to index {file_path.name}: {e}")
```

**Benefits:**
- Zero configuration required
- Automatic file detection and indexing
- Smart filtering (only relevant files)
- Continuous monitoring

### **3. Batch Processing (Best for Bulk Operations)**

```python
class BatchDocumentProcessor:
    def process_batch_file(self, batch_file: str):
        """Process YAML batch file with document specifications."""
        with open(batch_file, 'r') as f:
            batch_config = yaml.safe_load(f)
        
        results = {"total": 0, "successful": 0, "failed": 0, "skipped": 0}
        
        for item in batch_config['documents']:
            results['total'] += 1
            try:
                if 'file' in item:
                    self._add_file(item['file'], item.get('metadata', {}))
                elif 'directory' in item:
                    self._add_directory(item['directory'], item.get('recursive', True))
                elif 'url' in item:
                    self._add_from_url(item['url'], item.get('metadata', {}))
                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                print(f"❌ Failed to process {item}: {e}")
        
        return results
```

**Batch Configuration Example:**
```yaml
documents:
  - file: "path/to/document.pdf"
    metadata:
      title: "Document Title"
      author: "Author Name"
      tags: ["tag1", "tag2"]
  - directory: "path/to/documents"
    recursive: true
    metadata:
      project: "Project Name"
      tags: ["project", "docs"]
  - url: "https://example.com/document.pdf"
    metadata:
      title: "Online Document"
      source: "web"
```

**Benefits:**
- Process many documents at once
- YAML-based configuration
- Mix different source types
- Resumable operations

### **Implementation Strategy**

**Phase 1: Core API** - Implement programmatic API for developers
**Phase 2: Auto-Discovery** - Add smart file watching for end users  
**Phase 3: Batch Processing** - Add bulk operations for large collections
**Phase 4: CLI Interface** - Add command-line tools for immediate use

This design provides a focused, agent-friendly document retrieval tool that complements other MCP tools while maintaining clear boundaries and responsibilities.
