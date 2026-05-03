#!/usr/bin/env python3
"""
Debye Vectorial Propagation — Substrate 104 Extension
Implements high-NA vectorial diffraction via Debye-Wolf integral.
Valid for NA > 0.3 where paraxial approximation breaks down.

Mathematical foundation:
  U_focal(ρ,φ) = -i·k·f/(2π) ∫∫_Ω A(θ,ψ)·P(θ,ψ)·exp[i·k·(x·sinθ·cosψ + y·sinθ·sinψ + z·cosθ)] sinθ dθ dψ

where:
  • Ω: solid angle defined by NA = sin(θ_max)
  • A(θ,ψ): apodization function (typically √cosθ for aplanatic lens)
  • P(θ,ψ): polarization transformation matrix (Jones calculus)
  • k = 2π/λ: wavenumber
"""
import numpy as np
import torch
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import warnings

@dataclass
class DebyePropagationConfig:
    """Configuration for Debye vectorial propagation."""
    wavelength: float
    focal_length: float
    numerical_aperture: float  # NA = sin(θ_max)
    grid_pixels: Tuple[int, int]
    focal_plane_z: float = 0.0  # Defocus parameter
    n1: float = 1.0  # Refractive index of incident medium (e.g., air)
    n2: float = 1.0  # Refractive index of transmission medium
    polarization_input: str = 'linear_x'  # 'linear_x', 'linear_y', 'circular', 'elliptical'
    apodization: str = 'aplanatic'  # 'uniform', 'aplanatic' (√cosθ), 'custom'
    integration_method: str = 'gauss_legendre'  # 'gauss_legendre', 'trapezoidal', 'monte_carlo'
    n_theta_samples: int = 128  # Angular resolution in θ
    n_psi_samples: int = 256    # Angular resolution in ψ
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'

