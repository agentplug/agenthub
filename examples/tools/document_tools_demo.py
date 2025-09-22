# -*- coding: utf-8 -*-
"""
Document Tools Demo

This demo showcases the built-in document retrieval tools and demonstrates
the difference between agents with and without document tools.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import agenthub
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import agenthub as ah
from agenthub.core.tools.builtin.document import (
    document_parse, 
    document_search, 
    document_chunk, 
    document_extract_metadata
)
import time

# Enable monitoring for better visibility
print("🔍 Monitoring enabled for agent testing")


def create_sample_documents(temp_dir: str) -> dict:
    """Create sample documents for testing."""
    print("📄 Creating sample documents for testing...")
    
    documents = {}
    
    # Create a sample text document
    text_file = os.path.join(temp_dir, "sample_report.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("""
# Quarterly Business Report

## Executive Summary
This quarter has shown significant growth in our technology division. 
We've successfully launched three new products and expanded our market 
presence in the European region.

## Key Metrics
- Revenue increased by 25% compared to last quarter
- Customer satisfaction scores improved to 4.8/5.0
- Employee retention rate reached 95%
- New client acquisitions: 150

## Technology Initiatives
Our development team has been working on several key projects:
1. AI-powered customer service chatbot
2. Mobile application for iOS and Android
3. Cloud infrastructure migration

## Challenges and Solutions
The main challenge this quarter was scaling our infrastructure to handle 
increased traffic. We solved this by implementing a microservices architecture 
and using containerization with Docker.

## Next Quarter Goals
- Launch the mobile application
- Complete cloud migration
- Expand to Asian markets
- Implement advanced analytics dashboard

## Contact Information
For questions about this report, contact:
- CEO: john.doe@company.com
- CTO: jane.smith@company.com
- Phone: +1-555-0123
        """)
    documents['text'] = text_file
    
    # Create a sample markdown document
    md_file = os.path.join(temp_dir, "project_plan.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("""
# Project Plan: E-commerce Platform

## Overview
This document outlines the development plan for our new e-commerce platform.

## Objectives
- Create a modern, scalable e-commerce solution
- Implement secure payment processing
- Provide excellent user experience
- Support multiple languages and currencies

## Technical Requirements

### Backend
- **Language**: Python with Django
- **Database**: PostgreSQL
- **API**: RESTful API with GraphQL support
- **Authentication**: JWT tokens with OAuth2

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Material-UI components
- **State Management**: Redux Toolkit
- **Testing**: Jest and Cypress

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Planning | 2 weeks | Requirements, Architecture |
| Backend Development | 6 weeks | API, Database, Authentication |
| Frontend Development | 8 weeks | UI Components, User Flows |
| Integration | 2 weeks | API Integration, Testing |
| Deployment | 1 week | Production Setup, Monitoring |

