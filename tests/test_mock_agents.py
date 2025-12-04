"""
Unit tests for src/modules/mock_agents.py
Tests mock agent implementations
"""

import pytest
from unittest.mock import patch

from src.modules.mock_agents import (
    run_mock_youtube_agent,
    run_mock_spotify_agent,
    run_mock_history_agent,
    run_mock_judge
)
from src.models import (
    Waypoint,
    Coordinates,
    AgentResult,
    ContentType,
    AgentStatus,
    AgentContext,
    create_fallback_content
)


@pytest.mark.unit
class TestMockYouTubeAgent:
    """Test mock YouTube agent"""

    def test_mock_youtube_agent_success(self, sample_waypoints):
        """Test successful YouTube agent execution"""
        waypoint = sample_waypoints[0]
        transaction_id = "TXID-test-123"

        result = run_mock_youtube_agent(transaction_id, waypoint)

        assert result is not None
        assert result.agent_name == "youtube"
        assert result.transaction_id == transaction_id
        assert result.waypoint_id == waypoint.id
        assert result.is_successful()
        assert result.status == AgentStatus.SUCCESS
        assert result.content is not None
        assert result.content.content_type == ContentType.VIDEO
        assert waypoint.location_name in result.content.title
        assert result.content.url is not None
        assert "youtube.com" in result.content.url
        assert result.execution_time_ms > 0

    def test_mock_youtube_agent_with_context(self):
        """Test YouTube agent with agent context"""
        waypoint = Waypoint(
            id=1,
            location_name="Test Location",
            coordinates=Coordinates(lat=40.0, lng=-74.0),
            instruction="Test instruction",
            distance_from_start=0.0,
            step_index=0
        )
        waypoint.agent_context = AgentContext(
            youtube_query="test video query",
            spotify_query="test music query",
            history_query="test history query"
        )

        transaction_id = "TXID-test-456"

        result = run_mock_youtube_agent(transaction_id, waypoint)

        assert result.is_successful()
        assert result.content.content_type == ContentType.VIDEO


@pytest.mark.unit
class TestMockSpotifyAgent:
    """Test mock Spotify agent"""

    def test_mock_spotify_agent_success(self, sample_waypoints):
        """Test successful Spotify agent execution"""
        waypoint = sample_waypoints[0]
        transaction_id = "TXID-test-123"

        result = run_mock_spotify_agent(transaction_id, waypoint)

        assert result is not None
        assert result.agent_name == "spotify"
        assert result.transaction_id == transaction_id
        assert result.waypoint_id == waypoint.id
        assert result.is_successful()
        assert result.status == AgentStatus.SUCCESS
        assert result.content is not None
        assert result.content.content_type == ContentType.SONG
        assert waypoint.location_name in result.content.title
        assert result.content.url is not None
        assert "spotify.com" in result.content.url
        assert result.execution_time_ms > 0
        assert result.content.metadata.get("artist") == "Mock Artist"

    def test_mock_spotify_agent_with_context(self):
        """Test Spotify agent with agent context"""
        waypoint = Waypoint(
            id=2,
            location_name="Central Park",
            coordinates=Coordinates(lat=40.785091, lng=-73.968285),
            instruction="Enter the park",
            distance_from_start=500.0,
            step_index=1
        )
        waypoint.agent_context = AgentContext(
            youtube_query="central park video",
            spotify_query="central park music",
            history_query="central park history"
        )

        transaction_id = "TXID-test-789"

        result = run_mock_spotify_agent(transaction_id, waypoint)

        assert result.is_successful()
        assert result.content.content_type == ContentType.SONG
        assert result.content.relevance_score > 0.5


@pytest.mark.unit
class TestMockHistoryAgent:
    """Test mock History agent"""

    def test_mock_history_agent_success(self, sample_waypoints):
        """Test successful History agent execution"""
        waypoint = sample_waypoints[0]
        transaction_id = "TXID-test-123"

        result = run_mock_history_agent(transaction_id, waypoint)

        assert result is not None
        assert result.agent_name == "history"
        assert result.transaction_id == transaction_id
        assert result.waypoint_id == waypoint.id
        assert result.is_successful()
        assert result.status == AgentStatus.SUCCESS
        assert result.content is not None
        assert result.content.content_type == ContentType.HISTORY
        assert waypoint.location_name in result.content.title
        assert result.content.description is not None
        assert "historical" in result.content.description.lower() or "History" in result.content.title
        assert result.execution_time_ms > 0

    def test_mock_history_agent_no_url(self, sample_waypoints):
        """Test that history agent returns no URL (text-based content)"""
        waypoint = sample_waypoints[1]
        transaction_id = "TXID-test-456"

        result = run_mock_history_agent(transaction_id, waypoint)

        assert result.is_successful()
        assert result.content.content_type == ContentType.HISTORY
        # History content typically doesn't have a URL
        assert result.content.url is None

    def test_mock_history_agent_with_context(self):
        """Test History agent with agent context"""
        waypoint = Waypoint(
            id=3,
            location_name="Empire State Building",
            coordinates=Coordinates(lat=40.748817, lng=-73.985428),
            instruction="Visit landmark",
            distance_from_start=1000.0,
            step_index=2
        )
        waypoint.agent_context = AgentContext(
            youtube_query="empire state building tour",
            spotify_query="new york music",
            history_query="empire state building history"
        )

        transaction_id = "TXID-test-999"

        result = run_mock_history_agent(transaction_id, waypoint)

        assert result.is_successful()
        assert result.content.content_type == ContentType.HISTORY
        assert result.content.relevance_score > 0.0


