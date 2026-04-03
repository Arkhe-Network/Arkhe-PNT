import random
import time
from dataclasses import dataclass

@dataclass
class HydroState:
    precipitation: int  # mm * 1000
    recharge: int       # m3/s * 10^6
    pumping: int        # m3/s * 10^6
    evapotranspiration: int # mm * 1000
    storage_current: int # Scale units
    storage_previous: int # Scale units
    quantum_coherence: int  # 0-100000 (T2* in ns)

def simulate_kalman(noise_type: str) -> int:
    """Simula o filtro Kalman do FPGA para o NV-Diamond witness"""
    baseline = 80000
    if noise_type == "classical":
        return int(max(0, min(100000, baseline + random.gauss(0, 5000))))
    elif noise_type == "quantum":
        return int(baseline * random.random() * 0.5)
    return baseline

def check_hydro_balance(state: HydroState) -> tuple:
    PRECISION = 1000
    ERROR_MARGIN = 10 # 1%

    # Range limit for geofence in simulation
    MIN_LEVEL = 1000
    MAX_LEVEL = 100000000

    # 1. Verificação Quântica
    quantum_valid = state.quantum_coherence > 50000

    # 2. Balanço de Massa
    precip_contrib = state.precipitation * 1000
    evap_contrib = state.evapotranspiration * 1000

    total_in = precip_contrib + state.recharge
    total_out = state.pumping + evap_contrib

    delta_real = state.storage_current - state.storage_previous
    delta_theory = total_in - total_out

    diff_abs = abs(delta_real - delta_theory)

    mass_valid = (diff_abs < ERROR_MARGIN * PRECISION) and quantum_valid

    # 3. Geofence & Segurança (República HYDRO-Ω: k-anonimato >= 30 lares)
    level_safe = MIN_LEVEL < state.storage_current < MAX_LEVEL
    pump_safe = state.pumping < 5000000

    # Simulação de Prova ZK de Geofence
    zk_geofence_valid = random.random() > 0.05 # 95% de chance de prova válida
    k_anonymity_satisfied = True # Presumido no simulador

    safety_valid = level_safe and pump_safe and quantum_valid and zk_geofence_valid and k_anonymity_satisfied

    diagnostics = []
    if not zk_geofence_valid:
        diagnostics.append("ZK-GEOFENCE: Falha na prova de localização (ou k-anonimato < 30)")
    if not quantum_valid:
        diagnostics.append(f"DECOERÊNCIA: T2*={state.quantum_coherence}ns (<50000ns)")
    if diff_abs >= ERROR_MARGIN * PRECISION:
        diagnostics.append(f"VIOLAÇÃO MASSA: Erro={diff_abs}")
    if not level_safe:
        diagnostics.append(f"GEOFENCE: Nível={state.storage_current} fora do range")
    if not pump_safe:
        diagnostics.append(f"EXTRAÇÃO: Taxa={state.pumping/1e6}m3/s acima do limite")

    return mass_valid, safety_valid, "; ".join(diagnostics) if diagnostics else "RESSONÂNCIA ALCANÇADA ✓"

def run_protocol_tests():
    print("="*60)
    print("   HYDRO-Ω PROTOCOL VALIDATOR: UNIFIED STACK")
    print("="*60)

    scenarios = [
        ("OPERAÇÃO NOMINAL", "classical", 15000, 5000000, 2000000, 8000, 50000, 10050000),
        ("SOBRE-EXTRAÇÃO", "classical", 15000, 5000000, 8000000, 8000, 50000, 4050000),
        ("TEMPESTADE SOLAR", "quantum", 15000, 5000000, 2000000, 8000, 50000, 10050000),
        ("MANIPULAÇÃO DADOS", "classical", 15000, 5000000, 2000000, 8000, 50000, 50000000)
    ]

    for name, noise, precip, rech, pump, evap, prev, curr in scenarios:
        coherence = simulate_kalman(noise)
        state = HydroState(
            precipitation=precip,
            recharge=rech,
            pumping=pump,
            evapotranspiration=evap,
            storage_previous=prev,
            storage_current=curr,
            quantum_coherence=coherence
        )

        mass, safety, diag = check_hydro_balance(state)
        status = "✓ VALIDADO" if (mass and safety) else "✗ REJEITADO"

        print(f"\n[CENÁRIO: {name}]")
        print(f"  > Status:    {status}")
        print(f"  > Coerência: {coherence} ns")
        print(f"  > Resultado: {diag}")
        time.sleep(0.1)

if __name__ == "__main__":
    run_protocol_tests()
