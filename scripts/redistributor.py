import torch
import torch.nn as nn
import numpy as np

class PhaseGradientRedistributor(nn.Module):
    """
    Trainable neural module to dynamically adjust Tzinor coupling weights (K)
    to maximize global coherence (R) after node failures.
    """
    def __init__(self, n_nodes, dist_mask, initial_k=1.5, sparse_weight=0.01):
        super().__init__()
        self.n_nodes = n_nodes
        self.sparse_weight = sparse_weight

        # Trainable coupling matrix K
        self.K = nn.Parameter(torch.full((n_nodes, n_nodes), initial_k))

        # Distance mask: physical constraints on connectivity
        self.register_buffer('dist_mask', dist_mask)

    def forward(self, phases, alive_mask):
        """
        Calculates global coherence (R) and phase derivatives.
        """
        # Expand phases to calculate differences (phi_j - phi_i)
        phi_i = phases.unsqueeze(1)
        phi_j = phases.unsqueeze(0)
        phase_diff = phi_j - phi_i

        # Effective connectivity: physical distance AND node status (EMP)
        effective_mask = alive_mask.unsqueeze(1) * alive_mask.unsqueeze(0) * self.dist_mask

        # Kuramoto coupling term
        coupling = torch.sum(self.K * effective_mask * torch.sin(phase_diff), dim=1)

        # Order parameter R (Global Coherence)
        # Using real/imag parts for script compatibility
        cos_sum = torch.mean(torch.cos(phases))
        sin_sum = torch.mean(torch.sin(phases))
        R = torch.sqrt(cos_sum**2 + sin_sum**2)

        # Loss function: Maximize coherence, minimize total coupling energy (L2 + L1)
        loss = (1.0 - R) + 0.01 * torch.norm(self.K) + self.sparse_weight * torch.norm(self.K, p=1)

        # Derivative dtheta/dt
        dtheta = coupling

        return R, dtheta, loss

def redistribute_dynamic_coupling(model, phases, alive_mask, steps=50, dt=0.1):
    """Executes gradient-based optimization of matrix K."""
    optimizer = torch.optim.Adam([model.K], lr=0.05)

    phases_working = phases.clone().detach()

    for step in range(steps):
        optimizer.zero_grad()
        R, dtheta, loss = model(phases_working, alive_mask)
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            model.K.clamp_(0.1, 5.0)
            phases_working = (phases_working + dtheta * dt) % (2 * torch.pi)

        if step % 10 == 0:
            print(f"  > Step {step}: R={R.item():.4f}, K_avg={model.K.mean().item():.4f}")

    return model.K.detach(), phases_working.detach()
