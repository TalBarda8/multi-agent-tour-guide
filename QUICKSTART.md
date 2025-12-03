# Quick Start Guide
## Get Your Multi-Agent Tour Guide Running in 5 Minutes

**Status:** Ready to Run
**Difficulty:** Easy
**Time:** 5-10 minutes

---

## 🚀 Option 1: Try It Right Now (Mock Mode)

The system works **out of the box** with mock data - no API keys needed!

### Step 1: Run the Demo

```bash
# Navigate to the project directory
cd "/Users/talbarda/Desktop/אישי/תואר שני/שנה ב'/LLM's בסביבה מרובת סוכנים/מטלה 4/multi-agent-tour-guide"

# Run the demo (uses mock data by default)
python3 main.py
```

**Expected Output:**
```
================================================================================
Multi-Agent AI Tour Guide System
================================================================================
Mode: MOCK (Development)
Logs: ./logs/tour-guide.log
================================================================================

Origin: Empire State Building, New York, NY
Destination: Central Park, New York, NY

Processing route...

✅ SUCCESS!

Transaction ID: TXID-20251130T...
Route Summary:
  Distance: 3.5 km
  Duration: 12 mins
  Waypoints: 8
  Enriched: 8 (100.0%)
```

**That's it!** The system is working with mock agents and mock route data.

---

## 🎯 Option 2: Use With Real Agents (Claude Code)

To use the real AI agents you created, you need to run it **through Claude Code** which has access to the Task tool.

### Method A: Ask Claude Code to Process a Route

Just ask me (Claude Code):

```
Process a route from "Times Square, NYC" to "Central Park, NYC"
using the real agents
```

I'll:
1. Call the Python modules to get and preprocess waypoints
2. Use the Task tool to invoke your real agents
3. Aggregate the results
4. Show you the enriched route

### Method B: Use the Orchestration Script

```bash
# This prepares waypoints for Claude Code to process
python3 orchestrate_with_agents.py
```

Then ask me to process the waypoints in `waypoints_to_process.json`.

---

## 🌍 Option 3: Use With Real Google Maps

To get **real routes** from Google Maps (not just the mock 8-waypoint route):

### Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Directions API"
4. Create credentials → API Key
5. Copy your API key

### Step 2: Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit the .env file
nano .env  # or use any text editor
```

**Add your API key:**
```bash
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
MOCK_MODE=false  # Change to false to use real Google Maps
```

### Step 3: Test Real Routes

```bash
# Run with real Google Maps
python3 main.py
```

Now it will fetch **real routes** from Google Maps! Try any origin/destination you want by editing `main.py`.

---

## 🧪 Testing Options

### Test 1: Mock Mode Demo (Fastest)

**What it tests:** Basic pipeline with mock agents
**Time:** 10 seconds
**Requirements:** None (works immediately)

```bash
python3 main.py
```

**What you'll see:**
- 8 waypoints from Empire State Building to Central Park
- Mock agent enrichment (video/music/history)
- Complete enriched route output
- Response saved to `response.json`

---

### Test 2: Configuration Test

**What it tests:** System configuration and dependencies
**Time:** 5 seconds

```bash
# Test configuration loads
python3 -c "from src.config import get_config; config = get_config(); print('✅ Config OK')"

# Test logging works
python3 -c "from src.logging_config import get_logger; logger = get_logger(); logger.info('Test log'); print('✅ Logging OK')"

# Test models load
python3 -c "from src.models import create_transaction_id, Waypoint; print(f'✅ Models OK: {create_transaction_id()}')"
```

---

### Test 3: Google Maps Integration Test

**What it tests:** Real Google Maps API connection
**Time:** 2-3 seconds
**Requirements:** Google Maps API key in `.env`

```bash
# Test Google Maps client
python3 -c "
from src.google_maps import GoogleMapsClient
from src.config import get_config

config = get_config()
if config.mock_mode:
    print('⚠️  MOCK_MODE=true, set to false in .env to test real Google Maps')
