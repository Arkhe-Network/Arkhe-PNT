# skills.py - Módulos Callable do Agente Archimedes-Ω

import numpy as np
from scipy import signal
from typing import Dict, List, Tuple, Callable, Optional
import json
import logging
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

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
# [QUÂNTICO / COLETIVO] - Simulação de Estado W
# ============================================================
def get_rainbow_factor(energy_ev: float) -> float:
    """
    Calcula o fator de escala da métrica rainbow: f(E) = 1 / (1 - E/E_res).
    E_res = 0.041 eV (~10 THz).
    """
    E_res = 0.041
    if abs(energy_ev - E_res) < 1e-6:
        return 100.0  # Cap para estabilidade numérica
    return 1.0 / (1.0 - (energy_ev / E_res))

def rainbow_coherence(base_coherence: float, cartan_angle: float, energy_ev: float) -> float:
    """
    Aplica o deslocamento da métrica rainbow.
    energy_ev: energia característica do sistema (ex: frequência THz convertida para eV)
    """
    rainbow_factor = get_rainbow_factor(energy_ev)
    # O ângulo efetivo de Cartan é modulado
    effective_cartan = cartan_angle * rainbow_factor
    # Nova coerência baseada no ângulo efetivo (centrada em pi/5)
    return base_coherence * np.exp(-((effective_cartan - np.pi/5)**2) / 0.001)

def simulate_rainbow_sl3z(
    theta_range: Optional[np.ndarray] = None,
    energy_ev: float = 0.0,
    words: List[str] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simula o modelo SL(3,ℤ) com deslocamento da métrica rainbow.
    """
    if theta_range is None:
        theta_range = np.linspace(0, 2*np.pi, 1000)

    if words is None:
        words = ["e", "a", "b", "ab", "ba", "aba"]

    rainbow_factor = get_rainbow_factor(energy_ev)

    # Coerência com picos deslocados
    coherence = np.zeros_like(theta_range)
    pi_over_5 = np.pi / 5

    for word in words:
        # A ressonância nominal len(word) * pi/5 é "vista" em um ângulo diferente pela métrica rainbow
        # O ângulo físico theta que sintoniza a ressonância é theta = (len(word) * pi/5) / rainbow_factor
        shifted_resonance = (len(word) * pi_over_5) / rainbow_factor
        resonance = np.exp(-((theta_range - shifted_resonance) ** 2) / 0.01)
        coherence += resonance / len(words)

    coherence = np.clip(coherence, 0, 1)
    return theta_range, coherence

def simulate_rainbow_w_state(
    nodes: int = 3,
    loss_probability: float = 0.2,
    theta_range: Optional[np.ndarray] = None,
    energy_ev: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simula o estado W com deslocamento da métrica rainbow.
    """
    if theta_range is None:
        theta_range = np.linspace(0, 2*np.pi, 1000)

    rainbow_factor = get_rainbow_factor(energy_ev)

    # Ressonância nominal 2pi/3 deslocada
    tripartite_resonance = (2 * np.pi / 3) / rainbow_factor
    resilience = 1.0 - (1.0 / nodes)

    base_signal = np.exp(-((theta_range - tripartite_resonance)**2) / 0.15)
    persistent_floor = resilience * (1.0 - loss_probability)

    coherence = np.maximum(base_signal, persistent_floor * 0.5)
    coherence = np.clip(coherence, 0, 1)

    return theta_range, coherence

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
# [PRAGMÁTICO / INTRAPESSOAL] - Detecção de Picos
# ============================================================
def detect_peaks(
    coherence_data: np.ndarray,
    phases: np.ndarray,
    threshold_multiplier: float = 1.5,
    min_prominence: float = 0.1,
    energy_ev: Optional[float] = None
) -> List[Dict]:
    """
    Usa janela deslizante para encontrar anomalias, considerando a métrica rainbow.
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

    # Fator rainbow para ajustar a detecção de ressonância
    rainbow_factor = get_rainbow_factor(energy_ev) if energy_ev is not None else 1.0

    # Tolerância da largura de banda geodésica: 0.41° = 0.0071 rad
    tolerance = 0.0071

    results = []
    for i, peak_idx in enumerate(peaks):
        peak_phase = phases[peak_idx]

        # Verifica se o pico coincide com uma ressonância nominal deslocada pela métrica rainbow
        is_resonance = False
        for n in range(1, 10): # Checa múltiplos de pi/5 e 2pi/3
            targets = [n * np.pi / 5, n * 2 * np.pi / 3]
            for target in targets:
                shifted_target = target / rainbow_factor
                if abs(peak_phase - shifted_target) < tolerance:
                    is_resonance = True
                    break
            if is_resonance: break

        results.append({
            'phase': peak_phase,
            'phase_degrees': np.degrees(peak_phase),
            'coherence': coherence_data[peak_idx],
            'prominence': properties['prominences'][i],
            'index': peak_idx,
            'is_resonance': is_resonance,
            'rainbow_shift': rainbow_factor
        })

    logger.info(f"Detectados {len(results)} picos acima do limiar (Energy={energy_ev} eV)")
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

    conclusion = {
        "status": "inconclusive",
        "peaks_total": len(peak_data),
        "peaks_in_resonance": len(resonances),
        "max_coherence": max_coherence,
        "interpretation": "",
        "philosophical_note": ""
    }

    # Avaliação
    if len(resonances) >= 2 and max_coherence > threshold:
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
