#!/usr/bin/env python3
"""
Working Web Content Analyzer Script

This is a direct script that bypasses the packaging issues and works immediately.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_content_analyzer.simple_analyzer import SimpleWebContentAnalyzer
from web_content_analyzer.config import Config


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python analyze.py <url>")
        print("  python analyze.py batch <file.txt>")
        print("")
        print("Examples:")
        print("  python analyze.py https://example.com")
        print("  python analyze.py batch examples/urls.txt")
        return

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: Please set ANTHROPIC_API_KEY environment variable")
        print("Example: export ANTHROPIC_API_KEY=sk-ant-api03-...")
        return

    try:
        config = Config()
        config.validate()
        analyzer = SimpleWebContentAnalyzer(config)

        if sys.argv[1] == "batch" and len(sys.argv) >= 3:
            # Batch processing
            file_path = Path(sys.argv[2])
            if not file_path.exists():
                print(f"Error: File {file_path} not found")
                return

            urls = []
            with file_path.open() as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if not line.startswith(("http://", "https://")):
                            print(f"Warning: Line {line_num} invalid URL format: {line}")
                            continue
                        urls.append(line)

            if not urls:
                print("No valid URLs found in file")
                return

            print(f"Processing {len(urls)} URLs...")
            results = analyzer.analyze_batch(urls)

            successful = [r for r in results if r['status'] == 'success']
            failed = [r for r in results if r['status'] == 'failed']

            print(f"\nBatch Processing Complete:")
            print(f"  Successful: {len(successful)}")
            print(f"  Failed: {len(failed)}")

            if successful:
                print("\n" + "="*60)
                print("SUCCESSFUL ANALYSES:")
                print("="*60)
                for result in successful:
                    display_result(result)
                    print("-" * 40)

            if failed:
                print("\n" + "="*60)
                print("FAILED ANALYSES:")
                print("="*60)
                for result in failed:
                    display_result(result)
                    print("-" * 40)

        else:
            # Single URL analysis
            url = sys.argv[1]
            print(f"Analyzing: {url}")
            result = analyzer.analyze_url(url)
            display_result(result)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def display_result(result):
    """Display analysis result in text format."""
    print(f"\nURL: {result['url']}")
    print(f"Status: {result['status']}")

    if result['status'] == 'success':
        print(f"Processing time: {result['processing_time']:.2f}s")
        print("\nKeywords:")
        for i, keyword in enumerate(result['keywords'], 1):
            print(f"  {i:2d}. {keyword}")
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()