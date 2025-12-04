#!/usr/bin/env python3
"""
Spotify Location Music Finder
Finds relevant music for specific geographic locations
"""

import os
import sys
import time
import json
import base64
import requests
from typing import Dict, Any, Optional, List


def authenticate_spotify() -> Optional[str]:
    """
    Authenticate with Spotify Web API using client credentials flow

    Returns:
        Access token if successful, None otherwise
    """
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set", file=sys.stderr)
        return None

    # Create authorization header
    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    # Request access token
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    try:
        response = requests.post(url, headers=headers, data=data, timeout=5)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Spotify authentication failed: {e}", file=sys.stderr)
        return None


def search_spotify(token: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search Spotify for tracks matching the query

    Args:
        token: Spotify access token
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of track objects
    """
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": query,
        "type": "track",
        "limit": limit,
        "market": "US"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('tracks', {}).get('items', [])
    except Exception as e:
        print(f"Spotify search failed: {e}", file=sys.stderr)
        return []


def calculate_relevance_score(
    track: Dict[str, Any],
    location_name: str,
    search_query: str
) -> float:
    """
    Calculate how relevant a track is to the location

    Scoring factors:
    - Location name in track title: +0.30
    - Location name in artist name: +0.25
    - Location keywords in title: +0.20
    - Popularity (0-100 scaled): +0.15
    - Album name match: +0.10

    Args:
        track: Spotify track object
        location_name: Name of the location
        search_query: Original search query

    Returns:
        Relevance score between 0.0 and 1.0
    """
    score = 0.0

    title = track.get('name', '').lower()
    artists = ' '.join([a.get('name', '') for a in track.get('artists', [])]).lower()
    album = track.get('album', {}).get('name', '').lower()
    popularity = track.get('popularity', 0)  # 0-100

    location_lower = location_name.lower()

    # Extract key location terms (like "5th avenue", "manhattan", "new york")
    location_keywords = []
    if '5th avenue' in location_lower or 'fifth avenue' in location_lower:
        location_keywords.extend(['5th avenue', 'fifth avenue', '5th ave'])
    if 'manhattan' in location_lower or 'midtown' in location_lower:
        location_keywords.extend(['manhattan', 'midtown'])
    location_keywords.extend(['new york', 'nyc', 'ny'])

    # Check title matches
    for keyword in location_keywords:
        if keyword in title:
            score += 0.30
            break

    # Check artist matches
    for keyword in location_keywords:
        if keyword in artists:
            score += 0.25
            break

    # Check for "city" or "urban" themes in title
    urban_keywords = ['city', 'urban', 'street', 'avenue', 'downtown', 'uptown']
    if any(kw in title for kw in urban_keywords):
        score += 0.15

    # Check album name
    for keyword in location_keywords:
        if keyword in album:
            score += 0.10
            break

    # Add popularity bonus (scaled to 0-0.20)
    score += (popularity / 100) * 0.20

    # Cap at 1.0
    return min(score, 1.0)


def select_best_track(
    tracks: List[Dict[str, Any]],
    location_name: str,
    search_query: str
) -> Optional[Dict[str, Any]]:
    """
    Select the most relevant track from search results

    Args:
        tracks: List of Spotify track objects
        location_name: Location name
        search_query: Original search query

    Returns:
        Best track with calculated relevance_score, or None
    """
    if not tracks:
        return None

    best_track = None
    best_score = 0.0

    for track in tracks:
        score = calculate_relevance_score(track, location_name, search_query)

        # Prefer tracks with higher score, use popularity as tiebreaker
        if score > best_score or (score == best_score and best_track and
                                  track.get('popularity', 0) > best_track.get('popularity', 0)):
            best_track = track
            best_score = score

    if best_track:
        best_track['calculated_relevance_score'] = best_score

    return best_track


def find_music_for_location(
    transaction_id: str,
    waypoint_id: int,
    location_name: str,
    search_query: str,
    latitude: float,
    longitude: float
) -> Dict[str, Any]:
    """
    Find the most relevant music for a specific location

    Args:
        transaction_id: Unique transaction identifier
        waypoint_id: Waypoint identifier
        location_name: Human-readable location name
        search_query: Pre-constructed Spotify search query
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        JSON result in AgentResult format
    """
    start_time = time.time()

    # Authenticate
    token = authenticate_spotify()
    if not token:
        return {
            "agent_name": "spotify",
            "transaction_id": transaction_id,
            "waypoint_id": waypoint_id,
            "status": "error",
            "content": None,
            "error_message": "Spotify authentication failed: Missing or invalid credentials",
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }

    # Search for tracks
    tracks = search_spotify(token, search_query)

    # If initial search is weak, try alternative searches
    if len(tracks) < 5:
        # Try broader NYC search
        alternative_query = "New York City urban street"
        tracks = search_spotify(token, alternative_query)

    # Select best track
    best_track = select_best_track(tracks, location_name, search_query)

    if not best_track:
        return {
            "agent_name": "spotify",
            "transaction_id": transaction_id,
            "waypoint_id": waypoint_id,
            "status": "error",
            "content": None,
            "error_message": "No tracks found matching location criteria",
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }

    # Extract track information
    track_url = best_track.get('external_urls', {}).get('spotify')
    artists = best_track.get('artists', [])
    artist_name = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'
    album_name = best_track.get('album', {}).get('name', 'Unknown Album')

    execution_time = int((time.time() - start_time) * 1000)

    return {
        "agent_name": "spotify",
        "transaction_id": transaction_id,
        "waypoint_id": waypoint_id,
        "status": "success",
        "content": {
            "content_type": "song",
            "title": best_track.get('name', 'Unknown Track'),
            "description": f"{artist_name} - {album_name}",
            "url": track_url,
            "relevance_score": best_track.get('calculated_relevance_score', 0.5),
            "metadata": {
                "artist": artist_name,
                "album": album_name,
                "popularity": best_track.get('popularity', 0),
                "preview_url": best_track.get('preview_url')
            }
        },
        "error_message": None,
        "execution_time_ms": execution_time
    }


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 6:
        print("Usage: spotify_finder.py <transaction_id> <waypoint_id> <location_name> <search_query> <lat> <lng>")
        sys.exit(1)

    transaction_id = sys.argv[1]
    waypoint_id = int(sys.argv[2])
    location_name = sys.argv[3]
    search_query = sys.argv[4]
    latitude = float(sys.argv[5])
    longitude = float(sys.argv[6])

    result = find_music_for_location(
        transaction_id,
        waypoint_id,
        location_name,
        search_query,
        latitude,
        longitude
    )

    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
