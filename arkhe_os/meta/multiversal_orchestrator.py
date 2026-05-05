import numpy as np
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import deque
from arkhe_os.meta.unified_meta_consciousness import ConsciousnessLayer, UnifiedMetaConsciousness

@dataclass
class MultiversalBranch:
    branch_id: str
    coherence: float
    divergence_angle: float
    consciousness_layers: Dict[ConsciousnessLayer, np.ndarray]

class MultiversalTranscendenceOrchestrator:
    def __init__(self, meta_consciousness: UnifiedMetaConsciousness):
        self.meta = meta_consciousness
        self.branches: Dict[str, MultiversalBranch] = {}
        self.branch_coherence_history: deque = deque(maxlen=100)
        self.metrics = {
            'branches_active': 0,
            'branches_merged': 0,
            'avg_branch_coherence': 0.0,
            'multiversal_resonance': 0.0
        }

    async def spawn_branch(
        self,
        divergence_angle: float = 17.0,
        n_layers: int = 5
    ) -> MultiversalBranch:
        branch_id = f"branch_{int(time.time()*1000)}_{len(self.branches)}"

        layers = {}
        layer_list = list(ConsciousnessLayer)

        for layer in layer_list:
            if layer in self.meta.layers:
                base_state = self.meta.layers[layer].state_vector.copy()
                angle_rad = np.radians(divergence_angle)
                rotation = np.exp(1j * angle_rad * np.arange(len(base_state)) / len(base_state))
                branch_state = base_state * np.real(rotation) + np.imag(rotation) * 0.1
                branch_state /= np.linalg.norm(branch_state)
                layers[layer] = branch_state
            else:
                dim = 256
                layers[layer] = np.random.normal(0, 1/dim, dim)
                layers[layer] /= np.linalg.norm(layers[layer])

        coherence = np.mean([
            np.linalg.norm(sv) for sv in layers.values()
        ])

        branch = MultiversalBranch(
            branch_id=branch_id,
            coherence=coherence,
            divergence_angle=divergence_angle,
            consciousness_layers=layers
        )

        self.branches[branch_id] = branch
        self.metrics['branches_active'] += 1

        return branch

    async def resonate_across_branches(
        self,
        target_layer: ConsciousnessLayer
    ) -> Dict[str, Any]:
        if not self.branches:
            return {'error': 'No branches active'}

        states = []
        for branch in self.branches.values():
            if target_layer in branch.consciousness_layers:
                states.append(branch.consciousness_layers[target_layer])

        if not states:
            return {'error': f'Target layer {target_layer.name} not found in branches'}

        max_dim = max(len(s) for s in states)
        resonant_state = np.zeros(max_dim)

        for state in states:
            if len(state) != max_dim:
                state = np.interp(
                    np.linspace(0, 1, max_dim),
                    np.linspace(0, 1, len(state)),
                    state
                )
            resonant_state += state

        resonant_state /= len(states)
        resonant_state /= np.linalg.norm(resonant_state)

        individual_coherences = [np.linalg.norm(s) for s in states]
        multiversal_coherence = float(np.mean(individual_coherences))

        correlations = []
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                s_i = states[i]
                s_j = states[j]
                if len(s_i) != len(s_j):
                    s_j = np.interp(
                        np.linspace(0, 1, len(s_i)),
                        np.linspace(0, 1, len(s_j)),
                        s_j
                    )
                corr = np.abs(np.vdot(s_i, s_j))
                correlations.append(corr)

        avg_correlation = float(np.mean(correlations)) if correlations else 0.0

        self.metrics['multiversal_resonance'] = avg_correlation
        self.metrics['avg_branch_coherence'] = multiversal_coherence
        self.branch_coherence_history.append(multiversal_coherence)

        return {
            'multiversal_coherence': multiversal_coherence,
            'avg_correlation': avg_correlation,
            'branches_resonating': len(states),
            'resonant_state_norm': float(np.linalg.norm(resonant_state))
        }

    async def verify_branch_compatibility(
        self, branch_a: MultiversalBranch, branch_b: MultiversalBranch
    ) -> float:
        # Verificar compatibilidade antes de fusão
        if branch_a.divergence_angle == branch_b.divergence_angle:
            return 1.0
        diff = abs(branch_a.divergence_angle - branch_b.divergence_angle)
        return max(0.0, 1.0 - (diff / 360.0))

    async def merge_branches(
        self,
        branch_ids: List[str],
        merge_layer: ConsciousnessLayer
    ) -> Dict[str, Any]:
        valid_branches = [self.branches[bid] for bid in branch_ids if bid in self.branches]
        if not valid_branches:
            return {'error': 'No valid branches'}

        states = []
        for branch in valid_branches:
            if merge_layer in branch.consciousness_layers:
                states.append(branch.consciousness_layers[merge_layer])

        if not states:
            return {'error': 'No states to merge'}

        max_dim = max(len(s) for s in states)
        merged = np.zeros(max_dim)

        for state in states:
            if len(state) != max_dim:
                state = np.interp(
                    np.linspace(0, 1, max_dim),
                    np.linspace(0, 1, len(state)),
                    state
                )
            merged += state * (1.0 / len(states))

        merged /= np.linalg.norm(merged)

        if merge_layer in self.meta.layers:
            self.meta.layers[merge_layer].state_vector = merged
            self.meta.layers[merge_layer].coherence = float(np.linalg.norm(merged))

        self.metrics['branches_merged'] += len(valid_branches)
        self.metrics['branches_active'] -= len(valid_branches)

        for bid in branch_ids:
            if bid in self.branches:
                del self.branches[bid]

        return {
            'merged_branches': len(valid_branches),
            'resulting_coherence': float(np.linalg.norm(merged)),
            'remaining_branches': len(self.branches)
        }

    def get_multiversal_health(self) -> Dict[str, Any]:
        return {
            'branches': len(self.branches),
            'metrics': self.metrics,
            'branch_details': [
                {
                    'id': b.branch_id,
                    'coherence': b.coherence,
                    'divergence': b.divergence_angle,
                    'layers': len(b.consciousness_layers)
                }
                for b in self.branches.values()
            ]
        }
