import pytest
from substrates.substrato_infinity_kardashev_ii import (
    CMVPSubmissionPackageV2,
    AgentPentestFramework,
    ByzantineFaultSimulator,
    EPController,
    KardashevIITransceiverV3,
    KardashevIINetworkV3,
)

def test_cmvp_submission_package():
    package = CMVPSubmissionPackageV2()
    submission = package.generate_full_submission(fixed_timestamp=1234567890.0)
    assert submission["overall_compliance"] is True
    assert "canonical_seal" in submission
    assert submission["areas"]["Self-Tests"]["details"]["power_up_tests"]["dilithium_kat"] == "PASS"

def test_agent_pentest_framework():
    framework = AgentPentestFramework()
    results = framework.run_full_pentest("test_agent_1")
    assert len(results) == 7
    summary = framework.get_summary()
    assert summary["total_blocked"] == 7
    assert summary["production_ready"] is True

def test_byzantine_fault_simulator():
    sim = ByzantineFaultSimulator(total_nodes=7, byzantine_nodes=2)
    result = sim.run_simulation(rounds=10)
    assert result["total_nodes"] == 7
    assert result["byzantine_nodes"] == 2
    assert result["within_tolerance"] is True

def test_ep_controller():
    controller = EPController()
    ep = controller.generate_ep("left")
    assert ep.chirality == "left"
    ep_looped = controller.encircle_ep(ep, "clockwise")
    assert ep_looped.eigenvalue_a == ep.eigenvalue_b
    assert ep_looped.eigenvalue_b == ep.eigenvalue_a

def test_kardashev_ii_network():
    net = KardashevIINetworkV3()
    net.register_node("emissor")
    net.register_node("receptor")
    received = net.broadcast_message("emissor", "TEST PAYLOAD")
    assert len(received) == 1
    assert received[0]["receiver"] == "receptor"
    assert received[0]["decoded"]["payload"] == "TEST PAYLOAD"
    assert received[0]["decoded"]["integrity_verified"] is True
