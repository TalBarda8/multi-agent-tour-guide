"""
Module 3: Waypoint Preprocessor
Enriches waypoint data with metadata for agent processing
"""

import time
import re
from typing import List

from src.models import (
    TransactionContext,
    RouteData,
    Waypoint,
    WaypointMetadata,
    AgentContext,
    LocationType
)
from src.logging_config import get_logger


def preprocess_waypoints(context: TransactionContext, route: RouteData) -> List[Waypoint]:
    """
    Enrich waypoint data with metadata for agent processing

    Input Contract:
        - TransactionContext
        - RouteData with waypoints

    Output Contract:
        - List of Waypoints with metadata and agent_context populated

    Args:
        context: Transaction context
        route: Route data with waypoints

    Returns:
        List of processed waypoints with metadata
    """
    logger = get_logger()

    context.log_stage_entry("waypoint_preprocessing")
    logger.log_stage_entry(
        "waypoint_preprocessing",
        context.transaction_id,
        waypoint_count=len(route.waypoints)
    )

    start_time = time.time()
    processed_waypoints = []

    for waypoint in route.waypoints:
        # Classify location type
        location_type = _classify_location_type(waypoint)

        # Extract nearby landmarks from instruction
        landmarks = _extract_landmarks(waypoint.instruction, waypoint.location_name)

        # Extract neighborhood if possible
        neighborhood = _extract_neighborhood(waypoint.location_name)

        # Generate search keywords
        keywords = _generate_search_keywords(
            waypoint.location_name,
            landmarks,
            neighborhood
        )

        # Create metadata
        waypoint.metadata = WaypointMetadata(
            location_type=location_type,
            nearby_landmarks=landmarks,
            neighborhood=neighborhood,
            search_keywords=keywords
        )

        # Build agent-specific queries
        waypoint.agent_context = AgentContext(
            youtube_query=_build_youtube_query(waypoint),
            music_query=_build_music_query(waypoint),
            history_query=_build_history_query(waypoint)
        )

        processed_waypoints.append(waypoint)

        # Log preprocessing for each waypoint
        logger.debug(
            "Waypoint preprocessed",
            transaction_id=context.transaction_id,
            waypoint_id=waypoint.id,
            location_type=location_type.value,
            search_keywords=keywords
        )

    duration_ms = int((time.time() - start_time) * 1000)

    logger.log_stage_exit(
        "waypoint_preprocessing",
        context.transaction_id,
        duration_ms=duration_ms,
        processed_count=len(processed_waypoints)
    )

    return processed_waypoints


def _classify_location_type(waypoint: Waypoint) -> LocationType:
    """
    Classify the type of location based on name and instruction

    Args:
        waypoint: Waypoint to classify

    Returns:
        LocationType classification
    """
    name_lower = waypoint.location_name.lower()
    instruction_lower = waypoint.instruction.lower()

    # Check for landmarks
    landmark_keywords = [
        "park", "building", "tower", "statue", "museum", "library",
        "cathedral", "church", "bridge", "square", "plaza", "center"
    ]
    if any(keyword in name_lower for keyword in landmark_keywords):
        return LocationType.LANDMARK

    # Check for highway/interstate
    if any(term in name_lower for term in ["highway", "interstate", "i-", "route"]):
        return LocationType.HIGHWAY

    # Check for intersection (contains &, "and", or "at")
    if "&" in name_lower or " and " in name_lower or " at " in name_lower:
        return LocationType.INTERSECTION

    # Check for neighborhood names
    neighborhood_keywords = [
        "district", "quarter", "neighborhood", "heights", "village", "town"
    ]
    if any(keyword in name_lower for keyword in neighborhood_keywords):
        return LocationType.NEIGHBORHOOD

    # Default to intersection
    return LocationType.INTERSECTION


