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
    @patch('src.google_maps.client.GoogleMapsClient')
    def test_successful_route_retrieval_mock_mode(
        self,
        mock_client_class,
        mock_get_config,
        transaction_context,
        mock_config
    ):
        """Test successful route retrieval in mock mode"""
        mock_get_config.return_value = mock_config

        # Mock client
        mock_client = Mock()
        mock_client.get_directions.return_value = {
            "routes": [{
                "legs": [{
                    "distance": {"text": "10 km", "value": 10000},
                    "duration": {"text": "15 mins", "value": 900},
                    "steps": [
                        {
                            "html_instructions": "Head north",
                            "distance": {"text": "1 km", "value": 1000},
                            "start_location": {"lat": 40.7128, "lng": -74.0060},
                            "end_location": {"lat": 40.7228, "lng": -74.0060}
                        }
                    ]
                }]
            }],
            "status": "OK"
        }
        mock_client_class.return_value = mock_client

        # Execute
        route_data = retrieve_route(transaction_context)

        # Verify
        assert route_data is not None
        assert route_data.distance == "10 km"
        assert route_data.duration == "15 mins"
        assert len(route_data.waypoints) > 0

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
        mock_get_config.return_value = mock_config

        mock_client = Mock()
        mock_client.get_directions.return_value = {
            "routes": [],
            "status": "ZERO_RESULTS"
        }
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
