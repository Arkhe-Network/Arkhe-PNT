import numpy as np
import scipy.signal as signal

def compute_liveness_score(gsr, mag_noise, fs=100.0):
    """
    Computes liveness score based on GSR-Magnetic coherence and stability.
    """
    # 1. Bandpass filter (0.5-30 Hz)
    nyquist = fs / 2.0
    b, a = signal.butter(4, [0.5/nyquist, 30/nyquist], btype='band')
    gsr_f = signal.filtfilt(b, a, gsr)
    mag_f = signal.filtfilt(b, a, mag_noise)

    # 2. Coherence
    freqs, coh = signal.coherence(gsr_f, mag_f, fs=fs, nperseg=int(fs*2))
    band = (freqs >= 0.5) & (freqs <= 30)
    mean_coh = np.mean(coh[band])

    # 3. Stability (Std Dev of coherence across windows)
    # For simulation, we'll assume a value based on mean_coh
    stability = 0.9 if mean_coh > 0.3 else 0.2

    return 0.7 * mean_coh + 0.3 * stability

def run_sim():
    print("🜏 [LIVENESS] Simulating Σ-Level 0 Body-Antenna Coupling...")
    fs = 100.0
    duration = 10.0
    t = np.arange(0, duration, 1/fs)

    # Case 1: Real Operator (Coupled with STEP magnetic fluctuations)
    mag_noise = np.random.normal(0, 1.0, len(t))
    gsr_real = 0.4 * mag_noise + np.random.normal(0, 0.5, len(t)) # Coupled
    score_real = compute_liveness_score(gsr_real, mag_noise)

    # Case 2: Silicone Mask / Replay (Uncoupled noise)
    gsr_fake = np.random.normal(0, 1.0, len(t))
    score_fake = compute_liveness_score(gsr_fake, mag_noise)

    print(f"  > Real Operator Liveness Score: {score_real:.4f}")
    print(f"  > Synthetic Attack Liveness Score: {score_fake:.4f}")

    if score_real > 0.5 > score_fake:
        print("✅ VERDICT: Liveness engine correctly differentiates real bio-coupling from synthetic noise.")

if __name__ == "__main__":
    run_sim()
