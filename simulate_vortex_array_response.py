#!/usr/bin/env python3
"""
simulate_vortex_array_response.py
Simula resposta espectral da matriz 10×10 μm de micro-vórtices.
Valida invertibilidade: fase óptica → assinatura espectral → reconstrução de fase.
"""
import numpy as np
import h5py
from pathlib import Path
from scipy.fft import fft2, fftshift, ifft2, ifftshift
from scipy.optimize import least_squares

# Parâmetros físicos da matriz de micro-vórtices
VORTEX_PARAMS = {
    'pitch': 1e-6,              # 1 μm centro-a-centro
    'core_diameter': 300e-9,    # 300 nm núcleo do vórtice
    'depth': 1.5e-6,            # 1.5 μm profundidade
    'dn_range': (0.02, 0.08),   # Δn modulado
    'array_size': (10, 10),     # 10×10 vórtices
    'wavelength_range': (400e-9, 1550e-9),  # 400–1550 nm
    'n_pixels': 1151            # 1 nm resolução espectral
}

def generate_vortex_phase_profile(x, y, vortex_params):
    """
    Gera perfil de fase óptica da matriz de micro-vórtices.

    Args:
        x, y: coordenadas espaciais (arrays 2D)
        vortex_params: dicionário com parâmetros da matriz

    Returns:
        phase_profile: fase óptica φ(x,y) ∈ [0, 2π)
    """
    pitch = vortex_params['pitch']
    core_d = vortex_params['core_diameter']
    dn_min, dn_max = vortex_params['dn_range']
    nx, ny = vortex_params['array_size']

    # Profundidade óptica efetiva (proporcional a Δn × depth)
    depth_eff = vortex_params['depth'] * np.mean([dn_min, dn_max])

    # Fase base
    phase = np.zeros_like(x)

    # Adicionar contribuição de cada vórtice
    for i in range(nx):
        for j in range(ny):
            # Centro do vórtice
            cx = (i - nx/2 + 0.5) * pitch
            cy = (j - ny/2 + 0.5) * pitch

            # Distância radial ao centro
            r = np.sqrt((x - cx)**2 + (y - cy)**2)

            # Perfil de vórtice: fase azimutal + modulação radial
            theta = np.arctan2(y - cy, x - cx)
            radial_profile = np.exp(-((r - core_d/2)**2) / (2 * (core_d/4)**2))

            # Fase do vórtice: carga topológica m=1
            vortex_phase = theta * radial_profile * depth_eff * 2*np.pi / vortex_params['wavelength_range'][1]

            phase += vortex_phase

    return np.mod(phase, 2*np.pi)

def phase_to_spectrum(phi_oscillators, kappa, vortex_params, phi_sync=0.58*np.pi):
    """
    Converte fases dos osciladores do Crystal Brain em espectro óptico.

    Modelo simplificado:
    1. Acoplamento evanescente: Δφ_opt(λ) = Σᵢ αᵢ(λ)·sin(φᵢ - φ_sync)
    2. Transformada de Fourier espacial via difração na matriz de vórtices
    3. Intensidade espectral: S(λ) = |ℱ{exp[i·Δφ_opt·V(x,y)]}|²

    Args:
        phi_oscillators: fases φᵢ ∈ [0, 2π) dos 768 osciladores
        kappa: acoplamento global (afeta αᵢ(λ))
        vortex_params: parâmetros da matriz de micro-vórtices
        phi_sync: fase de sincronização do fingerprint ARKHE

    Returns:
        spectrum: vetor espectral S(λ) ∈ ℝ^1151 (400–1550 nm, 1 nm resolução)
    """
    n_osc = len(phi_oscillators)
    lambda_min, lambda_max = vortex_params['wavelength_range']
    n_lambda = vortex_params['n_pixels']
    wavelengths = np.linspace(lambda_min, lambda_max, n_lambda)

    # Coeficientes de acoplamento espectral αᵢ(λ)
    # Modelo simplificado: dependência gaussiana com pico em λ₀
    lambda_0 = 975e-9  # Comprimento de onda central
    sigma_lambda = 200e-9  # Largura espectral

    spectrum = np.zeros(n_lambda)

    for idx, lam in enumerate(wavelengths):
        # Acoplamento espectral modulado por kappa
        alpha = kappa * np.exp(-((lam - lambda_0)**2) / (2 * sigma_lambda**2))

        # Deslocamento de fase óptica induzido pelos osciladores
        delta_phi_opt = np.sum(alpha * np.sin(phi_oscillators - phi_sync))

        # Gerar perfil de fase da matriz de vórtices para este λ
        # (simplificação: usamos grade espacial fixa)
        nx, ny = 128, 128  # Grade para FFT
        x = np.linspace(-5e-6, 5e-6, nx)
        y = np.linspace(-5e-6, 5e-6, ny)
        X, Y = np.meshgrid(x, y)

        vortex_phase = generate_vortex_phase_profile(X, Y, vortex_params)

        # Campo óptico: exp[i · Δφ_opt · V(x,y)]
        optical_field = np.exp(1j * delta_phi_opt * vortex_phase)

        # Transformada de Fourier espacial (difração)
        far_field = fftshift(fft2(optical_field))

        # Intensidade espectral: integrar sobre plano focal
        intensity = np.mean(np.abs(far_field)**2)
        spectrum[idx] = intensity

    # Normalizar espectro
    spectrum = spectrum / np.max(spectrum)

    return spectrum

