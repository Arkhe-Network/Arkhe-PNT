import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_thermal_stress():
    print("🔥 SIMULAÇÃO DE STRESS TÉRMICO (SARCÓFAGO)")
    print("-" * 60)

    engine = SASCEMEngine()

    # Power dissipation: 3.5W (SiP) + 1.0W (LDO) = 4.5W
    power_w = 4.5
    ambient_c = 25.0

    print(f"[*] Simulating thermal drift with OPTIMIZED cooling (R_theta=5 K/W)...")
    # Using Gap Pad + Thermal Vias to reduce R_theta from 15 to 5
    results = engine.thermal.simulate_thermal_drift(power_w, ambient_c, r_theta_ja=5.0)

    print(f"    - Final Interior Temp: {results['final_temp_c']:.1f} °C")
    print(f"    - Absorber Attenuation Scaling: {results['absorber_attenuation_scaling']:.3f}")

    if results['status'] == "STABLE":
        print("    ✅ THERMAL STABILITY VALIDATED (< 70 °C)")
    else:
        print("    ❌ EXCESSIVE HEAT (Potential Absorber Degradation)")

    report = {
        "analysis": "THERMAL-STRESS",
        "power_w": power_w,
        "final_temp_c": results['final_temp_c'],
        "status": results['status']
    }

    with open("thermal_stress_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório Térmico salvo.")

if __name__ == "__main__":
    model_thermal_stress()
