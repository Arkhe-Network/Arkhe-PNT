import pytest
import asyncio
from arkhe_tv.audience_bridge.api import AudienceAggregator, BroadcasterMapping

@pytest.mark.asyncio
async def test_aggregator_initialization():
    aggregator = AudienceAggregator("test_id", "test_token")
    assert aggregator.twitch_client_id == "test_id"
    assert "globo" in aggregator.BROADCASTER_MAPPINGS

@pytest.mark.asyncio
async def test_get_share_of_tv():
    aggregator = AudienceAggregator("test_id", "test_token")

    # Mock cache data
    class MockSnapshot:
        def __init__(self, total_viewers):
            self.total_viewers = total_viewers

    aggregator._cache = {
        "audience_globo": MockSnapshot(500),
        "audience_sbt": MockSnapshot(300),
        "audience_band": MockSnapshot(200)
    }

    share = aggregator.get_share_of_tv("globo", 1000)
    assert share == 50.0  # 500 / 1000 * 100
