# Agent Creation Guide
## Multi-Agent AI Tour Guide System

**Status:** 📍 **YOU ARE HERE** - Ready for Agent Creation

---

## Current Progress

✅ **Phase 1: Complete** - All infrastructure is built and tested
- Core data structures defined
- All 6 pipeline modules implemented
- Structured logging with transaction IDs working
- Mock agents successfully tested end-to-end

📍 **Phase 2: Ready** - Waiting for real agent creation

❌ **Phase 3: Pending** - Will integrate agents after creation

---

## System Architecture Summary

The system currently has **mock implementations** for 4 agents in the Orchestrator module (`src/modules/orchestrator.py`):

1. **YouTube Agent** - Finds relevant videos for waypoints
2. **Spotify Agent** - Finds relevant music for waypoints
3. **History Agent** - Retrieves historical facts about waypoints
4. **Judge Agent** - Evaluates and selects the best content

Each mock agent currently:
- Simulates API call delays
- Returns hardcoded test data
- Properly logs all operations
- Follows the `AgentResult` interface

---

## When to Create Agents

### 🎯 **CREATE AGENTS NOW**

You are at the perfect point to create the real agents. The infrastructure is ready:
- ✅ Data structures defined (`AgentResult`, `ContentItem`, etc.)
- ✅ Orchestrator manages threading and timeouts
- ✅ Logging captures all agent operations
- ✅ Error handling gracefully manages failures

Once you create the agents, I will integrate them into the system by replacing the mock implementations in:
- `src/modules/orchestrator.py:_run_youtube_agent()`
- `src/modules/orchestrator.py:_run_spotify_agent()`
- `src/modules/orchestrator.py:_run_history_agent()`
- `src/modules/orchestrator.py:_run_judge()`

---

## Agent Specifications

Below are the detailed specifications for each agent. Create them in your interface using these specs.

---

### 1. YouTube Agent

**Agent Name:** `YouTubeContentAgent`

**Description:**
Find contextually relevant YouTube videos for locations along a route. Search for videos that showcase the location, provide virtual tours, or explain the historical/cultural significance.

**Input Parameters:**
- `transaction_id` (string): Transaction ID for tracing
- `waypoint_id` (integer): ID of the waypoint being processed
- `location_name` (string): Name of the location (e.g., "5th Avenue & E 34th St")
- `search_query` (string): Pre-built YouTube search query (e.g., "5th Avenue 34th Street New York tour video")
- `coordinates` (object): `{lat: float, lng: float}` - Geographic coordinates

**Expected Output Format:**
```json
{
  "agent_name": "youtube",
  "transaction_id": "<same as input>",
  "waypoint_id": <same as input>,
  "status": "success|timeout|error",
  "content": {
    "content_type": "video",
    "title": "Video Title Here",
    "description": "Video description...",
    "url": "https://youtube.com/watch?v=...",
    "relevance_score": 0.85,
    "metadata": {
      "channel": "Channel Name",
      "view_count": 123456,
      "duration": "10:30"
    }
  },
  "error_message": null,
  "execution_time_ms": 2500
}
```

**Processing Logic:**
1. Use the provided `search_query` to search YouTube Data API
2. Filter results for videos (not channels/playlists)
3. Rank by relevance, view count, and recency
4. Select the best video
5. Calculate relevance score (0.0 to 1.0) based on:
   - Title/description match with location name
   - View count and engagement
   - Video quality indicators

**Timeout:** 5000ms (enforced by orchestrator)

**Error Handling:**
- If API quota exceeded: Return `status: "error"` with appropriate message
- If no results found: Return low relevance score or error
- If network timeout: Let orchestrator handle timeout

**Skills Needed:**
- YouTube Data API integration
- Search query formulation
- Result ranking and scoring
- JSON output formatting

**Color/Theme:** 🔴 Red (YouTube brand color)

---

### 2. Spotify Agent

**Agent Name:** `SpotifyContentAgent`

**Description:**
Find contextually relevant music or audio content for locations along a route. Search for songs that match the mood, genre, or cultural context of the location.

**Input Parameters:**
- `transaction_id` (string): Transaction ID for tracing
- `waypoint_id` (integer): ID of the waypoint being processed
- `location_name` (string): Name of the location
- `search_query` (string): Pre-built Spotify search query (e.g., "New York City Manhattan urban")
- `coordinates` (object): `{lat: float, lng: float}` - Geographic coordinates

