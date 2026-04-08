import numpy as np
import os
import sys
import json

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import EMSpecification, SASCEMEngine
from src.physics.sasc_phase_slam import MarconiASICDesigner, Heaviside3DScene

def model_tzinor_antennas():
    print("🚀 MODELANDO 850.024 (ANTENAS TZINOR 77 GHz)")
    print("-" * 60)

    engine = SASCEMEngine()
    designer = MarconiASICDesigner(engine.heaviside0)
    scene_engine = Heaviside3DScene()

    spec = EMSpecification(
        frequency_range=(76e9, 81e9),
        target_lambda2=0.99,
        max_jitter_ps=0.1
    )

    print("[*] Synthesizing Phased Array 8x8 for Long-Range...")
    design = designer.design_tzinor_array(spec)

    print(f"    - Type: {design['type']}")
    print(f"    - Predicted Lambda2: {design['predicted_lambda2']:.5f}")
    print(f"    - Est. Range: {design['range_estimate_km']} km")

    # Simulate outdoor propagation
    print("[*] Simulating outdoor phase propagation (W-Band)...")
    outdoor_scene = np.zeros((64, 64))
    outdoor_scene[20:44, 20:44] = 0.2 # Atmosphere/Clutter

    propagation = scene_engine.predict_scene(outdoor_scene, 77e9)
    print(f"    - Avg Outdoor Coherence: {np.mean(propagation['lambda2_field']):.4f}")

    report = {
        "block": "850.024",
        "lambda2": design['predicted_lambda2'],
        "range_km": design['range_estimate_km'],
        "outdoor_coherence": float(np.mean(propagation['lambda2_field'])),
        "status": "APPROVED"
    }

    with open("tzinor_antennas_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório de Antenas Tzinor salvo.")

if __name__ == "__main__":
    model_tzinor_antennas()
