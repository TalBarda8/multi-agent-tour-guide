"""
Module 6: Response Formatter
Formats final output for user consumption
"""

import time
from datetime import datetime
from typing import Dict, Any

from src.models import FinalRoute
from src.logging_config import get_logger


def format_response(final_route: FinalRoute) -> Dict[str, Any]:
    """
    Format final output for user consumption

    Input Contract:
        - FinalRoute with all enrichments and statistics

    Output Contract:
        - User-friendly dictionary ready for JSON serialization

    Args:
        final_route: Complete route with all data

    Returns:
        Formatted response dictionary
    """
    logger = get_logger()

    logger.log_stage_entry(
        "response_formatting",
        final_route.transaction_id
    )

    start_time = time.time()

    # Build user-friendly response
    response = {
        "transaction_id": final_route.transaction_id,
        "route": {
            "summary": {
                "total_distance": final_route.route_metadata.get("distance", "N/A"),
                "total_duration": final_route.route_metadata.get("duration", "N/A"),
                "total_waypoints": final_route.statistics.total_waypoints,
                "enriched_count": final_route.statistics.enriched_waypoints,
                "success_rate": f"{final_route.statistics.success_rate() * 100:.1f}%"
            },
            "waypoints": _format_waypoints(final_route.waypoints)
        },
        "statistics": {
            "total_processing_time": _format_duration_ms(
                final_route.statistics.total_processing_time_ms
            ),
            "average_processing_time": _format_duration_ms(
                int(final_route.statistics.average_processing_time_ms)
            ),
            "content_breakdown": final_route.statistics.content_breakdown
        },
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0"
        }
    }

    duration_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "Response formatting completed",
        transaction_id=final_route.transaction_id,
        response_size_bytes=len(str(response))
    )

    logger.log_stage_exit(
        "response_formatting",
        final_route.transaction_id,
        duration_ms=duration_ms
    )

    return response


def _format_waypoints(waypoints) -> list[Dict[str, Any]]:
    """
    Format waypoints for user-friendly output

    Args:
        waypoints: List of enriched waypoints

    Returns:
        List of formatted waypoint dictionaries
    """
    formatted = []

    for waypoint in waypoints:
        wp_data = {
            "step": waypoint.id,
            "location": waypoint.location_name,
            "coordinates": {
                "lat": waypoint.coordinates.lat,
                "lng": waypoint.coordinates.lng
            },
            "instruction": waypoint.instruction,
            "distance_from_start": _format_distance_meters(waypoint.distance_from_start)
        }

        # Add enrichment if present
        if waypoint.enrichment and waypoint.enrichment.selected_content:
            content = waypoint.enrichment.selected_content
            wp_data["content"] = {
                "type": content.content_type.value,
                "title": content.title,
                "description": content.description,
                "url": content.url,
                "relevance_score": f"{content.relevance_score:.2f}"
            }

            # Add metadata for specific content types
            if content.metadata:
                if "artist" in content.metadata:
                    wp_data["content"]["artist"] = content.metadata["artist"]
                if "album" in content.metadata:
                    wp_data["content"]["album"] = content.metadata["album"]

            # Add decision info (optional, for debugging)
            wp_data["decision"] = {
                "winner": waypoint.enrichment.judge_decision.winner,
                "confidence": f"{waypoint.enrichment.judge_decision.confidence_score:.2f}",
                "reasoning": waypoint.enrichment.judge_decision.reasoning
            }

        else:
            # No enrichment available
            wp_data["content"] = {
                "type": "none",
                "title": "No content available",
                "description": "Content enrichment was not successful for this waypoint"
            }

        formatted.append(wp_data)

    return formatted


def _format_duration_ms(milliseconds: int) -> str:
    """
    Format milliseconds into human-readable duration

    Args:
        milliseconds: Duration in milliseconds

    Returns:
        Formatted string (e.g., "12.5 seconds", "2.3 minutes")
    """
    if milliseconds < 1000:
        return f"{milliseconds} ms"
    elif milliseconds < 60000:
        seconds = milliseconds / 1000
        return f"{seconds:.1f} seconds"
    else:
        minutes = milliseconds / 60000
        return f"{minutes:.1f} minutes"


def _format_distance_meters(meters: float) -> str:
    """
    Format distance from meters to readable format

    Args:
        meters: Distance in meters

    Returns:
        Formatted string (e.g., "1.2 km", "450 m")
    """
    if meters >= 1000:
        km = meters / 1000
        return f"{km:.1f} km"
    else:
        return f"{int(meters)} m"
