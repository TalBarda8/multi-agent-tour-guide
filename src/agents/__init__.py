"""
Agent Client Wrappers
Interfaces to the real specialized agents
"""

from src.agents.youtube_client import call_youtube_agent
from src.agents.spotify_client import call_spotify_agent
from src.agents.history_client import call_history_agent
from src.agents.judge_client import call_judge_agent

__all__ = [
    "call_youtube_agent",
    "call_spotify_agent",
    "call_history_agent",
    "call_judge_agent",
]