**Expected Output Format:**
```json
{
  "agent_name": "spotify",
  "transaction_id": "<same as input>",
  "waypoint_id": <same as input>,
  "status": "success|timeout|error",
  "content": {
    "content_type": "song",
    "title": "Song Title",
    "description": "Artist Name - Album Name",
    "url": "https://open.spotify.com/track/...",
    "relevance_score": 0.90,
    "metadata": {
      "artist": "Artist Name",
      "album": "Album Name",
      "popularity": 85,
      "preview_url": "https://..."
    }
  },
  "error_message": null,
  "execution_time_ms": 1800
}
```

**Processing Logic:**
1. Use Spotify Web API with provided `search_query`
2. Search for tracks matching the location context
3. Consider:
   - Location name matches in song title/lyrics
   - Genre appropriateness (e.g., jazz for historic neighborhoods)
   - Artist origin/connection to location
4. Rank by popularity and relevance
5. Calculate relevance score based on contextual match

**Timeout:** 5000ms

**Error Handling:**
- If authentication fails: Return error status
- If no matching songs: Return lower relevance score or generic result
- Handle rate limiting gracefully

**Skills Needed:**
- Spotify Web API integration
- Client credentials flow authentication
- Music search and recommendation
- Genre/mood mapping

**Color/Theme:** 🟢 Green (Spotify brand color)

---

### 3. History Agent

**Agent Name:** `HistoryContentAgent`

**Description:**
Retrieve historical facts, stories, or trivia about locations along the route. Use Wikipedia, historical databases, or LLM knowledge to provide interesting context.

**Input Parameters:**
- `transaction_id` (string): Transaction ID for tracing
- `waypoint_id` (integer): ID of the waypoint being processed
- `location_name` (string): Name of the location
- `search_query` (string): Pre-built history query (e.g., "5th Avenue 34th Street history Manhattan")
- `coordinates` (object): `{lat: float, lng: float}` - Geographic coordinates

**Expected Output Format:**
```json
{
  "agent_name": "history",
  "transaction_id": "<same as input>",
  "waypoint_id": <same as input>,
  "status": "success|timeout|error",
  "content": {
    "content_type": "history",
    "title": "Historical Fact Title",
    "description": "Detailed historical narrative about the location, including key dates, events, and significance. Should be 2-4 sentences.",
    "url": null,
    "relevance_score": 0.75,
    "metadata": {
      "source": "Wikipedia",
      "time_period": "1920s-1930s",
      "category": "architecture"
    }
  },
  "error_message": null,
  "execution_time_ms": 1200
}
```

**Processing Logic:**
1. Search Wikipedia API for location
2. Extract relevant historical information
3. Alternatively, use LLM to generate historical context
4. Summarize into 2-4 engaging sentences
5. Calculate relevance based on:
   - Direct mention of location
   - Historical significance
   - Interesting/unusual facts

**Timeout:** 5000ms

**Error Handling:**
- If no Wikipedia entry: Use general neighborhood history
- If API unavailable: Use LLM fallback
- Return generic fact if nothing specific found

**Skills Needed:**
- Wikipedia API integration
- Text extraction and summarization
- Historical knowledge (or LLM access)
- Fact verification

**Color/Theme:** 📘 Blue (information/knowledge theme)

---

### 4. Judge Agent

**Agent Name:** `JudgeContentAgent`

**Description:**
Evaluate outputs from YouTube, Spotify, and History agents and intelligently select the best content for each waypoint. Consider relevance, quality, diversity, and user preferences.

**Input Parameters:**
- `transaction_id` (string): Transaction ID for tracing
- `waypoint_id` (integer): ID of the waypoint being judged
- `location_name` (string): Name of the location
- `youtube_result` (object): Output from YouTube agent (may be null if failed)
- `spotify_result` (object): Output from Spotify agent (may be null if failed)
- `history_result` (object): Output from History agent (may be null if failed)
- `previous_selections` (array): List of content types selected for previous waypoints (for diversity)

**Expected Output Format:**
```json
{
  "winner": "youtube|spotify|history|fallback",
  "reasoning": "Selected YouTube because it has the highest relevance score (0.90) and provides a visual tour, which is ideal for a landmark location. Spotify scored 0.82 but music is less appropriate here. History scored 0.70.",
  "confidence_score": 0.88,
  "individual_scores": {
    "youtube": 0.90,
    "spotify": 0.75,
    "history": 0.70
  },
  "decision_time_ms": 850,
  "tie_breaker_applied": false,
  "selected_content": {
    "content_type": "video",
    "title": "...",
    "description": "...",
    "url": "...",
    "relevance_score": 0.90,
    "metadata": {...}
  }
}
```

**Decision Criteria (Weighted):**

1. **Relevance to Location (40%)**: How well does the content match the location?
2. **Content Quality (30%)**: Is the content high-quality, popular, well-produced?
3. **Route Diversity (20%)**: Avoid selecting the same type repeatedly
4. **User Preferences (10%)**: If user prefers certain content types

