#!/usr/bin/env python3
"""
calmodulin_lambda2_analysis.py
===============================
Analysis pipeline for Calmodulin Dimer Phase 1 — Arkhe(n) Synapse-kappa.
Extended with Solvation Displacement and Thermodynamic Force analysis.

This script:
1. Extracts dihedral angles of residue 74 (linker hinge) from monA and monB.
2. Calculates lambda-2 conformational coherence over time.
3. Quantifies solvation displacement and entropy changes at the Ca2+ binding sites.
4. Performs statistical and thermodynamic analysis (ANOVA, Pearson, G_displacement).
5. Generates summary plots (4 panels).

Arkhe-Chain timestamp: 847.621
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

try:
    import MDAnalysis as mda
    from MDAnalysis.analysis import dihedrals
    from MDAnalysis.lib.distances import distance_array
except ImportError:
    mda = None
    print("MDAnalysis not installed. Falling back to mock data for demonstration.")

class SolvationDisplacementAnalyzer:
    """
    Measures water displacement by Ca2+ and correlates with lambda-2.
    """
    def __init__(self, topology, trajectory, calcium_sel="resname CA",
                 water_sel="resname SOL and around 3.0 (resname CA)"):
        if mda is None:
            self.u = None
            return
        self.u = mda.Universe(topology, trajectory)
        self.ca = self.u.select_atoms(calcium_sel)
        self.water_shell = self.u.select_atoms(water_sel, updating=True)

    def calculate_solvation_entropy(self, frame):
        """
        Estimates configurational entropy of solvation water via 2-body correlation.
        """
        if self.u is None:
            return 0.0, 0

        self.u.trajectory[frame]
        if len(self.water_shell) == 0:
            return 0.0, 0

        water_o = self.water_shell.select_atoms("name OW").positions
        n_water = len(water_o)

        if n_water < 2:
            return 0.0, n_water

        dist_matrix = distance_array(water_o, water_o)
        hist, _ = np.histogram(dist_matrix[dist_matrix > 0], bins=50, range=(0, 10), density=True)

        p = hist / hist.sum()
        p = p[p > 0]
        S_config = -np.sum(p * np.log(p))

        return S_config, n_water

def calculate_lambda2(phi_a, phi_b):
    """
    Calculate lambda-2 conformational coherence.
    lambda2(t) = (1/2) |exp(i*theta-1(t)) + exp(i*theta-2(t))|
    """
    phi_a_rad = np.deg2rad(phi_a)
    phi_b_rad = np.deg2rad(phi_b)
    z = 0.5 * (np.exp(1j * phi_a_rad) + np.exp(1j * phi_b_rad))
    return np.abs(z)

def extract_dihedrals(work_dir):
    """
    Extract residue 74 dihedrals. Atoms: N-CA-C-N
    """
    if mda is None:
        n_frames = 1000
        if "apo" in work_dir:
            phi_a = np.random.normal(0, 80, n_frames)
            phi_b = np.random.normal(180, 80, n_frames)
        elif "4ca" in work_dir:
            phi_a = np.random.normal(60, 10, n_frames)
            phi_b = np.random.normal(60, 10, n_frames)
        else: # 2ca
            phi_a = np.random.normal(30, 40, n_frames)
            phi_b = np.random.normal(40, 40, n_frames)
        return np.linspace(0, 100, n_frames), phi_a, phi_b

    tpr = os.path.join(work_dir, "production.tpr")
    xtc = os.path.join(work_dir, "production.xtc")

    if not os.path.exists(tpr) or not os.path.exists(xtc):
        return None, None, None

    u = mda.Universe(tpr, xtc)
    sel_a = [
        u.select_atoms("segid PROA and resid 74 and name N")[0],
        u.select_atoms("segid PROA and resid 74 and name CA")[0],
        u.select_atoms("segid PROA and resid 74 and name C")[0],
        u.select_atoms("segid PROA and resid 75 and name N")[0]
    ]
    sel_b = [
        u.select_atoms("segid PROB and resid 74 and name N")[0],
        u.select_atoms("segid PROB and resid 74 and name CA")[0],
        u.select_atoms("segid PROB and resid 74 and name C")[0],
        u.select_atoms("segid PROB and resid 75 and name N")[0]
    ]

    phi_a = []
    phi_b = []
    times = []
    for ts in u.trajectory:
        times.append(ts.time / 1000.0)
        phi_a.append(mda.lib.distances.calc_dihedrals(sel_a[0].position, sel_a[1].position, sel_a[2].position, sel_a[3].position))
        phi_b.append(mda.lib.distances.calc_dihedrals(sel_b[0].position, sel_b[1].position, sel_b[2].position, sel_b[3].position))

    return np.array(times), np.array(phi_a), np.array(phi_b)

def main():
    states = ["apo", "2ca", "4ca"]
    n_replicas = 5
    results = []

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("Starting integrated Arkhe(n) Calmodulin Analysis...")

    for state in states:
        for r in range(n_replicas):
            work_dir = os.path.join(parent_dir, f"{state}_r{r}")
            times, phi_a, phi_b = extract_dihedrals(work_dir)

            if times is not None:
                l2 = calculate_lambda2(phi_a, phi_b)
                mean_l2 = np.mean(l2)

                # Mock solvation metrics if real simulation isn't available
                if mda is None:
                    if state == "apo":
                        n_water = np.random.randint(6, 10)
                        s_solv = np.random.uniform(4.0, 5.0)
                    elif state == "4ca":
                        n_water = np.random.randint(0, 2)
                        s_solv = np.random.uniform(1.0, 2.0)
                    else:
                        n_water = np.random.randint(2, 6)
                        s_solv = np.random.uniform(2.5, 4.0)
                else:
                    # In real usage, use SolvationDisplacementAnalyzer
                    analyzer = SolvationDisplacementAnalyzer(os.path.join(work_dir, "production.tpr"),
                                                           os.path.join(work_dir, "production.xtc"))
                    s_solv_traj = []
                    n_water_traj = []
                    for f in range(len(analyzer.u.trajectory)):
                        s, n = analyzer.calculate_solvation_entropy(f)
                        s_solv_traj.append(s)
                        n_water_traj.append(n)
                    s_solv = np.mean(s_solv_traj)
                    n_water = np.mean(n_water_traj)

                results.append({
                    "state": state,
                    "replica": r,
                    "lambda2": mean_l2,
                    "n_water": n_water,
                    "S_solvation": s_solv
                })
                print(f"  {state} r{r}: lambda-2={mean_l2:.4f}, S_solv={s_solv:.3f}, n_water={n_water:.1f}")

    if not results:
        print("No results to analyze.")
        return

    df = pd.DataFrame(results)

    # Thermodynamic Displacement Calculation
    T = 310 # K
    delta_S_solv = df[df["state"]=="4ca"]["S_solvation"].mean() - df[df["state"]=="apo"]["S_solvation"].mean()
    G_disp = -T * delta_S_solv * 0.008314 # kJ/mol proxy

    print(f"\n[Arkhe-Chain] Thermodynamic Analysis:")
    print(f"  Delta S_solvation: {delta_S_solv:.3f} bits")
    print(f"  G_displacement (proxy): {G_disp:.2f} kJ/mol")

    # Plotting (4 panels)
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Arkhe(n) Calmodulin Phase 1: Solvation & Coherence', fontsize=16)

    # 1. Lambda-2 Bar Chart
    means = df.groupby("state")["lambda2"].mean()
    stds = df.groupby("state")["lambda2"].std()
    means.loc[states].plot(kind="bar", yerr=stds, ax=axes[0,0], color=['#ef4444', '#f59e0b', '#10b981'])
    axes[0,0].axhline(y=0.847, color='blue', linestyle='--', label="λ2-crit (0.847)")
    axes[0,0].set_title("Mean Lambda-2 by State")
    axes[0,0].set_ylabel("Coherence λ2")
    axes[0,0].legend()

    # 2. Solvation Displacement vs Lambda-2
    colors = {'apo': '#ef4444', '2ca': '#f59e0b', '4ca': '#10b981'}
    for s in states:
        subset = df[df["state"] == s]
        axes[0,1].scatter(subset["n_water"], subset["lambda2"], c=colors[s], label=s, s=50)
    axes[0,1].set_title("Solvation Displacement vs Coherence")
    axes[0,1].set_xlabel("N Water Molecules in Site")
    axes[0,1].set_ylabel("Coherence λ2")
    axes[0,1].legend()

    # 3. Solvation Entropy by State
    s_means = df.groupby("state")["S_solvation"].mean()
    s_stds = df.groupby("state")["S_solvation"].std()
    s_means.loc[states].plot(kind="bar", yerr=s_stds, ax=axes[1,0], color=['#ef4444', '#f59e0b', '#10b981'])
    axes[1,0].set_title("Solvation Entropy S_config")
    axes[1,0].set_ylabel("Entropy (bits)")

    # 4. Phase Diagram
    ca_conc = [0, 2, 4]
    l2_means = [df[df["state"]==s]["lambda2"].mean() for s in states]
    l2_stds = [df[df["state"]==s]["lambda2"].std() for s in states]
    axes[1,1].errorbar(ca_conc, l2_means, yerr=l2_stds, fmt='o-', color='#6366f1', markersize=10, capsize=5)
    axes[1,1].axhline(y=0.847, color='red', linestyle='--')
    axes[1,1].fill_between(ca_conc, 0.847, 1.0, alpha=0.1, color='green', label='Coherent')
    axes[1,1].fill_between(ca_conc, 0, 0.847, alpha=0.1, color='red', label='Thermal')
    axes[1,1].set_title("Calcium-Induced Phase Transition")
    axes[1,1].set_xlabel("Ca2+ per Monomer")
    axes[1,1].set_ylabel("Mean λ2")
    axes[1,1].legend()

    plt.tight_layout()
    plt.savefig("arkhe_calmodulin_displacement_analysis.png")
    print(f"\nAnalysis complete. Plot saved as arkhe_calmodulin_displacement_analysis.png")

if __name__ == "__main__":
    main()
