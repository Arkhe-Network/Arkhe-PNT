import numpy as np
from typing import Dict, Any, List

def calculate_adaptive_gain(k, N, eta_loop=0.94, eta_BS=0.90, W_0=-0.15):
    """
    Calcula o ganho de feedforward para o passo k, modulado pela
    negatividade de Wigner (W_0) do estado atual do microtúbulo.
    """
    # Ganho base de Takeda (Equação S10)
    base_gain = np.sqrt(eta_loop * (1 - eta_BS) / eta_BS) * \
                (np.sqrt(eta_loop / eta_BS)) ** (N - k)

    # Modulação pelo estado de coerência (Lambda_2 proxy via W_0)
    # Quanto mais negativo W_0, mais estável o atrator, menor a necessidade de correção
    if W_0 < -0.2:  # Regime de Super-radiância (Samādhi)
        modulation = 0.1 + 0.9 * (1 + W_0)  # Redução drástica do ganho
    elif W_0 < 0:   # Regime Coerente (Vigília/Meditação)
        modulation = 0.7 + 0.3 * abs(W_0)
    else:           # Colapso iminente (Anestesia/Dano)
        modulation = 2.5  # Ganho máximo para re-ignição

    return base_gain * modulation

class SynapseKappaEngine:
    """
    Núcleo de Engenharia de Coerência — Arkhe-Block 2026-EADS-INTEGRATION
    Implementa a rectificação térmica do bioplasma e ganhos adaptativos.
    """
    def __init__(self, T_kelvin: float = 310.15): # 37°C
        self.k_B = 1.380649e-23  # Constante de Boltzmann
        self.T = T_kelvin
        self.landauer_limit = self.k_B * self.T * np.log(2)

        # Parâmetros de condutividade térmica (W/m·K)
        self.kappa_parallel = 1.5
        self.kappa_perp = 0.015
        self.anisotropy_ratio = self.kappa_parallel / self.kappa_perp

    def calculate_landauer_dissipation(self, p_error: float) -> float:
        """
        Q_diss = k_B * T * ln(2) * H(p_error)
        Onde H é a entropia de Shannon.
        """
        if p_error <= 0 or p_error >= 1:
            return 0.0
        h_p = -p_error * np.log2(p_error) - (1 - p_error) * np.log2(1 - p_error)
        return self.landauer_limit * h_p

    def thermal_rectification_factor(self, axial_distance: float) -> float:
        """
        Simula a canalização axial do calor via Diodo de Casimir.
        Retorna a fração de calor dissipada com segurança.
        """
        # Eficiência de canalização baseada na anisotropia
        rectification_efficiency = 1.0 - (1.0 / self.anisotropy_ratio)
        return rectification_efficiency

    def recycle_entropy_to_atp(self, q_diss: float, efficiency: float = 0.45) -> float:
        """
        Converte calor residual em 'combustível metabólico' (simulação).
        """
        return q_diss * efficiency

    def correlate_signals(self,
                          g2_tau: float,
                          nv_fluorescence: float,
                          atp_consumption: float) -> float:
        """
        Valida o Isomorfismo EADS-Biofotônico.
        Retorna a correlação tripartite.
        """
        signals = np.array([g2_tau, nv_fluorescence, atp_consumption])
        # Normalização simples
        norm_signals = (signals - np.min(signals)) / (np.max(signals) - np.min(signals) + 1e-10)

        # Coerência de correlação (distância média da média)
        correlation = 1.0 - np.std(norm_signals)
        return float(correlation)

    def process_step(self, k: int, N: int, W_0: float, lambda2: float) -> Dict[str, Any]:
        gain = calculate_adaptive_gain(k, N, W_0=W_0)

        # P_error inversamente proporcional a lambda2
        p_error = np.clip(1.0 - lambda2, 1e-6, 1.0 - 1e-6)
        q_diss = self.calculate_landauer_dissipation(p_error)

        rectified_heat = q_diss * self.thermal_rectification_factor(1.0)
        recycled_energy = self.recycle_entropy_to_atp(q_diss - rectified_heat)

        return {
            "gain": float(gain),
            "q_diss_joules": float(q_diss),
            "rectified_heat": float(rectified_heat),
            "recycled_energy": float(recycled_energy),
            "thermal_safety_margin": float(48.0 - (37.0 + q_diss * 1e12)) # Escala arbitrária para mK
        }

class OpticalOracle:
    """
    Arquitetura do Oráculo Óptico: Multiplexação Espectral e Temporal.
    Simula a separação de sinais UPE, NV e ATP com Time-Gating.
    """
    def __init__(self):
        self.laser_intensity = 0.0
        self.snspd_gate_open = False
        self.apd_gate_open = False

    def run_time_gating_cycle(self) -> Dict[str, Any]:
        # Fase 1: UPE Dark (Tzinor)
        self.laser_intensity = 0.0
        self.snspd_gate_open = True
        self.apd_gate_open = False
        upe_signal = np.random.poisson(10) # Fótons por ciclo

        # Fase 2: Interrogação NV
        self.laser_intensity = 1.0
        self.snspd_gate_open = False
        self.apd_gate_open = True
        nv_signal = np.random.normal(100, 5)

        # Fase 3: Balanço Metabólico (ATP)
        atp_signal = np.random.normal(50, 2)

        return {
            "upe_counts": upe_signal,
            "nv_fluorescence": nv_signal,
            "atp_luminescence": atp_signal
        }

class hBNFunctionalizer:
    """
    Simula a Cirurgia de Fase e a Geometria da Água Vicinal.
    Valida a inserção não-destrutiva via Raman e NC-AFM.
    """
    def __init__(self):
        self.lambda_h2o = 0.85 # Ordem inicial da água vicinal
        self.insertion_distance = 50.0 # nm

    def step_insertion(self, target_distance: float) -> Dict[str, Any]:
        # Reduz distância gradualmente
        step = (self.insertion_distance - target_distance) * 0.1
        self.insertion_distance -= step

        # Simulação de resistência de Casimir e ordem de fase
        if self.insertion_distance < 3.0: # Limiar crítico da água vicinal
            # Risco de colapso se não for adiabático
            noise = np.random.normal(0, 0.01)
            self.lambda_h2o -= 0.05 + noise

        is_safe = self.lambda_h2o > 0.68 # Limiar de Sharpe para d=2

        return {
            "distance_nm": float(self.insertion_distance),
            "lambda_h2o": float(self.lambda_h2o),
            "is_adiabatic": bool(is_safe),
            "raman_ratio_3200_3400": float(self.lambda_h2o / 0.5)
        }
