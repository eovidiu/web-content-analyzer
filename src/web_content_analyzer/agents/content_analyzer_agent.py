"""Content Analyzer Agent for understanding web content using Claude API."""

from crewai import Agent, LLM
from ..tools.content_analyzer import ContentAnalyzerTool


def create_content_analyzer_agent(config) -> Agent:
    """Create a content analyzer agent with Claude API tool."""

    content_analyzer_tool = ContentAnalyzerTool(api_key=config.anthropic_api_key)

    # Create Claude LLM
    claude_llm = LLM(
        model="claude-3-5-sonnet-latest",
        api_key=config.anthropic_api_key
    )

    return Agent(
        role="Content Analysis Specialist",
        goal="Analyze web content to understand main themes, topics, and identify key concepts for keyword extraction",
        backstory=(
            "You are a content analysis expert who excels at quickly understanding the core "
            "themes and topics of written content. You have a deep understanding of different "
            "content types - from technical documentation to news articles to marketing pages. "
            "You can identify the most important concepts, technical terms, and named entities "
            "that define what a piece of content is really about. Your analysis provides the "
            "foundation for accurate keyword extraction."
        ),
        tools=[content_analyzer_tool],
        llm=claude_llm,
        verbose=config.verbose,
        allow_delegation=False,
        max_execution_time=120  # 2 minutes should be enough for Claude API calls
    )