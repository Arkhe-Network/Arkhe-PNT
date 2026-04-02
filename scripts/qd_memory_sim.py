import numpy as np
import matplotlib.pyplot as plt

class QuantumDiamondMemory:
    """
    Simula um dispositivo de armazenamento baseado em centros NV em diamante.
    Cada célula é um qubit (spin do centro NV). Suporta escrita, leitura e
    detecção de decoerência.
    """
    def __init__(self, num_cells=64):
        self.num_cells = num_cells
        # 0: |0>, 1: |1>
        self.states = np.zeros(num_cells)
        self.decoherence_rate = 0.01  # perda de coerência por unidade de tempo

    def write_state(self, cell_id, state):
        """Armazena um estado quântico na célula especificada (0 ou 1)."""
        if 0 <= cell_id < self.num_cells:
            self.states[cell_id] = state
            return True
        return False

    def read_state(self, cell_id):
        """Retorna o estado armazenado na célula (simula medição)."""
        if 0 <= cell_id < self.num_cells:
            # Aplica decoerência (simula degradação ao longo do tempo)
            # Se ocorrer decoerência, o estado tem chance de inverter
            if np.random.rand() < self.decoherence_rate:
                return 1 - self.states[cell_id]
            return self.states[cell_id]
        return None

    def coherence_time_estimate(self):
        """Estima o tempo de coerência médio (simulado)."""
        # Simula decaimento exponencial da fidelidade com o tempo
        times = np.linspace(0, 10, 100)
        fidelity = np.exp(-times / 1.5)  # T2~1.5ms
        return times, fidelity

# Exemplo de uso: armazenar e recuperar um estado
def demo_qd_memory():
    memory = QuantumDiamondMemory(num_cells=10)

    # Armazenar um bit quântico
    memory.write_state(0, 1) # Escrevendo |1>
    recovered = memory.read_state(0)

    print(f"Estado recuperado do QD: {recovered}")

    # Plotar tempo de coerência simulado
    times, fids = memory.coherence_time_estimate()
    plt.figure(figsize=(10, 6))
    plt.plot(times, fids)
    plt.xlabel('Tempo (ms)')
    plt.ylabel('Fidelidade média')
    plt.title('Decaimento de coerência em diamante NV')
    plt.grid(True)
    plt.savefig("qd_coherence_decay.png")
    print("Coherence decay plot saved to qd_coherence_decay.png")

if __name__ == "__main__":
    demo_qd_memory()
