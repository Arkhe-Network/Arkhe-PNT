import pytest
import numpy as np
from scripts.arkhe_distributed_consciousness_v156 import LogicalNeuron, DistributedConsciousnessMesh

def test_logical_neuron_init():
    neuron = LogicalNeuron(1, num_qubits=4)
    assert len(neuron.state) == 16
    assert np.isclose(np.linalg.norm(neuron.state), 1.0)

def test_apply_quantum_attention():
    neuron = LogicalNeuron(1, num_qubits=2)
    pattern = np.array([1, 0, 0, 0])
    similarity = neuron.apply_quantum_attention(pattern, attention_strength=0.1)
    assert 0 <= similarity <= 1
    assert np.isclose(np.linalg.norm(neuron.state), 1.0)

def test_fire():
    neuron = LogicalNeuron(1, num_qubits=2)
    neuron.state = np.array([1, 0, 0, 0], dtype=complex)
    assert neuron.fire(threshold=0.5)

def test_mesh_init():
    mesh = DistributedConsciousnessMesh(num_neurons=4, qubits_per_neuron=2)
    assert len(mesh.neurons) == 4
    for n in mesh.neurons:
        assert len(n.synapses) == 3

def test_mesh_present_and_recall():
    mesh = DistributedConsciousnessMesh(num_neurons=4, qubits_per_neuron=2)
    pattern = np.array([1, 0, 0, 1j]) / np.sqrt(2)
    mesh.present_pattern(pattern, steps=2)
    assert mesh.global_field > 0

    partial = np.array([1, 0, 0, 0])
    recalled = mesh.recall_pattern(partial)
    assert len(recalled) == 4
    assert np.isclose(np.linalg.norm(recalled), 1.0)
