"""Content analysis tool using Claude API."""

import logging
from typing import Dict, Any

from anthropic import Anthropic
from crewai.tools import BaseTool


logger = logging.getLogger(__name__)


class ContentAnalyzerTool(BaseTool):
    """Tool for analyzing web content using Claude API."""

    name: str = "content_analyzer"
    description: str = (
        "Analyzes web content using Claude API to understand themes, topics, "
        "and extract meaningful insights suitable for keyword extraction."
    )

    def __init__(self, api_key: str):
        super().__init__()
        self._client = Anthropic(api_key=api_key)

    def _run(self, content: str) -> str:
        """Analyze the given content and return insights."""
        if content.startswith("ERROR:"):
            return content  # Pass through errors from previous step

        logger.info(f"Analyzing content ({len(content)} characters)")

        try:
            # Prepare the analysis prompt
            analysis_prompt = self._create_analysis_prompt(content)

            response = self._client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1500,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )

            analysis_result = response.content[0].text

            logger.info("Successfully analyzed content with Claude API")
            return analysis_result

        except Exception as e:
            error_msg = f"Error during content analysis: {str(e)}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"

    def _create_analysis_prompt(self, content: str) -> str:
        """Create a detailed prompt for content analysis."""
        return f"""Analyze the following web content and provide a comprehensive analysis focused on identifying key themes, topics, and concepts that would be useful for keyword extraction.

Web Content:
{content}

Please provide your analysis in the following structured format:

## Main Topics
List the 3-5 primary topics or themes discussed in this content.

## Technical Terms & Concepts
Identify important technical terms, jargon, or specialized concepts mentioned.

## Named Entities
List significant people, organizations, products, or locations mentioned.

## Key Themes & Messages
Describe the main messages, arguments, or points being communicated.

## Content Category
Categorize this content (e.g., news article, blog post, product page, documentation, etc.)

## Context & Domain
What domain or industry does this content relate to?

Be thorough but concise. Focus on elements that would help identify the most representative keywords for this content."""