#!/usr/bin/env python3
"""Simple test script to verify our tools work independently."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_content_analyzer.tools.web_scraper import WebScraperTool
from web_content_analyzer.tools.content_analyzer import ContentAnalyzerTool
from web_content_analyzer.tools.keyword_extractor import KeywordExtractorTool


def main():
    """Test the tools directly without CrewAI."""
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        return 1

    url = "https://example.com"
    print(f"Testing tools with URL: {url}")

    try:
        # Step 1: Web scraping
        print("\n1. Testing web scraper...")
        scraper = WebScraperTool()
        content = scraper._run(url)
        print(f"Scraped content length: {len(content)} characters")
        if content.startswith("ERROR:"):
            print(f"Scraping failed: {content}")
            return 1
        print("✅ Web scraping successful")

        # Step 2: Content analysis
        print("\n2. Testing content analyzer...")
        analyzer = ContentAnalyzerTool(api_key=api_key)
        analysis = analyzer._run(content[:5000])  # Limit content for test
        print(f"Analysis length: {len(analysis)} characters")
        if analysis.startswith("ERROR:"):
            print(f"Analysis failed: {analysis}")
            return 1
        print("✅ Content analysis successful")

        # Step 3: Keyword extraction
        print("\n3. Testing keyword extractor...")
        extractor = KeywordExtractorTool()
        keywords = extractor._run(analysis)
        print("Extracted keywords:")
        print(keywords)
        if keywords.startswith("ERROR:"):
            print(f"Keyword extraction failed: {keywords}")
            return 1
        print("✅ Keyword extraction successful")

        print(f"\n🎉 All tools working! Final result:\n{keywords}")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())