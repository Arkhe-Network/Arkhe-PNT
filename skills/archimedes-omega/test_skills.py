# test_skills.py
import pytest
import numpy as np
import json
import tempfile
from pathlib import Path
import os

# Importar módulos a testar
from skills import (
    load_baseline,
    simulate_su2_continuous,
    simulate_sl3z_discrete,
    simulate_w_state_coherence,
    detect_peaks,
    synthesize_conclusion,
    visualize_topology
)


# ============================================================
# Testes: simulate_w_state_coherence (Quântico/Coletivo)
# ============================================================
def test_simulate_w_state_coherence_output_shape(theta_range):
    """Verifica formato da saída."""
    phases, coherence = simulate_w_state_coherence(theta_range=theta_range)

    assert len(phases) == len(theta_range)
    assert len(coherence) == len(theta_range)


def test_simulate_w_state_coherence_values():
    """Verifica que coerência está no intervalo [0, 1]."""
    _, coherence = simulate_w_state_coherence()
    assert np.all(coherence >= 0.0)
    assert np.all(coherence <= 1.0)


def test_simulate_w_state_coherence_resilience():
    """Verifica que maior número de nodos aumenta a resiliência (piso de coerência)."""
    theta = np.linspace(0, 2*np.pi, 100)

    # Com 3 nodos
    _, coherence_3 = simulate_w_state_coherence(nodes=3, loss_probability=0.5, theta_range=theta)
    # Com 10 nodos
    _, coherence_10 = simulate_w_state_coherence(nodes=10, loss_probability=0.5, theta_range=theta)

    # O piso de coerência deve ser maior com 10 nodos (resiliência = 1 - 1/n)
    assert np.min(coherence_10) > np.min(coherence_3)


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def theta_range():
    """Range padrão de fases para testes."""
    return np.linspace(0, 2*np.pi, 100)


