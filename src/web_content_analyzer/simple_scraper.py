"""Simple HTTP-based web scraper as fallback when Playwright fails."""

import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class SimpleHttpScraper:
    """HTTP-based scraper that works without browser dependencies."""

    def __init__(self, timeout_seconds=30):
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape(self, url: str) -> str:
        """Scrape content from URL using HTTP requests."""
        try:
            logger.info(f"HTTP scraping URL: {url}")

            # Make HTTP request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            logger.info(f"HTTP scraped {len(text)} characters from {url}")
            return text

        except requests.RequestException as e:
            error_msg = f"ERROR: HTTP request failed: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"ERROR: Scraping failed: {str(e)}"
            logger.error(error_msg)
            return error_msg