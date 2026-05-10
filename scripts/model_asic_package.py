import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_asic_package():
    print("📦 SIMULAÇÃO DE EMPACOTAMENTO SiP (850.023-ASIC)")
    print("-" * 60)

    engine = SASCEMEngine()

    # Critical Parameters (Optimized for Phase Coherence):
    # Bond wire length: 0.3 mm (further reduced to meet S11)
    # Shielding: 45 dB (Enhanced ground shield)
    bw_length = 0.3
    shielding = 45.0
    freq = 60.0

    print(f"[*] Analyzing optimized bond wire (Length={bw_length} mm, Shielding={shielding} dB) at {freq} GHz...")
    results = engine.sip.analyze_package(bw_length, freq, shielding_db=shielding)

    print(f"    - Return Loss (S11): {results['s11_db']:.1f} dB")
    print(f"    - Bond Wire -> CPG Coupling (S21): {results['s21_db']:.1f} dB")
    print(f"    - Package Jitter Degradation: {results['jitter_degradation_ps']:.6f} ps")

    # Accept criteria:
    # S11 < -10 dB
    # S21 < -80 dB
    # Jitter Deg < 0.03 ps

    if results['s11_db'] < -10.0:
        print("    ✅ S11 SPEC MET")
    else:
        print("    ❌ S11 SPEC FAILED (Excessive Reflection)")

    if results['s21_db'] < -80.0:
        print("    ✅ S21 SPEC MET")
    else:
        print("    ❌ S21 SPEC FAILED (Parasitic Antenna)")

    if results['jitter_degradation_ps'] < 0.03:
        print("    ✅ PACKAGE JITTER SPEC MET (< 0.03 ps)")
    else:
        print("    ❌ EXCESSIVE PACKAGE JITTER")

    report = {
        "analysis": "SiP-PACKAGE",
        "bond_wire_mm": bw_length,
        "results": results,
        "status": "APPROVED" if (results['s11_db'] < -10 and results['s21_db'] < -80) else "FAILED"
    }

    with open("asic_package_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Empacotamento salvo.")

if __name__ == "__main__":
    model_asic_package()
