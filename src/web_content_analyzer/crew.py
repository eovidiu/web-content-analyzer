"""Main CrewAI orchestration for Web Content Analyzer."""

import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from crewai import Crew, Task

from .config import Config
from .agents import (
    create_web_scraper_agent,
    create_content_analyzer_agent,
    create_keyword_extractor_agent
)


logger = logging.getLogger(__name__)


class WebContentAnalyzer:
    """Main class for orchestrating web content analysis using CrewAI."""

    def __init__(self, config: Config):
        self.config = config
        self.crew = self._create_crew()

    def _create_crew(self) -> Crew:
        """Create and configure the CrewAI crew with agents."""
        # Create specialized agents
        self.web_scraper = create_web_scraper_agent(self.config)
        self.content_analyzer = create_content_analyzer_agent(self.config)
        self.keyword_extractor = create_keyword_extractor_agent(self.config)

        # Tasks will be created dynamically for each analysis
        # Return None for now, we'll create the crew when needed
        return None

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """Analyze a single URL and return results."""
        start_time = time.time()

        try:
            logger.info(f"Starting analysis of URL: {url}")

            # Create tasks for sequential processing
            scraping_task = Task(
                description=f"Scrape and extract clean text content from the URL: {url}",
                agent=self.web_scraper,
                expected_output="Clean, readable text content from the web page"
            )

            analysis_task = Task(
                description="Analyze the scraped content to understand main themes, topics, and key concepts",
                agent=self.content_analyzer,
                expected_output="Structured analysis of content themes, topics, technical terms, and entities",
                context=[scraping_task]
            )

            extraction_task = Task(
                description="Extract and rank the top 10 most representative keywords from the analysis",
                agent=self.keyword_extractor,
                expected_output="List of exactly 10 keywords that best characterize the content",
                context=[analysis_task]
            )

            # Create crew with tasks and agents
            from crewai import LLM
            crew_llm = LLM(
                model="claude-3-5-sonnet-latest",
                api_key=self.config.anthropic_api_key
            )

            crew = Crew(
                agents=[self.web_scraper, self.content_analyzer, self.keyword_extractor],
                tasks=[scraping_task, analysis_task, extraction_task],
                verbose=self.config.verbose,
                memory=False,
                manager_llm=crew_llm
            )

            # Execute the crew
            result = crew.kickoff()

            processing_time = time.time() - start_time

            # Parse the keywords from the result
            keywords = self._parse_keywords_from_result(str(result))

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
        """Parse keywords from the crew execution result."""
        keywords = []

        try:
            # The result should contain the keyword extraction output
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

            # Fallback: if we didn't find the structured format, try to extract any keywords
            if not keywords and not result_text.startswith("ERROR:"):
                logger.warning("Could not parse structured keyword output, attempting fallback extraction")
                # Simple fallback - just take the last part of the result
                words = result_text.split()[-20:]  # Last 20 words as potential keywords
                keywords = [word.strip('.,!?') for word in words if len(word) > 3][:10]

        except Exception as e:
            logger.error(f"Error parsing keywords from result: {str(e)}")

        return keywords[:10]  # Ensure we return at most 10 keywords