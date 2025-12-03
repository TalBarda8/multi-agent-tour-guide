"""
Module 4: Orchestrator
Coordinates parallel agent execution for each waypoint
This is the central nervous system of the multi-agent platform
"""

import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Dict
import threading

from src.models import (
    TransactionContext,
    Waypoint,
    AgentResult,
    WaypointEnrichment,
    create_fallback_content,
    create_timeout_result,
    create_error_result
)
from src.modules.mock_agents import (
    run_mock_youtube_agent,
    run_mock_spotify_agent,
    run_mock_history_agent,
    run_mock_judge
)
from src.logging_config import get_logger
from src.config import get_config


class Orchestrator:
    """
    Central coordinator for multi-agent waypoint enrichment
    Manages thread pools, timeouts, and result aggregation
    """

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.max_agent_threads
        )
        self.results_cache: Dict[int, WaypointEnrichment] = {}
        self._cache_lock = threading.Lock()

    def enrich_route(
        self,
        context: TransactionContext,
        waypoints: List[Waypoint]
    ) -> List[Waypoint]:
        """
        Main orchestration method
        Processes all waypoints with parallel agent execution

        Input Contract:
            - TransactionContext
            - List of preprocessed Waypoints

        Output Contract:
            - List of enriched Waypoints

        Args:
            context: Transaction context
            waypoints: List of waypoints to enrich

        Returns:
            List of enriched waypoints
        """
        context.log_stage_entry("orchestration")
        self.logger.log_stage_entry(
            "orchestration",
            context.transaction_id,
            waypoint_count=len(waypoints)
        )

        start_time = time.time()
        enriched_waypoints = []

        # Process waypoints in batches for controlled concurrency
        batches = self._create_batches(waypoints)

        for batch_idx, batch in enumerate(batches):
            self.logger.debug(
                f"Processing waypoint batch {batch_idx + 1}/{len(batches)}",
                transaction_id=context.transaction_id,
                batch_size=len(batch)
            )

            batch_results = self._process_waypoint_batch(context, batch)
            enriched_waypoints.extend(batch_results)

        duration_ms = int((time.time() - start_time) * 1000)

        self.logger.log_stage_exit(
            "orchestration",
            context.transaction_id,
            duration_ms=duration_ms,
            enriched_count=sum(1 for wp in enriched_waypoints if wp.is_enriched())
        )

        return enriched_waypoints

    def _process_waypoint_batch(
        self,
        context: TransactionContext,
        waypoints: List[Waypoint]
    ) -> List[Waypoint]:
        """
        Process multiple waypoints concurrently

        Args:
            context: Transaction context
            waypoints: Batch of waypoints to process

        Returns:
            List of enriched waypoints
        """
        futures: List[tuple[Waypoint, Future]] = []

        # Submit all waypoints in batch to thread pool
        for waypoint in waypoints:
            future = self.thread_pool.submit(
                self._enrich_single_waypoint,
                context,
                waypoint
            )
            futures.append((waypoint, future))

        # Collect results with timeout
        results = []
        timeout_seconds = (self.config.agent_timeout_ms + self.config.judge_timeout_ms + 1000) / 1000

        for waypoint, future in futures:
            try:
                enriched = future.result(timeout=timeout_seconds)
                results.append(enriched)
            except TimeoutError:
                self.logger.error(
                    f"Waypoint {waypoint.id} processing timeout",
                    transaction_id=context.transaction_id,
                    waypoint_id=waypoint.id
                )
                # Return waypoint without enrichment
                results.append(waypoint)
            except Exception as e:
                self.logger.error(
                    f"Waypoint {waypoint.id} processing error",
                    transaction_id=context.transaction_id,
                    waypoint_id=waypoint.id,
                    error=str(e),
                    exc_info=True
                )
                results.append(waypoint)

        return results

    def _enrich_single_waypoint(
        self,
        context: TransactionContext,
        waypoint: Waypoint
    ) -> Waypoint:
        """
        Run all agents for a single waypoint and select best content

        This is where the parallel agent execution happens:
        1. Launch YouTube, Spotify, History agents in parallel
        2. Wait for results (with timeout)
        3. Run Judge agent to select best content
        4. Assemble enrichment

        Args:
            context: Transaction context
            waypoint: Waypoint to enrich

        Returns:
            Enriched waypoint
        """
        start_time = time.time()

        self.logger.info(
            "Starting waypoint enrichment",
            transaction_id=context.transaction_id,
            waypoint_id=waypoint.id,
            location_name=waypoint.location_name
        )

        # Launch 3 agents in parallel
        agent_futures = {
            'youtube': self.thread_pool.submit(
                run_mock_youtube_agent,
                context.transaction_id,
                waypoint
            ),
            'spotify': self.thread_pool.submit(
                run_mock_spotify_agent,
                context.transaction_id,
                waypoint
            ),
            'history': self.thread_pool.submit(
                run_mock_history_agent,
                context.transaction_id,
                waypoint
            )
        }

        # Collect agent results with timeout
        agent_results = {}
        timeout_seconds = self.config.agent_timeout_ms / 1000

        for agent_name, future in agent_futures.items():
            try:
                result = future.result(timeout=timeout_seconds)
                agent_results[agent_name] = result
            except TimeoutError:
                self.logger.warning(
                    f"{agent_name} agent timeout",
                    transaction_id=context.transaction_id,
                    waypoint_id=waypoint.id,
                    timeout_ms=self.config.agent_timeout_ms
                )
                agent_results[agent_name] = create_timeout_result(
                    agent_name,
                    context.transaction_id,
                    waypoint.id,
                    self.config.agent_timeout_ms
                )
            except Exception as e:
                self.logger.error(
                    f"{agent_name} agent error",
                    transaction_id=context.transaction_id,
                    waypoint_id=waypoint.id,
                    error=str(e),
                    exc_info=True
                )
                agent_results[agent_name] = create_error_result(
                    agent_name,
                    context.transaction_id,
                    waypoint.id,
                    e
                )

        # Run Judge to select best content
        judge_decision = run_mock_judge(context, waypoint, agent_results)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Assemble enrichment
        waypoint.enrichment = WaypointEnrichment(
            selected_content=judge_decision.selected_content or create_fallback_content(waypoint),
            all_agent_results=agent_results,
            judge_decision=judge_decision,
            processing_time_ms=processing_time_ms
        )

        # Log completion
        successful_agents = sum(1 for r in agent_results.values() if r.is_successful())
        self.logger.log_waypoint_enrichment(
            transaction_id=context.transaction_id,
            waypoint_id=waypoint.id,
            location_name=waypoint.location_name,
            selected_type=waypoint.enrichment.selected_content.content_type.value,
            processing_time_ms=processing_time_ms,
            agent_success_count=successful_agents
        )

        return waypoint

    def _create_batches(self, waypoints: List[Waypoint]) -> List[List[Waypoint]]:
        """
        Split waypoints into batches for controlled concurrent processing

        Args:
            waypoints: All waypoints to process

        Returns:
            List of waypoint batches
        """
        batch_size = self.config.max_concurrent_waypoints
        return [
            waypoints[i:i + batch_size]
            for i in range(0, len(waypoints), batch_size)
        ]

    def shutdown(self):
        """Shutdown thread pool gracefully"""
        self.thread_pool.shutdown(wait=True)
