import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import subprocess
import time
from npm.production_npm_canon import ProductionNPMDeployer, ProductionBuildRecord
from npm.canonical_registry_mirror import CanonicalRegistryMirror
from sentinel.autonomous_orchestrator import AutonomousSentinelOrchestrator, SentinelRole
from security.malicious_dependency_detector import MaliciousDependencyDetector
import pandas as pd
import numpy as np

@pytest.fixture
def temporal_mock():
    mock = MagicMock()
    mock.anchor_event = AsyncMock(return_value="mocked_seal")
    return mock

@pytest.fixture
def phi_bus_mock():
    mock = MagicMock()
    mock.publish_metric = AsyncMock()
    mock.publish_event = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_production_npm_deployer(temporal_mock, phi_bus_mock):
    npm_manager_mock = MagicMock()
    npm_manager_mock.npm_install = AsyncMock(return_value={"returncode": 0, "phi_c": 0.95, "record": {"returncode": 0}})
    npm_manager_mock.npm_audit = AsyncMock(return_value={"returncode": 0, "phi_c": 0.96, "audit_summary": {"vulnerabilities": {"critical": 0}}})
    npm_manager_mock.npm_run_script = AsyncMock(side_effect=[
        {"returncode": 0, "phi_c": 0.94, "record": {"returncode": 0}}, # build
        {"returncode": 0, "phi_c": 0.95, "record": {"stdout": "All files | 95.0%"}} # test
    ])

    deployer = ProductionNPMDeployer(npm_manager=npm_manager_mock, temporal_chain=temporal_mock, phi_bus=phi_bus_mock)

    # 0.2*0.95 + 0.3*0.96 + 0.3*0.94 + 0.2*0.95 = 0.19 + 0.288 + 0.282 + 0.19 = 0.95
    record = await deployer.execute_production_build("/tmp/fake_project", {"registry": "fake-registry"})

    assert record.build_id is not None
    assert record.vulnerabilities_found == 0
    assert abs(sum(record.phi_c_scores.values()) / len(record.phi_c_scores) - 0.95) < 0.01
    temporal_mock.anchor_event.assert_called_once()
    phi_bus_mock.publish_metric.assert_called_once()

@pytest.mark.asyncio
async def test_canonical_registry_mirror(temporal_mock, phi_bus_mock):
    mirror = CanonicalRegistryMirror(temporal_chain=temporal_mock, phi_bus=phi_bus_mock)

    # Mock aiohttp response
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 200
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={
        "time": {"created": "2023-01-01T00:00:00.000Z"},
        "dist-tags": {"latest": "1.0.0"},
        "versions": {
            "1.0.0": {
                "_npmUser": {"name": "github-actions"},
                "dependencies": {},
                "dist": {"integrity": "sha512-fakehash"}
            }
        }
    })

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        metadata = await mirror.fetch_package_metadata("safe-pkg")
        assert metadata is not None
        assert metadata.name == "safe-pkg"
        assert metadata.version == "1.0.0"
        assert metadata.sha512 == "sha512-fakehash"
        assert metadata.publisher_verified is True
        assert metadata.phi_c_score > 0.8  # should be high due to verified publisher and valid integrity

@pytest.mark.asyncio
async def test_autonomous_orchestrator(temporal_mock, phi_bus_mock):
    class MockBuildSentinel:
        async def evaluate_artifact_phi_c(self, data):
            return 0.96

    class MockSecuritySentinel:
        async def scan_for_vulnerabilities(self, data):
            return {"critical": 0, "high": 0}

    sentinels = {
        SentinelRole.BUILD: MockBuildSentinel(),
        SentinelRole.SECURITY: MockSecuritySentinel()
    }

    orchestrator = AutonomousSentinelOrchestrator(temporal_chain=temporal_mock, phi_bus=phi_bus_mock, sentinels=sentinels)

    decision = await orchestrator.orchestrate_event("npm_install", {"package": "react"})

    assert decision.decision == "proceed"
    assert decision.consensus_phi_c > 0.95
    temporal_mock.anchor_event.assert_called_once()
    phi_bus_mock.publish_event.assert_called_once()

@pytest.mark.asyncio
async def test_malicious_dependency_detector(temporal_mock, phi_bus_mock):
    detector = MaliciousDependencyDetector(temporal_chain=temporal_mock, phi_bus=phi_bus_mock)

    # Mock extract features to return a safe feature set
    with patch.object(detector, "_extract_features", AsyncMock(return_value={
        "package_age_days": 400,
        "typosquatting_score": 0.0,
        "known_vulnerabilities": 0,
        "uses_eval": 0.0,
        "uses_child_process": 0.0,
        "obfuscation_score": 0.0
    })):
        assessment = await detector.assess_dependency("safe-pkg", "1.0.0")
        assert assessment.is_malicious is False
        assert assessment.risk_score < 0.3
        assert "✅ BAIXO RISCO: Pacote parece seguro para uso" in assessment.recommendations

    # Also test train_model to hit the "stratify fallback" behavior in continuous training scenarios
    # creating dummy data where only one class exists
    df = pd.DataFrame({
        "package_age_days": [10, 20],
        "typosquatting_score": [0, 0],
        "known_vulnerabilities": [0, 0],
        "uses_eval": [0, 0],
        "uses_child_process": [0, 0],
        "uses_network_calls": [0, 0],
        "uses_file_system_write": [0, 0],
        "obfuscation_score": [0, 0],
        "publisher_account_age_days": [10, 20],
        "download_count_log": [0, 0],
        "update_frequency_days": [0, 0],
        "dependency_count": [0, 0],
        "dev_dependency_count": [0, 0],
        "name_entropy": [0, 0],
        "contains_numbers": [0, 0],
        "maintainer_changes_count": [0, 0],
        "suspicious_version_jumps": [0, 0],
        "transitive_deps_count": [0, 0],
        "high_risk_transitive_deps": [0, 0],
        "circular_dependency_depth": [0, 0],
        "is_malicious": [True, True] # Single class to trigger stratify fallback
    })

    metrics = await detector.train_model(df)
    assert metrics is not None

def test_substrato_232_execution():
    result = subprocess.run(["python", "-m", "substrates.substrato_232_npm_canon_production"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "ARKHE Ω‑TEMP" in result.stdout
    assert "CANONICAL SEAL: f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2" in result.stdout
