import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class HydroState:
    precipitation: int  # mm * 1000
    recharge: int       # m3/s * 10^6
    pumping: int        # m3/s * 10^6
    evapotranspiration: int  # mm * 1000
    storage_current: int     # m3 * 1000
    storage_previous: int    # m3 * 1000
    quantum_coherence: int   # 0-100000

    # Limites (públicos)
    min_level: int = 10000 * 1000  # 10m * 1000
    max_level: int = 100000 * 1000 # 100m * 1000
    max_pump: int = 5000000        # 5m3/s * 10^6
    min_coherence: int = 50000      # 50μs

def simulate_kalman_filter(noise_type: str = "classical") -> int:
    """
    Simula o filtro de Kalman do FPGA.
    - "classical": ruído gaussiano (vibração) → retorna coherência alta
    - "quantum": decoerência real → retorna queda abrupta
    - "mixed": ambos → filtro deve distinguir
    """
    baseline = 80000
    if noise_type == "classical":
        # Ruído térmico: variação alta, média constante
        return int(np.clip(baseline + np.random.normal(0, 5000), 0, 100000))
    elif noise_type == "quantum":
        # Decoerência: queda exponencial significativa (abaixo do limiar de 50000)
        return int(np.random.randint(0, 45000))
    else:
        return baseline

def check_hydro_balance(state: HydroState) -> Tuple[bool, bool, str]:
    """
    Replica a lógica do circuito Circom.
    Retorna: (mass_balance_valid, safety_compliant, diagnostic)
    """
    PRECISION = 1000
    ERROR_MARGIN = 10

    # 1. Verificação Quântica
    quantum_valid = state.quantum_coherence > state.min_coherence

    # 2. Balanço de Massa
    # Let's simplify and make the simulator match the intended physics balance:
    # Precip (mm) * Area = Volume.
    # If we assume Area=1 (normalized), then precip (mm) is directly comparable to depth change.
    # If storage is in m3, and Area is 1m2, then 1mm = 0.001 m3.
    # If precipitation input is mm*1000, then 1000 units = 1mm = 0.001 m3.

    # In Circom:
    # signal precipContrib <== precipitation * 1000; (where precipitation is mm*1000)
    # precipContrib = 10^6
    # recharge = m3/s * 10^6
    # So both are effectively in units of 10^-6 m3 (assuming 1s period and 1m2 area)

    # All state values are already scaled:
    # precipitation: mm * 1000
    # recharge: m3/s * 10^6
    # pumping: m3/s * 10^6
    # evapotranspiration: mm * 1000
    # storage: m3 * 1000

    # In Circom: signal precipContrib <== precipitation * 1000;
    # If precipitation is 50,000 (50mm), precipContrib is 50,000,000 (50e6).
    precip_contrib = state.precipitation * 1000
    evap_contrib = state.evapotranspiration * 1000

    # totalInputs = 50e6 + 5e6 = 55e6
    total_inputs = precip_contrib + state.recharge
    total_outputs = state.pumping + evap_contrib

    # theoreticalDelta = 55e6 - 10e6 = 45e6
    theoretical_delta = total_inputs - total_outputs

    # currentStorage = 95,000 (95m3). previousStorage = 50,000 (50m3).
    # deltaStorage = 45,000,000.
    delta_storage = state.storage_current - state.storage_previous

    # In my scenarios: storage_current is 95000*1000 = 95e6.
    # storage_previous is 50000*1000 = 50e6.
    # So delta_storage is 45e6.
    # theoretical_delta is (50e3 * 1000 + 5e6) - (2e6 + 8e3 * 1000) = 45e6.

    diff_abs = abs(delta_storage - theoretical_delta)
    mass_valid = (diff_abs < ERROR_MARGIN * PRECISION) and quantum_valid

    # 3. Limites Operacionais
    level_safe = (state.storage_current > state.min_level and
                  state.storage_current < state.max_level)
    pump_safe = state.pumping < state.max_pump
    evap_safe = state.evapotranspiration > 0

    safety_valid = level_safe and pump_safe and evap_safe and quantum_valid

    # Diagnóstico
    issues = []
    if not quantum_valid:
        issues.append("Decoerência quântica detectada (possível interferência)")
    if diff_abs >= ERROR_MARGIN * PRECISION:
        issues.append(f"Erro de conservação: {diff_abs} (limite: {ERROR_MARGIN*PRECISION})")
    if not level_safe:
        issues.append("Nível fora dos limites operacionais (Geofence)")
    if not pump_safe:
        issues.append("Over-extraction detectada")

    return mass_valid, safety_valid, "; ".join(issues) if issues else "OK"

if __name__ == "__main__":
    # Simulação de cenários
    # precipitação: mm*1000
    # recharge: m3/s * 10^6
    # pumping: m3/s * 10^6
    # evap: mm * 1000
    # prev/curr storage: m3 * 1000
    scenarios = [
        # Normal:
        # precipitation: 50 * 1000 (mm*1000) => precip_contrib = 50e6
        # recharge: 5 * 10^6 (m3/s * 10^6)
        # pumping: 2 * 10^6
        # evap: 8 * 1000 => evap_contrib = 8e6
        # theoreticalDelta = (50e6 + 5e6) - (2e6 + 8e6) = 55e6 - 10e6 = 45e6
        # deltaStorage_scaled = delta * 1000 = 45e6 => delta = 45000
        # storage_current = storage_previous + delta = 50000 + 45000 = 95000
        ("Operação Normal", "classical", 50*1000, 5*1000000, 2*1000000, 8*1000, 50000*1000, 95000*1000),
        ("Over-pumping", "classical", 20*1000, 2*1000000, 8*1000000, 15*1000, 50000*1000, 49000*1000),  # Bombeamento excessivo
        ("Tempestade Solar", "quantum", 50*1000, 5*1000000, 2*1000000, 8*1000, 50000*1000, 95000*1000),  # Decoerência QD
        ("Vazamento não detectado", "classical", 50*1000, 5*1000000, 2*1000000, 8*1000, 50000*1000, 48000*1000),  # Erro de massa
    ]

    print("=== Simulador HYDRO-Ω ZK ===\n")
    for name, noise, precip, recharge, pump, evap, prev, curr in scenarios:
        coherence = simulate_kalman_filter(noise)
        state = HydroState(
            precipitation=precip,
            recharge=recharge,
            pumping=pump,
            evapotranspiration=evap,
            storage_previous=prev,
            storage_current=curr,
            quantum_coherence=coherence
        )

        mass_ok, safety_ok, diag = check_hydro_balance(state)
        status = "✓ APROVADO" if (mass_ok and safety_ok) else "✗ REJEITADO"

        print(f"Cenário: {name}")
        print(f"  Coerência QD: {coherence}μs ({'OK' if coherence > 50000 else 'FALHA'})")
        print(f"  Balanço: {'OK' if mass_ok else 'FALHA'} | Segurança: {'OK' if safety_ok else 'FALHA'}")
        print(f"  Diagnóstico: {diag}")
        print(f"  Status ZK: {status}\n")
