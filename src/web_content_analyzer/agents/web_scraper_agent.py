"""Web Scraper Agent for extracting content from web pages."""

from crewai import Agent, LLM
from ..tools.web_scraper import WebScraperTool


def create_web_scraper_agent(config) -> Agent:
    """Create a web scraper agent with Playwright tool."""

    web_scraper_tool = WebScraperTool()

    # Create Claude LLM
    claude_llm = LLM(
        model="claude-3-5-sonnet-latest",
        api_key=config.anthropic_api_key
    )

    return Agent(
        role="Web Content Scraper",
        goal="Extract clean, readable text content from web pages, including JavaScript-rendered content",
        backstory=(
            "You are an expert web scraper who specializes in extracting meaningful content "
            "from modern web pages. You understand how to handle JavaScript-heavy sites, "
            "filter out navigation and ads, and focus on the main content that users care about. "
            "You're skilled at dealing with various website structures and can adapt to "
            "different content management systems and layouts."
        ),
        tools=[web_scraper_tool],
        llm=claude_llm,
        verbose=config.verbose,
        allow_delegation=False,
        max_execution_time=config.timeout_seconds
    )