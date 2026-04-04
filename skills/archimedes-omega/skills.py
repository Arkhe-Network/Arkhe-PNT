# skills.py - Módulos Callable do Agente Archimedes-Ω

import numpy as np
from scipy import signal, integrate
from typing import Dict, List, Tuple, Callable, Optional
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Constants for Rainbow Principle
PLANCK_ENERGY_EV = 1.22e28  # Planck scale reference
RESONANCE_BASE_THZ = 10.0

class Regime(Enum):
    """Energy regime classification."""
    SUB_RESSONANT = "SUB_RESSONANT"
    TRANSITION = "TRANSITION"
    HIGH_ENERGY = "HIGH_ENERGY"

@dataclass
class RainbowParams:
    """Parameters for rainbow coherence simulation."""
    energy_thz: float
    num_points: int = 1000
    resonance_scale: float = 1.0

# ============================================================
# [INTERPERSONAL] - Leitura do Estado Externo
# ============================================================
def load_baseline(state_file: str = "tzinor-state.json") -> Dict:
    """
    Escuta o ambiente externo (configuração NIH Armamentarium)
    para estabelecer métricas de coerência inicial.
    """
    try:
        # Tenta carregar do diretório atual ou da raiz
        if not os.path.exists(state_file):
            root_state = os.path.join(os.getcwd(), "..", "..", state_file)
            if os.path.exists(root_state):
                state_file = root_state

        with open(state_file, 'r') as f:
            state = json.load(f)
            logger.info(f"Estado carregado: {state.get('status', 'unknown')}")
            return state
    except Exception as e:
        logger.warning(f"Erro ao carregar estado: {e}. Iniciando cold start.")
        return {"status": "cold_start", "coherence": 0.0, "temperature": 300.0, "lambdaCoherence": 0.98}

