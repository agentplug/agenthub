import time

import agenthub as ah

start_time = time.time()
paper_analyzer = ah.load_agent("agentplug/scientific-paper-analyzer")
print("Analyzing paper with solve method...")
result = paper_analyzer.solve("Analyze this paper for me: sample_docs/2501.12948v1.pdf")
print(result)
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
