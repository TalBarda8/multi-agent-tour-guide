"""
Module 5: Result Aggregator
Collects all enriched waypoints and compiles final route with statistics
"""

import time
from typing import List, Dict

from src.models import (
    TransactionContext,
    Waypoint,
    FinalRoute,
    RouteStatistics,
    ContentType
)
from src.logging_config import get_logger


def aggregate_results(
    context: TransactionContext,
    enriched_waypoints: List[Waypoint],
    route_metadata: Dict[str, str]
) -> FinalRoute:
    """
    Collect all enriched waypoints and compile final route

    Input Contract:
        - TransactionContext
        - List of enriched Waypoints
        - Route metadata (distance, duration)

    Output Contract:
        - FinalRoute with statistics

    Args:
        context: Transaction context
        enriched_waypoints: List of waypoints (hopefully enriched)
        route_metadata: Original route data (distance, duration)

    Returns:
        FinalRoute with complete statistics
    """
    logger = get_logger()

    context.log_stage_entry("result_aggregation")
    logger.log_stage_entry(
        "result_aggregation",
        context.transaction_id,
        waypoint_count=len(enriched_waypoints)
    )

    start_time = time.time()

    # Count enriched vs failed waypoints
    enriched_count = sum(1 for wp in enriched_waypoints if wp.is_enriched())
    failed_count = len(enriched_waypoints) - enriched_count

    # Calculate total and average processing time
    processing_times = [
        wp.enrichment.processing_time_ms
        for wp in enriched_waypoints
        if wp.enrichment
    ]

    total_processing_time = sum(processing_times)
    average_processing_time = (
        total_processing_time / len(processing_times)
        if processing_times
        else 0.0
    )

    # Calculate content type breakdown
    content_breakdown = _calculate_content_breakdown(enriched_waypoints)

    # Create statistics
    statistics = RouteStatistics(
        total_waypoints=len(enriched_waypoints),
        enriched_waypoints=enriched_count,
        failed_waypoints=failed_count,
        total_processing_time_ms=total_processing_time,
        average_processing_time_ms=average_processing_time,
        content_breakdown=content_breakdown
    )

    # Create final route
    final_route = FinalRoute(
        transaction_id=context.transaction_id,
        waypoints=enriched_waypoints,
        statistics=statistics,
        route_metadata=route_metadata
    )

    duration_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "Route aggregation completed",
        transaction_id=context.transaction_id,
        total_waypoints=statistics.total_waypoints,
        success_rate=statistics.success_rate(),
        total_time_ms=total_processing_time
    )

    logger.log_stage_exit(
        "result_aggregation",
        context.transaction_id,
        duration_ms=duration_ms,
        enriched_count=enriched_count,
        failed_count=failed_count
    )

    return final_route


def _calculate_content_breakdown(waypoints: List[Waypoint]) -> Dict[str, int]:
    """
    Calculate breakdown of content types selected

    Args:
        waypoints: List of enriched waypoints

    Returns:
        Dictionary mapping content type to count
    """
    breakdown = {
        ContentType.VIDEO.value: 0,
        ContentType.SONG.value: 0,
        ContentType.HISTORY.value: 0,
        ContentType.FALLBACK.value: 0
    }

    for waypoint in waypoints:
        if waypoint.enrichment and waypoint.enrichment.selected_content:
            content_type = waypoint.enrichment.selected_content.content_type.value
            breakdown[content_type] = breakdown.get(content_type, 0) + 1

    return breakdown
