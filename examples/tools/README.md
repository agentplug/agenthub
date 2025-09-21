# Web Tools Demo

This demo clearly demonstrates the difference between agents with and without web tools, perfect for client presentations.

## Quick Start

```bash
python web_tools_demo.py
```

## Demo Options

### 1. Quick Demo (5 minutes) - Recommended for clients
- Shows key comparisons between agents with/without web tools
- Demonstrates web search, scraping, and multiple tools working together
- Perfect for showcasing the value proposition

### 2. Full Demo (15 minutes) - Complete showcase
- All 7 comprehensive demos
- Individual tool comparisons
- Real-world business scenario
- Complete feature demonstration

### 3. Individual Tool Tests
- Direct tool testing without agents
- Verifies all tools are working correctly
- Useful for debugging and validation

## What Each Demo Shows

### Demo 1: Web Search Tool
- **Without**: Agent can only use training data (limited, outdated)
- **With**: Agent can search for current, real-time information
- **Question**: "What are the latest developments in AI regulation in 2025?"

### Demo 2: Web Scraping Tool
- **Without**: Agent cannot access specific website content
- **With**: Agent can extract and analyze content from any website
- **Question**: "Analyze the content from https://httpbin.org/html"

### Demo 3: Web Analysis Tool
- **Without**: Agent cannot perform sentiment analysis or topic extraction
- **With**: Agent provides sentiment, topics, and readability analysis
- **Question**: "Analyze sentiment, topics, and readability of content"

### Demo 4: Web Summarization Tool
- **Without**: Agent cannot process long articles effectively
- **With**: Agent can summarize and extract key points from long content
- **Question**: "Summarize key points from a long article"

### Demo 5: Multiple Tools Working Together
- Shows how agents can chain multiple web tools
- Demonstrates comprehensive research workflows
- **Question**: "Research trends, analyze content, and provide summary"

### Demo 6: Search and Scrape Combo Tool
- Shows the efficiency of combined operations
- One tool that searches and scrapes automatically
- **Question**: "Find and analyze latest information about ML best practices"

### Demo 7: Real-World Business Scenario
- Competitive analysis using multiple web tools
- Shows practical business value
- **Question**: "Conduct competitive analysis of AI customer service tools"

## Key Benefits Demonstrated

1. **Real-time Information Access**: Agents can access current data
2. **Content Extraction**: Agents can analyze specific web content
3. **Advanced Analysis**: Sentiment, topics, readability insights
4. **Efficient Summarization**: Process long articles quickly
5. **Workflow Automation**: Multiple tools working together
6. **Business Value**: Real-world competitive analysis

## Perfect for Client Demos

This demo is specifically designed for client presentations because it:
- Clearly shows the difference between agents with/without tools
- Uses real-world examples and scenarios
- Demonstrates measurable business value
- Is easy to follow and understand
- Shows both individual and combined tool capabilities

## Technical Notes

- All demos use the `agentplug/analysis-agent` for consistency
- Tools are loaded using the `external_tools` parameter
- Monitoring is enabled for multi-tool demos
- Error handling ensures smooth demo experience
- Results are truncated for readability but show full capabilities