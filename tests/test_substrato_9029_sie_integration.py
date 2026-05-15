import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from arkhe_sie.sie_client import SIEClient, EncodeRequest, ScoreRequest, ExtractRequest
from arkhe_sie.temporal_anchor import SIETemporalAnchor
from arkhe_sie.guardian_monitor import SIEQualityMonitor
from arkhe_sie.model_registry import SIEModelRegistry
from arkhe_sie.bridge import ArkheSIEBridge

@pytest.fixture
def bridge():
    class MockTemporalChain:
        async def anchor_event(self, event_type: str, data: dict) -> str:
            return f"mock_seal"

    class MockGuardian:
        class Report:
            severity = 0.0

        def exorcise(self, text: str):
            return True, self.Report()

    return ArkheSIEBridge(
        temporal_chain=MockTemporalChain(),
        guardian=MockGuardian()
    )

@pytest.mark.asyncio
async def test_sie_client_encode():
    client = SIEClient()
    request = EncodeRequest(texts=["Hello world"])

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
        mock_post.return_value = mock_response

        response = await client.encode(request)

        assert "embeddings" in response
        assert response["embeddings"] == [[0.1, 0.2, 0.3]]

@pytest.mark.asyncio
async def test_sie_client_score():
    client = SIEClient()
    request = ScoreRequest(query="What is AI?", documents=["AI is artificial intelligence."])

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"scores": [0.95]}
        mock_post.return_value = mock_response

        response = await client.score(request)

        assert "scores" in response
        assert response["scores"] == [0.95]

@pytest.mark.asyncio
async def test_sie_client_extract():
    client = SIEClient()
    request = ExtractRequest(text="Apple is looking at buying U.K. startup for $1 billion", entities=["organization"])

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"entities": {"organization": ["Apple", "U.K. startup"]}}
        mock_post.return_value = mock_response

        response = await client.extract(request)

        assert "entities" in response
        assert response["entities"]["organization"] == ["Apple", "U.K. startup"]

@pytest.mark.asyncio
async def test_temporal_anchor():
    anchor = SIETemporalAnchor()
    event = await anchor.anchor_encode(
        request={"texts": ["test"]},
        response={"embeddings": [[0.1]]},
        latency_ms=10.0,
        phi_c=0.98
    )

    assert event.operation == "encode"
    assert event.phi_c == 0.98

@pytest.mark.asyncio
async def test_guardian_monitor_encode():
    monitor = SIEQualityMonitor()
    phi_c = await monitor.validate_embeddings(["test"], [[0.1, 0.2]])
    assert phi_c == 0.98

    # Degraded
    phi_c = await monitor.validate_embeddings(["test"], [[float('nan')]])
    assert phi_c == 0.3

@pytest.mark.asyncio
async def test_guardian_monitor_score():
    monitor = SIEQualityMonitor()
    phi_c = await monitor.validate_scores("query", ["doc1", "doc2"], [0.9, 0.1])
    assert phi_c == 0.96

@pytest.mark.asyncio
async def test_guardian_monitor_extract():
    monitor = SIEQualityMonitor()
    phi_c = await monitor.validate_extractions("Apple", {"organization": ["Apple"]})
    assert phi_c == 0.94

def test_model_registry():
    registry = SIEModelRegistry()
    model = registry.get_model("BAAI/bge-large-en-v1.5")
    assert model.primitive == "encode"

    extract_models = registry.list_by_primitive("extract")
    assert len(extract_models) == 1
    assert extract_models[0].name == "Babelscape/rebel-large"

@pytest.mark.asyncio
async def test_bridge_encode_safe(bridge):
    with patch.object(bridge.sie, 'encode') as mock_encode:
        mock_encode.return_value = {"embeddings": [[0.1, 0.2]]}
        response = await bridge.encode_safe(texts=["Hello"])

        assert "arkhe_phi_c" in response
        assert "arkhe_latency_ms" in response
        assert response["embeddings"] == [[0.1, 0.2]]

@pytest.mark.asyncio
async def test_bridge_score_safe(bridge):
    with patch.object(bridge.sie, 'score') as mock_score:
        mock_score.return_value = {"scores": [0.99]}
        response = await bridge.score_safe(query="q", documents=["d1"])

        assert "arkhe_phi_c" in response
        assert "arkhe_latency_ms" in response
        assert response["scores"] == [0.99]

@pytest.mark.asyncio
async def test_bridge_extract_safe(bridge):
    with patch.object(bridge.sie, 'extract') as mock_extract:
        mock_extract.return_value = {"entities": {"org": ["A"]}}
        response = await bridge.extract_safe(text="t", entities=["org"])

        assert "arkhe_phi_c" in response
        assert "arkhe_latency_ms" in response
        assert response["entities"]["org"] == ["A"]
