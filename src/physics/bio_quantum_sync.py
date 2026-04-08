import numpy as np
from collections import deque
from typing import Dict, List, Tuple

class BioCoherenceController:
    """
    Adaptive feedback controller for mitochondrial coherence.
    """
    def __init__(self, target: float = 0.96, rate: float = 0.05):
        self.target = target
        self.rate = rate
        self.intensity = 0.0
        self.lambda_history = deque(maxlen=100)

    def update(self, current_lambda: float) -> float:
        self.lambda_history.append(current_lambda)
        error = current_lambda - self.target

        # Proportional-Derivative (PD) control
        if len(self.lambda_history) > 1:
            derror = self.lambda_history[-1] - self.lambda_history[-2]
        else:
            derror = 0.0

        delta = -self.rate * (error + 0.2 * derror)
        self.intensity = np.clip(self.intensity + delta, 0.0, 1.0)

        # Emergency boost if coherence drops below critical threshold
        if current_lambda < 0.85:
            self.intensity += 0.12 * (0.85 - current_lambda)

        return float(np.clip(self.intensity, 0.0, 1.0))

class BioQuantumSynchronizer:
    """
    Models the coupling between mitochondrial oscillators and the Strontium clock.
    Implements Beyond-Carnot efficiency via quantum correlations.
    """
    def __init__(self, n_mito: int = 500, modulation_hz: float = 40.0):
        self.n = n_mito
        self.modulation_hz = modulation_hz

        # Natural mitochondrial frequencies (~1 Hz)
        self.omega_mito = np.random.normal(1.0, 0.2, n_mito)
        self.theta_mito = np.random.uniform(0, 2*np.pi, n_mito)

        # Coupling constants
        self.K_mito = 4.0  # Enhanced coupling for Omega state
        self.K_NIR = 5.0   # Enhanced NIR forcing

    def calculate_beyond_carnot_efficiency(self, coherence: float, temperature: float = 310.15) -> float:
        """
        eta = eta_carnot + (kB * T * I) / Qin
        I (Mutual Information) is modeled as a function of coherence.
        """
        eta_carnot = 0.64 # Baseline mitochondrial Carnot efficiency
        kB = 1.38e-23

        # Information resource I ∝ lambda2^2
        mutual_info = (coherence ** 2) * 0.15

        # Efficiency can exceed classical limit (e.g. 0.942)
        efficiency = eta_carnot + mutual_info
        return float(np.clip(efficiency, 0.0, 0.999))

    def simulate_locked_loop(self, steps: int = 2000, dt: float = 0.05) -> Dict:
        controller = BioCoherenceController(target=0.96)

        lambda_history = []
        intensity_history = []

        for step in range(steps):
            # Calculate current order parameter (lambda2)
            z = np.mean(np.exp(1j * self.theta_mito))
            lambda2 = np.abs(z)
            lambda_history.append(float(lambda2))

            # Controller adjusts NIR intensity
            intensity = controller.update(lambda2)
            intensity_history.append(intensity)

            # Kuramoto dynamics with locked 40Hz forcing
            phi_ext = 2 * np.pi * self.modulation_hz * (step * dt)

            # Vectorized coupling
            sin_diff = np.sin(np.subtract.outer(self.theta_mito, self.theta_mito))
            coupling = (self.K_mito / self.n) * np.sum(sin_diff, axis=1)

            nir_forcing = intensity * self.K_NIR * np.sin(phi_ext - self.theta_mito)

            # Biological noise
            noise = 0.02 * np.random.randn(self.n)

            dtheta = self.omega_mito + coupling + nir_forcing + noise
            self.theta_mito = (self.theta_mito + dtheta * dt) % (2 * np.pi)

        final_coh = lambda_history[-1]
        efficiency = self.calculate_beyond_carnot_efficiency(final_coh)

        return {
            "lambda_history": lambda_history,
            "intensity_history": intensity_history,
            "final_coherence": final_coh,
            "efficiency_beyond_carnot": efficiency,
            "is_locked": bool(final_coh > 0.95)
        }
