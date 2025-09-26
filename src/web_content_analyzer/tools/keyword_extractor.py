"""Keyword extraction tool that processes content analysis results."""

import logging
import re
from typing import List

from crewai.tools import BaseTool


logger = logging.getLogger(__name__)


class KeywordExtractorTool(BaseTool):
    """Tool for extracting the top 10 keywords from content analysis."""


    name: str = "keyword_extractor"
    description: str = (
        "Extracts and ranks the top 10 most representative keywords from "
        "content analysis results, focusing on themes, technical terms, and entities."
    )

    def _run(self, analysis_result: str) -> str:
        """Extract top 10 keywords from the analysis result."""
        if analysis_result.startswith("ERROR:"):
            return analysis_result  # Pass through errors from previous step

        logger.info("Extracting keywords from analysis result")

        try:
            keywords = self._extract_keywords_from_analysis(analysis_result)

            # Return keywords as a formatted string
            result = "TOP 10 KEYWORDS:\n"
            for i, keyword in enumerate(keywords, 1):
                result += f"{i:2d}. {keyword}\n"

            logger.info(f"Successfully extracted {len(keywords)} keywords")
            return result.strip()

        except Exception as e:
            error_msg = f"Error during keyword extraction: {str(e)}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"

    def _extract_keywords_from_analysis(self, analysis: str) -> List[str]:
        """Extract keywords from the structured analysis result."""
        keywords = []

        # Extract from different sections of the analysis
        sections = {
            'main_topics': r"## Main Topics\s*(.*?)(?=##|\Z)",
            'technical_terms': r"## Technical Terms & Concepts\s*(.*?)(?=##|\Z)",
            'named_entities': r"## Named Entities\s*(.*?)(?=##|\Z)",
            'themes': r"## Key Themes & Messages\s*(.*?)(?=##|\Z)",
            'domain': r"## Context & Domain\s*(.*?)(?=##|\Z)"
        }

        for section_name, pattern in sections.items():
            match = re.search(pattern, analysis, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(1).strip()
                section_keywords = self._extract_from_section(section_content, section_name)
                keywords.extend(section_keywords)

        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(keyword)

        # Limit to top 10 and clean up
        final_keywords = []
        for keyword in unique_keywords[:10]:
            cleaned = self._clean_keyword(keyword)
            if cleaned and len(cleaned) > 2:
                final_keywords.append(cleaned)

        # Ensure we have exactly 10 keywords (pad if necessary)
        while len(final_keywords) < 10 and len(unique_keywords) > len(final_keywords):
            for keyword in unique_keywords[len(final_keywords):]:
                cleaned = self._clean_keyword(keyword)
                if cleaned and len(cleaned) > 2 and cleaned not in final_keywords:
                    final_keywords.append(cleaned)
                    if len(final_keywords) == 10:
                        break

        return final_keywords[:10]  # Ensure exactly 10 or fewer

    def _extract_from_section(self, content: str, section_type: str) -> List[str]:
        """Extract keywords from a specific section of the analysis."""
        keywords = []

        # Split by common delimiters
        items = re.split(r'[,\n\-\•\*]', content)

        for item in items:
            item = item.strip()
            if not item:
                continue

            # Remove numbering and bullet points
            item = re.sub(r'^\d+\.\s*', '', item)
            item = re.sub(r'^[•\-\*]\s*', '', item)
            item = item.strip()

            if len(item) < 3 or len(item) > 50:
                continue

            # For different section types, extract differently
            if section_type == 'named_entities':
                # Extract proper nouns and company names
                if item[0].isupper() or any(word[0].isupper() for word in item.split() if len(word) > 2):
                    keywords.append(item)
            elif section_type == 'technical_terms':
                # Look for technical terminology
                keywords.append(item)
            else:
                # Extract noun phrases and important terms
                words = item.split()
                if 1 <= len(words) <= 4:  # Prefer 1-4 word phrases
                    keywords.append(item)

        return keywords

    def _clean_keyword(self, keyword: str) -> str:
        """Clean and normalize a keyword."""
        # Remove extra whitespace and punctuation
        keyword = re.sub(r'\s+', ' ', keyword.strip())
        keyword = re.sub(r'^[^\w]+|[^\w]+$', '', keyword)

        # Remove common stop words at the beginning
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = keyword.split()

        while words and words[0].lower() in stop_words:
            words = words[1:]

        while words and words[-1].lower() in stop_words:
            words = words[:-1]

        keyword = ' '.join(words)

        # Capitalize properly
        if keyword:
            # Check if it's likely a proper noun (contains uppercase letters)
            if any(c.isupper() for c in keyword):
                return keyword  # Keep original capitalization
            else:
                return keyword.lower()  # Convert to lowercase for common terms

        return keyword