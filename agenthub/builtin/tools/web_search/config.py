"""
Configuration and constants for web search tool
"""

from dataclasses import dataclass, field


@dataclass
class WebSearchConfig:
    """Configuration for web search tool"""

    max_results: int = 10
    timeout: int = 10
    max_content_length: int = 5000
    exclude_domains: list[str] = field(default_factory=list)
    enable_query_rewriting: bool = True
    enable_content_extraction: bool = True

    def __post_init__(self) -> None:
        if not self.exclude_domains:
            self.exclude_domains = []
