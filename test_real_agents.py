"""
Direct test of real agents for minimal API usage
Processes ONE waypoint from test_waypoints.json
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Load test waypoint
with open("test_waypoints.json") as f:
    data = json.load(f)
    transaction_id = data["transaction_id"]
    waypoint = data["waypoints"][0]

print("=" * 80)
print("MINIMAL END-TO-END TEST - REAL AGENTS")
print("=" * 80)
print(f"Transaction ID: {transaction_id}")
print(f"Waypoint: {waypoint['location']}")
print(f"Coordinates: ({waypoint['coordinates']['lat']}, {waypoint['coordinates']['lng']})")
print()
print("Invoking 3 content agents in parallel...")
print("=" * 80)
print()

# This will be processed by Claude Code to invoke the actual agents
print("Agents to invoke:")
print("1. youtube-location-video-finder")
print("2. music-location-finder")
print("3. history-location-researcher")
print("4. content-evaluator-judge (after collecting results)")