def spectrum_to_phase(spectrum, vortex_params, phi_sync=0.58*np.pi,
                      n_osc=768, max_iter=100, tol=1e-4):
    """
    Reconstrói fases dos osciladores a partir do espectro medido.

    Usa otimização não-linear para inverter phase_to_spectrum.
    Nota: A invertibilidade é garantida apenas localmente (vizinhança do manifold CAPTURE).

    Args:
        spectrum: vetor espectral medido S(λ)
        vortex_params: parâmetros da matriz de micro-vórtices
        phi_sync: fase de sincronização
        n_osc: número de osciladores (768)
        max_iter: iterações máximas da otimização
        tol: tolerância de convergência

    Returns:
        phi_reconstructed: fases reconstruídas φᵢ ∈ [0, 2π)
        success: bool indicando convergência
        residual: erro quadrático médio da reconstrução
    """
    lambda_min, lambda_max = vortex_params['wavelength_range']
    n_lambda = vortex_params['n_pixels']
    wavelengths = np.linspace(lambda_min, lambda_max, n_lambda)

    def reconstruction_error(phi_flat, kappa_guess=0.75):
        """Função de erro para otimização."""
        phi = phi_flat.reshape(n_osc, 1)  # (768, 1)

        # Calcular espectro previsto
        spec_pred = phase_to_spectrum(phi.ravel(), kappa_guess, vortex_params, phi_sync)

        # Erro quadrático médio
        mse = np.mean((spec_pred - spectrum)**2)
        return mse

    # Inicialização: fases aleatórias próximas ao manifold CAPTURE
    np.random.seed(42)
    phi_init = np.random.uniform(0, 2*np.pi, n_osc)

    # Otimização: least_squares com bounds [0, 2π]
    result = least_squares(
        lambda p: phase_to_spectrum(p, 0.75, vortex_params, phi_sync) - spectrum,
        phi_init,
        bounds=(0, 2*np.pi),
        max_nfev=max_iter,
        ftol=tol
    )

    phi_reconstructed = np.mod(result.x, 2*np.pi)
    success = result.success and result.cost < tol
    residual = np.sqrt(result.cost)

    return phi_reconstructed, success, residual

def validate_invertibility(n_trials=10, noise_level=0.01):
    """
    Valida invertibilidade fase→espectro→fase via simulação Monte Carlo.

    Args:
        n_trials: número de ensaios de validação
        noise_level: ruído aditivo no espectro (fração da intensidade máxima)

    Returns:
        results: dicionário com métricas de validação
    """
    results = {
        'success_rate': 0,
        'mean_reconstruction_error': 0,
        'mean_residual': 0,
        'trials': []
    }

    for trial in range(n_trials):
        # Gerar fases aleatórias próximas ao manifold CAPTURE
        np.random.seed(trial)
        phi_true = np.random.uniform(0.3*np.pi, 0.7*np.pi, 768)  # Vizinhana de φ_sync

        # Calcular espectro "verdadeiro"
        spectrum_true = phase_to_spectrum(phi_true, kappa=0.75, vortex_params=VORTEX_PARAMS)

        # Adicionar ruído de medição
        noise = np.random.normal(0, noise_level, len(spectrum_true))
        spectrum_noisy = np.clip(spectrum_true + noise, 0, 1)

        # Reconstruir fases
        phi_rec, success, residual = spectrum_to_phase(
            spectrum_noisy, VORTEX_PARAMS, n_osc=768
        )

        # Calcular erro de reconstrução (invariante a permutação global de fase)
        # Usar correlação circular como métrica
        phase_diff = np.angle(np.exp(1j * (phi_true - phi_rec)))
        reconstruction_error = np.mean(np.abs(phase_diff))

        results['trials'].append({
            'trial': trial,
            'success': success,
            'residual': residual,
            'reconstruction_error': reconstruction_error
        })

        if success:
            results['success_rate'] += 1
            results['mean_reconstruction_error'] += reconstruction_error
            results['mean_residual'] += residual

    # Normalizar métricas
    n_success = results['success_rate']
    results['success_rate'] /= n_trials
    if n_success > 0:
        results['mean_reconstruction_error'] /= n_success
        results['mean_residual'] /= n_success

    return results

if __name__ == '__main__':
    print("🔬 Simulando resposta espectral da matriz de micro-vórtices...")
    print(f"   Parâmetros: {VORTEX_PARAMS['array_size'][0]}×{VORTEX_PARAMS['array_size'][1]} vórtices, "
          f"pitch={VORTEX_PARAMS['pitch']*1e6:.1f} μm, λ={np.array(VORTEX_PARAMS['wavelength_range'])*1e9} nm")

    # Validar invertibilidade
    validation = validate_invertibility(n_trials=5, noise_level=0.01)

    print(f"\n📊 Resultados de validação (n={validation['trials'].__len__()} ensaios):")
    print(f"   • Taxa de sucesso: {validation['success_rate']*100:.1f}%")
    print(f"   • Erro médio de reconstrução: {validation['mean_reconstruction_error']:.4f} rad")
    print(f"   • Residual médio: {validation['mean_residual']:.4f}")

    # Salvar resultados
    Path('results/vortex_simulation').mkdir(parents=True, exist_ok=True)
    with h5py.File('results/vortex_simulation/vortex_response_validation.h5', 'w') as f:
        f.create_dataset('validation_results', data=np.array([
            validation['success_rate'],
            validation['mean_reconstruction_error'],
            validation['mean_residual']
        ]))
        for i, trial in enumerate(validation['trials']):
            grp = f.create_group(f'trial_{i}')
            for k, v in trial.items():
                if k != 'trial':
                    grp.create_dataset(k, data=v)

    print(f"\n💾 Resultados salvos: results/vortex_simulation/vortex_response_validation.h5")

    if validation['success_rate'] > 0.8:
        print(f"✅ Invertibilidade fase→espectro VALIDADA para vizinhança do manifold CAPTURE")
    else:
        print(f"⚠️  Invertibilidade necessita refinamento do modelo ou redução de ruído")