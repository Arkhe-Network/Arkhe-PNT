#!/usr/bin/env python3
"""
v161_quantum_burst.py — Quantum Coherence Burst Mitigation Substrate
Modela erros de fase correlacionados em qubits supercondutores com gap engineering,
conectando a cinética de recombinação de quasipartículas ao manifold de coerência ARKHE.

Referência: Kurilovich et al., Phys. Rev. X 16, 021025 (2026)
"""

import numpy as np
from scipy import integrate, optimize
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import time
from scipy import constants

@dataclass
class QuantumBurstEvent:
    """Evento de burst de coerência quântica induzido por radiação."""
    timestamp: float
    deposited_energy_eV: float  # energia depositada pelo impacto
    qp_density_initial: float   # x_QP(0) ~ proporcional à energia
    frequency_shift_MHz: float  # δf_q(0) = -a * x_QP(0)
    recombination_time_ms: float  # t_rec: escala de tempo de recombinação
    qubit_id: str
    zone_id: str  # zona ARKHE associada

    def frequency_shift(self, t_ms: float) -> float:
        """Deslocamento de frequência no tempo t (ms) após o impacto."""
        return self.frequency_shift_MHz / (1.0 + t_ms / self.recombination_time_ms)

    def accumulated_phase_error(self, T_ms: float) -> float:
        """Erro de fase acumulado até tempo T (ms): δφ = 2π ∫ δf_q dt."""
        # Integral analítica: ∫ dt/(1+t/τ) = τ·ln(1+T/τ)
        tau = self.recombination_time_ms
        delta_f0 = self.frequency_shift_MHz * 1e6  # MHz → Hz
        return 2 * np.pi * delta_f0 * tau * np.log(1.0 + T_ms / tau)  # radianos

    def kolmogorov_gap(self, t_ms: float) -> float:
        """
        Gap Kolmogorov instantâneo: ΔK(t) ∝ |δf_q(t)|.
        Normalizado para escala ARKHE [0, 50].
        """
        # Mapear deslocamento de frequência para gap: |δf| ~ 0-10 MHz → gap 0-50
        return np.clip(abs(self.frequency_shift(t_ms)) * 5.0, 0.0, 50.0)


