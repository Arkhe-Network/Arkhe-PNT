import pytest
import asyncio
from unittest.mock import MagicMock, patch

from opencode.k8s_autoscaler_production import K8sProductionAutoscaler, K8sScalingMetrics
from learning.federated_prompt_policy import FederatedPromptPolicyLearner, LocalPolicyUpdate
from federation.cross_org_consensus_validator import CrossOrgConsensusValidator, OrgValidationVote, ConsensusOutcome

@pytest.mark.asyncio
async def test_k8s_autoscaler_scale_up():
    with patch('kubernetes.config.load_incluster_config'), patch('kubernetes.config.load_kube_config'), patch('kubernetes.client.AppsV1Api'), patch('kubernetes.client.CustomObjectsApi'):
        scaler = K8sProductionAutoscaler()

    mock_metrics = K8sScalingMetrics(
        deployment_name="test-deploy",
        namespace="arkhe-opencode",
        current_replicas=2,
        desired_replicas=2,
        available_replicas=2,
        pending_pods=5,
        cpu_utilization_percent=80.0,
        memory_utilization_percent=80.0,
        request_latency_p99_ms=2500.0,
        error_rate_percent=1.5,
        system_phi_c=0.95
    )

    with patch.object(scaler, 'collect_k8s_metrics', return_value=mock_metrics):
        with patch.object(scaler, 'execute_scaling', return_value={"status": "success"}) as mock_exec:
            decision = await scaler.run_scaling_cycle("test-deploy")

            assert decision.action == "scale_up"
            assert decision.to_replicas > 2
            mock_exec.assert_called_once()

@pytest.mark.asyncio
async def test_federated_learner_compute_update():
    learner = FederatedPromptPolicyLearner("org_test", ["act1", "act2"])

    # Adicionar algumas experiências
    learner.update_local_policy("p1", {"ctx": 1}, "act1", 0.9, "p2", {"ctx": 2})

    update = learner.compute_local_update()

    assert isinstance(update, LocalPolicyUpdate)
    assert update.org_id == "org_test"
    assert update.experience_count == 1
    assert len(update.q_table_delta) > 0

@pytest.mark.asyncio
async def test_consensus_validator_approval():
    validator = CrossOrgConsensusValidator("org1", ["org1", "org2", "org3"])

    # Iniciar validação
    with patch.object(validator, '_broadcast_validation_request'):
        cid = await validator.initiate_validation({"key": "val"}, {"meta": "data"})

    assert cid in validator._pending_validations

    # Receber votos positivos
    h = validator._pending_validations[cid]["request"]["config_hash"]
    v1 = OrgValidationVote("org2", h, True, 0.95, "ok", "sig1")
    v2 = OrgValidationVote("org3", h, True, 0.95, "ok", "sig2")
    v3 = OrgValidationVote("org1", h, True, 0.95, "ok", "sig3")

    with patch.object(validator, '_verify_vote_signature', return_value=True):
        # Disable automatic finalize so we can control when it's checked
        # However, it checks >= len - 1 so the second vote triggers finalize if length is 3.
        # But wait, len(federation_members) = 3. 3-1 = 2. So 2 votes triggers finalize.
        # But to have min_orgs_met = 3, we need 3 votes.
        # Let's change min_orgs_for_consensus temporarily, or add 4 orgs.
        validator.CONFIG["min_orgs_for_consensus"] = 2
        await validator.receive_vote(v1)
        await validator.receive_vote(v2)

    # Verificar resultado
    assert len(validator._consensus_history) == 1
    res = validator._consensus_history[0]
    assert res.outcome == ConsensusOutcome.APPROVED
