"""
Benchmark manager for evaluation benchmarks.
"""

from typing import Dict, List, Optional
from ..core.data_models import BenchmarkDefinition, SampleData


class BenchmarkManager:
    """Manages available benchmarks for evaluation."""
    
    def __init__(self):
        """Initialize benchmark manager."""
        self._benchmarks = {}
        self._predefined_benchmarks = PredefinedBenchmarks()
        self._load_predefined_benchmarks()
    
    def _load_predefined_benchmarks(self):
        """Load predefined benchmarks."""
        predefined = self._predefined_benchmarks.get_all_benchmarks()
        self._benchmarks.update(predefined)
    
    def get_benchmark(self, name: str) -> Optional[BenchmarkDefinition]:
        """Get benchmark by name."""
        return self._benchmarks.get(name)
    
    def get_available_benchmarks(self) -> List[str]:
        """Get list of available benchmark names."""
        return list(self._benchmarks.keys())
    
    def register_benchmark(self, benchmark: BenchmarkDefinition) -> bool:
        """Register a custom benchmark."""
        try:
            self._benchmarks[benchmark.name] = benchmark
            return True
        except Exception:
            return False
    
    def create_custom_benchmark(
        self, 
        name: str, 
        samples: List[SampleData],
        metrics: List[str],
        description: str = ""
    ) -> BenchmarkDefinition:
        """Create a custom benchmark."""
        benchmark = BenchmarkDefinition(
            name=name,
            description=description,
            samples=samples,
            metrics=metrics
        )
        
        self.register_benchmark(benchmark)
        return benchmark


class PredefinedBenchmarks:
    """Predefined benchmark definitions."""
    
    def get_all_benchmarks(self) -> Dict[str, BenchmarkDefinition]:
        """Get all predefined benchmarks."""
        benchmarks = {}
        
        # Basic QA benchmark
        benchmarks["basic_qa"] = self._create_basic_qa_benchmark()
        
        # Math benchmark
        benchmarks["math"] = self._create_math_benchmark()
        
        # Creative writing benchmark
        benchmarks["creative_writing"] = self._create_creative_writing_benchmark()
        
        # Code generation benchmark
        benchmarks["code_generation"] = self._create_code_generation_benchmark()
        
        return benchmarks
    
    def _create_basic_qa_benchmark(self) -> BenchmarkDefinition:
        """Create basic Q&A benchmark."""
        samples = [
            SampleData(
                input_text="What is the capital of France?",
                expected_output="Paris",
                difficulty="easy",
                category="geography"
            ),
            SampleData(
                input_text="Who wrote 'To Kill a Mockingbird'?",
                expected_output="Harper Lee",
                difficulty="easy",
                category="literature"
            ),
            SampleData(
                input_text="What is the largest planet in our solar system?",
                expected_output="Jupiter",
                difficulty="easy",
                category="science"
            ),
            SampleData(
                input_text="In what year did World War II end?",
                expected_output="1945",
                difficulty="medium",
                category="history"
            ),
            SampleData(
                input_text="What is the chemical symbol for gold?",
                expected_output="Au",
                difficulty="medium",
                category="science"
            )
        ]
        
        return BenchmarkDefinition(
            name="basic_qa",
            description="Basic question and answer benchmark",
            samples=samples,
            metrics=["accuracy", "response_time", "quality_score"]
        )
    
    def _create_math_benchmark(self) -> BenchmarkDefinition:
        """Create math benchmark."""
        samples = [
            SampleData(
                input_text="What is 15 + 27?",
                expected_output="42",
                difficulty="easy",
                category="arithmetic"
            ),
            SampleData(
                input_text="Solve for x: 2x + 5 = 13",
                expected_output="x = 4",
                difficulty="medium",
                category="algebra"
            ),
            SampleData(
                input_text="What is the area of a circle with radius 5?",
                expected_output="78.54 or 25π",
                difficulty="medium",
                category="geometry"
            ),
            SampleData(
                input_text="What is the derivative of x²?",
                expected_output="2x",
                difficulty="hard",
                category="calculus"
            ),
            SampleData(
                input_text="What is 7! (7 factorial)?",
                expected_output="5040",
                difficulty="medium",
                category="combinatorics"
            )
        ]
        
        return BenchmarkDefinition(
            name="math",
            description="Mathematics benchmark",
            samples=samples,
            metrics=["accuracy", "response_time", "quality_score"]
        )
    
    def _create_creative_writing_benchmark(self) -> BenchmarkDefinition:
        """Create creative writing benchmark."""
        samples = [
            SampleData(
                input_text="Write a haiku about the ocean.",
                expected_output=None,
                difficulty="medium",
                category="poetry"
            ),
            SampleData(
                input_text="Write a short story about a robot learning to love.",
                expected_output=None,
                difficulty="hard",
                category="fiction"
            ),
            SampleData(
                input_text="Describe a sunset in three sentences.",
                expected_output=None,
                difficulty="easy",
                category="descriptive"
            ),
            SampleData(
                input_text="Write a dialogue between two characters meeting for the first time.",
                expected_output=None,
                difficulty="medium",
                category="dialogue"
            ),
            SampleData(
                input_text="Create a product description for a magical coffee mug.",
                expected_output=None,
                difficulty="medium",
                category="marketing"
            )
        ]
        
        return BenchmarkDefinition(
            name="creative_writing",
            description="Creative writing benchmark",
            samples=samples,
            metrics=["quality_score", "coherence_score", "creativity_score"]
        )
    
    def _create_code_generation_benchmark(self) -> BenchmarkDefinition:
        """Create code generation benchmark."""
        samples = [
            SampleData(
                input_text="Write a Python function to calculate the factorial of a number.",
                expected_output="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
                difficulty="medium",
                category="python"
            ),
            SampleData(
                input_text="Create a JavaScript function to reverse a string.",
                expected_output="function reverseString(str) {\n    return str.split('').reverse().join('');\n}",
                difficulty="easy",
                category="javascript"
            ),
            SampleData(
                input_text="Write a SQL query to find all users with age greater than 25.",
                expected_output="SELECT * FROM users WHERE age > 25;",
                difficulty="easy",
                category="sql"
            ),
            SampleData(
                input_text="Create a CSS class for a responsive navigation bar.",
                expected_output=".nav-bar {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    padding: 1rem;\n}\n\n@media (max-width: 768px) {\n    .nav-bar {\n        flex-direction: column;\n    }\n}",
                difficulty="medium",
                category="css"
            ),
            SampleData(
                input_text="Write a Python class for a simple bank account.",
                expected_output="class BankAccount:\n    def __init__(self, balance=0):\n        self.balance = balance\n    \n    def deposit(self, amount):\n        self.balance += amount\n    \n    def withdraw(self, amount):\n        if amount <= self.balance:\n            self.balance -= amount\n        else:\n            raise ValueError('Insufficient funds')",
                difficulty="hard",
                category="oop"
            )
        ]
        
        return BenchmarkDefinition(
            name="code_generation",
            description="Code generation benchmark",
            samples=samples,
            metrics=["accuracy", "code_quality", "syntax_correctness"]
        )


class CustomBenchmark:
    """Custom benchmark implementation."""
    
    def __init__(self, name: str, samples: List[SampleData], metrics: List[str]):
        """Initialize custom benchmark."""
        self.name = name
        self.samples = samples
        self.metrics = metrics
    
    def to_definition(self) -> BenchmarkDefinition:
        """Convert to benchmark definition."""
        return BenchmarkDefinition(
            name=self.name,
            description=f"Custom benchmark: {self.name}",
            samples=self.samples,
            metrics=self.metrics
        )
