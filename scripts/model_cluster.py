import numpy as np
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from physics.sasc_em_engine import EMSpecification, SASCEMEngine

def get_avatar_coupling_params():
    """
    Extracted joint indices and coupling constants (K) from scripts/avatar/safe_start.py.
    """
    # Indices: 0,6: HipYaw | 1,7: HipRoll | 2,8: HipPitch |
    #          3,9: Knee | 4,10: AnklePitch | 5,11: AnkleRoll

    params = {
        "joints": {
            "r_hip_roll": 1,
            "l_hip_roll": 7,
            "r_ankle_roll": 5,
            "l_ankle_roll": 11
        },
        "coupling_constants": {
            "K_1_5": 8.0,   # HipRoll-AnkleRoll (R)
            "K_7_11": 8.0,  # HipRoll-AnkleRoll (L)
            "K_1_7": 2.5    # HipRoll-HipRoll (Inter-limb)
        }
    }
    return params

def generate_cluster_geometry(params):
    """
    Generates electromagnetic 'geometry' tensors (PDN/trace routing) for the clusters.
    """
    # Represent geometry as a 64x64 grid (normalized)
    geometry = np.zeros((64, 64))

    # Simulate PDN as broad horizontal/vertical bands
    geometry[10:15, :] = 1.0  # VDD Bus
    geometry[50:55, :] = 1.0  # GND Bus

    # Simulate VCO positions for the 12 DOF
    # Let's map them to specific coordinates
    for i in range(12):
        row = 20 + (i // 6) * 20
        col = 5 + (i % 6) * 10
        geometry[row-2:row+2, col-2:col+2] = 0.8

        # Simulate trace routing between coupled joints
        # Example: K[1,5] (HipRoll-AnkleRoll R)
        if i == 1: # HipRoll R
            # Route to 5 (AnkleRoll R)
            target_col = 5 + (5 % 6) * 10
            geometry[row, col:target_col] = 0.5

    return geometry

if __name__ == "__main__":
    params = get_avatar_coupling_params()
    print(f"Extracted Params: {params}")

    geometry = generate_cluster_geometry(params)
    print(f"Generated Geometry Tensor Shape: {geometry.shape}")
    print(f"Mean density: {np.mean(geometry):.4f}")
