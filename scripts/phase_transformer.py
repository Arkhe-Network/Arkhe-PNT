import math
import random
import time
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TrajectoryPoint:
    t: float
    r_t: float
    entropy: float
    throughput_gbps: float

class PhaseTrajectoryTransformer:
    """
    Simula o Layer τ do Planejador de Deployment.
    Prediz trajetórias de coerência R(t) baseadas em estados passados e parâmetros de hardware (VCSEL).
    """
    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
        # Parâmetros baseados no paper SPIE 2026: 362.71 Gbps aggregate, 1.4 nJ/bit
        self.max_throughput = 362.71
        self.energy_efficiency = 1.4 # nJ/bit

    def predict_trajectory(self, current_phases: List[float], steps: int = 20) -> List[TrajectoryPoint]:
        print(f"τ [Transformer] Gerando trajetória de fase para {len(current_phases)} nós...")

        trajectory = []
        phases = list(current_phases)

        for i in range(steps):
            # Simula a evolução da fase para convergência (Kuramoto simplificado)
            # R(t) = |1/N sum exp(i * phase_j)|
            r_t = abs(sum(complex(math.cos(p), math.sin(p)) for p in phases)) / len(phases)

            # Cálculo de entropia (simplificado)
            entropy = 1.0 - r_t

            # Throughput simulado: escala com a coerência
            # No paper, throughput depende da SNR. Aqui associamos SNR alta a alta coerência.
            current_throughput = self.max_throughput * (r_t ** 2)

            trajectory.append(TrajectoryPoint(
                t=float(i),
                r_t=r_t,
                entropy=entropy,
                throughput_gbps=current_throughput
            ))

            # Atualiza fases para o próximo passo (atração para a média)
            avg_phase = math.atan2(
                sum(math.sin(p) for p in phases),
                sum(math.cos(p) for p in phases)
            )

            for j in range(len(phases)):
                # K = 0.1 (coupling constant)
                phases[j] = (phases[j] + 0.1 * math.sin(avg_phase - phases[j]) + random.uniform(-0.01, 0.01)) % (2 * math.pi)

        return trajectory

def print_trajectory(traj: List[TrajectoryPoint]):
    print(f"{'Step':<5} | {'R(t)':<8} | {'Entropy':<8} | {'Throughput (Gbps)':<18}")
    print("-" * 50)
    for p in traj:
        print(f"{p.t:<5.0f} | {p.r_t:<8.4f} | {p.entropy:<8.4f} | {p.throughput_gbps:<18.2f}")

if __name__ == "__main__":
    transformer = PhaseTrajectoryTransformer()

    # Caso 1: Alta dessincronia
    init_phases = [0.0, math.pi, math.pi/2]
    print("\n--- Cenário: Alta Dessincronia ---")
    traj1 = transformer.predict_trajectory(init_phases)
    print_trajectory(traj1)

    # Caso 2: Quase síncrono
    init_phases_sync = [0.1, 0.2, 0.0]
    print("\n--- Cenário: Quase Síncrono ---")
    traj2 = transformer.predict_trajectory(init_phases_sync)
    print_trajectory(traj2)