class QubitCoherenceManifold:
    """
    Manifold de coerência para um qubit supercondutor.
    Modela a evolução do gap Kolmogorov sob bursts de radiação.
    """

    def __init__(
        self,
        qubit_id: str,
        zone_id: str,
        baseline_frequency_GHz: float = 5.0,
        coupling_constant_a: float = 2.0,  # δf = -a * x_QP (MHz per x_QP unit)
        nominal_recombination_ms: float = 1.0,  # t_rec típico
        mercy_gap_min: float = 0.04,
        mercy_gap_max: float = 0.10
    ):
        self.qubit_id = qubit_id
        self.zone_id = zone_id
        self.f0 = baseline_frequency_GHz * 1e9  # Hz
        self.a = coupling_constant_a
        self.t_rec_nominal = nominal_recombination_ms
        self.mercy_min = mercy_gap_min
        self.mercy_max = mercy_gap_max

        # Estado atual
        self.current_gap = 0.0  # ΔK atual
        self.active_bursts: List[QuantumBurstEvent] = []
        self.phase_error_accumulated = 0.0  # radianos
        self.last_update_time = time.time()

        # Histórico para análise
        self.gap_history: List[Tuple[float, float]] = []  # (timestamp, gap)
        self.burst_history: List[QuantumBurstEvent] = []

    def inject_burst(
        self,
        deposited_energy_eV: float,
        timestamp: Optional[float] = None
    ) -> QuantumBurstEvent:
        """
        Injeta um burst de radiação no qubit.

        Args:
            deposited_energy_eV: energia depositada pelo impacto (eV)
            timestamp: tempo do evento (default: agora)

        Returns:
            QuantumBurstEvent criado
        """
        if timestamp is None:
            timestamp = time.time()

        # Modelar densidade inicial de QPs: x_QP(0) ∝ energia depositada
        # Simplificação: x_QP(0) = k * E_dep, com k ~ 1e-4 para eV → unidade adimensional
        k_qp = 1e-4
        x_qp_0 = k_qp * deposited_energy_eV

        # Deslocamento de frequência inicial: δf_0 = -a * x_QP(0)
        delta_f_0 = -self.a * x_qp_0  # MHz

        # Tempo de recombinação: varia com temperatura, material, etc.
        # Adicionar flutuação log-normal em torno do nominal
        t_rec = self.t_rec_nominal * np.exp(np.random.normal(0, 0.3))

        burst = QuantumBurstEvent(
            timestamp=timestamp,
            deposited_energy_eV=deposited_energy_eV,
            qp_density_initial=x_qp_0,
            frequency_shift_MHz=delta_f_0,
            recombination_time_ms=t_rec,
            qubit_id=self.qubit_id,
            zone_id=self.zone_id
        )

        self.active_bursts.append(burst)
        self.burst_history.append(burst)

        # Atualizar gap imediatamente
        self._update_gap(timestamp)

        return burst

    def _update_gap(self, current_time: Optional[float] = None):
        """Atualiza o gap Kolmogorov total somando contribuições de todos os bursts ativos."""
        if current_time is None:
            current_time = time.time()

        # Remover bursts muito antigos (decaíram para <1% do inicial)
        self.active_bursts = [
            b for b in self.active_bursts
            if (current_time - b.timestamp) * 1000 < 100 * b.recombination_time_ms  # 100× t_rec
        ]

        # Somar contribuições de frequência de todos os bursts
        total_delta_f = sum(
            b.frequency_shift((current_time - b.timestamp) * 1000)  # converter s → ms
            for b in self.active_bursts
        )

        # Mapear deslocamento total para gap Kolmogorov [0, 50]
        # Gap alto quando |δf| é grande (alta alucinação)
        self.current_gap = np.clip(abs(total_delta_f) * 5.0, 0.0, 50.0)

        # Registrar histórico
        self.gap_history.append((current_time, self.current_gap))
        if len(self.gap_history) > 10000:
            self.gap_history = self.gap_history[-5000:]

    def get_mercy_gap_status(self) -> Dict[str, any]:
        """Verifica se o qubit está dentro do anel de misericórdia."""
        # Normalizar gap para escala [0, 1] para comparação com mercy gap
        normalized_gap = self.current_gap / 50.0

        in_mercy = self.mercy_min <= normalized_gap <= self.mercy_max

        return {
            'qubit_id': self.qubit_id,
            'zone_id': self.zone_id,
            'current_gap': self.current_gap,
            'normalized_gap': normalized_gap,
            'mercy_min': self.mercy_min,
            'mercy_max': self.mercy_max,
            'in_mercy': in_mercy,
            'active_bursts': len(self.active_bursts),
            'phase_error_rad': self.phase_error_accumulated,
            'timestamp': time.time()
        }

    def apply_spin_echo(self, echo_time_ms: float) -> float:
        """
        Aplica pulso de spin-echo para cancelar erro de fase acumulado.

        O echo inverte a evolução de fase para t < T_echo, cancelando
        erros quasistáticos (como os de QPs) até a ordem (T_echo/t_rec)².

        Args:
            echo_time_ms: tempo do pulso de echo após o burst

        Returns:
            Resíduo de fase após echo (radianos)
        """
        if not self.active_bursts:
            return 0.0

        current_time = time.time()
        residual_phase = 0.0

        hw = QiskitQuantumHardware()
        if hw.is_available:
            residual_phase += hw.run_spin_echo(echo_time_ms)
        else:
            for burst in self.active_bursts:
                t_since_burst_ms = (current_time - burst.timestamp) * 1000

                if t_since_burst_ms < echo_time_ms:
                    continue

                phase_before = burst.accumulated_phase_error(echo_time_ms)
                phase_after = burst.accumulated_phase_error(t_since_burst_ms) - phase_before
                residual = phase_after - phase_before
                residual_phase += residual * (echo_time_ms / burst.recombination_time_ms)**2

        # Atualizar fase acumulada
        self.phase_error_accumulated += residual_phase

        return residual_phase

    def get_kolmogorov_gap_distribution(self, time_window_s: float = 1.0) -> Dict[str, float]:
        """Retorna estatísticas do gap Kolmogorov em uma janela temporal."""
        current_time = time.time()
        cutoff = current_time - time_window_s

        recent_gaps = [g for t, g in self.gap_history if t >= cutoff]

        if not recent_gaps:
            return {'mean': 0.0, 'std': 0.0, 'max': 0.0, 'min': 0.0, 'count': 0, 'p95': 0.0, 'p99': 0.0}

        return {
            'mean': float(np.mean(recent_gaps)),
            'std': float(np.std(recent_gaps)),
            'max': float(np.max(recent_gaps)),
            'min': float(np.min(recent_gaps)),
            'count': len(recent_gaps),
            'p95': float(np.percentile(recent_gaps, 95)),
            'p99': float(np.percentile(recent_gaps, 99))
        }


