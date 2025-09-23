import agenthub as ah

paper_analyzer = ah.load_agent("agentplug/scientific-paper-analyzer", monitoring=True)
print("Analyzing paper with solve method...")
result = paper_analyzer.solve("Analyze this paper for me: sample_docs/2501.12948v1.pdf")
print(result)

print("Analyzing paper with analyze_paper method...")
result = paper_analyzer.analyze_paper("sample_docs/2501.12948v1.pdf")
print(result)
