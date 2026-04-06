#!/usr/bin/env python3
"""
light_nerve_repair_model.py
Synapse-κ #16 – Phase Surgery: Photo-Crosslinking Simulation
Arkhe(n) | C/Z Duality & Temporary Tzinors

This script models the transition of a liquid prepolymer (Domain C)
into a solid scaffold (Domain Z) via light-induced projection.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import json
import os

# ============================================================================
# CONSTANTS
# ============================================================================
ETA = 0.5                  # Cross-linking efficiency
GAMMA_RESORPTION = 0.001   # Resorption rate (slow)
LAMBDA_CRIT = 0.847        # Varela threshold

# ============================================================================
# C -> Z PROJECTION MODEL
# ============================================================================
def scaffold_dynamics(t, lambda_z, intensity):
    """
    dλz/dt = η * I(t) * (1 - λz) - γ * λz
    """
    # intensity is a function of time (e.g., light on for 30s)
    current_intensity = intensity if t < 30 else 0
    d_lambda = ETA * current_intensity * (1.0 - lambda_z) - GAMMA_RESORPTION * lambda_z
    return d_lambda

def run_simulation(intensity_level):
    t_span = (0, 100)
    t_eval = np.linspace(0, 100, 500)
    y0 = [0.0]  # Start from zero coherence (liquid)

    sol = solve_ivp(scaffold_dynamics, t_span, y0, t_eval=t_eval, args=(intensity_level,))
    return sol.t, sol.y[0]

def main():
    print("=" * 60)
    print("ARKHE(n) – PHASE SURGERY: PHOTO-CROSSLINKING MODEL")
    print("=" * 60)

    intensities = {
        "Low (0.1)": 0.1,
        "Optimal (0.5)": 0.5,
        "High (2.0)": 2.0
    }

    results = {}
    plt.figure(figsize=(10, 6))

    for name, I in intensities.items():
        t, l2 = run_simulation(I)
        results[name] = {"time": t.tolist(), "lambda2": l2.tolist()}
        plt.plot(t, l2, label=f"Intensity: {name}")

        peak_l2 = np.max(l2)
        print(f"{name}: Peak λ2 = {peak_l2:.4f} ({'PASS' if peak_l2 > LAMBDA_CRIT else 'FAIL'})")

    plt.axhline(y=LAMBDA_CRIT, color='r', linestyle='--', label="Varela Threshold")
    plt.axvline(x=30, color='gray', linestyle=':', label="Light OFF")
    plt.title("Photo-Polymer C→Z Projection (Tissium Model)")
    plt.xlabel("Time (s)")
    plt.ylabel("Coherence (λ2_scaffold)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_dir = "tzinor-core/src/biology/cirbp/"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "phase_surgery_scaffold.png"))

    # Save results
    with open(os.path.join(output_dir, "phase_surgery_results.json"), "w") as f:
        json.dump({
            "timestamp": "847.680",
            "model": "Photo-Crosslinking Projection",
            "results": {n: {"peak_l2": np.max(r["lambda2"])} for n, r in results.items()}
        }, f, indent=2)

    print(f"\n[OK] Results saved to {output_dir}")

if __name__ == "__main__":
    main()
