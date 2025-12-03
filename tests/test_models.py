"""
Unit tests for src/models.py
Tests all data structures and helper functions
"""

import pytest
from datetime import datetime
import time

from src.models import (
    Coordinates,
    ContentType,
    AgentStatus,
    LocationType,
    WaypointMetadata,
    ContentItem,
    AgentResult,
    JudgeDecision,
    Waypoint,
    RouteData,
    TransactionContext,
    RouteStatistics,
    FinalRoute,
    create_transaction_id,
    create_fallback_content,
    create_timeout_result,
    create_error_result
)


@pytest.mark.unit
class TestCoordinates:
    """Test Coordinates data structure"""

    def test_coordinates_creation(self):
        coords = Coordinates(lat=40.7128, lng=-74.0060)
        assert coords.lat == 40.7128
        assert coords.lng == -74.0060

    def test_coordinates_string_representation(self):
        coords = Coordinates(lat=40.7128, lng=-74.0060)
        result = str(coords)
        assert "40.712800" in result
        assert "-74.006000" in result


@pytest.mark.unit
class TestContentItem:
    """Test ContentItem data structure"""

    def test_content_item_creation(self):
        content = ContentItem(
            content_type=ContentType.VIDEO,
            title="Test Video",
            description="Test description",
            relevance_score=0.85,
            url="https://youtube.com/test"
        )
        assert content.content_type == ContentType.VIDEO
        assert content.title == "Test Video"
        assert content.relevance_score == 0.85

    def test_content_item_to_dict(self):
        content = ContentItem(
            content_type=ContentType.SONG,
            title="Test Song",
            description="A test song",
            relevance_score=0.90,
            url="https://spotify.com/test",
            metadata={"artist": "Test Artist"}
        )
        result = content.to_dict()
        assert result["type"] == "song"
        assert result["title"] == "Test Song"
        assert result["relevance_score"] == 0.90
        assert result["metadata"]["artist"] == "Test Artist"


@pytest.mark.unit
class TestAgentResult:
    """Test AgentResult data structure"""

    def test_successful_agent_result(self, sample_content_item):
        result = AgentResult(
            agent_name="youtube",
            transaction_id="TXID-test-123",
            waypoint_id=1,
            status=AgentStatus.SUCCESS,
            content=sample_content_item,
            execution_time_ms=500
        )
        assert result.is_successful()
        assert result.agent_name == "youtube"

    def test_failed_agent_result(self):
        result = AgentResult(
            agent_name="youtube",
            transaction_id="TXID-test-123",
            waypoint_id=1,
            status=AgentStatus.ERROR,
            content=None,
            error_message="API timeout"
        )
        assert not result.is_successful()
        assert result.error_message == "API timeout"

    def test_agent_result_to_dict(self, sample_agent_result):
        result_dict = sample_agent_result.to_dict()
        assert result_dict["agent_name"] == "youtube"
        assert result_dict["status"] == "success"
        assert result_dict["content"] is not None


@pytest.mark.unit
class TestWaypoint:
    """Test Waypoint data structure"""

    def test_waypoint_creation(self, sample_coordinates):
        waypoint = Waypoint(
            id=1,
            location_name="Test Location",
            coordinates=sample_coordinates,
            instruction="Turn right",
            distance_from_start=1000.0
        )
        assert waypoint.id == 1
        assert waypoint.location_name == "Test Location"
        assert not waypoint.is_enriched()

    def test_waypoint_to_dict(self, sample_waypoint):
        result = sample_waypoint.to_dict()
        assert result["id"] == 1
        assert result["location_name"] == "5th Ave & 42nd St"
        assert result["coordinates"]["lat"] == 40.7128


@pytest.mark.unit
class TestTransactionContext:
    """Test TransactionContext data structure"""

    def test_context_creation(self):
        context = TransactionContext(
            transaction_id="TXID-test-123",
            origin="Start",
            destination="End"
        )
        assert context.transaction_id == "TXID-test-123"
        assert context.current_stage == "initialization"

    def test_stage_transition(self):
        context = TransactionContext(
            transaction_id="TXID-test-123",
            origin="Start",
            destination="End"
        )
        context.log_stage_entry("validation")
        assert context.current_stage == "validation"

    def test_metadata_addition(self):
        context = TransactionContext(
            transaction_id="TXID-test-123",
            origin="Start",
            destination="End"
        )
        context.add_metadata("test_key", "test_value")
        assert context.metadata["test_key"] == "test_value"

    def test_elapsed_time(self):
        context = TransactionContext(
            transaction_id="TXID-test-123",
            origin="Start",
            destination="End"
        )
        time.sleep(0.1)  # Sleep for 100ms
        elapsed = context.get_elapsed_time_ms()
        assert elapsed >= 100


@pytest.mark.unit
class TestRouteStatistics:
    """Test RouteStatistics data structure"""

    def test_statistics_creation(self):
        stats = RouteStatistics(
            total_waypoints=10,
            enriched_waypoints=8,
            failed_waypoints=2,
            total_processing_time_ms=5000,
            average_processing_time_ms=500.0,
            content_breakdown={"video": 3, "music": 3, "history": 2}
        )
        assert stats.total_waypoints == 10
        assert stats.success_rate() == 0.8

    def test_zero_waypoints_success_rate(self):
        stats = RouteStatistics(
            total_waypoints=0,
            enriched_waypoints=0,
            failed_waypoints=0,
            total_processing_time_ms=0,
            average_processing_time_ms=0.0,
            content_breakdown={}
        )
        assert stats.success_rate() == 0.0


@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions"""

    def test_create_transaction_id(self):
        txid = create_transaction_id()
        assert txid.startswith("TXID-")
        assert len(txid) > 20

    def test_unique_transaction_ids(self):
        txid1 = create_transaction_id()
        txid2 = create_transaction_id()
        assert txid1 != txid2

    def test_create_fallback_content(self, sample_waypoint):
        content = create_fallback_content(sample_waypoint)
        assert content.content_type == ContentType.FALLBACK
        assert sample_waypoint.location_name in content.description
        assert content.relevance_score == 0.0

    def test_create_timeout_result(self):
        result = create_timeout_result("youtube", "TXID-test", 1, 5000)
        assert result.status == AgentStatus.TIMEOUT
        assert result.execution_time_ms == 5000
        assert "timeout" in result.error_message.lower()

    def test_create_error_result(self):
        error = ValueError("Test error")
        result = create_error_result("youtube", "TXID-test", 1, error)
        assert result.status == AgentStatus.ERROR
        assert "Test error" in result.error_message
