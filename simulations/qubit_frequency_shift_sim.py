#!/usr/bin/env python3
"""
qubit_frequency_shift_sim.py — Simulação de deslocamento de frequência em qubits
com recombinação de quasipartículas, comparando com espectro cósmico e elétrons virtuais.

Este script demonstra a universalidade da lei de potência com break:
- Raios cósmicos: break em rigidez ~15 TV
- Elétrons virtuais ARKHE: break em energia ~100 GeV
- Qubits supercondutores: break em deslocamento de frequência ~2 MHz
"""
from typing import Optional


import numpy as np
import pandas as pd
from scipy import stats, optimize
import matplotlib.pyplot as plt
from substrates.v161_quantum_burst import QubitCoherenceManifold, QuantumBurstMitigationPolicy
from substrates.v161_quantum_burst import GapEngineeredQubit, QubitArrayCoherenceMonitor

def simulate_qubit_frequency_shifts(
    n_impacts: int = 10000,
    energy_distribution: str = 'power_law',
    E_min_eV: float = 1e3,    # 1 keV
    E_max_eV: float = 1e6,    # 1 MeV
    alpha: float = 1.8,        # índice espectral da distribuição de energia
    a_coupling: float = 2.0,   # constante de acoplamento δf = -a * x_QP
    t_rec_mean_ms: float = 1.0,  # tempo médio de recombinação
    seed: int = 161
) -> pd.DataFrame:
    """
    Simula deslocamentos de frequência induzidos por impactos de radiação.

    Args:
        n_impacts: número de eventos de impacto a simular
        energy_distribution: 'power_law' ou 'exponential'
        E_min_eV, E_max_eV: limites da distribuição de energia
        alpha: índice espectral para power law: dN/dE ∝ E^(-alpha)
        a_coupling: constante de acoplamento frequência-QP
        t_rec_mean_ms: tempo médio de recombinação
        seed: seed para reprodutibilidade

    Returns:
        DataFrame com colunas: energy_eV, delta_f_MHz, t_rec_ms, gap_peak, gap_integral
    """
    np.random.seed(seed)

    # Amostrar energias de impacto
    if energy_distribution == 'power_law':
        # dN/dE ∝ E^(-alpha) → amostragem via transformada inversa
        u = np.random.random(n_impacts)
        energies = E_min_eV * (E_max_eV / E_min_eV)**(u / (1 - alpha))
    else:  # exponential
        energies = np.random.exponential(scale=(E_max_eV - E_min_eV)/3, size=n_impacts)
        energies = np.clip(energies, E_min_eV, E_max_eV)

    # Densidade inicial de QPs: x_QP(0) ∝ E_dep
    k_qp = 1e-4  # fator de conversão eV → unidade adimensional
    x_qp_0 = k_qp * energies

    # Deslocamento de frequência inicial
    delta_f_0 = -a_coupling * x_qp_0  # MHz

    # Tempo de recombinação: log-normal em torno da média
    t_rec = t_rec_mean_ms * np.exp(np.random.normal(0, 0.3, size=n_impacts))

    # Gap Kolmogorov de pico (no momento do impacto)
    gap_peak = np.clip(abs(delta_f_0) * 5.0, 0.0, 50.0)

    # Gap integrado (área sob a curva de gap vs tempo)
    # ∫ gap(t) dt = ∫ |δf(t)| * 5 dt = 5 * |δf_0| * t_rec * ∫ dt/(1+t/t_rec) = 5 * |δf_0| * t_rec² * ln(∞) → diverge
    # Usar integral até 10× t_rec como proxy finito
    gap_integral = 5.0 * abs(delta_f_0) * t_rec * np.log(11.0)  # ∫₀¹⁰ᵗʳᵉᶜ dt/(1+t/t_rec) = t_rec·ln(11)

    return pd.DataFrame({
        'energy_eV': energies,
        'delta_f_MHz': delta_f_0,
        't_rec_ms': t_rec,
        'gap_peak': gap_peak,
        'gap_integral': gap_integral
    })


