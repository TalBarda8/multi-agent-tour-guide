"""
Unit tests for src/modules/waypoint_preprocessor.py
Tests waypoint metadata enrichment and query generation
"""

import pytest
from src.modules.waypoint_preprocessor import preprocess_waypoints
from src.models import LocationType


@pytest.mark.unit
class TestWaypointPreprocessor:
    """Test waypoint preprocessing module"""

    def test_preprocess_adds_metadata(self, transaction_context, sample_route_data):
        """Test that preprocessing adds metadata to waypoints"""
        processed = preprocess_waypoints(transaction_context, sample_route_data)

        assert len(processed) > 0
        for waypoint in processed:
            # Metadata should be added
            assert waypoint.metadata is not None or waypoint.agent_context is not None

    def test_preprocess_preserves_waypoint_data(
        self,
        transaction_context,
        sample_route_data
    ):
        """Test that preprocessing preserves original waypoint data"""
        original_waypoints = sample_route_data.waypoints
        processed = preprocess_waypoints(transaction_context, sample_route_data)

        assert len(processed) == len(original_waypoints)
        for original, processed_wp in zip(original_waypoints, processed):
            assert processed_wp.id == original.id
            assert processed_wp.location_name == original.location_name
            assert processed_wp.coordinates.lat == original.coordinates.lat
            assert processed_wp.coordinates.lng == original.coordinates.lng

    def test_preprocess_generates_agent_context(
        self,
        transaction_context,
        sample_route_data
    ):
        """Test that preprocessing generates agent context with search queries"""
        processed = preprocess_waypoints(transaction_context, sample_route_data)

        for waypoint in processed:
            if waypoint.agent_context:
                # Should have queries for all agent types
                assert hasattr(waypoint.agent_context, 'youtube_query')
                assert hasattr(waypoint.agent_context, 'spotify_query')
                assert hasattr(waypoint.agent_context, 'history_query')

    def test_preprocess_updates_context_stage(
        self,
        transaction_context,
        sample_route_data
    ):
        """Test that preprocessing updates transaction context stage"""
        preprocess_waypoints(transaction_context, sample_route_data)
        # Stage should have been updated
        assert transaction_context.current_stage is not None

    def test_preprocess_empty_waypoints(self, transaction_context, sample_route_data):
        """Test preprocessing handles empty waypoint list"""
        sample_route_data.waypoints = []
        processed = preprocess_waypoints(transaction_context, sample_route_data)
        assert len(processed) == 0

    def test_preprocess_location_type_classification(
        self,
        transaction_context,
        sample_route_data
    ):
        """Test that preprocessing classifies location types"""
        processed = preprocess_waypoints(transaction_context, sample_route_data)

        for waypoint in processed:
            if waypoint.metadata:
                # Location type should be classified
                assert isinstance(waypoint.metadata.location_type, LocationType)
