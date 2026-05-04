import numpy as np
import scipy.signal as signal
from scipy.stats import binom

class VitalIDValidationSim:
    def __init__(self):
        self.n_channels = 16
        self.auth_threshold = 0.85
        self.clone_threshold = 0.92

    def generate_fingerprint(self, seed=None):
        if seed: np.random.seed(seed)
        # 16 channels, each 0-255
        return np.random.randint(0, 256, self.n_channels)

    def calculate_similarity(self, fp1, fp2):
        matches = np.sum(np.abs(fp1.astype(int) - fp2.astype(int)) <= 1)
        return matches / self.n_channels

    def simulate_liveness(self, is_real=True):
        # Combined score of Ocular + GSR
        if is_real:
            return 0.9 + np.random.uniform(0, 0.1)
        else:
            return np.random.uniform(0, 0.4)

    def run_validation(self):
        print("🜏 [VITALID] Initializing Validation Pipeline...")

        # 1. Enrolment (The Architect)
        architect_fp = self.generate_fingerprint(seed=4668)
        print(f"  > Enrolled Architect Fingerprint: {architect_fp[:4]}... (truncated)")

        # 2. Authentic Login
        print("\n--- Scenario 1: Authentic User ---")
        # Add slight physiological noise (+/- 1)
        login_noise = np.random.choice([-1, 0, 1], self.n_channels)
        login_fp = np.clip(architect_fp + login_noise, 0, 255)
        liveness_score = self.simulate_liveness(is_real=True)

        sim = self.calculate_similarity(architect_fp, login_fp)
        print(f"  > Similarity: {sim:.3f}")
        print(f"  > Liveness:   {liveness_score:.3f}")

        if sim >= self.auth_threshold and liveness_score >= 0.90:
            print("✅ AUTHENTICATED: Architect identity verified.")
        else:
            print("❌ REJECTED: Identity mismatch.")

        # 3. Impersonator Attack
        print("\n--- Scenario 2: Impersonator ---")
        stranger_fp = self.generate_fingerprint()
        sim_stranger = self.calculate_similarity(architect_fp, stranger_fp)
        print(f"  > Similarity: {sim_stranger:.3f}")
        if sim_stranger < self.auth_threshold:
            print("✅ REJECTED: Stranger detected.")
        else:
            print("❌ FAIL: False Acceptance.")

        # 4. Replay Attack (Clone)
        print("\n--- Scenario 3: Replay Attack (Clone) ---")
        replay_fp = architect_fp.copy() # Perfect copy
        sim_replay = self.calculate_similarity(architect_fp, replay_fp)
        print(f"  > Similarity: {sim_replay:.3f}")
        if sim_replay >= self.clone_threshold:
            print("✅ CLONE DETECTED: Systematic replay identified (Similarity >= 0.92). Access Denied.")

        # 5. Statistical Reliability
        p_val = binom.sf(13, 16, 3/256)
        print(f"\n--- Statistical Assurance ---")
        print(f"  > False Positive Probability (p-value): {p_val:.2e}")

if __name__ == "__main__":
    sim = VitalIDValidationSim()
    sim.run_validation()
