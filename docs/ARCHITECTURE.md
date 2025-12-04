# Architecture Documentation
## Multi-Agent AI Tour Guide System

**Version:** 1.0
**Last Updated:** December 4, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Principles](#architectural-principles)
3. [C4 Model](#c4-model)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Concurrency Model](#concurrency-model)
7. [Technology Stack](#technology-stack)
8. [Design Patterns](#design-patterns)
9. [Architecture Decision Records](#architecture-decision-records)
10. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The Multi-Agent AI Tour Guide System is a distributed, asynchronous platform that enriches navigation waypoints with contextually relevant multimedia content through coordinated AI agent execution.

### Key Characteristics

- **Architecture Style**: Modular Pipeline with Event-Driven Agent Coordination
- **Concurrency Model**: Multithreading (I/O-bound operations)
- **Agent Coordination**: Orchestrator Pattern
- **Data Flow**: Unidirectional pipeline with parallel agent execution
- **Observability**: Structured logging with distributed tracing via Transaction IDs

---

## Architectural Principles

### 1. Modularity
Each pipeline stage is an independent, testable unit with well-defined input/output contracts.

### 2. Observability First
All operations emit structured logs with transaction IDs for complete traceability.

### 3. Fault Tolerance
Graceful degradation ensures system functionality even when individual agents fail.

### 4. Scalability
Thread pool management and batch processing enable handling of large routes.

### 5. Extensibility
Plugin-based agent architecture allows adding new content sources without core changes.

---

## C4 Model

### Level 1: System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                    End User / Application                     │
│                                                               │
└────────────────────────┬──────────────────────────────────┘
                         │ Route Request (origin, destination)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│          Multi-Agent AI Tour Guide System                     │
│          Enriches routes with multimedia content              │
│                                                               │
└────┬──────────┬──────────┬──────────┬──────────────────────┘
     │          │          │          │
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Google  │ │ YouTube  │ │  Spotify │ │Wikipedia │
│  Maps   │ │   API    │ │   API    │ │   API    │
│   API   │ │          │ │          │ │          │
└─────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Level 2: Container Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                     Tour Guide Application                      │
├───────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            Pipeline Orchestrator (Python)                 │ │
│  │  - Request validation                                     │ │
│  │  - Route retrieval                                        │ │
│  │  - Waypoint preprocessing                                 │ │
│  │  - Agent orchestration                                    │ │
│  │  - Result aggregation                                     │ │
│  │  - Response formatting                                    │ │
│  └──────────────┬────────────────────────────────────────────┘ │
│                 │                                               │
│  ┌──────────────▼────────────────────────────────────────────┐ │
│  │            Agent Execution Layer (ThreadPool)             │ │
│  ├──────────────┬──────────────┬──────────────┬──────────────┤ │
│  │   YouTube    │   Spotify    │   History    │    Judge     │ │
│  │    Agent     │    Agent     │    Agent     │    Agent     │ │
│  │  (Thread 1)  │  (Thread 2)  │  (Thread 3)  │  (Thread 4)  │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Logging & Monitoring Layer                   │ │
│  │  - Structured logging (JSON)                              │ │
│  │  - Transaction ID propagation                             │ │
│  │  - Performance metrics                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### Level 3: Component Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                       src/ Package                              │
├───────────────────────────────────────────────────────────────┤
│                                                                 │
│  models.py                                                      │
│  ├─ TransactionContext: Request tracking                       │
│  ├─ Waypoint: Location data structure                          │
│  ├─ AgentResult: Standardized agent output                     │
│  ├─ ContentItem: Polymorphic content                           │
│  └─ JudgeDecision: Selection result                            │
│                                                                 │
│  pipeline.py                                                    │
│  └─ execute_pipeline(): Main orchestration function            │
│                                                                 │
│  config.py                                                      │
│  └─ SystemConfig: Centralized configuration                    │
│                                                                 │
│  modules/                                                       │
│  ├─ request_validator.py: Input validation (Module 1)          │
│  ├─ route_retrieval.py: Google Maps integration (Module 2)     │
│  ├─ waypoint_preprocessor.py: Metadata enrichment (Module 3)   │
│  ├─ orchestrator.py: Agent coordination (Module 4)             │
│  ├─ mock_agents.py: Agent implementations                      │
│  ├─ result_aggregator.py: Result assembly (Module 5)           │
│  └─ response_formatter.py: Output formatting (Module 6)        │
│                                                                 │
│  google_maps/                                                   │
│  └─ client.py: Google Maps API wrapper                         │
│                                                                 │
│  agents/                                                        │
│  └─ youtube_client.py: YouTube API wrapper                     │
│                                                                 │
│  logging_config.py                                              │
│  └─ Structured logger configuration                            │
│                                                                 │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Module 1: Request Validator

**Responsibility**: Validate user input and initialize request tracking

**Input Contract**:
```python
{
    "origin": str,
    "destination": str,
    "preferences": Dict[str, Any] (optional)
}
```

**Output Contract**:
```python
TransactionContext(
    transaction_id: str,
    origin: str,
    destination: str,
    user_preferences: Dict[str, Any]
)
```

**Error Handling**: Raises `ValidationError` for invalid inputs

---

### Module 2: Route Retrieval

**Responsibility**: Fetch route data from Google Maps Directions API

**Dependencies**: Google Maps API, google_maps.client

**Input Contract**: TransactionContext

**Output Contract**:
```python
RouteData(
    distance: str,
    duration: str,
    waypoints: List[Waypoint],
    steps: List[Dict[str, Any]]
)
```

**Error Handling**: Raises `RouteRetrievalError` for API failures

---

### Module 3: Waypoint Preprocessor

**Responsibility**: Enrich waypoints with metadata and generate agent queries

**Processing Steps**:
1. Classify location type (intersection, landmark, highway, etc.)
2. Extract nearby landmarks
3. Identify neighborhood
4. Generate search queries for each agent type

**Input Contract**: TransactionContext, RouteData

**Output Contract**: `List[Waypoint]` with metadata and agent_context populated

---

### Module 4: Orchestrator

**Responsibility**: Coordinate parallel agent execution

**Architecture**: Thread pool executor with configurable concurrency

**Processing Flow**:
```
For each waypoint:
    1. Launch YouTube, Spotify, History agents in parallel threads
    2. Wait for results with timeout (5 seconds)
    3. Invoke Judge agent with collected results
    4. Assemble WaypointEnrichment
    5. Log completion metrics
```

**Concurrency Control**:
- Max threads: Configurable (default: 50)
- Batch size: Configurable (default: 5 waypoints/batch)
- Timeout enforcement: Per-agent timeouts with fallback

---

### Module 5: Result Aggregator

**Responsibility**: Assemble final route with statistics

**Calculations**:
- Total/enriched/failed waypoint counts
- Average processing time
- Content type breakdown
- Success rate percentage

**Input Contract**: TransactionContext, List[Waypoint], route_metadata

**Output Contract**: FinalRoute with complete enrichment data

---

### Module 6: Response Formatter

**Responsibility**: Format output for user consumption

**Output Format**: JSON-serializable dictionary

**Structure**:
```json
{
    "transaction_id": "TXID-...",
    "route": {
        "distance": "...",
        "duration": "...",
        "waypoints": [...]
    },
    "statistics": {...},
    "timestamp": "..."
}
```

---

## Data Flow

### Sequential Pipeline Flow

```
User Request
    │
    ▼
[1] Request Validator
    │ (generates TXID)
    ▼
[2] Route Retrieval
    │ (Google Maps API)
    ▼
[3] Waypoint Preprocessor
    │ (metadata enrichment)
    ▼
[4] Orchestrator
    │ ┌──────────────────────────┐
    │ │  Parallel Agent Layer    │
    │ │  ┌────────┐ ┌──────────┐ │
    │ │  │YouTube │ │ Spotify  │ │
    │ │  │ Agent  │ │  Agent   │ │
    │ │  └────┬───┘ └────┬─────┘ │
    │ │       │          │        │
    │ │  ┌────▼──────────▼─────┐ │
    │ │  │   History Agent     │ │
    │ │  └──────────┬──────────┘ │
    │ │             │             │
    │ │  ┌──────────▼──────────┐ │
    │ │  │    Judge Agent      │ │
    │ │  └─────────────────────┘ │
    │ └──────────────────────────┘
    ▼
[5] Result Aggregator
    │
    ▼
[6] Response Formatter
    │
    ▼
User Response
```

### Transaction ID Propagation

Every module receives and forwards the Transaction ID:

```
TXID-20251203T143052-uuid
    │
    ├─> Validation logs
    ├─> Route retrieval logs
    ├─> Preprocessing logs
    ├─> Agent execution logs (all 4 agents)
    ├─> Aggregation logs
    └─> Final response
```

---

## Concurrency Model

### Multithreading for I/O-Bound Operations

**Rationale**: All agent operations are I/O-bound (API calls), making multithreading optimal.

**Thread Pool Configuration**:
```python
ThreadPoolExecutor(max_workers=50)
```

**Thread Safety Measures**:
1. TransactionContext uses threading.Lock for metadata updates
2. Logger is thread-safe by design
3. Agent results collected synchronously after parallel execution

**Batch Processing**:
```python
# Process 5 waypoints concurrently
batch_size = 5
batches = [waypoints[i:i+5] for i in range(0, len(waypoints), 5)]
```

### Why Not Multiprocessing?

1. Operations are I/O-bound, not CPU-bound
2. ThreadPool has lower overhead than ProcessPool
3. No GIL contention (waiting on network I/O)
4. Simpler state sharing between threads

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.9+ | Main programming language |
| Concurrency | ThreadPoolExecutor | stdlib | Parallel agent execution |
| HTTP Client | Requests | 2.31+ | API communication |
| Configuration | python-dotenv | 1.0+ | Environment management |
| Testing | PyTest | 7.0+ | Unit/integration testing |
| Logging | Structlog | 24.0+ | Structured logging |
| Data Validation | Dataclasses | stdlib | Type-safe models |

### External APIs

| Service | Purpose | Rate Limits |
|---------|---------|-------------|
| Google Maps Directions API | Route retrieval | Configurable per key |
| YouTube Data API v3 | Video content search | 10,000 requests/day |
| Spotify Web API | Music content search | 1 request/second |
| Wikipedia API | Historical content | No hard limit |

---

## Design Patterns

### 1. Pipeline Pattern
Sequential stages with clear input/output contracts

### 2. Orchestrator Pattern
Central coordinator for distributed agent execution

### 3. Repository Pattern
Abstraction layer for external API access (Google Maps, YouTube clients)

### 4. Factory Pattern
Agent result creation (timeout_result, error_result, fallback_content)

### 5. Strategy Pattern
Judge agent selection logic (extensible decision criteria)

### 6. Observer Pattern
Structured logging at each pipeline stage

---

## Architecture Decision Records

### ADR-001: Pipeline Architecture

**Status**: Accepted
**Date**: 2025-11-30

**Context**: Need clear data flow and module boundaries

**Decision**: Implement sequential pipeline with 6 discrete stages

**Consequences**:
- **Positive**: Clear separation of concerns, easy to test
- **Negative**: No backward data flow (requires careful planning)

---

### ADR-002: Multithreading vs Multiprocessing

**Status**: Accepted
**Date**: 2025-11-30

**Context**: Agent operations are I/O-bound (API calls)

**Decision**: Use ThreadPoolExecutor, not ProcessPoolExecutor

**Rationale**:
- I/O-bound workload (network API calls)
- Lower overhead than multiprocessing
- Easier state sharing
- No GIL contention during I/O wait

**Consequences**:
- **Positive**: Optimal performance for I/O workload, simpler code
- **Negative**: Would not scale for CPU-bound operations

---

### ADR-003: Mock Mode for Development

**Status**: Accepted
**Date**: 2025-11-30

**Context**: Development requires fast iteration without API costs

**Decision**: Implement mock mode with simulated agent responses

**Consequences**:
- **Positive**: Fast development, no API costs during testing
- **Negative**: Requires maintenance of mock implementations

---

## Deployment Architecture

### Production Deployment

```
┌─────────────────────────────────────────┐
│         Application Server              │
│  ┌───────────────────────────────────┐  │
│  │   Tour Guide Application          │  │
│  │   (Python 3.9+ Runtime)           │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│  ┌───────────────▼───────────────────┐  │
│  │   Environment Configuration       │  │
│  │   - .env file                     │  │
│  │   - API keys (secrets)            │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌───────────────────────────────────┐  │
│  │   Logging                         │  │
│  │   - ./logs/tour-guide.log         │  │
│  │   - Rotation: 100MB, 5 backups    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
            │
            │ HTTPS
            ▼
┌─────────────────────────────────────────┐
│      External API Services              │
│  - Google Maps Directions API           │
│  - YouTube Data API v3                  │
│  - Spotify Web API                      │
│  - Wikipedia API                        │
└─────────────────────────────────────────┘
```

### Scalability Considerations

1. **Horizontal Scaling**: Stateless design allows multiple instances
2. **Rate Limiting**: Configurable per-agent timeouts
3. **Circuit Breaker**: Agent timeout with fallback content
4. **Caching**: Optional result caching (configurable TTL)

---

## Security Architecture

### API Key Management

```
.env file (gitignored)
    ├─ GOOGLE_MAPS_API_KEY
    ├─ YOUTUBE_API_KEY
    ├─ SPOTIFY_CLIENT_ID
    └─ SPOTIFY_CLIENT_SECRET
```

### Best Practices

1. **Never commit** `.env` to version control
2. **Rotate keys** periodically
3. **Use environment-specific** keys (dev/staging/prod)
4. **Monitor usage** to detect anomalies

---

## Performance Characteristics

### Typical Route Processing

| Metric | Value |
|--------|-------|
| Waypoints | 10 |
| Total Time | < 30 seconds |
| Per-Waypoint | ~2-3 seconds |
| Agent Parallelism | 3x speedup |
| Memory Usage | < 100 MB |
| API Calls | 1 Maps + 30 Agent (3 per waypoint) |

### Bottlenecks

1. **Google Maps API**: Sequential (cannot parallelize)
2. **Agent Timeouts**: 5 seconds worst-case per waypoint
3. **Network Latency**: Variable based on API response times

---

## Future Architecture Enhancements

### Planned Improvements

1. **Result Caching**: Redis-based caching for repeated queries
2. **Async/Await**: Migrate to asyncio for better I/O performance
3. **Message Queue**: Decouple agent execution with RabbitMQ/Redis
4. **Microservices**: Split agents into independent services
5. **GraphQL API**: Replace REST with GraphQL for flexible queries

---

**Document Owner**: Architecture Team
**Review Cycle**: Quarterly
**Next Review**: March 2026