## Success Metrics
- Page load time < 2 seconds
- 99.9% uptime
- Support for 10,000 concurrent users
- Mobile responsiveness score > 95
        """)
    documents['markdown'] = md_file
    
    # Create a sample JSON document
    json_file = os.path.join(temp_dir, "data_analysis.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write("""
{
  "analysis_id": "ANL-2024-001",
  "title": "Customer Behavior Analysis",
  "date": "2024-06-28",
  "analyst": "Dr. Sarah Johnson",
  "department": "Data Science",
  "summary": {
    "total_customers": 15420,
    "analysis_period": "Q2 2024",
    "key_findings": [
      "Mobile usage increased by 35%",
      "Peak activity between 7-9 PM",
      "Cart abandonment rate decreased to 12%"
    ]
  },
  "metrics": {
    "page_views": 245000,
    "unique_visitors": 15420,
    "conversion_rate": 0.08,
    "average_session_duration": 180,
    "bounce_rate": 0.15
  },
  "recommendations": [
    "Implement mobile-first design improvements",
    "Add push notifications for cart abandonment",
    "Optimize checkout process for mobile users"
  ]
}
        """)
    documents['json'] = json_file
    
    print(f"✅ Created {len(documents)} sample documents in {temp_dir}")
    return documents


def test_document_tools_directly(documents: dict):
    """Test document tools directly to show their capabilities."""
    print("\n🔧 Testing Document Tools Directly")
    print("=" * 50)
    
    # Test document parsing
    print("\n1. Testing document_parse tool:")
    for doc_type, file_path in documents.items():
        print(f"\n   Parsing {doc_type} document...")
        result = document_parse(file_path, extract_metadata=True, extract_tables=True)
        
        if result['success']:
            content = result['content']
            metadata = result['metadata']
            print(f"   ✅ Successfully parsed {doc_type} document")
            print(f"   📊 Word count: {content.get('word_count', 'N/A')}")
            print(f"   📄 File size: {result.get('file_size', 'N/A')} bytes")
            print(f"   🏷️  Document type: {metadata.get('type', 'N/A')}")
        else:
            print(f"   ❌ Failed to parse {doc_type} document: {result['error']}")
    
    # Test document search
    print("\n2. Testing document_search tool:")
    search_queries = ["revenue growth", "technology initiatives", "mobile application"]
    
    for query in search_queries:
        print(f"\n   Searching for: '{query}'")
        result = document_search(
            query=query,
            source_path=os.path.dirname(list(documents.values())[0]),
            max_results=3,
            similarity_threshold=0.5
        )
        
        if result['success']:
            print(f"   ✅ Found {result['total_found']} results")
            for i, search_result in enumerate(result['results'][:2], 1):
                print(f"   📄 Result {i}: {search_result['document_path'].split('/')[-1]}")
                print(f"      Similarity: {search_result['similarity_score']:.3f}")
        else:
            print(f"   ❌ Search failed: {result['error']}")


def test_agent_without_document_tools(documents: dict):
    """Test agent without document tools."""
    print("\n🤖 Testing Agent WITHOUT Document Tools")
    print("=" * 50)
    
    try:
        print("Agent capabilities without document tools:")
        print("- Can only work with text provided directly")
        print("- Cannot access or search through documents")
        print("- Limited to general knowledge and web search")
        
        # Create document context (same as in test_agent_with_document_tools)
        document_context = f"""
        I have access to the following documents in the directory: {os.path.dirname(list(documents.values())[0])}
        - sample_report.txt: A quarterly business report
        - project_plan.md: An e-commerce platform project plan
        - data_analysis.json: Customer behavior analysis data
        
        Please analyze these documents to answer the questions.
        """
        
        questions = [
            "What is the revenue growth mentioned in the documents?",
            "What technology initiatives are planned?",
            "What are the key metrics from the business report?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. Question: {question}")
            print("⏳ Processing...")
            
            # Create a fresh agent instance for each question to avoid state pollution
            print("🔍 Loading fresh agent with monitoring enabled...")
            agent = ah.load_agent("agentplug/analysis-agent", monitoring=True)
            
            # Include document context in the question
            full_question = f"{document_context}\n\n{question}"
            
            # Actually call the agent
            result = agent.analyze_text(full_question)
            # Handle both monitoring and non-monitoring result structures
            if "result" in result and isinstance(result["result"], dict):
                status = result["result"].get("status", "completed")
                analysis = result["result"].get("summary", "No analysis available")
                tools_used = result["result"].get("tools_used", [])
                # Handle error cases
                if status == "error":
                    analysis = result["result"].get("error", "Unknown error occurred")
            else:
                status = result.get("status", "completed")
                analysis = result.get("summary", "No analysis available")
                tools_used = result.get("tools_used", [])
                # Handle error cases
                if status == "error":
                    analysis = result.get("error", "Unknown error occurred")
            
            print(f"✅ Status: {status}")
            print(f"🔧 Tools used: {', '.join(tools_used) if tools_used else 'None'}")
            print(f"📝 Response: {analysis}")
            print("   Limitation: Cannot access or search documents directly")
            
            # Add interactive prompt between questions
            if i < len(questions):
                print(f"\n⏸️  Question {i} completed. Press Enter to continue to question {i+1}...")
                input()
            
    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        import traceback
        traceback.print_exc()


def test_agent_with_document_tools(documents: dict):
    """Test agent with document tools."""
    print("\n🤖 Testing Agent WITH Document Tools")
    print("=" * 50)
    
    try:
        # Load agent with document tools
        print("🔍 Loading agent with document tools and monitoring enabled...")
        agent = ah.load_agent(
            "agentplug/analysis-agent", 
            external_tools=["document_parse", "document_search", "document_extract_metadata"],
            monitoring=False
        )
        
        print("Agent capabilities with document tools:")
        print("- Can parse multiple document formats")
        print("- Can search through documents semantically")
        print("- Can extract metadata and analyze content")
        print("- Can work with document collections")
        
        # Provide context about the documents to the agent
        document_context = f"""
        I have access to the following documents in the directory: {os.path.dirname(list(documents.values())[0])}
        - sample_report.txt: A quarterly business report
        - project_plan.md: An e-commerce platform project plan
        - data_analysis.json: Customer behavior analysis data
        
        You can use the document tools to search and analyze these documents.
        """
        
        questions = [
            f"{document_context}\n\nWhat is the revenue growth mentioned in the documents?",
            f"{document_context}\n\nWhat technology initiatives are planned?", 
            f"{document_context}\n\nWhat are the key metrics from the business report?",
            f"{document_context}\n\nWhat challenges were faced and how were they solved?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. Question: {question.split('?')[0]}?")
            print("⏳ Processing...")
            
            # Actually call the agent
            result = agent.analyze_text(question)
            # Handle both monitoring and non-monitoring result structures
            if "result" in result and isinstance(result["result"], dict):
                status = result["result"].get("status", "completed")
                analysis = result["result"].get("summary", "No analysis available")
                tools_used = result["result"].get("tools_used", [])
                # Handle error cases
                if status == "error":
                    analysis = result["result"].get("error", "Unknown error occurred")
            else:
                status = result.get("status", "completed")
                analysis = result.get("summary", "No analysis available")
                tools_used = result.get("tools_used", [])
                # Handle error cases
                if status == "error":
                    analysis = result.get("error", "Unknown error occurred")
            
            print(f"✅ Status: {status}")
            print(f"🔧 Tools used: {', '.join(tools_used) if tools_used else 'None'}")
            print(f"📝 Response: {analysis}")
            print("   ✅ Agent can now access and analyze documents directly!")
            
            # Add interactive prompt between questions
            if i < len(questions):
                print(f"\n⏸️  Question {i} completed. Press Enter to continue to question {i+1}...")
                input()
            
    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main demo function."""
    print("🚀 Document Tools Demo")
    print("=" * 50)
    print("This demo showcases the built-in document retrieval tools")
    print("and demonstrates their capabilities for AI agents.\n")
    
    # Create temporary directory for sample documents
    temp_dir = tempfile.mkdtemp(prefix="document_tools_demo_")
    
    try:
        # Create sample documents
        documents = create_sample_documents(temp_dir)
        
        # Test document tools directly
        #test_document_tools_directly(documents)
        
        # Test agent without document tools
        test_agent_without_document_tools(documents)
        
        # Test agent with document tools
        #test_agent_with_document_tools(documents)
        
        # Summary
        print("\n📊 Demo Summary")
        print("=" * 50)
        print("✅ Document parsing: Supports TXT, MD, HTML, JSON, CSV, PDF, DOCX")
        print("✅ Document search: Semantic search with similarity scoring")
        print("✅ Document chunking: Intelligent text segmentation")
        print("✅ Metadata extraction: Comprehensive content analysis")
        print("✅ Agent integration: Seamless tool integration with AI agents")
        print("\n🎯 Key Benefits:")
        print("- Agents can now work with document collections")
        print("- Semantic search finds relevant information quickly")
        print("- Multiple document formats supported automatically")
        print("- Rich metadata extraction for better context")
        print("- Intelligent chunking for optimal retrieval")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up temporary directory: {e}")


if __name__ == "__main__":
    main()
