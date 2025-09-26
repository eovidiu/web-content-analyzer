"""Configuration management for Web Content Analyzer."""

import os
import logging
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration settings for the Web Content Analyzer."""

    anthropic_api_key: Optional[str] = None
    verbose: bool = False
    parallel_limit: int = 3
    timeout_seconds: int = 180  # 3 minutes
    max_content_size_mb: int = 10
    max_retries: int = 3
    retry_delay_seconds: int = 2

    def __post_init__(self):
        """Initialize configuration from environment variables."""
        self.anthropic_api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )

        if self.parallel_limit < 1 or self.parallel_limit > 10:
            raise ValueError("Parallel limit must be between 1 and 10")

        if self.timeout_seconds < 30 or self.timeout_seconds > 600:
            raise ValueError("Timeout must be between 30 and 600 seconds")

        if self.max_content_size_mb < 1 or self.max_content_size_mb > 100:
            raise ValueError("Max content size must be between 1 and 100 MB")