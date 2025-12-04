"""
Main Pipeline
Orchestrates the complete flow through all 6 modules
"""

from typing import Dict, Any

from src.models import TransactionContext
from src.modules import (
    validate_request,
    ValidationError,
    retrieve_route,
    RouteRetrievalError,
    preprocess_waypoints,
    Orchestrator,
    aggregate_results,
    format_response
)
from src.logging_config import get_logger
from src.config import get_config


class PipelineError(Exception):
    """Base exception for pipeline errors"""
    pass


def execute_pipeline(
    origin: str,
    destination: str,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Execute the complete multi-agent tour guide pipeline

    This is the main entry point that orchestrates all 6 modules:
    1. Request Validation
    2. Route Retrieval
    3. Waypoint Preprocessing
    4. Orchestration (multi-agent enrichment)
    5. Result Aggregation
    6. Response Formatting

    Args:
        origin: Starting location
        destination: Ending location
        preferences: Optional user preferences

    Returns:
        Formatted response dictionary

    Raises:
        ValidationError: If input validation fails
        RouteRetrievalError: If route cannot be retrieved
        PipelineError: For other pipeline errors
    """
    logger = get_logger()
    config = get_config()

    # Initialize orchestrator
    orchestrator = Orchestrator()
    context = None  # Initialize to avoid UnboundLocalError in exception handlers

    try:
        # ============================================================
        # MODULE 1: REQUEST VALIDATION
        # ============================================================
        context = validate_request(origin, destination, preferences)

        logger.info(
            "Pipeline started",
            transaction_id=context.transaction_id,
            origin=origin,
            destination=destination,
            mock_mode=config.mock_mode
        )

        # ============================================================
        # MODULE 2: ROUTE RETRIEVAL
        # ============================================================
        route_data = retrieve_route(context)

        # Extract route metadata for final response
        route_metadata = {
            "distance": route_data.distance,
            "duration": route_data.duration
        }

        # ============================================================
        # MODULE 3: WAYPOINT PREPROCESSING
        # ============================================================
        processed_waypoints = preprocess_waypoints(context, route_data)

        # ============================================================
        # MODULE 4: ORCHESTRATION (Multi-Agent Enrichment)
        # ============================================================
        enriched_waypoints = orchestrator.enrich_route(context, processed_waypoints)

        # ============================================================
        # MODULE 5: RESULT AGGREGATION
        # ============================================================
        final_route = aggregate_results(context, enriched_waypoints, route_metadata)

        # ============================================================
        # MODULE 6: RESPONSE FORMATTING
        # ============================================================
        response = format_response(final_route)

        # Log pipeline completion
        logger.info(
            "Pipeline completed successfully",
            transaction_id=context.transaction_id,
            total_time_ms=context.get_elapsed_time_ms(),
            enriched_waypoints=final_route.statistics.enriched_waypoints,
            success_rate=final_route.statistics.success_rate()
        )

        return response

    except ValidationError as e:
        logger.error(
            "Pipeline failed: Validation error",
            transaction_id=getattr(context, 'transaction_id', 'N/A'),
            error=str(e)
        )
        raise

    except RouteRetrievalError as e:
        logger.error(
            "Pipeline failed: Route retrieval error",
            transaction_id=context.transaction_id,
            error=str(e)
        )
        raise

    except Exception as e:
        logger.critical(
            "Pipeline failed: Unexpected error",
            transaction_id=getattr(context, 'transaction_id', 'N/A'),
            error=str(e),
            exc_info=True
        )
        raise PipelineError(f"Unexpected pipeline error: {str(e)}") from e

    finally:
        # Cleanup
        orchestrator.shutdown()


class ErrorResponse:
    """Structure for error responses"""

    def __init__(self, transaction_id: str, error_code: str, message: str):
        self.transaction_id = transaction_id
        self.error_code = error_code
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        from datetime import datetime
        return {
            "transaction_id": self.transaction_id,
            "error": {
                "code": self.error_code,
                "message": self.message
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def execute_pipeline_safe(
    origin: str,
    destination: str,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Safe pipeline execution with comprehensive error handling
    Returns error response instead of raising exceptions

    Args:
        origin: Starting location
        destination: Ending location
        preferences: Optional user preferences

    Returns:
        Success response or error response dictionary
    """
    try:
        return execute_pipeline(origin, destination, preferences)

    except ValidationError as e:
        from src.models import create_transaction_id
        return ErrorResponse(
            transaction_id=create_transaction_id(),
            error_code="VALIDATION_ERROR",
            message=str(e)
        ).to_dict()

    except RouteRetrievalError as e:
        from src.models import create_transaction_id
        return ErrorResponse(
            transaction_id=create_transaction_id(),
            error_code="ROUTE_NOT_FOUND",
            message="Unable to find route between locations"
        ).to_dict()

    except Exception as e:
        from src.models import create_transaction_id
        return ErrorResponse(
            transaction_id=create_transaction_id(),
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred"
        ).to_dict()