@pytest.fixture
def temp_dir():
    """Diretório temporário para testes de I/O."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================
# Testes: load_baseline (Interpersonal)
# ============================================================
def test_load_baseline_with_file(temp_dir):
    """Testa carregamento com arquivo válido."""
    state_file = temp_dir / "tzinor-state.json"
    test_data = {
        "status": "ready",
        "coherence": 0.95,
        "temperature": 310.0,
        "sample_id": "BEXORG-3.0-001"
    }
    state_file.write_text(json.dumps(test_data))

    result = load_baseline(str(state_file))

    assert result["status"] == "ready"
    assert result["coherence"] == 0.95
    assert result["temperature"] == 310.0


def test_load_baseline_fallback():
    """Testa fallback quando arquivo não existe."""
    result = load_baseline("nonexistent-file-xyz.json")

    assert result["status"] == "cold_start"
    assert result["coherence"] == 0.0
    assert "temperature" in result


# ============================================================
# Testes: simulate_su2_continuous (Lógico/Naturalista)
# ============================================================
def test_simulate_su2_continuous_output_shape(theta_range):
    """Verifica formato da saída."""
    phases, coherence = simulate_su2_continuous(theta_range=theta_range)

    assert len(phases) == len(theta_range)
    assert len(coherence) == len(theta_range)
    assert phases.shape == coherence.shape


def test_simulate_su2_continuous_values():
    """Verifica que coerência está no intervalo válido."""
    theta = np.linspace(0, np.pi, 50)
    phases, coherence = simulate_su2_continuous(theta_range=theta)

    assert np.all(coherence >= -0.1), "Coerência não pode ser excessivamente negativa (considerando ruído)"
    assert np.all(coherence <= 1.1), "Coerência não pode exceder 1 significativamente (considerando ruído)"


def test_simulate_su2_continuous_decay():
    """Verifica comportamento de decaimento."""
    theta = np.linspace(0, 2*np.pi, 100)
    phases, coherence = simulate_su2_continuous(
        theta_range=theta,
        thermal_noise=0.1,
        temperature=310.0
    )

    # Coerência deve decair com o aumento do ângulo (efeito térmico)
    # Usando média das janelas iniciais/finais para ignorar ruído individual
    assert np.mean(coherence[:10]) > np.mean(coherence[-10:]), "Decaimento não observado"


def test_simulate_su2_continuous_temperature_effect():
    """Verifica efeito da temperatura na decoerência."""
    theta = np.linspace(0.1, np.pi, 50) # Evitar 0 para o fator térmico

    # Temperatura baixa = maior coerência
    _, coherence_low = simulate_su2_continuous(theta_range=theta, temperature=77)
    # Temperatura alta = menor coerência
    _, coherence_high = simulate_su2_continuous(theta_range=theta, temperature=400)

    assert np.mean(coherence_low) > np.mean(coherence_high), \
        "Temperatura alta deveria reduzir coerência"


# ============================================================
# Testes: simulate_sl3z_discrete (Espacial/Musical)
# ============================================================
def test_simulate_sl3z_discrete_output_shape(theta_range):
    """Verifica formato da saída."""
    phases, coherence = simulate_sl3z_discrete(theta_range=theta_range)

    assert len(phases) == len(theta_range)
    assert len(coherence) == len(theta_range)


def test_simulate_sl3z_discrete_resonance():
    """Verifica que há ressonância em π/5."""
    theta = np.linspace(0, 2*np.pi, 1000)
    phases, coherence = simulate_sl3z_discrete(theta_range=theta)

    # Encontrar índice mais próximo de π/5
    idx_pi5 = np.argmin(np.abs(phases - np.pi/5))

    # A coerência no pico deve ser significativa
    assert coherence[idx_pi5] > 0.1, \
        f"Pico em π/5 muito fraco: {coherence[idx_pi5]}"


def test_simulate_sl3z_discrete_words():
    """Verifica efeito de diferentes palavras do grupo."""
    theta = np.linspace(0, 2*np.pi, 500)

    # Com palavras diferentes
    _, coherence_with_words = simulate_sl3z_discrete(
        theta_range=theta,
        words=["a", "b", "ab", "ba"]
    )

    # Sem palavras (usará default)
    _, coherence_default = simulate_sl3z_discrete(theta_range=theta)

    # Devem ser diferentes
    assert not np.allclose(coherence_with_words, coherence_default), \
        "Palavras não afetam a coerência"


# ============================================================
# Testes: detect_peaks (Pragmático/Intrapessoal)
# ============================================================
def test_detect_peaks_single_peak():
    """Detecta um único pico bem definido."""
    theta = np.linspace(0, np.pi, 200)
    signal = np.zeros_like(theta)

    # Criar pico em π/5
    peak_idx = np.argmin(np.abs(theta - np.pi/5))
    signal[peak_idx] = 0.95
    # Adicionar um pouco de decaimento para não ser tudo zero
    signal += 0.01

    peaks = detect_peaks(signal, theta, threshold_multiplier=0.5, min_prominence=0.1)

    assert len(peaks) == 1
    assert abs(peaks[0]['phase'] - np.pi/5) < 0.05


def test_detect_peaks_no_peaks():
    """Retorna lista vazia quando não há picos."""
    theta = np.linspace(0, np.pi, 100)
    signal = np.ones(100) * 0.5 # Sinal constante

    peaks = detect_peaks(signal, theta, threshold_multiplier=2.0)

    assert len(peaks) == 0


# ============================================================
# Testes: synthesize_conclusion (Criativo/Existencial)
# ============================================================
def test_synthesize_conclusion_discrete_confirmed():
    """Testa confirmação de reticulado discreto."""
    peaks = [
        {'phase': np.pi/5, 'coherence': 0.98, 'is_resonance': True},
        {'phase': 2*np.pi/5, 'coherence': 0.96, 'is_resonance': True}
    ]

    conclusion = synthesize_conclusion(peaks, threshold=0.95)

    assert conclusion['status'] == "DISCRETE_LATTICE_CONFIRMED"
    assert "ressonâncias" in conclusion['interpretation']


def test_synthesize_conclusion_no_signal():
    """Testa sem sinal detectado."""
    peaks = []

    conclusion = synthesize_conclusion(peaks, threshold=0.95)

    assert conclusion['status'] == "NO_SIGNAL"


# ============================================================
# Testes: visualize_topology (Visual/Practical)
# ============================================================
def test_visualize_topology_creates_file(temp_dir):
    """Verifica que arquivo de imagem é criado."""
    output_file = temp_dir / "test_coherence.png"

    su2_data = (
        np.linspace(0, 2*np.pi, 100),
        np.random.random(100)
    )
    sl3z_data = (
        np.linspace(0, 2*np.pi, 100),
        np.random.random(100)
    )
    peaks = []

    result = visualize_topology(
        su2_data, sl3z_data, peaks, str(output_file)
    )

    assert output_file.exists()
    assert result == str(output_file)


# ============================================================
# Executar testes
# ============================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