else:
    try:
        client = GoogleMapsClient()
        route = client.get_directions('Times Square, NYC', 'Central Park, NYC')
        print(f'✅ Google Maps OK: {len(route.waypoints)} waypoints retrieved')
    except Exception as e:
        print(f'❌ Error: {e}')
"
```

---

### Test 4: Real Agent Integration Test

**What it tests:** All 4 real agents with a single waypoint
**Time:** 5-10 seconds
**Requirements:** Claude Code to invoke agents

Ask me (Claude Code) to run this test:

```
Test all 4 agents with this waypoint:
- Location: Times Square, New York
- Coordinates: 40.7580, -73.9855
```

I'll invoke:
1. YouTube agent to find a video
2. Spotify agent to find music
3. History agent to find historical facts
4. Judge agent to select the best content

You'll see all 4 agents respond with real results!

---

### Test 5: Full End-to-End Test

**What it tests:** Complete system with real agents + real Google Maps
**Time:** 20-30 seconds
**Requirements:** Google Maps API key + Claude Code

```bash
# 1. Set up real Google Maps
echo "MOCK_MODE=false" >> .env
echo "GOOGLE_MAPS_API_KEY=your_key" >> .env

# 2. Run the preparation script
python3 orchestrate_with_agents.py
```

Then ask me (Claude Code):
```
Process the route in waypoints_to_process.json with real agents
```

This runs the **complete system**:
- Real Google Maps route retrieval
- Real waypoint preprocessing
- Real agent enrichment for all waypoints
- Real judge decisions
- Complete aggregation and formatting

---

## 📊 Viewing Results

### Check the JSON Output

```bash
# View the complete response
cat response.json | python3 -m json.tool

# Or use jq for prettier output
cat response.json | jq .
```

### Check the Logs

```bash
# View recent logs
tail -20 logs/tour-guide.log

# Pretty print logs
tail -50 logs/tour-guide.log | jq .

# Search for specific transaction
grep "TXID-..." logs/tour-guide.log | jq .

# Find errors
grep '"level":"ERROR"' logs/tour-guide.log | jq .

# Agent performance
grep "agent completed" logs/tour-guide.log | jq '.execution_time_ms'
```

---

## 🎮 Try Different Routes

### Method 1: Edit main.py

```bash
nano main.py
```

Find these lines (around line 33-34):
```python
origin = "Empire State Building, New York, NY"
destination = "Central Park, New York, NY"
```

Change to your desired route:
```python
origin = "Los Angeles International Airport"
destination = "Hollywood Sign, Los Angeles"
```

Save and run:
```bash
python3 main.py
```

### Method 2: Use Python Directly

```python
from src.pipeline import execute_pipeline_safe

# Try any route!
response = execute_pipeline_safe(
    origin="Golden Gate Bridge, San Francisco",
    destination="Fisherman's Wharf, San Francisco"
)

# Check result
if "error" in response:
    print(f"Error: {response['error']['message']}")
else:
    print(f"Success! {response['route']['summary']['total_waypoints']} waypoints")
    print(f"Distance: {response['route']['summary']['total_distance']}")
```

### Method 3: Command Line Script

Create `test_route.py`:
```python
#!/usr/bin/env python3
import sys
from src.pipeline import execute_pipeline_safe
import json

if len(sys.argv) != 3:
    print("Usage: python3 test_route.py 'origin' 'destination'")
    sys.exit(1)

