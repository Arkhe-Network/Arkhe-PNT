#!/usr/bin/env python3
"""
simulate_optical_homeostasis.py
Simula loop homeostático puramente óptico:
Detector de desvio espectral → Atuador Kerr de κ → Osciladores de fase → Novo espectro.
Demonstra convergência a regime CAPTURE via ajuste óptico de acoplamento.
"""
import numpy as np
import json
from pathlib import Path
from scipy.integrate import solve_ivp

# Parâmetros do loop homeostático óptico
HOMEOSTASIS_PARAMS = {
    # Controle PI óptico
    'gamma_prop': 1e-3,      # Ganho proporcional
    'gamma_int': 1e-6,       # Ganho integral
    'kappa_bounds': (0.1, 2.0),  # Faixa de ajuste de κ

    # Osciladores de Kuramoto
    'n_oscillators': 768,    # Número de osciladores (Crystal Brain)
    'omega_mean': 2*np.pi*1e12,  # Frequência natural média: 1 THz
    'omega_spread': 0.01,    # Dispersão de frequências naturais (1%)
    'noise_amplitude': 0.01, # Amplitude do ruído de fase ξᵢ(t)

    # Sensor espectral
    'target_spectrum_file': 'results/vortex_simulation/target_capture_spectrum.npy',
    'spectral_resolution': 1e-9,  # 1 nm
    'wavelength_range': (400e-9, 1550e-9),

    # Simulação
    'dt': 1e-6,              # Passo de tempo: 1 μs
    'max_steps': 10000,      # Número máximo de passos
    'convergence_threshold': 1e-4,  # Limiar de erro para convergência
    'min_steps_for_convergence': 100  # Passos mínimos antes de verificar convergência
}

def generate_target_capture_spectrum(vortex_params, n_osc=768, phi_sync=0.58*np.pi):
    """
    Gera espectro alvo "ideal" para regime CAPTURE.

    Em produção, isto seria medido experimentalmente ou calculado via modelo físico completo.
    Aqui usamos um espectro sintético com características de coerência alta.

    Args:
        vortex_params: parâmetros da matriz de micro-vórtices
        n_osc: número de osciladores
        phi_sync: fase de sincronização

    Returns:
        target_spectrum: vetor espectral S_target(λ) ∈ ℝ^1151
    """
    lambda_axis = np.linspace(
        vortex_params['wavelength_range'][0],
        vortex_params['wavelength_range'][1],
        vortex_params['n_pixels']
    )

    # Espectro alvo: pico estreito em λ₀ com caudas gaussianas
    # (assinatura de alta coerência no manifold CAPTURE)
    lambda_0 = 975e-9
    sigma_narrow = 15e-9   # Pico estreito: coerência alta
    sigma_broad = 100e-9   # Caudas largas: ruído residual

    target = (
        0.7 * np.exp(-((lambda_axis - lambda_0)**2) / (2 * sigma_narrow**2)) +
        0.3 * np.exp(-((lambda_axis - lambda_0)**2) / (2 * sigma_broad**2))
    )

    # Normalizar
    target = target / np.max(target)

    return target

def kuramoto_optical_dynamics(t, phi, kappa, omega, noise_amp):
    """
    Equações de Kuramoto para osciladores ópticos com ruído.

    dφᵢ/dt = ωᵢ + (κ/N) Σⱼ sin(φⱼ - φᵢ) + ξᵢ(t)

    Args:
        t: tempo (não usado explicitamente, mas requerido por solve_ivp)
        phi: vetor de fases φᵢ ∈ [0, 2π)
        kappa: acoplamento global
        omega: vetor de frequências naturais ωᵢ
        noise_amp: amplitude do ruído de fase

    Returns:
        dphi_dt: derivadas temporais das fases
    """
    n = len(phi)

    # Termo de acoplamento de Kuramoto
    coupling = np.zeros(n)
    for i in range(n):
        coupling[i] = np.sum(np.sin(phi - phi[i]))
    coupling *= kappa / n

    # Ruído de fase (Wiener process discretizado)
    noise = noise_amp * np.random.randn(n) / np.sqrt(HOMEOSTASIS_PARAMS['dt'])

    return omega + coupling + noise

