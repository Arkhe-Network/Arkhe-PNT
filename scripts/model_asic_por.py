import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine

def model_asic_por():
    print("👶 SIMULAÇÃO DE ACORDE PRIMORDIAL (POWER-ON RESET)")
    print("-" * 60)

    engine = SASCEMEngine()

    print("[*] Initiating 4-Stage POR Sequence...")
    por_results = engine.por.simulate_wakeup(cpg_init_l2=0.5)

    for stage in por_results['stages']:
        print(f"    - T={stage['t_ms']}ms: Stage {stage['stage']} -> {stage['status']} (L2={stage['l2']:.2f})")

    print(f"\n[*] Total Wake-up Time: {por_results['total_time_ms']} ms")
    print(f"[*] Final Coherence L2: {por_results['final_l2']:.4f}")

    if por_results['is_deterministic'] and por_results['final_l2'] > 0.8:
        print("    ✅ POR SEQUENCE VALIDATED (Deterministic < 100ms)")
    else:
        print("    ❌ POR SEQUENCE FAILED")

    report = {
        "analysis": "ASIC-POR",
        "total_time_ms": por_results['total_time_ms'],
        "final_l2": por_results['final_l2'],
        "status": "APPROVED" if por_results['is_deterministic'] else "RETRY"
    }

    with open("asic_por_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de POR salvo.")

if __name__ == "__main__":
    model_asic_por()
