import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_asic_interfaces():
    print("🔌 REVISÃO DE HERMETICIDADE DE INTERFACES")
    print("-" * 60)

    engine = SASCEMEngine()

    print("[*] Case A: Standard USB (No isolation, potential ground loop)...")
    case_a = engine.interface.analyze_interface(isolation_active=False, vbus_connected=True, gnd_strategy="shared_pcb")
    print(f"    - Isolation: {case_a['interface_isolation_db']} dB")
    print(f"    - L2 Penalty: {case_a['l2_coherence_penalty']:.3f}")
    print(f"    - Status: {case_a['status']}")

    print("\n[*] Case B: Arkhe Isolated USB (ADuM4160 + Star Ground)...")
    case_b = engine.interface.analyze_interface(isolation_active=True, vbus_connected=False, gnd_strategy="chassis_only")
    print(f"    - Isolation: {case_b['interface_isolation_db']} dB")
    print(f"    - L2 Penalty: {case_b['l2_coherence_penalty']:.3f}")
    print(f"    - Status: {case_b['status']}")

    if case_b['status'] == "HERMETIC":
        print("    ✅ INTERFACE VALIDATED (No spectral leaks)")
    else:
        print("    ❌ INTERFACE LEAKY")

    report = {
        "analysis": "ASIC-INTERFACES",
        "standard_usb": case_a,
        "arkhe_usb": case_b,
        "status": "APPROVED" if case_b['status'] == "HERMETIC" else "REJECTED"
    }

    with open("asic_interface_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Interfaces salvo.")

if __name__ == "__main__":
    model_asic_interfaces()