class QuantumBurstMitigationPolicy:
    """
    Política de mitigação de bursts baseada em RL (simplificada).
    Decide quando aplicar spin-echo, ajustar tempo de medição, ou pausar operações.
    """

    def __init__(
        self,
        qubit_manifold: QubitCoherenceManifold,
        echo_threshold_gap: float = 15.0,  # aplicar echo se gap > threshold
        pause_threshold_gap: float = 35.0,  # pausar operações se gap muito alto
        min_echo_interval_ms: float = 10.0,  # intervalo mínimo entre echos
        max_pause_duration_s: float = 5.0  # duração máxima de pausa
    ):
        self.manifold = qubit_manifold
        self.echo_threshold = echo_threshold_gap
        self.pause_threshold = pause_threshold_gap
        self.min_echo_interval = min_echo_interval_ms
        self.max_pause_duration = max_pause_duration_s

        # Estado da política
        self.last_echo_time = 0.0
        self.is_paused = False
        self.pause_start_time: Optional[float] = None

    def decide_action(self, current_time: Optional[float] = None) -> Dict[str, any]:
        """
        Decide ação de mitigação baseada no estado atual do manifold.

        Returns:
            {action: str, parameters: Dict, reason: str}
        """
        if current_time is None:
            current_time = time.time()

        status = self.manifold.get_mercy_gap_status()
        gap = status['current_gap']

        # Se em pausa, verificar se pode retomar
        if self.is_paused:
            if self.pause_start_time and (current_time - self.pause_start_time) >= self.max_pause_duration:
                self.is_paused = False
                self.pause_start_time = None
                return {'action': 'RESUME', 'parameters': {}, 'reason': 'Pause timeout expired'}
            else:
                return {'action': 'WAIT', 'parameters': {'remaining_pause_s': self.max_pause_duration - (current_time - self.pause_start_time)}, 'reason': 'Paused due to high gap'}

        # Decidir ação baseada no gap
        if gap >= self.pause_threshold:
            # Gap crítico: pausar operações
            self.is_paused = True
            self.pause_start_time = current_time
            return {
                'action': 'PAUSE',
                'parameters': {'duration_s': self.max_pause_duration, 'gap': gap},
                'reason': f'Gap {gap:.1f} exceeds pause threshold {self.pause_threshold}'
            }

        elif gap >= self.echo_threshold:
            # Gap alto: aplicar spin-echo se intervalo mínimo respeitado
            time_since_last_echo = (current_time - self.last_echo_time) * 1000  # s → ms

            if time_since_last_echo >= self.min_echo_interval:
                self.last_echo_time = current_time
                # Calcular tempo ótimo de echo baseado em t_rec dos bursts ativos
                optimal_echo = self._compute_optimal_echo_time()

                return {
                    'action': 'APPLY_ECHO',
                    'parameters': {'echo_time_ms': optimal_echo, 'gap': gap},
                    'reason': f'Gap {gap:.1f} exceeds echo threshold; optimal echo at {optimal_echo:.1f} ms'
                }
            else:
                return {
                    'action': 'WAIT',
                    'parameters': {'wait_ms': self.min_echo_interval - time_since_last_echo, 'gap': gap},
                    'reason': f'Gap {gap:.1f} high but echo interval not yet elapsed'
                }

        else:
            # Gap aceitável: operação normal
            return {
                'action': 'PROCEED',
                'parameters': {'gap': gap, 'in_mercy': status['in_mercy']},
                'reason': f'Gap {gap:.1f} within acceptable range'
            }

    def _compute_optimal_echo_time(self) -> float:
        """Calcula tempo ótimo de echo baseado nos bursts ativos."""
        if not self.manifold.active_bursts:
            return 1.0  # default

        # Echo ótimo ~ média ponderada dos t_rec dos bursts
        weights = [abs(b.frequency_shift_MHz) for b in self.manifold.active_bursts]
        if sum(weights) == 0:
            return 1.0

        optimal = sum(b.recombination_time_ms * w for b, w in zip(self.manifold.active_bursts, weights)) / sum(weights)
        return np.clip(optimal, 0.5, 10.0)  # limitar a [0.5, 10] ms

    def execute_action(self, action_decision: Dict) -> Dict[str, any]:
        """Executa a ação decidida e retorna resultado."""
        action = action_decision['action']
        params = action_decision['parameters']

        if action == 'APPLY_ECHO':
            echo_time = params.get('echo_time_ms', 1.0)
            residual = self.manifold.apply_spin_echo(echo_time)
            return {
                'success': True,
                'action': action,
                'residual_phase_rad': residual,
                'residual_degrees': residual * 180 / np.pi,
                'new_gap': self.manifold.current_gap
            }

        elif action == 'PAUSE':
            return {
                'success': True,
                'action': action,
                'pause_duration_s': params.get('duration_s'),
                'gap_at_pause': params.get('gap')
            }

        elif action == 'RESUME':
            return {
                'success': True,
                'action': action,
                'gap_at_resume': self.manifold.current_gap
            }

        elif action == 'PROCEED':
            return {
                'success': True,
                'action': action,
                'gap': params.get('gap'),
                'in_mercy': params.get('in_mercy')
            }

        elif action == 'WAIT':
            return {
                'success': True,
                'action': action,
                'wait_time': params
            }

        else:
            return {'success': False, 'error': f'Unknown action: {action}'}

