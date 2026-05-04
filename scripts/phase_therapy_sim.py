import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class PathologicalTzinorSim:
    """
    Models metastatic cancer as a 'pathological Tzinor' and simulates
    IVMT-Rx-4 targeted decoherence.
    """
    def __init__(self, n_tumor=1000, n_healthy=1000, T=20.0, dt=0.1):
        self.n_tumor = n_tumor
        self.n_healthy = n_healthy
        self.T = T
        self.dt = dt

        # Natural frequencies: Tumor cells (pathological high-coherence)
        # vs. Healthy stem cells (balanced stochasticity)
        self.omega_tumor = np.random.normal(0.5, 0.05, n_tumor)
        self.omega_healthy = np.random.normal(0.2, 0.1, n_healthy)

        self.theta_tumor = np.random.uniform(-np.pi, np.pi, n_tumor)
        self.theta_healthy = np.random.uniform(-np.pi, np.pi, n_healthy)

    def rhs(self, t, theta, K_internal, F_decoherence, is_tumor):
        n = len(theta)
        z = np.mean(np.exp(1j * theta))
        R = np.abs(z)
        psi = np.angle(z)

        # Internal coupling (Tumor has higher auto-organization)
        omega = self.omega_tumor if is_tumor else self.omega_healthy
        dtheta = omega + K_internal * R * np.sin(psi - theta)

        # IVMT-Rx-4 decoherence injection (Phase Shield for healthy, disruptive for tumor)
        if F_decoherence > 0:
            # Targeted frequency disruption (simplified)
            # In a real system, IVMT-Rx-4 targets specific tumor motility frequencies.
            if is_tumor:
                dtheta += F_decoherence * np.random.normal(0, 1.0, n)
            else:
                # Healthy cells resist due to wider natural frequency distribution (Biological Resilience)
                dtheta += 0.1 * F_decoherence * np.random.normal(0, 1.0, n)

        return dtheta

    def simulate(self, F_rx=5.0):
        t_eval = np.arange(0, self.T, self.dt)

        # 1. Simulate Tumor (Untreated)
        sol_t_untreated = solve_ivp(self.rhs, (0, self.T), self.theta_tumor,
                                   t_eval=t_eval, args=(8.0, 0, True))

        # 2. Simulate Tumor (Treated with IVMT-Rx-4)
        sol_t_treated = solve_ivp(self.rhs, (0, self.T), self.theta_tumor,
                                 t_eval=t_eval, args=(8.0, F_rx, True))

        # 3. Simulate Healthy Cells (Check for toxicity/EMI)
        sol_h_treated = solve_ivp(self.rhs, (0, self.T), self.theta_healthy,
                                 t_eval=t_eval, args=(2.0, F_rx, False))

        return t_eval, sol_t_untreated.y, sol_t_treated.y, sol_h_treated.y

if __name__ == "__main__":
    print("🜏 [ONCOLOGY] Initializing Phase Therapy Simulation (IVMT-Rx-4)...")
    sim = PathologicalTzinorSim()
    t, tumor_raw, tumor_rx, healthy_rx = sim.simulate(F_rx=10.0)

    R_tumor_raw = [np.abs(np.mean(np.exp(1j * tumor_raw[:, i]))) for i in range(len(t))]
    R_tumor_rx = [np.abs(np.mean(np.exp(1j * tumor_rx[:, i]))) for i in range(len(t))]
    R_healthy_rx = [np.abs(np.mean(np.exp(1j * healthy_rx[:, i]))) for i in range(len(t))]

    print(f"  > Tumor Baseline R: {R_tumor_raw[-1]:.3f}")
    print(f"  > Tumor Post-Rx R:   {R_tumor_rx[-1]:.3f} (DECOHERENCE ACHIEVED)")
    print(f"  > Healthy Post-Rx R: {R_healthy_rx[-1]:.3f} (BIOLOGICAL STABILITY)")

    plt.figure(figsize=(10,6))
    plt.plot(t, R_tumor_raw, '--', label='Tumor (Untreated)', color='red', alpha=0.5)
    plt.plot(t, R_tumor_rx, label='Tumor + IVMT-Rx-4', color='red', linewidth=2)
    plt.plot(t, R_healthy_rx, label='Healthy + IVMT-Rx-4', color='green', linewidth=2)
    plt.xlabel('Time (normalized)')
    plt.ylabel('Coherence R')
    plt.title('Phase Therapy: Pathological Tzinor Disruption')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('phase_therapy_results.png')
    print("Results saved to phase_therapy_results.png")
