"""Command-line interface for Web Content Analyzer."""

import os
import sys
from pathlib import Path
from typing import List

import click
from dotenv import load_dotenv

from .simple_analyzer import SimpleWebContentAnalyzer as WebContentAnalyzer
from .config import Config

load_dotenv()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(ctx, verbose):
    """Web Content Analyzer - Extract keywords from web pages using CrewAI and Claude API."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text",
              help="Output format (default: text)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def analyze(url: str, output: str, verbose: bool):
    """Analyze a single URL and extract keywords."""
    try:
        config = Config(verbose=verbose)
        config.validate()

        analyzer = WebContentAnalyzer(config)

        click.echo(f"Analyzing: {url}")

        result = analyzer.analyze_url(url)

        if output == "json":
            import json
            click.echo(json.dumps(result, indent=2))
        else:
            _display_text_result(result)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--parallel", "-p", default=3, help="Number of parallel processes (default: 3)")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text",
              help="Output format (default: text)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def batch(file: Path, parallel: int, output: str, verbose: bool):
    """Process multiple URLs from a file (one URL per line)."""
    try:
        config = Config(verbose=verbose, parallel_limit=parallel)
        config.validate()

        urls = _read_urls_from_file(file)

        analyzer = WebContentAnalyzer(config)

        click.echo(f"Processing {len(urls)} URLs with {parallel} parallel workers...")

        results = analyzer.analyze_batch(urls)

        if output == "json":
            import json
            click.echo(json.dumps(results, indent=2))
        else:
            _display_batch_results(results)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--port", "-p", default=8000, help="Port to run the server on (default: 8000)")
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind the server to")
def server(port: int, host: str):
    """Start the web server with UI for batch processing."""
    try:
        config = Config()
        config.validate()

        from .server import create_app
        import uvicorn

        app = create_app(config)

        click.echo(f"Starting server at http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)

    except Exception as e:
        click.echo(f"Error starting server: {str(e)}", err=True)
        sys.exit(1)


def _read_urls_from_file(file: Path) -> List[str]:
    """Read URLs from a text file, one per line."""
    urls = []
    with file.open() as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                if not line.startswith(("http://", "https://")):
                    raise ValueError(f"Line {line_num}: Invalid URL format: {line}")
                urls.append(line)

    if not urls:
        raise ValueError("No valid URLs found in file")

    return urls


def _display_text_result(result: dict):
    """Display analysis result in text format."""
    click.echo(f"\nURL: {result['url']}")
    click.echo(f"Status: {result['status']}")

    if result['status'] == 'success':
        click.echo(f"Processing time: {result['processing_time']:.2f}s")
        click.echo("\nKeywords:")
        for i, keyword in enumerate(result['keywords'], 1):
            click.echo(f"  {i:2d}. {keyword}")
    else:
        click.echo(f"Error: {result['error']}")


def _display_batch_results(results: List[dict]):
    """Display batch analysis results in text format."""
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    click.echo(f"\nBatch Processing Complete:")
    click.echo(f"  Successful: {len(successful)}")
    click.echo(f"  Failed: {len(failed)}")

    if successful:
        click.echo("\n" + "="*60)
        click.echo("SUCCESSFUL ANALYSES:")
        click.echo("="*60)
        for result in successful:
            _display_text_result(result)
            click.echo("-" * 40)

    if failed:
        click.echo("\n" + "="*60)
        click.echo("FAILED ANALYSES:")
        click.echo("="*60)
        for result in failed:
            _display_text_result(result)
            click.echo("-" * 40)


if __name__ == "__main__":
    main()