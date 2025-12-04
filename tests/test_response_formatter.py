"""
Unit tests for src/modules/response_formatter.py
Tests response formatting and output generation
"""

import pytest
from src.modules.response_formatter import (
    format_response,
    _format_waypoints,
    _format_duration_ms,
    _format_distance_meters
)
from src.models import (
    FinalRoute,
    RouteStatistics,
    Waypoint,
    Coordinates,
    WaypointEnrichment,
    ContentItem,
    ContentType,
    JudgeDecision,
    AgentResult,
    AgentStatus
)


@pytest.mark.unit
class TestResponseFormatter:
    """Test response formatting module"""

    def test_format_response_complete(self, sample_waypoints):
        """Test complete response formatting"""
        # Add enrichment to waypoints
        for wp in sample_waypoints[:2]:
            wp.enrichment = WaypointEnrichment(
                selected_content=ContentItem(
                    content_type=ContentType.VIDEO,
                    title=f"Video for {wp.location_name}",
                    description="Test description",
                    relevance_score=0.85,
                    url="https://youtube.com/test"
                ),
                all_agent_results={},
                judge_decision=JudgeDecision(
                    winner="youtube",
                    reasoning="Best content",
                    confidence_score=0.85,
                    individual_scores={"youtube": 0.85},
                    decision_time_ms=50,
                    tie_breaker_applied=False,
                    selected_content=None
                ),
                processing_time_ms=200
            )

        final_route = FinalRoute(
            transaction_id="TXID-test-123",
            waypoints=sample_waypoints,
            route_metadata={"distance": "10 km", "duration": "15 mins"},
            statistics=RouteStatistics(
                total_waypoints=len(sample_waypoints),
                enriched_waypoints=2,
                failed_waypoints=0,
                total_processing_time_ms=5000,
                average_processing_time_ms=250.0,
                content_breakdown={"video": 2}
            )
        )

        response = format_response(final_route)

        # Verify structure
        assert "transaction_id" in response
        assert response["transaction_id"] == "TXID-test-123"
        assert "route" in response
        assert "statistics" in response
        assert "metadata" in response

        # Verify route summary
        assert response["route"]["summary"]["total_distance"] == "10 km"
        assert response["route"]["summary"]["total_duration"] == "15 mins"
        assert response["route"]["summary"]["total_waypoints"] == len(sample_waypoints)
        assert response["route"]["summary"]["enriched_count"] == 2

        # Verify waypoints
        assert len(response["route"]["waypoints"]) == len(sample_waypoints)

        # Verify metadata
        assert "timestamp" in response["metadata"]
        assert "version" in response["metadata"]

    def test_format_waypoints_with_enrichment(self):
        """Test waypoint formatting with enrichment"""
        waypoint = Waypoint(
            id=1,
            location_name="Test Location",
            coordinates=Coordinates(lat=40.7128, lng=-74.0060),
            instruction="Go north",
            distance_from_start=1500.0,
            step_index=0
        )

        content = ContentItem(
            content_type=ContentType.SONG,
            title="Test Song",
            description="A great song",
            relevance_score=0.90,
            url="https://spotify.com/test",
            metadata={"artist": "Test Artist", "album": "Test Album"}
        )

        waypoint.enrichment = WaypointEnrichment(
            selected_content=content,
            all_agent_results={},
            judge_decision=JudgeDecision(
                winner="spotify",
                reasoning="Best music",
                confidence_score=0.90,
                individual_scores={"spotify": 0.90},
                decision_time_ms=100,
                tie_breaker_applied=False,
                selected_content=content
            ),
            processing_time_ms=300
        )

        formatted = _format_waypoints([waypoint])

        assert len(formatted) == 1
        wp = formatted[0]

        assert wp["step"] == 1
        assert wp["location"] == "Test Location"
        assert wp["coordinates"]["lat"] == 40.7128
        assert wp["coordinates"]["lng"] == -74.0060
        assert wp["instruction"] == "Go north"
        assert "1.5 km" in wp["distance_from_start"]

        # Check content
        assert "content" in wp
        assert wp["content"]["type"] == "song"
        assert wp["content"]["title"] == "Test Song"
        assert wp["content"]["artist"] == "Test Artist"
        assert wp["content"]["album"] == "Test Album"

        # Check decision
        assert "decision" in wp
        assert wp["decision"]["winner"] == "spotify"

    def test_format_waypoints_without_enrichment(self):
        """Test waypoint formatting without enrichment"""
        waypoint = Waypoint(
            id=1,
            location_name="Test Location",
            coordinates=Coordinates(lat=40.7128, lng=-74.0060),
            instruction="Go north",
            distance_from_start=500.0,
            step_index=0
        )

        formatted = _format_waypoints([waypoint])

        assert len(formatted) == 1
        wp = formatted[0]

        assert wp["step"] == 1
        assert "content" in wp
        assert wp["content"]["type"] == "none"
        assert "No content available" in wp["content"]["title"]

    def test_format_waypoints_with_history_content(self):
        """Test formatting waypoint with history content (no URL)"""
        waypoint = Waypoint(
            id=1,
            location_name="Historical Site",
            coordinates=Coordinates(lat=40.7128, lng=-74.0060),
            instruction="Visit site",
            distance_from_start=2500.0,
            step_index=0
        )

        content = ContentItem(
            content_type=ContentType.HISTORY,
            title="History of Site",
            description="Historical facts",
            relevance_score=0.75,
            url=None  # History content has no URL
        )

        waypoint.enrichment = WaypointEnrichment(
            selected_content=content,
            all_agent_results={},
            judge_decision=JudgeDecision(
                winner="history",
                reasoning="Good historical content",
                confidence_score=0.75,
                individual_scores={"history": 0.75},
                decision_time_ms=80,
                tie_breaker_applied=False,
                selected_content=content
            ),
            processing_time_ms=250
        )

        formatted = _format_waypoints([waypoint])

        assert len(formatted) == 1
        wp = formatted[0]

        assert wp["content"]["type"] == "history"
        assert wp["content"]["url"] is None

    def test_format_duration_ms_milliseconds(self):
        """Test formatting durations less than 1 second"""
        assert _format_duration_ms(500) == "500 ms"
        assert _format_duration_ms(999) == "999 ms"

    def test_format_duration_ms_seconds(self):
        """Test formatting durations in seconds"""
        assert _format_duration_ms(1000) == "1.0 seconds"
        assert _format_duration_ms(5500) == "5.5 seconds"
        assert _format_duration_ms(30000) == "30.0 seconds"

    def test_format_duration_ms_minutes(self):
        """Test formatting durations in minutes"""
        assert _format_duration_ms(60000) == "1.0 minutes"
        assert _format_duration_ms(150000) == "2.5 minutes"
        assert _format_duration_ms(300000) == "5.0 minutes"

    def test_format_distance_meters_meters(self):
        """Test formatting distances less than 1 km"""
        assert _format_distance_meters(0) == "0 m"
        assert _format_distance_meters(500) == "500 m"
        assert _format_distance_meters(999) == "999 m"

    def test_format_distance_meters_kilometers(self):
        """Test formatting distances in kilometers"""
        assert _format_distance_meters(1000) == "1.0 km"
        assert _format_distance_meters(2500) == "2.5 km"
        assert _format_distance_meters(10000) == "10.0 km"
        assert _format_distance_meters(1234.5) == "1.2 km"

    def test_format_response_empty_waypoints(self):
        """Test formatting response with no waypoints"""
        final_route = FinalRoute(
            transaction_id="TXID-empty-123",
            waypoints=[],
            route_metadata={"distance": "0 km", "duration": "0 mins"},
            statistics=RouteStatistics(
                total_waypoints=0,
                enriched_waypoints=0,
                failed_waypoints=0,
                total_processing_time_ms=100,
                average_processing_time_ms=0.0,
                content_breakdown={}
            )
        )

        response = format_response(final_route)

        assert response["route"]["summary"]["total_waypoints"] == 0
        assert response["route"]["summary"]["enriched_count"] == 0
        assert len(response["route"]["waypoints"]) == 0

    def test_format_response_zero_enrichment(self, sample_waypoints):
        """Test formatting when no waypoints were enriched"""
        final_route = FinalRoute(
            transaction_id="TXID-no-enrichment",
            waypoints=sample_waypoints,
            route_metadata={"distance": "5 km", "duration": "10 mins"},
            statistics=RouteStatistics(
                total_waypoints=len(sample_waypoints),
                enriched_waypoints=0,
                failed_waypoints=len(sample_waypoints),
                total_processing_time_ms=2000,
                average_processing_time_ms=100.0,
                content_breakdown={}
            )
        )

        response = format_response(final_route)

        assert response["route"]["summary"]["enriched_count"] == 0
        assert response["route"]["summary"]["success_rate"] == "0.0%"

    def test_format_waypoints_with_metadata_variations(self):
        """Test waypoint formatting with different metadata combinations"""
        waypoint = Waypoint(
            id=1,
            location_name="Test Location",
            coordinates=Coordinates(lat=40.7128, lng=-74.0060),
            instruction="Go",
            distance_from_start=1000.0,
            step_index=0
        )

        # Content with only artist metadata
        content = ContentItem(
            content_type=ContentType.SONG,
            title="Test Song",
            description="Test song description",
            relevance_score=0.80,
            url="https://spotify.com/test",
            metadata={"artist": "Test Artist"}  # Only artist, no album
        )

        waypoint.enrichment = WaypointEnrichment(
            selected_content=content,
            all_agent_results={},
            judge_decision=JudgeDecision(
                winner="spotify",
                reasoning="Good",
                confidence_score=0.80,
                individual_scores={},
                decision_time_ms=50,
                tie_breaker_applied=False,
                selected_content=content
            ),
            processing_time_ms=200
        )

        formatted = _format_waypoints([waypoint])

        assert formatted[0]["content"]["artist"] == "Test Artist"
        assert "album" not in formatted[0]["content"]
