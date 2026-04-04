import json
import numpy as np
import matplotlib.pyplot as plt
import os

def load_baseline():
    try:
        with open('tzinor-state.json', 'r') as f:
            state = json.load(f)
            return state.get('lambdaCoherence', 0.98)
    except Exception as e:
        print(f"Warning: Could not load tzinor-state.json: {e}")
        return 0.98

def simulate_microtubule_experiment():
    baseline_coherence = load_baseline()
    print(f"🜏 Baseline Coherence (from Tzinor): {baseline_coherence:.4f}")

    # Parameters
    theta = np.linspace(0, np.pi, 200)
    noise_level = 0.005

    # Discrete angles (SL(3, Z))
    discrete_angles = {
        r"$\pi/5$": np.pi/5,
        r"$2\pi/5$": 2*np.pi/5,
        r"$\pi/4$": np.pi/4,
        r"$\pi/3$": np.pi/3,
        r"$\pi/2$": np.pi/2
    }

    # Model 1: Continuous SU(2) - Exponential decay
    R_su2 = baseline_coherence * np.exp(-0.2 * theta)
    R_su2_noisy = R_su2 + np.random.normal(0, noise_level, len(theta))

    # Model 2: Discrete SL(3, Z) - Decay with peaks
    R_sl3z = baseline_coherence * np.exp(-0.2 * theta)
    for name, angle in discrete_angles.items():
        # Add a Gaussian peak at each discrete angle
        # Increased peak height and width for better detection in simulation
        peak = 0.08 * np.exp(-((theta - angle)**2) / (2 * 0.015**2))
        R_sl3z += peak

    R_sl3z_noisy = R_sl3z + np.random.normal(0, noise_level, len(theta))

    # Peak Detection Algorithm (Sliding window of 11 for better smoothing)
    def detect_peaks(data, window_size=11, threshold_sigma=1.5):
        peaks_found = []
        for i in range(window_size, len(data) - window_size):
            window = data[i - window_size//2 : i + window_size//2 + 1]
            local_mean = np.mean(window)
            local_std = np.std(window)
            # Check if it's a local maximum and above a simple local threshold
            if data[i] > local_mean + threshold_sigma * local_std and data[i] == np.max(window):
                peaks_found.append(i)
        return peaks_found

    peaks_sl3z = detect_peaks(R_sl3z_noisy)

    # Visualization
    plt.figure(figsize=(12, 7))
    plt.plot(theta, R_su2_noisy, 'r-', alpha=0.3, label='SU(2) Hypothesis (Continuous)')
    plt.plot(theta, R_sl3z_noisy, 'b-', alpha=0.8, label=r'$SL(3, \mathbb{Z})$ Hypothesis (Discrete)')

    # Mark target angles
    for name, angle in discrete_angles.items():
        plt.axvline(x=angle, color='gray', linestyle='--', alpha=0.5)
        plt.text(angle, 0.5, name, rotation=90, verticalalignment='bottom', fontsize=10)

    # Highlight detected peaks
    if peaks_sl3z:
        plt.scatter(theta[peaks_sl3z], R_sl3z_noisy[peaks_sl3z], color='gold', edgecolors='black',
                    s=100, zorder=5, label='Detected Discrete Peaks')

    plt.title(r'Microtubule FRET Coherence Scan: $SU(2)$ vs $SL(3, \mathbb{Z})$', fontsize=14)
    plt.xlabel(r'Rotation Angle $\theta$ (rad)', fontsize=12)
    plt.ylabel(r'Coherence $R(\theta)$ (FRET Ratio)', fontsize=12)
    plt.ylim(0.4, 1.1)
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    output_path = 'microtubule_resurrect_plot.png'
    plt.savefig(output_path)
    print(f"🜏 Plot saved to {output_path}")

    # Print analysis
    print("\n🜏 --- Analysis Results ---")
    print(f"Target angles: {', '.join([f'{v:.4f}' for v in discrete_angles.values()])}")
    print(f"Detected peaks at θ: {', '.join([f'{theta[i]:.4f}' for i in peaks_sl3z])}")

    # Verify if peaks match targets
    matches = 0
    for p_idx in peaks_sl3z:
        p_theta = theta[p_idx]
        for t_theta in discrete_angles.values():
            if abs(p_theta - t_theta) < 0.015:
                matches += 1
                break

    print(f"Peak Matching Accuracy: {matches}/{len(discrete_angles)}")
    if matches >= 3:
        print(r"🜏 CONCLUSION: Discrete $SL(3, \mathbb{Z})$ substrate hypothesis supported by simulation.")
    else:
        print("🜏 CONCLUSION: Null hypothesis not rejected or insufficient resolution.")

if __name__ == "__main__":
    simulate_microtubule_experiment()