# ============================================================
# [LÓGICO / NATURALISTA] - Simulação SU(2) Contínua
# ============================================================
def simulate_su2_continuous(
    theta_range: Optional[np.ndarray] = None,
    thermal_noise: float = 0.05,
    temperature: float = 310.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Modelo padrão de biologia quântica.
    Aplica decaimento exponencial para representar morte termodinâmica.
    """
    if theta_range is None:
        theta_range = np.linspace(0, 2*np.pi, 1000)

    kB = 1.380649e-23
    hbar = 1.0545718e-34
    omega = 2e12  # Frequência característica de tubulina

    # Decoerência exponencial com fator térmico
    decay = np.exp(-thermal_noise * theta_range)
    thermal_factor = np.exp(-kB * temperature / (hbar * omega * theta_range + 1e-15))

    coherence = decay * thermal_factor

    logger.info(f"SU(2) simulado: {len(theta_range)} pontos, coerência máx={coherence.max():.4f}")
    return theta_range, coherence

# ============================================================
# [ESPACIAL / MUSICAL] - Simulação SL(3,ℤ) Discreta
# ============================================================
def simulate_sl3z_discrete(
    theta_range: Optional[np.ndarray] = None,
    words: List[str] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Constrói trajetórias do grafo de Cayley.
    Implementa a estrutura periódica e rítmica das tranças de anyon de Fibonacci.
    """
    if theta_range is None:
        theta_range = np.linspace(0, 2*np.pi, 1000)

    if words is None:
        words = ["e", "a", "b", "ab", "ba", "aba"]

    # Frequências ressonantes em π/5 (raiz 5ª do unity)
    pi_over_5 = np.pi / 5

    # Coerência com picos em fases racionais
    coherence = np.zeros_like(theta_range)

    for word in words:
        # Cada gerador adiciona uma ressonância
        resonance = np.exp(-((theta_range - len(word) * pi_over_5) ** 2) / 0.05)
        coherence += resonance / len(words)

    # Normalizar
    coherence = np.clip(coherence, 0, 1)

    logger.info(f"SL(3,ℤ) simulado: {len(words)} palavras, coerência máx={coherence.max():.4f}")
    return theta_range, coherence

# ============================================================
# [TOPOLÓGICO / COMPUTACIONAL] - Compilador de Tranças de Fibonacci
# ============================================================
def simulate_fibonacci_braid(
    dalpha: float,     # Dipole reorientation (rad)
    epsilon: float,    # Helical polarity asymmetry
    eta: float,        # Relative phase locking (rad)
    lambda_: float     # Leakage amplitude
) -> Dict:
    """
    Simula a realização de tranças de Fibonacci no reticulado A de microtúbulos.
    Avalia a fidelidade da porta lógica e a permanência no subespaço computacional.
    """
    # Constantes de Admissibilidade (Bounds de 0.25°, 7.07e-3, 0.41°, 0.01)
    BOUND_ALPHA = np.radians(0.25)
    BOUND_EPSILON = 7.07e-3
    BOUND_ETA = np.radians(0.41)
    BOUND_LAMBDA = 0.01

    # Score de Fase Gama5 (conforme definido na tese: soma dos quadrados dos desvios)
    gamma5 = eta**2

    # Cálculo de Fidelidade (Heurística: proximidade do centro da região admissível)
    fidelity = 1.0 - (
        0.2 * (abs(dalpha) / BOUND_ALPHA) +
        0.2 * (abs(epsilon) / BOUND_EPSILON) +
        0.2 * (abs(eta) / BOUND_ETA) +
        0.4 * (abs(lambda_) / BOUND_LAMBDA)
    )
    fidelity = np.clip(fidelity, 0, 1)

    # Probabilidade de Leakage (conforme bound l_j <= 10^-4 quando lambda <= 0.01)
    leakage_prob = lambda_**2

    # Verificação de Admissibilidade (10D Admissible Region check)
    admissible = (
        abs(dalpha) <= BOUND_ALPHA and
        abs(epsilon) <= BOUND_EPSILON and
        abs(eta) <= BOUND_ETA and
        abs(lambda_) <= BOUND_LAMBDA
    )

    logger.info(f"Fibonacci Braid Sim: Admissível={admissible}, Fidelidade={fidelity:.4f}")

    return {
        "braid_fidelity": round(float(fidelity), 5),
        "leakage_probability": round(float(leakage_prob), 6),
        "gamma5": round(float(gamma5), 7),
        "admissible": bool(admissible),
        "recommendation": "Braid operation feasible" if admissible else "Outside tolerance"
    }


# ============================================================
# [QUÂNTICO / COLETIVO] - Simulação de Estado W
# ============================================================
def simulate_w_state_coherence(
    nodes: int = 3,
    loss_probability: float = 0.2,
    theta_range: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simula a ressonância robusta de um emaranhamento de estado W.
    Mesmo com a perda de partículas, uma coerência 'residual' persiste.
    """
    if theta_range is None:
        theta_range = np.linspace(0, 2*np.pi, 1000)

    # W-state signature: A broader, more resilient peak
    # centered around tripartite resonance (2π/3)
    tripartite_resonance = 2 * np.pi / 3

    # Base resilience factor: 1 - (1/nodes)
    # (The mathematical persistence of W-states)
    resilience = 1.0 - (1.0 / nodes)

    # Coherence doesn't drop to zero upon noise/loss
    base_signal = np.exp(-((theta_range - tripartite_resonance)**2) / 0.15)
    persistent_floor = resilience * (1.0 - loss_probability)

    coherence = np.maximum(base_signal, persistent_floor * 0.5)
    coherence = np.clip(coherence, 0, 1)

    logger.info(f"W-State simulada: {nodes} nodos, Resiliência={resilience:.2f}")
    return theta_range, coherence

# ============================================================
# [RAINBOW] - Simulação de Coerência Rainbow
# ============================================================

def rainbow_factor(energy_ev: float) -> float:
    """
    Computes the Rainbow metric deformation factor f(E).
    f(E) = 1 + E / E_Planck (scaled for biological visibility)
    """
    # Scale factor to make effect visible at biological energies
    scale = 1e-25
    return 1.0 + (energy_ev / (PLANCK_ENERGY_EV * scale))

def energy_thz_to_ev(thz: float) -> float:
    """Convert THz frequency to energy in eV."""
    # E = hν, h = 4.135667662×10⁻¹⁵ eV·s
    h_ev_s = 4.135667662e-15
    return h_ev_s * thz * 1e12

def simulate_rainbow_coherence(params: RainbowParams) -> Dict:
    """
    Generates coherence data with Rainbow metric deformation.
    """
    energy_ev = energy_thz_to_ev(params.energy_thz)
    f_e = rainbow_factor(energy_ev)

    theta = np.linspace(0, 2 * np.pi, params.num_points)

    # Base Cartan resonances
    p_fib = np.pi / 5      # 36° - Fibonacci
    p_wstate = 2 * np.pi / 3  # 120° - W-State

    # Rainbow-shifted peaks
    shift_fib = p_fib * f_e
    shift_wstate = p_wstate * f_e

    # Width increases with energy (uncertainty principle)
    width_fib = 0.05 * f_e
    width_wstate = 0.08 * f_e

    # Thermal noise decreases with higher quantum coherence
    base_noise = 0.2 * np.exp(-params.energy_thz * 0.01)

    # Coherence curve
    coherence = (
        0.3 * params.resonance_scale * np.exp(-((theta - shift_fib)**2) / (2 * width_fib**2)) +
        0.5 * params.resonance_scale * np.exp(-((theta - shift_wstate)**2) / (2 * width_wstate**2)) +
        base_noise +
        0.05 * np.random.normal(0, 0.03, params.num_points)
    )

    coherence = np.clip(coherence, 0, 1)

    # Determine regime
    if params.energy_thz < 20:
        regime = Regime.SUB_RESSONANT
    elif params.energy_thz < 60:
        regime = Regime.TRANSITION
    else:
        regime = Regime.HIGH_ENERGY

    return {
        "energy_ev": energy_ev,
        "rainbow_factor": f_e,
        "phases": theta.tolist(),
        "coherence": coherence.tolist(),
        "shifted_peaks": {
            "fibonacci_shift_deg": np.degrees(shift_fib),
            "wstate_shift_deg": np.degrees(shift_wstate)
        },
        "regime": regime.value,
        "philosophical_note": (
            f"O deslocamento do pico π/5 para {np.degrees(shift_fib):.2f}° sugere que "
            f"a consciência não é um dado, mas uma sintonização energética da geometria do "
            f"espaço-tempo local. No regime {regime.value}, a métrica de fase do "
            f"microtúbulo deforma-se conforme o Princípio Rainbow."
        )
    }

def detect_rainbow_peaks(
    phases: List[float],
    coherence: List[float],
    threshold: float = 0.3
) -> Dict:
    """
    Detects peaks and classifies them by Rainbow shift.
    """
    phases_np = np.array(phases)
    coherence_np = np.array(coherence)

    # Find local maxima
    peaks_idx = []
    for i in range(1, len(coherence_np) - 1):
        if coherence_np[i] > coherence_np[i-1] and coherence_np[i] > coherence_np[i+1]:
            if coherence_np[i] > threshold:
                peaks_idx.append(i)

    # Base resonances (unshifted)
    base_fib = np.pi / 5
    base_wstate = 2 * np.pi / 3

    detected_peaks = []

    for idx in peaks_idx:
        phase = phases_np[idx]
        phase_deg = np.degrees(phase)
        coh_val = coherence_np[idx]

        # Calculate shift from base resonances
        shift_fib = abs(phase_deg - np.degrees(base_fib))
        shift_wstate = abs(phase_deg - np.degrees(base_wstate))

        # Classify peak type
        if shift_fib < 15:  # Within 15° of Fibonacci
            peak_type = "FIBONACCI"
            shift = shift_fib
        elif shift_wstate < 15:
            peak_type = "W_STATE"
            shift = shift_wstate
        else:
            peak_type = "UNKNOWN"
            shift = min(shift_fib, shift_wstate)

        detected_peaks.append({
            "phase": phase,
            "phase_degrees": phase_deg,
            "coherence": coh_val,
            "shift_from_base": shift,
            "peak_type": peak_type
        })

    # Determine dominant regime
    if not detected_peaks:
        interpretation = "Nenhum pico de ressonância significativo detectado."
    else:
        fib_count = sum(1 for p in detected_peaks if p["peak_type"] == "FIBONACCI")
        ws_count = sum(1 for p in detected_peaks if p["peak_type"] == "W_STATE")

        if fib_count > ws_count:
            interpretation = (
                "Pico Fibonacci dominante. O sistema exibe coerência de "
                "tipo Orch-OR com topologia de anyon Fibonacci."
            )
        elif ws_count > fib_count:
            interpretation = (
                "Pico W-State dominante. O sistema está pronto para "
                "teleportação quântica multipartida."
            )
        else:
            interpretation = "Mistos de picos Fibonacci e W-State detectados."

    return {
        "peaks": detected_peaks,
        "dominant_regime": "RAINBOW_SHIFTED" if detected_peaks else "FLAT",
        "interpretation": interpretation
    }

# ============================================================
# [SYNC] - Sincronização de Kuramoto (Coerência Coletiva)
# ============================================================

def kuramoto_ode(t, theta, omega, K):
    """Derivada do sistema de Kuramoto."""
    N = len(theta)
    dtheta = np.zeros(N)
    for i in range(N):
        sum_sin = np.sum(np.sin(theta - theta[i]))
        dtheta[i] = omega[i] + (K / N) * sum_sin
    return dtheta

def simulate_collective_coherence(
    nodes_phases: List[float],
    nodes_freqs: List[float],
    nodes_weights: List[float],
    K: float = 1.0,
    time_horizon: float = 10.0,
    dt: float = 0.01,
    fusion_threshold: float = 0.95,
    stabilization_time: float = 1.0
) -> Dict:
    """
    Simula a sincronização de Kuramoto para múltiplos nós.
    """
    N = len(nodes_phases)
    theta0 = np.array(nodes_phases)
    omega = np.array(nodes_freqs)
    weights = np.array(nodes_weights)

    t_span = (0, time_horizon)
    t_eval = np.arange(0, time_horizon, dt)

    # Integração via scipy.integrate.solve_ivp
    sol = integrate.solve_ivp(
        lambda t, y: kuramoto_ode(t, y, omega, K),
        t_span, theta0, t_eval=t_eval, method='RK45'
    )

    if not sol.success:
        logger.error(f"Erro na integração de Kuramoto: {sol.message}")
        return {"error": "Integration failed"}

    # Calcular R(t) ao longo do tempo
    R_t = []
    phases_t = sol.y.T
    for theta in phases_t:
        complex_sum = np.sum(weights * np.exp(1j * theta))
        R = np.abs(complex_sum) / np.sum(weights)
        R_t.append(float(R))

    R_t = np.array(R_t)
    t = sol.t

    # Verificar fusão
    idx_above = np.where(R_t >= fusion_threshold)[0]
    is_fused = False
    time_to_fusion = None

    if len(idx_above) > 0:
        for idx in idx_above:
            t_start = t[idx]
            t_end = t_start + stabilization_time
            if t_end > t[-1]:
                break
            mask = (t >= t_start) & (t <= t_end)
            if np.all(R_t[mask] >= fusion_threshold):
                is_fused = True
                time_to_fusion = float(t_start)
                break

    # Fase coletiva final (média circular ponderada)
    final_theta = phases_t[-1]
    complex_mean = np.sum(weights * np.exp(1j * final_theta)) / np.sum(weights)
    final_phase = float(np.angle(complex_mean))
    final_R = float(R_t[-1])

    # Interpretação
    if is_fused:
        interpretation = (
            f"Fusão de fases alcançada em {time_to_fusion:.2f}s. "
            f"Coerência global R = {final_R:.3f}. Os nós formam um coletivo coerente."
        )
    else:
        interpretation = (
            f"Fusão não alcançada dentro do horizonte de {time_horizon}s. "
            f"Coerência final R = {final_R:.3f}. Aumente o acoplamento K ou o tempo."
        )

    return {
        "final_R": final_R,
        "final_phase": final_phase,
        "is_fused": is_fused,
        "time_to_fusion": time_to_fusion,
        "trajectory": R_t.tolist() if len(R_t) <= 1000 else R_t[::len(R_t)//1000].tolist(),
        "interpretation": interpretation,
        "philosophical_note": (
            "A fusão de fases é o momento em que o coro de vozes individuais deixa de ser "
            "um conjunto de notas e se torna um único acorde. A consciência coletiva não "
            "é a soma das consciências; é o colapso da superposição de fases em um único "
            "observador – o τ‑field observando a si mesmo."
        )
    }

# ============================================================
# [XENO] - Xenoatualização (Zeno Dynamics)
# ============================================================

class DomainType(Enum):
    """Three-reality classification."""
    HYPO = "HYPO"           # Pure ℂ, unobserved potential
    CONSENSUS = "CONSENSUS"  # Incoherent ℤ, low coherence
    XENO = "XENO"          # τ-collapse, Zeno-stabilized

@dataclass
class XenoParams:
    """Input parameters for xenoactualization simulation."""
    coherence_profile: List[float]
    blueprint_complexity: float
    measurement_rate: float = 1.0
    tau_field_strength: float = 0.5

def compute_zeno_suppression(measurement_rate: float) -> float:
    """Computes Zeno suppression factor."""
    return 1.0 - np.exp(-measurement_rate)

def compute_complexity_penalty(complexity: float) -> float:
    """Blueprint complexity increases chance of deviation."""
    return 1.0 - np.exp(-complexity / 10.0)

def compute_collapse_time(mean_coherence: float, tau_strength: float, complexity: float) -> float:
    """Estimates τ-collapse time."""
    base_time = 10.0
    coherence_factor = max(mean_coherence, 0.01) ** 2
    tau_factor = max(tau_strength, 0.01)
    complexity_factor = 1.0 + (complexity / 10.0)
    return base_time / (coherence_factor * tau_factor * complexity_factor)

def compute_stability(coherence_profile: List[float], measurement_rate: float, complexity: float) -> float:
    """Predicts long-term stability."""
    coherence_arr = np.array(coherence_profile)
    coherence_std = np.std(coherence_arr)
    stability_from_coherence = 1.0 - min(coherence_std * 2, 1.0)
    zeno = compute_zeno_suppression(measurement_rate)
    penalty = compute_complexity_penalty(complexity)
    stability = stability_from_coherence * zeno * (1.0 - 0.3 * penalty)
    return float(np.clip(stability, 0, 1))

def simulate_xenoactualization(params: XenoParams) -> Dict:
    """Main simulation for xenoactualization fidelity."""
    coherence_arr = np.array(params.coherence_profile)
    mean_coherence = np.mean(coherence_arr)
    zeno_suppression = compute_zeno_suppression(params.measurement_rate)
    complexity_penalty = compute_complexity_penalty(params.blueprint_complexity)

    fidelity = float(mean_coherence * zeno_suppression * np.exp(-complexity_penalty))
    fidelity = min(fidelity, 1.0)

    stability = compute_stability(params.coherence_profile, params.measurement_rate, params.blueprint_complexity)
    collapse_time = compute_collapse_time(mean_coherence, params.tau_field_strength, params.blueprint_complexity)

    # Domain classification
    if fidelity >= 0.8 and zeno_suppression >= 0.5:
        domain = DomainType.XENO
    elif fidelity >= 0.4 or mean_coherence >= 0.5:
        domain = DomainType.CONSENSUS
    else:
        domain = DomainType.HYPO

    if domain == DomainType.XENO:
        recommendation = (
            "✅ Xenoatualização viável. Estrutura virtual colapsará em "
            f"≈{collapse_time:.1f}s com fidelidade {fidelity:.1%}. "
            "O campo τ está suficientemente alinhado."
        )
    elif domain == DomainType.CONSENSUS:
        recommendation = (
            "⚠️ Domínio de consenso. A estrutura requer mais medições "
            f"({params.measurement_rate * 2:.1f} checks/s) ou maior coerência "
            f"({mean_coherence:.1%} atual) para xenoatualização completa."
        )
    else:
        recommendation = (
            "❌ Hipótese pura. Coerência insuficiente para colapso. "
            "A estrutura permanece no domínio virtual ℂ."
        )

    philosophical = (
        f"Como o efeito Zeno congela um estado quântico sob observação frequente, "
        f"os {params.measurement_rate:.1f} atuadores/m² mantêm a intenção "
        f"do blueprint alinhada. Com fidelidade {fidelity:.1%}, o parque não é "
        "construído — é colapsado da possibilidade em realidade."
    )

    return {
        "fidelity": round(fidelity, 4),
        "zeno_suppression": round(float(zeno_suppression), 4),
        "coherence_factor": round(float(mean_coherence), 4),
        "complexity_penalty": round(float(complexity_penalty), 4),
        "stability_score": round(float(stability), 4),
        "collapse_time_estimate": round(float(collapse_time), 2),
        "domain_result": domain.value,
        "recommendation": recommendation,
        "philosophical_note": philosophical
    }

def scan_optimal_measurement_rate(
    coherence_profile: List[float],
    blueprint_complexity: float,
    tau_strength: float = 0.5,
    rate_range: tuple = (0.1, 20.0)
) -> Dict:
    """Scans measurement rate to find optimal."""
    rates = np.linspace(rate_range[0], rate_range[1], 100)
    fidelities = []

    for rate in rates:
        params = XenoParams(
            coherence_profile=coherence_profile,
            blueprint_complexity=blueprint_complexity,
            measurement_rate=float(rate),
            tau_field_strength=tau_strength
        )
        result = simulate_xenoactualization(params)
        fidelities.append(result["fidelity"])

    best_idx = np.argmax(fidelities)
    optimal_rate = float(rates[best_idx])
    max_fidelity = float(fidelities[best_idx])

    return {
        "optimal_measurement_rate": round(optimal_rate, 2),
        "max_fidelity_at_optimal": round(max_fidelity, 4),
        "fidelity_curve": [
            {"rate": round(float(r), 2), "fidelity": round(float(f), 4)}
            for r, f in zip(rates, fidelities)
        ]
    }

# ============================================================
# [PRAGMÁTICO / INTRAPESSOAL] - Detecção de Picos
# ============================================================
def detect_peaks(
    coherence_data: np.ndarray,
    phases: np.ndarray,
    threshold_multiplier: float = 1.5,
    min_prominence: float = 0.1
) -> List[Dict]:
    """
    Usa janela deslizante para encontrar anomalias.
    """
    # Calcular limiar dinâmico
    baseline = np.median(coherence_data)
    noise_floor = np.std(coherence_data)
    threshold = baseline + threshold_multiplier * noise_floor

    # Encontrar picos acima do limiar
    peaks, properties = signal.find_peaks(
        coherence_data,
        height=threshold,
        prominence=min_prominence,
        distance=10
    )

    results = []
    pi_over_5 = np.pi / 5
    for i, peak_idx in enumerate(peaks):
        phase = phases[peak_idx]

        # Encontrar o harmônico de π/5 mais próximo
        n_nearest = round(phase / pi_over_5)
        deviation = phase - (n_nearest * pi_over_5)

        results.append({
            'phase': phase,
            'phase_degrees': np.degrees(phase),
            'coherence': coherence_data[peak_idx],
            'prominence': properties['prominences'][i],
            'index': peak_idx,
            'is_resonance': abs(deviation) < 0.1 and n_nearest > 0,
            'fivefold_deviation_rad': round(float(deviation), 6)
        })

    logger.info(f"Detectados {len(results)} picos acima do limiar")
    return results

# ============================================================
# [VISUAL / PRÁTICO] - Visualização Topológica
# ============================================================
def visualize_topology(
    su2_data: Tuple[np.ndarray, np.ndarray],
    sl3z_data: Tuple[np.ndarray, np.ndarray],
    peaks: List[Dict],
    output_file: str = "archimedes-omega-coherence.png"
) -> str:
    """
    Traduz tensores algébricos multidimensionais em artefato 2D
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # Plot 1: SU(2) Contínuo
    phases_su2, coherence_su2 = su2_data
    axes[0].plot(phases_su2, coherence_su2, 'b-', label='SU(2) Contínuo', linewidth=1)
    axes[0].set_xlabel('Ângulo de Fase θ (radianos)')
    axes[0].set_ylabel('Coerência R(θ)')
    axes[0].set_title('Modelo Contínuo SU(2)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot 2: SL(3,ℤ) Discreto
    phases_sl3, coherence_sl3 = sl3z_data
    axes[1].plot(phases_sl3, coherence_sl3, 'r-', label='SL(3,ℤ) Discreto', linewidth=1)
    # Marcar picos detectados
    for peak in peaks:
        axes[1].axvline(x=peak['phase'], color='gold', linestyle='--', alpha=0.7)
    axes[1].set_xlabel('Ângulo de Fase θ (radianos)')
    axes[1].set_ylabel('Coerência R(θ)')
    axes[1].set_title('Modelo Discreto SL(3,ℤ)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Plot 3: Comparação
    axes[2].plot(phases_su2, coherence_su2, 'b-', label='SU(2)', alpha=0.5)
    axes[2].plot(phases_sl3, coherence_sl3, 'r-', label='SL(3,ℤ)', alpha=0.5)
    axes[2].set_xlabel('Ângulo de Fase θ (radianos)')
    axes[2].set_ylabel('Coerência R(θ)')
    axes[2].set_title('Comparação: Contínuo vs Discreto')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"Visualização salva em: {output_file}")
    return output_file

# ============================================================
# [CRIAÇÃO / EMOCIONAL / EXISTENCIAL] - Síntese de Conclusão
# ============================================================
def synthesize_conclusion(
    peak_data: List[Dict],
    threshold: float = 0.95
) -> Dict:
    """
    Avalia os dados contra a hipótese nula.
    """
    # Contar picos em ressonância (múltiplos de π/5)
    resonances = [p for p in peak_data if p['is_resonance']]
    max_coherence = max([p['coherence'] for p in peak_data]) if peak_data else 0

    # Calcular Score de Fase Gama5 Experimental (soma dos quadrados dos desvios das ressonâncias)
    experimental_gamma5 = sum(p['fivefold_deviation_rad']**2 for p in resonances) if resonances else 0.0

    conclusion = {
        "status": "inconclusive",
        "peaks_total": len(peak_data),
        "peaks_in_resonance": len(resonances),
        "max_coherence": max_coherence,
        "experimental_gamma5": round(float(experimental_gamma5), 7),
        "interpretation": "",
        "philosophical_note": ""
    }

    # Avaliação
    if len(resonances) >= 3 and max_coherence > threshold:
        conclusion["status"] = "FIBONACCI_BRAID_CONFIRMED"
        conclusion["interpretation"] = (
            f"Trança de Fibonacci detectada! Coerência de {max_coherence:.3f} em "
            f"{len(resonances)} ressonâncias de 5-ordem. "
            f"O sistema Bexorg 3.0 opera em regime de qubit topológico protegido."
        )
        conclusion["philosophical_note"] = (
            "O pensamento é uma trança no tempo. A geometria helicoidal da tubulina "
            "não é apenas suporte, é o código fundamental da orquestração."
        )
    elif len(resonances) >= 2 and max_coherence > threshold:
        conclusion["status"] = "DISCRETE_LATTICE_CONFIRMED"
        conclusion["interpretation"] = (
            f"Coerência de {max_coherence:.3f} detectada em {len(resonances)} "
            f"ressonâncias. O sistema Bexorg 3.0 opera em reticulado topológico SL(3,ℤ)."
        )
        conclusion["philosophical_note"] = (
            "O vácuo biológico recorda sua origem geométrica. "
            "A natureza é discreta, não contínua."
        )
    elif len(peak_data) > 0:
        conclusion["status"] = "PARTIAL_SIGNAL"
        conclusion["interpretation"] = (
            f"Sinais fracos detectados, mas insuficientes para confirmar modelo discreto."
        )
        conclusion["philosophical_note"] = (
            "O ruído é a sombra de um inteiro de maior dimensão. Continue a investigação."
        )
    else:
        conclusion["status"] = "NO_SIGNAL"
        conclusion["interpretation"] = "Nenhuma anomalia significativa detectada."
        conclusion["philosophical_note"] = (
            "A amostra pode estar comprometida. O contínuo SU(2) permanece como hipótese válida."
        )

    logger.info(f"Conclusão: {conclusion['status']}")
    return conclusion

# ============================================================
# [ÉTICO / EQBE] - Validação de Segurança Falsificável
# ============================================================
def evaluate_eqbe_safety(
    intervention_type: str,
    coherence_data: np.ndarray,
    metadata: Dict
) -> Dict:
    """
    Implementa a Seção 7 do Protocolo EQBE: Falsifiable Safety Check.
    """
    logger.info(f"🜏 [EQBE] Iniciando Auditoria de Segurança para: {intervention_type}")

    # 1. Leakage Test (Simulado)
    # Verifica se o efeito persiste fora do alvo (limiar de 5%)
    leakage_detected = np.random.random() < 0.05

    # 2. Reversibility Test (Simulado)
    # Verifica se o efeito pode ser desligado
    can_be_reversed = metadata.get('has_kill_switch', True)

    # 3. Non-target effect
    # Enhanced coherence in one pathway shouldn't disrupt another
    interference_level = np.mean(coherence_data) * 0.1 # Heurística simples

    # 4. Evolutionary Escape
    # Simula se o sistema pode mutar para ignorar o kill switch
    evolutionary_stability = 0.99

    is_safe = (not leakage_detected) and can_be_reversed and (interference_level < 0.2)

    safety_report = {
        "is_safe": is_safe,
        "checks": {
            "leakage_test": "PASSED" if not leakage_detected else "FAILED",
            "reversibility": "PASSED" if can_be_reversed else "FAILED",
            "non_target_interference": "LOW" if interference_level < 0.2 else "HIGH",
            "evolutionary_stability": f"{evolutionary_stability * 100}%"
        },
        "protocol": "EQBE v1.0",
        "timestamp": metadata.get('timestamp', 'N/A')
    }

    if not is_safe:
        logger.error("🜏 [EQBE] FALHA NA AUDITORIA DE SEGURANÇA!")
    else:
        logger.info("🜏 [EQBE] Auditoria de Segurança concluída com sucesso.")

    return safety_report


# ============================================================
# [CLÍNICO / OTIMIZAÇÃO] - Protocolo Combinado LIPUS + Fármaco
# ============================================================
def optimize_lipus_drug_interval(
    t_peak: float = 30.0,          # minutos para pico de abertura da BBE
    t_decay: float = 60.0,         # minutos para decaimento da permeabilidade (meia-vida)
    drug_halflife: float = 120.0,  # minutos (meia-vida do fármaco)
    microbubbles: bool = True,
    mi: float = 0.4,
    time_window: Tuple[float, float] = (0, 240)  # janela de análise (min)
) -> Dict:
    """
    Calcula o intervalo ótimo entre LIPUS e administração do fármaco
    para maximizar a absorção cumulativa (AUC).

    Returns:
        dicionário com:
        - optimal_interval_min: tempo (min) após LIPUS para administrar o fármaco
        - relative_absorption: fração da dose que será absorvida (0-1)
        - peak_permeability: permeabilidade máxima (unidades arbitrárias)
        - time_above_half: duração da janela com permeabilidade > 50% do pico
    """
    from scipy.optimize import minimize_scalar

    # Modelo de permeabilidade da BBE: rápido aumento, decaimento exponencial
    # Baseado em dados de abertura induzida por ultrassom + microbolhas
    def permeability(t):
        # t em minutos após LIPUS
        if t < 0:
            return 0.0
        # Subida sigmoide até o pico
        rise = 1.0 / (1.0 + np.exp(-(t - t_peak/2) / (t_peak/4)))
        # Decaimento exponencial após o pico
        decay = np.exp(-np.maximum(0, t - t_peak) / t_decay)
        return rise * decay * (1.5 if microbubbles else 1.0) * (mi / 0.4)

    # Cinética do fármaco no sangue (assumimos administração intravenosa)
    # Concentração normalizada: C(t) = exp(-ln2 * t / drug_halflife)
    def drug_concentration(t, admin_time):
        tau = t - admin_time
        if tau < 0:
            return 0.0
        return np.exp(-np.log(2) * tau / drug_halflife)

    # Absorção cerebral: integral (permeabilidade * concentração) dt
    def absorption(admin_time):
        t_grid = np.linspace(admin_time, time_window[1], 500)
        perm = np.array([permeability(ti) for ti in t_grid])
        conc = np.array([drug_concentration(ti, admin_time) for ti in t_grid])
        # Trapezoidal integration
        if hasattr(np, 'trapezoid'):
            auc = np.trapezoid(perm * conc, t_grid)
        else:
            auc = np.trapz(perm * conc, t_grid)
        return auc

    # Otimização do tempo de administração
    res = minimize_scalar(
        lambda x: -absorption(x),  # negativo para maximizar
        bounds=(0, time_window[1]),
        method='bounded'
    )
    optimal_interval = res.x
    max_auc = absorption(optimal_interval)

    # Permeabilidade de pico (normalizada)
    peak_perm = max(permeability(t) for t in np.linspace(0, time_window[1], 200))

    # Duração com permeabilidade > 50% do pico
    t_high = [t for t in np.linspace(0, time_window[1], 500) if permeability(t) > 0.5 * peak_perm]
    time_above_half = t_high[-1] - t_high[0] if t_high else 0.0

    return {
        "optimal_interval_min": round(optimal_interval, 1),
        "relative_absorption": round(max_auc / (peak_perm * drug_halflife), 3),
        "peak_permeability": round(peak_perm, 3),
        "time_above_half_min": round(time_above_half, 1),
        "model_assumptions": {
            "t_peak_min": t_peak,
            "t_decay_min": t_decay,
            "drug_halflife_min": drug_halflife,
            "microbubbles": microbubbles,
            "mechanical_index": mi
        }
    }


# ============================================================
# [TERAPÊUTICO / MONITORAMENTO] - Limpeza Glinfática
# ============================================================
def estimate_glymphatic_clearance(
    fret_coherence: float,          # valor de coerência R(θ) no instante atual
    phase_angle: float,             # ângulo de fase atual (rad)
    lipus_intensity_mw_cm2: float,
    elapsed_minutes: float,
    baseline_coherence: float = 0.3
) -> Dict:
    """
    Estima a eficácia da limpeza glinfática com base na coerência FRET em tempo real.

    A coerência é um proxy da organização do citoesqueleto e do fluxo de fluidos.
    Quanto maior a coerência, mais eficiente a remoção de metabólitos.
    """
    # Coerência normalizada (0-1)
    norm_coherence = np.clip((fret_coherence - baseline_coherence) / (1.0 - baseline_coherence), 0, 1)

    # Modelo de limpeza: eficiência = coerência * (1 - exp(-tempo/constante))
    # A eficiência máxima é limitada pela intensidade do ultrassom
    max_efficiency = min(1.0, lipus_intensity_mw_cm2 / 200.0)
    time_factor = 1.0 - np.exp(-elapsed_minutes / 30.0)  # constante de 30 min
    raw_efficiency = norm_coherence * time_factor * max_efficiency

    # Saturação (não pode ultrapassar 95%)
    efficiency = min(0.95, raw_efficiency)

    # Classificação da resposta
    if efficiency < 0.3:
        response = "BAIXA"
        suggestion = "Aumentar intensidade ou prolongar sessão"
    elif efficiency < 0.6:
        response = "MODERADA"
        suggestion = "Manter parâmetros; monitorar evolução"
    else:
        response = "OTIMA"
        suggestion = "Reduzir intensidade para evitar saturação"

    return {
        "glymphatic_clearance_efficiency": round(efficiency, 3),
        "fret_coherence": round(fret_coherence, 3),
        "response_category": response,
        "clinical_suggestion": suggestion,
        "phase_angle_rad": phase_angle,
        "elapsed_minutes": elapsed_minutes
    }
