#!/usr/bin/env python3
"""
cirbp_statistical_analysis.py
Synapse-κ #15 – Fase 4: Modelo de Análise Estatística para Reparo In Vitro
Arkhe(n) | Longevidade e Coerência Genómica

Este script processa os dados de fluorescência (focos γ-H2AX) e calcula
a velocidade de reparo e o ganho de coerência λ₂_DNA.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import json
import os

# ============================================================================
# PARÂMETROS ARKHE
# ============================================================================
LAMBDA_MAX = 0.999
LAMBDA_CRIT = 0.847

# ============================================================================
# PROCESSAMENTO DE FLUORESCÊNCIA (SIMULAÇÃO)
# ============================================================================
def simulate_foci_data(n_cells=50, t_points=[0, 15, 30, 60, 120]):
    """
    Simula dados de focos γ-H2AX (contagem manual/automatizada).
    """
    data = []

    # Taxas de reparo (focos por hora)
    rates = {
        "Controle (basal)": 0.2,
        "Peptídeo v1": 1.5,
        "Baleia (controle +)": 2.0
    }

    for cond, rate in rates.items():
        for t in t_points:
            # Modelo de decaimento exponencial: F(t) = F0 * exp(-rate * t)
            f0 = 25.0  # focos iniciais após radiação
            mean_foci = f0 * np.exp(-rate * (t/60.0))
            foci_counts = np.random.poisson(mean_foci, n_cells)

            for count in foci_counts:
                data.append({
                    "Condição": cond,
                    "Tempo (min)": t,
                    "Focos": count,
                    "λ2_DNA": LAMBDA_MAX - (count/30.0)*(1.0-LAMBDA_CRIT)
                })

    return pd.DataFrame(data)

# ============================================================================
# ANÁLISE ESTATÍSTICA
# ============================================================================
def analyze_repair_kinetics(df):
    print("\n" + "="*60)
    print("ANÁLISE ESTATÍSTICA: REPARO DE DNA (ARKHE-v1)")
    print("="*60)

    # 1. Velocidade de reparo (Regressão Linear no log)
    results = {}
    for cond in df["Condição"].unique():
        sub = df[(df["Condição"] == cond) & (df["Tempo (min)"] > 0)]
        slope, intercept, r_val, p_val, std_err = stats.linregress(sub["Tempo (min)"], np.log(sub["Focos"] + 1))
        results[cond] = {
            "repair_rate": -slope,
            "r_squared": r_val**2,
            "p_value": p_val
        }
        print(f"Condição: {cond:20s} | Taxa: {(-slope):.4f} | R²: {r_val**2:.3f}")

    # 2. Comparação em t=60min (ANOVA)
    t60 = df[df["Tempo (min)"] == 60]
    groups = [t60[t60["Condição"] == c]["Focos"] for c in df["Condição"].unique()]
    f_stat, p_anova = stats.f_oneway(*groups)
    print(f"\nANOVA (t=60min): F={f_stat:.2f}, p={p_anova:.2e}")

    return results, p_anova

# ============================================================================
# VISUALIZAÇÃO
# ============================================================================
def plot_results(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Painel 1: Cinética de Desaparecimento de Focos
    for cond in df["Condição"].unique():
        sub = df[df["Condição"] == cond]
        means = sub.groupby("Tempo (min)")["Focos"].mean()
        stds = sub.groupby("Tempo (min)")["Focos"].std()
        axes[0].errorbar(means.index, means, yerr=stds, fmt='-o', label=cond, capsize=5)

    axes[0].set_title("Cinética de Reparo (Focos γ-H2AX)")
    axes[0].set_xlabel("Tempo (minutos)")
    axes[0].set_ylabel("Média de Focos/Célula")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Painel 2: Recuperação da Coerência λ2_DNA
    for cond in df["Condição"].unique():
        sub = df[df["Condição"] == cond]
        l2_means = sub.groupby("Tempo (min)")["λ2_DNA"].mean()
        axes[1].plot(l2_means.index, l2_means, '-s', label=cond)

    axes[1].axhline(y=LAMBDA_CRIT, color='r', linestyle='--', label="Limiar de Varela")
    axes[1].set_title("Recuperação da Coerência λ2_DNA")
    axes[1].set_xlabel("Tempo (minutos)")
    axes[1].set_ylabel("λ2_DNA")
    axes[1].set_ylim(0.8, 1.0)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("tzinor-core/src/biology/cirbp/cirbp_repair_kinetics.png")
    print("\n[OK] Gráfico salvo: tzinor-core/src/biology/cirbp/cirbp_repair_kinetics.png")

# ============================================================================
# MAIN
# ============================================================================
def main():
    # 1. Simular dados
    df = simulate_foci_data()

    # 2. Analisar
    kinetics, p_anova = analyze_repair_kinetics(df)

    # 3. Plotar
    plot_results(df)

    # 4. Salvar JSON
    output = {
        "timestamp": "847.640",
        "analysis_type": "γ-H2AX Foci Kinetics",
        "results": {
            cond: {
                "repair_velocity": kinetics[cond]["repair_rate"],
                "p_value_vs_time": kinetics[cond]["p_value"],
                "final_lambda2": float(df[(df["Condição"] == cond) & (df["Tempo (min)"] == 120)]["λ2_DNA"].mean())
            } for cond in kinetics
        },
        "anova_p_value": p_anova,
        "validation_status": "PASSED" if p_anova < 0.001 else "FAILED"
    }

    with open("tzinor-core/src/biology/cirbp/cirbp_statistical_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("[OK] Resultados salvos em tzinor-core/src/biology/cirbp/cirbp_statistical_results.json")

if __name__ == "__main__":
    main()
