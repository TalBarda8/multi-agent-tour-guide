"""
YouTube Agent Client
Wrapper for youtube-location-video-finder agent
"""

import time
from typing import Dict, Any

from src.models import AgentResult, ContentItem, ContentType, AgentStatus, Waypoint
from src.logging_config import get_logger


def call_youtube_agent(
    transaction_id: str,
    waypoint: Waypoint
) -> AgentResult:
    """
    Call the YouTube location video finder agent

    This function is designed to be called by Claude Code's orchestration,
    which will use the Task tool to invoke the youtube-location-video-finder agent.

    Args:
        transaction_id: Transaction ID for tracking
        waypoint: Waypoint to find video for

    Returns:
        AgentResult with video content
    """
    logger = get_logger()
    start_time = time.time()

    logger.log_agent_start(
        "youtube",
        transaction_id,
        waypoint.id,
        search_query=waypoint.agent_context.youtube_query if waypoint.agent_context else ""
    )

    # This function will be called with the agent result from Task tool
    # For now, return a placeholder that indicates real agent should be called
    raise NotImplementedError(
        "This function should be called by Claude Code orchestration using Task tool. "
        "Use the youtube-location-video-finder agent via Task tool."
    )


def parse_youtube_agent_response(
    response: Dict[str, Any],
    transaction_id: str,
    waypoint_id: int,
    execution_time_ms: int
) -> AgentResult:
    """
    Parse response from YouTube agent into AgentResult format

    Args:
        response: Raw response from agent
        transaction_id: Transaction ID
        waypoint_id: Waypoint ID
        execution_time_ms: Execution time

    Returns:
        Parsed AgentResult
    """
    logger = get_logger()

    try:
        # Extract content from agent response
        content = ContentItem(
            content_type=ContentType.VIDEO,
            title=response.get("title", "Unknown Video"),
            description=response.get("description", ""),
            relevance_score=response.get("relevance_score", 0.5),
            url=response.get("url"),
            metadata={
                "channel": response.get("channel"),
                "view_count": response.get("view_count"),
                "duration": response.get("duration"),
                "source": "youtube-location-video-finder"
            }
        )

        result = AgentResult(
            agent_name="youtube",
            transaction_id=transaction_id,
            waypoint_id=waypoint_id,
            status=AgentStatus.SUCCESS,
            content=content,
            execution_time_ms=execution_time_ms
        )

        logger.log_agent_completion(
            "youtube",
            transaction_id,
            waypoint_id,
            result.status.value,
            execution_time_ms,
            relevance_score=content.relevance_score
        )

        return result

    except Exception as e:
        logger.log_agent_error(
            "youtube",
            transaction_id,
            waypoint_id,
            str(e)
        )

        return AgentResult(
            agent_name="youtube",
            transaction_id=transaction_id,
            waypoint_id=waypoint_id,
            status=AgentStatus.ERROR,
            content=None,
            error_message=str(e),
            execution_time_ms=execution_time_ms
        )
