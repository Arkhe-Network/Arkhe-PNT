import numpy as np
import os
import sys
import json
import time

# Use PYTHONPATH or proper package structure
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.physics.sasc_em_engine import SASCEMEngine
from src.physics.sasc_phase_slam import Heaviside3DScene, PhaseCoherenceSLAM
from scripts.avatar.safe_start import KuramotoCouplingMatrix, CentralPatternGenerator

def run_smg_001():
    print("🚶 INICIANDO SMG-001: MARCHA GUIADA POR FASE")
    print("-" * 60)

    # 1. Initialize Engines
    scene_engine = Heaviside3DScene()
    slam = PhaseCoherenceSLAM(scene_engine)
    coupling = KuramotoCouplingMatrix()
    cpg = CentralPatternGenerator(coupling)
    # Add noise to break symmetry for Kuramoto synchronization
    cpg.theta = np.random.uniform(0, 2*np.pi, cpg.n)
    cpg.running = True

    # 2. Simulate Corridor with Obstacles
    corridor_length = 100 # units
    avatar_pos = 0.0
    velocity = 0.3
    dt = 0.01

    # Obstacles at 30, 60, 80
    obstacles = [30, 60, 80]

    path_coherence = []
    cpg_coherence = []

    print("[*] Traversing Corridor...")

    # Pre-sync CPG to avoid starting at 0.0 coherence
    for _ in range(500):
        cpg.step(dt=0.01)

    for t in range(int(corridor_length / (velocity * dt))):
        avatar_pos += velocity * dt

        # Local geometry perception (Radar 60GHz)
        local_geo = np.zeros((64, 64))
        # Left wall (drywall)
        local_geo[:, :5] = 0.6
        # Right wall (glass)
        local_geo[:, 59:] = 0.9

        for obs in obstacles:
            if abs(avatar_pos - obs) < 5:
                # Obstacle detected in range
                row = int(32 + 10 * np.sin(avatar_pos)) # Simulating some relative position
                col = int(32 + (obs - avatar_pos) * 4)
                if 0 <= col < 64:
                    local_geo[row-2:row+2, col-2:col+2] = 1.0

        # Update SLAM
        slam_update = slam.update(local_geo, 60e9)
        path_coherence.append(slam_update['local_coherence'])

        # Adjust CPG based on navigation
        # If low coherence/obstacle, reduce omega (speed) or adjust coupling
        if not slam_update['safe_to_navigate']:
            correction = np.ones(12) * -0.5 # Slow down
        else:
            correction = None

        cpg.step(dt=dt, balance_correction=correction)
        cpg_coherence.append(cpg.lambda2_cpg)

        if int(avatar_pos) % 20 == 0 and (avatar_pos % 1 < 0.1):
             print(f"    - Pos: {avatar_pos:.1f}m | Amb.L2: {slam_update['local_coherence']:.3f} | CPG.L2: {cpg.lambda2_cpg:.4f}")

    print("-" * 60)
    print("📊 RELATÓRIO DE ESTABILIDADE DE TRAJETÓRIA (SMG-001)")
    print(f"    - Status: SUCCESS")
    print(f"    - Média Amb. L2: {np.mean(path_coherence):.4f}")
    print(f"    - Média CPG L2: {np.mean(cpg_coherence):.4f}")
    print(f"    - Nodes do Grafo SLAM: {len(slam.state.graph_nodes)}")

    report = {
        "simulation": "SMG-001",
        "avatar_pos": avatar_pos,
        "avg_path_l2": float(np.mean(path_coherence)),
        "avg_cpg_l2": float(np.mean(cpg_coherence)),
        "graph_nodes": len(slam.state.graph_nodes),
        "status": "COMPLETED"
    }

    with open("smg_001_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n[+] Relatório SMG-001 salvo.")

if __name__ == "__main__":
    run_smg_001()
