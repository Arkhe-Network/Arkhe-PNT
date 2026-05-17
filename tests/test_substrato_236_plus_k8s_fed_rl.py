import pytest
import os
import json
import asyncio
from substrates.substrato_236_plus_k8s_fed_rl import (
    OpenCodeAutoScalerK8s, ScalingMetrics, ScaleDirection,
    PromptRLOptimizer, PromptExperience,
    FederatedPromptRLAggregator, FederatedPromptRLOptimizer, FederatedPromptUpdate,
    CrossOrgConsensusValidator, ConfigFederationServiceWithConsensus, ConfigVisibility
)

class MockTemporalChain:
    """Mock for TemporalChain anchoring."""
    async def anchor_event(self, event_type: str, data: dict):
        return f"mock_seal_{event_type}_{hash(str(data))}"

def test_k8s_autoscaler():
    scaler = OpenCodeAutoScalerK8s()
    # It should default to mock since k8s is likely not available in the test runner

    # Force a scale up decision
    metrics = ScalingMetrics(
        active_sessions=100, pending_prompts=50, avg_latency_ms=3000,
        system_phi_c=0.95, token_usage_rate=0.8, worker_health_ratio=0.85,
        cpu_percent=90, memory_percent=90, pod_count=2
    )
    decision = scaler.evaluate_scaling_policy(metrics)
    assert decision.direction == ScaleDirection.UP
    assert decision.target_replicas > 2

    scaler.execute_scaling(decision)
    assert scaler._current_replicas == decision.target_replicas

def test_prompt_rl_optimizer():
    optimizer = PromptRLOptimizer()
    context = {"domain": "test"}
    final_prompt, stats = optimizer.optimize_prompt("Hello", context, max_iterations=3)

    assert "iterations" in stats
    assert "final_phi_c" in stats
    assert len(optimizer._experience_buffer) > 0

def test_federated_rl_aggregator():
    aggregator = FederatedPromptRLAggregator()

    # Valid update
    update = FederatedPromptUpdate(
        organization_id="org_test", policy_weights={"state1": [0.1, 0.2]},
        action_space=["action1", "action2"], training_episodes=10,
        avg_reward=0.5, avg_phi_c=0.9, sample_count=100, phi_c_score=0.95
    )
    update.pqc_signature = aggregator._sign_update(update)
    assert aggregator.submit_local_update(update) is True

    # Aggregate
    global_policy = aggregator.aggregate_updates()
    assert "state1" in global_policy

def test_cross_org_consensus():
    validator = CrossOrgConsensusValidator()
    validator.register_organization("orgA", 0.95)
    validator.register_organization("orgB", 0.90)
    validator.register_organization("orgC", 0.85)

    config_id = "config_1"

    # Two approvals out of three should reach consensus
    validator.cast_vote("orgA", config_id, True, "looks good")
    validator.cast_vote("orgB", config_id, True, "approved")

    result = validator._check_consensus(config_id)
    assert result["status"] == "approved"
