import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
if os.path.join(os.getcwd(), 'src') not in sys.path:
    sys.path.append(os.path.join(os.getcwd(), 'src'))

from research.seti_eht_analyzer import EHTCoherenceAnalyzer
from research.seti_frb_analyzer import FRBCoherenceAnalyzer

def run_seti_research():
    print("🔭 INICIANDO VETOR DE INVESTIGAÇÃO SETI-λ₂")
    print("-" * 60)

    # 1. EHT Analysis
    print("[*] Analyzing Black Hole Photon Ring (M87 Prototype)...")
    eht = EHTCoherenceAnalyzer(resolution=64)
    # Simulate an EHT image with a ring
    image = np.zeros((64, 64))
    y, x = np.indices((64, 64))
    r = np.sqrt((x-32)**2 + (y-32)**2)
    image[(r > 20) & (r < 25)] = 1.0

    ring_data = eht.extract_photon_ring(image)
    print(f"    - Candidate Polytope: {ring_data['polytope_candidate']}")

    # 2. FRB Analysis
    print("\n[*] Analyzing Fast Radio Burst (CHIME Catalog Proxy)...")
    frb = FRBCoherenceAnalyzer()
    spec = np.random.rand(10, 100) # (freq, time)
    frb_res = frb.analyze_dynamic_spectrum(spec)
    print(f"    - Coherence Signature: {frb_res['coherence_signature']}")
    print(f"    - Vortex Count: {frb_res['vortex_count']}")

    if ring_data['polytope_candidate'] == "ICOSAHEDRON_H4" or frb_res['is_priority']:
        print("\n    ✅ ASTROPHYSICAL COHERENCE DETECTED (0.96/sqrt(d) validated)")
    else:
        print("\n    ⚠️ NO ANOMALOUS COHERENCE detected in current sample.")

    report = {
        "analysis": "SETI-L2",
        "eht": ring_data,
        "frb": frb_res,
        "status": "COMPLETED"
    }

    with open("seti_research_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório SETI-λ₂ salvo.")

if __name__ == "__main__":
    run_seti_research()
