"""
Unit tests for src/modules/orchestrator.py
Tests parallel agent coordination and waypoint enrichment
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import TimeoutError as FuturesTimeoutError

from src.modules.orchestrator import Orchestrator
from src.models import (
    Waypoint,
    Coordinates,
    AgentResult,
    AgentStatus,
    ContentType,
    create_fallback_content,
    create_timeout_result,
    create_error_result,
    WaypointEnrichment,
    ContentItem,
    JudgeDecision
)


@pytest.mark.unit
class TestOrchestrator:
    """Test Orchestrator class"""

    def test_orchestrator_initialization(self, mock_config):
        """Test orchestrator initializes properly"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            orchestrator = Orchestrator()

            assert orchestrator.config == mock_config
            assert orchestrator.thread_pool is not None
            assert orchestrator.results_cache == {}
            assert orchestrator._cache_lock is not None

            # Cleanup
            orchestrator.shutdown()

    def test_create_batches_single_batch(self):
        """Test batch creation with fewer waypoints than batch size"""
        with patch('src.modules.orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.max_concurrent_waypoints = 5
            mock_config.max_agent_threads = 10
            mock_get_config.return_value = mock_config

            orchestrator = Orchestrator()
            waypoints = [
                Waypoint(
                    id=i,
                    location_name=f"Location {i}",
                    coordinates=Coordinates(lat=40.0 + i, lng=-74.0),
                    instruction=f"Step {i}",
                    distance_from_start=float(i * 100),
                    step_index=i
                )
                for i in range(3)
            ]

            batches = orchestrator._create_batches(waypoints)

            assert len(batches) == 1
            assert len(batches[0]) == 3

            # Cleanup
            orchestrator.shutdown()

    def test_create_batches_multiple_batches(self):
        """Test batch creation with more waypoints than batch size"""
        with patch('src.modules.orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.max_concurrent_waypoints = 3
            mock_config.max_agent_threads = 10
            mock_get_config.return_value = mock_config

            orchestrator = Orchestrator()
            waypoints = [
                Waypoint(
                    id=i,
                    location_name=f"Location {i}",
                    coordinates=Coordinates(lat=40.0 + i, lng=-74.0),
                    instruction=f"Step {i}",
                    distance_from_start=float(i * 100),
                    step_index=i
                )
                for i in range(8)
            ]

            batches = orchestrator._create_batches(waypoints)

            assert len(batches) == 3  # 8 waypoints / 3 batch size = 3 batches
            assert len(batches[0]) == 3
            assert len(batches[1]) == 3
            assert len(batches[2]) == 2

            # Cleanup
            orchestrator.shutdown()

    @patch('src.modules.orchestrator.run_mock_judge')
    @patch('src.modules.orchestrator.run_mock_history_agent')
    @patch('src.modules.orchestrator.run_mock_spotify_agent')
    @patch('src.modules.orchestrator.run_mock_youtube_agent')
    def test_enrich_single_waypoint_success(
        self,
        mock_youtube,
        mock_spotify,
        mock_history,
        mock_judge,
        transaction_context,
        sample_waypoints,
        mock_config
    ):
        """Test successful enrichment of single waypoint"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            # Setup mocks
            youtube_result = AgentResult(
                agent_name="youtube",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.VIDEO,
                    title="Test Video",
                    description="Test video description",
                    relevance_score=0.85,
                    url="https://youtube.com/test"
                )
            )

            spotify_result = AgentResult(
                agent_name="spotify",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.SONG,
                    title="Test Song",
                    description="Test song description",
                    relevance_score=0.80,
                    url="https://spotify.com/test"
                )
            )

            history_result = AgentResult(
                agent_name="history",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.HISTORY,
                    title="Test History",
                    description="Historical facts",
                    relevance_score=0.75
                )
            )

            mock_youtube.return_value = youtube_result
            mock_spotify.return_value = spotify_result
            mock_history.return_value = history_result

            mock_judge.return_value = JudgeDecision(
                winner="youtube",
                selected_content=youtube_result.content,
                reasoning="Video has best engagement",
                confidence_score=0.9,
                individual_scores={"youtube": 0.9, "spotify": 0.7, "history": 0.8}
            )

            orchestrator = Orchestrator()
            enriched_waypoint = orchestrator._enrich_single_waypoint(
                transaction_context,
                sample_waypoints[0]
            )

            # Verify enrichment
            assert enriched_waypoint.enrichment is not None
            assert enriched_waypoint.enrichment.selected_content.content_type == ContentType.VIDEO
            assert len(enriched_waypoint.enrichment.all_agent_results) == 3
            assert enriched_waypoint.enrichment.judge_decision.winner == "youtube"
            assert enriched_waypoint.is_enriched()

            # Cleanup
            orchestrator.shutdown()

    @patch('src.modules.orchestrator.run_mock_judge')
    @patch('src.modules.orchestrator.run_mock_history_agent')
    @patch('src.modules.orchestrator.run_mock_spotify_agent')
    @patch('src.modules.orchestrator.run_mock_youtube_agent')
    def test_enrich_single_waypoint_with_agent_timeout(
        self,
        mock_youtube,
        mock_spotify,
        mock_history,
        mock_judge,
        transaction_context,
        sample_waypoints,
        mock_config
    ):
        """Test waypoint enrichment when an agent times out"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            # YouTube times out
            def youtube_timeout(*args, **kwargs):
                import time
                time.sleep(10)  # Simulate long operation
                return AgentResult(
                    agent_name="youtube",
                    transaction_id=transaction_context.transaction_id,
                    waypoint_id=sample_waypoints[0].id,
                    success=False
                )

            mock_youtube.side_effect = youtube_timeout

            # Other agents succeed
            spotify_result = AgentResult(
                agent_name="spotify",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.SONG,
                    title="Test Song",
                    description="Test song description",
                    relevance_score=0.80,
                    url="https://spotify.com/test"
                )
            )

            history_result = AgentResult(
                agent_name="history",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.HISTORY,
                    title="Test History",
                    description="Historical facts",
                    relevance_score=0.75
                )
            )

            mock_spotify.return_value = spotify_result
            mock_history.return_value = history_result

            mock_judge.return_value = JudgeDecision(
                winner="spotify",
                selected_content=spotify_result.content,
                reasoning="Spotify available",
                confidence_score=0.8,
                individual_scores={"spotify": 0.8, "history": 0.7}
            )

            # Reduce timeout for faster test
            mock_config.agent_timeout_ms = 100

            orchestrator = Orchestrator()
            enriched_waypoint = orchestrator._enrich_single_waypoint(
                transaction_context,
                sample_waypoints[0]
            )

            # Should still complete with timeout result for youtube
            assert enriched_waypoint.enrichment is not None
            assert 'youtube' in enriched_waypoint.enrichment.all_agent_results
            # YouTube should be marked as failed due to timeout
            youtube_result_actual = enriched_waypoint.enrichment.all_agent_results['youtube']
            assert not youtube_result_actual.is_successful()

            # Cleanup
            orchestrator.shutdown()

    @patch('src.modules.orchestrator.run_mock_judge')
    @patch('src.modules.orchestrator.run_mock_history_agent')
    @patch('src.modules.orchestrator.run_mock_spotify_agent')
    @patch('src.modules.orchestrator.run_mock_youtube_agent')
    def test_enrich_single_waypoint_with_agent_error(
        self,
        mock_youtube,
        mock_spotify,
        mock_history,
        mock_judge,
        transaction_context,
        sample_waypoints,
        mock_config
    ):
        """Test waypoint enrichment when an agent raises an error"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            # YouTube raises error
            mock_youtube.side_effect = RuntimeError("YouTube API error")

            # Other agents succeed
            spotify_result = AgentResult(
                agent_name="spotify",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.SONG,
                    title="Test Song",
                    description="Test song description",
                    relevance_score=0.80,
                    url="https://spotify.com/test"
                )
            )

            history_result = AgentResult(
                agent_name="history",
                transaction_id=transaction_context.transaction_id,
                waypoint_id=sample_waypoints[0].id,
                status=AgentStatus.SUCCESS,
                content=ContentItem(
                    content_type=ContentType.HISTORY,
                    title="Test History",
                    description="Historical facts",
                    relevance_score=0.75
                )
            )

            mock_spotify.return_value = spotify_result
            mock_history.return_value = history_result

            mock_judge.return_value = JudgeDecision(
                winner="history",
                selected_content=history_result.content,
                reasoning="History best available",
                confidence_score=0.8,
                individual_scores={"spotify": 0.7, "history": 0.8}
            )

            orchestrator = Orchestrator()
            enriched_waypoint = orchestrator._enrich_single_waypoint(
                transaction_context,
                sample_waypoints[0]
            )

            # Should complete with error result for youtube
            assert enriched_waypoint.enrichment is not None
            assert 'youtube' in enriched_waypoint.enrichment.all_agent_results
            youtube_result = enriched_waypoint.enrichment.all_agent_results['youtube']
            assert not youtube_result.is_successful()
            assert "error" in youtube_result.error_message.lower() or youtube_result.error_message

            # Cleanup
            orchestrator.shutdown()

    @patch('src.modules.orchestrator.Orchestrator._enrich_single_waypoint')
    def test_process_waypoint_batch(
        self,
        mock_enrich,
        transaction_context,
        sample_waypoints,
        mock_config
    ):
        """Test processing a batch of waypoints"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            # Mock the enrichment to return the waypoint as-is
            mock_enrich.side_effect = lambda ctx, wp: wp

            orchestrator = Orchestrator()
            batch = sample_waypoints[:3]

            results = orchestrator._process_waypoint_batch(transaction_context, batch)

            assert len(results) == 3
            assert mock_enrich.call_count == 3

            # Cleanup
            orchestrator.shutdown()

    @patch('src.modules.orchestrator.Orchestrator._enrich_single_waypoint')
    def test_process_waypoint_batch_with_timeout(
        self,
        mock_enrich,
        transaction_context,
        sample_waypoints,
        mock_config
    ):
        """Test batch processing when a waypoint times out"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            # First waypoint succeeds, second times out
            def enrich_with_timeout(ctx, wp):
                if wp.id == 2:
                    import time
                    time.sleep(10)  # Simulate timeout
                return wp

            mock_enrich.side_effect = enrich_with_timeout

            # Set very short timeout
            mock_config.agent_timeout_ms = 50
            mock_config.judge_timeout_ms = 50

            orchestrator = Orchestrator()
            batch = sample_waypoints[:2]

            results = orchestrator._process_waypoint_batch(transaction_context, batch)

            # Should get both waypoints back, even if one timed out
            assert len(results) == 2

            # Cleanup
            orchestrator.shutdown()

    @patch('src.modules.orchestrator.Orchestrator._process_waypoint_batch')
    def test_enrich_route_complete(
        self,
        mock_process_batch,
        transaction_context,
        sample_waypoints,
        mock_config
    ):
        """Test complete route enrichment"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            # Mock batch processing to return waypoints
            mock_process_batch.return_value = sample_waypoints

            orchestrator = Orchestrator()
            result = orchestrator.enrich_route(transaction_context, sample_waypoints)

            assert len(result) == len(sample_waypoints)
            assert mock_process_batch.called

            # Cleanup
            orchestrator.shutdown()

    def test_shutdown(self, mock_config):
        """Test orchestrator shutdown"""
        with patch('src.modules.orchestrator.get_config', return_value=mock_config):
            orchestrator = Orchestrator()

            # Should not raise exception
            orchestrator.shutdown()

            # Thread pool should be shut down
            assert orchestrator.thread_pool._shutdown
