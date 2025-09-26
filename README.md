# Web Content Analyzer

A CrewAI-based web content analysis agent that extracts keywords from web pages using Claude API.

## Features

- **JavaScript-Rendered Content**: Uses Playwright to scrape modern web pages
- **AI-Powered Analysis**: Leverages Claude API for intelligent content analysis
- **Multi-Agent Architecture**: Uses CrewAI with specialized agents for scraping, analysis, and keyword extraction
- **Batch Processing**: Process multiple URLs with configurable parallelism
- **Error Resilience**: Continues processing other URLs if one fails
- **Simple CLI**: Easy command-line interface for single URLs or batch processing

## Installation

### Prerequisites

- Python 3.12+
- Claude API key from Anthropic

### Setup

1. Clone or download this project
2. Install with uv:

```bash
cd web-content-analyzer
uv sync
```

3. Install Playwright browsers:

```bash
uv run playwright install chromium
```

4. Configure your API key:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Single URL Analysis

```bash
# Direct execution
uvx . analyze https://example.com

# Or after installation
uv run web-analyzer analyze https://example.com

# With verbose logging
uvx . analyze https://example.com --verbose
```

### Batch Processing

Create a file with URLs (one per line):

```bash
# urls.txt
https://example.com
https://another-site.com
https://news.ycombinator.com
```

Then run batch analysis:

```bash
# Process with default 3 parallel workers
uvx . batch urls.txt

# Process with custom parallelism
uvx . batch urls.txt --parallel 5

# Output in JSON format
uvx . batch urls.txt --output json
```

### Web Server Mode (Future Enhancement)

```bash
uvx . server --port 8000
# Then visit http://localhost:8000
```

## Output

The tool extracts exactly 10 keywords that best characterize each web page, including:

- Main topics and themes
- Technical terms and concepts
- Named entities (people, organizations, products)
- Domain-specific terminology

Example output:
```
URL: https://example.com
Status: success
Processing time: 45.30s

Keywords:
   1. machine learning
   2. artificial intelligence
   3. neural networks
   4. data science
   5. Python
   6. TensorFlow
   7. deep learning
   8. natural language processing
   9. computer vision
   10. automation
```

## Configuration

Environment variables (all optional):

- `ANTHROPIC_API_KEY` - Required Claude API key
- `WEB_ANALYZER_VERBOSE` - Enable verbose logging (default: false)
- `WEB_ANALYZER_PARALLEL_LIMIT` - Batch processing parallelism (default: 3)
- `WEB_ANALYZER_TIMEOUT_SECONDS` - Per-URL timeout (default: 180)
- `WEB_ANALYZER_MAX_CONTENT_SIZE_MB` - Content size limit (default: 10)
- `WEB_ANALYZER_MAX_RETRIES` - Retry attempts (default: 3)

## Architecture

The system uses a multi-agent approach with CrewAI:

1. **Web Scraper Agent** - Extracts content using Playwright
2. **Content Analyzer Agent** - Analyzes content using Claude API
3. **Keyword Extractor Agent** - Extracts and ranks top 10 keywords

Agents work in sequence, with error isolation to ensure batch processing continues even if individual URLs fail.

## Limitations

- Maximum 3 minutes per URL
- Maximum 10MB content size per page
- Requires stable internet connection
- Claude API usage costs apply

## Troubleshooting

### Common Issues

1. **"ANTHROPIC_API_KEY not found"**
   - Ensure your `.env` file contains a valid API key
   - Verify the key is not expired or has quota remaining

2. **Playwright browser issues**
   - Run `uv run playwright install chromium`
   - Ensure sufficient disk space and memory

3. **Timeout errors**
   - Increase timeout with `WEB_ANALYZER_TIMEOUT_SECONDS`
   - Check internet connection stability
   - Some sites may be blocking automated access

4. **Content extraction issues**
   - Some sites use advanced anti-bot measures
   - Dynamic content may require longer wait times
   - Check if the site requires authentication

### Getting Help

For issues and feature requests, check the project repository or create an issue.