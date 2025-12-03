"""
Pipeline Modules Package
Contains all 6 pipeline modules with their interfaces

This package implements the complete processing pipeline:
- Module 1: Request Validation
- Module 2: Route Retrieval
- Module 3: Waypoint Preprocessing
- Module 4: Orchestration (Agent Coordination)
- Module 5: Result Aggregation
- Module 6: Response Formatting
"""

# Module 1: Request Validator
from src.modules.request_validator import validate_request, ValidationError

# Module 2: Route Retrieval
from src.modules.route_retrieval import retrieve_route, RouteRetrievalError

# Module 3: Waypoint Preprocessor
from src.modules.waypoint_preprocessor import preprocess_waypoints

# Module 4: Orchestrator
from src.modules.orchestrator import Orchestrator

# Module 5: Result Aggregator
from src.modules.result_aggregator import aggregate_results

# Module 6: Response Formatter
from src.modules.response_formatter import format_response

# Mock agent implementations
from src.modules.mock_agents import (
    run_mock_youtube_agent,
    run_mock_spotify_agent,
    run_mock_history_agent,
    run_mock_judge,
)

__all__ = [
    # Module exports
    "validate_request",
    "ValidationError",
    "retrieve_route",
    "RouteRetrievalError",
    "preprocess_waypoints",
    "Orchestrator",
    "aggregate_results",
    "format_response",

    # Mock agents
    "run_mock_youtube_agent",
    "run_mock_spotify_agent",
    "run_mock_history_agent",
    "run_mock_judge",
]
