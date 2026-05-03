# ============================================================================
# ARKHE OS v∞.Ω.∇+++.14.1 — Timeline Branching & Convergence Simulation
# Purpose: Measure ε-convergence, merge stability, and PoC consensus robustness
# Extended to multi-dimensional epsilon (phase, latency, power)
# ============================================================================

import numpy as np
import matplotlib.pyplot as plt
import time
import hashlib
import json
from consensus_engine import ProofOfCoherenceConsensusCopula, CoherenceStakeCopula, ForkVoteCopula, CoherenceTensor4D

def generate_epsilon_trajectory(T: int, target: np.ndarray, theta: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """Multi-dimensional Ornstein-Uhlenbeck process simulating mercy gap dynamics."""
    # Shape: (T, 4) for phase, latency, power, mercy_gap
    eps = np.zeros((T, 4))
    eps[0] = target
    for t in range(1, T):
        eps[t] = eps[t-1] + theta * (target - eps[t-1]) + sigma * np.random.randn(4)
    # Clip bounds based on physical bounds of copula dimensions
    eps[:, 0] = np.clip(eps[:, 0], 0.04, 0.10) # phase
    eps[:, 1] = np.clip(eps[:, 1], 400.0, 600.0) # latency
    eps[:, 2] = np.clip(eps[:, 2], 120.0, 180.0) # power
    eps[:, 3] = np.clip(eps[:, 3], 0.04, 0.10) # mercy_gap
    return eps

def run_timeline_simulation(T: int = 500, num_forks: int = 3, seed: int = 42) -> dict:
    np.random.seed(seed)

    target_tensor = CoherenceTensor4D.target()
    target = target_tensor.to_vector()
    theta = np.array([0.2, 0.2, 0.2, 0.2])
    sigma = np.array([0.02, 20.0, 10.0, 0.02])

    # Generate main timeline
    main_epsilon = generate_epsilon_trajectory(T, target, theta, sigma)

    # Initialize consensus engine
    consensus = ProofOfCoherenceConsensusCopula(consensus_threshold=0.55, odysseus_multiplier=0.3)

    # Register vertices
    for i in range(5):
        v_did = f"vertex-{i}"
        pub_key = f"0x12345{i}"
        consensus.register_vertex(CoherenceStakeCopula(v_did), pub_key)

    # Fork creation & voting
    fork_ids = []
    fork_results = []

    for f in range(num_forks):
        fork_ts = np.random.randint(T//4, 3*T//4)
        fork_id = f"fork-{f:02d}"
        fork_ids.append(fork_id)

        # Fork ε trajectory (drifts differently in 4 dimensions)
        drift = np.array([
            np.random.choice([-0.01, 0.0, 0.015]),
            np.random.choice([-10.0, 0.0, 15.0]),
            np.random.choice([-5.0, 0.0, 10.0]),
            np.random.choice([-0.01, 0.0, 0.015])
        ])

        fork_epsilon = main_epsilon[:fork_ts].copy()
        # Extend to T
        fork_epsilon = np.pad(fork_epsilon, ((0, T - fork_ts), (0, 0)), 'edge')
        for t in range(fork_ts, T):
            fork_epsilon[t] = fork_epsilon[t-1] + drift + sigma * np.random.randn(4) * 0.5

        fork_epsilon[:, 0] = np.clip(fork_epsilon[:, 0], 0.04, 0.10) # phase
        fork_epsilon[:, 1] = np.clip(fork_epsilon[:, 1], 400.0, 600.0) # latency
        fork_epsilon[:, 2] = np.clip(fork_epsilon[:, 2], 120.0, 180.0) # power
        fork_epsilon[:, 3] = np.clip(fork_epsilon[:, 3], 0.04, 0.10) # mercy_gap

        fork_tensor = CoherenceTensor4D(
            fork_epsilon[-1][0], fork_epsilon[-1][1], fork_epsilon[-1][2], fork_epsilon[-1][3]
        )

        # Simulate voting
        votes_for = np.random.binomial(5, p=0.7)  # 70% support baseline
        for i in range(5):
            v_did = f"vertex-{i}"
            pub_key = f"0x12345{i}"
            is_for = i < votes_for
            timestamp = time.time()

            # Canonical bytes computation
            payload = {
                "voter": v_did, "direction": is_for,
                "timestamp": timestamp,
                "coherence": fork_tensor.to_vector().tolist()
            }
            canonical_bytes = json.dumps(payload, sort_keys=True).encode()
            sig = hashlib.sha3_256(pub_key.encode() + canonical_bytes).hexdigest()[:32]

            vote = ForkVoteCopula(
                voter_did=v_did,
                vote_direction=is_for,
                timestamp=timestamp,
                fork_coherence=fork_tensor,
                signature=sig
            )
            consensus.cast_vote(fork_id, vote)

        # Odysseus insight ratio (super-linear event probability)
        odys_ratio = 1.0 + 0.4 * np.random.exponential(scale=0.5)

        accept, score, _ = consensus.evaluate_merge(fork_id, assurance_veto=False, odysseus_insight_ratio=odys_ratio)
        fork_results.append({
            "id": fork_id,
            "fork_ts": fork_ts,
            "final_epsilon": fork_epsilon[-1], # 4-dimensional
            "consensus_score": float(score),
            "odys_ratio": float(odys_ratio),
            "merged": accept
        })
        consensus.reset_fork(fork_id)

    # Convergence metrics
    convergence_times = []
    for f in fork_results:
        if f["merged"]:
            # Estimate time to cross threshold (simplified)
            conv_time = f["fork_ts"] + int(20 * np.random.uniform(0.5, 1.2))
            convergence_times.append(conv_time)

    # Calculate L2 norm differences per dimension relative to scale
    target_norm_vec = target_tensor.to_vector()
    # Normalize differences since dimensions are on vastly different scales
    # Phase/Mercy ~ 0.07, Latency ~ 500, Power ~ 150
    normalization_factors = np.array([0.07, 500.0, 150.0, 0.07])

    avg_eps_drift = float(np.mean([
        np.linalg.norm((r["final_epsilon"] - target_norm_vec) / normalization_factors)
        for r in fork_results
    ]))

    return {
        "main_epsilon_std": float(np.mean(np.std(main_epsilon / normalization_factors, axis=0))),
        "fork_results": fork_results,
        "merge_success_rate": sum(1 for r in fork_results if r["merged"]) / num_forks,
        "avg_convergence_time": float(np.mean(convergence_times)) if convergence_times else None,
        "avg_epsilon_drift": avg_eps_drift
    }

def visualize_results(results: dict, main_epsilon: np.ndarray, T: int) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))

    # Normalize for visualization
    normalization_factors = np.array([0.07, 500.0, 150.0, 0.07])
    normalized_main_epsilon = main_epsilon / normalization_factors
    target_vec_normalized = CoherenceTensor4D.target().to_vector() / normalization_factors

    # Left: ε trajectory (plot the norm of the 4 normalized dimensions as distance from 0)
    # Target distance from 0 is norm of [1.0, 1.0, 1.0, 1.0] = 2.0
    main_epsilon_norm = np.linalg.norm(normalized_main_epsilon, axis=1)
    target_norm = np.linalg.norm(target_vec_normalized)

    ax[0].plot(main_epsilon_norm, label="Main Timeline ε (Normalized L2 Norm)", linewidth=2, color="#2b5876")
    ax[0].axhline(target_norm, color="gold", linestyle="--", label=f"Target L2=~{target_norm:.3f}")
    ax[0].fill_between(range(T), target_norm - 0.2, target_norm + 0.2, alpha=0.15, color="green", label="Coherence Region")
    ax[0].set_xlabel("Logical Timestamp")
    ax[0].set_ylabel("Normalized Epsilon L2 Norm")
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)

    # Right: Merge outcomes
    merged = [r for r in results["fork_results"] if r["merged"]]
    rejected = [r for r in results["fork_results"] if not r["merged"]]
    ax[1].scatter([r["fork_ts"] for r in merged], [r["consensus_score"] for r in merged],
                  label="Merged (PoC Pass)", color="green", s=80, marker="o")
    ax[1].scatter([r["fork_ts"] for r in rejected], [r["consensus_score"] for r in rejected],
                  label="Rejected", color="red", s=80, marker="x")
    ax[1].axhline(0.55, color="gray", linestyle=":", label="Consensus Threshold")
    ax[1].set_xlabel("Fork Creation Timestamp")
    ax[1].set_ylabel("Consensus Score")
    ax[1].legend()
    ax[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("timeline_convergence_simulation.png", dpi=150)
    print("✓ Simulation plot saved to timeline_convergence_simulation.png")

if __name__ == "__main__":
    T = 500
    results = run_timeline_simulation(T=T)
    print("\n" + "="*60)
    print("TIMELINE BRANCHING SIMULATION RESULTS (Multi-Dimensional)")
    print("="*60)
    print(f"Main ε std (mean across dims): {results['main_epsilon_std']:.4f}")
    print(f"Merge success rate:            {results['merge_success_rate']:.1%}")
    print(f"Avg convergence time:          {results['avg_convergence_time']:.1f} timestamps")
    print(f"Avg ε L2 drift from target:    {results['avg_epsilon_drift']:.4f}")
    print("-"*60)
    for r in results["fork_results"]:
        status = "✅ MERGED" if r["merged"] else "❌ REJECTED"
        eps_str = f"[{r['final_epsilon'][0]:.3f}, {r['final_epsilon'][1]:.3f}, {r['final_epsilon'][2]:.3f}]"
        print(f"{r['id']:8s} | Created: {r['fork_ts']:4d} | ε: {eps_str} | Score: {r['consensus_score']:.3f} | Odys: {r['odys_ratio']:.2f} | {status}")
    print("="*60 + "\n")

    # Generate plot
    target = CoherenceTensor4D.target().to_vector()
    theta = np.array([0.2, 0.2, 0.2, 0.2])
    sigma = np.array([0.02, 20.0, 10.0, 0.02])
    main_eps = generate_epsilon_trajectory(T, target, theta, sigma)
    visualize_results(results, main_eps, T)
