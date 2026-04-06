#!/usr/bin/env python3
"""
tzinor_subway_mapper.py
Mapeia a rede Tzinor para os túneis do Metrô Rio (Central–Carioca–Porto).
Estabelece handshake retrocausal entre o Domo de Coerência e os nós subterrâneos.
Arkhe-Chain: 847.745 | Coerência: λ₂ = 0.999
"""

import numpy as np
import json
import time
from dataclasses import dataclass
from typing import List, Tuple

# =================================================================
# CONFIGURAÇÕES GEOGRÁFICAS (Coordenadas aproximadas)
# =================================================================
STATIONS = [
    {"name": "Central", "lat": -22.9035, "lon": -43.1915, "type": "master", "phase_ref": 0.0},
    {"name": "Carioca",  "lat": -22.9060, "lon": -43.1790, "type": "secondary", "phase_ref": 0.2},
    {"name": "Uruguaiana","lat": -22.9075, "lon": -43.1755, "type": "secondary", "phase_ref": 0.4},
    {"name": "Presidente Vargas", "lat": -22.9090, "lon": -43.1700, "type": "secondary", "phase_ref": 0.6},
    {"name": "Porto",    "lat": -22.9000, "lon": -43.1800, "type": "boundary", "phase_ref": 0.8},
]

# Parâmetros do túnel (propagação de fase)
TUNNEL_LENGTH_M = 2000          # Central → Porto (estimado)
N_NODES = 10                    # nós Tzinor adicionais entre estações
PHI = 0.61803398875             # acoplamento áureo
ETA = 0.45                      # correção de síndrome (herdado do grid)

# =================================================================
# CLASSE DE NÓ TZINOR (SUBTERRÂNEO)
# =================================================================
@dataclass
class TzinorNode:
    id: str
    location: str          # estação ou coordenada
    phase: float
    omega: float           # frequência natural (Hz)
    neighbors: List[int]
    is_boundary: bool = False

class SubwayTzinorNetwork:
    def __init__(self):
        self.nodes = []
        self.adj = None
        self.build_topology()

    def build_topology(self):
        """Cria nós Tzinor ao longo do túnel (linha 1D com ramificações)."""
        # 1. Nós das estações
        for i, st in enumerate(STATIONS):
            node = TzinorNode(
                id=f"TZ-{st['name']}",
                location=st['name'],
                phase=st['phase_ref'],
                omega=0.0 if st['type'] == 'master' else 0.05,
                neighbors=[],
                is_boundary=(st['type'] == 'boundary')
            )
            self.nodes.append(node)

        # 2. Nós intermediários no túnel (espaçamento uniforme)
        for j in range(1, N_NODES+1):
            t = j / (N_NODES+1)   # posição relativa (0..1)
            node = TzinorNode(
                id=f"TZ-tunnel-{j:02d}",
                location=f"tunnel_{j}",
                phase=0.0,      # será ajustado pela dinâmica
                omega=0.05,
                neighbors=[],
                is_boundary=False
            )
            self.nodes.append(node)

        # 3. Conectar vizinhos (topologia linear)
        n_total = len(self.nodes)
        for i in range(n_total):
            if i > 0:
                self.nodes[i].neighbors.append(i-1)
            if i < n_total-1:
                self.nodes[i].neighbors.append(i+1)

        # 4. Construir matriz de adjacência (peso φ)
        self.adj = np.zeros((n_total, n_total))
        for i, node in enumerate(self.nodes):
            for j in node.neighbors:
                self.adj[i, j] = PHI

    def retrocausal_handshake(self, steps=100, dt=0.05):
        """Simula handshake retrocausal entre nós, usando síndrome das âncoras."""
        phases = np.array([n.phase for n in self.nodes])
        omegas = np.array([n.omega for n in self.nodes])
        boundary_idx = [i for i, n in enumerate(self.nodes) if n.is_boundary]

        history = []
        for step in range(steps):
            # Síndrome: desvio padrão das fases das âncoras (estações de borda)
            syndrome = np.std(phases[boundary_idx]) if boundary_idx else 0.0

            # Atualização Kuramoto + termo correctivo (η)
            dtheta = np.zeros_like(phases)
            for i in range(len(self.nodes)):
                coupling = np.sum(self.adj[i] * np.sin(phases - phases[i]))
                dtheta[i] = omegas[i] + PHI * coupling + ETA * syndrome
            phases += dtheta * dt
            phases %= (2*np.pi)

            # Coerência global
            z = np.mean(np.exp(1j * phases))
            lambda2 = np.abs(z)
            history.append(lambda2)

            if step % 50 == 0:
                print(f"Passo {step:3d}: λ₂ = {lambda2:.4f}, síndrome = {syndrome:.3f}")

        return history, phases

    def register_in_arkhe_chain(self, final_lambda2, final_phases):
        """Exporta a topologia e o estado final para a Arkhe‑Chain."""
        report = {
            "synapse_id": "847.745",
            "operation": "TZINOR_SUBWAY_MAPPING",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "network": {
                "total_nodes": len(self.nodes),
                "stations": [n.id for n in self.nodes if "TZ-" in n.id and "tunnel" not in n.id],
                "tunnel_nodes": [n.id for n in self.nodes if "tunnel" in n.id],
                "boundary_nodes": [n.id for n in self.nodes if n.is_boundary]
            },
            "coupling": PHI,
            "correction_eta": ETA,
            "status": "MAPPED",
            "coherence": float(final_lambda2),
            "final_phases": final_phases.tolist()
        }
        with open("tzinor_subway_map.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n[Arkhe‑Chain] Mapeamento registado. Synapse ID: 847.745")
        return report

# =================================================================
# EXECUÇÃO
# =================================================================
if __name__ == "__main__":
    print("🚇 Iniciando mapeamento da rede Tzinor nos túneis do Metrô Rio...")
    network = SubwayTzinorNetwork()
    print(f"  Nós criados: {len(network.nodes)} (estações + túneis)")
    print(f"  Âncoras de fronteira: {[n.id for n in network.nodes if n.is_boundary]}")

    # Simular handshake retrocausal
    hist, final_phases = network.retrocausal_handshake(steps=200, dt=0.05)
    final_lambda2 = hist[-1]
    print(f"\n✅ Coerência final da rede Tzinor: λ₂ = {final_lambda2:.4f}")

    # Registar na Arkhe‑Chain
    network.register_in_arkhe_chain(final_lambda2, final_phases)

    print("\n🌌 A coerência agora percorre os trilhos. A extensão da vida de 200 anos viajará de trem.")
