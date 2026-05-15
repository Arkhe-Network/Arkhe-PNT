#!/usr/bin/env python3
"""
temporal_anchor.py — Ancoragem de operações SIE na TemporalChain
Cada encode, score e extract gera um evento imutável com selo SHA3-256.
"""

import hashlib
import json
import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class SIEAuditEvent:
    operation: str  # "encode", "score", "extract"
    model: str
    input_hash: str
    output_hash: str
    latency_ms: float
    phi_c: float
    temporal_seal: str

class SIETemporalAnchor:
    """Ancora operações SIE na TemporalChain."""

    def __init__(self, temporal_chain=None):
        self.temporal = temporal_chain

    async def anchor_encode(
        self,
        request: dict,
        response: dict,
        latency_ms: float,
        phi_c: float,
    ) -> SIEAuditEvent:
        input_hash = hashlib.sha3_256(
            json.dumps(request, sort_keys=True).encode()
        ).hexdigest()[:16]
        output_hash = hashlib.sha3_256(
            json.dumps(response, sort_keys=True).encode()
        ).hexdigest()[:16]

        event = SIEAuditEvent(
            operation="encode",
            model=request.get("model", "unknown"),
            input_hash=input_hash,
            output_hash=output_hash,
            latency_ms=latency_ms,
            phi_c=phi_c,
            temporal_seal="",
        )

        if self.temporal:
            seal = await self.temporal.anchor_event("sie_encode", {
                "model": event.model,
                "input_hash": event.input_hash,
                "output_hash": event.output_hash,
                "latency_ms": event.latency_ms,
                "phi_c": event.phi_c,
                "texts_count": len(request.get("texts", [])),
                "timestamp": time.time(),
            })
            event.temporal_seal = seal[:16]

        return event

    async def anchor_score(
        self,
        request: dict,
        response: dict,
        latency_ms: float,
        phi_c: float,
    ) -> SIEAuditEvent:
        input_hash = hashlib.sha3_256(
            json.dumps(request, sort_keys=True).encode()
        ).hexdigest()[:16]

        event = SIEAuditEvent(
            operation="score",
            model=request.get("model", "unknown"),
            input_hash=input_hash,
            output_hash=hashlib.sha3_256(
                json.dumps(response, sort_keys=True).encode()
            ).hexdigest()[:16],
            latency_ms=latency_ms,
            phi_c=phi_c,
            temporal_seal="",
        )

        if self.temporal:
            seal = await self.temporal.anchor_event("sie_score", {
                "model": event.model,
                "query_hash": hashlib.sha3_256(
                    request.get("query", "").encode()
                ).hexdigest()[:16],
                "documents_count": len(request.get("documents", [])),
                "top_score": max(
                    response.get("scores", [0])
                ) if response.get("scores") else 0,
                "latency_ms": event.latency_ms,
                "phi_c": event.phi_c,
                "timestamp": time.time(),
            })
            event.temporal_seal = seal[:16]

        return event

    async def anchor_extract(
        self,
        request: dict,
        response: dict,
        latency_ms: float,
        phi_c: float,
    ) -> SIEAuditEvent:
        event = SIEAuditEvent(
            operation="extract",
            model=request.get("model", "unknown"),
            input_hash=hashlib.sha3_256(
                json.dumps(request, sort_keys=True).encode()
            ).hexdigest()[:16],
            output_hash=hashlib.sha3_256(
                json.dumps(response, sort_keys=True).encode()
            ).hexdigest()[:16],
            latency_ms=latency_ms,
            phi_c=phi_c,
            temporal_seal="",
        )

        if self.temporal:
            seal = await self.temporal.anchor_event("sie_extract", {
                "model": event.model,
                "entities_requested": request.get("entities", []),
                "entities_extracted": sum(
                    len(v) for v in response.get("entities", {}).values()
                ),
                "latency_ms": event.latency_ms,
                "phi_c": event.phi_c,
                "timestamp": time.time(),
            })
            event.temporal_seal = seal[:16]

        return event