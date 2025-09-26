"""Web scraping tool using Playwright for JavaScript-rendered content."""

import asyncio
import logging
from typing import Optional, ClassVar

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


logger = logging.getLogger(__name__)


class WebScraperTool(BaseTool):
    """Tool for scraping web content using Playwright."""

    name: str = "web_scraper"
    description: str = (
        "Scrapes web content from URLs, including JavaScript-rendered pages. "
        "Returns cleaned text content suitable for analysis."
    )

    # Configuration constants
    TIMEOUT_SECONDS: ClassVar[int] = 180
    MAX_CONTENT_SIZE_MB: ClassVar[int] = 10

    def _run(self, url: str) -> str:
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

                # Set timeout and navigate to URL
                page.set_default_timeout(self.TIMEOUT_SECONDS * 1000)  # Playwright uses milliseconds

                try:
                    response = await page.goto(url, wait_until="domcontentloaded")

                    if not response or not response.ok:
                        error_msg = f"Failed to load page. Status: {response.status if response else 'No response'}"
                        logger.error(error_msg)
                        return f"ERROR: {error_msg}"

                    # Wait for any dynamic content to load
                    await page.wait_for_timeout(2000)  # 2 seconds

                    # Get page content
                    content = await page.content()

                    # Check content size
                    if len(content.encode('utf-8')) > (self.MAX_CONTENT_SIZE_MB * 1024 * 1024):
                        logger.warning(f"Content size exceeds limit for {url}")
                        return "ERROR: Content size exceeds 10MB limit"

                    # Extract and clean text content
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

            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
                element.decompose()

            # Extract text from main content areas
            main_content = ""

            # Try to find main content areas
            main_selectors = ['main', '[role="main"]', '.content', '.post-content', '.article-content', '.entry-content']

            for selector in main_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    main_content = main_element.get_text(separator=' ', strip=True)
                    break

            # Fallback to body content if no main content area found
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator=' ', strip=True)

            # Clean up the text
            lines = main_content.split('\n')
            cleaned_lines = []

            for line in lines:
                line = line.strip()
                if line and len(line) > 10:  # Skip very short lines
                    cleaned_lines.append(line)

            cleaned_content = '\n'.join(cleaned_lines)

            # Limit content length for processing
            if len(cleaned_content) > 50000:  # ~50k characters should be plenty
                cleaned_content = cleaned_content[:50000] + "..."
                logger.info("Content truncated to 50k characters for processing")

            return cleaned_content

        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return f"ERROR: Failed to extract text content: {str(e)}"