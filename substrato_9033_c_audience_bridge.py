#!/usr/bin/env python3
"""
Launcher / Demo para Substrato 9033-C — Audience Bridge: TV 3.0 ↔ Twitch
"""
import asyncio
from arkhe_tv.audience_bridge.api import app, AudienceAggregator

async def main():
    print("Iniciando Substrato 9033-C: Audience Bridge: TV 3.0 ↔ Twitch")

    import arkhe_tv.audience_bridge.api as api_module

    # Initialize aggregator
    api_module.aggregator = AudienceAggregator(
        twitch_client_id="test_client_id",
        twitch_token="test_token"
    )

    print("✅ Módulo inicializado.")

if __name__ == "__main__":
    asyncio.run(main())
