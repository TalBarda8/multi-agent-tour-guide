"""
Module 2: Route Retrieval
Fetches route data from Google Maps Directions API
"""

import time
from typing import List, Dict, Any

from src.models import TransactionContext, RouteData, Waypoint, Coordinates
from src.logging_config import get_logger
from src.config import get_config


class RouteRetrievalError(Exception):
    """Raised when route retrieval fails"""
    pass


def retrieve_route(context: TransactionContext) -> RouteData:
    """
    Fetch route data from Google Maps Directions API

    Input Contract:
        - TransactionContext with origin and destination

    Output Contract:
        - RouteData object with waypoints and route metadata

    Raises:
        - RouteRetrievalError if route cannot be retrieved

    Args:
        context: Transaction context with origin/destination

    Returns:
        RouteData with waypoints extracted from route
    """
    logger = get_logger()
    config = get_config()

    # Update stage
    context.log_stage_entry("route_retrieval")

    logger.log_stage_entry(
        "route_retrieval",
        context.transaction_id,
        origin=context.origin,
        destination=context.destination
    )

    start_time = time.time()

    try:
        if config.mock_mode:
            # Use mock data during development
            route_data = _retrieve_route_mock(context)
        else:
            # Real Google Maps API call (to be implemented in Phase 4)
            route_data = _retrieve_route_real(context)

        # Calculate processing time
        duration_ms = int((time.time() - start_time) * 1000)

        # Log successful retrieval
        logger.info(
            "Route retrieved successfully",
            transaction_id=context.transaction_id,
            waypoint_count=len(route_data.waypoints),
            total_distance=route_data.distance,
            api_response_time_ms=duration_ms
        )

        logger.log_stage_exit(
            "route_retrieval",
            context.transaction_id,
            duration_ms=duration_ms,
            waypoint_count=len(route_data.waypoints)
        )

        return route_data

    except Exception as e:
        logger.error(
            "Route retrieval failed",
            transaction_id=context.transaction_id,
            error=str(e),
            exc_info=True
        )
        raise RouteRetrievalError(f"Failed to retrieve route: {str(e)}")


def _retrieve_route_mock(context: TransactionContext) -> RouteData:
    """
    Mock route retrieval for development
    Returns hardcoded waypoints for testing

    Args:
        context: Transaction context

    Returns:
        Mock RouteData
    """
    # Create mock waypoints based on origin/destination
    # For now, create a simple route with 8 waypoints
    mock_waypoints = [
        Waypoint(
            id=1,
            location_name="5th Avenue & E 34th St",
            coordinates=Coordinates(lat=40.748817, lng=-73.985428),
            instruction="Head north on 5th Ave",
            distance_from_start=0.0,
            step_index=0
        ),
        Waypoint(
            id=2,
            location_name="5th Avenue & E 42nd St",
            coordinates=Coordinates(lat=40.753182, lng=-73.981736),
            instruction="Continue on 5th Ave",
            distance_from_start=804.5,
            step_index=1
        ),
        Waypoint(
            id=3,
            location_name="5th Avenue & E 50th St",
            coordinates=Coordinates(lat=40.758402, lng=-73.977459),
            instruction="Continue on 5th Ave",
            distance_from_start=1650.2,
            step_index=2
        ),
        Waypoint(
            id=4,
            location_name="5th Avenue & E 59th St",
            coordinates=Coordinates(lat=40.764526, lng=-73.973448),
            instruction="Turn left onto Central Park S",
            distance_from_start=2410.8,
            step_index=3
        ),
        Waypoint(
            id=5,
            location_name="Central Park South & 6th Ave",
            coordinates=Coordinates(lat=40.765187, lng=-73.976345),
            instruction="Continue to Central Park",
            distance_from_start=2650.3,
            step_index=4
        ),
        Waypoint(
            id=6,
            location_name="Central Park - The Pond",
            coordinates=Coordinates(lat=40.767456, lng=-73.974821),
            instruction="Enter Central Park",
            distance_from_start=2890.7,
            step_index=5
        ),
        Waypoint(
            id=7,
            location_name="Central Park - Bethesda Terrace",
            coordinates=Coordinates(lat=40.772932, lng=-73.971589),
            instruction="Continue through Central Park",
            distance_from_start=3200.4,
            step_index=6
        ),
        Waypoint(
            id=8,
            location_name="Central Park - Belvedere Castle",
            coordinates=Coordinates(lat=40.779267, lng=-73.969083),
            instruction="Arrive at destination",
            distance_from_start=3450.9,
            step_index=7
        ),
    ]

    return RouteData(
        distance="3.5 km",
        duration="12 mins",
        waypoints=mock_waypoints,
        steps=[]  # Raw steps not needed for mock
    )


def _retrieve_route_real(context: TransactionContext) -> RouteData:
    """
    Real Google Maps API integration

    Args:
        context: Transaction context

    Returns:
        RouteData from Google Maps API

    Raises:
        RouteRetrievalError: If route cannot be retrieved
    """
    from src.google_maps import GoogleMapsClient, GoogleMapsError

    logger = get_logger()

    try:
        # Create Google Maps client
        client = GoogleMapsClient()

        # Get directions
        route_data = client.get_directions(
            origin=context.origin,
            destination=context.destination,
            mode="driving"
        )

        logger.info(
            "Successfully retrieved route from Google Maps",
            transaction_id=context.transaction_id,
            waypoint_count=len(route_data.waypoints),
            distance=route_data.distance
        )

        return route_data

    except GoogleMapsError as e:
        logger.error(
            "Google Maps API error",
            transaction_id=context.transaction_id,
            error=str(e)
        )
        raise RouteRetrievalError(f"Failed to get route from Google Maps: {str(e)}")

    except Exception as e:
        logger.error(
            "Unexpected error retrieving route",
            transaction_id=context.transaction_id,
            error=str(e),
            exc_info=True
        )
        raise RouteRetrievalError(f"Unexpected error: {str(e)}")
