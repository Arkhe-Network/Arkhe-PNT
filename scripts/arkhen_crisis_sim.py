import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class ArkhenCrisisSimulator:
    def __init__(self, n_citizens=10000, n_mobile=370, dt=0.1, T=60.0):
        self.n_citizens = n_citizens
        self.n_mobile = n_mobile
        self.dt = dt
        self.T = T

        # Internal states: Rio Population + Mobile Nodes
        self.n_total = n_citizens + n_mobile
        self.omega = np.random.normal(0.1, 0.02, self.n_total)
        self.theta = np.random.uniform(-np.pi, np.pi, self.n_total)

        # Node status (True = Online, False = Offline due to EMP)
        self.status = np.ones(self.n_total, dtype=bool)

    def apply_emp_attack(self, fraction=0.2):
        """Simulate EMP disabling a fraction of mobile nodes."""
        # Mobile nodes are indices [n_citizens : n_total]
        mobile_indices = np.arange(self.n_citizens, self.n_total)
        n_disable = int(len(mobile_indices) * fraction)
        disabled = np.random.choice(mobile_indices, n_disable, replace=False)
        self.status[disabled] = False
        return disabled

    def kuramoto_rhs(self, t, theta, K_internal, K_ext_attack, K_beacon):
        # Effective status (EMP + AI suppression)
        # nodes_online = self.status

        # Calculate Rio Order Parameter R
        # Only online nodes contribute to the mean field
        online_mask = self.status
        if not np.any(online_mask):
            return self.omega

        z = np.mean(np.exp(1j * theta[online_mask]))
        R = np.abs(z)
        psi = np.angle(z)

        # dtheta = omega + K_int * R * sin(psi - theta)
        dtheta = self.omega + K_internal * R * np.sin(psi - theta)

        # AI Attack (K_ext_attack) -> trying to force phase 0
        dtheta -= K_ext_attack * np.sin(theta)

        # Beacon of Freedom Effect (K_beacon)
        # In Rio, this is 0 (it's the source). In other states, it would be positive.
        # But for this simulation, we'll model the Interstate injection as a separate entity later.

        # Apply EMP: disabled nodes have 0 dynamics (frozen)
        dtheta[~online_mask] = 0

        return dtheta

    def simulate_rio_crisis(self, K_ext=6.0, emp_at=20.0, emp_duration=20.0):
        t_eval = np.arange(0, self.T, self.dt)

        # Phase 1: Nominal with AI Attack
        sol1 = solve_ivp(self.kuramoto_rhs, (0, emp_at), self.theta,
                         t_eval=t_eval[t_eval < emp_at], args=(5.0, K_ext, 0))

        # Phase 2: EMP Strike
        self.apply_emp_attack(0.2)
        theta_after_emp = sol1.y[:, -1]
        sol2 = solve_ivp(self.kuramoto_rhs, (emp_at, emp_at + emp_duration), theta_after_emp,
                         t_eval=t_eval[(t_eval >= emp_at) & (t_eval < emp_at + emp_duration)],
                         args=(5.0, K_ext, 0))

        # Phase 3: Recovery (EMP ends, nodes reboot)
        self.status[:] = True
        theta_recovery = sol2.y[:, -1]
        sol3 = solve_ivp(self.kuramoto_rhs, (emp_at + emp_duration, self.T), theta_recovery,
                         t_eval=t_eval[t_eval >= emp_at + emp_duration], args=(5.0, K_ext, 0))

        t = np.concatenate([sol1.t, sol2.t, sol3.t])
        y = np.concatenate([sol1.y, sol2.y, sol3.y], axis=1)

        R_t = [np.abs(np.mean(np.exp(1j * y[:, i]))) for i in range(len(t))]
        return t, R_t

    def simulate_national_expansion(self, rio_R_final):
        """Simulate the Beacon of Freedom effect on other states."""
        states = {
            'São Paulo': {'K_base': 2.0, 'init_R': 0.71},
            'Belo Horizonte': {'K_base': 1.8, 'init_R': 0.68},
            'Vitória': {'K_base': 1.5, 'init_R': 0.65}
        }

        results = {}
        K_beacon = 3.0 # Coupling strength from Rio's beacon

        for name, params in states.items():
            # Final R = (K_base * init_R + K_beacon * rio_R) / (K_base + K_beacon)
            # Simplified coupling model for steady state
            boosted_R = (params['K_base'] * params['init_R'] + K_beacon * rio_R_final) / (params['K_base'] + K_beacon)
            resilience = (boosted_R - params['init_R']) / (1.0 - params['init_R'])
            results[name] = {
                'final_R': boosted_R,
                'resilience': resilience
            }
        return results

if __name__ == "__main__":
    print("🜏 [SIMULATION] Arkhen Crisis & National Expansion...")
    sim = ArkhenCrisisSimulator(n_citizens=5000, n_mobile=370, T=60.0)

    t, R_t = sim.simulate_rio_crisis(K_ext=6.0, emp_at=20.0, emp_duration=20.0)
    rio_R_final = R_t[-1]

    print(f"🜏 [RIO] Minimum Coherence during EMP: {min(R_t):.3f}")
    print(f"🜏 [RIO] Final Recovery Coherence: {rio_R_final:.3f}")

    national = sim.simulate_national_expansion(rio_R_final)
    for state, res in national.items():
        print(f"🜏 [BEACON] {state}: R Boosted to {res['final_R']:.3f} (Resilience ρ: {res['resilience']:.3f})")

    plt.figure(figsize=(12,6))
    plt.plot(t, R_t, label='Rio Global Coherence R(t)', color='#10b981', linewidth=2)
    plt.axvspan(20, 40, color='red', alpha=0.1, label='EMP Strike (20% Node Loss)')
    plt.xlabel('Time (s)')
    plt.ylabel('R(t)')
    plt.title('Arkhen Crisis: Rio EMP Resilience & Recovery')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('arkhen_crisis_results.png')
    print("Crisis plot saved to arkhen_crisis_results.png")
