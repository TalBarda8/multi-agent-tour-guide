"""
Minimal End-to-End Test
Tests first waypoint only to minimize API usage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import execute_pipeline_safe
from src.config import get_config

# Check configuration
config = get_config()
print(f"Mock Mode: {config.mock_mode}")
print(f"Google Maps API Key: {'SET' if config.google_maps_api_key else 'NOT SET'}")
print(f"YouTube API Key: {'SET' if config.youtube_api_key else 'NOT SET'}")
print()

# Minimal route
origin = "Jerusalem"
destination = "Jerusalem Central Station"

print("Running minimal test...")
print(f"Route: {origin} → {destination}")
print()

response = execute_pipeline_safe(
    origin=origin,
    destination=destination,
    preferences={"content_type": "auto"}
)

if "error" in response:
    print(f"❌ ERROR: {response['error']['message']}")
else:
    print("✅ Pipeline completed successfully")
    print()

    # Show first waypoint only
    waypoint = response['route']['waypoints'][0]
    print(f"Waypoint: {waypoint['location']}")
    print(f"Coords: ({waypoint['coordinates']['lat']}, {waypoint['coordinates']['lng']})")
    print()

    if 'content' in waypoint and waypoint['content']['type'] != 'none':
        content = waypoint['content']
        print(f"Selected Content: {content['type'].upper()}")
        print(f"  Title: {content['title']}")
        print(f"  Score: {content['relevance_score']}")
        print()

        if 'decision' in waypoint:
            decision = waypoint['decision']
            print(f"Judge Decision:")
            print(f"  Winner: {decision['winner']}")
            print(f"  Confidence: {decision['confidence']}")
            print(f"  Reasoning: {decision['reasoning']}")