**Processing Logic:**
1. Check which agents succeeded (have valid content)
2. If all failed → return "fallback" decision
3. Evaluate each successful agent:
   - Base score = agent's relevance_score
   - Adjust for location type (e.g., landmarks → prefer video)
   - Penalize if same type selected recently
4. Select highest-scoring agent
5. Generate clear reasoning explaining the decision
6. Calculate confidence score

**Timeout:** 3000ms

**Error Handling:**
- If all agents failed: Return fallback decision
- If tie: Apply tiebreaker rules (prefer variety)
- If timeout: Let orchestrator use fallback

**Skills Needed:**
- Multi-criteria decision analysis
- Content quality assessment
- Natural language generation (for reasoning)
- Optionally: LLM integration for sophisticated evaluation

**Color/Theme:** ⚖️ Purple (judgment/wisdom theme)

---

## Integration After Agent Creation

### What I'll Do Once You Create the Agents:

1. **Update `src/modules/orchestrator.py`**:
   - Replace `_run_youtube_agent()` with calls to your YouTube agent
   - Replace `_run_spotify_agent()` with calls to your Spotify agent
   - Replace `_run_history_agent()` with calls to your History agent
   - Replace `_run_judge()` with calls to your Judge agent

2. **Add Agent Client Code**:
   - Create `src/agents/` directory
   - Implement client wrappers for each agent
   - Handle agent communication (API calls, message formatting, etc.)

3. **Update Configuration**:
   - Add agent endpoint URLs or identifiers to config
   - Update environment variables as needed

4. **Test Integration**:
   - Run end-to-end tests with real agents
   - Verify transaction ID propagation
   - Check logging for all agent operations
   - Validate timeout handling
   - Test error scenarios

---

## Example Agent Call Flow

Once integrated, here's how an agent will be called:

```python
# In orchestrator._run_youtube_agent()

from src.agents.youtube_client import call_youtube_agent

def _run_youtube_agent(self, transaction_id: str, waypoint: Waypoint) -> AgentResult:
    start_time = time.time()

    self.logger.log_agent_start(
        "youtube",
        transaction_id,
        waypoint.id,
        search_query=waypoint.agent_context.youtube_query
    )

    try:
        # Call your real agent
        result = call_youtube_agent(
            transaction_id=transaction_id,
            waypoint_id=waypoint.id,
            location_name=waypoint.location_name,
            search_query=waypoint.agent_context.youtube_query,
            coordinates={
                "lat": waypoint.coordinates.lat,
                "lng": waypoint.coordinates.lng
            }
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        self.logger.log_agent_completion(
            "youtube",
            transaction_id,
            waypoint.id,
            result.status.value,
            execution_time_ms,
            relevance_score=result.content.relevance_score if result.content else 0.0
        )

        return result

    except Exception as e:
        self.logger.log_agent_error(
            "youtube",
            transaction_id,
            waypoint.id,
            str(e)
        )
        return create_error_result("youtube", transaction_id, waypoint.id, e)
```

---

## Testing After Agent Creation

Once agents are integrated, we'll test:

1. **Single Waypoint Test**: Verify all 4 agents run successfully
2. **Multi-Waypoint Test**: Verify batch processing and concurrency
3. **Timeout Test**: Simulate slow agents to test timeout handling
4. **Error Test**: Simulate agent failures to test error recovery
5. **Load Test**: Process route with 50 waypoints
6. **Log Analysis**: Verify transaction ID in all logs

---

## Next Steps

### For You (User):

1. **Create the 4 agents** using the specifications above in your agent interface
2. **Test each agent individually** with sample inputs
3. **Provide me with**:
   - Agent names/IDs (as they appear in your system)
   - How to call them (API endpoints, function names, etc.)
   - Any authentication requirements

### For Me (Claude):

1. Once you confirm agents are created, I will:
   - Create agent client code in `src/agents/`
   - Replace mock implementations with real calls
   - Add configuration for agent endpoints
   - Run integration tests
   - Document any issues

---

## Summary

**Current Status:** ✅ Infrastructure complete, ready for agents

**What's Built:**
- ✅ Complete 6-module pipeline
- ✅ Transaction ID tracking
- ✅ Structured JSON logging
- ✅ Thread pool management
- ✅ Timeout enforcement
- ✅ Error handling
- ✅ Mock agents (working end-to-end)

**What's Needed:**
- 🤖 Create 4 real agents using specs above

**What's Next:**
- 🔗 Integrate real agents
- 🧪 Test with real data
- 🌐 Add Google Maps API (Phase 4)

---

**Ready when you are! Let me know once you've created the agents and I'll integrate them immediately.**