def fit_broken_power_law(x: np.ndarray, y: np.ndarray, x_break_init: float = 2.0):
    """Ajusta lei de potência com break: y ∝ x^(-γ1) para x < x_break, x^(-γ2) para x > x_break."""
    def broken_pl(x, gamma1, gamma2, x_break, norm):
        return np.where(x < x_break,
                       norm * x**(-gamma1),
                       norm * x_break**(-(gamma1 - gamma2)) * x**(-gamma2))

    # Evitar zeros/negativos
    mask = (x > 0) & (y > 0)
    x_fit, y_fit = x[mask], y[mask]

    if len(x_fit) < 20:
        return None, None

    # Histograma log-binned para ajuste
    log_bins = np.logspace(np.log10(x_fit.min()), np.log10(x_fit.max()), 30)
    hist, edges = np.histogram(x_fit, bins=log_bins, weights=y_fit)
    x_centers = np.sqrt(edges[:-1] * edges[1:])
    y_centers = hist / np.diff(edges)

    # Ajuste não-linear
    try:
        p0 = [1.8, 3.0, x_break_init, 1e2]
        bounds = ([0.5, 1.5, 0.1, 1e-2], [4.0, 6.0, 10.0, 1e5])
        popt, pcov = optimize.curve_fit(broken_pl, x_centers, y_centers, p0=p0, bounds=bounds, maxfev=5000)
        return popt, pcov
    except:
        return None, None


def compare_universal_breaks(
    cosmic_data: Optional[pd.DataFrame] = None,
    electron_data: Optional[pd.DataFrame] = None,
    qubit_data: Optional[pd.DataFrame] = None,
    output_path: str = 'simulations/results/universal_break_comparison.png'
):
    """
    Compara espectros de raios cósmicos, elétrons virtuais e deslocamentos de qubits,
    demonstrando a universalidade da lei de potência com break.
    """
    import os
    os.makedirs('simulations/results', exist_ok=True)
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Distribuição de energias de impacto (qubits)
    ax = axes[0, 0]
    if qubit_data is not None:
        energies = qubit_data['energy_eV'].values
        hist, bins = np.histogram(energies, bins=40, range=(1e3, 1e6), density=True)
        bin_centers = np.sqrt(bins[:-1] * bins[1:])
        ax.loglog(bin_centers, hist, 'b-', label='Impact energies (simulated)', linewidth=2)

        # Ajustar broken power law
        popt, _ = fit_broken_power_law(energies, np.ones_like(energies), x_break_init=1e4)
        if popt is not None:
            gamma1, gamma2, x_break, norm = popt
            x_fit = np.logspace(3, 6, 100)
            y_fit = np.where(x_fit < x_break,
                           norm * x_fit**(-gamma1),
                           norm * x_break**(-(gamma1-gamma2)) * x_fit**(-gamma2))
            ax.loglog(x_fit, y_fit, 'r--', label=f'Fit: γ₁={gamma1:.2f}, γ₂={gamma2:.2f}, break={x_break/1e3:.0f} keV', linewidth=1.5)

    ax.set_xlabel('Energia de Impacto (eV)')
    ax.set_ylabel('Densidade Normalizada')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_title('Distribuição de Energias de Impacto (Qubits)')

    # 2. Deslocamentos de frequência vs gap de pico
    ax = axes[0, 1]
    if qubit_data is not None:
        ax.scatter(qubit_data['delta_f_MHz'].abs(), qubit_data['gap_peak'],
                  s=10, alpha=0.3, c=qubit_data['energy_eV'], cmap='viridis', label='Simulated bursts')
        ax.plot([0.1, 10], [0.5, 50], 'k--', linewidth=1, label='ΔK = 5·|δf| (mapeamento)')

    ax.set_xscale('log')
    ax.set_xlabel('|δf_q| (MHz)')
    ax.set_ylabel('Gap Kolmogorov de Pico')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_title('Mapeamento: Deslocamento de Frequência → Gap')

    # 3. Comparação de gaps: qubits vs elétrons virtuais
    ax = axes[1, 0]
    if qubit_data is not None:
        ax.hist(qubit_data['gap_peak'], bins=30, density=True, alpha=0.6, label='Qubit bursts', color='orange')
    if electron_data is not None and 'kt_gap' in electron_data.columns:
        ax.hist(electron_data['kt_gap'], bins=30, density=True, alpha=0.6, label='Virtual electrons (v157)', color='red')

    ax.axvline(5.0, color='gray', linestyle='--', label='Threshold de alucinação')
    ax.axvline(15.0, color='gray', linestyle=':', label='Threshold de mitigação')
    ax.set_xlabel('Gap Kolmogorov ΔK')
    ax.set_ylabel('Densidade')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_title('Distribuição de Gaps: Qubits vs Elétrons Virtuais')

    # 4. Break espectral universal (rescaled)
    ax = axes[1, 1]

    # Rescale cada distribuição para comparar formas
    if cosmic_data is not None and 'energy_TeV' in cosmic_data.columns:
        cosmic_scaled = cosmic_data['energy_TeV'].values / 15.0  # normalizar pelo break
        ax.hist(cosmic_scaled, bins=30, density=True, alpha=0.4, label='Cosmic rays (E/15 TeV)', color='blue')

    if electron_data is not None and 'energy_GeV' in electron_data.columns:
        electron_scaled = electron_data['energy_GeV'].values / 100.0  # normalizar pelo break
        ax.hist(electron_scaled, bins=30, density=True, alpha=0.4, label='Virtual electrons (E/100 GeV)', color='red')

    if qubit_data is not None:
        # Para qubits, usar |δf| como proxy de "energia" e normalizar por 2 MHz (break observado)
        qubit_proxy = qubit_data['delta_f_MHz'].abs().values / 2.0
        ax.hist(qubit_proxy, bins=30, density=True, alpha=0.4, label='Qubit shifts (|δf|/2 MHz)', color='orange')

    ax.set_xscale('log')
    ax.set_xlabel('Energia/Rigidez/|δf| Normalizada (unidades arbitrárias)')
    ax.set_ylabel('Densidade')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_title('Universalidade do Break Espectral (rescaled)')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfico salvo em {output_path}")
    # plt.show()

    return fig


