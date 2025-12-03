"""
Mock Agent Implementations
Provides mock implementations for YouTube, Spotify, and History agents
These will be replaced with real Claude Code agent calls in production
"""

import time
from typing import Dict

from src.models import (
    Waypoint,
    AgentResult,
    ContentItem,
    ContentType,
    AgentStatus,
    JudgeDecision,
    TransactionContext,
    create_fallback_content
)
from src.logging_config import get_logger


def run_mock_youtube_agent(
    transaction_id: str,
    waypoint: Waypoint
) -> AgentResult:
    """
    Mock implementation of YouTube agent

    Simulates YouTube API call to find relevant video content
    for a given waypoint location.

    Args:
        transaction_id: Unique transaction identifier
        waypoint: Waypoint location to find content for

    Returns:
        AgentResult with mock video content
    """
    logger = get_logger()
    start_time = time.time()

    logger.log_agent_start(
        "youtube",
        transaction_id,
        waypoint.id,
        search_query=waypoint.agent_context.youtube_query if waypoint.agent_context else ""
    )

    # Simulate API call delay
    time.sleep(0.5)

    # Create mock video content
    content = ContentItem(
        content_type=ContentType.VIDEO,
        title=f"Video about {waypoint.location_name}",
        description=f"A virtual tour of {waypoint.location_name}",
        relevance_score=0.75,
        url=f"https://youtube.com/watch?v=mock_{waypoint.id}",
        metadata={"source": "mock"}
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    result = AgentResult(
        agent_name="youtube",
        transaction_id=transaction_id,
        waypoint_id=waypoint.id,
        status=AgentStatus.SUCCESS,
        content=content,
        execution_time_ms=execution_time_ms
    )

    logger.log_agent_completion(
        "youtube",
        transaction_id,
        waypoint.id,
        result.status.value,
        execution_time_ms,
        relevance_score=content.relevance_score
    )

    return result


def run_mock_spotify_agent(
    transaction_id: str,
    waypoint: Waypoint
) -> AgentResult:
    """
    Mock implementation of Spotify agent

    Simulates Spotify API call to find relevant music content
    for a given waypoint location.

    Args:
        transaction_id: Unique transaction identifier
        waypoint: Waypoint location to find content for

    Returns:
        AgentResult with mock music content
    """
    logger = get_logger()
    start_time = time.time()

    logger.log_agent_start(
        "spotify",
        transaction_id,
        waypoint.id,
        search_query=waypoint.agent_context.spotify_query if waypoint.agent_context else ""
    )

    # Simulate API call delay
    time.sleep(0.4)

    # Create mock music content
    content = ContentItem(
        content_type=ContentType.SONG,
        title=f"Song for {waypoint.location_name}",
        description="A fitting soundtrack for this location",
        relevance_score=0.82,
        url=f"https://open.spotify.com/track/mock_{waypoint.id}",
        metadata={"source": "mock", "artist": "Mock Artist"}
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    result = AgentResult(
        agent_name="spotify",
        transaction_id=transaction_id,
        waypoint_id=waypoint.id,
        status=AgentStatus.SUCCESS,
        content=content,
        execution_time_ms=execution_time_ms
    )

    logger.log_agent_completion(
        "spotify",
        transaction_id,
        waypoint.id,
        result.status.value,
        execution_time_ms,
        relevance_score=content.relevance_score
    )

    return result


def run_mock_history_agent(
    transaction_id: str,
    waypoint: Waypoint
) -> AgentResult:
    """
    Mock implementation of History agent

    Simulates Wikipedia/historical database query to find relevant
    historical facts for a given waypoint location.

    Args:
        transaction_id: Unique transaction identifier
        waypoint: Waypoint location to find content for

    Returns:
        AgentResult with mock historical content
    """
    logger = get_logger()
    start_time = time.time()

    logger.log_agent_start(
        "history",
        transaction_id,
        waypoint.id,
        search_query=waypoint.agent_context.history_query if waypoint.agent_context else ""
    )

    # Simulate API call delay
    time.sleep(0.3)

    # Create mock historical content
    content = ContentItem(
        content_type=ContentType.HISTORY,
        title=f"History of {waypoint.location_name}",
        description=f"Fascinating historical facts about {waypoint.location_name} and its significance.",
        relevance_score=0.68,
        url=None,
        metadata={"source": "mock"}
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    result = AgentResult(
        agent_name="history",
        transaction_id=transaction_id,
        waypoint_id=waypoint.id,
        status=AgentStatus.SUCCESS,
        content=content,
        execution_time_ms=execution_time_ms
    )

    logger.log_agent_completion(
        "history",
        transaction_id,
        waypoint.id,
        result.status.value,
        execution_time_ms,
        relevance_score=content.relevance_score
    )

    return result


def run_mock_judge(
    context: TransactionContext,
    waypoint: Waypoint,
    agent_results: Dict[str, AgentResult]
) -> JudgeDecision:
    """
    Mock implementation of Judge agent

    Evaluates results from all content agents and selects the best one
    based on relevance scores. Real implementation will use LLM-based
    sophisticated decision logic.

    Args:
        context: Transaction context
        waypoint: Waypoint being judged
        agent_results: Results from all content agents

    Returns:
        JudgeDecision with selected content and reasoning
    """
    logger = get_logger()
    start_time = time.time()

    logger.debug(
        "Judge evaluation started",
        transaction_id=context.transaction_id,
        waypoint_id=waypoint.id
    )

    try:
        # Simple selection based on relevance score
        best_agent = None
        best_score = 0.0
        scores = {}

        # Evaluate each agent's result
        for agent_name, result in agent_results.items():
            if result.is_successful() and result.content:
                score = result.content.relevance_score
                scores[agent_name] = score
                if score > best_score:
                    best_score = score
                    best_agent = agent_name
            else:
                scores[agent_name] = 0.0

        # Select winner or fallback
        if best_agent:
            selected_content = agent_results[best_agent].content
            reasoning = f"Selected {best_agent} with highest relevance score ({best_score:.2f})"
        else:
            # All agents failed - use fallback
            selected_content = create_fallback_content(waypoint)
            reasoning = "All agents failed, using fallback content"
            best_agent = "fallback"
            best_score = 0.0

        decision_time_ms = int((time.time() - start_time) * 1000)

        decision = JudgeDecision(
            winner=best_agent,
            reasoning=reasoning,
            confidence_score=best_score,
            individual_scores=scores,
            decision_time_ms=decision_time_ms,
            tie_breaker_applied=False,
            selected_content=selected_content
        )

        logger.log_judge_decision(
            transaction_id=context.transaction_id,
            waypoint_id=waypoint.id,
            winner=best_agent,
            confidence=best_score,
            reasoning=reasoning
        )

        return decision

    except Exception as e:
        logger.error(
            "Judge error, using fallback",
            transaction_id=context.transaction_id,
            waypoint_id=waypoint.id,
            error=str(e)
        )

        # Fallback decision on error
        return JudgeDecision(
            winner="fallback",
            reasoning=f"Judge error: {str(e)}",
            confidence_score=0.0,
            individual_scores={},
            decision_time_ms=0,
            tie_breaker_applied=False,
            selected_content=create_fallback_content(waypoint)
        )
