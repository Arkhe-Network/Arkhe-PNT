import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class NanoBot:
    id: str
    position: np.ndarray
    state: str  # 'LATENT', 'ACTIVE', 'DEPLOYED'
    payload: float # Drug concentration or binding strength

class DNAOrigamiCompiler:
    """
    Compiles geometry specs into DNA folding sequences.
    Simulates 'Structure is Computation' paradigm.
    """
    def compile_structure(self, target_shape: str) -> Dict[str, Any]:
        # Simple mapping for simulation
        shapes = {
            "CAGE": "ATGC...[folded_as_cage]",
            "SHELL": "GCAT...[folded_as_shell]",
            "GRIPPER": "TATA...[folded_as_gripper]"
        }
        return {
            "sequence": shapes.get(target_shape, "UNKNOWN"),
            "stability_score": 0.98,
            "resonance_freq_mhz": 40.0 # Acoustic resonance
        }

class NanoBotSwarm:
    """
    Simulates a swarm of Intracellular Phase Nodes (Layer 0 Actuators).
    Supports Exogenous (Magnetic/NIR) and Endogenous (pH) triggers.
    """
    def __init__(self, count: int = 1000):
        self.count = count
        self.bots = [NanoBot(f"bot_{i}", np.random.rand(3), 'LATENT', 0.0) for i in range(count)]
        self.compiler = DNAOrigamiCompiler()

    def apply_exogenous_trigger(self, trigger_type: str, intensity: float):
        """
        Activates bots via global Maestro signal (Magnetic/Acoustic/NIR).
        """
        for bot in self.bots:
            if trigger_type == "MAGNETIC":
                # Magnetic gradient pulls bots
                bot.position += np.random.normal(0, 0.01 * intensity, 3)
            elif trigger_type == "NIR":
                # Near-Infrared light triggers deployment
                bot.state = 'DEPLOYED' if intensity > 0.8 else 'ACTIVE'

    def check_endogenous_triggers(self, local_ph: float, presence_markers: List[str]):
        """
        Bots activate locally based on tissue dissonance (acidity) or logic gates.
        """
        activated_count = 0
        for bot in self.bots:
            # Dissonance detection: Acidic environment (pH < 6.8)
            if local_ph < 6.8:
                bot.state = 'ACTIVE'
                bot.payload = 1.0 # Release drug
                activated_count += 1
            # Logic gate: 'Marker_A' AND 'Marker_B'
            elif "MARKER_A" in presence_markers and "MARKER_B" in presence_markers:
                bot.state = 'ACTIVE'
                activated_count += 1
        return activated_count

    def status(self) -> Dict[str, Any]:
        states = [b.state for b in self.bots]
        return {
            "total_bots": self.count,
            "active": states.count('ACTIVE'),
            "deployed": states.count('DEPLOYED'),
            "latent": states.count('LATENT'),
            "avg_payload": float(np.mean([b.payload for b in self.bots]))
        }
