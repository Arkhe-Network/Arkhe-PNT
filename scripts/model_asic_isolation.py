import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_asic_isolation():
    print("🛡️ REVISÃO DE ISOLAMENTO RADAR-CPG (850.023-ASIC)")
    print("-" * 60)

    engine = SASCEMEngine()

    # Target distance: 250 um
    # Shielding factor: 1.0 (Deep N-Well + Guard Rings)
    distance_um = 250.0
    shielding = 1.0

    print(f"[*] Simulating isolation at {distance_um} um distance (Shielding={shielding})...")
    iso_results = engine.crosstalk.simulate_isolation(distance_um, shielding)

    print(f"    - Substrate Isolation: {iso_results['substrate_isolation_db']:.1f} dB")
    print(f"    - Magnetic Isolation: {iso_results['magnetic_isolation_db']:.1f} dB")
    print(f"    - PDN Isolation: {iso_results['pdn_isolation_db']:.1f} dB")
    print(f"    - Jitter Degradation: {iso_results['jitter_degradation_ps']:.4f} ps")

    if iso_results['substrate_isolation_db'] < -85 and iso_results['magnetic_isolation_db'] < -70:
        print("    ✅ ISOLATION SPECS MET")
    else:
        print("    ⚠️ ISOLATION BELOW TARGET")

    if iso_results['jitter_degradation_ps'] < 0.1:
        print("    ✅ JITTER DEGRADATION WITHIN LIMIT (< 0.1 ps)")
    else:
        print("    ❌ CRITICAL JITTER DEGRADATION")

    report = {
        "analysis": "ASIC-ISOLATION",
        "distance_um": distance_um,
        "shielding_factor": shielding,
        "results": iso_results,
        "status": "APPROVED" if iso_results['jitter_degradation_ps'] < 0.1 else "FAILED"
    }

    with open("asic_isolation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Isolamento salvo.")

if __name__ == "__main__":
    model_asic_isolation()
