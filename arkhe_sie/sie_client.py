#!/usr/bin/env python3
"""
sie_client.py — Cliente para Superlinked Inference Engine (SIE)
Suporta as três primitivas: encode, score, extract.
"""

import httpx
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EncodeRequest:
    texts: List[str]
    model: str = "BAAI/bge-large-en-v1.5"
    pooling: str = "mean"

@dataclass
class ScoreRequest:
    query: str
    documents: List[str]
    model: str = "BAAI/bge-reranker-v2-m3"

@dataclass
class ExtractRequest:
    text: str
    entities: List[str]  # ["person", "organization", "date", etc.]
    model: str = "Babelscape/rebel-large"

class SIEClient:
    """Cliente HTTP para o SIE com retry e métricas."""

    def __init__(self, endpoint: str = "http://localhost:9080"):
        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self._model_cache: Dict[str, bool] = {}

    async def encode(self, request: EncodeRequest) -> Dict:
        """Converte textos em embeddings vetoriais."""
        response = await self.client.post(
            f"{self.endpoint}/encode",
            json={
                "texts": request.texts,
                "model": request.model,
                "pooling": request.pooling,
            }
        )
        response.raise_for_status()
        return response.json()

    async def score(self, request: ScoreRequest) -> Dict:
        """Rerankeia documentos por relevância à query."""
        response = await self.client.post(
            f"{self.endpoint}/score",
            json={
                "query": request.query,
                "documents": request.documents,
                "model": request.model,
            }
        )
        response.raise_for_status()
        return response.json()

    async def extract(self, request: ExtractRequest) -> Dict:
        """Extrai entidades de texto não estruturado."""
        response = await self.client.post(
            f"{self.endpoint}/extract",
            json={
                "text": request.text,
                "entities": request.entities,
                "model": request.model,
            }
        )
        response.raise_for_status()
        return response.json()

    async def list_models(self) -> List[Dict]:
        """Lista modelos disponíveis no servidor SIE."""
        response = await self.client.get(f"{self.endpoint}/models")
        response.raise_for_status()
        return response.json()

    async def health(self) -> bool:
        """Verifica saúde do servidor SIE."""
        try:
            response = await self.client.get(f"{self.endpoint}/health")
            return response.status_code == 200
        except Exception:
            return False
