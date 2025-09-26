#!/usr/bin/env python3
"""Test scraping functionality with the 10 selected websites."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_content_analyzer.standalone_tools import StandaloneWebScraper

def main():
    urls = [
        "https://example.com",
        "https://wikipedia.org",
        "https://github.com/anthropics/claude-code",
        "https://news.ycombinator.com",
        "https://stackoverflow.com/questions/1",
        "https://www.reddit.com/r/programming",
        "https://medium.com/@golang/introducing-go-1-18-beta-1-3b47b8f55b2f",
        "https://docs.python.org/3/",
        "https://www.nature.com/",
        "https://techcrunch.com"
    ]

    print("🌐 Testing Web Content Scraping on 10 Random Websites")
    print("=" * 60)

    scraper = StandaloneWebScraper(timeout_seconds=60, max_content_size_mb=10)
    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n{i:2d}. {url}")
        try:
            content = scraper.scrape(url)
            if content.startswith("ERROR:"):
                print(f"     ❌ Failed: {content}")
                results.append({"url": url, "status": "failed", "content_length": 0})
            else:
                print(f"     ✅ Success: {len(content):,} characters")
                # Show first 150 chars as preview
                preview = content[:150].replace('\n', ' ').replace('\r', ' ')
                print(f"     Preview: {preview}...")
                results.append({"url": url, "status": "success", "content_length": len(content)})
        except Exception as e:
            print(f"     ❌ Exception: {str(e)}")
            results.append({"url": url, "status": "error", "content_length": 0})

    # Summary
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    total_content = sum(r["content_length"] for r in results)

    print(f"\n{'='*60}")
    print(f"📊 SCRAPING RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful}/{len(urls)} websites")
    print(f"❌ Failed: {failed}/{len(urls)} websites")
    print(f"📄 Total content: {total_content:,} characters")
    print(f"📊 Average per site: {total_content//successful if successful > 0 else 0:,} characters")

    if successful == len(urls):
        print(f"\n🎉 Perfect! All {len(urls)} websites scraped successfully!")
        print("🚀 System ready for full AI analysis with API key")
    elif successful > 0:
        print(f"\n✅ {successful} out of {len(urls)} websites working well")
        print("🚀 System ready for AI analysis on working sites")

    return results

if __name__ == "__main__":
    main()