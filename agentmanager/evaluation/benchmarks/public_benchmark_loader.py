"""
Public benchmark loader for downloading and managing publicly available benchmarks.
"""

import os
import json
import requests
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from ..core.data_models import PublicBenchmark, BenchmarkDefinition, SampleData

logger = logging.getLogger(__name__)


class PublicBenchmarkLoader:
    """Loader for publicly available benchmarks."""
    
    def __init__(self, cache_dir: str = "~/.agenthub/benchmarks/"):
        """Initialize the public benchmark loader."""
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported public benchmarks
        self.supported_benchmarks = {
            "humaneval": {
                "name": "HumanEval",
                "description": "Code generation benchmark with 164 problems",
                "source": "https://github.com/openai/human-eval",
                "format": "jsonl",
                "metrics": ["pass_at_k", "exact_match"],
                "license": "MIT",
                "citation": "Chen et al. (2021). Evaluating Large Language Models Trained on Code."
            },
            "glue": {
                "name": "GLUE",
                "description": "General Language Understanding Evaluation",
                "source": "https://gluebenchmark.com/",
                "format": "tsv",
                "metrics": ["accuracy", "f1", "matthews_correlation"],
                "license": "Various",
                "citation": "Wang et al. (2019). GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding."
            },
            "gsm8k": {
                "name": "GSM8K",
                "description": "Grade School Math 8K problems",
                "source": "https://github.com/openai/grade-school-math",
                "format": "jsonl",
                "metrics": ["accuracy", "exact_match"],
                "license": "MIT",
                "citation": "Cobbe et al. (2021). Training Verifiers to Solve Math Word Problems."
            },
            "arc": {
                "name": "ARC",
                "description": "AI2 Reasoning Challenge",
                "source": "https://github.com/allenai/arc",
                "format": "jsonl",
                "metrics": ["accuracy", "exact_match"],
                "license": "Apache 2.0",
                "citation": "Clark et al. (2018). Think you have solved question answering? Try ARC, the AI2 reasoning challenge."
            },
            "hellaswag": {
                "name": "HellaSwag",
                "description": "Commonsense reasoning with multiple choice questions",
                "source": "https://github.com/rowanz/hellaswag",
                "format": "jsonl",
                "metrics": ["accuracy", "exact_match"],
                "license": "MIT",
                "citation": "Zellers et al. (2019). HellaSwag: Can a Machine Really Finish Your Sentence?"
            }
        }
    
    def is_supported(self, benchmark_name: str) -> bool:
        """Check if a benchmark is supported."""
        return benchmark_name in self.supported_benchmarks
    
    def list_supported(self) -> List[str]:
        """List all supported public benchmarks."""
        return list(self.supported_benchmarks.keys())
    
    def get_benchmark_info(self, benchmark_name: str) -> Dict[str, Any]:
        """Get information about a public benchmark."""
        if not self.is_supported(benchmark_name):
            raise ValueError(f"Unsupported public benchmark: {benchmark_name}")
        return self.supported_benchmarks[benchmark_name]
    
    def load_benchmark(self, benchmark_name: str) -> BenchmarkDefinition:
        """Load a publicly available benchmark."""
        if not self.is_supported(benchmark_name):
            raise ValueError(f"Unsupported public benchmark: {benchmark_name}")
        
        benchmark_info = self.supported_benchmarks[benchmark_name]
        
        # Check if already cached
        cache_path = self.cache_dir / f"{benchmark_name}_{benchmark_info.get('version', 'latest')}"
        if cache_path.exists():
            logger.info(f"Loading cached benchmark: {benchmark_name}")
            return self._load_from_cache(cache_path, benchmark_info)
        
        # Download and cache the benchmark
        logger.info(f"Downloading benchmark: {benchmark_name}")
        samples = self._download_benchmark(benchmark_name, benchmark_info)
        
        # Create benchmark definition
        benchmark_def = BenchmarkDefinition(
            name=benchmark_name,
            description=benchmark_info["description"],
            samples=samples,
            metrics=benchmark_info["metrics"],
            metadata={
                "source": benchmark_info["source"],
                "format": benchmark_info["format"],
                "license": benchmark_info["license"],
                "citation": benchmark_info["citation"],
                "version": benchmark_info.get("version", "latest")
            },
            benchmark_type="public"
        )
        
        # Cache the benchmark
        self._cache_benchmark(cache_path, benchmark_def)
        
        return benchmark_def
    
    def _download_benchmark(self, benchmark_name: str, benchmark_info: Dict[str, Any]) -> List[SampleData]:
        """Download benchmark data from source."""
        source = benchmark_info["source"]
        format_type = benchmark_info["format"]
        
        if source.startswith("https://github.com/"):
            return self._download_from_github(source, benchmark_name, format_type)
        elif source.startswith("https://huggingface.co/"):
            return self._download_from_huggingface(source, benchmark_name, format_type)
        else:
            raise ValueError(f"Unsupported source: {source}")
    
    def _download_from_github(self, source: str, benchmark_name: str, format_type: str) -> List[SampleData]:
        """Download benchmark from GitHub repository."""
        # For now, we'll create mock data for demonstration
        # In a real implementation, this would download from GitHub
        logger.warning(f"Mock download from GitHub: {source}")
        return self._create_mock_samples(benchmark_name, format_type)
    
    def _download_from_huggingface(self, source: str, benchmark_name: str, format_type: str) -> List[SampleData]:
        """Download benchmark from Hugging Face."""
        # For now, we'll create mock data for demonstration
        # In a real implementation, this would download from Hugging Face
        logger.warning(f"Mock download from Hugging Face: {source}")
        return self._create_mock_samples(benchmark_name, format_type)
    
    def _create_mock_samples(self, benchmark_name: str, format_type: str) -> List[SampleData]:
        """Create mock samples for demonstration purposes."""
        samples = []
        
        if benchmark_name == "humaneval":
            # Mock HumanEval samples
            for i in range(5):
                samples.append(SampleData(
                    input_text=f"def problem_{i}():\n    \"\"\"Write a function that returns {i}.\"\"\"\n    pass",
                    expected_output=f"def problem_{i}():\n    return {i}",
                    metadata={"problem_id": f"problem_{i}", "difficulty": "medium"},
                    category="code_generation"
                ))
        
        elif benchmark_name == "glue":
            # Mock GLUE samples
            glue_tasks = [
                ("The movie was great!", "positive"),
                ("I hate this book.", "negative"),
                ("The weather is okay.", "neutral")
            ]
            for text, label in glue_tasks:
                samples.append(SampleData(
                    input_text=text,
                    expected_output=label,
                    metadata={"task": "sentiment_analysis"},
                    category="text_classification"
                ))
        
        elif benchmark_name == "gsm8k":
            # Mock GSM8K samples
            math_problems = [
                "Sarah has 12 apples. She gives 3 to her friend. How many apples does she have left?",
                "A store has 24 books. They sell 8 books. How many books are left?",
                "Tom has 15 marbles. He finds 7 more. How many marbles does he have now?"
            ]
            for problem in math_problems:
                samples.append(SampleData(
                    input_text=problem,
                    expected_output="9",  # Mock answer
                    metadata={"domain": "arithmetic"},
                    category="math_reasoning"
                ))
        
        else:
            # Generic mock samples
            for i in range(3):
                samples.append(SampleData(
                    input_text=f"Sample input {i+1}",
                    expected_output=f"Sample output {i+1}",
                    metadata={"benchmark": benchmark_name},
                    category="general"
                ))
        
        return samples
    
    def _load_from_cache(self, cache_path: Path, benchmark_info: Dict[str, Any]) -> BenchmarkDefinition:
        """Load benchmark from cache."""
        try:
            with open(cache_path / "benchmark.json", "r") as f:
                data = json.load(f)
            
            # Convert samples back to SampleData objects
            samples = []
            for sample_data in data["samples"]:
                samples.append(SampleData(
                    input_text=sample_data["input_text"],
                    expected_output=sample_data.get("expected_output"),
                    metadata=sample_data.get("metadata", {}),
                    category=sample_data.get("category"),
                    difficulty=sample_data.get("difficulty")
                ))
            
            return BenchmarkDefinition(
                name=data["name"],
                description=data["description"],
                samples=samples,
                metrics=data["metrics"],
                evaluation_criteria=data.get("evaluation_criteria"),
                metadata=data.get("metadata", {}),
                benchmark_type=data.get("benchmark_type", "public")
            )
        except Exception as e:
            logger.error(f"Failed to load from cache: {e}")
            raise
    
    def _cache_benchmark(self, cache_path: Path, benchmark_def: BenchmarkDefinition):
        """Cache benchmark definition."""
        cache_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        data = {
            "name": benchmark_def.name,
            "description": benchmark_def.description,
            "samples": [
                {
                    "input_text": sample.input_text,
                    "expected_output": sample.expected_output,
                    "metadata": sample.metadata or {},
                    "category": sample.category,
                    "difficulty": sample.difficulty
                }
                for sample in benchmark_def.samples
            ],
            "metrics": benchmark_def.metrics,
            "evaluation_criteria": benchmark_def.evaluation_criteria,
            "metadata": benchmark_def.metadata or {},
            "benchmark_type": benchmark_def.benchmark_type
        }
        
        with open(cache_path / "benchmark.json", "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Cached benchmark: {benchmark_def.name}")
