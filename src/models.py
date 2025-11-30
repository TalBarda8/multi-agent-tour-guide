"""
Core data structures for the Multi-Agent Tour Guide System

This module defines all data models used throughout the pipeline:
- TransactionContext: Request tracking and metadata
- Waypoint: Route points with location data
- AgentResult: Standardized agent output
- ContentItem: Polymorphic content structure
- JudgeDecision: Judge agent evaluation result
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
import uuid
import threading


class ContentType(Enum):
    """Types of content that can be selected for waypoints"""
    VIDEO = "video"
    SONG = "song"
    HISTORY = "history"
    FALLBACK = "fallback"


class AgentStatus(Enum):
    """Status of agent execution"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    PENDING = "pending"


class LocationType(Enum):
    """Types of locations along the route"""
    INTERSECTION = "intersection"
    LANDMARK = "landmark"
    HIGHWAY = "highway"
    NEIGHBORHOOD = "neighborhood"
    UNKNOWN = "unknown"


@dataclass
class Coordinates:
    """Geographic coordinates"""
    lat: float
    lng: float

    def __str__(self) -> str:
        return f"({self.lat:.6f}, {self.lng:.6f})"


@dataclass
class WaypointMetadata:
    """
    Metadata about a waypoint location
    Used for agent query construction and context
    """
    location_type: LocationType
    nearby_landmarks: List[str] = field(default_factory=list)
    neighborhood: Optional[str] = None
    search_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_type": self.location_type.value,
            "nearby_landmarks": self.nearby_landmarks,
            "neighborhood": self.neighborhood,
            "search_keywords": self.search_keywords
        }


@dataclass
class ContentItem:
    """
    Polymorphic content structure
    Represents video, song, or history content
    """
    content_type: ContentType
    title: str
    description: str
    relevance_score: float  # 0.0 to 1.0
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.content_type.value,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata
        }


@dataclass
class AgentResult:
    """
    Standard result structure for all agents
    Every agent must return this structure
    """
    agent_name: str  # "youtube" | "spotify" | "history" | "judge"
    transaction_id: str
    waypoint_id: int
    status: AgentStatus
    content: Optional[ContentItem] = None
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_successful(self) -> bool:
        """Check if agent execution was successful"""
        return self.status == AgentStatus.SUCCESS and self.content is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "transaction_id": self.transaction_id,
            "waypoint_id": self.waypoint_id,
            "status": self.status.value,
            "content": self.content.to_dict() if self.content else None,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class JudgeDecision:
    """
    Result of Judge Agent evaluation
    Contains the selected content and reasoning
    """
    winner: str  # Agent name that won
    reasoning: str  # Explanation of choice
    confidence_score: float  # 0.0 to 1.0
    individual_scores: Dict[str, float]  # Scores per agent
    decision_time_ms: int = 0
    tie_breaker_applied: bool = False
    selected_content: Optional[ContentItem] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "winner": self.winner,
            "reasoning": self.reasoning,
            "confidence_score": self.confidence_score,
            "individual_scores": self.individual_scores,
            "decision_time_ms": self.decision_time_ms,
            "tie_breaker_applied": self.tie_breaker_applied,
            "selected_content": self.selected_content.to_dict() if self.selected_content else None
        }


@dataclass
class WaypointEnrichment:
    """
    Enrichment data added to a waypoint after agent processing
    Contains selected content and all agent results
    """
    selected_content: ContentItem
    all_agent_results: Dict[str, AgentResult]
    judge_decision: JudgeDecision
    processing_time_ms: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_content": self.selected_content.to_dict(),
            "all_agent_results": {
                name: result.to_dict()
                for name, result in self.all_agent_results.items()
            },
            "judge_decision": self.judge_decision.to_dict(),
            "processing_time_ms": self.processing_time_ms
        }


@dataclass
class AgentContext:
    """
    Context information passed to agents for query construction
    Contains pre-built search queries for each agent type
    """
    youtube_query: str
    spotify_query: str
    history_query: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "youtube_query": self.youtube_query,
            "spotify_query": self.spotify_query,
            "history_query": self.history_query
        }


@dataclass
class Waypoint:
    """
    Represents a single point along the route
    Contains location data, metadata, and enrichment (after processing)
    """
    id: int
    location_name: str
    coordinates: Coordinates
    instruction: str
    distance_from_start: float = 0.0  # Meters
    step_index: int = 0
    metadata: Optional[WaypointMetadata] = None
    agent_context: Optional[AgentContext] = None
    enrichment: Optional[WaypointEnrichment] = None

    def is_enriched(self) -> bool:
        """Check if waypoint has been enriched"""
        return self.enrichment is not None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "location_name": self.location_name,
            "coordinates": {"lat": self.coordinates.lat, "lng": self.coordinates.lng},
            "instruction": self.instruction,
            "distance_from_start": self.distance_from_start,
            "step_index": self.step_index
        }

        if self.metadata:
            result["metadata"] = self.metadata.to_dict()

        if self.agent_context:
            result["agent_context"] = self.agent_context.to_dict()

        if self.enrichment:
            result["enrichment"] = self.enrichment.to_dict()

        return result


