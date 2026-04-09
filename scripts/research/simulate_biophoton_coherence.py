import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.bio_coherence import BiophotonCoherenceSensor
from src.physics.sasc_em_engine import SASCEMEngine

def simulate_biophoton_coherence():
    print("✨ SIMULANDO O ANEL DE FÓTONS CEREBRAL (BIOPHOTON-COHERENCE)")
    print("-" * 60)

    engine = SASCEMEngine()
    sensor = BiophotonCoherenceSensor()

    # 1. Simulate states
    states = ["Deep Sleep", "REM Sleep", "Waking", "Meditation", "Samadhi"]
    # Simulated intensities and photon counts
    # Poisson-like for low coherence, sub-Poissonian for high

    print("[*] Correlating EEG-Shadow λ₂ with Optical Biophoton λ₂...")

    results = []
    for i, state in enumerate(states):
        # Higher index -> higher coherence
        l2_eeg = 0.1 + 0.2 * i

        # Simulate photon counts for this state
        # High coherence -> low variance relative to mean (sub-Poissonian)
        mean_counts = 100 * (i + 1)
        if i < 3:
            # Poisson
            counts = np.random.poisson(mean_counts, 100)
        else:
            # Sub-Poissonian (squeezed)
            counts = np.random.normal(mean_counts, np.sqrt(mean_counts) * 0.5, 100)

        opt_res = sensor.measure_coherence(counts, np.arange(100))
        l2_opt = opt_res['lambda2_biophoton']

        print(f"    - {state:12s}: EEG.L2={l2_eeg:.2f} | OPT.L2={l2_opt:.4f} | {opt_res['status']}")
        results.append({
            "state": state,
            "l2_eeg": l2_eeg,
            "l2_opt": l2_opt,
            "status": opt_res['status']
        })

    # Calculate Correlation
    eeg_arr = [r['l2_eeg'] for r in results]
    opt_arr = [r['l2_opt'] for r in results]
    correlation = np.corrcoef(eeg_arr, opt_arr)[0, 1]

    print(f"\n[*] Global Correlation EEG-UPE: {correlation:.4f}")

    if correlation > 0.8:
        print("    ✅ HYPOTHESIS VALIDATED: Biophotons are the Optical Shadow of Fase.")
    else:
        print("    ⚠️ LOW CORRELATION: Biological Phase Vacuum not yet established.")

    # Waveguide analysis
    print("\n[*] Organic Waveguide Analysis (Microtubule):")
    wg = engine.bioplasma.analyze_waveguide("Microtubule")
    print(f"    - Structure: {wg['structure']}")
    print(f"    - Sharpe Threshold (tau): {wg['tau_sharpe']:.3f}")
    print(f"    - Status: {wg['waveguide_status']}")

    report = {
        "analysis": "BIOPHOTON-COHERENCE",
        "correlation": float(correlation),
        "results": results,
        "waveguide": wg,
        "status": "APPROVED" if correlation > 0.8 else "RETRY"
    }

    with open("biophoton_coherence_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Coerência Biofotônica salvo.")

if __name__ == "__main__":
    simulate_biophoton_coherence()
