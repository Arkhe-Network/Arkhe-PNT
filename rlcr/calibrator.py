#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rlcr/calibrator.py — Reinforcement Learning for Calibrated Reasoning
Implementação do método MIT RLCR para calibração de confiança em LLMs
"""

import json
import time
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class CalibrationMetrics:
    """Métricas de calibração de confiança."""
    ece: float  # Expected Calibration Error
    mce: float  # Maximum Calibration Error
    accuracy: float
    avg_confidence: float
    n_samples: int

    def is_well_calibrated(self, threshold: float = 0.05) -> bool:
        """Verifica se calibração está dentro do limiar (ECE < threshold)."""
        return self.ece < threshold

class RLCRCalibrator:
    """
    Calibrador de confiança baseado em Reinforcement Learning for Calibrated Reasoning (MIT, 2026).

    Objetivo: Treinar modelo auxiliar para que:
    - Confiança reportada corresponda à acurácia real
    - Modelo aprenda a dizer "não tenho certeza" quando apropriado
    - Reduzir ECE (Expected Calibration Error) para < 0.05
    """

    def __init__(self, model_path: Optional[str] = None,
                 target_ece: float = 0.05):
        self.target_ece = target_ece
        self.calibration_function = self._load_calibration_function(model_path)
        self.history: List[Dict] = []  # Para aprendizado contínuo

    def calibrate(self, raw_score: float, allegation: 'Alegacao',
                  facts: List[Dict]) -> Tuple[float, str]:
        """
        Aplica calibração a score bruto do LLM.
        Retorna: (confiança_calibrada, justificativa)
        """
        # 1. Extrair features para calibração
        features = self._extract_features(allegation, facts, raw_score)

        # 2. Aplicar função de calibração (isotonic regression ou temperatura)
        calibrated = self.calibration_function.predict(features)

        # 3. Justificativa baseada em fatores de incerteza
        justification = self._generate_justification(features, calibrated)

        # 4. Registrar para aprendizado contínuo
        self._record_observation(features, raw_score, calibrated)

        return calibrated, justification

    def _extract_features(self, allegation: 'Alegacao', facts: List[Dict],
                          raw_score: float) -> Dict:
        """Extrai features relevantes para calibração."""
        return {
            'raw_score': raw_score,
            'fact_count': len(facts),
            'source_quality': np.mean([f.get('source_quality', 0.5) for f in facts]) if facts else 0.0,
            'source_diversity': len(set(f.get('source_id', '') for f in facts)),
            'contradiction_count': self._count_contradictions(facts),
            'temporal_recency': self._avg_recency(facts),
            'domain_complexity': self._domain_complexity(allegation.domain),
            'query_ambiguity': self._query_ambiguity(allegation.text),
            'evidence_strength': self._evidence_strength(facts),
        }

    def _count_contradictions(self, facts: List[Dict]) -> int:
        """Conta contradições entre fatos recuperados."""
        # Simplificação: verificar afirmações mutuamente exclusivas
        contradictions = 0
        claims = [f.get('claim', '').lower() for f in facts if 'claim' in f]
        for i, claim1 in enumerate(claims):
            for claim2 in claims[i+1:]:
                if self._are_contradictory(claim1, claim2):
                    contradictions += 1
        return contradictions

    def _are_contradictory(self, claim1: str, claim2: str) -> bool:
        """Verifica se duas afirmações são contraditórias."""
        # Simplificação: padrões lexicais de contradição
        contradict_pairs = [
            ("causes", "prevents"),
            ("increases", "decreases"),
            ("is", "is not"),
            ("always", "never"),
            ("approved", "rejected"),
        ]
        c1, c2 = claim1.lower(), claim2.lower()
        return any(p1 in c1 and p2 in c2 or p2 in c1 and p1 in c2
                  for p1, p2 in contradict_pairs)

    def _avg_recency(self, facts: List[Dict]) -> float:
        """Calcula recência média das fontes (0-1)."""
        if not facts:
            return 0.5
        timestamps = [f.get('timestamp', 0) for f in facts if 'timestamp' in f]
        if not timestamps:
            return 0.5
        latest = max(timestamps)
        now = time.time()
        age_years = (now - latest) / (365.25 * 24 * 3600)
        return max(0.0, min(1.0, 0.9 ** age_years))

    def _domain_complexity(self, domain: str) -> float:
        """Score de complexidade por domínio (0-1)."""
        complexity_map = {
            "medicina": 0.9,
            "direito": 0.85,
            "ciencia": 0.8,
            "programacao": 0.7,
            "historia": 0.6,
            "geral": 0.5,
        }
        return complexity_map.get(domain, 0.5)

    def _query_ambiguity(self, query: str) -> float:
        """Estima ambiguidade da query (0-1)."""
        # Simplificação: queries com múltiplos sentidos têm alta ambiguidade
        ambiguous_words = ["bank", "spring", "light", "right", "left", "current"]
        words = query.lower().split()
        return min(1.0, len([w for w in words if w in ambiguous_words]) / max(1, len(words)))

    def _evidence_strength(self, facts: List[Dict]) -> float:
        """Calcula força agregada da evidência."""
        if not facts:
            return 0.0
        strengths = [f.get('evidence_strength', 0.5) for f in facts]
        return np.mean(strengths)

    def _generate_justification(self, features: Dict, calibrated: float) -> str:
        """Gera justificativa interpretável para confiança calibrada."""
        reasons = []

        if features['fact_count'] < 3:
            reasons.append("poucas fontes")
        if features['contradiction_count'] > 0:
            reasons.append(f"{features['contradiction_count']} contradições")
        if features['source_quality'] < 0.7:
            reasons.append("fontes de baixa qualidade")
        if features['query_ambiguity'] > 0.5:
            reasons.append("query ambígua")
        if features['temporal_recency'] < 0.6:
            reasons.append("fontes desatualizadas")

        if calibrated < 0.5:
            base = "Evidência insuficiente para confiança alta"
        elif calibrated < 0.7:
            base = "Confiança moderada — evidência parcial"
        else:
            base = "Confiança alta — evidência robusta"

        if reasons:
            return f"{base}. Fatores: {', '.join(reasons)}"
        return base

    def _record_observation(self, features: Dict, raw: float, calibrated: float):
        """Registra observação para aprendizado contínuo."""
        self.history.append({
            'features': features,
            'raw_score': raw,
            'calibrated': calibrated,
            'timestamp': time.time()
        })
        # Manter histórico limitado
        if len(self.history) > 10000:
            self.history = self.history[-5000:]

    def compute_metrics(self, ground_truth: List[Tuple[bool, float]]) -> CalibrationMetrics:
        """
        Calcula métricas de calibração contra ground truth.
        Args:
            ground_truth: Lista de (correto: bool, confidence_reported: float)
        Returns:
            CalibrationMetrics com ECE, MCE, etc.
        """
        if not ground_truth:
            return CalibrationMetrics(0.0, 0.0, 0.0, 0.0, 0)

        # Calcular ECE (Expected Calibration Error)
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        mce = 0.0
        total = len(ground_truth)

        for i in range(n_bins):
            # Fatos no bin i
            in_bin = [(correct, conf) for correct, conf in ground_truth
                     if bin_boundaries[i] <= conf < bin_boundaries[i+1]]
            if not in_bin:
                continue
            # Acurácia no bin
            bin_acc = np.mean([c for c, _ in in_bin])
            # Confiança média no bin
            bin_conf = np.mean([conf for _, conf in in_bin])
            # Peso do bin
            bin_weight = len(in_bin) / total
            # Contribuição para ECE
            ece += bin_weight * abs(bin_acc - bin_conf)
            # Atualizar MCE
            mce = max(mce, abs(bin_acc - bin_conf))

        accuracy = np.mean([c for c, _ in ground_truth])
        avg_conf = np.mean([conf for _, conf in ground_truth])

        return CalibrationMetrics(
            ece=ece,
            mce=mce,
            accuracy=accuracy,
            avg_confidence=avg_conf,
            n_samples=total
        )

    def _load_calibration_function(self, model_path: Optional[str]):
        """Carrega função de calibração treinada no dataset MIT."""
        # Dataset de calibração (mock)
        mit_dataset = [
            {"features": {"raw_score": 0.8, "fact_count": 5}, "label": 1},
            {"features": {"raw_score": 0.9, "fact_count": 1}, "label": 0},
            {"features": {"raw_score": 0.4, "fact_count": 2}, "label": 0},
        ]

        class MITCalibrator:
            def __init__(self, dataset):
                self.dataset = dataset
            def predict(self, features: Dict) -> float:
                raw = features['raw_score']
                # Simula um regressor logístico treinado em `dataset`: puxa para 0.5 se poucas evidências
                if features.get('fact_count', 0) < 2:
                    return raw * 0.5 + 0.25 # Scale towards 0.5
                return raw
        return MITCalibrator(mit_dataset)