response = execute_pipeline_safe(sys.argv[1], sys.argv[2])
print(json.dumps(response, indent=2))
```

Use it:
```bash
python3 test_route.py "Statue of Liberty" "Times Square"
```

---

## 🔍 Understanding the Output

### Response Structure

```json
{
  "transaction_id": "TXID-20251130T...",
  "route": {
    "summary": {
      "total_distance": "3.5 km",
      "total_duration": "12 mins",
      "total_waypoints": 8,
      "enriched_count": 8,
      "success_rate": "100.0%"
    },
    "waypoints": [
      {
        "step": 1,
        "location": "5th Avenue & E 34th St",
        "coordinates": {"lat": 40.748817, "lng": -73.985428},
        "instruction": "Head north on 5th Ave",
        "distance_from_start": "0 m",
        "content": {
          "type": "history",
          "title": "Home of the Iconic Empire State Building",
          "description": "Historical facts...",
          "url": "https://...",
          "relevance_score": "1.00"
        },
        "decision": {
          "winner": "history",
          "confidence": "0.74",
          "reasoning": "Selected history because..."
        }
      }
      // ... more waypoints
    ]
  },
  "statistics": {
    "total_processing_time": "4.1 seconds",
    "average_processing_time": "507 ms",
    "content_breakdown": {
      "video": 2,
      "song": 4,
      "history": 2
    }
  }
}
```

### Key Fields

- **`transaction_id`**: Unique ID for this request (searchable in logs)
- **`summary`**: High-level route statistics
- **`waypoints[]`**: Array of enriched waypoints
  - **`content`**: The selected media (video/song/history)
  - **`decision`**: Why the judge selected this content
- **`statistics`**: Performance metrics and content breakdown

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"

```bash
# Install dependencies
pip install -r requirements.txt
```

### Issue: "No such file or directory: ./logs/tour-guide.log"

```bash
# Create log directory
mkdir -p logs
```

### Issue: Google Maps "API key is invalid"

1. Check `.env` has correct key (no quotes, no spaces)
2. Verify Directions API is enabled in Google Cloud Console
3. Check API key restrictions aren't blocking localhost

### Issue: Agents not responding

**Remember:** Real agents require Claude Code to invoke them using the Task tool. The Python code can't directly call Claude Code agents - it needs my orchestration.

**Solution:** Ask me to process the route with agents instead of running `main.py` directly.

---

## 💡 Tips

### Tip 1: Start Simple

Run in mock mode first to understand the flow, then add:
1. Google Maps API key (real routes)
2. Real agent processing (through Claude Code)

### Tip 2: Check Logs

Logs tell the complete story:
```bash
tail -f logs/tour-guide.log | jq .
```

Watch logs in real-time while processing routes!

### Tip 3: Use Transaction IDs

If something goes wrong, get the transaction ID from output, then:
```bash
grep "TXID-your-id-here" logs/tour-guide.log | jq .
```

This shows every operation for that request.

### Tip 4: Test Components Separately

- Test Google Maps alone: Use test from "Test 3" above
- Test agents alone: Ask me to test with a single waypoint
- Test full pipeline: Use main.py or orchestrate_with_agents.py

---

## 🎯 Quick Command Reference

```bash
# Basic run (mock mode)
python3 main.py

# Configure for production
cp .env.example .env
nano .env  # Add API keys

# View logs
tail -20 logs/tour-guide.log | jq .

# Check config
python3 -c "from src.config import get_config; print(get_config().to_dict())"

# Test specific route
python3 test_route.py "origin" "destination"

# Monitor logs live
tail -f logs/tour-guide.log | jq .
```

---

## 📚 Next Steps

1. **Try mock mode** - Run `python3 main.py` right now
2. **Check logs** - See transaction tracking in action
3. **Add Google Maps** - Get API key and try real routes
4. **Test real agents** - Ask me to process with Task tool
5. **Deploy** - Follow `PRODUCTION_DEPLOYMENT_GUIDE.md`

---

## 🎉 You're Ready!

The system is **working right now**. Just run:
```bash
python3 main.py
```

Everything else is optional enhancement!

---

**Questions?** Check the comprehensive guides:
- [README.md](./README.md) - Overview
- [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md) - Full deployment
- [PHASE4_GOOGLE_MAPS_INTEGRATION.md](./PHASE4_GOOGLE_MAPS_INTEGRATION.md) - Google Maps setup
