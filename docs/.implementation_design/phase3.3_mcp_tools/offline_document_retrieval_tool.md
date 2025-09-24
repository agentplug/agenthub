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

### **2. Document Format Support**
- **Text Documents**: TXT, MD, RST, AsciiDoc
- **Office Documents**: DOCX, XLSX, PPTX, ODT
- **PDFs**: Text extraction and metadata
- **Web Archives**: HTML, MHTML (offline web pages)
- **Structured Data**: JSON, XML, YAML
- **Code Files**: Python, JavaScript, Java, C++

### **3. Search Capabilities**
- **Content Search**: Full-text search within documents
- **Metadata Search**: Search by file properties, dates, authors
- **Smart Filtering**: Filter by document type, size, date range
- **Relevance Scoring**: Rank results by relevance to query

### **4. Agent-Friendly Interface**
- **Natural Language**: Accept conversational queries
- **Consistent Responses**: Structured JSON output format
- **Smart Suggestions**: Helpful guidance for better results
- **Error Recovery**: Graceful failure with actionable messages

## **Excluded Functionality**

### **❌ Not Included**
- **Code Execution**: Handled by Code Generation tool
- **Data Analysis**: Handled by Tabular Analysis tool
- **Web Search**: Handled by Web Search tool
- **External APIs**: Handled by External Resources tool
- **Document Processing**: Focus on retrieval, not analysis
- **Content Generation**: Focus on finding, not creating

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
    
    return {
        "original": query,
        "normalized": normalized_query,
        "key_terms": key_terms
    }
```

#### **Search Strategy**
- **Keyword Search**: Traditional full-text search with term matching
- **Relevance Scoring**: Rank results by title, content, and metadata matches
- **Smart Filtering**: Filter by document type, size, and date

### **3. Suggestion Generation**

The tool generates intelligent suggestions to guide agent behavior:

```python
def _generate_suggestions(query: str, results: list) -> list:
    """Generate helpful suggestions based on search results."""
    if len(results) == 0:
        return [
            "Try broader search terms",
            "Use 'list' operation to see available documents"
        ]
    elif len(results) == 1:
        return ["Use 'get' operation to retrieve full content"]
    elif len(results) > 5:
        return ["Try more specific search terms to narrow results"]
    
    return []
```

### **4. Storage Strategy (JSON-Based)**

#### **Storage Architecture**
```
data/
├── documents.json          # Document metadata
├── search_index.json       # Search term mappings
└── documents/              # Document files
    ├── doc_001_example.txt
    └── doc_002_ai_trends.pdf
```

#### **JSON File Structure**

**documents.json** - Document metadata:
```json
{
  "documents": {
    "doc_001": {
      "id": "doc_001",
      "title": "AI Trends 2024",
      "file_path": "./data/documents/doc_001_ai_trends.pdf",
      "file_type": ".pdf",
      "summary": "Comprehensive analysis of AI trends...",
      "author": "John Doe",
      "tags": ["AI", "trends", "2024"]
    }
  }
}
```

**search_index.json** - Search term mappings:
```json
{
  "index": {
    "ai": ["doc_001"],
    "trends": ["doc_001"],
    "2024": ["doc_001"]
  }
}
```

#### **Benefits of JSON Approach**
- **No Database**: Pure file-based storage
- **Human Readable**: Easy to inspect and debug
- **Portable**: Copy directory to move everything
- **Simple**: No setup or configuration required
- **Fast Development**: Can be built in minutes

## **Performance Requirements**

### **Response Time**
- **Typical Queries**: < 500ms
- **Large Collections**: < 2 seconds for 10,000+ documents
- **Indexing Speed**: 100+ documents per minute

### **Resource Usage**
- **Memory**: < 100MB for typical usage
- **Storage**: ~1MB per 100 documents
- **CPU**: Minimal impact during operation

### **Reliability**
- **Offline Operation**: Works without internet connection
- **Data Integrity**: Consistent local storage
- **Error Recovery**: Graceful handling of file errors

## **Implementation Notes**

### **Technology Stack**
- **Python**: Primary implementation language
- **JSON**: Data storage and serialization
- **File System**: Document storage and organization
- **Optional**: PyPDF2, python-docx, beautifulsoup4 for document processing

### **Key Dependencies**
```
# Core (built-in Python modules)
json, pathlib, hashlib, re, datetime

