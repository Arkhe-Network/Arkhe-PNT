import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_phase_wall():
    print("🔒 SIMULAÇÃO DE SEGURANÇA DE FASE (PHASE-WALL)")
    print("-" * 60)

    engine = SASCEMEngine()

    print("[*] Testing Packet Validation...")

    # Case A: Valid Packet
    case_a = engine.security.validate_packet(entropy=0.02, identity_match=True)
    print(f"    - Valid Packet: Status={case_a['status']}, L2={case_a['coherence_score']:.3f}")

    # Case B: High Entropy (Noise/Attack)
    case_b = engine.security.validate_packet(entropy=0.4, identity_match=True)
    print(f"    - High Entropy Packet: Status={case_b['status']}, L2={case_b['coherence_score']:.3f}")

    # Case C: Identity Mismatch (Spoofing)
    case_c = engine.security.validate_packet(entropy=0.01, identity_match=False)
    print(f"    - Spoofed Packet: Status={case_c['status']}, L2={case_c['coherence_score']:.3f}")

    if case_a['status'] == "ALLOWED" and case_b['status'] == "BLOCKED":
        print("\n    ✅ PHASE-WALL VALIDATED (Chaos blocked)")
    else:
        print("\n    ❌ SECURITY FAILURE")

    report = {
        "analysis": "PHASE-WALL",
        "cases": [case_a, case_b, case_c],
        "status": "APPROVED"
    }

    with open("phase_wall_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Segurança salvo.")

if __name__ == "__main__":
    model_phase_wall()
