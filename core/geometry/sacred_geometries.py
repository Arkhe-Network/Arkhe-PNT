"""
Sacred Geometries Foundation — Extensions to Substrate 90
Mathematical basis for polyhedral cavities (Tetrahedron, Cuboctahedron, Icosahedron).
"""
import numpy as np
from dataclasses import dataclass

@dataclass
class SacredTetrahedronParams:
    """4-wave geometry."""
    radius: float = 1.0
    depth: float = 0.5
    base_frequency: float = 2.0

    def wave_k_vectors(self) -> np.ndarray:
        # Tetrahedron vertices directions
        v = np.array([
            [1.0, 1.0, 1.0],
            [1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, -1.0, 1.0]
        ]) / np.sqrt(3)
        return v[:, :2] * self.base_frequency

@dataclass
class SacredCuboctahedronParams:
    """12-wave geometry."""
    radius: float = 1.0
    depth: float = 0.5
    base_frequency: float = 2.0

    def wave_k_vectors(self) -> np.ndarray:
        # 12 vertices of cuboctahedron
        v = []
        for i in [-1.0, 1.0]:
            for j in [-1.0, 1.0]:
                v.extend([[i, j, 0.0], [i, 0.0, j], [0.0, i, j]])
        v = np.array(v) / np.sqrt(2)
        return v[:, :2] * self.base_frequency

@dataclass
class SacredIcosahedronParams:
    """20-wave geometry."""
    radius: float = 1.0
    depth: float = 0.5
    base_frequency: float = 2.0

    def wave_k_vectors(self) -> np.ndarray:
        phi = (1.0 + np.sqrt(5)) / 2.0
        # 12 vertices + 8 face normals to get 20 waves, or just 20 face normals
        # For simplicity, returning exactly 20 distinct directions on the sphere

        # 12 vertices of icosahedron
        v = []
        for i in [-1.0, 1.0]:
            for j in [-phi, phi]:
                v.extend([[0.0, i, j], [j, 0.0, i], [i, j, 0.0]])

        # We need 8 more to reach 20 waves. We use vertices of a dual dodecahedron.
        for i in [-1.0, 1.0]:
            for j in [-1.0, 1.0]:
                for k in [-1.0, 1.0]:
                    v.append([i, j, k])

        v = np.array(v)
        v = v / np.linalg.norm(v, axis=1, keepdims=True)
        return v[:, :2] * self.base_frequency
