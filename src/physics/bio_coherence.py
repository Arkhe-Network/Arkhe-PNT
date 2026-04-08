import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from typing import Dict, List, Tuple

class MitochondrialKuramoto:
    """
    Coupled oscillator model for mitochondrial dynamics.
    Each mitochondrion = phase oscillator theta_i with natural frequency omega_i.
    Coupling via NIR phase field (K_NIR) and local coupling (K_local).
    """

    def __init__(self, n_mito: int = 500, k_local: float = 1.5, k_nir: float = 2.0):
        self.n = n_mito
        self.K_local = k_local  # Gap-junction coupling
        self.K_NIR = k_nir      # NIR-induced coupling

        # Natural frequencies (Lorentzian distribution, gamma = 0.5 Hz)
        self.omega = np.random.standard_cauchy(n_mito) * 0.5

        # Initial phases (disordered)
        self.theta = np.random.uniform(0, 2*np.pi, n_mito)

        # Spatial positions (simplified 3D grid)
        self.pos = np.random.rand(n_mito, 3)

    def derivatives(self, theta: np.ndarray, t: float, nir_intensity: float, modulation_hz: float = 40.0) -> np.ndarray:
        """
        dtheta_i/dt = omega_i + K_local/N * sum(sin(theta_j - theta_i))
                      + K_NIR * nir_intensity * sin(Phi_NIR - theta_i)
        """
        # Local coupling term (near neighbors)
        # Using a vectorized approach for performance
        local_coupling = np.zeros(self.n)
        for i in range(self.n):
            distances = np.linalg.norm(self.pos - self.pos[i], axis=1)
            neighbors = (distances < 0.1) & (distances > 0)
            if np.any(neighbors):
                local_coupling[i] = (self.K_local / self.n) * np.sum(np.sin(theta[neighbors] - theta[i]))

        # NIR coupling term (global coherent field)
        # Phi_NIR = 2pi * modulation_hz * t
        phi_nir = 2 * np.pi * modulation_hz * t
        nir_coupling = self.K_NIR * nir_intensity * np.sin(phi_nir - theta)

        return self.omega + local_coupling + nir_coupling

    def order_parameter(self, theta: np.ndarray) -> float:
        """Calculates order parameter r(t) = |<e^(i*theta)>| (global coherence)"""
        return np.abs(np.mean(np.exp(1j * theta)))

    def simulate(self, t_max: float = 5.0, dt: float = 0.01, nir_intensity: float = 1.0, modulation_hz: float = 40.0) -> Dict:
        """
        Simulates the mitochondrial phase evolution.
        """
        t = np.arange(0, t_max, dt)
        theta_t = np.zeros((len(t), self.n))
        r_t = np.zeros(len(t))

        # Simple Euler integration for phase dynamics
        curr_theta = self.theta.copy()
        for i in range(len(t)):
            # Intensity is 0 for first half, nir_intensity for second half
            curr_intensity = nir_intensity if t[i] > (t_max / 2) else 0.0

            dtheta = self.derivatives(curr_theta, t[i], curr_intensity, modulation_hz)
            curr_theta += dtheta * dt
            curr_theta %= (2 * np.pi)

            theta_t[i] = curr_theta
            r_t[i] = self.order_parameter(curr_theta)

        # Metrics
        r_basal = np.mean(r_t[:len(t)//2])
        r_induced = np.mean(r_t[len(t)//2:])
        improvement = ((r_induced - r_basal) / r_basal * 100) if r_basal > 0 else 0

        # ATP Projection (logistic efficiency)
        atp_efficiency = 1.0 / (1.0 + np.exp(-10 * (r_t - 0.5)))

        return {
            't': t.tolist(),
            'r_t': r_t.tolist(),
            'atp_efficiency': atp_efficiency.tolist(),
            'r_basal': float(r_basal),
            'r_induced': float(r_induced),
            'improvement_percent': float(improvement),
            'lambda2_equiv': float(r_induced**2)
        }

    def visualize(self, results: Dict, output_path: str):
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.plot(results['t'], results['r_t'], 'c-', label='Coerência (r)')
        plt.axvline(x=max(results['t'])/2, color='y', linestyle='--', label='NIR ON')
        plt.title("Evolução da Coerência Mitocondrial")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Parâmetro de Ordem (r)")
        plt.grid(True, alpha=0.2)
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(results['t'], results['atp_efficiency'], 'm-', label='Eficiência ATP')
        plt.axvline(x=max(results['t'])/2, color='y', linestyle='--', label='NIR ON')
        plt.title("Projeção Z: Produção de ATP")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Eficiência (0-1)")
        plt.grid(True, alpha=0.2)
        plt.legend()

        plt.suptitle(f"Bio-Sync: Melhora de {results['improvement_percent']:.1f}% em Coerência")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

if __name__ == "__main__":
    engine = MitochondrialKuramoto()
    res = engine.simulate()
    print(f"Basal: {res['r_basal']:.3f}, Induced: {res['r_induced']:.3f}")
    engine.visualize(res, "bio_sync_test.png")
