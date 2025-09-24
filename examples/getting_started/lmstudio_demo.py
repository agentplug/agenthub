#!/usr/bin/env python3
"""
Demo script showing LM Studio support in AgentHub.

This script demonstrates the new LM Studio fallback functionality
with updated model scoring priorities.
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agenthub.core.llm.llm_service import get_shared_llm_service


def main():
    """Demonstrate LM Studio support functionality."""
    print("🚀 AgentHub LM Studio Support Demo")
    print("=" * 50)

    # Initialize LLM service (will auto-detect Ollama first, then LM Studio)
    print("\n1. Initializing LLM Service...")
    service = get_shared_llm_service()
    print(f"   Current model: {service.get_current_model()}")
    print(f"   Is local model: {service.is_local_model()}")

    # Test model scoring with new priorities
    print("\n2. Testing Model Scoring System...")
    test_models = [
        "ollama:qwen:8b-instruct",  # High score (qwen=60, 8b=40, instruct=10, ollama=5)
        "qwen/qwen3-8b-instruct",  # LM Studio format (qwen=60, 8b=40, instruct=10)
        "ollama:deepseek-r1:32b",  # Should score high (deepseek=60, 32b=50, ollama=5)
        "ollama:gpt-oss:20b",  # Should score medium (gpt-oss=50, 20b=45, ollama=5)
        "ollama:llama3:latest",  # Should score medium (llama=40, latest=40, ollama=5)
        "meta-llama/llama-3.2-1b-instruct",  # LM Studio (llama=40, 1b=30, instruct=10)
    ]

    print("   Model Scoring Results:")
    for model in test_models:
        score = service._calculate_model_score(model)
        platform = "Ollama" if model.startswith("ollama:") else "LM Studio"
        print(f"   {model:<35} → {score:3d} points ({platform})")

    # Test basic generation
    print("\n3. Testing Generation...")
    start_time = time.time()
    response = service.generate("What is the capital of France?")
    end_time = time.time()
    print(f"   Response: {response[:80]}...")
    print(f"   Time: {end_time - start_time:.2f}s")

    print("\n✅ Demo completed!")
    print("\nKey Features:")
    print("- 🥇 Ollama preferred, LM Studio as fallback")
    print("- 🎯 Qwen & DeepSeek: 60 points (highest priority)")
    print("- 🥈 GPT-OSS: 50 points (high priority)")
    print("- 📏 Latest types: 8B equivalent (40 points)")
    print("- 🏆 Ollama platform bonus: +5 points")


if __name__ == "__main__":
    main()
