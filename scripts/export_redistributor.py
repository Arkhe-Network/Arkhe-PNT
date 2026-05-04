import torch
import torch.nn as nn
import numpy as np
from redistributor import PhaseGradientRedistributor

def export():
    print("🜏 [EXPORT] Initializing export pipeline...")
    n_nodes = 1000
    dist_mask = (torch.rand(n_nodes, n_nodes) > 0.95).float()

    model = PhaseGradientRedistributor(n_nodes, dist_mask)

    # Create dummy inputs for tracing
    phases_dummy = torch.rand(n_nodes) * 2 * np.pi
    alive_dummy = torch.ones(n_nodes)

    # 1. Traced Export
    print("  > Tracing model...")
    traced_model = torch.jit.trace(model, (phases_dummy, alive_dummy))
    traced_model.save("redistributor_traced.pt")
    print("✅ Exported: redistributor_traced.pt")

    # 2. Scripted Export
    print("  > Scripting model...")
    scripted_model = torch.jit.script(model)
    scripted_model.save("redistributor_scripted.pt")
    print("✅ Exported: redistributor_scripted.pt")

if __name__ == "__main__":
    export()
