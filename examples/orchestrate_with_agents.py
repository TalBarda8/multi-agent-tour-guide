"""
Claude Code Orchestration Script

This script demonstrates how Claude Code orchestrates the real agents.
It should be run BY Claude Code, not as a standalone Python script.

The orchestration flow:
1. Python modules handle data processing (validation, preprocessing, etc.)
2. Claude Code calls Task agents for content enrichment
3. Results are aggregated and formatted by Python modules

To run: Ask Claude Code to execute this workflow
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.modules import (
    validate_request,
    retrieve_route,
    preprocess_waypoints,
    aggregate_results,
    format_response
)
from src.logging_config import get_logger


class AgentOrchestrator:
    """
    Orchestrator that works with Claude Code's Task agents

    This class provides the structure, but the actual agent calls
    must be made by Claude Code using the Task tool.
    """

    def __init__(self):
        self.logger = get_logger()

    def process_route(self, origin: str, destination: str):
        """
        Process a route with real agents

        This method should be called by Claude Code, which will:
        1. Run Python modules for data processing
        2. Use Task tool to invoke agents for each waypoint
        3. Collect results and aggregate

        Args:
            origin: Starting location
            destination: Ending location
        """
        # Step 1: Validate request
        context = validate_request(origin, destination)

        self.logger.info(
            "Orchestration started with real agents",
            transaction_id=context.transaction_id
        )

        # Step 2: Retrieve route
        route_data = retrieve_route(context)

        # Step 3: Preprocess waypoints
        processed_waypoints = preprocess_waypoints(context, route_data)

        self.logger.info(
            f"Ready to enrich {len(processed_waypoints)} waypoints with real agents",
            transaction_id=context.transaction_id
        )

        # Step 4: For each waypoint, agents need to be called
        # This is where Claude Code takes over using Task tool

        print("\n" + "="*80)
        print("WAITING FOR CLAUDE CODE ORCHESTRATION")
        print("="*80)
        print(f"\nTransaction ID: {context.transaction_id}")
        print(f"Waypoints to process: {len(processed_waypoints)}\n")

        for waypoint in processed_waypoints:
            print(f"Waypoint {waypoint.id}: {waypoint.location_name}")
            print(f"  YouTube Query: {waypoint.agent_context.youtube_query}")
            print(f"  Spotify Query: {waypoint.agent_context.spotify_query}")
            print(f"  History Query: {waypoint.agent_context.history_query}")
            print()

        print("Claude Code should now:")
        print("1. For each waypoint, invoke agents using Task tool:")
        print("   - youtube-location-video-finder")
        print("   - spotify-location-music-finder")
        print("   - history-location-researcher")
        print("2. Collect all 3 results")
        print("3. Invoke content-evaluator-judge to select best content")
        print("4. Attach enrichment to waypoint")
        print("5. Call aggregate_results() and format_response()")
        print("="*80)

        return {
            "context": context,
            "route_data": route_data,
            "processed_waypoints": processed_waypoints
        }


def save_waypoints_for_processing(waypoints, filename="waypoints_to_process.json"):
    """
    Save waypoints to file for Claude Code to process
    """
    data = {
        "waypoints": [
            {
                "id": wp.id,
                "location_name": wp.location_name,
                "coordinates": {
                    "lat": wp.coordinates.lat,
                    "lng": wp.coordinates.lng
                },
                "queries": {
                    "youtube": wp.agent_context.youtube_query,
                    "spotify": wp.agent_context.spotify_query,
                    "history": wp.agent_context.history_query
                }
            }
            for wp in waypoints
        ]
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nWaypoints saved to {filename}")
    print("Claude Code can now process these waypoints with real agents.")


if __name__ == "__main__":
    print("="*80)
    print("Multi-Agent Tour Guide - Real Agent Orchestration")
    print("="*80)
    print("\nThis script prepares waypoints for Claude Code to process with real agents.\n")

    orchestrator = AgentOrchestrator()

    # Example route
    result = orchestrator.process_route(
        origin="Empire State Building, New York, NY",
        destination="Central Park, New York, NY"
    )

    # Save waypoints for Claude to process
    save_waypoints_for_processing(
        result["processed_waypoints"],
        "waypoints_to_process.json"
    )