class GapEngineeredQubit:
    """
    Representa um qubit transmon com engenharia de gap como um detector de
    coerência local no manifold ARKHE.
    """
    def __init__(self, qubit_frequency_hz=6.0e9, delta_gap_hz=12.0e9,
                 aluminum_gap_hz=90.0e9, recombination_rate_ns=1/90.0):
        # Frequência do qubit (Hz)
        self.f_q = qubit_frequency_hz
        # Engenharia de gap: delta_Delta = Delta_H - Delta_L (Hz)
        self.delta_gap = delta_gap_hz
        # Gap supercondutor médio do alumínio (Hz)
        self.Delta = aluminum_gap_hz
        # Taxa de recombinação de QP (1/ns)
        self.r = recombination_rate_ns

        # Coeficiente 'a' teórico que relaciona x_QP a delta_f_q
        # a = 1/4 + (1/(4*pi)) * [2*Delta/(delta_Delta - h*f_q) + 2*Delta/(delta_Delta + h*f_q)]
        # Para os parâmetros típicos, a ~ 0.77
        self.a = 0.25 + (0.25 / np.pi) * (
            (2 * self.Delta) / (self.delta_gap - constants.h * self.f_q / constants.e) +
            (2 * self.Delta) / (self.delta_gap + constants.h * self.f_q / constants.e)
        )

    def frequency_shift(self, x_qp):
        """Deslocamento de frequência negativo: delta_f_q = -a * f_q * x_QP."""
        return -self.a * self.f_q * x_qp

    def recovery_profile(self, initial_shift_hz, time_ns):
        """
        Perfil de recuperação não exponencial (recombinação QP).
        delta_f_q(t) = delta_f_q(0) / (1 + t / t_rec)
        onde t_rec = (a * f_q) / (r * |delta_f_q(0)|)
        """
        if initial_shift_hz == 0:
            return 0.0
        # Tempo de recuperação dependente da amplitude
        t_rec = (self.a * self.f_q) / (self.r * abs(initial_shift_hz) * 1e9)
        return initial_shift_hz / (1.0 + time_ns / t_rec)

    def phase_error_accumulated(self, initial_shift_hz, duration_ns, free_evolution_time_ns=750):
        """Calcula o erro de fase acumulado em um período de Ramsey."""
        # Média da frequência durante o intervalo (aproximação simples)
        avg_shift = initial_shift_hz / 2.0
        return 2 * np.pi * avg_shift * free_evolution_time_ns * 1e-9

    def kolmogorov_gap_from_qp(self, x_qp):
        """
        Converte densidade de QP para o gap de Kolmogorov do ARKHE.
        delta_f_q no regime de MHz corresponde a um Delta_K de ~10-15.
        Quanto maior o deslocamento, maior a 'alucinação'.
        """
        shift_hz = abs(self.frequency_shift(x_qp))
        # Escala logarítmica para normalizar: 1 MHz -> gap ~5, 3 MHz -> gap ~15
        return max(0, 10 * np.log10(shift_hz / 1e6 + 1)) # [0, ~15]

