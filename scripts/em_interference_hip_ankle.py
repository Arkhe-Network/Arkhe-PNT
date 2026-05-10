import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import EMSpecification, SASCEMEngine
from scripts.model_cluster import get_avatar_coupling_params, generate_cluster_geometry

def run_interference_simulation():
    """
    Executes the near-field interference simulation for the HipRoll/AnkleRoll cluster.
    """
    print("🌐 INICIANDO SIMULAÇÃO DE INTERFERÊNCIA DE CAMPO PRÓXIMO (SASC-EM)")
    print("-" * 60)

    engine = SASCEMEngine()
    params = get_avatar_coupling_params()
    geometry = generate_cluster_geometry(params)

    # Target frequency: 900 MHz (critical for VCO)
    freq = 900e6

    # Define specification
    spec = EMSpecification(
        frequency_range=(890e6, 910e6),
        target_lambda2=0.999,
        max_jitter_ps=2.1
    )

    # Step 1: Characterize initial design
    print(f"[*] Characterizing initial design at {freq/1e6:.1f} MHz...")
    result = engine.heaviside0.predict(geometry, freq)

    print(f"    - Lambda2: {result['lambda2']:.4f}")
    print(f"    - Jitter: {result['jitter_ps']:.4f} ps")
    print(f"    - Passivity: {'OK' if result['passivity_check'] else 'FAIL'}")

    # Step 2: Inverse Design (Optimization) if necessary
    if result['jitter_ps'] > spec.max_jitter_ps or result['lambda2'] < spec.target_lambda2:
        print("\n[*] Initial design below threshold. Invoking Marconi-0 for optimization...")
        optimization = engine.marconi0.generate_design(spec, initial_geometry=geometry)

        optimized_result = optimization['predicted_performance']
        print(f"    - Optimized Lambda2: {optimized_result['lambda2']:.4f}")
        print(f"    - Optimized Jitter: {optimized_result['jitter_ps']:.4f} ps")
        print(f"    - Status: {optimization['convergence_status']}")

        final_result = optimized_result
    else:
        print("\n[*] Initial design satisfies specifications.")
        final_result = result

    print("-" * 60)
    print("📊 RESULTADO FINAL DA SIMULAÇÃO")
    print(f"    - Coerência Lambda2: {final_result['lambda2']:.6f}")
    print(f"    - Jitter Residual: {final_result['jitter_ps']:.6f} ps")

    if final_result['jitter_ps'] < spec.max_jitter_ps:
        print("    ✅ ESPECIFICAÇÃO ATENDIDA (Threshold < 2.1 ps)")
    else:
        print("    ❌ FALHA: Jitter acima do limite")

    # Save report
    report = {
        "timestamp": "2026-04-10T12:00:00Z",
        "cluster": "HipRoll/AnkleRoll",
        "lambda2": final_result['lambda2'],
        "jitter_ps": final_result['jitter_ps'],
        "frequency_hz": freq,
        "status": "APPROVED" if final_result['jitter_ps'] < spec.max_jitter_ps else "REJECTED"
    }

    with open("em_interference_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório salvo em em_interference_report.json")

if __name__ == "__main__":
    run_interference_simulation()
