#!/usr/bin/env python3
"""
generate_latency_map.py
Gera o mapa de latência quântica projetada para a expansão Tzinor.
Baseado nos dados de coerência λ₂ da rede subterrânea.
"""

import json
import numpy as np
import matplotlib.pyplot as plt

def generate_latency_map():
    try:
        with open("tzinor_subway_map.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Erro: tzinor_subway_map.json não encontrado.")
        return

    nodes = data["network"]["stations"] + data["network"]["tunnel_nodes"]
    phases = np.array(data["final_phases"])
    lambda2 = data["coherence"]

    # Latência baseada na coerência: L = L_base * (1 - lambda2) / (lambda2 - 0.847)
    # Se lambda2 > 0.99, latência colapsa para quase zero (retrocausalidade)
    base_latency = 1.4 # ns
    latencies = []

    for p in phases:
        # Simplificação: latência local é função da fase relativa
        # Em regime soberano (lambda2 > 0.847), a latência é reduzida drasticamente
        l_eff = base_latency * (1.0 - lambda2) / (lambda2 - 0.84 + 1e-6)
        latencies.append(max(0.01, l_eff))

    # Visualização
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')

    x = range(len(nodes))
    plt.bar(x, latencies, color='cyan', alpha=0.7, label='Latência Efetiva (ns)')
    plt.axhline(y=1.4, color='red', linestyle='--', label='Gargalo Eletrônico (1.4ns)')

    plt.xticks(x, nodes, rotation=45, ha='right')
    plt.ylabel('Latência (ns)')
    plt.title(f'Mapa de Latência Quântica Projetada - Corredor Tzinor (λ₂ = {lambda2:.4f})')
    plt.legend()
    plt.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig("tzinor_latency_map.png")
    print("✅ Mapa de latência quântica gerado: tzinor_latency_map.png")

if __name__ == "__main__":
    generate_latency_map()
