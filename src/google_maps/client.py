"""
Google Maps Directions API Client
Handles route retrieval and waypoint extraction
"""

import time
from typing import List, Dict, Any, Optional
import urllib.parse
import urllib.request
import json

from src.models import RouteData, Waypoint, Coordinates
from src.logging_config import get_logger
from src.config import get_config


class GoogleMapsError(Exception):
    """Raised when Google Maps API returns an error"""
    pass


class GoogleMapsClient:
    """
    Client for Google Maps Directions API
    Retrieves routes and extracts waypoints from directions
    """

    BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self.api_key = self.config.google_maps_api_key

        if not self.api_key and not self.config.mock_mode:
            raise GoogleMapsError(
                "Google Maps API key not configured. "
                "Set GOOGLE_MAPS_API_KEY in .env file or enable MOCK_MODE=true"
            )

    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving"
    ) -> RouteData:
        """
        Get directions from Google Maps API

        Args:
            origin: Starting address or place name
            destination: Ending address or place name
            mode: Travel mode (driving, walking, bicycling, transit)

        Returns:
            RouteData with extracted waypoints

        Raises:
            GoogleMapsError: If API call fails or no route found
        """
        # Build API request URL
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": self.api_key
        }

        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

        self.logger.debug(
            "Calling Google Maps API",
            origin=origin,
            destination=destination,
            mode=mode
        )

        start_time = time.time()

        try:
            # Make API request
            with urllib.request.urlopen(url, timeout=self.config.route_retrieval_timeout_ms / 1000) as response:
                data = json.loads(response.read().decode())

            response_time_ms = int((time.time() - start_time) * 1000)

            # Check API status
            status = data.get("status")

            if status != "OK":
                error_message = self._get_error_message(status, data)
                self.logger.error(
                    f"Google Maps API error: {status}",
                    status=status,
                    error_message=error_message
                )
                raise GoogleMapsError(error_message)

            # Parse response and extract route data
            route_data = self._parse_directions_response(data)

            self.logger.info(
                "Google Maps API call successful",
                waypoint_count=len(route_data.waypoints),
                total_distance=route_data.distance,
                response_time_ms=response_time_ms
            )

            return route_data

        except urllib.error.URLError as e:
            self.logger.error(
                "Network error calling Google Maps API",
                error=str(e),
                exc_info=True
            )
            raise GoogleMapsError(f"Network error: {str(e)}")

        except json.JSONDecodeError as e:
            self.logger.error(
                "Failed to parse Google Maps API response",
                error=str(e),
                exc_info=True
            )
            raise GoogleMapsError(f"Invalid API response: {str(e)}")

        except Exception as e:
            self.logger.error(
                "Unexpected error calling Google Maps API",
                error=str(e),
                exc_info=True
            )
            raise GoogleMapsError(f"Unexpected error: {str(e)}")

    def _parse_directions_response(self, data: Dict[str, Any]) -> RouteData:
        """
        Parse Google Maps directions response and extract waypoints

        Args:
            data: Raw API response

        Returns:
            RouteData with waypoints extracted from steps
        """
        try:
            # Get the first route (Google Maps can return alternatives)
            route = data["routes"][0]
            leg = route["legs"][0]  # Assuming single leg (no intermediate stops)

            # Extract overall route information
            distance = leg["distance"]["text"]
            duration = leg["duration"]["text"]
            steps = leg["steps"]

            # Extract waypoints from steps
            waypoints = self._extract_waypoints_from_steps(steps)

            return RouteData(
                distance=distance,
                duration=duration,
                waypoints=waypoints,
                steps=steps
            )

        except (KeyError, IndexError) as e:
            self.logger.error(
                "Failed to parse route from response",
                error=str(e),
                exc_info=True
            )
            raise GoogleMapsError(f"Invalid route structure in API response: {str(e)}")

    def _extract_waypoints_from_steps(self, steps: List[Dict[str, Any]]) -> List[Waypoint]:
        """
        Extract waypoints from navigation steps

        Each step in Google Maps directions represents a maneuver.
        We create a waypoint for each significant step.

        Args:
            steps: List of navigation steps from API

        Returns:
            List of Waypoint objects
        """
        waypoints = []
        cumulative_distance = 0.0

        for idx, step in enumerate(steps):
            try:
                # Extract location data
                start_location = step["start_location"]
                end_location = step["end_location"]

                # Get instruction (remove HTML tags)
                instruction = self._clean_html_instruction(step["html_instructions"])

                # Calculate distance
                distance_meters = step["distance"]["value"]
                cumulative_distance += distance_meters

                # Create location name from instruction or address
                location_name = self._extract_location_name(instruction, start_location)

                # Create waypoint
                waypoint = Waypoint(
                    id=idx + 1,
                    location_name=location_name,
                    coordinates=Coordinates(
                        lat=start_location["lat"],
                        lng=start_location["lng"]
                    ),
                    instruction=instruction,
                    distance_from_start=cumulative_distance,
                    step_index=idx
                )

                waypoints.append(waypoint)

            except (KeyError, ValueError) as e:
                self.logger.warning(
                    f"Failed to parse step {idx}",
                    error=str(e)
                )
                continue

        return waypoints

    def _clean_html_instruction(self, html_instruction: str) -> str:
        """
        Remove HTML tags from instruction text

        Args:
            html_instruction: Instruction with HTML tags

        Returns:
            Clean text instruction
        """
        # Simple HTML tag removal (more robust parsing could use html.parser)
        import re
        clean = re.sub('<[^<]+?>', '', html_instruction)
        return clean.strip()

    def _extract_location_name(
        self,
        instruction: str,
        location: Dict[str, float]
    ) -> str:
        """
        Extract a meaningful location name from instruction or coordinates

        Args:
            instruction: Navigation instruction
            location: Lat/lng dictionary

        Returns:
            Location name suitable for display
        """
        # Try to extract street names from instruction
        # e.g., "Turn right onto Main St" -> "Main St"
        import re

        # Pattern: "onto X" or "on X" or "toward X"
        patterns = [
            r'onto\s+([^,\.]+)',
            r'on\s+([^,\.]+)',
            r'toward\s+([^,\.]+)',
            r'at\s+([^,\.]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                location_name = match.group(1).strip()
                # Clean up common suffixes
                location_name = re.sub(r'\s*\(.*?\)', '', location_name)
                if len(location_name) > 3:
                    return location_name

        # Fallback: use coordinates
        return f"{location['lat']:.4f}, {location['lng']:.4f}"

    def _get_error_message(self, status: str, data: Dict[str, Any]) -> str:
        """
        Get user-friendly error message based on API status

        Args:
            status: API status code
            data: Full API response

        Returns:
            Error message
        """
        error_messages = {
            "NOT_FOUND": "No route found between the specified locations",
            "ZERO_RESULTS": "No route could be calculated between these locations",
            "MAX_WAYPOINTS_EXCEEDED": "Too many waypoints specified",
            "INVALID_REQUEST": "Invalid request parameters",
            "REQUEST_DENIED": "API key is invalid or request was denied",
            "UNKNOWN_ERROR": "Unknown error occurred",
            "OVER_QUERY_LIMIT": "API query limit exceeded"
        }

        base_message = error_messages.get(status, f"API error: {status}")

        # Add additional error message if available
        if "error_message" in data:
            base_message += f" - {data['error_message']}"

        return base_message


def reverse_geocode(lat: float, lng: float, api_key: str) -> Optional[str]:
    """
    Reverse geocode coordinates to get address
    Optional utility function for future use

    Args:
        lat: Latitude
        lng: Longitude
        api_key: Google Maps API key

    Returns:
        Address string or None if failed
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lng}",
        "key": api_key
    }

    try:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(full_url, timeout=5) as response:
            data = json.loads(response.read().decode())

        if data["status"] == "OK" and data["results"]:
            return data["results"][0]["formatted_address"]

    except Exception:
        pass

    return None
