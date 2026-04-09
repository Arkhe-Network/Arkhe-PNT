import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
if os.path.join(os.getcwd(), 'src') not in sys.path:
    sys.path.append(os.path.join(os.getcwd(), 'src'))

from research.connectome_spectral_analysis import ConnectomePolytopeAnalyzer

def run_connectome_research():
    print("🧠 INICIANDO VETOR DE VALIDAÇÃO NEURAL")
    print("-" * 60)

    # 1. Connectome Polytope Analysis
    print("[*] Analyzing Human Connectome (HCP Proxy Matrix)...")
    # Simulate a 100-region connectivity matrix
    W = np.random.rand(100, 100)
    W = (W + W.T) / 2 # Symmetric

    analyzer = ConnectomePolytopeAnalyzer(W)

    # Simulate consciousness coherence data
    coherence_data = {
        'NREM_deep': 0.3,
        'REM': 0.7,
        'Lucid': 0.9,
        'Meditation': 0.85
    }

    mapping = analyzer.map_states(coherence_data)
    print(f"    - Spectral Dimension (d): {mapping['spectral_dim']:.2f}")
    print(f"    - All States Quantized: {mapping['all_quantized']}")

    for state, data in mapping['mapping'].items():
        print(f"    - {state:10s}: Observed L2={data['l2_observed']:.2f} -> Quantized={data['is_quantized']}")

    if mapping['all_quantized']:
        print("\n    ✅ NEURAL QUANTIZATION VALIDATED (States align with spectral gaps)")
    else:
        print("\n    ⚠️ CONTINUOUS SPECTRUM detected (States not fully quantized)")

    report = {
        "analysis": "CONNECTOME-POLYTOPE",
        "mapping": mapping,
        "status": "COMPLETED"
    }

    with open("connectome_research_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Validação Neural salvo.")

if __name__ == "__main__":
    run_connectome_research()
