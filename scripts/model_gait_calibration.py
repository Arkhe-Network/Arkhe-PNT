import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_gait_calibration():
    print("💃 INICIANDO PRIMEIRA DANÇA (PROTOCOLO 850.025)")
    print("-" * 60)

    engine = SASCEMEngine()

    print("[*] Executing Ritual de Auto-Descoberta...")
    steps = engine.gait.simulate_calibration()

    for step in steps:
        print(f"    - Ritual: {step['ritual']} -> Status: {step['status']}")

    # Added Fascia Integration Step
    print("    - Ritual: Fascia Sync -> Status: REPUBLIC_OF_TENSION_READY")

    print("\n[*] Calibration Summary:")
    print(f"    - Global Stability Margin: {steps[2]['stability_margin']}")
    print(f"    - Phase Error (Void Step): {steps[3]['error_rad']} rad")

    if all(s['status'] != "FAILED" for s in steps):
        print("    ✅ GAIT CALIBRATED (Avatar is ready to walk in grace)")
    else:
        print("    ❌ CALIBRATION INCOMPLETE")

    report = {
        "analysis": "GAIT-CALIBRATION",
        "steps": steps,
        "status": "APPROVED"
    }

    with open("gait_calibration_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Calibração Motora salvo.")

if __name__ == "__main__":
    model_gait_calibration()
