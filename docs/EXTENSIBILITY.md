# Extensibility & Plugin Architecture
## Multi-Agent AI Tour Guide System

**Version:** 1.0
**Last Updated**: December 3, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Plugin Architecture](#plugin-architecture)
3. [Adding New Agents](#adding-new-agents)
4. [Adding New Modules](#adding-new-modules)
5. [Adding API Integrations](#adding-api-integrations)
6. [Configuration Extensions](#configuration-extensions)
7. [Customization Points](#customization-points)
8. [Extension Examples](#extension-examples)

---

## Overview

The Multi-Agent AI Tour Guide System is designed for extensibility through:
- **Plugin-based agent architecture**
- **Modular pipeline design**
- **Configurable decision criteria**
- **Abstracted API clients**
- **Event-driven logging**

This document provides comprehensive guidance for extending the system.

---

## Plugin Architecture

### Agent Plugin System

New content agents can be added without modifying core orchestration logic.

**Extension Points**:
1. Agent implementation (Claude Code agent.md file)
2. Agent registration (orchestrator configuration)
3. Result aggregation (standardized AgentResult format)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Core Orchestrator                     │
│                  (Unchanged)                             │
└──────────────┬──────────────┬─────────────┬─────────────┘
               │              │             │
               ▼              ▼             ▼
         ┌─────────┐    ┌─────────┐   ┌─────────┐
         │YouTube  │    │ Spotify │   │ History │
         │ Agent   │    │  Agent  │   │  Agent  │
         │(Built-in)    │(Built-in)   │(Built-in)
         └─────────┘    └─────────┘   └─────────┘

         New Agents (Pluggable):

         ┌─────────┐    ┌─────────┐   ┌─────────┐
         │Weather  │    │  Food   │   │  Art    │
         │ Agent   │    │  Agent  │   │ Agent   │
         │(Plugin) │    │(Plugin) │   │(Plugin) │
         └─────────┘    └─────────┘   └─────────┘
```

---

## Adding New Agents

### Step 1: Create Agent Definition

Create `.claude/agents/{agent-name}.md`:

```markdown
# {Agent Name}

## Purpose
{One sentence description}

## Input Contract
- transaction_id: string
- waypoint_id: integer
- location_name: string
- coordinates: {lat: float, lng: float}
- search_query: string

## Output Contract
Return JSON:
{
  "agent_name": "{agent-name}",
  "transaction_id": "{transaction_id}",
  "waypoint_id": {waypoint_id},
  "status": "success|timeout|error",
  "content": {
    "type": "{content_type}",
    "title": "...",
    "description": "...",
    "relevance_score": 0.0-1.0,
    "url": "...",
    "metadata": {...}
  },
  "error_message": null,
  "execution_time_ms": 0
}

## Agent Implementation

{Your implementation logic}
```

### Step 2: Register Agent in Orchestrator

Modify `src/modules/orchestrator.py`:

```python
def _enrich_single_waypoint(self, context, waypoint):
    # Add new agent to parallel execution
    agent_futures = {
        'youtube': self.thread_pool.submit(...),
        'spotify': self.thread_pool.submit(...),
        'history': self.thread_pool.submit(...),
        'weather': self.thread_pool.submit(  # NEW AGENT
            self._run_weather_agent,
            context.transaction_id,
            waypoint
        )
    }
    # ... rest of logic unchanged
```

### Step 3: Implement Agent Runner Method

```python
def _run_weather_agent(
    self,
    transaction_id: str,
    waypoint: Waypoint
) -> AgentResult:
    """
    Execute Weather agent for waypoint

    Args:
        transaction_id: Transaction ID
        waypoint: Waypoint to process

    Returns:
        AgentResult with weather content
    """
    start_time = time.time()

    # Invoke Claude Code agent via Task tool
    # OR implement direct API integration

    # Return standardized AgentResult
    return AgentResult(
        agent_name="weather",
        transaction_id=transaction_id,
        waypoint_id=waypoint.id,
        status=AgentStatus.SUCCESS,
        content=content_item,
        execution_time_ms=execution_time_ms
    )
```

### Step 4: Update Judge Agent

Update Judge decision criteria to include new agent type:

```python
def _evaluate_content(self, agent_results):
    scores = {
        'youtube': self._score_video(agent_results['youtube']),
        'spotify': self._score_music(agent_results['spotify']),
        'history': self._score_history(agent_results['history']),
        'weather': self._score_weather(agent_results['weather'])  # NEW
    }
    return self._select_winner(scores)
```

---

## Adding New Modules

### Pipeline Module Extension

To add a new processing stage to the pipeline:

#### Step 1: Create Module File

`src/modules/sentiment_analyzer.py`:

```python
"""
Module 7: Sentiment Analyzer
Analyzes user preferences and adjusts content selection
"""

from src.models import TransactionContext, Waypoint
from src.logging_config import get_logger

logger = get_logger()

def analyze_user_sentiment(
    context: TransactionContext,
    waypoints: List[Waypoint]
) -> Dict[str, Any]:
    """
    Analyze user sentiment from preferences

    Input Contract:
        - TransactionContext with user_preferences
        - List of enriched Waypoints

    Output Contract:
        - Sentiment scores per waypoint
        - Adjustment recommendations
    """
    context.log_stage_entry("sentiment_analysis")

    logger.log_stage_entry(
        "sentiment_analysis",
        context.transaction_id
    )

    # Your analysis logic here

    logger.log_stage_exit(
        "sentiment_analysis",
        context.transaction_id,
        duration_ms=execution_time
    )

    return sentiment_data
```

#### Step 2: Integrate into Pipeline

Modify `src/pipeline.py`:

```python
def execute_pipeline(origin, destination, preferences):
    # ... existing modules 1-4 ...

    # New Module 7: Sentiment Analysis
    sentiment_data = analyze_user_sentiment(context, enriched_waypoints)
    context.add_metadata("sentiment", sentiment_data)

    # ... existing modules 5-6 ...
```

#### Step 3: Add Tests

Create `tests/test_sentiment_analyzer.py`:

```python
@pytest.mark.unit
class TestSentimentAnalyzer:
    def test_sentiment_analysis(self, transaction_context, sample_waypoints):
        result = analyze_user_sentiment(transaction_context, sample_waypoints)
        assert result is not None
        # ... assertions ...
```

---

## Adding API Integrations

### Creating New API Client

#### Step 1: Create Client Module

`src/apis/weather_client.py`:

```python
"""
Weather API Client
Integrates with OpenWeatherMap API
"""

import requests
from typing import Dict, Optional
from src.config import get_config

class WeatherClient:
    """
    Client for OpenWeatherMap API
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.weather_api_key

    def get_weather(
        self,
        lat: float,
        lng: float
    ) -> Optional[Dict]:
        """
        Get current weather for coordinates

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Weather data dictionary

        Raises:
            WeatherAPIError: If API call fails
        """
        url = f"{self.BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Weather API error: {str(e)}")


class WeatherAPIError(Exception):
    """Weather API error"""
    pass
```

#### Step 2: Add Configuration

Modify `src/config.py`:

```python
@dataclass
class SystemConfig:
    # ... existing fields ...
    weather_api_key: str = ""

    @classmethod
    def from_env(cls):
        return cls(
            # ... existing fields ...
            weather_api_key=os.getenv("WEATHER_API_KEY", "")
        )
```

#### Step 3: Add to `.env.example`

```bash
# Weather API
WEATHER_API_KEY=your_weather_api_key_here
```

---

## Configuration Extensions

### Adding New Configuration Parameters

#### Step 1: Extend SystemConfig

```python
@dataclass
class SystemConfig:
    # New parameters
    enable_caching: bool = True
    cache_backend: str = "redis"  # "redis" | "memory" | "file"
    cache_ttl_seconds: int = 3600

    # Agent-specific settings
    youtube_max_results: int = 5
    spotify_search_limit: int = 10

    def validate(self) -> list[str]:
        errors = []

        # Validate new parameters
        if self.cache_backend not in ["redis", "memory", "file"]:
            errors.append("Invalid cache_backend")

        if self.cache_ttl_seconds <= 0:
            errors.append("cache_ttl_seconds must be positive")

        return errors
```

#### Step 2: Environment Variables

Add to `.env`:

```bash
# Caching
ENABLE_CACHING=true
CACHE_BACKEND=redis
CACHE_TTL_SECONDS=3600

# Agent Settings
YOUTUBE_MAX_RESULTS=5
SPOTIFY_SEARCH_LIMIT=10
```

---

## Customization Points

### 1. Decision Criteria

Customize Judge agent scoring:

```python
# src/modules/judge_scorer.py

class JudgeScorer:
    """Customizable scoring logic for Judge agent"""

    def __init__(self, weights: Dict[str, float]):
        self.weights = weights

    def score_content(
        self,
        content: ContentItem,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate weighted score for content

        Weights:
            - relevance: 0.4 (content match to location)
            - quality: 0.3 (views, ratings, source authority)
            - diversity: 0.2 (avoid repetition)
            - freshness: 0.1 (recent content preferred)
        """
        scores = {
            'relevance': self._score_relevance(content, context),
            'quality': self._score_quality(content),
            'diversity': self._score_diversity(content, context),
            'freshness': self._score_freshness(content)
        }

        weighted_score = sum(
            scores[criterion] * self.weights.get(criterion, 0.0)
            for criterion in scores
        )

        return weighted_score
```

Usage:

```python
# Custom weights for specific use case
scorer = JudgeScorer(weights={
    'relevance': 0.5,  # Prioritize relevance
    'quality': 0.3,
    'diversity': 0.15,
    'freshness': 0.05
})
```

### 2. Query Templates

Customize agent search queries:

```python
# src/modules/query_builder.py

class QueryBuilder:
    """Build optimized search queries for agents"""

    YOUTUBE_TEMPLATES = [
        "{location} tour guide",
        "{location} travel vlog",
        "visit {location} video"
    ]

    MUSIC_TEMPLATES = [
        "songs about {location}",
        "{location} music",
        "{location} anthem"
    ]

    @classmethod
    def build_youtube_query(cls, waypoint: Waypoint) -> str:
        """Build YouTube search query"""
        template = random.choice(cls.YOUTUBE_TEMPLATES)
        return template.format(location=waypoint.location_name)
```

### 3. Logging Format

Customize structured logging output:

```python
# src/logging_config.py

def configure_custom_logger():
    """Configure logger with custom format"""

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            CustomProcessor(),  # Add your processor
            structlog.processors.JSONRenderer()
        ],
        # ... rest of config ...
    )


class CustomProcessor:
    """Custom log processor"""

    def __call__(self, logger, method_name, event_dict):
        # Add custom fields
        event_dict["environment"] = os.getenv("ENV", "development")
        event_dict["version"] = "1.0.0"
        return event_dict
```

---

## Extension Examples

### Example 1: Weather Agent

**Purpose**: Provide weather information for waypoints

**Files to Create**:
1. `.claude/agents/weather-forecast.md`
2. `src/apis/weather_client.py`
3. `tests/test_weather_agent.py`

**Implementation**:
```python
# In orchestrator.py
def _run_weather_agent(self, transaction_id, waypoint):
    client = WeatherClient()
    weather_data = client.get_weather(
        waypoint.coordinates.lat,
        waypoint.coordinates.lng
    )

    content = ContentItem(
        content_type=ContentType.WEATHER,
        title=f"Weather at {waypoint.location_name}",
        description=f"{weather_data['description']}, {weather_data['temp']}°C",
        relevance_score=1.0,  # Always relevant
        metadata=weather_data
    )

    return AgentResult(
        agent_name="weather",
        transaction_id=transaction_id,
        waypoint_id=waypoint.id,
        status=AgentStatus.SUCCESS,
        content=content
    )
```

### Example 2: Food Recommendations Agent

**Purpose**: Suggest restaurants and cuisine at waypoints

**Agent Definition**: `.claude/agents/food-recommender.md`

```markdown
# Food Recommender Agent

Search for highly-rated restaurants near waypoint coordinates.

Use Google Places API or Yelp API to find:
1. Top-rated restaurants within 500m radius
2. Cuisine type
3. Price range
4. Current open/closed status

Return top recommendation with:
- Restaurant name
- Cuisine
- Rating
- Distance from waypoint
- URL (Google Maps/Yelp link)
```

### Example 3: Traffic Alert Agent

**Purpose**: Warn about traffic conditions ahead

**Integration Points**:
1. Google Maps Traffic Layer API
2. Waze real-time data
3. Local traffic APIs

**Output Format**:
```json
{
  "agent_name": "traffic",
  "content": {
    "type": "alert",
    "title": "Heavy Traffic Ahead",
    "description": "15-minute delay expected on Highway 101",
    "severity": "moderate",
    "alternatives": ["Take Route 280 instead"]
  }
}
```

---

## Best Practices for Extensions

### 1. Maintain Contracts

Always adhere to standardized input/output contracts:

```python
# Input: TransactionContext + Waypoint
# Output: AgentResult

def new_agent_function(
    transaction_id: str,
    waypoint: Waypoint
) -> AgentResult:
    # Implementation
    pass
```

### 2. Error Handling

Implement graceful degradation:

```python
try:
    result = api_call()
except TimeoutError:
    return create_timeout_result(agent_name, transaction_id, waypoint_id, timeout_ms)
except Exception as e:
    return create_error_result(agent_name, transaction_id, waypoint_id, e)
```

### 3. Logging

Log all operations with transaction ID:

```python
logger.log_agent_start(agent_name, transaction_id, waypoint_id)
# ... operation ...
logger.log_agent_completion(agent_name, transaction_id, waypoint_id, status)
```

### 4. Testing

Write comprehensive tests for extensions:

```python
@pytest.mark.unit
def test_new_agent_success(mock_config, sample_waypoint):
    result = new_agent_function("TXID-test", sample_waypoint)
    assert result.status == AgentStatus.SUCCESS
    assert result.content is not None
```

### 5. Documentation

Document all extensions:
- Update ARCHITECTURE.md with new components
- Add ADR (Architecture Decision Record) for significant changes
- Include usage examples in docstrings

---

## Conclusion

The Multi-Agent AI Tour Guide System provides multiple extension points:
1. **Agent Plugins**: Add new content sources
2. **Pipeline Modules**: Add processing stages
3. **API Integrations**: Connect to new services
4. **Configuration**: Customize behavior
5. **Decision Logic**: Adjust selection criteria

All extensions follow standardized contracts ensuring seamless integration without core modifications.

---

**Document Owner**: Engineering Team
**Review Cycle**: Quarterly
**Next Review**: March 2026