def _extract_landmarks(instruction: str, location_name: str) -> List[str]:
    """
    Extract landmark names from instruction text

    Args:
        instruction: Navigation instruction
        location_name: Name of the location

    Returns:
        List of landmark names
    """
    landmarks = []

    # Common landmark patterns in instructions
    landmark_patterns = [
        r"near ([\w\s]+)",
        r"past ([\w\s]+)",
        r"toward ([\w\s]+)",
        r"at ([\w\s]+)",
    ]

    combined_text = f"{instruction} {location_name}"

    for pattern in landmark_patterns:
        matches = re.findall(pattern, combined_text, re.IGNORECASE)
        landmarks.extend(matches)

    # Clean and deduplicate
    cleaned_landmarks = []
    for landmark in landmarks:
        cleaned = landmark.strip()
        if cleaned and len(cleaned) > 3 and cleaned not in cleaned_landmarks:
            cleaned_landmarks.append(cleaned)

    return cleaned_landmarks[:3]  # Limit to top 3


def _extract_neighborhood(location_name: str) -> str:
    """
    Extract neighborhood name from location

    Args:
        location_name: Location name

    Returns:
        Neighborhood name or None
    """
    # Common neighborhood indicators
    neighborhood_patterns = [
        r"(\w+\s+(?:District|Quarter|Heights|Village|Town))",
        r"((?:Upper|Lower|East|West|North|South)\s+\w+)",
    ]

    for pattern in neighborhood_patterns:
        match = re.search(pattern, location_name, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Default: extract area from location (e.g., "Manhattan" from "5th Ave, Manhattan")
    if "," in location_name:
        parts = location_name.split(",")
        if len(parts) > 1:
            potential_neighborhood = parts[-1].strip()
            if potential_neighborhood and len(potential_neighborhood) > 2:
                return potential_neighborhood

    return None


def _generate_search_keywords(
    location_name: str,
    landmarks: List[str],
    neighborhood: str
) -> List[str]:
    """
    Generate search keywords for the location

    Args:
        location_name: Name of location
        landmarks: Nearby landmarks
        neighborhood: Neighborhood name

    Returns:
        List of search keywords
    """
    keywords = []

    # Add location name components
    name_parts = re.split(r'[&,\-]', location_name)
    for part in name_parts:
        cleaned = part.strip()
        if cleaned and len(cleaned) > 2:
            keywords.append(cleaned)

    # Add landmarks
    keywords.extend(landmarks)

    # Add neighborhood
    if neighborhood:
        keywords.append(neighborhood)

    # Deduplicate while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower not in seen:
            seen.add(keyword_lower)
            unique_keywords.append(keyword)

    return unique_keywords[:5]  # Limit to top 5


def _build_youtube_query(waypoint: Waypoint) -> str:
    """
    Build YouTube search query for waypoint

    Args:
        waypoint: Waypoint with metadata

    Returns:
        YouTube search query string
    """
    keywords = waypoint.metadata.search_keywords[:3]
    query = " ".join(keywords)

    # Add context for better results
    if waypoint.metadata.location_type == LocationType.LANDMARK:
        query += " tour video"
    elif waypoint.metadata.location_type == LocationType.NEIGHBORHOOD:
        query += " neighborhood walking tour"
    else:
        query += " travel guide"

    return query


def _build_music_query(waypoint: Waypoint) -> str:
    """
    Build music search query for waypoint (YouTube Music search)

    Args:
        waypoint: Waypoint with metadata

    Returns:
        Music search query string for YouTube
    """
    # Use neighborhood or main location for music search
    if waypoint.metadata.neighborhood:
        query = waypoint.metadata.neighborhood
    else:
        query = waypoint.metadata.search_keywords[0] if waypoint.metadata.search_keywords else waypoint.location_name

    # Add music-specific keywords for YouTube search
    if waypoint.metadata.location_type == LocationType.LANDMARK:
        query += " song instrumental ambient music"
    else:
        query += " song city urban music"

    return query


def _build_history_query(waypoint: Waypoint) -> str:
    """
    Build history/Wikipedia search query for waypoint

    Args:
        waypoint: Waypoint with metadata

    Returns:
        History search query string
    """
    keywords = waypoint.metadata.search_keywords[:2]
    query = " ".join(keywords)

    # Add "history" for better Wikipedia results
    query += " history"

    return query
