"""Keyword Extractor Agent for extracting the top 10 keywords."""

from crewai import Agent, LLM
from ..tools.keyword_extractor import KeywordExtractorTool


def create_keyword_extractor_agent(config) -> Agent:
    """Create a keyword extractor agent."""

    keyword_extractor_tool = KeywordExtractorTool()

    # Create Claude LLM
    claude_llm = LLM(
        model="claude-3-5-sonnet-latest",
        api_key=config.anthropic_api_key
    )

    return Agent(
        role="Keyword Extraction Specialist",
        goal="Extract and rank the top 10 most representative keywords that best characterize the web content",
        backstory=(
            "You are a keyword extraction specialist with expertise in information retrieval "
            "and content categorization. You understand how to identify the most important and "
            "representative terms from content analysis. You know how to balance different types "
            "of keywords - including main topics, technical terms, and named entities - to create "
            "a comprehensive set of keywords that accurately represents the content. You always "
            "provide exactly 10 keywords, ranked by importance and relevance."
        ),
        tools=[keyword_extractor_tool],
        llm=claude_llm,
        verbose=config.verbose,
        allow_delegation=False,
        max_execution_time=60  # 1 minute should be plenty for keyword extraction
    )