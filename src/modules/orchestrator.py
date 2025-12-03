"""
Module 4: Orchestrator
Coordinates parallel agent execution for each waypoint
This is the central nervous system of the multi-agent platform
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import List, Dict, Callable, Optional
import threading

from src.models import (
    TransactionContext,
    Waypoint,
    AgentResult,
    WaypointEnrichment,
    JudgeDecision,
    ContentItem,
    ContentType,
    AgentStatus,
    create_fallback_content,
    create_timeout_result,
    create_error_result
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
        1. Launch YouTube (video), Music (YouTube songs), History agents in parallel
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
                self._run_youtube_agent,
                context.transaction_id,
                waypoint
            ),
            'music': self.thread_pool.submit(
                self._run_music_agent,
                context.transaction_id,
                waypoint
            ),
            'history': self.thread_pool.submit(
                self._run_history_agent,
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
        judge_decision = self._run_judge(context, waypoint, agent_results)

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

    def _run_youtube_agent(
        self,
        transaction_id: str,
        waypoint: Waypoint
    ) -> AgentResult:
        """
        Execute YouTube agent
        MOCK IMPLEMENTATION - will be replaced with real agent call

        Args:
            transaction_id: Transaction ID
            waypoint: Waypoint to process

        Returns:
            AgentResult from YouTube agent
        """
        start_time = time.time()

        self.logger.log_agent_start(
            "youtube",
            transaction_id,
            waypoint.id,
            search_query=waypoint.agent_context.youtube_query if waypoint.agent_context else ""
        )

        # MOCK: Simulate API call delay
        time.sleep(0.5)

        # MOCK: Create fake result
        content = ContentItem(
            content_type=ContentType.VIDEO,
            title=f"Video about {waypoint.location_name}",
            description=f"A virtual tour of {waypoint.location_name}",
            relevance_score=0.75,
            url=f"https://youtube.com/watch?v=mock_{waypoint.id}",
            metadata={"source": "mock"}
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        result = AgentResult(
            agent_name="youtube",
            transaction_id=transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=content,
            execution_time_ms=execution_time_ms
        )

        self.logger.log_agent_completion(
            "youtube",
            transaction_id,
            waypoint.id,
            result.status.value,
            execution_time_ms,
            relevance_score=content.relevance_score
        )

        return result

    def _run_music_agent(
        self,
        transaction_id: str,
        waypoint: Waypoint
    ) -> AgentResult:
        """
        Execute Music agent (searches YouTube for songs/music videos)
        MOCK IMPLEMENTATION - will be replaced with real agent call

        Args:
            transaction_id: Transaction ID
            waypoint: Waypoint to process

        Returns:
            AgentResult from Music agent
        """
        start_time = time.time()

        self.logger.log_agent_start(
            "music",
            transaction_id,
            waypoint.id,
            search_query=waypoint.agent_context.music_query if waypoint.agent_context else ""
        )

        # MOCK: Simulate API call delay
        time.sleep(0.4)

        # MOCK: Create fake result
        content = ContentItem(
            content_type=ContentType.SONG,
            title=f"Song for {waypoint.location_name}",
            description="A fitting soundtrack for this location (from YouTube Music)",
            relevance_score=0.82,
            url=f"https://youtube.com/watch?v=mock_music_{waypoint.id}",
            metadata={"source": "mock", "platform": "YouTube Music"}
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        result = AgentResult(
            agent_name="music",
            transaction_id=transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=content,
            execution_time_ms=execution_time_ms
        )

        self.logger.log_agent_completion(
            "music",
            transaction_id,
            waypoint.id,
            result.status.value,
            execution_time_ms,
            relevance_score=content.relevance_score
        )

        return result

    def _run_history_agent(
        self,
        transaction_id: str,
        waypoint: Waypoint
    ) -> AgentResult:
        """
        Execute History agent
        MOCK IMPLEMENTATION - will be replaced with real agent call

        Args:
            transaction_id: Transaction ID
            waypoint: Waypoint to process

        Returns:
            AgentResult from History agent
        """
        start_time = time.time()

        self.logger.log_agent_start(
            "history",
            transaction_id,
            waypoint.id,
            search_query=waypoint.agent_context.history_query if waypoint.agent_context else ""
        )

        # MOCK: Simulate API call delay
        time.sleep(0.3)

        # MOCK: Create fake result
        content = ContentItem(
            content_type=ContentType.HISTORY,
            title=f"History of {waypoint.location_name}",
            description=f"Fascinating historical facts about {waypoint.location_name} and its significance.",
            relevance_score=0.68,
            url=None,
            metadata={"source": "mock"}
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        result = AgentResult(
            agent_name="history",
            transaction_id=transaction_id,
            waypoint_id=waypoint.id,
            status=AgentStatus.SUCCESS,
            content=content,
            execution_time_ms=execution_time_ms
        )

        self.logger.log_agent_completion(
            "history",
            transaction_id,
            waypoint.id,
            result.status.value,
            execution_time_ms,
            relevance_score=content.relevance_score
        )

        return result

    def _run_judge(
        self,
        context: TransactionContext,
        waypoint: Waypoint,
        agent_results: Dict[str, AgentResult]
    ) -> JudgeDecision:
        """
        Execute Judge agent to select best content
        MOCK IMPLEMENTATION - will be replaced with real agent call

        Args:
            context: Transaction context
            waypoint: Waypoint being judged
            agent_results: Results from all agents

        Returns:
            JudgeDecision with selected content
        """
        start_time = time.time()

        self.logger.debug(
            "Judge evaluation started",
            transaction_id=context.transaction_id,
            waypoint_id=waypoint.id
        )

        try:
            # MOCK: Simple selection based on relevance score
            # Real Judge will use LLM or sophisticated decision logic

            best_agent = None
            best_score = 0.0
            scores = {}

            for agent_name, result in agent_results.items():
                if result.is_successful() and result.content:
                    score = result.content.relevance_score
                    scores[agent_name] = score
                    if score > best_score:
                        best_score = score
                        best_agent = agent_name
                else:
                    scores[agent_name] = 0.0

            if best_agent:
                selected_content = agent_results[best_agent].content
                reasoning = f"Selected {best_agent} with highest relevance score ({best_score:.2f})"
            else:
                # All agents failed - use fallback
                selected_content = create_fallback_content(waypoint)
                reasoning = "All agents failed, using fallback content"
                best_agent = "fallback"
                best_score = 0.0

            decision_time_ms = int((time.time() - start_time) * 1000)

            decision = JudgeDecision(
                winner=best_agent,
                reasoning=reasoning,
                confidence_score=best_score,
                individual_scores=scores,
                decision_time_ms=decision_time_ms,
                tie_breaker_applied=False,
                selected_content=selected_content
            )

            self.logger.log_judge_decision(
                transaction_id=context.transaction_id,
                waypoint_id=waypoint.id,
                winner=best_agent,
                confidence=best_score,
                reasoning=reasoning
            )

            return decision

        except Exception as e:
            self.logger.error(
                "Judge error, using fallback",
                transaction_id=context.transaction_id,
                waypoint_id=waypoint.id,
                error=str(e)
            )

            # Fallback decision
            return JudgeDecision(
                winner="fallback",
                reasoning=f"Judge error: {str(e)}",
                confidence_score=0.0,
                individual_scores={},
                decision_time_ms=0,
                tie_breaker_applied=False,
                selected_content=create_fallback_content(waypoint)
            )

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
