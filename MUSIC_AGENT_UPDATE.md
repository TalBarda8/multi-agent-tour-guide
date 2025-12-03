# Music Agent Update - Spotify → YouTube Music

**Date:** December 2, 2025
**Status:** ✅ Code Updated - Agent Creation Needed

---

## 🎯 What Changed

The system has been updated to use a **Music Agent** that searches **YouTube** for songs instead of Spotify. This eliminates the need for Spotify API credentials.

### Key Benefits
- ✅ No Spotify API credentials needed
- ✅ Both agents use YouTube (different purposes)
- ✅ Simpler configuration
- ✅ Music Agent finds songs/music videos on YouTube

---

## 📝 Code Changes Made

### 1. **Orchestrator** (`src/modules/orchestrator.py`)
- ✅ Renamed `_run_spotify_agent()` → `_run_music_agent()`
- ✅ Updated agent name from `"spotify"` → `"music"`
- ✅ Updated mock implementation to use YouTube URLs
- ✅ Updated comments to reflect YouTube Music search

### 2. **Models** (`src/models.py`)
- ✅ Updated `AgentResult` comment: `"spotify"` → `"music"`
- ✅ Updated `AgentContext`: `spotify_query` → `music_query`

### 3. **Waypoint Preprocessor** (`src/modules/waypoint_preprocessor.py`)
- ✅ Renamed `_build_spotify_query()` → `_build_music_query()`
- ✅ Updated to add music-specific keywords for YouTube search
- ✅ Now adds: `"song instrumental ambient music"` or `"song city urban music"`

### 4. **Configuration** (`src/config.py`)
- ✅ Removed `spotify_client_id` and `spotify_client_secret` fields
- ✅ Removed Spotify validation checks
- ✅ Updated YouTube API comment: "Used by YouTube agents (video + music)"

### 5. **Environment Files** (`.env`, `.env.example`)
- ✅ Removed `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
- ✅ Updated comments for `YOUTUBE_API_KEY`

---

## 🎵 Agent Comparison

### Before: Two Platforms
| Agent | Platform | Purpose |
|-------|----------|---------|
| YouTube Agent | YouTube | Find walking tours, location videos |
| Spotify Agent | Spotify | Find songs/music (required credentials) |

### After: One Platform, Two Purposes
| Agent | Platform | Purpose |
|-------|----------|---------|
| YouTube Video Agent | YouTube | Find walking tours, location videos |
| Music Agent | YouTube | Find songs, music videos |

---

## 🔨 What You Need to Do

### Step 1: Create New Music Agent

You need to create a **new agent** in your Claude Code interface called:

**Agent Name:** `youtube-location-music-finder` or `music-location-finder`

**Agent Purpose:** Find music/songs on YouTube for a given location

**Agent Skills:** Same as your YouTube agent - searches YouTube using the YouTube Data API v3

### Step 2: Agent Specification

The Music Agent should:

1. **Search YouTube for music** related to the location
2. **Filter for songs/music videos** (not walking tours)
3. **Look for:**
   - Songs mentioning the location name
   - Music videos filmed at the location
   - Songs by artists from that location
   - Genre-appropriate music (instrumental for landmarks, urban for city streets)

### Step 3: Input Format

The Music Agent receives:
```json
{
  "transaction_id": "TXID-...",
  "waypoint_id": 1,
  "location": "5th Avenue & E 34th St, New York",
  "coordinates": {"lat": 40.748817, "lng": -73.985428},
  "search_query": "Empire State Building song instrumental ambient music"
}
```

### Step 4: Output Format

The Music Agent should return:
```json
{
  "agent_name": "music",
  "transaction_id": "TXID-...",
  "waypoint_id": 1,
  "status": "success",
  "content": {
    "type": "song",
    "title": "Empire State of Mind",
    "artist": "JAY-Z featuring Alicia Keys",
    "url": "https://youtube.com/watch?v=...",
    "description": "Iconic NYC anthem featuring the Empire State Building",
    "relevance_score": 0.95
  }
}
```

---

## 🎬 Example Search Differences

### YouTube Video Agent
**Search Query:** `"5th Avenue walking tour NYC 4K"`
**Results:** Walking tours, street views, virtual tours

### Music Agent
**Search Query:** `"Empire State Building song instrumental ambient music"`
**Results:** Songs, music videos, soundtracks

---

## 🧪 Testing

Once you create the Music Agent, test it:

```bash
# Ask Claude Code to process a route with the new agent
"Process a route from Times Square to Central Park using real agents including the new Music agent"
```

Expected behavior:
- ✅ YouTube Video Agent finds walking tours
- ✅ Music Agent finds songs/music videos
- ✅ History Agent finds historical facts
- ✅ Judge selects best content with diversity

---

## 📊 System Status

| Component | Status |
|-----------|--------|
| **Code Updates** | ✅ Complete |
| **Music Agent Creation** | ⏳ **You need to create this** |
| **YouTube Video Agent** | ✅ Already exists |
| **History Agent** | ✅ Already exists |
| **Judge Agent** | ✅ Already exists |

---

## 🚀 Next Steps

1. **Create the Music Agent** in your Claude Code interface
2. **Test with a sample route** to verify all agents work
3. **Compare results** - Judge should select mix of video, music, and history

---

## ✅ Benefits Achieved

- 🎵 Music enrichment without Spotify credentials
- 🎬 Both agents use same YouTube platform
- 🔧 Simpler system configuration
- 💰 No additional API costs (only YouTube)
- 🎯 Clear separation: Video Agent = visual tours, Music Agent = songs

---

**Status:** Code ready, waiting for Music Agent creation
**Questions?** Review this document or ask for clarification
