"""
Multi-Agent AI Tour Guide System
Main package initialization

This package provides a multi-agent system that enriches navigation routes
with contextually relevant multimedia content through coordinated AI agent execution.
"""

__version__ = "1.0.0"
__author__ = "Tour Guide Development Team"

# Public API exports
from src.models import (
    # Core data structures
    TransactionContext,
    Waypoint,
    Coordinates,
    RouteData,
    ContentItem,
    AgentResult,
    JudgeDecision,
    WaypointEnrichment,
    RouteStatistics,
    FinalRoute,

    # Enums
    ContentType,
    AgentStatus,
    LocationType,

    # Helper functions
    create_transaction_id,
    create_fallback_content,
    create_timeout_result,
    create_error_result,
)

from src.config import (
    SystemConfig,
    get_config,
    set_config,
)

from src.pipeline import (
    execute_pipeline,
    execute_pipeline_safe,
    PipelineError,
)

from src.logging_config import get_logger

__all__ = [
    # Version and metadata
    "__version__",
    "__author__",

    # Core data structures
    "TransactionContext",
    "Waypoint",
    "Coordinates",
    "RouteData",
    "ContentItem",
    "AgentResult",
    "JudgeDecision",
    "WaypointEnrichment",
    "RouteStatistics",
    "FinalRoute",

    # Enums
    "ContentType",
    "AgentStatus",
    "LocationType",

    # Helper functions
    "create_transaction_id",
    "create_fallback_content",
    "create_timeout_result",
    "create_error_result",

    # Configuration
    "SystemConfig",
    "get_config",
    "set_config",

    # Pipeline
    "execute_pipeline",
    "execute_pipeline_safe",
    "PipelineError",

    # Logging
    "get_logger",
]
