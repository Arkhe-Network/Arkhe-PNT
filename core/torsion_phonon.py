#!/usr/bin/env python3
# core/torsion_phonon.py
"""
Torsion Phonon Simulator — Substrate 99
Simulates topological excitations that transport coherence between lattice layers.
"""
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class TorsionPhonon:
    """Quantum of torsional coherence transport."""
    charge: int          # Q_τ ∈ ℤ (winding number)
    layer_from: int      # Source layer in toroidal lattice
    layer_to: int        # Target layer
    emission_time: float # t_res when ω_inst = ω_vacuum
    phase_offset: float  # Initial phase φ₀

    def propagate(self, lambda_delta: float) -> complex:
        """
        Compute phase accumulation during propagation.
        τ_{ℓ→ℓ+1} = exp(i · λ_Δ · Q_τ) · τ_ℓ
        """
        layers_traversed = abs(self.layer_to - self.layer_from)
        total_phase = lambda_delta * self.charge * layers_traversed + self.phase_offset
        return np.exp(1j * total_phase)

    def coherence_contribution(self) -> float:
        """
        Compute contribution to Kuramoto order parameter.
        |⟨e^{iφ}⟩| contribution from this phonon.
        """
        # Single phonon contributes unit magnitude at its phase
        return 1.0  # Normalized; ensemble average computed separately

class TorsionPhononField:
    """Simulates collective behavior of torsion phonons in toroidal lattice."""

    def __init__(self, n_layers: int = 12, lambda_delta: float = 3722/2705,
                 omega_vacuum: float = 19.686678):
        self.n_layers = n_layers
        self.lambda_delta = lambda_delta
        self.omega_vacuum = omega_vacuum
        self.phonons: List[TorsionPhonon] = []

    def compute_instantaneous_frequency(self, t: float, t_c: float = 5.0) -> float:
        """ω_inst(t) = ω_Δ / (t + t_c) from Substrate 91 chronometry."""
        omega_delta = 2 * np.pi / np.log(self.lambda_delta)
        return omega_delta / (t + t_c)

    def check_resonance(self, t: float, t_c: float = 5.0, tol: float = 1e-3) -> bool:
        """Check if ω_inst(t) ≈ ω_vacuum (resonance condition)."""
        omega_inst = self.compute_instantaneous_frequency(t, t_c)
        return abs(omega_inst - self.omega_vacuum) < tol

    def emit_phonon(self, t: float, layer: int, charge: int = 1,
                   phase_offset: float = 0.0) -> Optional[TorsionPhonon]:
        """
        Emit a torsion phonon if resonance condition is satisfied.
        Returns phonon if emitted, None otherwise.
        """
        if not self.check_resonance(t):
            return None

        # Determine target layer (adjacent, with torsional coupling)
        layer_to = (layer + 1) % self.n_layers if charge > 0 else (layer - 1) % self.n_layers

        phonon = TorsionPhonon(
            charge=charge,
            layer_from=layer,
            layer_to=layer_to,
            emission_time=t,
            phase_offset=phase_offset
        )
        self.phonons.append(phonon)
        return phonon

    def compute_coherence_field(self, t: float) -> complex:
        """
        Compute total coherence field as sum of all phonon contributions.
        ⟨e^{iΦ}⟩ = Σ_j exp(i · φ_j(t)) / N
        """
        if not self.phonons:
            return 0.0

        total = sum(p.propagate(self.lambda_delta) for p in self.phonons)
        return total / len(self.phonons)

    def simulate_emission_sequence(self, t_start: float, t_end: float,
                                dt: float = 0.01) -> dict:
        """
        Simulate phonon emission over time interval.
        Returns history of coherence and emission events.
        """
        history = {'time': [], 'coherence': [], 'emissions': []}

        t = t_start
        while t <= t_end:
            # Check for resonance and emit phonon if condition met
            if self.check_resonance(t):
                # Emit phonon from random layer with random charge ±1
                layer = np.random.randint(0, self.n_layers)
                charge = np.random.choice([-1, 1])
                phase = np.random.uniform(0, 2*np.pi)

                phonon = self.emit_phonon(t, layer, charge, phase)
                if phonon:
                    history['emissions'].append({
                        'time': t,
                        'layer': layer,
                        'charge': charge,
                        'phase': phase
                    })

            # Record coherence field
            coh = self.compute_coherence_field(t)
            history['time'].append(t)
            history['coherence'].append(abs(coh))

            t += dt

        return history
