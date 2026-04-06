#!/usr/bin/env python3
"""
arkhe_mechanotransduction.py
Arkhe(n) – Mechanotransduction Module (Synapse-κ)
Models the transduction of light-induced stiffness into cellular decision making (YAP/TAZ).
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime

# ============================================================================
# PHYSICAL & BIOLOGICAL CONSTANTS
# ============================================================================
E_MAX_KPA = 150.0       # Maximum theoretical stiffness of fully cured Tissium
K_RETICULATION = 0.005  # Reticulation rate constant (cm^2/mJ)
E_50_YAP = 10.0         # Stiffness at which 50% YAP is nuclear (kPa)
YAP_SCALE = 3.0         # Sharpness of YAP translocation switch
E_OPTIMAL_NEURAL = 12.0 # Optimal stiffness for neural lineage (kPa)
NEURAL_WINDOW_SIGMA = 4.0 # Tolerance for neural lineage coherence

class MechanotransductionModel:
    """
    Models the multi-layer transduction:
    Light Dose -> Stiffness (E) -> YAP/TAZ Ratio -> Mechanic Coherence (MCF)
    """

    @staticmethod
    def calculate_stiffness(irradiance_mw_cm2: float, time_s: float) -> float:
        """
        Calculates Young's Modulus E (kPa) based on photopolymerization dose.
        E = E_max * (1 - exp(-k * dose))
        """
        dose = irradiance_mw_cm2 * time_s # mJ/cm^2
        stiffness = E_MAX_KPA * (1 - np.exp(-K_RETICULATION * dose))
        return float(stiffness)

    @staticmethod
    def calculate_yap_ratio(stiffness_kpa: float) -> float:
        """
        Models the Nuclear/Cytoplasmic ratio of YAP/TAZ.
        Ratio > 1.0 indicates predominantly nuclear YAP (stiff substrate).
        Ratio < 1.0 indicates predominantly cytoplasmic YAP (soft substrate).
        """
        # Sigmoidal response to stiffness
        ratio = 0.2 + 2.0 / (1 + np.exp(-(stiffness_kpa - E_50_YAP) / YAP_SCALE))
        return float(ratio)

    @staticmethod
    def calculate_mechanic_coherence(stiffness_kpa: float) -> float:
        """
        Calculates the Mechanic Coherence Factor (MCF).
        Measures how well the mechanical environment aligns with the neural blueprint.
        """
        # Gaussian window around the neural optimum
        mcf = np.exp(-(stiffness_kpa - E_OPTIMAL_NEURAL)**2 / (2 * NEURAL_WINDOW_SIGMA**2))
        return float(mcf)

def simulate_mechanotransduction_panel():
    """
    Simulates a panel of different light doses to find the 'Neural Window'.
    """
    times = np.linspace(0, 60, 100) # seconds
    irradiance = 15.0 # mW/cm^2

    model = MechanotransductionModel()

    results = []
    for t in times:
        E = model.calculate_stiffness(irradiance, t)
        yap = model.calculate_yap_ratio(E)
        mcf = model.calculate_mechanic_coherence(E)

        results.append({
            "time_s": t,
            "dose_mj_cm2": irradiance * t,
            "stiffness_kpa": E,
            "yap_ratio": yap,
            "mechanic_coherence": mcf
        })

    return results

def plot_mechanotransduction(results):
    df = pd.DataFrame(results)

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Plot Stiffness and MCF
    color = 'tab:blue'
    ax1.set_xlabel('Dose (mJ/cm²)')
    ax1.set_ylabel('Stiffness (kPa)', color=color)
    ax1.plot(df['dose_mj_cm2'], df['stiffness_kpa'], color=color, label='Stiffness (E)')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Coherence / YAP Ratio', color=color)
    ax2.plot(df['dose_mj_cm2'], df['mechanic_coherence'], color='green', lw=2, label='Mechanic Coherence (MCF)')
    ax2.plot(df['dose_mj_cm2'], df['yap_ratio'], color=color, linestyle='--', label='YAP Nuc/Cyto Ratio')
    ax2.tick_params(axis='y', labelcolor=color)

    # Highlight Neural Window
    neural_mask = df['mechanic_coherence'] > 0.8
    if any(neural_mask):
        ax1.fill_between(df['dose_mj_cm2'], 0, E_MAX_KPA, where=neural_mask, color='green', alpha=0.1, label='Neural Lineage Window')

    plt.title("Arkhe(n) Mechanotransduction Model: Phase-Stiffness Transduction")
    fig.tight_layout()
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.savefig("mechanotransduction_analysis.png", dpi=150)
    print("✅ Plot saved: mechanotransduction_analysis.png")

if __name__ == "__main__":
    import pandas as pd
    print("=" * 70)
    print("ARKHE(n) – MECANOTRANSDUÇÃO DE FASE (Synapse-κ)")
    print("=" * 70)

    data = simulate_mechanotransduction_panel()
    plot_mechanotransduction(data)

    # Find optimal dose for neural
    optimal_idx = np.argmax([r['mechanic_coherence'] for r in data])
    opt = data[optimal_idx]

    print(f"\n🎯 Ponto Óptimo Neural Detectado:")
    print(f"   Dose: {opt['dose_mj_cm2']:.1f} mJ/cm²")
    print(f"   Tempo (a 15mW): {opt['time_s']:.1f} s")
    print(f"   Rigidez: {opt['stiffness_kpa']:.2f} kPa")
    print(f"   Coerência Mecânica: {opt['mechanic_coherence']:.4f}")

    # Register in Arkhe-Chain
    report = {
        "event": "MECHANOTRANSDUCTION_CALIBRATION",
        "timestamp": datetime.now().isoformat(),
        "optimal_params": opt,
        "model_version": "v1.0-YAP-LINC",
        "status": "VALIDATED"
    }
    with open("mechanotransduction_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✅ Relatório registrado: mechanotransduction_report.json")