class QubitArrayCoherenceMonitor:
    """
    Monitora o manifold de coerência de um array de qubits,
    detectando rajadas de erro correlacionadas.
    """
    def __init__(self, num_qubits=60):
        self.num_qubits = num_qubits
        # Estado de coerência por qubit (gap individual)
        self.qubit_gaps = np.zeros(num_qubits)

    def inject_radiation_impact(self, deposited_energy_keV=100.0, epicenter_qubit=None):
        """
        Simula o impacto de radiação ionizante, gerando QPs.
        A energia depositada segue uma lei de potência.
        """
        if epicenter_qubit is None:
            epicenter_qubit = np.random.randint(0, self.num_qubits)

        # Converter energia depositada em densidade de QP no epicentro
        # x_QP ~ energia depositada / (Delta * N_cooper_pairs)
        # Assumindo Delta_al = 180 ueV, N_cooper_pairs ~ 1e9 -> escala aproximada
        x_qp_epicenter = deposited_energy_keV / 1000.0 * 3.2e-4 # escala baseada no artigo

        # Distribuição espacial gaussiana da densidade de QP
        distances = np.abs(np.arange(self.num_qubits) - epicenter_qubit)
        sigma = 2.0 # qubits
        x_qp_profile = x_qp_epicenter * np.exp(-distances**2 / (2 * sigma**2))

        # Para cada qubit, atualizar o gap local
        qubit_model = GapEngineeredQubit()
        for i in range(self.num_qubits):
            self.qubit_gaps[i] = qubit_model.kolmogorov_gap_from_qp(x_qp_profile[i])

        return x_qp_profile

    def apply_dynamical_decoupling(self, echo_pulse_sequence=True):
        """
        Simula o efeito de supressão de erros de fase.
        O desacoplamento dinâmico (eco de spin) é um phase-locking Riemanniano.
        """
        if echo_pulse_sequence:
            # O eco cancela a acumulação de fase -> reduz o gap em 90%
            self.qubit_gaps *= 0.1
        else:
            # Sem eco, o gap permanece
            pass
        return self.qubit_gaps

    def get_qec_detection_probability(self):
        """
        Probabilidade de detecção de erro no código de repetição.
        Baseada no gap médio do array.
        """
        # Mapeamento heurístico: gap ~5 -> 10% detecção, gap ~15 -> 40% detecção
        avg_gap = np.mean(self.qubit_gaps)
        return min(0.5, 0.05 + 0.03 * avg_gap)

