"""
Sacred Geometry Foundation — Substrate 90 Enhancement
Mathematical basis for parabolic hexagonal cavity with six coherent waves.

Geometric Principles:
• Hexagon: 6-fold rotational symmetry, φ-related proportions
• Parabola: z = depth·(r/radius)², focus-directrix property
• Wave Interference: Superposition of 6 coherent modes with hexagonal k-vectors
• Coherence Isosurface: |Ψ| = threshold defines topological structure
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class HexagonalCavityParams:
    """Parameters defining the sacred geometry cavity."""
    # Hexagon geometry
    radius: float = 1.0           # Circumradius of hexagon
    side_length: float = None     # Derived: radius (for regular hexagon)

    # Parabolic profile
    depth: float = 0.5            # Maximum z at center
    focus_distance: float = None  # Derived: radius²/(4·depth)

    # Wave parameters (6 coherent modes)
    base_frequency: float = 2.0   # Base angular frequency ω₀
    amplitude_balance: float = 1.0  # 1.0 = equal amplitudes, <1 = imbalanced
    phase_coherence: float = 1.0   # 1.0 = aligned phases, <1 = dispersed

    # Coupling
    nonlinear_coupling: float = 0.1  # Strength of mode-mode coupling

    def __post_init__(self):
        if self.side_length is None:
            self.side_length = self.radius  # Regular hexagon
        if self.focus_distance is None:
            self.focus_distance = self.radius**2 / (4 * self.depth) if self.depth > 0 else float('inf')

    def hex_vertices(self) -> np.ndarray:
        """Compute 2D vertices of regular hexagon."""
        angles = np.arange(6) * np.pi / 3  # 0, 60°, 120°, ..., 300°
        return np.array([
            [self.radius * np.cos(a), self.radius * np.sin(a)]
            for a in angles
        ])

    def wave_k_vectors(self) -> np.ndarray:
        """Compute wave vectors for 6 hexagonal directions."""
        # k-vectors point along hexagon symmetry axes
        angles = np.arange(6) * np.pi / 3 + np.pi / 6  # Offset by 30°
        return np.array([
            [np.cos(a), np.sin(a)] * self.base_frequency
            for a in angles
        ])

    def parabolic_profile(self, xy: np.ndarray) -> np.ndarray:
        """Compute z = depth·(r/radius)² for points in xy-plane."""
        r = np.linalg.norm(xy, axis=-1, keepdims=True)
        r_clamped = np.clip(r / self.radius, 0, 1)
        return self.depth * r_clamped**2