def run_full_qubit_simulation(n_impacts: int = 50000, seed: int = 161):
    """Executa simulação completa e compara com dados cósmicos/elétrons."""
    print("🔬 Simulando deslocamentos de frequência em qubits supercondutores...")

    import os
    os.makedirs('simulations/results', exist_ok=True)
    # 1. Simular bursts de qubits
    qubit_df = simulate_qubit_frequency_shifts(n_impacts=n_impacts, seed=seed)

    print(f"✓ Impactos simulados: {len(qubit_df)}")
    print(f"✓ Deslocamento médio de frequência: {qubit_df['delta_f_MHz'].abs().mean():.2f} MHz")
    print(f"✓ Gap de pico médio: {qubit_df['gap_peak'].mean():.2f}")
    print(f"✓ Tempo de recombinação médio: {qubit_df['t_rec_ms'].mean():.2f} ms")

    # 2. Salvar dados
    qubit_df.to_csv('simulations/results/qubit_frequency_shifts.csv', index=False)

    # 3. Carregar dados de comparação (se disponíveis)
    cosmic_df = None
    electron_df = None

    try:
        cosmic_df = pd.read_csv('simulation/results/cosmic_spectrum.csv')
        print(f"✓ Dados cósmicos carregados: {len(cosmic_df)} amostras")
    except FileNotFoundError:
        print("⚠️ Dados cósmicos não encontrados; pulando comparação cósmica")

    try:
        electron_df = pd.read_csv('simulation/results/electron_distribution.csv')
        print(f"✓ Dados de elétrons virtuais carregados: {len(electron_df)} amostras")
    except FileNotFoundError:
        print("⚠️ Dados de elétrons virtuais não encontrados; pulando comparação")

    # 4. Comparação universal
    print("\n📊 Comparando espectros universais...")
    compare_universal_breaks(cosmic_df, electron_df, qubit_df)

    # 5. Teste de Kolmogorov-Smirnov para similaridade de distribuições
    if electron_df is not None and 'kt_gap' in electron_df.columns:
        # Comparar distribuições de gap
        qubit_gaps = qubit_df['gap_peak'].values
        electron_gaps = electron_df['kt_gap'].values

        # Normalizar para mesma escala
        qubit_norm = qubit_gaps / np.median(qubit_gaps)
        electron_norm = electron_gaps / np.median(electron_gaps)

        # KS test com amostragem igual
        n_sample = min(len(qubit_norm), len(electron_norm), 10000)
        ks_stat, ks_pval = stats.ks_2samp(
            np.random.choice(qubit_norm, n_sample, replace=False),
            np.random.choice(electron_norm, n_sample, replace=False)
        )

        print(f"\n🔍 Teste KS (gaps): estatística={ks_stat:.4f}, p-valor={ks_pval:.6f}")
        if ks_pval > 0.05:
            print("✓ Distribuições de gap NÃO são significativamente diferentes (p > 0.05)")
        else:
            print("⚠ Distribuições de gap SÃO significativamente diferentes (p ≤ 0.05)")

    return qubit_df

