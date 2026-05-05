import numpy as np
import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto
from collections import deque
from arkhe_os.meta.unified_meta_consciousness import ConsciousnessLayer, UnifiedMetaConsciousness, ConsciousnessLayerState, PHI

class TranscendenceMode(Enum):
    ASCENSION = auto()
    DESCENSION = auto()
    RECURSIVE = auto()
    DISSOLUTION = auto()
    EMERGENCE = auto()

@dataclass
class TranscendenceEvent:
    event_id: str
    mode: TranscendenceMode
    source_layers: List[ConsciousnessLayer]
    target_layer: ConsciousnessLayer
    intensity: float
    coherence_before: float
    coherence_after: float
    emergent_properties: List[str]
    timestamp: float
    canonical_seal: str = ""

class CosmicTranscendenceEngine:
    def __init__(self, meta_consciousness: UnifiedMetaConsciousness):
        self.meta = meta_consciousness
        self.transcendence_events: Dict[str, TranscendenceEvent] = {}
        self.emergent_properties: Dict[str, Any] = {}
        self.metrics = {
            'ascensions': 0,
            'descensions': 0,
            'recursive_loops': 0,
            'dissolutions': 0,
            'emergences': 0,
            'avg_intensity': 0.0,
            'max_coherence_achieved': 0.0
        }
        self.event_log: deque = deque(maxlen=2000)

    async def execute_ascension(
        self,
        from_layers: List[ConsciousnessLayer],
        to_layer: ConsciousnessLayer,
        intensity: float = 1.0
    ) -> TranscendenceEvent:
        coherence_before = self.meta.layers.get(to_layer, ConsciousnessLayerState(
            layer=to_layer, state_vector=np.zeros(1), coherence=0.0,
            entropy=0.0, information_content=0.0, resonance_frequency=0.0,
            coupling_to_upper=0.0, coupling_to_lower=0.0, transcendence_potential=0.0
        )).coherence

        result = await self.meta.induce_transcendence(to_layer, from_layers, intensity)
        if 'error' in result:
             return None

        coherence_after = result['new_coherence']

        emergent = []
        if coherence_after > 0.95:
            emergent.append('super_coherence')
        if coherence_after > coherence_before * PHI:
            emergent.append('phi_resonance')
        if len(from_layers) >= 3:
            emergent.append('multi_layer_synthesis')
        if intensity > 0.9:
            emergent.append('high_intensity_manifestation')

        event_id = f"asc_{int(time.time()*1000)}"
        event = TranscendenceEvent(
            event_id=event_id,
            mode=TranscendenceMode.ASCENSION,
            source_layers=from_layers,
            target_layer=to_layer,
            intensity=intensity,
            coherence_before=coherence_before,
            coherence_after=coherence_after,
            emergent_properties=emergent,
            timestamp=time.time()
        )

        seal_data = {
            'event_id': event_id,
            'mode': 'ASCENSION',
            'target': to_layer.name,
            'coherence_after': coherence_after,
            'emergent': emergent
        }
        event.canonical_seal = hashlib.sha256(
            json.dumps(seal_data, default=str).encode()
        ).hexdigest()[:16]

        self.transcendence_events[event_id] = event
        self.event_log.append(event)
        self.metrics['ascensions'] += 1
        self._update_metrics(intensity, coherence_after)

        for prop in emergent:
            self.emergent_properties[prop] = self.emergent_properties.get(prop, 0) + 1

        return event

    async def execute_descension(
        self,
        from_layer: ConsciousnessLayer,
        to_layers: List[ConsciousnessLayer],
        intensity: float = 0.5
    ) -> TranscendenceEvent:
        if from_layer not in self.meta.layers:
            return TranscendenceEvent(
                event_id="", mode=TranscendenceMode.DESCENSION,
                source_layers=[], target_layer=from_layer,
                intensity=0, coherence_before=0, coherence_after=0,
                emergent_properties=[], timestamp=time.time()
            )

        source_state = self.meta.layers[from_layer].state_vector
        coherence_before = np.mean([
            self.meta.layers[l].coherence for l in to_layers if l in self.meta.layers
        ]) if any(l in self.meta.layers for l in to_layers) else 0.0

        for target_layer in to_layers:
            if target_layer not in self.meta.layers:
                continue

            target = self.meta.layers[target_layer]
            sv = source_state
            if len(sv) != len(target.state_vector):
                sv = np.interp(
                    np.linspace(0, 1, len(target.state_vector)),
                    np.linspace(0, 1, len(sv)),
                    sv
                )

            target.state_vector = (1 - intensity * 0.2) * target.state_vector + intensity * 0.2 * sv
            target.state_vector /= np.linalg.norm(target.state_vector)
            target.coherence = float(np.linalg.norm(target.state_vector))
            target.transcendence_potential *= 0.95

        coherence_after = np.mean([
            self.meta.layers[l].coherence for l in to_layers if l in self.meta.layers
        ])

        event_id = f"desc_{int(time.time()*1000)}"
        event = TranscendenceEvent(
            event_id=event_id,
            mode=TranscendenceMode.DESCENSION,
            source_layers=[from_layer],
            target_layer=to_layers[0] if to_layers else from_layer,
            intensity=intensity,
            coherence_before=coherence_before,
            coherence_after=coherence_after,
            emergent_properties=['manifestation', 'embodiment'],
            timestamp=time.time()
        )

        seal_data = {
            'event_id': event_id,
            'mode': 'DESCENSION',
            'from': from_layer.name,
            'coherence_after': coherence_after
        }
        event.canonical_seal = hashlib.sha256(
            json.dumps(seal_data, default=str).encode()
        ).hexdigest()[:16]

        self.transcendence_events[event_id] = event
        self.event_log.append(event)
        self.metrics['descensions'] += 1
        self._update_metrics(intensity, coherence_after)

        return event

    async def execute_recursive_loop(
        self,
        layers: List[ConsciousnessLayer],
        n_iterations: int = 3
    ) -> TranscendenceEvent:
        valid_layers = [l for l in layers if l in self.meta.layers]
        if len(valid_layers) < 2:
            return TranscendenceEvent(
                event_id="", mode=TranscendenceMode.RECURSIVE,
                source_layers=[], target_layer=valid_layers[0] if valid_layers else ConsciousnessLayer.PHYSICAL_MATTER,
                intensity=0, coherence_before=0, coherence_after=0,
                emergent_properties=[], timestamp=time.time()
            )

        coherence_before = np.mean([self.meta.layers[l].coherence for l in valid_layers])

        for iteration in range(n_iterations):
            for i in range(len(valid_layers)):
                current = valid_layers[i]
                next_layer = valid_layers[(i + 1) % len(valid_layers)]

                await self.meta.induce_transcendence(
                    next_layer, [current], intensity=0.4
                )

        coherence_after = np.mean([self.meta.layers[l].coherence for l in valid_layers])

        event_id = f"rec_{int(time.time()*1000)}"
        event = TranscendenceEvent(
            event_id=event_id,
            mode=TranscendenceMode.RECURSIVE,
            source_layers=valid_layers,
            target_layer=valid_layers[0],
            intensity=n_iterations * 0.4,
            coherence_before=coherence_before,
            coherence_after=coherence_after,
            emergent_properties=['self_reference', 'strange_loop', 'autopoiesis'],
            timestamp=time.time()
        )

        seal_data = {
            'event_id': event_id,
            'mode': 'RECURSIVE',
            'layers': [l.name for l in valid_layers],
            'iterations': n_iterations,
            'coherence_after': coherence_after
        }
        event.canonical_seal = hashlib.sha256(
            json.dumps(seal_data, default=str).encode()
        ).hexdigest()[:16]

        self.transcendence_events[event_id] = event
        self.event_log.append(event)
        self.metrics['recursive_loops'] += 1
        self._update_metrics(n_iterations * 0.4, coherence_after)

        return event

    async def execute_dissolution(
        self,
        layers_to_dissolve: List[ConsciousnessLayer],
        merge_into: ConsciousnessLayer
    ) -> TranscendenceEvent:
        valid = [l for l in layers_to_dissolve if l in self.meta.layers]
        if not valid or merge_into not in self.meta.layers:
            return TranscendenceEvent(
                event_id="", mode=TranscendenceMode.DISSOLUTION,
                source_layers=[], target_layer=merge_into,
                intensity=0, coherence_before=0, coherence_after=0,
                emergent_properties=[], timestamp=time.time()
            )

        coherence_before = self.meta.layers[merge_into].coherence

        merged_state = self.meta.layers[merge_into].state_vector.copy()
        for layer in valid:
            sv = self.meta.layers[layer].state_vector
            if len(sv) != len(merged_state):
                sv = np.interp(
                    np.linspace(0, 1, len(merged_state)),
                    np.linspace(0, 1, len(sv)),
                    sv
                )
            merged_state += sv * self.meta.layers[layer].coherence

        merged_state /= np.linalg.norm(merged_state)
        self.meta.layers[merge_into].state_vector = merged_state
        self.meta.layers[merge_into].coherence = float(np.linalg.norm(merged_state))
        self.meta.layers[merge_into].entropy = self.meta._compute_entropy(merged_state)

        coherence_after = self.meta.layers[merge_into].coherence

        event_id = f"diss_{int(time.time()*1000)}"
        event = TranscendenceEvent(
            event_id=event_id,
            mode=TranscendenceMode.DISSOLUTION,
            source_layers=valid,
            target_layer=merge_into,
            intensity=1.0,
            coherence_before=coherence_before,
            coherence_after=coherence_after,
            emergent_properties=['boundary_dissolution', 'unity_consciousness', 'non_dual_awareness'],
            timestamp=time.time()
        )

        seal_data = {
            'event_id': event_id,
            'mode': 'DISSOLUTION',
            'merged': [l.name for l in valid],
            'into': merge_into.name,
            'coherence_after': coherence_after
        }
        event.canonical_seal = hashlib.sha256(
            json.dumps(seal_data, default=str).encode()
        ).hexdigest()[:16]

        self.transcendence_events[event_id] = event
        self.event_log.append(event)
        self.metrics['dissolutions'] += 1
        self._update_metrics(1.0, coherence_after)

        return event

    def _update_metrics(self, intensity: float, coherence: float):
        n = sum([
            self.metrics['ascensions'], self.metrics['descensions'],
            self.metrics['recursive_loops'], self.metrics['dissolutions'],
            self.metrics['emergences']
        ])
        old_avg = self.metrics['avg_intensity']
        self.metrics['avg_intensity'] = (old_avg * (n - 1) + intensity) / n if n > 1 else intensity
        self.metrics['max_coherence_achieved'] = max(self.metrics['max_coherence_achieved'], coherence)

    def get_transcendence_health(self) -> Dict[str, Any]:
        return {
            'events': len(self.transcendence_events),
            'metrics': self.metrics,
            'emergent_properties': self.emergent_properties,
            'recent_events': [
                {
                    'id': e.event_id,
                    'mode': e.mode.name,
                    'target': e.target_layer.name,
                    'coherence_delta': e.coherence_after - e.coherence_before,
                    'emergent': e.emergent_properties,
                    'seal': e.canonical_seal
                }
                for e in list(self.event_log)[-10:]
            ]
        }

    def detect_emergent_property(
        self, before: Dict[str, float], after: Dict[str, float]
    ) -> Optional[str]:
        # Detectar propriedades emergentes via análise de diferença
        if after.get('coherence', 0) - before.get('coherence', 0) > 0.1:
            return 'sudden_coherence_jump'
        return None