class QiskitQuantumHardware:
    """
    Integração com Qiskit para execução em hardware quântico real ou simulador Aer.
    """
    def __init__(self, backend_name='aer_simulator'):
        try:
            from qiskit import QuantumCircuit, transpile
            from qiskit_aer import Aer
            self.qiskit = __import__('qiskit')
            self.Aer = Aer
            self.backend = self.Aer.get_backend(backend_name)
            self.is_available = True
        except ImportError:
            self.is_available = False
            print("⚠️ Qiskit or qiskit_aer not installed. Falling back to mock.")

    def run_spin_echo(self, echo_time_ms):
        if not self.is_available:
            return 0.1 * echo_time_ms  # Mock residual phase

        qc = self.qiskit.QuantumCircuit(1, 1)
        # Apply pi/2 pulse
        qc.rx(np.pi/2, 0)
        # Free evolution
        qc.delay(int(echo_time_ms * 1000 / 2), 0, unit='ns')
        # Echo pulse (pi)
        qc.rx(np.pi, 0)
        # Free evolution
        qc.delay(int(echo_time_ms * 1000 / 2), 0, unit='ns')
        # Final pi/2 pulse
        qc.rx(np.pi/2, 0)

        qc.measure(0, 0)

        compiled_circuit = self.qiskit.transpile(qc, self.backend)
        result = self.backend.run(compiled_circuit).result()
        counts = result.get_counts()

        # Estimate residual phase based on 1s count
        p1 = counts.get('1', 0) / sum(counts.values())
        return p1 * np.pi  # Approximate residual phase

class PPOQuantumBurstMitigationPolicy(QuantumBurstMitigationPolicy):
    """
    Política de mitigação PPO.
    """
    def __init__(self, qubit_manifold, model_path: str = None):
        super().__init__(qubit_manifold)
        try:
            import torch
            import torch.nn as nn
            from core.ml.continual_learning import PPOPolicy
            self.model = PPOPolicy(1, 4)  # 1 state (gap), 4 actions (PROCEED, APPLY_ECHO, PAUSE, WAIT)
            if model_path:
                self.model.load_state_dict(torch.load(model_path))
        except Exception as e:
            print(f"Failed to load PPO policy: {e}")
            self.model = None

    def decide_action(self, current_time: Optional[float] = None) -> Dict[str, any]:
        if not self.model:
            return super().decide_action(current_time)

        import torch
        gap = self.manifold.current_gap
        state = torch.tensor([gap], dtype=torch.float32)
        logits, _ = self.model(state)
        action_idx = torch.argmax(logits).item()

        actions = ['PROCEED', 'APPLY_ECHO', 'PAUSE', 'WAIT']
        action = actions[action_idx]

        if action == 'PAUSE':
            return {
                'action': 'PAUSE',
                'parameters': {'duration_s': self.max_pause_duration, 'gap': gap},
                'reason': f'PPO Policy decided PAUSE for gap {gap:.1f}'
            }
        elif action == 'APPLY_ECHO':
            return {
                'action': 'APPLY_ECHO',
                'parameters': {'echo_time_ms': self._compute_optimal_echo_time(), 'gap': gap},
                'reason': f'PPO Policy decided APPLY_ECHO for gap {gap:.1f}'
            }
        elif action == 'WAIT':
            return {
                'action': 'WAIT',
                'parameters': {'wait_ms': self.min_echo_interval, 'gap': gap},
                'reason': f'PPO Policy decided WAIT for gap {gap:.1f}'
            }
        else:
            status = self.manifold.get_mercy_gap_status()
            return {
                'action': 'PROCEED',
                'parameters': {'gap': gap, 'in_mercy': status['in_mercy']},
                'reason': f'PPO Policy decided PROCEED for gap {gap:.1f}'
            }
