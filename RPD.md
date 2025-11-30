# Requirements & Product Definition (RPD)
## Multi-Agent AI Tour Guide System

**Version:** 1.0
**Date:** November 30, 2025
**Document Status:** Final

---

## Table of Contents

1. [Project Vision](#1-project-vision)
2. [User Stories](#2-user-stories)
3. [System Actors & Agents](#3-system-actors--agents)
4. [Architecture Overview](#4-architecture-overview)
5. [Module Breakdown](#5-module-breakdown)
6. [Data Structures](#6-data-structures)
7. [Asynchronous Flow Design](#7-asynchronous-flow-design)
8. [Orchestrator Design](#8-orchestrator-design)
9. [Transaction ID Propagation](#9-transaction-id-propagation)
10. [Logging Specification](#10-logging-specification)
11. [Error Handling Strategy](#11-error-handling-strategy)
12. [Performance & Concurrency](#12-performance--concurrency)
13. [Development Phases](#13-development-phases)
14. [Example System Run-Through](#14-example-system-run-through)
15. [API Specifications](#15-api-specifications)
16. [Testing Strategy](#16-testing-strategy)
17. [Deployment Considerations](#17-deployment-considerations)

---

## 1. Project Vision

### 1.1 Overview

The **Multi-Agent AI Tour Guide System** is an intelligent, asynchronous platform that transforms ordinary driving directions into an enriched, multimedia journey experience. By integrating Google Maps Directions API with a coordinated team of AI agents, the system augments each waypoint along a route with contextually relevant content—videos, music, and historical narratives.

### 1.2 Core Objectives

- **Enrich Travel Experience**: Transform navigation waypoints into learning and entertainment opportunities
- **Demonstrate Multi-Agent Coordination**: Showcase asynchronous, parallel agent orchestration
- **Ensure Observability**: Provide complete visibility into system operations through structured logging
- **Maintain Performance**: Leverage concurrency to minimize total processing time
- **Enable Debugging**: Support comprehensive tracing and debugging through transaction IDs

### 1.3 System Boundaries

**In Scope:**
- Route retrieval from Google Maps Directions API
- Parallel agent execution (YouTube, Spotify, History)
- Intelligent content selection via Judge Agent
- Asynchronous orchestration and thread management
- Comprehensive structured logging
- Transaction tracking across all components

**Out of Scope:**
- Actual playback of audio/video content
- User interface development (beyond CLI/API)
- Persistent storage of route histories
- Real-time navigation features
- Turn-by-turn voice guidance

### 1.4 Success Criteria

1. **Functional**: Successfully enriches 95%+ of waypoints with relevant content
2. **Performance**: Processes entire route in under 30 seconds for typical 10-waypoint journey
3. **Reliability**: Handles agent failures gracefully without crashing
4. **Observability**: All operations traceable via transaction IDs and structured logs
5. **Scalability**: Supports routes with up to 50 waypoints without degradation

---

## 2. User Stories

### 2.1 Primary User Story

**As a** driver planning a road trip
**I want** an enriched navigation experience with contextual content at each waypoint
**So that** my journey is more entertaining, educational, and memorable

**Acceptance Criteria:**
- User provides origin and destination addresses
- System returns a list of waypoints with enriched content
- Each waypoint includes the best-selected media (video, song, or fact)
- Processing completes within reasonable time (< 30 seconds for typical routes)
- System provides clear feedback on processing status

### 2.2 Secondary User Stories

#### 2.2.1 Developer Debugging Story

**As a** system developer
**I want** comprehensive logs with transaction IDs
**So that** I can trace issues across the distributed agent system

**Acceptance Criteria:**
- Every log entry contains a transaction ID
- Logs show timing information for all operations
- Agent decisions are logged with reasoning
- Failures include stack traces and context

#### 2.2.2 System Administrator Story

**As a** system administrator
**I want** managed log files with rotation
**So that** disk space is controlled and logs remain accessible

**Acceptance Criteria:**
- Logs rotate at configurable size thresholds
- Old logs are archived or deleted per policy
- Log levels are configurable
- No console output pollution

---

## 3. System Actors & Agents

### 3.1 External Actors

#### 3.1.1 End User
- **Role**: Initiates route requests
- **Interactions**: Provides origin/destination, receives enriched route
- **Requirements**: Basic understanding of addresses/place names

#### 3.1.2 Google Maps Directions API
- **Role**: External service providing route data
- **Interactions**: Receives route queries, returns waypoint data
- **Requirements**: Valid API key, network connectivity

### 3.2 System Agents

#### 3.2.1 YouTube Agent

**Responsibility**: Find contextually relevant video content for waypoints

**Tools/Skills:**
- YouTube Data API v3 integration
- Search query formulation
- Video relevance scoring
- Result filtering and ranking

**Inputs:**
- Transaction ID
- Waypoint location name
- Waypoint coordinates (optional)
- Context information (step description)

**Outputs:**
- Video title
- Video URL
- Video description
- Relevance score
- Thumbnail URL

**Timeout**: 5 seconds

**Error Handling:**
- API rate limit exceeded → return empty result with error flag
- Network timeout → return empty result
- No results found → return "no video available" status

---

#### 3.2.2 Spotify Agent

**Responsibility**: Find contextually relevant music/audio content for waypoints

**Tools/Skills:**
- Spotify Web API integration
- Music search and recommendation
- Genre/mood mapping from location context
- Track popularity assessment

**Inputs:**
- Transaction ID
- Waypoint location name
- Waypoint coordinates (optional)
- Context information (neighborhood, landmark type)

**Outputs:**
- Track name
- Artist name
- Track URL
- Album name
- Relevance score

**Timeout**: 5 seconds

**Error Handling:**
- Authentication failure → return empty result
- No matching content → return "no song available" status
- API timeout → return empty result with timeout flag

---

#### 3.2.3 History Agent

**Responsibility**: Retrieve historical facts, stories, or trivia about waypoint locations

**Tools/Skills:**
- Wikipedia API integration
- Historical database queries
- Natural language processing for fact extraction
- Content summarization

**Inputs:**
- Transaction ID
- Waypoint location name
- Waypoint coordinates (optional)
- Location type/category

**Outputs:**
- Historical fact/story text
- Source attribution
- Relevance score
- Time period (if applicable)

**Timeout**: 5 seconds

**Error Handling:**
- No historical data found → return generic location info
- API unavailable → return "history unavailable" status
- Parsing errors → return simplified fact

---

#### 3.2.4 Judge Agent

**Responsibility**: Evaluate outputs from YouTube, Spotify, and History agents and select the best content

**Tools/Skills:**
- Multi-criteria decision analysis
- Content quality assessment
- Contextual relevance scoring
- LLM integration for semantic evaluation

**Inputs:**
- Transaction ID
- YouTube Agent output
- Spotify Agent output
- History Agent output
- Waypoint metadata
- User preferences (optional)

**Outputs:**
- Selected content (winner)
- Decision reasoning
- Confidence score
- Individual agent scores

**Decision Criteria:**
1. Relevance to location (40%)
2. Content quality/availability (30%)
3. Diversity across route (20%)
4. User preference alignment (10%)

**Timeout**: 3 seconds

**Error Handling:**
- All agent inputs empty → return default content
- Tie between options → apply tiebreaker rules
- Processing timeout → return first available valid result

---

#### 3.2.5 Orchestrator (Central Coordinator)

**Responsibility**: Manage the entire processing pipeline, coordinate agents, handle concurrency

**Tools/Skills:**
- Thread/process management
- Asynchronous execution coordination
- State management
- Result aggregation
- Timeout enforcement

**Inputs:**
- User request (origin, destination)
- System configuration

**Outputs:**
- Enriched route with all waypoints processed
- Processing metadata (timing, success rates)
- Transaction ID for tracking

**Key Responsibilities:**
1. Transaction ID generation and propagation
2. Google Maps API interaction
3. Agent thread creation and lifecycle management
4. Timeout enforcement across all agents
5. Result aggregation and ordering
6. Error recovery and fallback strategies
7. Logging coordination
8. Performance monitoring

---

## 4. Architecture Overview

### 4.1 High-Level Architecture

The system follows a **modular pipeline architecture** with explicit stages, each having defined inputs and outputs. The architecture emphasizes observability, traceability, and debuggability.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                 │
│                    (Origin + Destination)                            │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MODULE 1: REQUEST VALIDATOR                       │
│  - Validates input addresses                                         │
│  - Generates Transaction ID                                          │
│  - Initializes logging context                                       │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼ [Transaction ID: TXID-xxxxx]
┌─────────────────────────────────────────────────────────────────────┐
│                  MODULE 2: ROUTE RETRIEVAL                           │
│  - Calls Google Maps Directions API                                  │
│  - Parses waypoints and steps                                        │
│  - Extracts location names                                           │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼ [Route Data + TXID]
┌─────────────────────────────────────────────────────────────────────┐
│                MODULE 3: WAYPOINT PREPROCESSOR                       │
│  - Normalizes waypoint data                                          │
│  - Enriches with metadata                                            │
│  - Prepares for agent processing                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼ [Processed Waypoints + TXID]
┌─────────────────────────────────────────────────────────────────────┐
│              MODULE 4: ORCHESTRATOR (MAIN COORDINATOR)               │
│                                                                       │
│  For each waypoint, spawns parallel agents:                          │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   YouTube    │  │   Spotify    │  │   History    │              │
│  │    Agent     │  │    Agent     │  │    Agent     │              │
│  │  (Thread 1)  │  │  (Thread 2)  │  │  (Thread 3)  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│         └──────────────────┴──────────────────┘                      │
│                            │                                          │
│                            ▼                                          │
│                  ┌──────────────────┐                                │
│                  │   Judge Agent    │                                │
│                  │    (Thread 4)    │                                │
│                  └─────────┬────────┘                                │
│                            │                                          │
│  - Manages thread lifecycle                                          │
│  - Enforces timeouts                                                 │
│  - Aggregates results                                                │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼ [Enriched Waypoints + TXID]
┌─────────────────────────────────────────────────────────────────────┐
│                MODULE 5: RESULT AGGREGATOR                           │
│  - Collects all waypoint results                                     │
│  - Assembles final route structure                                   │
│  - Calculates processing statistics                                  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼ [Final Output + TXID]
┌─────────────────────────────────────────────────────────────────────┐
│                 MODULE 6: RESPONSE FORMATTER                         │
│  - Formats output for user consumption                               │
│  - Includes metadata and statistics                                  │
│  - Logs final completion                                             │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      USER RESPONSE                                   │
│              (Enriched Route with Media Content)                     │
└─────────────────────────────────────────────────────────────────────┘

                    LOGGING AT EVERY STAGE
                    (All logs include TXID)
```

### 4.2 Key Architectural Principles

1. **Modularity**: Each stage is independent with clear contracts
2. **Observability**: Logs written after each module execution
3. **Asynchronicity**: Agents run in parallel where possible
4. **Traceability**: Transaction IDs propagate through all layers
5. **Fault Tolerance**: Graceful degradation on agent failures
6. **Scalability**: Thread pool management for concurrent waypoint processing

### 4.3 Data Flow Characteristics

- **Sequential Modules**: 1 → 2 → 3 → 4 → 5 → 6 (pipeline stages)
- **Parallel Processing**: Within Module 4 (agents per waypoint)
- **Synchronization Points**: Orchestrator waits for all agents before proceeding
- **Backward Flow**: None (uni-directional pipeline)

---

## 5. Module Breakdown

### 5.1 Module 1: Request Validator

**Purpose**: Validate user input and initialize request context

**Input Contract:**
```python
{
    "origin": str,           # Address or place name
    "destination": str,      # Address or place name
    "preferences": {         # Optional
        "content_type": str, # "video" | "music" | "history" | "auto"
        "avoid": list[str]   # Content to avoid
    }
}
```

**Output Contract:**
```python
{
    "transaction_id": str,   # Generated UUID
    "origin": str,           # Validated origin
    "destination": str,      # Validated destination
    "preferences": dict,     # Normalized preferences
    "timestamp": datetime,   # Request initiation time
    "status": str            # "valid" | "invalid"
}
```

**Processing Steps:**
1. Generate unique transaction ID (UUID4)
2. Validate origin is non-empty string
3. Validate destination is non-empty string
4. Normalize preference values
5. Initialize logging context with transaction ID
6. Record validation timestamp

**Logging:**
- Log level: INFO
- Message: "Request validated"
- Fields: transaction_id, origin, destination, timestamp

**Error Conditions:**
- Empty origin → ValidationError
- Empty destination → ValidationError
- Invalid preference values → Use defaults with warning

---

### 5.2 Module 2: Route Retrieval

**Purpose**: Fetch route data from Google Maps Directions API

**Input Contract:**
```python
{
    "transaction_id": str,
    "origin": str,
    "destination": str,
    "preferences": dict
}
```

**Output Contract:**
```python
{
    "transaction_id": str,
    "route": {
        "distance": str,        # e.g., "45.2 km"
        "duration": str,        # e.g., "52 mins"
        "steps": list[dict],    # Navigation steps
        "waypoints": list[dict] # Extracted waypoints
    },
    "api_status": str,          # "OK" | "ERROR"
    "timestamp": datetime
}
```

**Waypoint Structure:**
```python
{
    "id": int,                  # Sequential waypoint ID
    "location_name": str,       # e.g., "Main St & 5th Ave"
    "coordinates": {
        "lat": float,
        "lng": float
    },
    "instruction": str,         # e.g., "Turn right onto Main St"
    "distance_from_start": str, # Cumulative distance
    "step_index": int           # Reference to navigation step
}
```

**Processing Steps:**
1. Construct Google Maps API request URL
2. Execute HTTP GET request
3. Parse JSON response
4. Extract steps from directions
5. Convert steps to waypoint objects
6. Validate waypoint data completeness
7. Calculate cumulative distances

**Logging:**
- Log level: INFO
- Message: "Route retrieved successfully"
- Fields: transaction_id, waypoint_count, total_distance, api_response_time

**Error Conditions:**
- API key invalid → APIError (fatal)
- No route found → NoRouteError (fatal)
- Network timeout → RetryableError (retry 3 times)
- Malformed response → ParsingError (fatal)

---

### 5.3 Module 3: Waypoint Preprocessor

**Purpose**: Enrich waypoint data with metadata for agent processing

**Input Contract:**
```python
{
    "transaction_id": str,
    "route": {
        "waypoints": list[dict]
    }
}
```

**Output Contract:**
```python
{
    "transaction_id": str,
    "processed_waypoints": list[dict]
}
```

**Processed Waypoint Structure:**
```python
{
    "id": int,
    "location_name": str,
    "coordinates": {"lat": float, "lng": float},
    "instruction": str,
    "metadata": {
        "location_type": str,       # "intersection" | "landmark" | "highway"
        "nearby_landmarks": list[str],
        "neighborhood": str,
        "search_keywords": list[str] # For agent queries
    },
    "agent_context": {
        "youtube_query": str,
        "spotify_query": str,
        "history_query": str
    }
}
```

**Processing Steps:**
1. For each waypoint:
   - Classify location type (intersection, landmark, highway segment)
   - Extract nearby landmark names from instruction text
   - Generate search keywords
   - Build agent-specific query strings
2. Add metadata fields
3. Validate all required fields present

**Logging:**
- Log level: DEBUG
- Message: "Waypoint preprocessed"
- Fields: transaction_id, waypoint_id, location_type, search_keywords

**Error Conditions:**
- Missing coordinates → Use location name only (warning)
- Unable to classify type → Default to "intersection"

---

### 5.4 Module 4: Orchestrator

**Purpose**: Coordinate parallel agent execution for each waypoint

**Input Contract:**
```python
{
    "transaction_id": str,
    "processed_waypoints": list[dict]
}
```

**Output Contract:**
```python
{
    "transaction_id": str,
    "enriched_waypoints": list[dict]
}
```

**Enriched Waypoint Structure:**
```python
{
    # Original waypoint fields plus:
    "enrichment": {
        "selected_content": {
            "type": str,        # "video" | "song" | "history"
            "title": str,
            "url": str,
            "description": str,
            "source": str       # Agent name
        },
        "all_agent_results": {
            "youtube": dict,
            "spotify": dict,
            "history": dict
        },
        "judge_decision": {
            "winner": str,
            "reasoning": str,
            "scores": dict
        },
        "processing_time_ms": int
    }
}
```

**Processing Steps:**

For each waypoint (can process multiple waypoints concurrently):

1. **Create Agent Threads**:
   - Spawn YouTube agent thread
   - Spawn Spotify agent thread
   - Spawn History agent thread
   - All threads receive same waypoint data + transaction ID

2. **Monitor Execution**:
   - Set timeout timer (5 seconds per agent)
   - Collect results as they complete
   - Handle timeouts gracefully

3. **Wait for Completion**:
   - Use thread join with timeout
   - Collect all available results

4. **Judge Phase**:
   - Spawn Judge agent thread
   - Pass all collected agent results
   - Set timeout timer (3 seconds)
   - Await decision

5. **Aggregate**:
   - Combine selected content with original waypoint
   - Calculate processing time
   - Store all agent outputs for debugging

**Concurrency Model:**
- **Agent-level parallelism**: 3 agents per waypoint run in parallel
- **Waypoint-level parallelism**: Multiple waypoints can be processed concurrently (configurable, default: 5 waypoints at a time)
- **Thread pool**: Fixed-size pool to prevent resource exhaustion

**Logging:**
- Log level: INFO
- Message: "Waypoint enrichment completed"
- Fields: transaction_id, waypoint_id, selected_type, processing_time_ms, agent_success_count

**Error Conditions:**
- All agents timeout → Use fallback content
- Judge timeout → Use first available agent result
- No valid results → Return waypoint with "no enrichment" flag

---

### 5.5 Module 5: Result Aggregator

**Purpose**: Collect all enriched waypoints and compile final route

**Input Contract:**
```python
{
    "transaction_id": str,
    "enriched_waypoints": list[dict]
}
```

**Output Contract:**
```python
{
    "transaction_id": str,
    "final_route": {
        "waypoints": list[dict],
        "statistics": {
            "total_waypoints": int,
            "enriched_waypoints": int,
            "failed_waypoints": int,
            "total_processing_time_ms": int,
            "average_processing_time_ms": float,
            "content_breakdown": {
                "video": int,
                "music": int,
                "history": int
            }
        }
    }
}
```

**Processing Steps:**
1. Collect all enriched waypoints
2. Calculate enrichment success rate
3. Compute processing statistics
4. Generate content breakdown
5. Order waypoints by original sequence
6. Validate completeness

**Logging:**
- Log level: INFO
- Message: "Route aggregation completed"
- Fields: transaction_id, total_waypoints, success_rate, total_time_ms

**Error Conditions:**
- Mismatched waypoint count → Warning log
- Missing waypoints → Error with details

---

### 5.6 Module 6: Response Formatter

**Purpose**: Format final output for user consumption

**Input Contract:**
```python
{
    "transaction_id": str,
    "final_route": dict
}
```

**Output Contract:**
```python
{
    "transaction_id": str,
    "route": {
        "waypoints": list[dict],  # User-friendly format
        "summary": {
            "total_distance": str,
            "total_duration": str,
            "enriched_count": int
        }
    },
    "metadata": {
        "processing_time": str,
        "timestamp": datetime,
        "version": str
    }
}
```

**Processing Steps:**
1. Convert internal format to user-friendly structure
2. Format timestamps as readable strings
3. Add API version information
4. Remove debugging fields
5. Validate JSON serializability

**Logging:**
- Log level: INFO
- Message: "Response formatting completed"
- Fields: transaction_id, response_size_bytes

**Error Conditions:**
- Serialization error → Log warning, return simplified format

---

## 6. Data Structures

### 6.1 Core Data Models

#### 6.1.1 Transaction Context

```python
class TransactionContext:
    """
    Context object propagated through entire pipeline
    """
    transaction_id: str          # UUID4 format
    created_at: datetime
    origin: str
    destination: str
    user_preferences: dict
    current_stage: str           # Module name
    metadata: dict               # Extensible metadata

    def log_stage_entry(self, stage_name: str) -> None:
        """Update current stage and log transition"""

    def get_elapsed_time_ms(self) -> int:
        """Calculate time since creation"""
```

#### 6.1.2 Waypoint

```python
class Waypoint:
    """
    Represents a single point along the route
    """
    id: int
    location_name: str
    coordinates: Coordinates
    instruction: str
    distance_from_start: float   # Meters
    step_index: int
    metadata: WaypointMetadata
    enrichment: Optional[WaypointEnrichment]

class Coordinates:
    lat: float
    lng: float

class WaypointMetadata:
    location_type: str
    nearby_landmarks: list[str]
    neighborhood: Optional[str]
    search_keywords: list[str]

class WaypointEnrichment:
    selected_content: ContentItem
    all_agent_results: dict[str, AgentResult]
    judge_decision: JudgeDecision
    processing_time_ms: int
```

#### 6.1.3 Agent Result

```python
class AgentResult:
    """
    Standard result structure for all agents
    """
    agent_name: str              # "youtube" | "spotify" | "history"
    transaction_id: str
    waypoint_id: int
    status: str                  # "success" | "timeout" | "error"
    content: Optional[ContentItem]
    error_message: Optional[str]
    execution_time_ms: int
    timestamp: datetime

class ContentItem:
    """
    Polymorphic content structure
    """
    content_type: str            # "video" | "song" | "history"
    title: str
    url: Optional[str]
    description: str
    relevance_score: float       # 0.0 to 1.0
    metadata: dict               # Agent-specific fields
```

#### 6.1.4 Judge Decision

```python
class JudgeDecision:
    """
    Result of Judge Agent evaluation
    """
    winner: str                  # Agent name
    reasoning: str               # Explanation of choice
    confidence_score: float      # 0.0 to 1.0
    individual_scores: dict[str, float]  # Scores per agent
    decision_time_ms: int
    tie_breaker_applied: bool
```

### 6.2 Configuration Structures

#### 6.2.1 System Configuration

```python
class SystemConfig:
    """
    Global system configuration
    """
    # API Keys
    google_maps_api_key: str
    youtube_api_key: str
    spotify_client_id: str
    spotify_client_secret: str

    # Timeouts (milliseconds)
    agent_timeout: int = 5000
    judge_timeout: int = 3000
    route_retrieval_timeout: int = 10000

    # Concurrency
    max_concurrent_waypoints: int = 5
    max_agent_threads: int = 50

    # Logging
    log_level: str = "INFO"
    log_file_path: str = "./logs/tour-guide.log"
    log_max_size_mb: int = 100
    log_backup_count: int = 5

    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
```

---

## 7. Asynchronous Flow Design

### 7.1 Concurrency Strategy

The system employs a **hybrid concurrency model**:

1. **Thread-based Parallelism**: For I/O-bound agent operations
2. **Process-based Parallelism**: Optional for CPU-intensive tasks (future enhancement)
3. **Async/Await Pattern**: For coordinating asynchronous operations

### 7.2 Thread Lifecycle Management

#### 7.2.1 Agent Thread Lifecycle

```
┌─────────────────┐
│  Thread Created │
│   (by Orch.)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Initialization │
│  - Get TXID     │
│  - Get Waypoint │
│  - Set Timeout  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Executing     │
│  - API Call     │
│  - Processing   │
│  - Logging      │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Success?│
    └────┬────┘
         │
    ┌────┴────┐
    │   Yes   │   No
    │         │    │
    ▼         ▼    ▼
┌────────┐  ┌──────────┐
│ Return │  │  Handle  │
│ Result │  │  Error   │
└───┬────┘  └────┬─────┘
    │            │
    └─────┬──────┘
          ▼
┌─────────────────┐
│  Thread Joins   │
│  (Orch. Waits)  │
└─────────────────┘
```

#### 7.2.2 Thread Pool Management

```python
class ThreadPoolManager:
    """
    Manages agent thread pool with timeout enforcement
    """
    def __init__(self, max_workers: int):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_futures: dict[str, Future] = {}

    def submit_agent_task(
        self,
        agent_func: Callable,
        transaction_id: str,
        waypoint: Waypoint,
        timeout_ms: int
    ) -> Future:
        """
        Submit agent task with timeout
        """
        future = self.executor.submit(agent_func, transaction_id, waypoint)
        self.active_futures[f"{transaction_id}_{waypoint.id}"] = future
        return future

    def wait_for_completion(
        self,
        futures: list[Future],
        timeout_ms: int
    ) -> list[AgentResult]:
        """
        Wait for all futures with timeout, return available results
        """
        results = []
        for future in as_completed(futures, timeout=timeout_ms/1000):
            try:
                results.append(future.result())
            except TimeoutError:
                logger.warning("Agent task timed out")
                results.append(create_timeout_result())
        return results
```

### 7.3 Synchronization Points

The system has specific synchronization points where parallel execution must converge:

1. **Agent Completion Barrier**: Orchestrator waits for all 3 agents (or timeout)
2. **Judge Completion**: Orchestrator waits for Judge decision
3. **Waypoint Batch Completion**: Result Aggregator waits for all waypoint batches
4. **Pipeline Stage Transitions**: Each module completes before next begins

### 7.4 Parallelism Hierarchy

```
Level 1: Pipeline Stages (Sequential)
│
├─ Request Validation
├─ Route Retrieval
├─ Waypoint Preprocessing
├─ Orchestration ────────────────────┐
│   │                                 │
│   Level 2: Waypoint Batches         │
│   │  (Parallel, max 5 concurrent)   │
│   │                                 │
│   ├─ Waypoint 1 ─┐                 │
│   ├─ Waypoint 2 ──┼─────────────┐  │
│   ├─ Waypoint 3 ──┤             │  │
│   ├─ Waypoint 4 ──┤             │  │
│   └─ Waypoint 5 ──┘             │  │
│       │                          │  │
│       Level 3: Agent Execution   │  │
│       (Parallel, 3 per waypoint) │  │
│       │                          │  │
│       ├─ YouTube Thread ─────────┤  │
│       ├─ Spotify Thread ─────────┼──┤
│       └─ History Thread ─────────┘  │
│           │                         │
│           Wait/Sync Point           │
│           │                         │
│       ├─ Judge Thread ──────────────┘
│           │
│           Result
│
├─ Result Aggregation
└─ Response Formatting
```

### 7.5 Error Propagation in Async Context

Errors in agent threads must be caught and converted to result objects:

```python
def safe_agent_execution(agent_func):
    """
    Wrapper ensuring exceptions don't crash threads
    """
    def wrapper(transaction_id: str, waypoint: Waypoint) -> AgentResult:
        try:
            return agent_func(transaction_id, waypoint)
        except TimeoutError:
            return AgentResult(
                status="timeout",
                error_message="Agent execution exceeded timeout",
                ...
            )
        except Exception as e:
            logger.error(f"Agent error: {str(e)}", exc_info=True)
            return AgentResult(
                status="error",
                error_message=str(e),
                ...
            )
    return wrapper
```

---

## 8. Orchestrator Design

### 8.1 Orchestrator Responsibilities

The Orchestrator is the **central nervous system** of the multi-agent platform. Its responsibilities include:

1. **Lifecycle Management**
   - Create and initialize agent threads
   - Monitor thread execution
   - Enforce timeouts
   - Clean up resources

2. **Concurrency Control**
   - Limit concurrent waypoint processing
   - Manage thread pool capacity
   - Prevent resource exhaustion

3. **State Management**
   - Track waypoint processing status
   - Maintain result cache
   - Handle partial failures

4. **Error Handling**
   - Catch agent exceptions
   - Implement retry logic
   - Provide fallback content

5. **Performance Optimization**
   - Batch waypoint processing
   - Reuse connections
   - Cache repeated queries

6. **Observability**
   - Emit structured logs
   - Track performance metrics
   - Maintain transaction context

### 8.2 Orchestrator State Machine

```
┌──────────────┐
│ INITIALIZED  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PROCESSING  │◄─────┐
│  WAYPOINTS   │      │
└──────┬───────┘      │
       │              │
       ├─ Process ────┘
       │  Next Batch
       │
       ▼
┌──────────────┐
│ AGGREGATING  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  COMPLETED   │
└──────────────┘

Error States:
┌──────────────┐
│ FAILED       │
└──────────────┘
┌──────────────┐
│ TIMEOUT      │
└──────────────┘
```

### 8.3 Orchestrator Algorithm

```python
class Orchestrator:
    def __init__(self, config: SystemConfig):
        self.config = config
        self.thread_pool = ThreadPoolManager(config.max_agent_threads)
        self.results_cache: dict[int, WaypointEnrichment] = {}

    def enrich_route(
        self,
        transaction_id: str,
        waypoints: list[Waypoint]
    ) -> list[Waypoint]:
        """
        Main orchestration method
        """
        enriched_waypoints = []

        # Process waypoints in batches
        for batch in self._create_batches(waypoints):
            batch_results = self._process_waypoint_batch(
                transaction_id,
                batch
            )
            enriched_waypoints.extend(batch_results)

        return enriched_waypoints

    def _process_waypoint_batch(
        self,
        transaction_id: str,
        waypoints: list[Waypoint]
    ) -> list[Waypoint]:
        """
        Process multiple waypoints concurrently
        """
        futures = []

        for waypoint in waypoints:
            future = self.thread_pool.submit_agent_task(
                self._enrich_single_waypoint,
                transaction_id,
                waypoint,
                self.config.agent_timeout
            )
            futures.append((waypoint, future))

        # Wait for all waypoints in batch
        results = []
        for waypoint, future in futures:
            try:
                enriched = future.result(
                    timeout=self.config.agent_timeout/1000 + 5  # Buffer
                )
                results.append(enriched)
            except TimeoutError:
                logger.error(f"Waypoint {waypoint.id} processing timeout")
                results.append(waypoint)  # Return without enrichment

        return results

    def _enrich_single_waypoint(
        self,
        transaction_id: str,
        waypoint: Waypoint
    ) -> Waypoint:
        """
        Run all agents for single waypoint
        """
        start_time = time.time()

        # Launch 3 agents in parallel
        agent_futures = {
            'youtube': self.thread_pool.executor.submit(
                youtube_agent.process, transaction_id, waypoint
            ),
            'spotify': self.thread_pool.executor.submit(
                spotify_agent.process, transaction_id, waypoint
            ),
            'history': self.thread_pool.executor.submit(
                history_agent.process, transaction_id, waypoint
            )
        }

        # Collect results with timeout
        agent_results = {}
        for agent_name, future in agent_futures.items():
            try:
                result = future.result(timeout=self.config.agent_timeout/1000)
                agent_results[agent_name] = result
            except TimeoutError:
                logger.warning(f"{agent_name} agent timeout for waypoint {waypoint.id}")
                agent_results[agent_name] = create_timeout_result(agent_name)
            except Exception as e:
                logger.error(f"{agent_name} agent error: {str(e)}")
                agent_results[agent_name] = create_error_result(agent_name, e)

        # Run Judge
        judge_result = self._run_judge(transaction_id, waypoint, agent_results)

        # Assemble enrichment
        processing_time = int((time.time() - start_time) * 1000)
        waypoint.enrichment = WaypointEnrichment(
            selected_content=judge_result.selected_content,
            all_agent_results=agent_results,
            judge_decision=judge_result,
            processing_time_ms=processing_time
        )

        return waypoint

    def _run_judge(
        self,
        transaction_id: str,
        waypoint: Waypoint,
        agent_results: dict[str, AgentResult]
    ) -> JudgeDecision:
        """
        Execute Judge agent to select best content
        """
        try:
            future = self.thread_pool.executor.submit(
                judge_agent.decide,
                transaction_id,
                waypoint,
                agent_results
            )
            decision = future.result(timeout=self.config.judge_timeout/1000)
            return decision
        except TimeoutError:
            logger.warning("Judge timeout, using fallback selection")
            return self._fallback_selection(agent_results)
        except Exception as e:
            logger.error(f"Judge error: {str(e)}")
            return self._fallback_selection(agent_results)

    def _fallback_selection(
        self,
        agent_results: dict[str, AgentResult]
    ) -> JudgeDecision:
        """
        Fallback when Judge fails: select first available result
        """
        for agent_name, result in agent_results.items():
            if result.status == "success":
                return JudgeDecision(
                    winner=agent_name,
                    reasoning="Fallback: Judge unavailable, selected first available",
                    confidence_score=0.5,
                    individual_scores={},
                    tie_breaker_applied=True
                )

        # All failed - return empty decision
        return JudgeDecision(
            winner="none",
            reasoning="All agents failed",
            confidence_score=0.0,
            individual_scores={},
            tie_breaker_applied=False
        )

    def _create_batches(
        self,
        waypoints: list[Waypoint]
    ) -> list[list[Waypoint]]:
        """
        Split waypoints into batches for concurrent processing
        """
        batch_size = self.config.max_concurrent_waypoints
        return [
            waypoints[i:i+batch_size]
            for i in range(0, len(waypoints), batch_size)
        ]
```

### 8.4 Timeout Strategy

The Orchestrator implements a **cascading timeout strategy**:

```
Total Waypoint Timeout = Agent Timeout + Judge Timeout + Buffer
                       = 5000ms + 3000ms + 1000ms
                       = 9000ms (9 seconds)

Agent Timeout = 5000ms
├─ YouTube: 5000ms max
├─ Spotify: 5000ms max
└─ History: 5000ms max

Judge Timeout = 3000ms
└─ Decision processing: 3000ms max

Buffer = 1000ms (for orchestration overhead)
```

If any timeout is exceeded:
1. Cancel pending operations
2. Use partial results
3. Log timeout event
4. Continue with next waypoint

---

## 9. Transaction ID Propagation

### 9.1 Purpose of Transaction IDs

Transaction IDs serve as the **golden thread** connecting all operations in a distributed, asynchronous system:

1. **End-to-end tracing**: Follow a request from start to finish
2. **Debugging**: Isolate logs for specific user requests
3. **Performance analysis**: Measure latency across components
4. **Error correlation**: Link related failures
5. **Audit trails**: Track system behavior

### 9.2 Transaction ID Format

```
Format: TXID-{timestamp}-{uuid}

Example: TXID-20250130T143052-7f3e4a2b-9c1d-4e8f-a5b3-6d2c8f1e9a4b

Components:
- Prefix: "TXID-" (for easy grep)
- Timestamp: ISO 8601 compact format
- UUID: UUID4 for uniqueness
```

### 9.3 Propagation Strategy

#### 9.3.1 Generation Point

```python
def create_transaction_id() -> str:
    """
    Generate unique transaction ID at request entry point
    """
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    unique_id = str(uuid.uuid4())
    return f"TXID-{timestamp}-{unique_id}"
```

**Generated in:** Module 1 (Request Validator)

#### 9.3.2 Propagation Through Modules

Every module function signature includes `transaction_id`:

```python
# Module interface pattern
def process_module(
    transaction_id: str,  # Always first parameter
    input_data: dict
) -> dict:
    logger.info("Processing started", extra={"transaction_id": transaction_id})
    # ... processing ...
    logger.info("Processing completed", extra={"transaction_id": transaction_id})
    return output_data
```

#### 9.3.3 Propagation Through Threads

Thread initialization receives transaction ID:

```python
def agent_worker(transaction_id: str, waypoint: Waypoint) -> AgentResult:
    """
    Every thread function receives transaction_id as first parameter
    """
    # Bind TXID to thread-local storage for automatic logging
    thread_context.transaction_id = transaction_id

    logger.info(
        f"Agent started for waypoint {waypoint.id}",
        extra={"transaction_id": transaction_id}
    )

    # ... agent processing ...

    return result
```

#### 9.3.4 Propagation to External APIs

Include transaction ID in API requests for external traceability:

```python
def call_google_maps_api(transaction_id: str, origin: str, dest: str):
    """
    Include TXID in headers/params for external API calls
    """
    headers = {
        "X-Transaction-ID": transaction_id,
        "User-Agent": f"TourGuide/1.0 (TXID: {transaction_id})"
    }

    response = requests.get(api_url, headers=headers)
    return response
```

### 9.4 Transaction Context Object

```python
class TransactionContext:
    """
    Thread-safe context object passed through pipeline
    """
    def __init__(self, transaction_id: str, origin: str, destination: str):
        self.transaction_id = transaction_id
        self.origin = origin
        self.destination = destination
        self.created_at = datetime.utcnow()
        self.metadata: dict = {}
        self._lock = threading.Lock()

    def add_metadata(self, key: str, value: any):
        """Thread-safe metadata addition"""
        with self._lock:
            self.metadata[key] = value

    def to_log_dict(self) -> dict:
        """Convert to logging dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "origin": self.origin,
            "destination": self.destination,
            "elapsed_ms": self.get_elapsed_time_ms()
        }
```

### 9.5 Transaction ID in Logs

Every log statement must include transaction ID:

```python
# Structured logging with TXID
logger.info(
    "Waypoint enrichment completed",
    extra={
        "transaction_id": transaction_id,
        "waypoint_id": waypoint.id,
        "selected_content_type": result.type,
        "processing_time_ms": processing_time
    }
)
```

**Log output example:**
```
2025-01-30 14:30:52.123 INFO [TXID-20250130T143052-7f3e4a2b] Waypoint enrichment completed waypoint_id=3 selected_content_type=video processing_time_ms=4521
```

---

## 10. Logging Specification

### 10.1 Logging Requirements

1. **No Console Output**: All logging via logging library, not print()
2. **Structured Logging**: Key-value pairs for machine parsing
3. **Log Rotation**: Automatic file rotation at size limits
4. **Performance**: Async logging to avoid blocking
5. **Transaction Tracing**: Every log includes transaction ID

### 10.2 Log Configuration

```python
import logging
from logging.handlers import RotatingFileHandler
import json

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logs
    """
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "transaction_id": getattr(record, "transaction_id", "N/A"),
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)

def setup_logging(config: SystemConfig):
    """
    Configure logging system
    """
    logger = logging.getLogger("tour_guide")
    logger.setLevel(getattr(logging, config.log_level))

    # Rotating file handler
    handler = RotatingFileHandler(
        filename=config.log_file_path,
        maxBytes=config.log_max_size_mb * 1024 * 1024,
        backupCount=config.log_backup_count,
        encoding='utf-8'
    )

    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

    return logger
```

### 10.3 Log Levels

| Level | Usage |
|-------|-------|
| **DEBUG** | Detailed information for diagnosing problems (waypoint preprocessing, query construction) |
| **INFO** | Confirmation that things are working (module completions, agent results) |
| **WARNING** | Indication of potential issues (timeouts, fallback usage, missing data) |
| **ERROR** | Errors that don't stop execution (agent failures, API errors) |
| **CRITICAL** | Serious errors causing system failure (missing API keys, fatal config errors) |

### 10.4 Logging by Module

#### Module 1: Request Validator

```python
# Entry log
logger.info(
    "Request received",
    extra={
        "transaction_id": txid,
        "origin": origin,
        "destination": destination
    }
)

# Validation success
logger.info(
    "Request validated",
    extra={
        "transaction_id": txid,
        "validation_time_ms": elapsed
    }
)

# Validation failure
logger.error(
    "Request validation failed",
    extra={
        "transaction_id": txid,
        "error": error_message
    }
)
```

#### Module 2: Route Retrieval

```python
# API call start
logger.debug(
    "Calling Google Maps API",
    extra={
        "transaction_id": txid,
        "origin": origin,
        "destination": destination
    }
)

# API success
logger.info(
    "Route retrieved",
    extra={
        "transaction_id": txid,
        "waypoint_count": len(waypoints),
        "total_distance_km": distance,
        "api_response_time_ms": response_time
    }
)

# API failure
logger.error(
    "Google Maps API error",
    extra={
        "transaction_id": txid,
        "status_code": response.status_code,
        "error_message": response.text
    }
)
```

#### Module 4: Orchestrator

```python
# Waypoint processing start
logger.info(
    "Starting waypoint enrichment",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "location_name": waypoint.location_name
    }
)

# Agent completion
logger.debug(
    "Agent completed",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "agent_name": agent_name,
        "status": result.status,
        "execution_time_ms": result.execution_time_ms
    }
)

# Judge decision
logger.info(
    "Judge decision made",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "winner": decision.winner,
        "confidence": decision.confidence_score,
        "reasoning": decision.reasoning
    }
)

# Waypoint completion
logger.info(
    "Waypoint enrichment completed",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "selected_type": enrichment.selected_content.content_type,
        "total_processing_time_ms": processing_time
    }
)
```

#### Agents (YouTube, Spotify, History)

```python
# Agent start
logger.debug(
    f"{agent_name} agent started",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "search_query": query
    }
)

# API call
logger.debug(
    f"{agent_name} API called",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "api_endpoint": endpoint
    }
)

# Success
logger.info(
    f"{agent_name} agent completed",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "result_count": len(results),
        "selected_title": result.title,
        "relevance_score": result.relevance_score
    }
)

# Timeout
logger.warning(
    f"{agent_name} agent timeout",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "timeout_ms": timeout
    }
)

# Error
logger.error(
    f"{agent_name} agent error",
    extra={
        "transaction_id": txid,
        "waypoint_id": waypoint.id,
        "error_type": type(e).__name__,
        "error_message": str(e)
    },
    exc_info=True
)
```

### 10.5 Log Analysis

Logs support queries like:

```bash
# All logs for specific transaction
grep "TXID-20250130T143052-7f3e4a2b" tour-guide.log

# All agent timeouts
grep "\"level\":\"WARNING\"" tour-guide.log | grep "timeout"

# Performance analysis for waypoints
grep "\"message\":\"Waypoint enrichment completed\"" tour-guide.log | \
  jq '.total_processing_time_ms'

# Judge decisions
grep "\"message\":\"Judge decision made\"" tour-guide.log | \
  jq '{winner: .winner, confidence: .confidence}'
```

### 10.6 Log Rotation Strategy

```
/var/log/tour-guide/
├── tour-guide.log          (current, max 100MB)
├── tour-guide.log.1        (previous rotation)
├── tour-guide.log.2
├── tour-guide.log.3
├── tour-guide.log.4
└── tour-guide.log.5        (oldest, deleted on next rotation)
```

**Rotation triggers:**
- File size exceeds 100MB
- Daily rotation at midnight (optional)

**Retention:**
- Keep last 5 rotated files
- Total maximum storage: 600MB

---

## 11. Error Handling Strategy

### 11.1 Error Classification

#### 11.1.1 Recoverable Errors

Errors that allow continued processing:

| Error Type | Example | Handling Strategy |
|------------|---------|-------------------|
| Agent Timeout | YouTube agent takes > 5s | Use partial results, log warning |
| No Results Found | Spotify finds no songs | Return empty result, continue |
| API Rate Limit | YouTube quota exceeded | Use cached/fallback content |
| Network Glitch | Transient connection error | Retry up to 3 times |

#### 11.1.2 Fatal Errors

Errors that stop processing:

| Error Type | Example | Handling Strategy |
|------------|---------|-------------------|
| Invalid API Key | Google Maps auth fails | Return error to user, log critical |
| Malformed Input | Invalid origin format | Reject request, return validation error |
| No Route Found | Google Maps returns ZERO_RESULTS | Return user-friendly error |
| System Resource | Out of memory, disk full | Fail gracefully, alert operations |

### 11.2 Error Handling by Layer

#### 11.2.1 Agent Layer

```python
class AgentExecutor:
    def execute_with_timeout(
        self,
        agent_func: Callable,
        timeout_ms: int,
        *args, **kwargs
    ) -> AgentResult:
        """
        Execute agent with timeout and error handling
        """
        try:
            # Set timeout
            signal.alarm(timeout_ms // 1000)

            # Execute
            result = agent_func(*args, **kwargs)

            # Cancel alarm
            signal.alarm(0)

            return result

        except TimeoutError:
            logger.warning("Agent timeout", extra={"timeout_ms": timeout_ms})
            return AgentResult(
                status="timeout",
                error_message=f"Agent exceeded {timeout_ms}ms timeout"
            )

        except requests.exceptions.RequestException as e:
            logger.error("Agent network error", exc_info=True)
            return AgentResult(
                status="error",
                error_message=f"Network error: {str(e)}"
            )

        except Exception as e:
            logger.error("Agent unexpected error", exc_info=True)
            return AgentResult(
                status="error",
                error_message=f"Unexpected error: {str(e)}"
            )
```

#### 11.2.2 Orchestrator Layer

```python
class Orchestrator:
    def handle_waypoint_failure(
        self,
        waypoint: Waypoint,
        error: Exception
    ) -> Waypoint:
        """
        Handle complete waypoint processing failure
        """
        logger.error(
            "Waypoint processing failed",
            extra={
                "waypoint_id": waypoint.id,
                "error": str(error)
            }
        )

        # Return waypoint with fallback content
        waypoint.enrichment = WaypointEnrichment(
            selected_content=self._get_fallback_content(waypoint),
            all_agent_results={},
            judge_decision=JudgeDecision(
                winner="fallback",
                reasoning="All agents failed, using fallback",
                confidence_score=0.0
            ),
            processing_time_ms=0
        )

        return waypoint

    def _get_fallback_content(self, waypoint: Waypoint) -> ContentItem:
        """
        Provide generic fallback content
        """
        return ContentItem(
            content_type="history",
            title=f"About {waypoint.location_name}",
            description=f"Passing through {waypoint.location_name}",
            relevance_score=0.0
        )
```

#### 11.2.3 Pipeline Layer

```python
def execute_pipeline(transaction_id: str, origin: str, destination: str):
    """
    Execute full pipeline with error handling at each stage
    """
    try:
        # Stage 1: Validate
        validated = validate_request(transaction_id, origin, destination)

    except ValidationError as e:
        logger.error("Validation failed", extra={"error": str(e)})
        return ErrorResponse(
            transaction_id=transaction_id,
            error_code="VALIDATION_ERROR",
            message=str(e)
        )

    try:
        # Stage 2: Retrieve Route
        route = retrieve_route(transaction_id, validated)

    except RouteRetrievalError as e:
        logger.error("Route retrieval failed", extra={"error": str(e)})
        return ErrorResponse(
            transaction_id=transaction_id,
            error_code="ROUTE_NOT_FOUND",
            message="Unable to find route between locations"
        )

    try:
        # Stage 3-6: Continue pipeline
        # ... (with similar try-except blocks)

    except Exception as e:
        # Catch-all for unexpected errors
        logger.critical("Unexpected pipeline error", exc_info=True)
        return ErrorResponse(
            transaction_id=transaction_id,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred"
        )
```

### 11.3 Retry Logic

```python
class RetryableOperation:
    def __init__(self, max_retries: int = 3, backoff_ms: int = 1000):
        self.max_retries = max_retries
        self.backoff_ms = backoff_ms

    def execute(self, operation: Callable, *args, **kwargs):
        """
        Execute operation with exponential backoff retry
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)

            except RetryableError as e:
                last_exception = e
                wait_time = self.backoff_ms * (2 ** attempt)

                logger.warning(
                    f"Operation failed, retrying in {wait_time}ms",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries,
                        "error": str(e)
                    }
                )

                time.sleep(wait_time / 1000)

        # All retries exhausted
        raise MaxRetriesExceeded(
            f"Operation failed after {self.max_retries} attempts",
            last_exception
        )
```

**Retryable operations:**
- Google Maps API calls (network errors)
- External API requests (transient failures)
- Database operations (connection issues)

**Non-retryable operations:**
- Validation errors (will fail again)
- Authentication errors (need manual fix)
- Malformed responses (parsing will fail again)

### 11.4 Graceful Degradation

The system prioritizes **continuing with partial results** over complete failure:

```
Full Success: All agents return valid results
             ↓
Degraded:    2 of 3 agents succeed
             ↓ (still functional)
Minimal:     1 of 3 agents succeeds
             ↓ (still provides value)
Fallback:    All agents fail → use generic content
             ↓ (route still returned)
Fatal:       Google Maps fails → no route data
             ↓
Error:       Return error to user
```

---

## 12. Performance & Concurrency

### 12.1 Performance Goals

| Metric | Target | Measurement |
|--------|--------|-------------|
| **End-to-End Latency** | < 30 seconds for 10-waypoint route | 95th percentile |
| **Agent Latency** | < 5 seconds per agent | 99th percentile |
| **Throughput** | 10 concurrent routes | Sustained load |
| **Success Rate** | > 95% waypoints enriched | Per-route average |
| **Resource Usage** | < 500 MB memory per route | Peak usage |

### 12.2 Concurrency Benefits

#### 12.2.1 Sequential vs. Parallel Comparison

**Sequential Processing (without concurrency):**

```
10 waypoints × (3 agents × 5s + judge 3s) = 10 × 18s = 180 seconds
```

**Parallel Processing (agents per waypoint):**

```
10 waypoints × (max(5s, 5s, 5s) + 3s) = 10 × 8s = 80 seconds
```

**Batched Parallel Processing (5 waypoints concurrent):**

```
Batch 1: 5 waypoints × 8s = 8s
Batch 2: 5 waypoints × 8s = 8s
Total: 16 seconds
```

**Speedup: 11.25x improvement**

#### 12.2.2 Parallelism Breakdown

```
Total Time Savings:

1. Agent-level parallelism:
   Sequential: 3 agents × 5s = 15s
   Parallel:   max(5s, 5s, 5s) = 5s
   Savings:    10s per waypoint

2. Waypoint-level parallelism:
   Sequential: 10 waypoints × 8s = 80s
   Parallel:   2 batches × 8s = 16s
   Savings:    64s total

Combined: 180s → 16s (91% reduction)
```

### 12.3 Bottleneck Analysis

#### 12.3.1 Identifying Bottlenecks

Potential bottlenecks in the system:

1. **Google Maps API Call** (sequential, single point)
   - Latency: ~500ms - 2s
   - Mitigation: Cache frequent routes

2. **Agent API Rate Limits**
   - YouTube: 10,000 requests/day
   - Spotify: Varies by auth
   - Mitigation: Request batching, caching

3. **Thread Pool Saturation**
   - Max threads: 50
   - Agents per waypoint: 4
   - Max concurrent waypoints: 50/4 = 12
   - Mitigation: Tune pool size based on load

4. **Judge LLM Latency** (if using LLM)
   - Latency: 1-3s per decision
   - Mitigation: Use fast model, cache similar decisions

#### 12.3.2 Performance Monitoring

```python
class PerformanceMonitor:
    """
    Track performance metrics throughout pipeline
    """
    def __init__(self):
        self.metrics = {
            "route_retrieval_ms": [],
            "agent_execution_ms": [],
            "judge_decision_ms": [],
            "total_pipeline_ms": []
        }

    def record_metric(self, metric_name: str, value: float):
        """Record timing metric"""
        self.metrics[metric_name].append(value)

    def get_statistics(self, metric_name: str) -> dict:
        """Calculate statistics for metric"""
        values = self.metrics[metric_name]
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99),
            "min": min(values),
            "max": max(values)
        }
```

### 12.4 Scalability Considerations

#### 12.4.1 Horizontal Scaling

To scale beyond single-machine capacity:

```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐   ┌───▼──┐
│ App  │   │ App  │  (Multiple instances)
│ Inst │   │ Inst │
│  1   │   │  2   │
└───┬──┘   └───┬──┘
    │          │
    └────┬─────┘
         │
┌────────▼────────┐
│  Shared Cache   │
│    (Redis)      │
└─────────────────┘
```

**Stateless Design**: Each app instance handles requests independently

**Shared Cache**: Results cached in Redis for reuse across instances

**Session Affinity**: Not required (stateless processing)

#### 12.4.2 Vertical Scaling

Tuning single-instance performance:

```python
# Scale thread pool based on CPU cores
import multiprocessing

cpu_count = multiprocessing.cpu_count()
max_threads = cpu_count * 5  # I/O-bound work, higher multiplier

config = SystemConfig(
    max_agent_threads=max_threads,
    max_concurrent_waypoints=max_threads // 4
)
```

#### 12.4.3 Caching Strategy

```python
class ResultCache:
    """
    Cache agent results to avoid redundant API calls
    """
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: dict = {}
        self.ttl = ttl_seconds

    def get_cache_key(self, agent_name: str, query: str) -> str:
        """Generate cache key from agent and query"""
        return f"{agent_name}:{hashlib.md5(query.encode()).hexdigest()}"

    def get(self, agent_name: str, query: str) -> Optional[AgentResult]:
        """Retrieve cached result if available and fresh"""
        key = self.get_cache_key(agent_name, query)

        if key in self.cache:
            cached_result, timestamp = self.cache[key]
            age_seconds = (datetime.utcnow() - timestamp).total_seconds()

            if age_seconds < self.ttl:
                logger.debug(f"Cache hit for {agent_name}", extra={"query": query})
                return cached_result

        return None

    def set(self, agent_name: str, query: str, result: AgentResult):
        """Store result in cache"""
        key = self.get_cache_key(agent_name, query)
        self.cache[key] = (result, datetime.utcnow())
```

**Cache hit rate goal**: > 30% for common routes

### 12.5 Concurrency Model Selection

**Chosen Model: Thread-based Concurrency**

Rationale:
- Agents are I/O-bound (API calls)
- Python's GIL not a bottleneck for I/O operations
- Simpler than multiprocessing
- Shared memory for caching

Alternative (future consideration):
- **Async/Await**: Even better for I/O-bound tasks
- **Multiprocessing**: If CPU-bound operations added (e.g., ML inference)

---

## 13. Development Phases

### 13.1 Phase 1: Block Design

**Objective**: Define system architecture and module contracts

**Duration**: Week 1-2

**Deliverables**:

1. **Module Specifications**
   - Input/output contracts for each module
   - Data structure definitions
   - Interface documentation

2. **Architecture Diagrams**
   - System overview diagram
   - Module interaction diagram
   - Data flow diagram

3. **Mock Implementations**
   - Stub functions for each module
   - Hardcoded sample data
   - End-to-end skeleton

**Tasks**:

- [ ] Define `TransactionContext` class
- [ ] Define `Waypoint` and related data structures
- [ ] Design module interfaces (6 modules)
- [ ] Create sequence diagrams for main flow
- [ ] Implement mock request validator
- [ ] Implement mock route retriever (hardcoded waypoints)
- [ ] Implement mock waypoint preprocessor
- [ ] Implement mock orchestrator (sequential, no threads)
- [ ] Implement mock agents (return dummy data)
- [ ] Implement mock aggregator
- [ ] Implement mock formatter
- [ ] Test end-to-end flow with mocks

**Success Criteria**:
- ✅ All module interfaces documented
- ✅ Mock pipeline runs start to finish
- ✅ Sample output matches expected format

---

### 13.2 Phase 2: Data Flow Planning

**Objective**: Document and validate complete data flow through system

**Duration**: Week 3

**Deliverables**:

1. **Data Flow Documentation**
   - Complete input/output specification per module
   - Sample data at each pipeline stage
   - Transformation rules

2. **Logging Plan**
   - Log statements for each module
   - Transaction ID propagation strategy
   - Log format specification

3. **Test Data Sets**
   - Valid input scenarios
   - Edge cases
   - Error scenarios

**Tasks**:

- [ ] Document sample data structures
- [ ] Create example transactions with real data
- [ ] Design logging schema (JSON structure)
- [ ] Implement logging configuration
- [ ] Add logging to all mock modules
- [ ] Test transaction ID propagation
- [ ] Create test cases for data transformations
- [ ] Validate log output format
- [ ] Test log rotation mechanism
- [ ] Create data validation functions

**Success Criteria**:
- ✅ Every pipeline stage has documented input/output
- ✅ Logs written at every stage transition
- ✅ Transaction ID appears in all logs
- ✅ Sample run produces complete log trace

---

### 13.3 Phase 3: Multithreading/Multiprocessing Layer

**Objective**: Implement asynchronous agent execution and orchestration

**Duration**: Week 4-5

**Deliverables**:

1. **Concurrent Agent Execution**
   - Thread pool implementation
   - Timeout enforcement
   - Result aggregation

2. **Orchestrator Implementation**
   - Thread lifecycle management
   - Error handling
   - Performance optimization

3. **Integration Testing**
   - Load testing
   - Concurrency testing
   - Error scenario testing

**Tasks**:

**Week 4: Basic Concurrency**
- [ ] Implement `ThreadPoolManager` class
- [ ] Implement agent thread wrapper functions
- [ ] Add timeout enforcement
- [ ] Implement result collection
- [ ] Test 3 agents running in parallel
- [ ] Implement Judge agent threading
- [ ] Test single waypoint enrichment

**Week 5: Full Orchestration**
- [ ] Implement waypoint batching logic
- [ ] Add batch-level concurrency
- [ ] Implement error handling in threads
- [ ] Add retry logic for transient failures
- [ ] Implement graceful degradation
- [ ] Add performance monitoring
- [ ] Conduct load testing
- [ ] Optimize thread pool sizing
- [ ] Test with 50-waypoint routes
- [ ] Validate all error scenarios

**Success Criteria**:
- ✅ Agents execute in parallel per waypoint
- ✅ Multiple waypoints processed concurrently
- ✅ Timeouts enforced correctly
- ✅ Errors handled without crashes
- ✅ Performance targets met (< 30s for 10 waypoints)

---

### 13.4 Phase 4: External API Integration (Implementation)

**Objective**: Replace mocks with real API integrations

**Duration**: Week 6-7

**Deliverables**:

1. **Google Maps Integration**
   - Real route retrieval
   - Error handling
   - Rate limit management

2. **Agent API Integrations**
   - YouTube Data API
   - Spotify Web API
   - Wikipedia/History API

3. **Judge Implementation**
   - LLM integration or rule-based logic
   - Decision algorithm
   - Scoring mechanism

**Tasks**:

**Week 6: Infrastructure APIs**
- [ ] Obtain Google Maps API key
- [ ] Implement Google Maps client
- [ ] Test route retrieval with various locations
- [ ] Handle API errors (ZERO_RESULTS, etc.)
- [ ] Implement request caching
- [ ] Test rate limiting

**Week 7: Content APIs**
- [ ] Obtain YouTube API key
- [ ] Implement YouTube agent (real)
- [ ] Obtain Spotify credentials
- [ ] Implement Spotify agent (real)
- [ ] Implement History agent (Wikipedia API)
- [ ] Test all agents with sample queries
- [ ] Implement Judge agent logic
- [ ] Test Judge decision-making
- [ ] Conduct end-to-end integration test

**Success Criteria**:
- ✅ All APIs successfully integrated
- ✅ Real content returned for waypoints
- ✅ Error handling works with real API errors
- ✅ System handles rate limits gracefully

---

### 13.5 Phase 5: Testing & Optimization

**Objective**: Comprehensive testing and performance tuning

**Duration**: Week 8

**Deliverables**:

1. **Test Suite**
   - Unit tests for all modules
   - Integration tests
   - End-to-end tests

2. **Performance Report**
   - Latency measurements
   - Bottleneck analysis
   - Optimization recommendations

3. **Bug Fixes**
   - All critical bugs resolved
   - Known issues documented

**Tasks**:

- [ ] Write unit tests for each module
- [ ] Write integration tests for pipeline
- [ ] Create end-to-end test scenarios
- [ ] Run performance benchmarks
- [ ] Analyze logs for errors
- [ ] Optimize slow operations
- [ ] Test edge cases (0 waypoints, 100 waypoints)
- [ ] Validate error recovery
- [ ] Load test with concurrent requests
- [ ] Review and refactor code
- [ ] Update documentation
- [ ] Prepare deployment package

**Success Criteria**:
- ✅ 90% code coverage
- ✅ All tests passing
- ✅ Performance targets met
- ✅ No critical bugs

---

## 14. Example System Run-Through

### 14.1 Scenario

**User Request:**
```json
{
  "origin": "Empire State Building, New York, NY",
  "destination": "Central Park, New York, NY"
}
```

### 14.2 Step-by-Step Execution

#### Step 1: Request Validation (Module 1)

**Input:**
```json
{
  "origin": "Empire State Building, New York, NY",
  "destination": "Central Park, New York, NY"
}
```

**Processing:**
1. Generate transaction ID: `TXID-20250130T143052-7f3e4a2b`
2. Validate origin: ✅ Valid
3. Validate destination: ✅ Valid
4. Initialize logging context

**Output:**
```json
{
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "origin": "Empire State Building, New York, NY",
  "destination": "Central Park, New York, NY",
  "preferences": {},
  "timestamp": "2025-01-30T14:30:52.123Z",
  "status": "valid"
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:30:52.123Z",
  "level": "INFO",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "request_validator",
  "message": "Request validated",
  "origin": "Empire State Building, New York, NY",
  "destination": "Central Park, New York, NY"
}
```

---

#### Step 2: Route Retrieval (Module 2)

**Processing:**
1. Call Google Maps Directions API
2. Parse response
3. Extract 8 waypoints from route

**Output (condensed):**
```json
{
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "route": {
    "distance": "3.2 km",
    "duration": "12 mins",
    "waypoints": [
      {
        "id": 1,
        "location_name": "5th Avenue & E 34th St",
        "coordinates": {"lat": 40.748817, "lng": -73.985428},
        "instruction": "Head north on 5th Ave"
      },
      {
        "id": 2,
        "location_name": "5th Avenue & E 42nd St",
        "coordinates": {"lat": 40.753182, "lng": -73.981736},
        "instruction": "Continue on 5th Ave"
      },
      {
        "id": 3,
        "location_name": "5th Avenue & E 59th St",
        "coordinates": {"lat": 40.764526, "lng": -73.973448},
        "instruction": "Turn left onto Central Park S"
      }
      // ... 5 more waypoints
    ]
  },
  "api_status": "OK",
  "timestamp": "2025-01-30T14:30:53.456Z"
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:30:53.456Z",
  "level": "INFO",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "route_retrieval",
  "message": "Route retrieved successfully",
  "waypoint_count": 8,
  "total_distance": "3.2 km",
  "api_response_time_ms": 1333
}
```

---

#### Step 3: Waypoint Preprocessing (Module 3)

**Processing for Waypoint 1:**

**Input:**
```json
{
  "id": 1,
  "location_name": "5th Avenue & E 34th St",
  "coordinates": {"lat": 40.748817, "lng": -73.985428},
  "instruction": "Head north on 5th Ave"
}
```

**Output (enriched):**
```json
{
  "id": 1,
  "location_name": "5th Avenue & E 34th St",
  "coordinates": {"lat": 40.748817, "lng": -73.985428},
  "instruction": "Head north on 5th Ave",
  "metadata": {
    "location_type": "intersection",
    "nearby_landmarks": ["Empire State Building"],
    "neighborhood": "Midtown Manhattan",
    "search_keywords": ["5th Avenue", "34th Street", "Midtown", "Manhattan"]
  },
  "agent_context": {
    "youtube_query": "5th Avenue 34th Street New York landmarks",
    "spotify_query": "New York City Manhattan urban",
    "history_query": "5th Avenue 34th Street history Manhattan"
  }
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:30:53.567Z",
  "level": "DEBUG",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "waypoint_preprocessor",
  "message": "Waypoint preprocessed",
  "waypoint_id": 1,
  "location_type": "intersection",
  "search_keywords": ["5th Avenue", "34th Street", "Midtown", "Manhattan"]
}
```

---

#### Step 4: Orchestrator - Waypoint Enrichment (Module 4)

**Processing Waypoint 1:**

##### 4a. Launch Agents in Parallel

**YouTube Agent (Thread 1):**
- Query: "5th Avenue 34th Street New York landmarks"
- API Call: YouTube Data API search
- Duration: 3.2s
- Result:
```json
{
  "agent_name": "youtube",
  "status": "success",
  "content": {
    "content_type": "video",
    "title": "Walking Tour: 5th Avenue from Empire State Building",
    "url": "https://youtube.com/watch?v=xyz123",
    "description": "Experience walking down iconic 5th Avenue...",
    "relevance_score": 0.85
  },
  "execution_time_ms": 3200
}
```

**Spotify Agent (Thread 2):**
- Query: "New York City Manhattan urban"
- API Call: Spotify search
- Duration: 2.8s
- Result:
```json
{
  "agent_name": "spotify",
  "status": "success",
  "content": {
    "content_type": "song",
    "title": "Empire State of Mind",
    "url": "https://open.spotify.com/track/abc456",
    "description": "Jay-Z feat. Alicia Keys - The Blueprint 3",
    "relevance_score": 0.92
  },
  "execution_time_ms": 2800
}
```

**History Agent (Thread 3):**
- Query: "5th Avenue 34th Street history Manhattan"
- API Call: Wikipedia API
- Duration: 2.1s
- Result:
```json
{
  "agent_name": "history",
  "status": "success",
  "content": {
    "content_type": "history",
    "title": "Historic 5th Avenue",
    "description": "Fifth Avenue between 34th and 42nd Street has been a major commercial corridor since the early 1900s. The Empire State Building, completed in 1931...",
    "relevance_score": 0.78
  },
  "execution_time_ms": 2100
}
```

**Log Entries:**
```json
[
  {
    "timestamp": "2025-01-30T14:30:53.600Z",
    "level": "DEBUG",
    "transaction_id": "TXID-20250130T143052-7f3e4a2b",
    "module": "youtube_agent",
    "message": "Agent started",
    "waypoint_id": 1,
    "search_query": "5th Avenue 34th Street New York landmarks"
  },
  {
    "timestamp": "2025-01-30T14:30:56.800Z",
    "level": "INFO",
    "transaction_id": "TXID-20250130T143052-7f3e4a2b",
    "module": "youtube_agent",
    "message": "Agent completed",
    "waypoint_id": 1,
    "result_count": 1,
    "selected_title": "Walking Tour: 5th Avenue from Empire State Building",
    "relevance_score": 0.85,
    "execution_time_ms": 3200
  }
  // Similar logs for Spotify and History agents
]
```

##### 4b. Judge Agent Decision

**Input to Judge:**
- YouTube result (relevance: 0.85)
- Spotify result (relevance: 0.92)
- History result (relevance: 0.78)

**Judge Processing:**
1. Evaluate relevance scores
2. Consider content diversity (previous waypoints)
3. Apply decision criteria:
   - Relevance to location: 40%
   - Content quality: 30%
   - Route diversity: 20%
   - User preference: 10%

**Judge Output:**
```json
{
  "winner": "spotify",
  "reasoning": "Spotify's 'Empire State of Mind' has highest relevance (0.92) and strong cultural connection to location. Provides musical variety for route.",
  "confidence_score": 0.88,
  "individual_scores": {
    "youtube": 0.82,
    "spotify": 0.89,
    "history": 0.71
  },
  "decision_time_ms": 1200,
  "tie_breaker_applied": false
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:30:58.000Z",
  "level": "INFO",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "judge_agent",
  "message": "Judge decision made",
  "waypoint_id": 1,
  "winner": "spotify",
  "confidence": 0.88,
  "reasoning": "Spotify's 'Empire State of Mind' has highest relevance..."
}
```

##### 4c. Assemble Waypoint Enrichment

**Final Enriched Waypoint 1:**
```json
{
  "id": 1,
  "location_name": "5th Avenue & E 34th St",
  "coordinates": {"lat": 40.748817, "lng": -73.985428},
  "instruction": "Head north on 5th Ave",
  "enrichment": {
    "selected_content": {
      "type": "song",
      "title": "Empire State of Mind",
      "url": "https://open.spotify.com/track/abc456",
      "description": "Jay-Z feat. Alicia Keys - The Blueprint 3",
      "source": "spotify"
    },
    "all_agent_results": {
      "youtube": { /* result */ },
      "spotify": { /* result */ },
      "history": { /* result */ }
    },
    "judge_decision": { /* decision */ },
    "processing_time_ms": 4400
  }
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:30:58.000Z",
  "level": "INFO",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "orchestrator",
  "message": "Waypoint enrichment completed",
  "waypoint_id": 1,
  "selected_type": "song",
  "total_processing_time_ms": 4400,
  "agent_success_count": 3
}
```

**Repeat for remaining 7 waypoints...**

---

#### Step 5: Result Aggregation (Module 5)

**Processing:**
1. Collect all 8 enriched waypoints
2. Calculate statistics

**Output:**
```json
{
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "final_route": {
    "waypoints": [ /* 8 enriched waypoints */ ],
    "statistics": {
      "total_waypoints": 8,
      "enriched_waypoints": 8,
      "failed_waypoints": 0,
      "total_processing_time_ms": 18500,
      "average_processing_time_ms": 2312.5,
      "content_breakdown": {
        "video": 2,
        "music": 4,
        "history": 2
      }
    }
  }
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:31:11.500Z",
  "level": "INFO",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "result_aggregator",
  "message": "Route aggregation completed",
  "total_waypoints": 8,
  "success_rate": 1.0,
  "total_time_ms": 18500
}
```

---

#### Step 6: Response Formatting (Module 6)

**Processing:**
1. Convert to user-friendly format
2. Remove internal debugging fields
3. Add metadata

**Final Output:**
```json
{
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "route": {
    "summary": {
      "origin": "Empire State Building, New York, NY",
      "destination": "Central Park, New York, NY",
      "total_distance": "3.2 km",
      "total_duration": "12 mins",
      "enriched_count": 8
    },
    "waypoints": [
      {
        "step": 1,
        "location": "5th Avenue & E 34th St",
        "instruction": "Head north on 5th Ave",
        "content": {
          "type": "song",
          "title": "Empire State of Mind",
          "artist": "Jay-Z feat. Alicia Keys",
          "url": "https://open.spotify.com/track/abc456"
        }
      },
      {
        "step": 2,
        "location": "5th Avenue & E 42nd St",
        "instruction": "Continue on 5th Ave",
        "content": {
          "type": "video",
          "title": "Grand Central Terminal History",
          "url": "https://youtube.com/watch?v=def789"
        }
      }
      // ... 6 more waypoints
    ]
  },
  "metadata": {
    "processing_time": "19.4 seconds",
    "timestamp": "2025-01-30T14:31:11.500Z",
    "version": "1.0.0"
  }
}
```

**Log Entry:**
```json
{
  "timestamp": "2025-01-30T14:31:11.567Z",
  "level": "INFO",
  "transaction_id": "TXID-20250130T143052-7f3e4a2b",
  "module": "response_formatter",
  "message": "Response formatting completed",
  "response_size_bytes": 2456
}
```

---

### 14.3 Complete Log Trace

User can search logs for this transaction:

```bash
grep "TXID-20250130T143052-7f3e4a2b" tour-guide.log
```

**Output (summarized):**
```
14:30:52.123 INFO [TXID-...] Request validated
14:30:53.456 INFO [TXID-...] Route retrieved successfully waypoint_count=8
14:30:53.567 DEBUG [TXID-...] Waypoint preprocessed waypoint_id=1
14:30:53.600 DEBUG [TXID-...] youtube_agent started waypoint_id=1
14:30:53.602 DEBUG [TXID-...] spotify_agent started waypoint_id=1
14:30:53.604 DEBUG [TXID-...] history_agent started waypoint_id=1
14:30:56.800 INFO [TXID-...] youtube_agent completed waypoint_id=1
14:30:56.402 INFO [TXID-...] spotify_agent completed waypoint_id=1
14:30:55.704 INFO [TXID-...] history_agent completed waypoint_id=1
14:30:58.000 INFO [TXID-...] Judge decision made waypoint_id=1 winner=spotify
14:30:58.000 INFO [TXID-...] Waypoint enrichment completed waypoint_id=1
... (repeat for waypoints 2-8)
14:31:11.500 INFO [TXID-...] Route aggregation completed
14:31:11.567 INFO [TXID-...] Response formatting completed
```

**Total Elapsed Time:** 19.4 seconds ✅ (under 30s target)

---

## 15. API Specifications

### 15.1 External APIs

#### 15.1.1 Google Maps Directions API

**Endpoint:**
```
https://maps.googleapis.com/maps/api/directions/json
```

**Parameters:**
- `origin`: Starting address or lat/lng
- `destination`: Ending address or lat/lng
- `key`: API key
- `mode`: `driving` (default)
- `alternatives`: `false`

**Sample Request:**
```http
GET https://maps.googleapis.com/maps/api/directions/json?origin=Empire+State+Building&destination=Central+Park&key=YOUR_API_KEY
```

**Sample Response (condensed):**
```json
{
  "routes": [{
    "legs": [{
      "steps": [
        {
          "html_instructions": "Head <b>north</b> on <b>5th Ave</b>",
          "distance": {"text": "0.5 mi", "value": 804},
          "duration": {"text": "3 mins", "value": 180},
          "start_location": {"lat": 40.748817, "lng": -73.985428},
          "end_location": {"lat": 40.753182, "lng": -73.981736}
        }
      ]
    }]
  }],
  "status": "OK"
}
```

**Rate Limits:**
- 40,000 requests/month (free tier)
- Mitigation: Cache routes

---

#### 15.1.2 YouTube Data API v3

**Endpoint:**
```
https://www.googleapis.com/youtube/v3/search
```

**Parameters:**
- `part`: `snippet`
- `q`: Search query
- `type`: `video`
- `maxResults`: `5`
- `key`: API key

**Sample Request:**
```http
GET https://www.googleapis.com/youtube/v3/search?part=snippet&q=5th+Avenue+New+York&type=video&maxResults=5&key=YOUR_API_KEY
```

**Sample Response (condensed):**
```json
{
  "items": [
    {
      "id": {"videoId": "xyz123"},
      "snippet": {
        "title": "Walking Tour: 5th Avenue",
        "description": "Experience walking down iconic 5th Avenue...",
        "thumbnails": {
          "default": {"url": "https://..."}
        }
      }
    }
  ]
}
```

**Rate Limits:**
- 10,000 quota units/day
- Search costs 100 units
- Mitigation: Cache results, limit searches

---

#### 15.1.3 Spotify Web API

**Authentication:**
- Client Credentials Flow
- Token endpoint: `https://accounts.spotify.com/api/token`

**Search Endpoint:**
```
https://api.spotify.com/v1/search
```

**Parameters:**
- `q`: Search query
- `type`: `track`
- `limit`: `5`

**Sample Request:**
```http
GET https://api.spotify.com/v1/search?q=New+York+City&type=track&limit=5
Authorization: Bearer {access_token}
```

**Sample Response (condensed):**
```json
{
  "tracks": {
    "items": [
      {
        "name": "Empire State of Mind",
        "artists": [{"name": "Jay-Z"}],
        "album": {"name": "The Blueprint 3"},
        "external_urls": {
          "spotify": "https://open.spotify.com/track/abc456"
        }
      }
    ]
  }
}
```

**Rate Limits:**
- Varies by auth type
- Mitigation: Request batching

---

#### 15.1.4 Wikipedia API

**Endpoint:**
```
https://en.wikipedia.org/api/rest_v1/page/summary/{title}
```

**Sample Request:**
```http
GET https://en.wikipedia.org/api/rest_v1/page/summary/Fifth_Avenue
```

**Sample Response (condensed):**
```json
{
  "title": "Fifth Avenue",
  "extract": "Fifth Avenue is a major and prominent thoroughfare in Manhattan, New York City...",
  "thumbnail": {
    "source": "https://..."
  }
}
```

**Rate Limits:**
- 200 requests/second
- No authentication required

---

### 15.2 System API (for external consumers)

#### 15.2.1 Enrich Route Endpoint

**Endpoint:**
```
POST /api/v1/route/enrich
```

**Request Body:**
```json
{
  "origin": "string",
  "destination": "string",
  "preferences": {
    "content_type": "auto|video|music|history",
    "avoid": ["string"]
  }
}
```

**Response (Success):**
```json
{
  "transaction_id": "string",
  "route": {
    "summary": {
      "origin": "string",
      "destination": "string",
      "total_distance": "string",
      "total_duration": "string",
      "enriched_count": 0
    },
    "waypoints": [
      {
        "step": 0,
        "location": "string",
        "instruction": "string",
        "content": {
          "type": "video|song|history",
          "title": "string",
          "url": "string",
          "description": "string"
        }
      }
    ]
  },
  "metadata": {
    "processing_time": "string",
    "timestamp": "datetime",
    "version": "string"
  }
}
```

**Response (Error):**
```json
{
  "transaction_id": "string",
  "error_code": "VALIDATION_ERROR|ROUTE_NOT_FOUND|INTERNAL_ERROR",
  "message": "string",
  "timestamp": "datetime"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Validation error
- `404 Not Found`: No route found
- `500 Internal Server Error`: System error
- `503 Service Unavailable`: External API unavailable

---

## 16. Testing Strategy

### 16.1 Test Pyramid

```
        ┌──────────────┐
        │     E2E      │  (10% of tests)
        │   Tests      │
        └──────────────┘
       ┌────────────────┐
       │  Integration   │  (30% of tests)
       │     Tests      │
       └────────────────┘
      ┌──────────────────┐
      │   Unit Tests     │  (60% of tests)
      │                  │
      └──────────────────┘
```

### 16.2 Unit Tests

**Scope:** Individual functions and classes

**Framework:** pytest

**Examples:**

```python
# test_request_validator.py
def test_validate_request_valid_input():
    """Test successful validation"""
    result = validate_request(
        transaction_id="test-123",
        origin="New York",
        destination="Boston"
    )
    assert result["status"] == "valid"
    assert result["origin"] == "New York"

def test_validate_request_empty_origin():
    """Test validation failure on empty origin"""
    with pytest.raises(ValidationError):
        validate_request(
            transaction_id="test-123",
            origin="",
            destination="Boston"
        )

# test_orchestrator.py
def test_enrich_waypoint_all_agents_success():
    """Test waypoint enrichment with all agents succeeding"""
    waypoint = create_mock_waypoint()
    result = orchestrator._enrich_single_waypoint("test-123", waypoint)

    assert result.enrichment is not None
    assert result.enrichment.selected_content is not None
    assert len(result.enrichment.all_agent_results) == 3

def test_enrich_waypoint_timeout_handling():
    """Test graceful handling of agent timeouts"""
    # Mock agents to timeout
    with patch('agents.youtube.process', side_effect=TimeoutError):
        waypoint = create_mock_waypoint()
        result = orchestrator._enrich_single_waypoint("test-123", waypoint)

        assert result.enrichment.all_agent_results['youtube'].status == "timeout"
```

**Coverage Goal:** 90%

---

### 16.3 Integration Tests

**Scope:** Module interactions and pipeline stages

**Examples:**

```python
# test_pipeline_integration.py
def test_full_pipeline_with_mocks():
    """Test complete pipeline with mocked external APIs"""
    with mock_google_maps_api(), mock_youtube_api(), mock_spotify_api():
        response = execute_pipeline(
            transaction_id="test-integration-1",
            origin="New York",
            destination="Boston"
        )

        assert response.route is not None
        assert len(response.route.waypoints) > 0
        assert all(wp.enrichment for wp in response.route.waypoints)

def test_orchestrator_agent_coordination():
    """Test orchestrator coordinates all agents correctly"""
    waypoints = [create_mock_waypoint() for _ in range(3)]
    results = orchestrator.enrich_route("test-123", waypoints)

    # Verify all waypoints processed
    assert len(results) == 3

    # Verify parallel execution (total time < sequential)
    assert orchestrator.total_time_ms < 3 * 8000  # 3 waypoints × 8s each
```

---

### 16.4 End-to-End Tests

**Scope:** Complete system with real external APIs (or staging APIs)

**Examples:**

```python
# test_e2e.py
@pytest.mark.e2e
def test_complete_route_enrichment():
    """Test complete flow from user request to response"""
    client = TestClient(app)

    response = client.post("/api/v1/route/enrich", json={
        "origin": "Empire State Building, NY",
        "destination": "Central Park, NY"
    })

    assert response.status_code == 200
    data = response.json()

    assert "transaction_id" in data
    assert data["route"]["summary"]["enriched_count"] > 0
    assert len(data["route"]["waypoints"]) > 0

    # Verify transaction ID in logs
    logs = read_logs()
    assert data["transaction_id"] in logs

@pytest.mark.e2e
def test_error_handling_no_route():
    """Test handling when no route exists"""
    client = TestClient(app)

    response = client.post("/api/v1/route/enrich", json={
        "origin": "New York",
        "destination": "London"  # No driving route
    })

    assert response.status_code == 404
    assert response.json()["error_code"] == "ROUTE_NOT_FOUND"
```

---

### 16.5 Performance Tests

**Scope:** Latency, throughput, concurrency

**Framework:** pytest-benchmark, locust

**Examples:**

```python
# test_performance.py
def test_waypoint_enrichment_latency(benchmark):
    """Benchmark single waypoint enrichment time"""
    waypoint = create_mock_waypoint()

    result = benchmark(
        orchestrator._enrich_single_waypoint,
        "test-123",
        waypoint
    )

    assert benchmark.stats.median < 8.0  # < 8 seconds

def test_concurrent_route_processing():
    """Test system under concurrent load"""
    routes = [
        ("NY", "Boston"),
        ("LA", "SF"),
        ("Chicago", "Detroit")
    ]

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(execute_pipeline, "test", orig, dest)
            for orig, dest in routes * 5  # 15 concurrent routes
        ]

        results = [f.result(timeout=60) for f in futures]

    assert all(r.route is not None for r in results)
```

**Load Testing (Locust):**

```python
# locustfile.py
from locust import HttpUser, task, between

class TourGuideUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def enrich_route(self):
        self.client.post("/api/v1/route/enrich", json={
            "origin": "New York, NY",
            "destination": "Boston, MA"
        })
```

**Run:** `locust --users 50 --spawn-rate 5`

---

### 16.6 Test Data Management

**Strategy:**
- Use fixture factories for consistent test data
- Mock external APIs by default
- Use VCR.py for recording/replaying API responses
- Separate test data from production config

```python
# conftest.py (pytest fixtures)
@pytest.fixture
def mock_waypoint():
    return Waypoint(
        id=1,
        location_name="Test Location",
        coordinates=Coordinates(lat=40.7, lng=-74.0),
        instruction="Test instruction",
        metadata=WaypointMetadata(...)
    )

@pytest.fixture
def mock_google_maps_api():
    with vcr.use_cassette('fixtures/google_maps_response.yaml'):
        yield
```

---

## 17. Deployment Considerations

### 17.1 Infrastructure Requirements

**Compute:**
- 2 vCPUs minimum
- 4 GB RAM
- SSD storage for logs

**Network:**
- Outbound HTTPS for external APIs
- Inbound HTTP/HTTPS for API endpoints

**Operating System:**
- Linux (Ubuntu 22.04 LTS recommended)
- Python 3.10+

---

### 17.2 Configuration Management

**Environment Variables:**

```bash
# API Keys
GOOGLE_MAPS_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here

# System Config
MAX_CONCURRENT_WAYPOINTS=5
MAX_AGENT_THREADS=50
AGENT_TIMEOUT_MS=5000
JUDGE_TIMEOUT_MS=3000

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/tour-guide/tour-guide.log
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=5
```

**Configuration File (`config.yaml`):**

```yaml
system:
  max_concurrent_waypoints: 5
  max_agent_threads: 50
  enable_caching: true
  cache_ttl_seconds: 3600

timeouts:
  agent_timeout_ms: 5000
  judge_timeout_ms: 3000
  route_retrieval_timeout_ms: 10000

logging:
  level: INFO
  file_path: ./logs/tour-guide.log
  max_size_mb: 100
  backup_count: 5
```

---

### 17.3 Deployment Steps

1. **Provision Server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python 3.10+
   sudo apt install python3.10 python3.10-venv
   ```

2. **Setup Application**
   ```bash
   # Create app directory
   mkdir -p /opt/tour-guide
   cd /opt/tour-guide

   # Create virtual environment
   python3.10 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Create .env file
   cp .env.example .env
   nano .env  # Edit with actual API keys
   ```

4. **Setup Logging**
   ```bash
   # Create log directory
   sudo mkdir -p /var/log/tour-guide
   sudo chown app-user:app-user /var/log/tour-guide
   ```

5. **Run Application**
   ```bash
   # Start server
   python main.py
   ```

---

### 17.4 Monitoring & Observability

**Metrics to Track:**

1. **Performance Metrics**
   - Request latency (p50, p95, p99)
   - Agent execution time
   - Waypoint enrichment success rate

2. **Resource Metrics**
   - CPU usage
   - Memory usage
   - Thread pool utilization
   - Disk I/O for logs

3. **Business Metrics**
   - Total routes processed
   - Content type distribution
   - Agent failure rates
   - API quota consumption

**Monitoring Tools:**
- Prometheus for metrics collection
- Grafana for dashboards
- Log aggregation with ELK stack (optional)

**Example Prometheus Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Request counter
route_requests_total = Counter(
    'route_requests_total',
    'Total route enrichment requests',
    ['status']
)

# Latency histogram
waypoint_processing_duration = Histogram(
    'waypoint_processing_duration_seconds',
    'Time spent processing waypoints',
    ['agent']
)

# Active threads gauge
active_agent_threads = Gauge(
    'active_agent_threads',
    'Number of active agent threads'
)
```

---

### 17.5 Security Considerations

1. **API Key Management**
   - Store keys in environment variables or secrets manager
   - Never commit keys to version control
   - Rotate keys periodically

2. **Input Validation**
   - Sanitize origin/destination inputs
   - Prevent injection attacks
   - Rate limit requests

3. **Network Security**
   - Use HTTPS for all external API calls
   - Implement request signing for API endpoints
   - Restrict outbound connections to required domains

4. **Logging Security**
   - Never log API keys or sensitive data
   - Sanitize user input in logs
   - Restrict log file access permissions

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Agent** | Autonomous component responsible for specific content retrieval (YouTube, Spotify, History, Judge) |
| **Enrichment** | Process of adding contextual content to waypoints |
| **Orchestrator** | Central coordinator managing agent execution and results |
| **Transaction ID** | Unique identifier tracking a request through the entire system |
| **Waypoint** | A point along the route requiring enrichment |
| **Pipeline** | Sequential flow of modules processing the request |
| **Thread Pool** | Managed collection of worker threads for concurrent execution |

---

## Appendix B: Architecture Diagrams

### B.1 System Context Diagram

```
┌──────────┐
│   User   │
└────┬─────┘
     │ Request
     ▼
┌─────────────────────────────────────┐
│  Multi-Agent Tour Guide System      │
│  - Request Processing               │
│  - Agent Orchestration              │
│  - Content Selection                │
└────┬────────────────────────────────┘
     │
     ├──► Google Maps API
     ├──► YouTube API
     ├──► Spotify API
     └──► Wikipedia API
```

### B.2 Module Dependency Diagram

```
Request Validator
     │
     ▼
Route Retrieval ──► Google Maps API
     │
     ▼
Waypoint Preprocessor
     │
     ▼
Orchestrator ──┬──► YouTube Agent ──► YouTube API
               ├──► Spotify Agent ──► Spotify API
               ├──► History Agent ──► Wikipedia API
               └──► Judge Agent
     │
     ▼
Result Aggregator
     │
     ▼
Response Formatter
```

---

## Appendix C: Sample Code Snippets

### C.1 Main Pipeline Entry Point

```python
def main():
    """Main entry point for tour guide system"""
    # Setup logging
    logger = setup_logging(config)

    # Initialize orchestrator
    orchestrator = Orchestrator(config)

    # Process request
    try:
        # Module 1: Validate
        validated = validate_request(
            transaction_id=create_transaction_id(),
            origin=user_input["origin"],
            destination=user_input["destination"]
        )

        # Module 2: Retrieve Route
        route = retrieve_route(validated)

        # Module 3: Preprocess Waypoints
        processed = preprocess_waypoints(route)

        # Module 4: Orchestrate Enrichment
        enriched = orchestrator.enrich_route(
            validated["transaction_id"],
            processed["waypoints"]
        )

        # Module 5: Aggregate Results
        final = aggregate_results(enriched)

        # Module 6: Format Response
        response = format_response(final)

        return response

    except Exception as e:
        logger.critical("Pipeline failed", exc_info=True)
        raise
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-30 | System Architect | Initial RPD creation |

---

**END OF RPD**
