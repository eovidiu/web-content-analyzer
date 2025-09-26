#!/usr/bin/env python3
"""Test just the web scraping functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_content_analyzer.standalone_tools import StandaloneWebScraper

def test_scraping():
    """Test web scraping with multiple URLs."""
    urls = [
        "https://example.com",
        "https://httpbin.org/html",  # Simple test endpoint
        "https://www.python.org",
        "https://github.com",
        "https://stackoverflow.com"
    ]

    scraper = StandaloneWebScraper(timeout_seconds=60, max_content_size_mb=5)

    print("Testing web scraping functionality:")
    print("=" * 50)

    successful = 0
    failed = 0

    for i, url in enumerate(urls, 1):
        print(f"\n{i}. Testing: {url}")
        try:
            content = scraper.scrape(url)
            if content.startswith("ERROR:"):
                print(f"   ❌ Failed: {content}")
                failed += 1
            else:
                print(f"   ✅ Success: {len(content)} characters scraped")
                # Show a snippet of the content
                snippet = content[:200].replace('\n', ' ')
                print(f"   Preview: {snippet}...")
                successful += 1
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            failed += 1

    print(f"\nResults: {successful} successful, {failed} failed")
    return successful, failed

if __name__ == "__main__":
    test_scraping()