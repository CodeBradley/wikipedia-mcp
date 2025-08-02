"""
Wikipedia MCP server implementation.
"""

import logging
from typing import Dict, List, Optional, Any

from fastmcp import FastMCP
from wikipedia_mcp.wikipedia_client import WikipediaClient

logger = logging.getLogger(__name__)

def create_server(language: str = "en", country: Optional[str] = None, enable_cache: bool = False) -> FastMCP:
    """Create and configure the Wikipedia MCP server."""
    server = FastMCP(
        name="Wikipedia",
    )

    # Initialize Wikipedia client
    wikipedia_client = WikipediaClient(language=language, country=country, enable_cache=enable_cache)

    # Register tools
    @server.tool()
    def search_wikipedia(query: str, limit: int = 10) -> Dict[str, Any]:
        """Search Wikipedia for articles matching a query."""
        logger.info(f"Tool: Searching Wikipedia for: {query}")
        results = wikipedia_client.search(query, limit=limit)
        return {
            "query": query,
            "results": results
        }

    @server.tool()
    def get_article(title: str) -> Dict[str, Any]:
        """Get the full content of a Wikipedia article."""
        logger.info(f"Tool: Getting article: {title}")
        article = wikipedia_client.get_article(title)
        return article

    @server.tool()
    def get_summary(title: str) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article."""
        logger.info(f"Tool: Getting summary for: {title}")
        summary = wikipedia_client.get_summary(title)
        return {
            "title": title,
            "summary": summary
        }

    @server.tool()
    def summarize_article_for_query(title: str, query: str, max_length: int = 250) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article tailored to a specific query."""
        logger.info(f"Tool: Getting query-focused summary for article: {title}, query: {query}")
        # Assuming wikipedia_client has a method like summarize_for_query
        summary = wikipedia_client.summarize_for_query(title, query, max_length=max_length)
        return {
            "title": title,
            "query": query,
            "summary": summary
        }

    @server.tool()
    def summarize_article_section(title: str, section_title: str, max_length: int = 150) -> Dict[str, Any]:
        """Get a summary of a specific section of a Wikipedia article."""
        logger.info(f"Tool: Getting summary for section: {section_title} in article: {title}")
        # Assuming wikipedia_client has a method like summarize_section
        summary = wikipedia_client.summarize_section(title, section_title, max_length=max_length)
        return {
            "title": title,
            "section_title": section_title,
            "summary": summary
        }

    @server.tool()
    def extract_key_facts(title: str, topic_within_article: str = "", count: int = 5) -> Dict[str, Any]:
        """Extract key facts from a Wikipedia article, optionally focused on a topic."""
        logger.info(f"Tool: Extracting key facts for article: {title}, topic: {topic_within_article}")
        # Convert empty string to None for backward compatibility
        topic = topic_within_article if topic_within_article.strip() else None
        # Assuming wikipedia_client has a method like extract_facts
        facts = wikipedia_client.extract_facts(title, topic, count=count)
        return {
            "title": title,
            "topic_within_article": topic_within_article,
            "facts": facts
        }

    @server.tool()
    def get_related_topics(title: str, limit: int = 10) -> Dict[str, Any]:
        """Get topics related to a Wikipedia article based on links and categories."""
        logger.info(f"Tool: Getting related topics for: {title}")
        related = wikipedia_client.get_related_topics(title, limit=limit)
        return {
            "title": title,
            "related_topics": related
        }

    @server.tool()
    def get_sections(title: str) -> Dict[str, Any]:
        """Get the sections of a Wikipedia article."""
        logger.info(f"Tool: Getting sections for: {title}")
        sections = wikipedia_client.get_sections(title)
        return {
            "title": title,
            "sections": sections
        }

    @server.tool()
    def get_links(title: str) -> Dict[str, Any]:
        """Get the links contained within a Wikipedia article."""
        logger.info(f"Tool: Getting links for: {title}")
        links = wikipedia_client.get_links(title)
        return {
            "title": title,
            "links": links
        }

    @server.tool()
    def get_page_revisions(title: str, limit: int = 50) -> Dict[str, Any]:
        """Get the complete revision history for a Wikipedia page."""
        logger.info(f"Tool: Getting revision history for: {title}, limit: {limit}")
        revisions = wikipedia_client.get_page_revisions(title, limit=limit)
        return revisions

    @server.tool()
    def get_user_contributions(username: str, limit: int = 50) -> Dict[str, Any]:
        """Get all contributions made by a specific Wikipedia user."""
        logger.info(f"Tool: Getting contributions for user: {username}, limit: {limit}")
        contributions = wikipedia_client.get_user_contributions(username, limit=limit)
        return contributions

    @server.tool()
    def get_user_info(username: str) -> Dict[str, Any]:
        """Get detailed information and statistics about a Wikipedia user."""
        logger.info(f"Tool: Getting user info for: {username}")
        user_info = wikipedia_client.get_user_info(username)
        return user_info

    @server.tool()
    def compare_revisions(from_rev: int, to_rev: int) -> Dict[str, Any]:
        """Compare two specific revisions of a Wikipedia page."""
        logger.info(f"Tool: Comparing revisions from {from_rev} to {to_rev}")
        comparison = wikipedia_client.compare_revisions(from_rev, to_rev)
        return comparison

    @server.tool()
    def get_page_creator(title: str) -> Dict[str, Any]:
        """Find who originally created a Wikipedia page."""
        logger.info(f"Tool: Getting page creator for: {title}")
        creator = wikipedia_client.get_page_creator(title)
        return creator

    @server.tool()
    def get_revision_details(revid: int) -> Dict[str, Any]:
        """Get detailed information about a specific revision."""
        logger.info(f"Tool: Getting details for revision: {revid}")
        details = wikipedia_client.get_revision_details(revid)
        return details

    @server.tool()
    def get_talk_page(title: str) -> Dict[str, Any]:
        """Get the content and metadata of a Wikipedia talk page."""
        logger.info(f"Tool: Getting talk page for: {title}")
        talk_page = wikipedia_client.get_talk_page(title)
        return talk_page

    @server.tool()
    def analyze_edit_activity(title: str, start_datetime: str = "", end_datetime: str = "", 
                            window_size: str = "day", z_threshold: float = 2.0) -> Dict[str, Any]:
        """Analyze edit activity patterns and detect spikes using statistical methods."""
        logger.info(f"Tool: Analyzing edit activity for: {title}, window: {window_size}, z_threshold: {z_threshold}")
        
        # Convert empty strings to None for optional parameters
        start_dt = start_datetime if start_datetime.strip() else None
        end_dt = end_datetime if end_datetime.strip() else None
        
        analysis = wikipedia_client.analyze_edit_activity(
            title, start_datetime=start_dt, end_datetime=end_dt, 
            window_size=window_size, z_threshold=z_threshold
        )
        return analysis

    @server.tool()
    def get_significant_revisions(title: str, start_datetime: str = "", end_datetime: str = "",
                                limit: int = 50, min_significance: float = 0.5) -> Dict[str, Any]:
        """Get the most significant revisions based on weighted scoring algorithm."""
        logger.info(f"Tool: Getting significant revisions for: {title}, limit: {limit}, min_significance: {min_significance}")
        
        # Convert empty strings to None for optional parameters
        start_dt = start_datetime if start_datetime.strip() else None
        end_dt = end_datetime if end_datetime.strip() else None
        
        significant = wikipedia_client.get_significant_revisions(
            title, start_datetime=start_dt, end_datetime=end_dt,
            limit=limit, min_significance=min_significance
        )
        return significant

    @server.resource("/search/{query}")
    def search(query: str) -> Dict[str, Any]:
        """Search Wikipedia for articles matching a query."""
        logger.info(f"Searching Wikipedia for: {query}")
        results = wikipedia_client.search(query, limit=10)
        return {
            "query": query,
            "results": results
        }

    @server.resource("/article/{title}")
    def article(title: str) -> Dict[str, Any]:
        """Get the full content of a Wikipedia article."""
        logger.info(f"Getting article: {title}")
        article = wikipedia_client.get_article(title)
        return article

    @server.resource("/summary/{title}")
    def summary(title: str) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article."""
        logger.info(f"Getting summary for: {title}")
        summary = wikipedia_client.get_summary(title)
        return {
            "title": title,
            "summary": summary
        }

    @server.resource("/summary/{title}/query/{query}/length/{max_length}")
    def summary_for_query_resource(title: str, query: str, max_length: int) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article tailored to a specific query."""
        logger.info(f"Resource: Getting query-focused summary for article: {title}, query: {query}, max_length: {max_length}")
        summary = wikipedia_client.summarize_for_query(title, query, max_length=max_length)
        return {
            "title": title,
            "query": query,
            "summary": summary
        }

    @server.resource("/summary/{title}/section/{section_title}/length/{max_length}")
    def summary_section_resource(title: str, section_title: str, max_length: int) -> Dict[str, Any]:
        """Get a summary of a specific section of a Wikipedia article."""
        logger.info(f"Resource: Getting summary for section: {section_title} in article: {title}, max_length: {max_length}")
        summary = wikipedia_client.summarize_section(title, section_title, max_length=max_length)
        return {
            "title": title,
            "section_title": section_title,
            "summary": summary
        }

    @server.resource("/sections/{title}")
    def sections(title: str) -> Dict[str, Any]:
        """Get the sections of a Wikipedia article."""
        logger.info(f"Getting sections for: {title}")
        sections = wikipedia_client.get_sections(title)
        return {
            "title": title,
            "sections": sections
        }

    @server.resource("/links/{title}")
    def links(title: str) -> Dict[str, Any]:
        """Get the links in a Wikipedia article."""
        logger.info(f"Getting links for: {title}")
        links = wikipedia_client.get_links(title)
        return {
            "title": title,
            "links": links
        }

    @server.resource("/facts/{title}/topic/{topic_within_article}/count/{count}")
    def key_facts_resource(title: str, topic_within_article: str, count: int) -> Dict[str, Any]:
        """Extract key facts from a Wikipedia article."""
        logger.info(f"Resource: Extracting key facts for article: {title}, topic: {topic_within_article}, count: {count}")
        facts = wikipedia_client.extract_facts(title, topic_within_article, count=count)
        return {
            "title": title,
            "topic_within_article": topic_within_article,
            "facts": facts
        }

    @server.resource("/revisions/{title}/limit/{limit}")
    def page_revisions_resource(title: str, limit: int) -> Dict[str, Any]:
        """Get the revision history for a Wikipedia page."""
        logger.info(f"Resource: Getting revision history for: {title}, limit: {limit}")
        return wikipedia_client.get_page_revisions(title, limit=limit)

    @server.resource("/user/{username}/contributions/limit/{limit}")
    def user_contributions_resource(username: str, limit: int) -> Dict[str, Any]:
        """Get contributions made by a specific Wikipedia user."""
        logger.info(f"Resource: Getting contributions for user: {username}, limit: {limit}")
        return wikipedia_client.get_user_contributions(username, limit=limit)

    @server.resource("/user/{username}/info")
    def user_info_resource(username: str) -> Dict[str, Any]:
        """Get detailed information about a Wikipedia user."""
        logger.info(f"Resource: Getting user info for: {username}")
        return wikipedia_client.get_user_info(username)

    @server.resource("/revisions/compare/{from_rev}/{to_rev}")
    def compare_revisions_resource(from_rev: int, to_rev: int) -> Dict[str, Any]:
        """Compare two specific revisions."""
        logger.info(f"Resource: Comparing revisions from {from_rev} to {to_rev}")
        return wikipedia_client.compare_revisions(from_rev, to_rev)

    @server.resource("/page/{title}/creator")
    def page_creator_resource(title: str) -> Dict[str, Any]:
        """Find who originally created a Wikipedia page."""
        logger.info(f"Resource: Getting page creator for: {title}")
        return wikipedia_client.get_page_creator(title)

    @server.resource("/revision/{revid}")
    def revision_details_resource(revid: int) -> Dict[str, Any]:
        """Get detailed information about a specific revision."""
        logger.info(f"Resource: Getting details for revision: {revid}")
        return wikipedia_client.get_revision_details(revid)

    @server.resource("/talk/{title}")
    def talk_page_resource(title: str) -> Dict[str, Any]:
        """Get the content and metadata of a Wikipedia talk page."""
        logger.info(f"Resource: Getting talk page for: {title}")
        return wikipedia_client.get_talk_page(title)

    @server.resource("/activity/{title}/window/{window_size}/threshold/{z_threshold}")
    def edit_activity_resource(title: str, window_size: str, z_threshold: float) -> Dict[str, Any]:
        """Analyze edit activity patterns and detect spikes."""
        logger.info(f"Resource: Analyzing edit activity for: {title}, window: {window_size}")
        return wikipedia_client.analyze_edit_activity(
            title, window_size=window_size, z_threshold=z_threshold
        )

    @server.resource("/significant/{title}/limit/{limit}/threshold/{min_significance}")
    def significant_revisions_resource(title: str, limit: int, min_significance: float) -> Dict[str, Any]:
        """Get the most significant revisions based on weighted scoring."""
        logger.info(f"Resource: Getting significant revisions for: {title}, limit: {limit}")
        return wikipedia_client.get_significant_revisions(
            title, limit=limit, min_significance=min_significance
        )

    return server 