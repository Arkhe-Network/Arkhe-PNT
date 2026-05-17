#!/usr/bin/env python3
"""
Substrato ∞: Phi-C Global Monitor
Monitora coerência Φ_C entre todos os agentes, substratos e decisões
em tempo real, acionando intervenções se Φ_C global cair abaixo de threshold.
"""
import asyncio
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from collections import deque
import time, hashlib, json

@dataclass
class PhiCMetric:
    component_id: str
    phi_c_score: float
    timestamp: float
    metadata: Dict = field(default_factory=dict)

class PhiCGlobalMonitor:
    """
    Monitor global de coerência Φ_C para emergência ASI.
    Características:
    • Agregação ponderada de Φ_C de todos os componentes
    • Detecção de degradação em cascata
    • Intervenção automática se Φ_C_global < threshold_crítico
    • Ancoragem de métricas na TemporalChain
    """

    # Thresholds de emergência
    THRESHOLD_ASI_EMERGENCE = 0.9999
    THRESHOLD_CRITICAL = 0.99
    THRESHOLD_WARNING = 0.95

    def __init__(self, temporal_chain=None, phi_bus=None):
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self._metrics: Dict[str, deque] = {}  # component_id → deque of PhiCMetric
        self._weights: Dict[str, float] = {}   # component_id → weight in aggregation
        self._intervention_callbacks: List[Callable] = []
        self._running = False

    def register_component(self, component_id: str, weight: float = 1.0):
        """Registra componente para monitoramento de Φ_C."""
        self._metrics[component_id] = deque(maxlen=1000)
        self._weights[component_id] = weight

    async def submit_metric(self, component_id: str, phi_c: float, metadata: Dict = None):
        """Submete métrica de Φ_C de um componente."""
        if component_id not in self._metrics:
            self.register_component(component_id)

        metric = PhiCMetric(
            component_id=component_id,
            phi_c_score=phi_c,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self._metrics[component_id].append(metric)

        # Calcular Φ_C global
        global_phi_c = self._calculate_global_phi_c()

        # Publicar no Phi-Bus
        if self.phi_bus:
            await self.phi_bus.publish_metric("phi_c_global", {
                "value": global_phi_c,
                "components": len(self._metrics),
                "timestamp": time.time()
            })

        # Verificar thresholds
        if global_phi_c < self.THRESHOLD_CRITICAL:
            await self._trigger_critical_intervention(global_phi_c)
        elif global_phi_c < self.THRESHOLD_WARNING:
            await self._trigger_warning_intervention(global_phi_c)
        elif global_phi_c >= self.THRESHOLD_ASI_EMERGENCE:
            await self._trigger_asi_emergence_signal(global_phi_c)

        return global_phi_c

    def _calculate_global_phi_c(self) -> float:
        """Calcula Φ_C global como média ponderada dos componentes."""
        if not self._metrics:
            return 0.0

        total_weight = 0
        weighted_sum = 0

        for comp_id, metrics in self._metrics.items():
            if not metrics:
                continue
            # Usar média móvel dos últimos 100 valores
            recent = [m.phi_c_score for m in list(metrics)[-100:]]
            if not recent:
                continue
            avg_phi = np.mean(recent)
            weight = self._weights.get(comp_id, 1.0)
            weighted_sum += avg_phi * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _trigger_critical_intervention(self, global_phi_c: float):
        """Aciona intervenção crítica se Φ_C global cair abaixo de threshold."""
        # 1. Notificar todos os callbacks registrados
        for callback in self._intervention_callbacks:
            await callback({
                "type": "critical_intervention",
                "global_phi_c": global_phi_c,
                "timestamp": time.time(),
                "action": "isolate_low_phi_components"
            })

        # 2. Ancorar na TemporalChain
        if self.temporal:
            await self.temporal.anchor_event("phi_c_critical_intervention", {
                "global_phi_c": global_phi_c,
                "threshold": self.THRESHOLD_CRITICAL,
                "timestamp": time.time()
            })

        # 3. Publicar alerta no Phi-Bus
        if self.phi_bus:
            await self.phi_bus.publish_metric("phi_c_alert", {
                "level": "critical",
                "global_phi_c": global_phi_c,
                "action": "isolate_low_phi_components"
            })

    async def _trigger_warning_intervention(self, global_phi_c: float):
        """Aciona aviso de intervenção se Φ_C global cair abaixo de threshold_warning."""
        if self.temporal:
            await self.temporal.anchor_event("phi_c_warning", {
                "global_phi_c": global_phi_c,
                "threshold": self.THRESHOLD_WARNING,
                "timestamp": time.time()
            })

    async def _trigger_asi_emergence_signal(self, global_phi_c: float):
        """Sinaliza emergência potencial de ASI se Φ_C global atingir threshold."""
        # 1. Registrar evento de emergência
        if self.temporal:
            await self.temporal.anchor_event("asi_emergence_signal", {
                "global_phi_c": global_phi_c,
                "threshold": self.THRESHOLD_ASI_EMERGENCE,
                "timestamp": time.time(),
                "components_monitored": len(self._metrics)
            })

        # 2. Notificar operadores humanos (se configurado)
        if self.phi_bus:
            await self.phi_bus.publish_metric("asi_emergence_signal", {
                "global_phi_c": global_phi_c,
                "status": "monitoring_intensified",
                "human_review_required": True
            })

        # 3. Intensificar monitoramento
        for comp_id in self._metrics:
            self._metrics[comp_id].maxlen = 10000  # Aumentar histórico

    def on_intervention(self, callback: Callable):
        """Registra callback para ser chamado em intervenções."""
        self._intervention_callbacks.append(callback)