@dataclass
class RouteData:
    """
    Complete route information from Google Maps
    Contains all waypoints and route metadata
    """
    distance: str  # e.g., "45.2 km"
    duration: str  # e.g., "52 mins"
    waypoints: List[Waypoint]
    steps: List[Dict[str, Any]] = field(default_factory=list)  # Raw navigation steps

    def waypoint_count(self) -> int:
        return len(self.waypoints)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distance": self.distance,
            "duration": self.duration,
            "waypoint_count": len(self.waypoints),
            "waypoints": [wp.to_dict() for wp in self.waypoints]
        }


@dataclass
class TransactionContext:
    """
    Context object propagated through entire pipeline
    Contains transaction ID and request metadata
    Thread-safe for concurrent access
    """
    transaction_id: str
    origin: str
    destination: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    current_stage: str = "initialization"
    metadata: Dict[str, Any] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def log_stage_entry(self, stage_name: str) -> None:
        """
        Update current stage and log transition
        Thread-safe operation
        """
        with self._lock:
            self.current_stage = stage_name

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata in a thread-safe manner
        """
        with self._lock:
            self.metadata[key] = value

    def get_elapsed_time_ms(self) -> int:
        """Calculate time since creation in milliseconds"""
        delta = datetime.utcnow() - self.created_at
        return int(delta.total_seconds() * 1000)

    def to_log_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "transaction_id": self.transaction_id,
            "origin": self.origin,
            "destination": self.destination,
            "current_stage": self.current_stage,
            "elapsed_ms": self.get_elapsed_time_ms()
        }


@dataclass
class RouteStatistics:
    """
    Statistics about route enrichment process
    Used in final response
    """
    total_waypoints: int
    enriched_waypoints: int
    failed_waypoints: int
    total_processing_time_ms: int
    average_processing_time_ms: float
    content_breakdown: Dict[str, int]  # {"video": 2, "music": 4, "history": 2}

    def success_rate(self) -> float:
        """Calculate enrichment success rate"""
        if self.total_waypoints == 0:
            return 0.0
        return self.enriched_waypoints / self.total_waypoints

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_waypoints": self.total_waypoints,
            "enriched_waypoints": self.enriched_waypoints,
            "failed_waypoints": self.failed_waypoints,
            "total_processing_time_ms": self.total_processing_time_ms,
            "average_processing_time_ms": self.average_processing_time_ms,
            "content_breakdown": self.content_breakdown,
            "success_rate": self.success_rate()
        }


@dataclass
class FinalRoute:
    """
    Complete route with all enrichments and statistics
    Final output of the aggregation stage
    """
    transaction_id: str
    waypoints: List[Waypoint]
    statistics: RouteStatistics
    route_metadata: Dict[str, str]  # distance, duration, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "waypoints": [wp.to_dict() for wp in self.waypoints],
            "statistics": self.statistics.to_dict(),
            "route_metadata": self.route_metadata
        }


def create_transaction_id() -> str:
    """
    Generate unique transaction ID
    Format: TXID-{timestamp}-{uuid}
    Example: TXID-20250130T143052-7f3e4a2b-9c1d-4e8f-a5b3-6d2c8f1e9a4b
    """
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    unique_id = str(uuid.uuid4())
    return f"TXID-{timestamp}-{unique_id}"


def create_fallback_content(waypoint: Waypoint) -> ContentItem:
    """
    Create generic fallback content when all agents fail
    """
    return ContentItem(
        content_type=ContentType.FALLBACK,
        title=f"About {waypoint.location_name}",
        description=f"Passing through {waypoint.location_name}",
        relevance_score=0.0,
        url=None,
        metadata={"fallback": True}
    )


def create_timeout_result(agent_name: str, transaction_id: str, waypoint_id: int, timeout_ms: int) -> AgentResult:
    """
    Create AgentResult for timeout scenario
    """
    return AgentResult(
        agent_name=agent_name,
        transaction_id=transaction_id,
        waypoint_id=waypoint_id,
        status=AgentStatus.TIMEOUT,
        content=None,
        error_message=f"Agent execution exceeded {timeout_ms}ms timeout",
        execution_time_ms=timeout_ms
    )


def create_error_result(agent_name: str, transaction_id: str, waypoint_id: int, error: Exception) -> AgentResult:
    """
    Create AgentResult for error scenario
    """
    return AgentResult(
        agent_name=agent_name,
        transaction_id=transaction_id,
        waypoint_id=waypoint_id,
        status=AgentStatus.ERROR,
        content=None,
        error_message=str(error),
        execution_time_ms=0
    )
