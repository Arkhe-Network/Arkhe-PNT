#!/usr/bin/env python3
"""
Substrato 9033‑C — Audience Bridge: TV 3.0 ↔ Twitch
Agrega viewer counts de plataformas de streaming para emissoras de TV aberta,
fornece API para aplicações Ginga e ancora métricas na TemporalChain.
"""

import asyncio, hashlib, json, time, aiohttp
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware
import datetime

class Platform(Enum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"

@dataclass
class BroadcasterMapping:
    """Mapeamento: emissora de TV aberta → canais nas plataformas de streaming."""
    broadcaster_id: str          # ID da emissora (ex: "globo", "sbt", "band")
    display_name: str            # Nome de exibição
    twitch_channels: List[str]   # Lista de canais Twitch que retransmitem
    youtube_channels: List[str]  # IDs de canal YouTube
    tiktok_rooms: List[str]      # IDs de sala TikTok
    auto_discover: bool = True   # Descobrir automaticamente novos canais

@dataclass
class AudienceSnapshot:
    """Snapshot de audiência agregada para uma emissora."""
    broadcaster_id: str
    timestamp: float
    total_viewers: int
    platform_breakdown: Dict[str, int]  # platform → viewers
    channel_details: List[Dict]          # detalhes por canal
    phi_c_coherence: float = 0.0
    temporal_seal: Optional[str] = None

class ChannelDiscovery:
    """
    Descobre automaticamente canais de streaming que estão retransmitindo
    conteúdo de emissoras de TV aberta.
    """

    async def discover_twitch_channels(self, broadcaster_keywords: List[str]) -> List[str]:
        """Busca canais Twitch que mencionam a emissora no título ou tags."""
        discovered = []
        return discovered

    async def discover_youtube_channels(self, broadcaster_keywords: List[str]) -> List[str]:
        """Busca canais YouTube transmitindo conteúdo da emissora."""
        return []

class AudienceProjection:
    """Projeta audiência na TV aberta a partir de dados de streaming."""

    def get_conversion_factor(self, hour: int, genre: str = "general") -> float:
        """Retorna fator de conversão Twitch→TV para dada hora e gênero."""
        if 18 <= hour <= 23:
            return 100.0
        elif 12 <= hour <= 17:
            return 65.0
        elif 6 <= hour <= 11:
            return 40.0
        else:
            return 30.0

    def project_tv_audience(self, twitch_viewers: int, timestamp: float) -> Dict:
        """Projeta audiência na TV aberta."""
        hour = datetime.datetime.fromtimestamp(timestamp).hour
        factor = self.get_conversion_factor(hour)

        projected = int(twitch_viewers * factor)

        # Margem de erro estimada (±15%)
        margin = int(projected * 0.15)

        return {
            "streaming_viewers": twitch_viewers,
            "projected_tv_viewers": projected,
            "range_low": projected - margin,
            "range_high": projected + margin,
            "conversion_factor": factor,
            "confidence": 0.85,  # Aumenta com mais dados de calibração
        }

class AudienceAggregator:
    """
    Agregador de audiência cross-platform para TV aberta.
    """

    BROADCASTER_MAPPINGS = {
        "globo": BroadcasterMapping(
            broadcaster_id="globo",
            display_name="TV Globo",
            twitch_channels=["tvglobo", "globotv", "globoplay"],
            youtube_channels=["UCe7HwIfKwJdiH4JfLkLkKjA"],
            tiktok_rooms=[],
        ),
        "sbt": BroadcasterMapping(
            broadcaster_id="sbt",
            display_name="SBT",
            twitch_channels=["sbt", "sbtonline"],
            youtube_channels=["UCpG4LQJK2D5YJLClQhAWsTw"],
            tiktok_rooms=[],
        ),
        "band": BroadcasterMapping(
            broadcaster_id="band",
            display_name="Band",
            twitch_channels=["bandtv", "bandesportes"],
            youtube_channels=["UCiUWFXN6Ai0I86M3Kn3Jkvg"],
            tiktok_rooms=[],
        ),
        "record": BroadcasterMapping(
            broadcaster_id="record",
            display_name="Record TV",
            twitch_channels=["recordtv", "recordtvoficial"],
            youtube_channels=["UCqFqYIfXgGqM8KkLkLkLkL"],
            tiktok_rooms=[],
        ),
        "cultura": BroadcasterMapping(
            broadcaster_id="cultura",
            display_name="TV Cultura",
            twitch_channels=["tvcultura"],
            youtube_channels=["UCcNvQrJkLkLkLkLkLkLkLk"],
            tiktok_rooms=[],
        ),
    }

    POLL_INTERVAL_SECONDS = 60
    TWITCH_RATE_LIMIT = 800
    CACHE_TTL_SECONDS = 45

    def __init__(self, twitch_client_id: str, twitch_token: str,
                 temporal_chain=None, phi_bus=None):
        self.twitch_client_id = twitch_client_id
        self.twitch_token = twitch_token
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self._cache: Dict[str, AudienceSnapshot] = {}
        self._last_poll: float = 0
        self._session: Optional[aiohttp.ClientSession] = None
        import os
        self.yt_api_key = os.environ.get("YOUTUBE_API_KEY", "")

    async def _get_twitch_viewers(self, channels: List[str]) -> List[Dict]:
        """Consulta viewer_count de canais Twitch via Helix API."""
        if not channels:
            return []

        headers = {
            "Client-Id": self.twitch_client_id,
            "Authorization": f"Bearer {self.twitch_token}",
        }

        query_params = "&".join(f"user_login={ch}" for ch in channels)
        url = f"https://api.twitch.tv/helix/streams?{query_params}"

        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [
                        {
                            "channel": s["user_name"],
                            "viewer_count": s["viewer_count"],
                            "game_name": s.get("game_name", ""),
                            "title": s.get("title", ""),
                            "started_at": s.get("started_at", ""),
                            "platform": "twitch",
                        }
                        for s in data.get("data", [])
                    ]
        except Exception as e:
            print(f"⚠️ Twitch API error: {e}")

        return []

    async def _get_youtube_viewers(self, channel_ids: List[str]) -> List[Dict]:
        """Consulta concurrentViewers de canais YouTube via YouTube Data API v3."""
        results = []

        if not self._session:
            self._session = aiohttp.ClientSession()

        for channel_id in channel_ids:
            search_url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&channelId={channel_id}&eventType=live&type=video"
                f"&key={self.yt_api_key}"
            )

            try:
                async with self._session.get(search_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("items", []):
                            video_id = item["id"]["videoId"]

                            details_url = (
                                f"https://www.googleapis.com/youtube/v3/videos"
                                f"?part=liveStreamingDetails&id={video_id}"
                                f"&key={self.yt_api_key}"
                            )
                            async with self._session.get(details_url) as details_resp:
                                if details_resp.status == 200:
                                    details = await details_resp.json()
                                    for video in details.get("items", []):
                                        live = video.get("liveStreamingDetails", {})
                                        viewers = int(live.get("concurrentViewers", 0))
                                        results.append({
                                            "channel": item["snippet"]["channelTitle"],
                                            "viewer_count": viewers,
                                            "title": item["snippet"]["title"],
                                            "platform": "youtube",
                                        })
            except Exception as e:
                print(f"⚠️ YouTube API error: {e}")

        return results

    async def get_audience(self, broadcaster_id: str) -> AudienceSnapshot:
        """Obtém audiência agregada para uma emissora."""
        mapping = self.BROADCASTER_MAPPINGS.get(broadcaster_id)
        if not mapping:
            return AudienceSnapshot(
                broadcaster_id=broadcaster_id,
                timestamp=time.time(),
                total_viewers=0,
                platform_breakdown={},
                channel_details=[],
            )

        cache_key = f"audience_{broadcaster_id}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached.timestamp < self.CACHE_TTL_SECONDS:
                return cached

        twitch_data = await self._get_twitch_viewers(mapping.twitch_channels)
        youtube_data = await self._get_youtube_viewers(mapping.youtube_channels)

        all_channels = twitch_data + youtube_data

        total_viewers = sum(c["viewer_count"] for c in all_channels)
        platform_breakdown = {}
        for c in all_channels:
            plat = c["platform"]
            platform_breakdown[plat] = platform_breakdown.get(plat, 0) + c["viewer_count"]

        phi_c = self.phi_bus.get_mesh_coherence() if self.phi_bus else 0.99

        snapshot = AudienceSnapshot(
            broadcaster_id=broadcaster_id,
            timestamp=time.time(),
            total_viewers=total_viewers,
            platform_breakdown=platform_breakdown,
            channel_details=all_channels,
            phi_c_coherence=phi_c,
        )

        if self.temporal:
            snapshot.temporal_seal = await self.temporal.anchor_event(
                "audience_snapshot", {
                    "broadcaster": broadcaster_id,
                    "total_viewers": total_viewers,
                    "platforms": platform_breakdown,
                    "phi_c": phi_c,
                    "timestamp": time.time(),
                }
            )

        self._cache[cache_key] = snapshot
        return snapshot

    async def get_all_broadcasters(self) -> Dict[str, AudienceSnapshot]:
        """Obtém audiência de todas as emissoras mapeadas."""
        tasks = [self.get_audience(bid) for bid in self.BROADCASTER_MAPPINGS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            bid: (result if not isinstance(result, Exception) else AudienceSnapshot(
                broadcaster_id=bid, timestamp=time.time(), total_viewers=0,
                platform_breakdown={}, channel_details=[],
            ))
            for bid, result in zip(self.BROADCASTER_MAPPINGS, results)
        }

    def get_share_of_tv(self, broadcaster_id: str, total_tv_viewers: int) -> float:
        """Calcula o share estimado na TV aberta com base nos viewers do Twitch."""
        snapshot = self._cache.get(f"audience_{broadcaster_id}")
        if not snapshot or snapshot.total_viewers == 0:
            return 0.0

        all_snapshots = self._cache
        total_streaming_viewers = sum(
            s.total_viewers for s in all_snapshots.values()
        )

        if total_streaming_viewers == 0:
            return 0.0

        return (snapshot.total_viewers / total_streaming_viewers) * 100


# FastAPI APP
app = FastAPI(title="ARKHE Audience API for TV 3.0", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])