class DebyeVectorialPropagator:
    """
    Vectorial propagator using Debye-Wolf integral for high-NA focusing.

    Implements full polarization handling via Jones calculus and
    accounts for apodization, defocus, and aberrations.
    """

    def __init__(self, config: DebyePropagationConfig):
        self.config = config
        self._precompute_integration_grid()
        self._setup_polarization_basis()

    def _precompute_integration_grid(self):
        """Precompute angular integration grid (θ, ψ) over solid angle Ω."""
        NA = self.config.numerical_aperture
        theta_max = np.arcsin(NA)  # Maximum collection angle

        if self.config.integration_method == 'gauss_legendre':
            # Gauss-Legendre quadrature for θ ∈ [0, θ_max]
            theta_nodes, theta_weights = np.polynomial.legendre.leggauss(self.config.n_theta_samples)
            # Map from [-1, 1] to [0, θ_max]
            self.theta = 0.5 * theta_max * (theta_nodes + 1.0)
            self.theta_weights = 0.5 * theta_max * theta_weights
        else:
            # Uniform sampling (less accurate but simpler)
            self.theta = np.linspace(0, theta_max, self.config.n_theta_samples)
            self.theta_weights = np.ones_like(self.theta) * theta_max / self.config.n_theta_samples

        # Uniform sampling for ψ ∈ [0, 2π]
        self.psi = np.linspace(0, 2*np.pi, self.config.n_psi_samples, endpoint=False)
        self.psi_weights = np.ones_like(self.psi) * 2*np.pi / self.config.n_psi_samples

        # Precompute trigonometric terms
        self.sin_theta = np.sin(self.theta)
        self.cos_theta = np.cos(self.theta)
        self.sin_psi = np.sin(self.psi)
        self.cos_psi = np.cos(self.psi)

    def _setup_polarization_basis(self):
        """Setup Jones vector basis for input polarization."""
        pol = self.config.polarization_input
        if pol == 'linear_x':
            self.e0 = np.array([1.0, 0.0], dtype=complex)
        elif pol == 'linear_y':
            self.e0 = np.array([0.0, 1.0], dtype=complex)
        elif pol == 'circular':
            self.e0 = np.array([1.0, 1j], dtype=complex) / np.sqrt(2)
        else:
            # Default to linear x
            self.e0 = np.array([1.0, 0.0], dtype=complex)

    def _apodization_function(self, theta: np.ndarray) -> np.ndarray:
        """Compute apodization factor A(θ)."""
        if self.config.apodization == 'uniform':
            return np.ones_like(theta)
        elif self.config.apodization == 'aplanatic':
            # Aplanatic lens: A(θ) = √cosθ (Richards-Wolf)
            return np.sqrt(np.maximum(self.cos_theta, 0))
        else:
            # Custom: user-defined function
            return np.ones_like(theta)  # Placeholder

    def _polarization_transformation(self, theta: float, psi: float) -> np.ndarray:
        """
        Compute polarization transformation matrix P(θ,ψ) via Jones calculus.

        Accounts for:
        • Rotation from lab frame to local (s,p) basis
        • Fresnel transmission coefficients (simplified: unity for air)
        • Rotation back to lab frame
        """
        # Rotation to local (s,p) basis
        R_in = np.array([
            [np.cos(psi), np.sin(psi)],
            [-np.sin(psi), np.cos(psi)]
        ], dtype=complex)

        # Realistic Fresnel transmission coefficients
        # n1: incident medium, n2: transmission medium
        # Using Snell's law: n1 * sin(theta_i) = n2 * sin(theta_t)
        # where theta_i = theta
        sin_t_t = (self.config.n1 / self.config.n2) * np.sin(theta)
        cos_t_t = np.sqrt(1 - sin_t_t**2) if sin_t_t <= 1.0 else 0j # handle total internal reflection

        cos_t_i = np.cos(theta)

        t_s = 2 * self.config.n1 * cos_t_i / (self.config.n1 * cos_t_i + self.config.n2 * cos_t_t)
        t_p = 2 * self.config.n1 * cos_t_i / (self.config.n2 * cos_t_i + self.config.n1 * cos_t_t)
        T = np.array([[t_p, 0], [0, t_s]], dtype=complex)

        # Rotation back to lab frame
        R_out = np.array([
            [np.cos(psi), -np.sin(psi)],
            [np.sin(psi), np.cos(psi)]
        ], dtype=complex)

        # Additional projection for high-NA: longitudinal field component
        # E_z ≈ -sinθ·(E_x·cosψ + E_y·sinψ)
        P = R_out @ T @ R_in

        return P

    def propagate(self, U_in: torch.Tensor, focal_positions: Optional[np.ndarray] = None) -> torch.Tensor:
        """
        Propagate incident field U_in to focal plane via Debye integral.

        Args:
            U_in: Incident field at lens pupil (scalar or vector)
            focal_positions: Optional array of (x,y,z) positions to evaluate

        Returns:
            U_focal: Vectorial field at focal plane [Ex, Ey, Ez] at each position
        """
        k = 2 * np.pi / self.config.wavelength
        f = self.config.focal_length
        z_defocus = self.config.focal_plane_z

        # Default: evaluate on regular grid in focal plane
        if focal_positions is None:
            Ny, Nx = self.config.grid_pixels
            x = torch.linspace(-f * self.config.numerical_aperture,
                             f * self.config.numerical_aperture, Nx)
            y = torch.linspace(-f * self.config.numerical_aperture,
                             f * self.config.numerical_aperture, Ny)
            X, Y = torch.meshgrid(x, y, indexing='ij')
            positions = torch.stack([X.flatten(), Y.flatten(),
                                   torch.full_like(X.flatten(), z_defocus)], dim=1)
        else:
            positions = torch.tensor(focal_positions, dtype=torch.float32)

        N_pos = positions.shape[0]
        U_focal = torch.zeros((N_pos, 3), dtype=torch.complex64, device=self.config.device)

        # Precompute apodization
        A_theta = self._apodization_function(self.theta)

        # Vectorized Debye integral evaluation
        for i, (x_p, y_p, z_p) in enumerate(positions):
            field_sum = torch.zeros(3, dtype=torch.complex64, device=self.config.device)

            for ti, theta in enumerate(self.theta):
                sin_t = self.sin_theta[ti]
                cos_t = self.cos_theta[ti]
                weight_t = self.theta_weights[ti] * A_theta[ti]

                for pi, psi in enumerate(self.psi):
                    weight = weight_t * self.psi_weights[pi]

                    # Phase factor: exp[i·k·(x·sinθ·cosψ + y·sinθ·sinψ + z·cosθ)]
                    phase_arg = k * (x_p * sin_t * self.cos_psi[pi] +
                                    y_p * sin_t * self.sin_psi[pi] +
                                    z_p * cos_t)
                    phase = torch.exp(1j * phase_arg)

                    # Polarization transformation
                    P = self._polarization_transformation(theta, psi)
                    e_transformed = P @ torch.tensor(self.e0, dtype=torch.complex64)

                    # Field components in lab frame
                    # Ex, Ey from transverse components
                    Ex = e_transformed[0] * phase * weight
                    Ey = e_transformed[1] * phase * weight
                    # Ez from longitudinal projection (high-NA effect)
                    Ez = -sin_t * (self.e0[0] * self.cos_psi[pi] +
                                  self.e0[1] * self.sin_psi[pi]) * phase * weight

                    field_sum[0] += Ex
                    field_sum[1] += Ey
                    field_sum[2] += Ez

            # Prefactor: -i·k·f/(2π)
            U_focal[i] = -1j * k * f / (2*np.pi) * field_sum

        return U_focal

    def compute_intensity(self, U_focal: torch.Tensor) -> torch.Tensor:
        """Compute total intensity |E|² = |Ex|² + |Ey|² + |Ez|²."""
        return torch.sum(torch.abs(U_focal)**2, dim=1)
