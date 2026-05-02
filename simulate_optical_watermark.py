#!/usr/bin/env python3
"""
simulate_optical_watermark.py
Implementa codificação de hash ZEE200 (256 bits) como padrão de interferência espectral
via interferômetro de Mach-Zehnder programável.
"""
import numpy as np
import hashlib
from pathlib import Path

# Parâmetros do watermarking óptico
WATERMARK_PARAMS = {
    'epsilon': 0.01,              # Profundidade de modulação
    'n_frequencies': 256,          # Uma por bit do hash
    'frequency_spacing': 0.001,    # Δf entre componentes ortogonais
    'base_frequency': 0.01,        # f₀ para primeira componente
    'wavelength_axis': np.linspace(400, 1550, 1151),  # 400–1550 nm, 1 nm resolução
    'theta_key': 'arkhe_master_key_2026'  # Chave secreta para fases θₖ
}

def generate_zee200_hash(seed_data, length=256):
    """
    Gera hash ZEE200 simulado (256 bits) a partir de dados de entrada.

    Em produção, isto seria substituído por chamada real ao backend ZEE200.

    Args:
        seed_data: bytes ou string para hashing
        length: número de bits do hash (padrão: 256)

    Returns:
        hash_bits: array de bits ∈ {0,1}^length
    """
    # Hash SHA-256 como proxy para ZEE200
    if isinstance(seed_data, str):
        seed_data = seed_data.encode()

    sha256_hash = hashlib.sha256(seed_data).digest()

    # Converter para bits
    hash_bits = np.unpackbits(np.frombuffer(sha256_hash, dtype=np.uint8))

    # Truncar ou estender para length bits
    if len(hash_bits) > length:
        hash_bits = hash_bits[:length]
    elif len(hash_bits) < length:
        hash_bits = np.pad(hash_bits, (0, length - len(hash_bits)), mode='edge')

    return hash_bits

def generate_modulation_pattern(hash_bits, params):
    """
    Gera padrão de modulação espectral a partir do hash ZEE200.

    S_mod(λ) = 1 + ε · Σₖ hₖ · cos(2π · fₖ · λ + θₖ)

    Args:
        hash_bits: array de bits ∈ {0,1}^256
        params: dicionário com parâmetros de watermarking

    Returns:
        modulation_pattern: vetor de modulação ∈ ℝ^1151
    """
    epsilon = params['epsilon']
    lambda_axis = params['wavelength_axis']
    modulation = np.ones_like(lambda_axis)

    for k, bit in enumerate(hash_bits):
        if bit == 1:
            # Frequência espacial ortogonal
            f_k = params['base_frequency'] + k * params['frequency_spacing']

            # Fase inicial derivada da chave secreta
            theta_k = hash(params['theta_key'] + str(k)) % (2*np.pi)

            # Adicionar componente de interferência
            modulation += epsilon * np.cos(2*np.pi * f_k * lambda_axis + theta_k)

    return modulation

def apply_watermark(spectrum_base, hash_bits, params):
    """
    Aplica watermark óptico ao espectro base.

    S_watermarked(λ) = S_base(λ) · [1 + ε · Σₖ hₖ · cos(2π · fₖ · λ + θₖ)]

    Args:
        spectrum_base: espectro base sem watermark
        hash_bits: hash ZEE200 a codificar
        params: parâmetros de watermarking

    Returns:
        spectrum_watermarked: espectro com watermark aplicado
    """
    modulation = generate_modulation_pattern(hash_bits, params)
    return spectrum_base * modulation

def verify_optical_watermark(spectrum_measured, hash_expected, params, threshold=0.85):
    """
    Verifica watermark óptico via correlação espectral.

    Args:
        spectrum_measured: espectro medido (possivelmente com watermark)
        hash_expected: hash ZEE200 esperado para verificação
        params: parâmetros de watermarking
        threshold: limiar de correlação para aceitação

    Returns:
        verified: bool indicando se watermark foi detectado
        correlation_score: valor da correlação cruzada normalizada
        detection_confidence: estimativa de confiança da detecção
    """
    # Reconstruir padrão de modulação esperado
    modulation_expected = generate_modulation_pattern(hash_expected, params)

    # Normalizar espectros para correlação
    s_meas_norm = (spectrum_measured - np.mean(spectrum_measured)) / np.std(spectrum_measured)
    mod_norm = (modulation_expected - np.mean(modulation_expected)) / np.std(modulation_expected)

    # Correlação cruzada normalizada
    correlation = np.corrcoef(s_meas_norm, mod_norm)[0, 1]

    # Estimativa de confiança baseada em SNR teórico
    epsilon = params['epsilon']
    n_bits = np.sum(hash_expected)  # Número de bits ativos
    theoretical_snr = epsilon * np.sqrt(n_bits / 2)  # Aproximação para interferência coerente
    detection_confidence = min(1.0, correlation * theoretical_snr)

    verified = correlation > threshold

    return verified, float(correlation), float(detection_confidence)

