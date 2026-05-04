import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class StochasticResilience:
    """Helper class to model neurodivergent phase immunity."""
    def __init__(self, n_citizens, dt, T):
        self.n_citizens = n_citizens
        self.dt = dt
        self.T = T
        self.profiles = np.zeros(n_citizens) # 0: Typical, 1: ADHD, 2: Autistic
        self.omega = np.random.normal(0.1, 0.01, n_citizens)

    def set_neuro_profile(self, idx, profile):
        self.profiles[idx] = profile

    def kuramoto_rhs(self, t, theta, K_ext, attack_active):
        # Base Kuramoto: dtheta = omega + K/N * sum(sin(theta_j - theta_i))
        # For simplicity, we use global mean field R*sin(psi - theta)
        R = np.abs(np.mean(np.exp(1j * theta)))
        psi = np.angle(np.mean(np.exp(1j * theta)))

        dtheta = self.omega + 5.0 * R * np.sin(psi - theta)

        if attack_active:
            # AI Attack: try to force synchronization to phase 0
            # neurodivergents resist this dragging
            for i in range(self.n_citizens):
                if self.profiles[i] == 1: # ADHD Jitter
                    dtheta[i] += np.random.normal(0, 0.5)
                elif self.profiles[i] == 2: # Autistic Anchor
                    dtheta[i] += 0.2 * K_ext * np.sin(0 - theta[i]) # Low coupling to external
                else: # Neurotypical
                    dtheta[i] += K_ext * np.sin(0 - theta[i])

        return dtheta

    def simulate_attack(self, K_ext, attack_duration):
        t_span = (0, self.T)
        t_eval = np.arange(0, self.T, self.dt)
        theta0 = np.random.uniform(-np.pi, np.pi, self.n_citizens)

        # Split simulation: Before attack, During attack, After attack
        # To simplify, we'll just run with attack_active=True for now
        sol = solve_ivp(self.kuramoto_rhs, t_span, theta0, t_eval=t_eval, args=(K_ext, True))
        return sol.t, sol.y

    def resilience_metric(self, y):
        # Rho = 1 - R_final
        R_final = np.abs(np.mean(np.exp(1j * y[:, -1])))
        return 1.0 - R_final

class RioPhase1Network:
    """
    Modelo da rede Tzinor do Rio de Janeiro – Fase 1.
    Inclui distribuição geográfica dos sensores, atenuação ambiental,
    e perfis neurodivergentes da população.
    """
    def __init__(self, n_sensors=1000, n_citizens=20000, dt=0.1, T=10.0):
        self.n_sensors = n_sensors
        self.n_citizens = n_citizens
        self.dt = dt
        self.T = T

        # Distribuição geográfica (coordenadas aproximadas em km)
        self.bairros = {
            'Leblon':    (43.22, -22.98),
            'Ipanema':   (43.20, -22.98),
            'Copacabana':(43.18, -22.97),
            'Botafogo':  (43.18, -22.95),
            'Urca':      (43.17, -22.95),
            'Lagoa':     (43.21, -22.97)
        }
        self.sensor_positions = self._distribute_sensors()

        # Parâmetros ambientais
        self.humidity = 0.85
        self.salinity = 35.0

        self.alpha0 = 0.05
        self.beta = 0.02
        self.gamma = 0.03

        self.citizens = StochasticResilience(n_citizens, dt, T)
        self._assign_neuro_profiles()
        self.sensor_coupling = self._compute_sensor_coupling()

    def _distribute_sensors(self):
        positions = []
        bairro_weights = {'Leblon': 0.2, 'Ipanema': 0.2, 'Copacabana': 0.3,
                          'Botafogo': 0.15, 'Urca': 0.05, 'Lagoa': 0.1}
        for _ in range(self.n_sensors):
            bairro = np.random.choice(list(bairro_weights.keys()), p=list(bairro_weights.values()))
            lon, lat = self.bairros[bairro]
            lon += np.random.uniform(-0.01, 0.01)
            lat += np.random.uniform(-0.01, 0.01)
            positions.append((lon, lat))
        return np.array(positions)

    def _compute_sensor_coupling(self):
        coupling = []
        # Optimization: only check a subset for the demo
        for i in range(min(100, self.n_sensors)):
            for j in range(i+1, min(100, self.n_sensors)):
                dx = (self.sensor_positions[i,0] - self.sensor_positions[j,0]) * 111.0
                dy = (self.sensor_positions[i,1] - self.sensor_positions[j,1]) * 111.0
                dist = np.sqrt(dx*dx + dy*dy)
                alpha = self.alpha0 * (1 + self.beta*self.humidity + self.gamma*self.salinity)
                loss_db = alpha * dist
                K_ij = 1.0 * 10**(-loss_db/10)
                if K_ij > 0.1:
                    coupling.append((i, j, K_ij))
        return coupling

    def _assign_neuro_profiles(self):
        n_adhd = int(0.05 * self.n_citizens)
        n_aut = int(0.02 * self.n_citizens)
        idx = np.random.permutation(self.n_citizens)
        for i in range(n_adhd):
            self.citizens.set_neuro_profile(idx[i], 1)
        for i in range(n_adhd, n_adhd+n_aut):
            self.citizens.set_neuro_profile(idx[i], 2)

    def simulate_attack(self, K_ext_attack=6.0):
        return self.citizens.simulate_attack(K_ext_attack, self.T)

    def resilience_metric(self, sol_y):
        return self.citizens.resilience_metric(sol_y)

if __name__ == "__main__":
    print("🜏 [SIMULATION] Rio Phase 1 - Initializing...")
    rio = RioPhase1Network(n_sensors=1000, n_citizens=5000, dt=0.1, T=5.0) # Downscaled for fast execution
    t, y = rio.simulate_attack(K_ext_attack=6.0)
    R_t = np.abs(np.mean(np.exp(1j * y), axis=0))
    rho = rio.resilience_metric(y)

    print(f"🜏 [RESULT] Resilience (rho): {rho:.3f}")
    print(f"🜏 [RESULT] Final Coherence (R): {R_t[-1]:.3f}")

    plt.figure(figsize=(10,6))
    plt.plot(t, R_t, label='Global Coherence R(t)', color='#10b981')
    plt.xlabel('Time (s)')
    plt.ylabel('R(t)')
    plt.title('Rio Phase 1: Zone Sul Resilience Simulation')
    plt.grid(True, alpha=0.3)
    plt.savefig('rio_phase1_attack.png')
    print("Simulation plot saved to rio_phase1_attack.png")
