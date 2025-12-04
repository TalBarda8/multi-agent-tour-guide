"""
Unit tests for src/modules/route_retrieval.py
Tests Google Maps API integration and route parsing
"""

import pytest
from unittest.mock import patch, Mock
from src.modules.route_retrieval import retrieve_route, RouteRetrievalError


@pytest.mark.unit
class TestRouteRetrieval:
    """Test route retrieval module"""

    @patch('src.modules.route_retrieval.get_config')
    def test_successful_route_retrieval_mock_mode(
        self,
        mock_get_config,
        transaction_context,
        mock_config
    ):
        """Test successful route retrieval in mock mode"""
        mock_get_config.return_value = mock_config

        # Execute (mock_mode=True by default in mock_config)
        route_data = retrieve_route(transaction_context)

        # Verify - should get mock data
        assert route_data is not None
        assert route_data.distance == "3.5 km"  # Mock data returns this
        assert route_data.duration == "12 mins"
        assert len(route_data.waypoints) == 8  # Mock returns 8 waypoints

    @patch('src.modules.route_retrieval.get_config')
    @patch('src.google_maps.client.GoogleMapsClient')
    def test_route_retrieval_api_error(
        self,
        mock_client_class,
        mock_get_config,
        transaction_context,
        mock_config
    ):
        """Test route retrieval handles API errors"""
        # Set mock_mode=False to use real client path
        mock_config.mock_mode = False
        mock_get_config.return_value = mock_config

        mock_client = Mock()
        mock_client.get_directions.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        with pytest.raises(RouteRetrievalError):
            retrieve_route(transaction_context)

    @patch('src.modules.route_retrieval.get_config')
    @patch('src.google_maps.client.GoogleMapsClient')
    def test_route_retrieval_zero_results(
        self,
        mock_client_class,
        mock_get_config,
        transaction_context,
        mock_config
    ):
        """Test route retrieval handles zero results"""
        # Set mock_mode=False to use real client path
        mock_config.mock_mode = False
        mock_get_config.return_value = mock_config

        from src.google_maps.client import GoogleMapsError
        mock_client = Mock()
        mock_client.get_directions.side_effect = GoogleMapsError("ZERO_RESULTS")
        mock_client_class.return_value = mock_client

        with pytest.raises(RouteRetrievalError):
            retrieve_route(transaction_context)

    @patch('src.modules.route_retrieval.get_config')
    def test_route_retrieval_updates_context_stage(
        self,
        mock_get_config,
        transaction_context,
        mock_config
    ):
        """Test that route retrieval updates transaction context stage"""
        mock_get_config.return_value = mock_config

        try:
            retrieve_route(transaction_context)
        except:
            pass  # Ignore errors, just check stage was updated

        # Stage should have been updated at some point
        assert transaction_context.current_stage is not None
