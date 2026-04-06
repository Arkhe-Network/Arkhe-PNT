#!/usr/bin/env python3
"""
arkhe_fluorescence_analysis.py
Arkhe(n) – Fase 4: Análise de Fluorescência e Coerência λ₂.
Simula a detecção de γ-H2AX foci e o cálculo de λ₂_DNA para validar a regeneração.
Inclui gatilhos de segurança EQBE (viabilidade MTT).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# ============================================================================
# PARÂMETROS BIOLÓGICOS
# ============================================================================
THRESHOLD_VIABILITY = 0.85
THRESHOLD_LAMBDA2_CRIT = 0.847

def simulate_fluorescence_scan(layout_csv: str):
    """
    Simula a leitura de um leitor de placas de fluorescência.
    Mede intensidade de GFP (Arkhe-v1 expression) e viabilidade celular.
    """
    if not os.path.exists(layout_csv):
        # Create dummy layout if missing
        wells = [f"{chr(65+i)}{j+1}" for i in range(8) for j in range(12)]
        df = pd.DataFrame({"well": wells, "nerve_type": "custom"})
    else:
        df = pd.read_csv(layout_csv)

    results = []
    for _, row in df.iterrows():
        well = row["well"]
        nerve = row.get("nerve_type", "unknown")

        # Simulação de sucesso baseada no tipo de nervo
        # Maior volume (Humano) pode ter regeneração mais lenta em 24h
        if "Rato" in nerve:
            success_prob = 0.95
        elif "Humano" in nerve:
            success_prob = 0.88
        else:
            success_prob = 0.90

        viability = np.random.normal(0.92, 0.03)
        # λ₂_DNA restauração
        lambda2 = 0.45 + (1.0 - 0.45) * success_prob * (1 - np.exp(-np.random.uniform(0.5, 1.5)))

        # Intensidade de fluorescência (RFU)
        rfu = 5000 * lambda2 + np.random.normal(0, 100)

        results.append({
            "well": well,
            "nerve_type": nerve,
            "viability_mtt": round(float(viability), 3),
            "lambda2_dna": round(float(lambda2), 4),
            "fluorescence_rfu": round(float(rfu), 1),
            "status": "APPROVED" if viability > THRESHOLD_VIABILITY and lambda2 > THRESHOLD_LAMBDA2_CRIT else "FLAGGED"
        })

    return results

def plot_fluorescence_results(results: list):
    df = pd.DataFrame(results)

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.hist(df["lambda2_dna"], bins=15, color='skyblue', edgecolor='black')
    plt.axvline(x=THRESHOLD_LAMBDA2_CRIT, color='red', linestyle='--', label='Crit Threshold')
    plt.title("Distribuição de Coerência λ₂_DNA")
    plt.xlabel("λ₂")
    plt.ylabel("Contagem")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.scatter(df["viability_mtt"], df["lambda2_dna"], c=df["fluorescence_rfu"], cmap='viridis')
    plt.axhline(y=THRESHOLD_LAMBDA2_CRIT, color='red', linestyle='--')
    plt.axvline(x=THRESHOLD_VIABILITY, color='orange', linestyle='--')
    plt.title("Viabilidade vs Coerência")
    plt.xlabel("Viabilidade (MTT)")
    plt.ylabel("λ₂_DNA")
    plt.colorbar(label='Fluorescência (RFU)')

    plt.tight_layout()
    plt.savefig("fluorescence_analysis_summary.png", dpi=150)
    print("✅ Gráfico de análise de fluorescência salvo: fluorescence_analysis_summary.png")

def main():
    print("=" * 70)
    print("ARKHE(n) – FASE 4: ANÁLISE DE FLUORESCÊNCIA E COERÊNCIA")
    print("=" * 70)

    layout_file = "plate_layout.csv"
    results = simulate_fluorescence_scan(layout_file)
    plot_fluorescence_results(results)

    # Registro na Arkhe-Chain
    report = {
        "event": "FLUORESCENCE_ANALYSIS_COMPLETE",
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(results),
        "mean_lambda2": float(np.mean([r["lambda2_dna"] for r in results])),
        "mean_viability": float(np.mean([r["viability_mtt"] for r in results])),
        "verdict": "SUCCESS" if np.mean([r["lambda2_dna"] for r in results]) > THRESHOLD_LAMBDA2_CRIT else "PARTIAL",
        "details": results
    }

    with open("arkhe_fluorescence_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Relatório de Fase 4 gerado: arkhe_fluorescence_report.json")
    print(f"   λ₂ médio: {report['mean_lambda2']:.4f}")
    print(f"   Viabilidade média: {report['mean_viability']*100:.1f}%")

if __name__ == "__main__":
    main()
