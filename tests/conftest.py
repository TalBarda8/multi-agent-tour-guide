"""
PyTest configuration and fixtures
Provides reusable test fixtures for all test modules
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    TransactionContext,
    Waypoint,
    Coordinates,
    WaypointMetadata,
    LocationType,
    ContentItem,
    ContentType,
    AgentResult,
    AgentStatus,
    JudgeDecision,
    RouteData,
    create_transaction_id
)
from src.config import SystemConfig, set_config


@pytest.fixture
def mock_config():
    """
    Provides a test configuration with mock mode enabled
    """
    config = SystemConfig(
        google_maps_api_key="test_key",
        youtube_api_key="test_youtube_key",
        spotify_client_id="test_spotify_id",
        spotify_client_secret="test_spotify_secret",
        agent_timeout_ms=5000,
        judge_timeout_ms=3000,
        route_retrieval_timeout_ms=10000,
        max_concurrent_waypoints=5,
        max_agent_threads=50,
        log_level="DEBUG",
        log_file_path="./test_logs/test.log",
        log_max_size_mb=10,
        log_backup_count=2,
        enable_caching=False,
        cache_ttl_seconds=3600,
        mock_mode=True
    )
    set_config(config)
    return config


@pytest.fixture
def transaction_context():
    """
    Provides a sample transaction context for testing
    """
    return TransactionContext(
        transaction_id=create_transaction_id(),
        origin="Test Origin",
        destination="Test Destination",
        user_preferences={"content_type": "auto"}
    )


@pytest.fixture
def sample_coordinates():
    """
    Provides sample coordinates
    """
    return Coordinates(lat=40.7128, lng=-74.0060)


@pytest.fixture
def sample_waypoint(sample_coordinates):
    """
    Provides a sample waypoint for testing
    """
    metadata = WaypointMetadata(
        location_type=LocationType.INTERSECTION,
        nearby_landmarks=["Central Park", "Times Square"],
        neighborhood="Manhattan",
        search_keywords=["new york", "intersection"]
    )

    return Waypoint(
        id=1,
        location_name="5th Ave & 42nd St",
        coordinates=sample_coordinates,
        instruction="Turn right onto 5th Avenue",
        distance_from_start=1500.0,
        step_index=3,
        metadata=metadata
    )


@pytest.fixture
def sample_waypoints(sample_coordinates):
    """
    Provides a list of sample waypoints
    """
    return [
        Waypoint(
            id=i,
            location_name=f"Location {i}",
            coordinates=Coordinates(
                lat=sample_coordinates.lat + i * 0.01,
                lng=sample_coordinates.lng + i * 0.01
            ),
            instruction=f"Continue for {i} km",
            distance_from_start=i * 1000.0,
            step_index=i
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_content_item():
    """
    Provides a sample content item
    """
    return ContentItem(
        content_type=ContentType.VIDEO,
        title="Test Video",
        description="A test video about the location",
        relevance_score=0.85,
        url="https://youtube.com/watch?v=test",
        metadata={"duration": "5:30", "views": 10000}
    )


@pytest.fixture
def sample_agent_result(transaction_context, sample_content_item):
    """
    Provides a sample successful agent result
    """
    return AgentResult(
        agent_name="youtube",
        transaction_id=transaction_context.transaction_id,
        waypoint_id=1,
        status=AgentStatus.SUCCESS,
        content=sample_content_item,
        error_message=None,
        execution_time_ms=450
    )


@pytest.fixture
def sample_judge_decision(sample_content_item):
    """
    Provides a sample judge decision
    """
    return JudgeDecision(
        winner="youtube",
        reasoning="Video content provides the most engaging experience for this landmark",
        confidence_score=0.87,
        individual_scores={
            "youtube": 0.85,
            "spotify": 0.72,
            "history": 0.68
        },
        decision_time_ms=250,
        tie_breaker_applied=False,
        selected_content=sample_content_item
    )


@pytest.fixture
def sample_route_data(sample_waypoints):
    """
    Provides sample route data
    """
    return RouteData(
        distance="15.2 km",
        duration="23 mins",
        waypoints=sample_waypoints,
        steps=[
            {"instruction": "Head north", "distance": "500 m"},
            {"instruction": "Turn right", "distance": "1.2 km"},
        ]
    )


@pytest.fixture
def mock_google_maps_response():
    """
    Provides a mock Google Maps API response
    """
    return {
        "routes": [
            {
                "legs": [
                    {
                        "distance": {"text": "15.2 km", "value": 15200},
                        "duration": {"text": "23 mins", "value": 1380},
                        "steps": [
                            {
                                "html_instructions": "Head <b>north</b> on Main St",
                                "distance": {"text": "0.5 km", "value": 500},
                                "duration": {"text": "2 mins", "value": 120},
                                "start_location": {"lat": 40.7128, "lng": -74.0060},
                                "end_location": {"lat": 40.7178, "lng": -74.0060}
                            },
                            {
                                "html_instructions": "Turn <b>right</b> onto 5th Ave",
                                "distance": {"text": "1.2 km", "value": 1200},
                                "duration": {"text": "5 mins", "value": 300},
                                "start_location": {"lat": 40.7178, "lng": -74.0060},
                                "end_location": {"lat": 40.7178, "lng": -73.9950}
                            }
                        ]
                    }
                ]
            }
        ],
        "status": "OK"
    }


@pytest.fixture
def mock_youtube_api_response():
    """
    Provides a mock YouTube API response
    """
    return {
        "items": [
            {
                "id": {"videoId": "test123"},
                "snippet": {
                    "title": "Amazing NYC Tour - Times Square",
                    "description": "A comprehensive tour of Times Square in New York City",
                    "thumbnails": {
                        "default": {"url": "https://example.com/thumb.jpg"}
                    }
                }
            }
        ]
    }


@pytest.fixture
def mock_logger():
    """
    Provides a mock logger for testing
    """
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    logger.log_stage_entry = Mock()
    logger.log_stage_exit = Mock()
    return logger


# Test markers
def pytest_configure(config):
    """
    Register custom markers for test organization
    """
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for module interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take significant time to run"
    )
    config.addinivalue_line(
        "markers", "api: Tests that interact with external APIs"
    )
