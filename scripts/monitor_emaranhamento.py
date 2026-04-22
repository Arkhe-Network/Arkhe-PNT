import time
import os
import random
import math

def render_orb(phase):
    chars = ["-", "\\", "|", "/"]
    idx = int((phase / (2 * math.pi)) * 4) % 4
    return f"[{chars[idx]}]"

def monitor_loop():
    nodes = {
        "alpha": {"phase": 0.0, "drift": 0.01},
        "beta":  {"phase": 0.0, "drift": 0.012},
        "gamma": {"phase": 0.0, "drift": 0.009},
        "delta": {"phase": 0.5, "drift": 0.05} # Delta está com drift alto (fora de sync)
    }

    odometer = 1635
    ghz_quality = 0.85

    try:
        while True:
            # os.system('clear') # Evitar no sandbox
            print("\n" * 2)
            print(f"ARKHE-Q MESH MONITOR [ODOMETER: {odometer:06d}]")
            print(f"GHZ QUALITY: [{'|' * int(ghz_quality * 20):<20}] {ghz_quality:.2f}")
            print("-" * 42)

            # Desenha topologia
            print(f"   (α) --*-- (β)      PHASE ORBS:")
            print(f"    |         |        α: {render_orb(nodes['alpha']['phase'])}")
            print(f"    *   [δ]   *        β: {render_orb(nodes['beta']['phase'])}")
            print(f"    |  /      |        γ: {render_orb(nodes['gamma']['phase'])}")
            print(f"   (γ) -------         δ: {render_orb(nodes['delta']['phase'])} " + ("(OUT OF SYNC)" if abs(nodes['delta']['phase'] - nodes['alpha']['phase']) > 0.5 else ""))
            print("-" * 42)

            status = "COHERENT_STABLE"
            if abs(nodes['delta']['phase'] - nodes['alpha']['phase']) > 0.5:
                status = "DELTA_DRIFT_DETECTED | INJECTING_PHASE_CORRECTION"
                # Simula correção
                nodes['delta']['phase'] -= 0.05
                ghz_quality -= 0.01
            else:
                ghz_quality = min(0.99, ghz_quality + 0.005)

            print(f"STATUS: {status}")
            print(f"CLEPSYDRA: [{'.' * (odometer % 5)}O] GOTA IMINENTE")

            # Atualiza fases
            for node in nodes.values():
                node['phase'] = (node['phase'] + node['drift']) % (2 * math.pi)

            odometer += 1
            time.sleep(0.5)

            if odometer > 1640: break # Limite para simulação automatizada

    except KeyboardInterrupt:
        print("\nMonitor encerrado.")

if __name__ == "__main__":
    monitor_loop()