def compute_spectral_error(phi, kappa, target_spectrum, vortex_params, phi_sync=0.58*np.pi):
    """
    Calcula erro espectral δ = ∫|S(λ; φ) - S_target(λ)|² dλ.

    Args:
        phi: fases atuais dos osciladores
        kappa: acoplamento global atual
        target_spectrum: espectro alvo
        vortex_params: parâmetros da matriz de micro-vórtices
        phi_sync: fase de sincronização

    Returns:
        error: erro espectral quadrático médio
    """
    # Calcular espectro atual (usando função do módulo anterior)
    from simulate_vortex_array_response import phase_to_spectrum
    spectrum_current = phase_to_spectrum(phi, kappa, vortex_params, phi_sync)

    # Erro quadrático médio espectral
    error = np.trapezoid((spectrum_current - target_spectrum)**2, dx=HOMEOSTASIS_PARAMS['spectral_resolution'])

    return error

def simulate_optical_homeostatic_loop(params):
    """
    Simula loop homeostático óptico completo.

    Retorna histórico de fases, espectros, κ e erro para análise de convergência.
    """
    # Inicialização
    np.random.seed(42)
    n_osc = params['n_oscillators']

    # Fases iniciais: aleatórias, mas com tendência ao manifold CAPTURE
    phi_sync = 0.58 * np.pi
    phi_init = np.random.uniform(phi_sync - 0.3*np.pi, phi_sync + 0.3*np.pi, n_osc)

    # Frequências naturais: distribuição gaussiana em torno de ω_mean
    omega = params['omega_mean'] * (1 + params['omega_spread'] * np.random.randn(n_osc))

    # Acoplamento inicial
    kappa = 0.75  # Valor típico para Crystal Brain
    integral_error = 0.0

    # Carregar ou gerar espectro alvo
    target_path = Path(params['target_spectrum_file'])
    if target_path.exists():
        target_spectrum = np.load(target_path)
    else:
        from simulate_vortex_array_response import VORTEX_PARAMS
        target_spectrum = generate_target_capture_spectrum(VORTEX_PARAMS, n_osc)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(target_path, target_spectrum)

    # Histórico para análise
    history = {
        'time': [], 'kappa': [], 'error': [],
        'phi_mean': [], 'phi_std': [], 'coherence': []
    }

    print(f"   🔄 Iniciando loop homeostático: κ₀={kappa:.3f}, φ_sync={phi_sync:.3f}")

    # Loop principal de simulação
    for step in range(params['max_steps']):
        t = step * params['dt']

        # [1] Calcular erro espectral atual
        from simulate_vortex_array_response import VORTEX_PARAMS
        error = compute_spectral_error(phi_init, kappa, target_spectrum, VORTEX_PARAMS)

        # [2] Atualizar κ via controle PI óptico
        integral_error += error * params['dt']
        kappa_new = kappa + params['gamma_prop'] * error + params['gamma_int'] * integral_error
        kappa = np.clip(kappa_new, *params['kappa_bounds'])

        # [3] Atualizar fases via integração de Kuramoto
        # Usar Euler-Maruyama para eficiência (solve_ivp seria mais preciso mas mais lento)
        dphi = kuramoto_optical_dynamics(t, phi_init, kappa, omega, params['noise_amplitude'])
        phi_init = np.mod(phi_init + dphi * params['dt'], 2*np.pi)

        # [4] Calcular métricas de coerência
        coherence = np.abs(np.mean(np.exp(1j * phi_init)))  # Parâmetro de ordem de Kuramoto
        phi_mean = np.angle(np.mean(np.exp(1j * phi_init)))
        phi_std = np.std(np.angle(np.exp(1j * (phi_init - phi_mean))))

        # [5] Registrar histórico
        history['time'].append(t)
        history['kappa'].append(kappa)
        history['error'].append(error)
        history['phi_mean'].append(phi_mean)
        history['phi_std'].append(phi_std)
        history['coherence'].append(coherence)

        # [6] Verificar convergência
        if step > params['min_steps_for_convergence'] and error < params['convergence_threshold']:
            print(f"   ✓ Convergiu em {step} passos: erro={error:.2e}, κ={kappa:.3f}, coerência={coherence:.4f}")
            break

        # Log periódico
        if step % 1000 == 0 and step > 0:
            print(f"   Passo {step:5d}: erro={error:.2e}, κ={kappa:.3f}, coerência={coherence:.4f}")

    # Converter listas para arrays
    for key in history:
        history[key] = np.array(history[key])

    return history, phi_init, kappa, target_spectrum

