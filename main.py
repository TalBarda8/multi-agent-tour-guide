"""
Multi-Agent AI Tour Guide System
Main Entry Point
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import execute_pipeline_safe
from src.config import get_config


def main():
    """
    Main function - demonstrates the system with a sample request
    """
    # Setup configuration and logging
    config = get_config()

    print("=" * 80)
    print("Multi-Agent AI Tour Guide System")
    print("=" * 80)
    print(f"Mode: {'MOCK (Development)' if config.mock_mode else 'PRODUCTION'}")
    print(f"Logs: {config.log_file_path}")
    print("=" * 80)
    print()

    # Example request
    origin = "Empire State Building, New York, NY"
    destination = "Central Park, New York, NY"

    print(f"Origin: {origin}")
    print(f"Destination: {destination}")
    print()
    print("Processing route...")
    print()

    # Execute pipeline
    response = execute_pipeline_safe(
        origin=origin,
        destination=destination,
        preferences={
            "content_type": "auto"
        }
    )

    # Display results
    if "error" in response:
        print("❌ ERROR:")
        print(f"  Code: {response['error']['code']}")
        print(f"  Message: {response['error']['message']}")
    else:
        print("✅ SUCCESS!")
        print()
        print(f"Transaction ID: {response['transaction_id']}")
        print()

        # Route summary
        summary = response['route']['summary']
        print("Route Summary:")
        print(f"  Distance: {summary['total_distance']}")
        print(f"  Duration: {summary['total_duration']}")
        print(f"  Waypoints: {summary['total_waypoints']}")
        print(f"  Enriched: {summary['enriched_count']} ({summary['success_rate']})")
        print()

        # Statistics
        stats = response['statistics']
        print("Processing Statistics:")
        print(f"  Total Time: {stats['total_processing_time']}")
        print(f"  Average Time per Waypoint: {stats['average_processing_time']}")
        print(f"  Content Breakdown:")
        for content_type, count in stats['content_breakdown'].items():
            if count > 0:
                print(f"    - {content_type}: {count}")
        print()

        # Waypoints (show first 3)
        print("Sample Waypoints:")
        for waypoint in response['route']['waypoints'][:3]:
            print(f"\n  Step {waypoint['step']}: {waypoint['location']}")
            print(f"    Instruction: {waypoint['instruction']}")
            if 'content' in waypoint and waypoint['content']['type'] != 'none':
                content = waypoint['content']
                print(f"    Content: {content['type'].upper()}")
                print(f"      Title: {content['title']}")
                print(f"      Relevance: {content['relevance_score']}")
                if 'decision' in waypoint:
                    print(f"      Selected by: {waypoint['decision']['winner']} (confidence: {waypoint['decision']['confidence']})")

        if len(response['route']['waypoints']) > 3:
            print(f"\n  ... and {len(response['route']['waypoints']) - 3} more waypoints")

    print()
    print("=" * 80)
    print(f"Full response saved to: ./response.json")
    print(f"Logs available at: {config.log_file_path}")
    print("=" * 80)

    # Save full response to file
    with open("response.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)


if __name__ == "__main__":
    main()
