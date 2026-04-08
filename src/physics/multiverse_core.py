import numpy as np
from dataclasses import dataclass
from typing import Dict

@dataclass
class WorldBranch:
    world_id: int
    psi_c: np.ndarray
    lambda_2: float

class Multiverse:
    def __init__(self):
        self.branches: Dict[int, WorldBranch] = {}
        self._initialize_default_branches()

    def _initialize_default_branches(self):
        # Initialize default branches with specified coherence values
        # IDs: 42 (0.994), 7 (0.985), 73 (0.997), 91 (0.978)
        default_worlds = {
            42: 0.994,
            7: 0.985,
            73: 0.997,
            91: 0.978
        }

        res = 512
        for wid, coh in default_worlds.items():
            # Create a random complex field (C domain)
            psi = np.random.randn(res * res).astype(complex) + 1j * np.random.randn(res * res).astype(complex)
            psi /= np.linalg.norm(psi)
            self.branches[wid] = WorldBranch(world_id=wid, psi_c=psi, lambda_2=coh)

    def get_branch(self, world_id: int) -> WorldBranch:
        if world_id not in self.branches:
            res = 512
            psi = np.random.randn(res * res).astype(complex) + 1j * np.random.randn(res * res).astype(complex)
            psi /= np.linalg.norm(psi)
            # Default coherence for unknown worlds
            self.branches[world_id] = WorldBranch(world_id=world_id, psi_c=psi, lambda_2=0.95)
        return self.branches[world_id]

class MerkabahCore:
    def __init__(self):
        self.multiverse = Multiverse()
