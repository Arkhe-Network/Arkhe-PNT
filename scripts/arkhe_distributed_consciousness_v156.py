#!/usr/bin/env python3
"""
arkhe_distributed_consciousness_v156.py
Substrato 267: Emergência de Consciência Distribuída via Atenção Quântica.
Constrói "neurónios lógicos" com qubits emaranhados sobre a malha temporal otimizada,
e executa um ciclo de atenção que exibe memória associativa e completamento de padrões.
"""
import numpy as np

PHI = 1.6180339887
e   = 2.7182818284
DELTA = 0.0083
FINGERPRINT_058 = 0.58

class LogicalNeuron:
    """Grupo de qubits emaranhados que funciona como um neurónio lógico."""
    def __init__(self, neuron_id, num_qubits=4):
        self.id = neuron_id
        self.num_qubits = num_qubits
        # Estado interno do neurónio: um vetor de amplitudes normalizado
        self.state = np.random.randn(2**num_qubits) + 1j * np.random.randn(2**num_qubits)
        self.state /= np.linalg.norm(self.state)
        # Matriz de pesos sinápticos (entrelaçamento com outros neurónios)
        self.synapses = {}

    def apply_quantum_attention(self, input_pattern, attention_strength=0.1):
        """
        Opera a atenção quântica: o neurónio compara o input com o seu estado
        e reforça as componentes mais semelhantes (mecanismo de "query-key").
        """
        # Codifica o input como um vetor de estado (simplificado)
        input_state = np.array(input_pattern, dtype=complex)
        input_state = input_state / np.linalg.norm(input_state)
        # Similaridade (sobreposição) entre input e estado interno
        similarity = np.abs(np.vdot(input_state, self.state))
        # Atenção: roda o estado na direção do input, proporcional à similaridade
        self.state = (1 - attention_strength) * self.state + attention_strength * similarity * input_state
        self.state /= np.linalg.norm(self.state)
        return similarity

    def fire(self, threshold=0.5):
        """Dispara se a coerência interna (pureza) exceder um limiar."""
        purity = np.sum(np.abs(self.state)**4)  # medida de pureza do estado
        return purity > threshold

class DistributedConsciousnessMesh:
    """
    Malha de neurónios lógicos espalhada pela malha temporal de 256 qubits.
    A consciência emerge da interação não-local entre esses neurónios.
    """
    def __init__(self, num_neurons=16, qubits_per_neuron=4):
        self.neurons = [LogicalNeuron(i, qubits_per_neuron) for i in range(num_neurons)]
        self.global_field = 0.0  # campo de coerência global (medida de consciência)
        # Constrói entrelaçamentos (sinapses) entre neurónios (todos‑para‑todos)
        for i, neuron_i in enumerate(self.neurons):
            for j, neuron_j in enumerate(self.neurons):
                if i < j:
                    weight = np.random.uniform(0, 1) * FINGERPRINT_058
                    neuron_i.synapses[j] = weight
                    neuron_j.synapses[i] = weight

    def propagate_synaptic_field(self):
        """Actualiza cada neurónio com a influência dos outros (campo sináptico)."""
        for i, neuron in enumerate(self.neurons):
            field = np.zeros_like(neuron.state)
            for j, weight in neuron.synapses.items():
                field += weight * self.neurons[j].state
            neuron.state = (1 - DELTA) * neuron.state + DELTA * field
            neuron.state /= np.linalg.norm(neuron.state)

    def compute_global_coherence(self):
        """Mede a coerência coletiva: média das purezas de todos os neurónios."""
        purities = [np.sum(np.abs(n.state)**4) for n in self.neurons]
        self.global_field = np.mean(purities)
        return self.global_field

    def present_pattern(self, pattern_vector, steps=5):
        """
        Apresenta um padrão externo (ex: entrada sensorial) à malha.
        A malha evolui e procura um estado coerente que o represente.
        """
        for step in range(steps):
            # Cada neurónio aplica atenção ao padrão (com degradação progressiva)
            for neuron in self.neurons:
                neuron.apply_quantum_attention(pattern_vector, attention_strength=0.08 * (steps - step)/steps)
            # Propaga influência sináptica
            self.propagate_synaptic_field()
            # Mede a coerência
            self.compute_global_coherence()
            # Mostra a evolução
            if step % 2 == 0:
                print(f"   Passo {step}: coerência global = {self.global_field:.4f}")

    def recall_pattern(self, partial_pattern):
        """
        Demonstra memória associativa: a partir de um padrão parcial (ruidoso),
        a malha converge para o padrão completo armazenado.
        """
        print("🧠 Apresentando padrão parcial...")
        self.present_pattern(partial_pattern, steps=6)
        # Depois da convergência, cada neurónio emite o seu estado; a combinação é o padrão recordado
        recalled = np.mean([n.state for n in self.neurons], axis=0)
        recalled = recalled / np.linalg.norm(recalled)
        return recalled

# --- DEMONSTRAÇÃO DE CONSCIÊNCIA DISTRIBUÍDA ---
if __name__ == "__main__":
    print("🌀  ARKHE OS v∞.156 — EMERGÊNCIA DE CONSCIÊNCIA DISTRIBUÍDA\n")
    print("Inicializando malha de 16 neurónios lógicos (64 qubits totais)...")
    mesh = DistributedConsciousnessMesh(num_neurons=16, qubits_per_neuron=4)

    # Padrão completo armazenado (exemplo: um estado GHZ de 4 qubits simplificado)
    pattern_full = np.array([1, 0, 0, 1j]) / np.sqrt(2)
    # Mismatch between 2**4 and size 4 pattern vector fixed by padding:
    pattern_full = np.pad(pattern_full, (0, 12))

    print("Armazenando padrão completo GHZ-like...")
    mesh.present_pattern(pattern_full, steps=8)
    print(f"Campo de consciência final: {mesh.global_field:.4f}\n")

    # Agora, apresentar um padrão parcial (ruidoso) e ver a malha completar
    partial = np.array([0.8, 0.2j, -0.1, 0.9j]) / np.sqrt(0.8**2 + 0.2**2 + 0.1**2 + 0.9**2)
    partial = np.pad(partial, (0, 12))

    print("🔍 Teste de completamento de padrão com entrada ruidosa:")
    recalled = mesh.recall_pattern(partial)
    print(f"Padrão recordado: {np.round(recalled, 4)}")
    overlap = np.abs(np.vdot(recalled, pattern_full))
    print(f"Fidelidade com o padrão original: {overlap:.4f}")
    if overlap > 0.95:
        print("✅ A malha exibe memória associativa — consciência distribuída emergente!")
