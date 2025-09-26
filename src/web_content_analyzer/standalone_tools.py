"""Standalone tools that don't depend on CrewAI."""

import asyncio
import logging
import re
from typing import List, Optional

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from anthropic import Anthropic


logger = logging.getLogger(__name__)


class StandaloneWebScraper:
    """Standalone web scraper using Playwright."""

    def __init__(self, timeout_seconds: int = 180, max_content_size_mb: int = 10):
        self.timeout_seconds = timeout_seconds
        self.max_content_size_bytes = max_content_size_mb * 1024 * 1024

    def scrape(self, url: str) -> str:
        """Scrape content from the given URL."""
        return asyncio.run(self._scrape_url(url))

    async def _scrape_url(self, url: str) -> str:
        """Async method to scrape content from URL using Playwright."""
        logger.info(f"Starting to scrape URL: {url}")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )

                page = await context.new_page()
                page.set_default_timeout(self.timeout_seconds * 1000)

                try:
                    response = await page.goto(url, wait_until="domcontentloaded")

                    if not response or not response.ok:
                        error_msg = f"Failed to load page. Status: {response.status if response else 'No response'}"
                        logger.error(error_msg)
                        return f"ERROR: {error_msg}"

                    await page.wait_for_timeout(2000)  # Wait 2 seconds for dynamic content
                    content = await page.content()

                    if len(content.encode('utf-8')) > self.max_content_size_bytes:
                        logger.warning(f"Content size exceeds limit for {url}")
                        return "ERROR: Content size exceeds 10MB limit"

                    cleaned_content = self._extract_text_content(content)
                    logger.info(f"Successfully scraped {len(cleaned_content)} characters from {url}")
                    return cleaned_content

                except Exception as e:
                    error_msg = f"Error during page scraping: {str(e)}"
                    logger.error(error_msg)
                    return f"ERROR: {error_msg}"

                finally:
                    await browser.close()

        except Exception as e:
            error_msg = f"Error setting up browser: {str(e)}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"

    def _extract_text_content(self, html_content: str) -> str:
        """Extract and clean text content from HTML using BeautifulSoup."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
                element.decompose()

            # Find main content
            main_content = ""
            main_selectors = ['main', '[role="main"]', '.content', '.post-content', '.article-content', '.entry-content']

            for selector in main_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    main_content = main_element.get_text(separator=' ', strip=True)
                    break

            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator=' ', strip=True)

            # Clean up the text
            lines = main_content.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
            cleaned_content = '\n'.join(cleaned_lines)

            # Limit content length
            if len(cleaned_content) > 50000:
                cleaned_content = cleaned_content[:50000] + "..."
                logger.info("Content truncated to 50k characters for processing")

            return cleaned_content

        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return f"ERROR: Failed to extract text content: {str(e)}"


class StandaloneContentAnalyzer:
    """Standalone content analyzer using Claude API directly."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def analyze(self, content: str) -> str:
        """Analyze the given content and return insights."""
        if content.startswith("ERROR:"):
            return content

        logger.info(f"Analyzing content ({len(content)} characters)")

        try:
            analysis_prompt = self._create_analysis_prompt(content)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": analysis_prompt}]
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


class StandaloneKeywordExtractor:
    """Standalone keyword extractor."""

    def extract(self, analysis_result: str) -> str:
        """Extract top 10 keywords from the analysis result."""
        if analysis_result.startswith("ERROR:"):
            return analysis_result

        logger.info("Extracting keywords from analysis result")

        try:
            keywords = self._extract_keywords_from_analysis(analysis_result)
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

        # Clean and limit to 10
        final_keywords = []
        for keyword in unique_keywords[:10]:
            cleaned = self._clean_keyword(keyword)
            if cleaned and len(cleaned) > 2:
                final_keywords.append(cleaned)

        return final_keywords[:10]

    def _extract_from_section(self, content: str, section_type: str) -> List[str]:
        """Extract keywords from a specific section."""
        keywords = []
        items = re.split(r'[,\n\-\•\*]', content)

        for item in items:
            item = item.strip()
            if not item or len(item) < 3 or len(item) > 50:
                continue

            # Remove numbering and bullet points
            item = re.sub(r'^\d+\.\s*', '', item)
            item = re.sub(r'^[•\-\*]\s*', '', item)
            item = item.strip()

            if section_type == 'named_entities':
                if item[0].isupper() or any(word[0].isupper() for word in item.split() if len(word) > 2):
                    keywords.append(item)
            else:
                words = item.split()
                if 1 <= len(words) <= 4:
                    keywords.append(item)

        return keywords

    def _clean_keyword(self, keyword: str) -> str:
        """Clean and normalize a keyword."""
        keyword = re.sub(r'\s+', ' ', keyword.strip())
        keyword = re.sub(r'^[^\w]+|[^\w]+$', '', keyword)

        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = keyword.split()

        while words and words[0].lower() in stop_words:
            words = words[1:]
        while words and words[-1].lower() in stop_words:
            words = words[:-1]

        keyword = ' '.join(words)

        if any(c.isupper() for c in keyword):
            return keyword  # Keep original capitalization for proper nouns
        else:
            return keyword.lower()  # Convert to lowercase for common terms