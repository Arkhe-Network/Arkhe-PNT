import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import json

# --- Configurações do Canal qhttp ---
# Inhomogeneidade magnética residual: 4 ppm
# Ruído térmico: AWGN modelado por SNR
# Taxa de repetição: f_rep (Hz)

def model_qhttp_ber(signal_power_dbm, f_rep_mhz, inhomogeneity_ppm=4.0, t_env_k=300.0):
    """
    Modela o canal qhttp e calcula a BER.
    signal_power_dbm: Potência do sinal (dBm)
    f_rep_mhz: Taxa de repetição (MHz)
    inhomogeneity_ppm: Inhomogeneidade magnética (ppm)
    """
    # Conversão de dBm para Watts
    p_signal = 10**((signal_power_dbm - 30) / 10)

    # Ruído Térmico (AWGN)
    # N = k * T * B. Assumindo largura de banda B proporcional a f_rep
    k_b = 1.38e-23
    bandwidth = f_rep_mhz * 1e6
    p_noise_thermal = k_b * t_env_k * bandwidth

    # Inhomogeneidade Magnética (Dephasing)
    # Provoca uma redução na amplitude efetiva do sinal (coerência)
    # Fator de dephasing proporcional à inhomogeneity_ppm
    # SNR_eff = P_signal * exp(- (gamma * deltaB * t)^2 ) / P_noise
    # Para simplificar, tratamos como uma penalidade na SNR
    dephasing_penalty = np.exp(-(inhomogeneity_ppm * 1e-6 * 5.0)**2) # 5.0 é um fator de escala empírico

    snr_linear = (p_signal * dephasing_penalty) / p_noise_thermal

    # BER para BPSK (ou similar quântico-clássico)
    ber = 0.5 * erfc(np.sqrt(snr_linear))
    return ber

def generate_analysis():
    powers = np.linspace(-60, -20, 20) # dBm
    rates = [1, 10, 50, 100] # MHz

    results = {}

    plt.figure(figsize=(10, 6))
    for r in rates:
        bers = [model_qhttp_ber(p, r) for p in powers]
        results[f"{r}MHz"] = bers
        plt.semilogy(powers, bers, label=f'Rep. Rate: {r} MHz')

    plt.title('Análise de Desempenho do Canal qhttp (4 ppm Inhomogeneity)')
    plt.xlabel('Signal Power (dBm)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend()
    plt.axhline(y=1e-3, color='r', linestyle='--', label='FEC Threshold')
    plt.savefig('qhttp_ber_curves.png')

    # --- Detalhes do Filtro de Kalman da Cúpula ---
    # O filtro estima a fase phi e a deriva de frequência omega
    # Matriz de Estado: x = [phi, omega]^T
    # Matriz de Transição A = [[1, dt], [0, 1]]
    dt = 1e-8 # 10ns (100MHz)

    # Covariância do Processo Q (Ruído de fase e instabilidade do clock)
    # Q = [[sigma_phi^2, 0], [0, sigma_omega^2]]
    # Valores otimizados para 4 ppm de instabilidade magnética
    q_matrix = [
        [1.0e-10, 0.0],
        [0.0, 4.0e-12]
    ]

    # Covariância da Medição R (Ruído térmico e shot noise do detector)
    r_value = 1.5e-3 # Radianos^2

    # Matriz de Covariância Inicial P
    p_matrix = [
        [1.0, 0.0],
        [0.0, 1.0]
    ]

    kalman_details = {
        "Q": q_matrix,
        "R": r_value,
        "P_init": p_matrix,
        "dt": dt,
        "notes": "Parâmetros otimizados para mitigação de drift magnético de 4ppm."
    }

    with open('kalman_dome_config.json', 'w') as f:
        json.dump(kalman_details, f, indent=4)

    print("Análise concluída. Curvas salvas em qhttp_ber_curves.png")
    print("Configuração do Filtro de Kalman salva em kalman_dome_config.json")

    # --- Melt-Protocol Specification ---
    melt_protocol = """
    # MELT-PROTOCOL (Protocolo de Fusão de Segurança)

    ## Gatilhos de Ativação:
    1. BER > 10^-2 persistentemente por 1000 ciclos.
    2. Instabilidade de Fase (Kalman Innovation) > 0.5 rad.
    3. Drift de Frequência > 10 ppm (Inhomogeneidade Magnética Residual excedida).

    ## Procedimento:
    1. **SHUTDOWN_PHASE**: Desativar drivers de fase v_phi imediatamente.
    2. **THERMAL_DUMP**: Ativar dissipadores Graphene-TPU em potência máxima.
    3. **ENTROPY_INJECTION**: Injetar ruído branco no canal qhttp para evitar entalpia de informação.
    4. **HARD_RESET**: Reinicializar o controlador v_phi_controller após 500ms de estabilização térmica.
    """

    with open('MELT_PROTOCOL.md', 'w') as f:
        f.write(melt_protocol)
    print("Melt-Protocol especificado em MELT_PROTOCOL.md")

if __name__ == "__main__":
    generate_analysis()
