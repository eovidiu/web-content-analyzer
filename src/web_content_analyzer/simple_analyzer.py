"""Simple analyzer that bypasses CrewAI's LLM issues and uses tools directly."""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from .config import Config
from .standalone_tools import StandaloneWebScraper, StandaloneContentAnalyzer, StandaloneKeywordExtractor


logger = logging.getLogger(__name__)


class SimpleWebContentAnalyzer:
    """Direct tool-based analyzer that bypasses CrewAI's LLM configuration issues."""

    def __init__(self, config: Config):
        self.config = config
        self.scraper = StandaloneWebScraper(
            timeout_seconds=config.timeout_seconds,
            max_content_size_mb=config.max_content_size_mb
        )
        self.analyzer = StandaloneContentAnalyzer(api_key=config.anthropic_api_key)
        self.extractor = StandaloneKeywordExtractor()

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """Analyze a single URL and return results."""
        start_time = time.time()

        try:
            logger.info(f"Starting analysis of URL: {url}")

            # Step 1: Scrape content
            logger.info("Step 1: Scraping web content...")
            content = self.scraper.scrape(url)
            if content.startswith("ERROR:"):
                raise Exception(f"Scraping failed: {content}")

            # Step 2: Analyze content
            logger.info("Step 2: Analyzing content with Claude API...")
            # Limit content size for analysis (first 10k characters should be enough)
            analysis_content = content[:10000] if len(content) > 10000 else content
            analysis = self.analyzer.analyze(analysis_content)
            if analysis.startswith("ERROR:"):
                raise Exception(f"Analysis failed: {analysis}")

            # Step 3: Extract keywords
            logger.info("Step 3: Extracting keywords...")
            keywords_result = self.extractor.extract(analysis)
            if keywords_result.startswith("ERROR:"):
                raise Exception(f"Keyword extraction failed: {keywords_result}")

            # Parse keywords from result
            keywords = self._parse_keywords_from_result(keywords_result)

            processing_time = time.time() - start_time
            logger.info(f"Analysis completed successfully in {processing_time:.2f}s")

            return {
                "url": url,
                "status": "success",
                "processing_time": processing_time,
                "keywords": keywords
            }

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error analyzing {url}: {error_msg}")

            return {
                "url": url,
                "status": "failed",
                "processing_time": processing_time,
                "error": error_msg,
                "keywords": []
            }

    def analyze_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple URLs in parallel."""
        logger.info(f"Starting batch analysis of {len(urls)} URLs with {self.config.parallel_limit} workers")

        results = []

        with ThreadPoolExecutor(max_workers=self.config.parallel_limit) as executor:
            # Submit all URL analysis tasks
            future_to_url = {
                executor.submit(self._analyze_single_url_with_retry, url): url
                for url in urls
            }

            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed analysis for {url} - Status: {result['status']}")
                except Exception as e:
                    error_result = {
                        "url": url,
                        "status": "failed",
                        "processing_time": 0,
                        "error": f"Unexpected error: {str(e)}",
                        "keywords": []
                    }
                    results.append(error_result)
                    logger.error(f"Unexpected error for {url}: {str(e)}")

        # Sort results to match original URL order
        url_to_result = {result["url"]: result for result in results}
        ordered_results = [url_to_result.get(url, {"url": url, "status": "failed", "error": "No result found"}) for url in urls]

        logger.info(f"Batch analysis complete: {sum(1 for r in results if r['status'] == 'success')} successful, "
                   f"{sum(1 for r in results if r['status'] == 'failed')} failed")

        return ordered_results

    def _analyze_single_url_with_retry(self, url: str) -> Dict[str, Any]:
        """Analyze a single URL with retry logic."""
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                result = self.analyze_url(url)
                if result["status"] == "success":
                    return result
                else:
                    last_error = result["error"]

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {last_error}")

            # Wait before retry (except on last attempt)
            if attempt < self.config.max_retries - 1:
                time.sleep(self.config.retry_delay_seconds)

        # All attempts failed
        return {
            "url": url,
            "status": "failed",
            "processing_time": 0,
            "error": f"Failed after {self.config.max_retries} attempts. Last error: {last_error}",
            "keywords": []
        }

    def _parse_keywords_from_result(self, result_text: str) -> List[str]:
        """Parse keywords from the keyword extraction result."""
        keywords = []

        try:
            lines = result_text.split('\n')

            # Look for the "TOP 10 KEYWORDS:" section
            in_keywords_section = False
            for line in lines:
                line = line.strip()

                if "TOP 10 KEYWORDS:" in line.upper():
                    in_keywords_section = True
                    continue

                if in_keywords_section and line:
                    # Parse numbered keyword lines (e.g., " 1. keyword")
                    import re
                    match = re.match(r'\s*\d+\.\s*(.+)', line)
                    if match:
                        keyword = match.group(1).strip()
                        if keyword:
                            keywords.append(keyword)
                    elif line.startswith('ERROR:'):
                        logger.error(f"Error in keyword extraction: {line}")
                        break

        except Exception as e:
            logger.error(f"Error parsing keywords from result: {str(e)}")

        return keywords[:10]  # Ensure we return at most 10 keywords