#!/usr/bin/env python3
"""
guardian_monitor.py — Monitor de qualidade Φ_C para saídas do SIE
Valida embeddings, scores e entidades extraídas via Guardian Attractor.
"""

import numpy as np
from typing import List, Optional

class SIEQualityMonitor:
    """
    Monitora qualidade das saídas do SIE via Guardian Attractor.

    Verificações:
    • Embeddings: degradação de coerência semântica
    • Scores: distribuição anômala de relevância
    • Extract: entidades maliciosas ou incorretas
    """

    def __init__(self, guardian=None, phi_c_threshold: float = 0.95):
        self.guardian = guardian
        self.threshold = phi_c_threshold

    async def validate_embeddings(
        self,
        texts: List[str],
        embeddings: List[List[float]],
    ) -> float:
        """
        Valida qualidade de embeddings gerados.
        Retorna Φ_C score (0.0 a 1.0).
        """
        if not embeddings or not texts:
            return 1.0

        # Verificar dimensionalidade consistente
        dims = [len(e) for e in embeddings]
        if len(set(dims)) > 1:
            return 0.5  # Inconsistência grave

        # Verificar se embeddings não são todos zeros ou NaN
        all_finite = all(
            np.isfinite(e).all() for e in embeddings
        )
        if not all_finite:
            return 0.3

        # Verificar diversidade de embeddings (não devem ser idênticos)
        if len(embeddings) > 1:
            pairwise_sims = []
            for i in range(min(len(embeddings), 10)):
                for j in range(i + 1, min(len(embeddings), 10)):
                    sim = np.dot(embeddings[i], embeddings[j]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                    )
                    pairwise_sims.append(sim)
            avg_sim = np.mean(pairwise_sims) if pairwise_sims else 0

            # Se todos os embeddings são muito similares, pode indicar problema
            if avg_sim > 0.99:
                return 0.6
            elif avg_sim > 0.95:
                return 0.8

        # Guardian Attractor: verificar conteúdo dos textos originais
        if self.guardian:
            for text in texts:
                safe, report = self.guardian.exorcise(text)
                if not safe and report.severity > 0.8:
                    return 0.4

        return 0.98

    async def validate_scores(
        self,
        query: str,
        documents: List[str],
        scores: List[float],
    ) -> float:
        """
        Valida qualidade de scores de relevância.
        Retorna Φ_C score (0.0 a 1.0).
        """
        if not scores:
            return 1.0

        # Verificar se scores estão no intervalo [0, 1]
        if not all(0.0 <= s <= 1.0 for s in scores):
            return 0.5

        # Verificar distribuição não é uniforme (deve haver discriminação)
        if len(scores) > 1:
            score_range = max(scores) - min(scores)
            if score_range < 0.01:
                return 0.7  # Pouca discriminação

        # Guardian: verificar query e documentos
        if self.guardian:
            safe_q, _ = self.guardian.exorcise(query)
            if not safe_q:
                return 0.3
            for doc in documents[:5]:
                safe_d, _ = self.guardian.exorcise(doc)
                if not safe_d:
                    return 0.5

        return 0.96

    async def validate_extractions(
        self,
        text: str,
        entities: dict,
    ) -> float:
        """
        Valida qualidade de entidades extraídas.
        """
        if not entities:
            return 1.0

        # Verificar se entidades extraídas não são vazias
        total_extracted = sum(len(v) for v in entities.values())
        if total_extracted == 0 and len(text.split()) > 50:
            return 0.6  # Texto longo sem entidades extraídas

        # Guardian: verificar texto original
        if self.guardian:
            safe, report = self.guardian.exorcise(text)
            if not safe:
                return 0.3

        return 0.94