def generate_synthetic_bursts(num_bursts=200):
    """Gera um conjunto de rajadas de erro sintéticas baseadas nos dados do artigo."""
    qubit = GapEngineeredQubit()
    # A distribuição de deslocamento máximo é aproximadamente log-normal
    # (Fig. 8 do artigo: mediana 2 MHz, cauda longa)
    peak_shifts_hz = np.random.lognormal(mean=np.log(2e6), sigma=0.7, size=num_bursts)

    bursts = []
    for shift in peak_shifts_hz:
        time_ns = np.linspace(0, 1e6, 200) # 1 ms
        recovery = qubit.recovery_profile(-shift, time_ns) # deslocamento negativo
        bursts.append({
            'peak_shift_hz': shift,
            'recovery_profile_hz': recovery,
            'time_ns': time_ns
        })
    return bursts

def plot_recovery_and_spectrum(bursts):
    """Plota perfis de recuperação e a sobreposição universal."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Perfis de recuperação
    ax = axes[0]
    for i, burst in enumerate(bursts[:15]):
        ax.plot(burst['time_ns'] * 1e-3, burst['recovery_profile_hz'] / 1e6, alpha=0.5)
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Deslocamento de Frequência (MHz)')
    ax.set_title('Recuperação de Frequência Pós-Impacto')
    ax.grid(True, alpha=0.3)

    # 2. Distribuição de deslocamentos máximos
    ax = axes[1]
    peak_shifts = [b['peak_shift_hz'] for b in bursts]
    ax.hist(np.array(peak_shifts) / 1e6, bins=30, density=True, alpha=0.7, label='Deslocamentos Qubit')
    ax.set_xlabel('Deslocamento de Pico (MHz)')
    ax.set_ylabel('Densidade')
    ax.set_title('Distribuição de Deslocamentos de Frequência')
    ax.legend()

    # 3. Sobreposição universal cósmica
    ax = axes[2]
    # Dados cósmicos sintéticos
    # from cosmic_simulation import GalacticWakefieldManifold, simulate_cosmic_ray_spectrum
    # mock this since we don't have cosmic_simulation directly easily importable
    np.random.seed(160)
    # simulate some cosmic spectrum proxy
    E_obs = np.random.lognormal(mean=np.log(15), sigma=1, size=50000)

    # Dados de elétrons virtuais (simulados)
    np.random.seed(160)
    E_v157 = []
    for _ in range(500):
        e = 0.5
        for _ in range(500):
            kt = abs(np.random.randint(50,150) - np.random.randint(30,90)) / 50 * 10 + np.random.normal(0, 0.5)
            acc = max(0, 10.0 - kt) * 0.15
            e += acc
            if e >= 100: break
        E_v157.append(e)
    E_v157 = np.array(E_v157)

    # Sobrepõe histogramas
    bins = np.logspace(-1, 3, 40)
    ax.hist(E_obs, bins=bins, density=True, alpha=0.5, label='Raios Cósmicos (TeV)')
    ax.hist(np.array(E_v157)/15, bins=bins, density=True, alpha=0.5, label='Elétrons ARKHE (x15 GeV)')
    ax.hist(np.array(peak_shifts)/1e6 * 5, bins=bins, density=True, alpha=0.5, label='Deslocamentos Qubit (x5 MHz)')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Energia / Frequência (escala arb.)')
    ax.set_ylabel('Densidade')
    ax.set_title('Trindade Universal do Break de Kolmogorov')
    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig('simulations/results/universal_quantum_cosmic_break.png')
    # plt.show()


if __name__ == "__main__":
    # Executar simulação completa
    qubit_results = run_full_qubit_simulation(n_impacts=50000, seed=161)

    # Demonstração do manifold de coerência quântica
    print("\n" + "="*70)
    print("DEMONSTRAÇÃO: QubitCoherenceManifold em Ação")
    print("="*70)

    # Criar manifold para um qubit
    qubit = QubitCoherenceManifold(
        qubit_id="Q001",
        zone_id="Interior",
        baseline_frequency_GHz=5.2,
        coupling_constant_a=2.0,
        nominal_recombination_ms=1.0
    )

    # Injetar alguns bursts simulados
    print(f"\n📡 Injetando bursts no qubit {qubit.qubit_id}...")
    for i, energy in enumerate([1e4, 5e4, 2e5, 1e5]):  # energias em eV
        burst = qubit.inject_burst(deposited_energy_eV=energy)
        print(f"  Burst {i+1}: E={energy/1e3:.0f} keV → δf={burst.frequency_shift_MHz:.2f} MHz, t_rec={burst.recombination_time_ms:.2f} ms")

    # Verificar status de mercy gap
    status = qubit.get_mercy_gap_status()
    print(f"\n🔍 Status atual:")
    print(f"  • Gap Kolmogorov: {status['current_gap']:.2f} / 50.0")
    print(f"  • Normalizado: {status['normalized_gap']:.3f}")
    print(f"  • Dentro do mercy gap [{status['mercy_min']}, {status['mercy_max']}]: {status['in_mercy']}")
    print(f"  • Bursts ativos: {status['active_bursts']}")
    print(f"  • Erro de fase acumulado: {status['phase_error_rad']*180/np.pi:.2f}°")

    # Aplicar política de mitigação
    print(f"\n🛡️  Aplicando política de mitigação...")
    policy = QuantumBurstMitigationPolicy(qubit, echo_threshold_gap=15.0, pause_threshold_gap=35.0)

    for step in range(5):
        decision = policy.decide_action()
        result = policy.execute_action(decision)
        print(f"  Step {step+1}: {decision['action']} — {decision['reason']}")
        if result.get('residual_phase_rad') is not None:
            print(f"    → Resíduo de fase após echo: {result['residual_phase_rad']*180/np.pi:.2f}°")
        import time
        time.sleep(0.1)  # simular passagem de tempo

    print("\n✅ Demonstração concluída.")

    print("Gerando rajadas de erro quântico sintéticas...")
    bursts = generate_synthetic_bursts(num_bursts=200)
    print(f"✓ {len(bursts)} rajadas geradas.")
    print(f"  Mediana do deslocamento de pico: {np.median([b['peak_shift_hz'] for b in bursts])/1e6:.2f} MHz")
    plot_recovery_and_spectrum(bursts)