# Optional document processing
PyPDF2>=3.0.0  # For PDF files
python-docx>=0.8.11  # For DOCX files
beautifulsoup4>=4.11.0  # For HTML files
```

### **File Structure**
```
offline_document_retrieval/
├── src/
│   ├── document_retrieval/
│   │   ├── storage/
│   │   │   ├── json_storage.py      # JSON storage
│   │   │   └── document_processor.py # Text extraction
│   │   ├── mcp/
│   │   │   └── tools.py             # MCP tool
│   │   └── utils/
│   │       ├── search.py            # Search logic
│   │       └── helpers.py           # Utilities
├── data/                            # Runtime data
│   ├── documents.json               # Metadata
│   ├── search_index.json            # Search index
│   └── documents/                   # Document files
└── requirements.txt
```

## **Smart File Watching for Document Addition**

### **How Smart File Watching Works**

The document retrieval tool uses intelligent file system monitoring to automatically discover and index new documents without user intervention.

#### **1. Automatic Directory Monitoring**

```python
class SmartDocumentDiscovery:
    def __init__(self, storage):
        self.storage = storage
        self.supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.html', '.json']
        self.watched_directories = []
    
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
        """Watch directory for new files using file system events."""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class DocumentHandler(FileSystemEventHandler):
            def __init__(self, discovery):
                self.discovery = discovery
            
            def on_created(self, event):
                if not event.is_directory:
                    self.discovery._process_new_file(event.src_path)
            
            def on_modified(self, event):
                if not event.is_directory:
                    self.discovery._process_modified_file(event.src_path)
        
        handler = DocumentHandler(self)
        observer = Observer()
        observer.schedule(handler, str(directory), recursive=True)
        observer.start()
        
        self.watched_directories.append({
            'path': directory,
            'observer': observer
        })
```

#### **2. Intelligent File Processing**

```python
def _process_new_file(self, file_path: str):
    """Process newly created file with smart filtering."""
    file_path = Path(file_path)
    
    # Wait for file to be fully written
    self._wait_for_file_complete(file_path)
    
    # Check if file should be indexed
    if not self._should_index_file(file_path):
        return
    
    try:
        # Extract content and metadata
        content = self._extract_content(file_path)
        metadata = self._generate_metadata(file_path)
        
        # Add to storage
        doc_id = self.storage.add_document(
            str(file_path),
            content,
            metadata
        )
        
        print(f"✅ Auto-indexed: {file_path.name}")
        
    except Exception as e:
        print(f"❌ Failed to index {file_path.name}: {e}")

def _should_index_file(self, file_path: Path) -> bool:
    """Smart filtering to determine if file should be indexed."""
    # Check file extension
    if file_path.suffix.lower() not in self.supported_extensions:
        return False
    
    # Check file size (skip very large files)
    if file_path.stat().st_size > 100 * 1024 * 1024:  # 100MB
        return False
    
    # Check if file is already indexed
    if self._is_already_indexed(file_path):
        return False
    
    # Check file age (skip very old files)
    file_age = time.time() - file_path.stat().st_mtime
    if file_age > 365 * 24 * 3600:  # 1 year
        return False
    
    return True
```

#### **3. Real-Time Document Discovery Process**

```
1. File System Event → New file detected
2. File Validation → Check extension, size, age
3. Content Extraction → Extract text from document
4. Metadata Generation → Auto-generate title, tags, etc.
5. Storage Update → Add to JSON storage and search index
6. User Notification → Show success/failure message
```

#### **4. Benefits of Smart File Watching**

- **Zero Configuration**: Works out of the box
- **Automatic Discovery**: No manual file addition needed
- **Smart Filtering**: Only indexes relevant documents
- **Real-Time Updates**: Documents available immediately
- **Continuous Monitoring**: Always up to date
- **User-Friendly**: No technical knowledge required

#### **5. Supported File Types**

- **Documents**: PDF, DOCX, TXT, MD, HTML
- **Data Files**: JSON, XML, YAML
- **Code Files**: Python, JavaScript, Java, C++
- **Excluded**: Images, videos, executables, system files

#### **6. User Experience**

Users simply:
1. **Save documents** to watched directories (Documents, Downloads, etc.)
2. **Documents are automatically indexed** within seconds
3. **Search immediately** using the document_retrieval tool
4. **No setup or configuration** required

This approach provides the best user experience by eliminating the need for manual document management while maintaining intelligent filtering and processing.

This design provides a focused, agent-friendly document retrieval tool that complements other MCP tools while maintaining clear boundaries and responsibilities.