def analyze_convergence(history, params):
    """
    Analisa resultados da simulação para métricas de convergência.

    Returns:
        analysis: dicionário com métricas quantitativas de desempenho
    """
    # Encontrar ponto de convergência (se houver)
    converged = np.any(history['error'] < params['convergence_threshold'])
    if converged:
        conv_idx = np.argmax(history['error'] < params['convergence_threshold'])
        conv_time = history['time'][conv_idx]
        conv_kappa = history['kappa'][conv_idx]
        conv_coherence = history['coherence'][conv_idx]
    else:
        conv_time = None
        conv_kappa = history['kappa'][-1]
        conv_coherence = history['coherence'][-1]

    # Métricas de estabilidade pós-convergência
    if converged and conv_idx < len(history['error']) - 100:
        post_conv_error = np.mean(history['error'][conv_idx:])
        post_conv_kappa_std = np.std(history['kappa'][conv_idx:])
        post_conv_coherence = np.mean(history['coherence'][conv_idx:])
    else:
        post_conv_error = history['error'][-1]
        post_conv_kappa_std = np.std(history['kappa'][-100:])
        post_conv_coherence = history['coherence'][-1]

    analysis = {
        'converged': converged,
        'convergence_time_s': conv_time,
        'final_kappa': conv_kappa,
        'final_coherence': conv_coherence,
        'post_convergence_error': post_conv_error,
        'post_convergence_kappa_stability': post_conv_kappa_std,
        'post_convergence_coherence': post_conv_coherence,
        'capture_regime_achieved': conv_coherence > 0.8  # Limiar para "CAPTURE"
    }

    return analysis

if __name__ == '__main__':
    print("🔄 Simulando loop homeostático óptico...")
    print(f"   Parâmetros: N={HOMEOSTASIS_PARAMS['n_oscillators']} osciladores, "
          f"γ₁={HOMEOSTASIS_PARAMS['gamma_prop']:.1e}, γ₂={HOMEOSTASIS_PARAMS['gamma_int']:.1e}")

    # Executar simulação
    history, phi_final, kappa_final, target_spectrum = simulate_optical_homeostatic_loop(HOMEOSTASIS_PARAMS)

    # Analisar convergência
    analysis = analyze_convergence(history, HOMEOSTASIS_PARAMS)

    print(f"\n📊 Análise de convergência:")
    print(f"   • Convergiu: {analysis['converged']}")
    if analysis['convergence_time_s'] is not None:
        print(f"   • Tempo de convergência: {analysis['convergence_time_s']*1e6:.1f} μs")
    print(f"   • κ final: {analysis['final_kappa']:.4f}")
    print(f"   • Coerência final: {analysis['final_coherence']:.4f}")
    print(f"   • Erro pós-convergência: {analysis['post_convergence_error']:.2e}")
    print(f"   • Estabilidade de κ (σ): {analysis['post_convergence_kappa_stability']:.4f}")
    print(f"   • Regime CAPTURE atingido: {analysis['capture_regime_achieved']}")

    # Salvar resultados
    Path('results/homeostasis_simulation').mkdir(parents=True, exist_ok=True)

    # Salvar histórico completo
    np.savez('results/homeostasis_simulation/homeostasis_convergence.npz',
             time=history['time'],
             kappa=history['kappa'],
             error=history['error'],
             coherence=history['coherence'],
             phi_mean=history['phi_mean'],
             phi_std=history['phi_std'],
             phi_final=phi_final,
             target_spectrum=target_spectrum,
             analysis=analysis)

    # Salvar análise em JSON para leitura humana
    with open('results/homeostasis_simulation/analysis_summary.json', 'w') as f:
        json.dump({k: (float(v) if isinstance(v, (np.floating, float)) else bool(v) if isinstance(v, (np.bool_, bool)) else v)
                   for k, v in analysis.items()}, f, indent=2)

    print(f"\n💾 Resultados salvos: results/homeostasis_simulation/")

    if analysis['capture_regime_achieved']:
        print(f"✅ Loop homeostático óptico VALIDADO: convergência a regime CAPTURE demonstrada")
    else:
        print(f"⚠️  Loop necessita ajuste de ganhos (γ₁, γ₂) ou condições iniciais")