#!/usr/bin/env python3
"""
bridge.py — Arkhe-SIE Bridge
Orquestrador principal que conecta SIE ao ecossistema Arkhe.
"""

import asyncio
import logging
from .sie_client import SIEClient, EncodeRequest, ScoreRequest, ExtractRequest
from .temporal_anchor import SIETemporalAnchor
from .guardian_monitor import SIEQualityMonitor
from .model_registry import SIEModelRegistry
from .mcp_tools import register_sie_tools

logger = logging.getLogger("arkhe.sie")

class ArkheSIEBridge:
    """Ponte entre SIE e Arkhe Safe Core."""

    def __init__(
        self,
        sie_endpoint: str = "http://localhost:9080",
        temporal_chain=None,
        guardian=None,
        mcp_server=None,
    ):
        self.sie = SIEClient(endpoint=sie_endpoint)
        self.anchor = SIETemporalAnchor(temporal_chain)
        self.monitor = SIEQualityMonitor(guardian)
        self.registry = SIEModelRegistry()
        self.mcp = mcp_server

        if self.mcp:
            register_sie_tools(self.mcp, self.sie, self.anchor, self.monitor)

    async def encode_safe(
        self,
        texts: list[str],
        model: str = "BAAI/bge-large-en-v1.5",
        pooling: str = "mean",
    ) -> dict:
        """Encode com validação de segurança e ancoragem."""
        request = EncodeRequest(texts=texts, model=model, pooling=pooling)

        start = asyncio.get_event_loop().time()
        response = await self.sie.encode(request)
        latency = (asyncio.get_event_loop().time() - start) * 1000

        phi_c = await self.monitor.validate_embeddings(texts, response.get("embeddings", []))
        await self.anchor.anchor_encode(
            {"texts": texts, "model": model, "pooling": pooling},
            response, latency, phi_c
        )

        response["arkhe_phi_c"] = phi_c
        response["arkhe_latency_ms"] = latency
        return response

    async def score_safe(
        self,
        query: str,
        documents: list[str],
        model: str = "BAAI/bge-reranker-v2-m3",
    ) -> dict:
        """Score com validação de segurança e ancoragem."""
        request = ScoreRequest(query=query, documents=documents, model=model)

        start = asyncio.get_event_loop().time()
        response = await self.sie.score(request)
        latency = (asyncio.get_event_loop().time() - start) * 1000

        phi_c = await self.monitor.validate_scores(query, documents, response.get("scores", []))
        await self.anchor.anchor_score(
            {"query": query, "documents": documents, "model": model},
            response, latency, phi_c
        )

        response["arkhe_phi_c"] = phi_c
        response["arkhe_latency_ms"] = latency
        return response

    async def extract_safe(
        self,
        text: str,
        entities: list[str],
        model: str = "Babelscape/rebel-large",
    ) -> dict:
        """Extract com validação de segurança e ancoragem."""
        request = ExtractRequest(text=text, entities=entities, model=model)

        start = asyncio.get_event_loop().time()
        response = await self.sie.extract(request)
        latency = (asyncio.get_event_loop().time() - start) * 1000

        phi_c = await self.monitor.validate_extractions(text, response.get("entities", {}))
        await self.anchor.anchor_extract(
            {"text": text, "entities": entities, "model": model},
            response, latency, phi_c
        )

        response["arkhe_phi_c"] = phi_c
        response["arkhe_latency_ms"] = latency
        return response