import pytest
import asyncio
from unittest.mock import MagicMock, patch

from security.hsm_pqc_signer import HSMConfig
from orchestration.guardrail_pipeline_orchestrator import GuardrailPipelineOrchestrator, GuardrailStatus

@pytest.fixture
def mock_hsm_config():
    return HSMConfig(
        pkcs11_library="/usr/lib/libsofthsm2.so",
        slot_id=1,
        key_label="substrate",
        pin="1234",
        session_timeout=300
    )

@pytest.fixture
def mock_temporal_chain():
    class MockTemporalChain:
        async def anchor_event(self, event_type, data):
            return "mock_seal"
    return MockTemporalChain()

@pytest.fixture
def mock_phi_bus():
    class MockPhiBus:
        async def publish_metric(self, metric_name, data):
            pass
    return MockPhiBus()

@pytest.mark.asyncio
async def test_guardrail_pipeline_benign_reaction(mock_hsm_config, mock_temporal_chain, mock_phi_bus):
    orchestrator = GuardrailPipelineOrchestrator(
        hsm_config=mock_hsm_config,
        temporal_chain=mock_temporal_chain,
        phi_bus=mock_phi_bus
    )

    # Mock Seccomp execution to return success
    orchestrator.seccomp_runner.run_reaction_sandboxed = MagicMock(return_value={
        "success": True,
        "output_molecule": {"atoms": [{"phi_c": 0.9}]}
    })

    # Mock HSM Signer
    orchestrator._hsm_healthy = True

    input_molecules = [{"atoms": [{"phi_c": 0.95}]}]
    reaction_code = "result = sum([1, 2, 3])"

    result = await orchestrator.execute_reaction_pipeline(
        reaction_code=reaction_code,
        input_molecules=input_molecules,
        reaction_name="BenignReaction"
    )

    assert result.overall_status == GuardrailStatus.PASSED
    assert len(result.guardrail_checks) == 4

@pytest.mark.asyncio
async def test_guardrail_pipeline_malicious_reaction(mock_hsm_config, mock_temporal_chain, mock_phi_bus):
    orchestrator = GuardrailPipelineOrchestrator(
        hsm_config=mock_hsm_config,
        temporal_chain=mock_temporal_chain,
        phi_bus=mock_phi_bus
    )

    input_molecules = [{"atoms": [{"phi_c": 0.95}]}]
    reaction_code = "import os\nos.system('rm -rf /')"

    result = await orchestrator.execute_reaction_pipeline(
        reaction_code=reaction_code,
        input_molecules=input_molecules,
        reaction_name="MaliciousReaction"
    )

    assert result.overall_status == GuardrailStatus.FAILED

    # Check that AST validation failed or it failed early due to HSM
    if len(result.guardrail_checks) > 2:
        ast_check = next(c for c in result.guardrail_checks if c.guardrail_name == "ast_ml_validation")
        assert ast_check.status == GuardrailStatus.FAILED
