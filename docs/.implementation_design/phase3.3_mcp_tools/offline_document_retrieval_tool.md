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

### **4. Storage Strategy**
- **SQLite Database**: Metadata, indices, configuration
- **FAISS Index**: Vector embeddings for semantic search
- **Whoosh Index**: Full-text search index
- **File System**: Original documents and extracted content

### **5. Performance Optimization**
- **Incremental Indexing**: Only re-index changed documents
- **Smart Caching**: Cache frequently accessed documents
- **Lazy Loading**: Load document content only when needed
- **Parallel Processing**: Process multiple documents simultaneously

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

### **Technology Stack**
- **Python**: Primary implementation language
- **FAISS**: Vector similarity search
- **Whoosh**: Full-text search engine
- **SQLite**: Metadata and configuration storage
- **sentence-transformers**: Local embedding generation
- **PyPDF2/pdfplumber**: PDF processing
- **python-docx**: Office document processing

### **Key Dependencies**
```
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
whoosh>=2.7.4
PyPDF2>=3.0.0
python-docx>=0.8.11
beautifulsoup4>=4.11.0
python-magic>=0.4.27
```

### **File Structure**
```
offline_document_retrieval/
├── src/
│   ├── document_retrieval/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── scanner.py
│   │   │   ├── extractor.py
│   │   │   ├── indexer.py
│   │   │   └── searcher.py
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   └── tools.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── formats.py
│   │       └── cache.py
├── tests/
├── docs/
├── requirements.txt
└── setup.py
```

This design provides a focused, agent-friendly document retrieval tool that complements other MCP tools while maintaining clear boundaries and responsibilities.