@pytest.mark.unit
class TestMockJudge:
    """Test mock Judge agent"""

    def test_mock_judge_selects_best_score(self, transaction_context, sample_waypoints):
        """Test judge selects agent with highest relevance score"""
        waypoint = sample_waypoints[0]

        # Create mock agent results with different scores
        from src.models import ContentItem

        youtube_result = AgentResult(
            agent_name="youtube",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=ContentItem(
                content_type=ContentType.VIDEO,
                title="Test Video",
                description="Test video description",
                relevance_score=0.95,  # Highest
                url="https://youtube.com/test"
            ),
            execution_time_ms=100
        )

        spotify_result = AgentResult(
            agent_name="spotify",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=ContentItem(
                content_type=ContentType.SONG,
                title="Test Song",
                description="Test song description",
                relevance_score=0.70,
                url="https://spotify.com/test"
            ),
            execution_time_ms=120
        )

        history_result = AgentResult(
            agent_name="history",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=ContentItem(
                content_type=ContentType.HISTORY,
                title="Test History",
                description="Historical facts",
                relevance_score=0.80
            ),
            execution_time_ms=150
        )

        agent_results = {
            "youtube": youtube_result,
            "spotify": spotify_result,
            "history": history_result
        }

        decision = run_mock_judge(transaction_context, waypoint, agent_results)

        assert decision is not None
        assert decision.winner == "youtube"  # Highest score
        assert decision.selected_content.content_type == ContentType.VIDEO
        assert decision.confidence_score == 0.95
        assert "youtube" in decision.reasoning.lower()
        assert len(decision.individual_scores) == 3
        assert decision.individual_scores["youtube"] == 0.95
        assert decision.decision_time_ms >= 0

    def test_mock_judge_handles_failed_agents(self, transaction_context, sample_waypoints):
        """Test judge handles failed agent results"""
        waypoint = sample_waypoints[0]

        from src.models import ContentItem

        # YouTube failed
        youtube_result = AgentResult(
            agent_name="youtube",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.ERROR,
            error_message="API Error"
        )

        # Spotify succeeded
        spotify_result = AgentResult(
            agent_name="spotify",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=ContentItem(
                content_type=ContentType.SONG,
                title="Test Song",
                description="Test song description",
                relevance_score=0.70,
                url="https://spotify.com/test"
            ),
            execution_time_ms=120
        )

        # History failed
        history_result = AgentResult(
            agent_name="history",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.TIMEOUT
        )

        agent_results = {
            "youtube": youtube_result,
            "spotify": spotify_result,
            "history": history_result
        }

        decision = run_mock_judge(transaction_context, waypoint, agent_results)

        assert decision is not None
        assert decision.winner == "spotify"  # Only successful agent
        assert decision.selected_content.content_type == ContentType.SONG
        assert decision.individual_scores["youtube"] == 0.0
        assert decision.individual_scores["spotify"] == 0.70
        assert decision.individual_scores["history"] == 0.0

    def test_mock_judge_all_agents_failed(self, transaction_context, sample_waypoints):
        """Test judge uses fallback when all agents fail"""
        waypoint = sample_waypoints[0]

        # All agents failed
        youtube_result = AgentResult(
            agent_name="youtube",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.ERROR,
            error_message="Error"
        )

        spotify_result = AgentResult(
            agent_name="spotify",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.TIMEOUT
        )

        history_result = AgentResult(
            agent_name="history",
            transaction_id=transaction_context.transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.ERROR,
            error_message="Error"
        )

        agent_results = {
            "youtube": youtube_result,
            "spotify": spotify_result,
            "history": history_result
        }

        decision = run_mock_judge(transaction_context, waypoint, agent_results)

        assert decision is not None
        assert decision.winner == "fallback"
        assert decision.selected_content is not None
        assert "failed" in decision.reasoning.lower()
        assert decision.confidence_score == 0.0

    def test_mock_judge_error_handling(self, transaction_context, sample_waypoints):
        """Test judge handles unexpected errors gracefully"""
        waypoint = sample_waypoints[0]

        # Create invalid agent results that might cause errors
        agent_results = {
            "youtube": None,  # Invalid - None result
        }

        # Should handle error and return fallback
        decision = run_mock_judge(transaction_context, waypoint, agent_results)

        assert decision is not None
        assert decision.winner == "fallback"
        assert decision.selected_content is not None
        assert "error" in decision.reasoning.lower()

    def test_mock_judge_empty_results(self, transaction_context, sample_waypoints):
        """Test judge with no agent results"""
        waypoint = sample_waypoints[0]
        agent_results = {}

        decision = run_mock_judge(transaction_context, waypoint, agent_results)

        assert decision is not None
        assert decision.winner == "fallback"
        assert decision.selected_content is not None