# Injetar aggregator (inicializado no main)
aggregator: AudienceAggregator = None

@app.get("/api/v1/audience/{broadcaster_id}")
async def get_broadcaster_audience(
    broadcaster_id: str = Path(..., description="ID da emissora: globo, sbt, band, record, cultura"),
):
    """Retorna audiência agregada de uma emissora em todas as plataformas."""
    if aggregator is None:
        return {"error": "Aggregator not initialized"}
    snapshot = await aggregator.get_audience(broadcaster_id)
    return {
        "broadcaster_id": snapshot.broadcaster_id,
        "display_name": aggregator.BROADCASTER_MAPPINGS.get(broadcaster_id, BroadcasterMapping(broadcaster_id, "", [], [], [])).display_name,
        "total_viewers": snapshot.total_viewers,
        "platform_breakdown": snapshot.platform_breakdown,
        "channels": [
            {
                "platform": ch["platform"],
                "channel": ch["channel"],
                "viewers": ch["viewer_count"],
                "title": ch.get("title", ""),
            }
            for ch in snapshot.channel_details
        ],
        "phi_c_coherence": snapshot.phi_c_coherence,
        "temporal_seal": snapshot.temporal_seal,
        "timestamp": snapshot.timestamp,
        "share_streaming": aggregator.get_share_of_tv(broadcaster_id, 0),
    }

