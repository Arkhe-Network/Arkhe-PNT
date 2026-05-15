#!/usr/bin/env python3
"""
model_registry.py — Registro de modelos SIE com metadados Arkhe
Cataloga os 85+ modelos suportados com informações de Φ_C baseline.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SIEModel:
    name: str                    # Nome do modelo (ex: "BAAI/bge-large-en-v1.5")
    primitive: str               # "encode", "score", "extract"
    dimensions: Optional[int]    # Dimensão dos embeddings (encode)
    max_tokens: int = 512
    phi_c_baseline: float = 0.97
    quantization_supported: bool = True
    languages: List[str] = None

class SIEModelRegistry:
    """Catálogo de modelos SIE disponíveis."""

    MODELS = {
        # ── Encode Models ─────────────────────────────
        "BAAI/bge-large-en-v1.5": SIEModel(
            name="BAAI/bge-large-en-v1.5",
            primitive="encode",
            dimensions=1024,
            max_tokens=512,
            phi_c_baseline=0.98,
            languages=["en"],
        ),
        "BAAI/bge-multilingual-gemma2": SIEModel(
            name="BAAI/bge-multilingual-gemma2",
            primitive="encode",
            dimensions=768,
            max_tokens=512,
            phi_c_baseline=0.97,
            languages=["en", "zh", "fr", "de", "es", "pt", "ja", "ko"],
        ),
        "intfloat/e5-large-v2": SIEModel(
            name="intfloat/e5-large-v2",
            primitive="encode",
            dimensions=1024,
            max_tokens=512,
            phi_c_baseline=0.96,
            languages=["en"],
        ),
        "Snowflake/snowflake-arctic-embed-l": SIEModel(
            name="Snowflake/snowflake-arctic-embed-l",
            primitive="encode",
            dimensions=1024,
            max_tokens=2048,
            phi_c_baseline=0.97,
            languages=["en"],
        ),

        # ── Score (Reranker) Models ──────────────────
        "BAAI/bge-reranker-v2-m3": SIEModel(
            name="BAAI/bge-reranker-v2-m3",
            primitive="score",
            dimensions=None,
            max_tokens=1024,
            phi_c_baseline=0.96,
            languages=["en", "zh", "fr", "de", "es", "pt", "ja", "ko"],
        ),
        "BAAI/bge-reranker-large": SIEModel(
            name="BAAI/bge-reranker-large",
            primitive="score",
            dimensions=None,
            max_tokens=512,
            phi_c_baseline=0.97,
            languages=["en"],
        ),

        # ── Extract Models ───────────────────────────
        "Babelscape/rebel-large": SIEModel(
            name="Babelscape/rebel-large",
            primitive="extract",
            dimensions=None,
            max_tokens=512,
            phi_c_baseline=0.94,
            languages=["en"],
        ),
    }

    @classmethod
    def get_model(cls, name: str) -> Optional[SIEModel]:
        return cls.MODELS.get(name)

    @classmethod
    def list_by_primitive(cls, primitive: str) -> List[SIEModel]:
        return [m for m in cls.MODELS.values() if m.primitive == primitive]

    @classmethod
    def list_all(cls) -> Dict[str, SIEModel]:
        return cls.MODELS.copy()