import numpy as np
import time
import json
from scripts.consciousness_ping_rtt import ConsciousnessPing

def map_rtt_stability(iterations=50):
    ping_validator = ConsciousnessPing()
    z0 = 1.0 + 0j

    rtt_history = []
    fidelity_history = []

    print(f"🜏 ARKHE(N) | RTT Stability Mapping (Node-B <-> Node-C)")
    print(f"Executing {iterations} iterations...")

    for i in range(iterations):
        # Add slight jitter to simulate environment fluctuations
        jitter = np.random.normal(0, 0.05)
        ping_validator.t_flight = (ping_validator.distance + jitter) / ping_validator.c

        results = ping_validator.perform_ping(z0)
        rtt_history.append(results["total_rtt_ps"])
        fidelity_history.append(results["phase_retention"])

        if (i+1) % 10 == 0:
            print(f"   [{i+1}/{iterations}] Mean RTT: {np.mean(rtt_history):.2f} ps | Stability: {1.0 - np.std(rtt_history)/np.mean(rtt_history):.4f}")

    analysis = {
        "mean_rtt_ps": float(np.mean(rtt_history)),
        "std_rtt_ps": float(np.std(rtt_history)),
        "min_rtt_ps": float(np.min(rtt_history)),
        "max_rtt_ps": float(np.max(rtt_history)),
        "stability_index": float(1.0 - np.std(rtt_history)/np.mean(rtt_history)),
        "mean_fidelity": float(np.mean(fidelity_history))
    }

    return analysis

if __name__ == "__main__":
    import sys
    # Add parent dir to path to find consciousness_ping_rtt if needed,
    # but it's in the same directory usually when run from scripts/
    # Actually, we should be in the root or scripts/

    # Let's just run it.
    analysis = map_rtt_stability()
    print("\n=== FINAL STABILITY REPORT ===")
    print(json.dumps(analysis, indent=2))

    with open("rtt_stability_report.json", "w") as f:
        json.dump(analysis, f, indent=2)
    print("\n✅ Stability mapping complete. Report saved to rtt_stability_report.json")