def simulate_watermark_robustness(n_trials=20, snr_db_range=(10, 40)):
    """
    Simula robustez do watermarking a ruído e distorções.

    Args:
        n_trials: número de ensaios por condição de SNR
        snr_db_range: tupla (min_SNR_dB, max_SNR_dB) para varredura

    Returns:
        robustness_results: dicionário com métricas de robustez
    """
    results = {
        'snr_db': [],
        'detection_rate': [],
        'mean_correlation': [],
        'false_alarm_rate': []
    }

    # Gerar hash de teste e espectro base
    np.random.seed(42)
    hash_test = generate_zee200_hash(b'arkhe_watermark_test_2026')
    spectrum_base = np.ones_like(WATERMARK_PARAMS['wavelength_axis']) * 0.5  # Espectro plano simulado
    spectrum_watermarked = apply_watermark(spectrum_base, hash_test, WATERMARK_PARAMS)

    # Varredura de SNR
    for snr_db in np.linspace(snr_db_range[0], snr_db_range[1], 10):
        snr_linear = 10**(snr_db / 10)
        noise_power = np.var(spectrum_watermarked) / snr_linear

        detections = 0
        correlations = []
        false_alarms = 0

        for trial in range(n_trials):
            # Adicionar ruído gaussiano
            noise = np.random.normal(0, np.sqrt(noise_power), len(spectrum_watermarked))
            spectrum_noisy = spectrum_watermarked + noise

            # Verificar watermark correto
            verified, corr, conf = verify_optical_watermark(
                spectrum_noisy, hash_test, WATERMARK_PARAMS
            )
            if verified:
                detections += 1
            correlations.append(corr)

            # Teste de falso alarme com hash incorreto
            hash_wrong = np.roll(hash_test, shift=1)  # Hash deslocado
            verified_wrong, _, _ = verify_optical_watermark(
                spectrum_noisy, hash_wrong, WATERMARK_PARAMS
            )
            if verified_wrong:
                false_alarms += 1

        results['snr_db'].append(snr_db)
        results['detection_rate'].append(detections / n_trials)
        results['mean_correlation'].append(np.mean(correlations))
        results['false_alarm_rate'].append(false_alarms / n_trials)

    return results

if __name__ == '__main__':
    print("🔐 Simulando codificação de hash ZEE200 em padrão de interferência...")
    print(f"   Parâmetros: ε={WATERMARK_PARAMS['epsilon']}, "
          f"n_freq={WATERMARK_PARAMS['n_frequencies']}, λ=[400, 1550] nm")

    # Gerar hash de teste
    hash_test = generate_zee200_hash(b'arkhe_proof_seed_2026')
    print(f"   Hash ZEE200 gerado: {np.sum(hash_test)} bits ativos de {len(hash_test)}")

    # Espectro base simulado (resposta de sensor sem watermark)
    spectrum_base = np.ones_like(WATERMARK_PARAMS['wavelength_axis']) * 0.5
    spectrum_base += 0.1 * np.sin(0.01 * WATERMARK_PARAMS['wavelength_axis'])  # Estrutura espectral suave

    # Aplicar watermark
    spectrum_watermarked = apply_watermark(spectrum_base, hash_test, WATERMARK_PARAMS)

    # Verificar watermark
    verified, correlation, confidence = verify_optical_watermark(
        spectrum_watermarked, hash_test, WATERMARK_PARAMS
    )

    print(f"\n📊 Resultados de verificação:")
    print(f"   • Watermark detectado: {verified}")
    print(f"   • Correlação cruzada: {correlation:.4f}")
    print(f"   • Confiança da detecção: {confidence:.4f}")

    # Simular robustez a ruído
    print(f"\n🔍 Simulando robustez a ruído...")
    robustness = simulate_watermark_robustness(n_trials=10, snr_db_range=(10, 40))

    print(f"   SNR (dB) | Detecção | Correlação | Falso Alarme")
    print(f"   " + "-"*50)
    for i, snr in enumerate(robustness['snr_db']):
        print(f"   {snr:6.1f}   | {robustness['detection_rate'][i]:6.1%}   | "
              f"{robustness['mean_correlation'][i]:6.4f}   | "
              f"{robustness['false_alarm_rate'][i]:6.1%}")

    # Salvar resultados
    Path('results/watermark_simulation').mkdir(parents=True, exist_ok=True)
    np.savez('results/watermark_simulation/watermark_validation.npz',
             hash_bits=hash_test,
             spectrum_base=spectrum_base,
             spectrum_watermarked=spectrum_watermarked,
             verification={'verified': verified, 'correlation': correlation, 'confidence': confidence},
             robustness=robustness)

    print(f"\n💾 Resultados salvos: results/watermark_simulation/watermark_validation.npz")

    if verified and correlation > 0.9:
        print(f"✅ Watermarking óptico VALIDADO: codificação ZEE200 → interferência espectral funcional")
    else:
        print(f"⚠️  Watermarking necessita ajuste de ε, frequências ou chave de fase")