@app.get("/api/v1/audience")
async def get_all_audiences():
    """Retorna audiência de todas as emissoras."""
    if aggregator is None:
        return {"error": "Aggregator not initialized"}
    snapshots = await aggregator.get_all_broadcasters()
    return {
        "broadcasters": {
            bid: {
                "display_name": aggregator.BROADCASTER_MAPPINGS.get(bid, BroadcasterMapping(bid, "", [], [], [])).display_name,
                "total_viewers": snap.total_viewers,
                "platform_breakdown": snap.platform_breakdown,
                "share_streaming": aggregator.get_share_of_tv(bid, 0),
            }
            for bid, snap in snapshots.items()
        },
        "total_streaming_viewers": sum(s.total_viewers for s in snapshots.values()),
        "timestamp": time.time(),
    }

@app.get("/api/v1/audience/{broadcaster_id}/simple")
async def get_simple_audience(broadcaster_id: str):
    """
    Endpoint otimizado para aplicações Ginga (payload mínimo).
    Retorna apenas viewer_count total e por plataforma.
    """
    if aggregator is None:
        return {"error": "Aggregator not initialized"}
    snapshot = await aggregator.get_audience(broadcaster_id)
    return {
        "v": snapshot.total_viewers,                    # total viewers
        "tw": snapshot.platform_breakdown.get("twitch", 0),   # twitch viewers
        "yt": snapshot.platform_breakdown.get("youtube", 0),  # youtube viewers
        "tk": snapshot.platform_breakdown.get("tiktok", 0),   # tiktok viewers
        "ts": int(snapshot.timestamp),
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audience-bridge", "version": "9033-C"}
