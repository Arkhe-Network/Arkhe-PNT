import torch
from redistributor import PhaseGradientRedistributor, redistribute_dynamic_coupling
import numpy as np

def simulate_healing():
    print("🜏 [HEALING] Starting Rio Recovery Simulation...")
    n = 1000
    dist_mask = (torch.rand(n, n) > 0.95).float()

    model = PhaseGradientRedistributor(n, dist_mask)
    phases = torch.rand(n) * 2 * torch.pi

    # EMP Attack: 20% failure
    alive_mask = torch.ones(n)
    alive_mask[:200] = 0

    # Initial R
    cos_sum = torch.mean(torch.cos(phases))
    sin_sum = torch.mean(torch.sin(phases))
    R_post_emp = torch.sqrt(cos_sum**2 + sin_sum**2).item()
    print(f"  > R (Post-EMP): {R_post_emp:.4f}")

    # Healing
    print("  > Running Autonomic Healing...")
    K_new, phases_new = redistribute_dynamic_coupling(model, phases, alive_mask, steps=50)

    # Final R
    cos_sum = torch.mean(torch.cos(phases_new))
    sin_sum = torch.mean(torch.sin(phases_new))
    R_healed = torch.sqrt(cos_sum**2 + sin_sum**2).item()
    print(f"  > R (Healed): {R_healed:.4f}")

    if R_healed > R_post_emp:
        print("✅ SUCCESS: Network healed.")
    else:
        print("❌ FAILURE: Coherence did not improve.")

if __name__ == "__main__":
    simulate_healing()
