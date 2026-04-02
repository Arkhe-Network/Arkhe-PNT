import time
import random

class FPGASimulator:
    def __init__(self, laser_duration_ns=1000):
        self.laser_duration_ns = laser_duration_ns
        self.laser_en = False
        self.microwave_en = False
        self.coherence_lock = False
        self.detector_count = 0
        self.state = "IDLE"

    def trigger(self):
        print("🜏 [HIL] Triggering FPGA Control Sequence...")
        self.state = "BUSY"
        self.laser_en = True
        self.microwave_en = True
        self.detector_count = 0

        # Simulate the duration of the pulse
        # In a real HIL, this would be a real-time loop
        steps = int(self.laser_duration_ns / 10)
        for _ in range(steps):
            # Simulate a detector pulse (fluorescence)
            if random.random() > 0.8:
                self.detector_count += 1

        self.laser_en = False
        self.microwave_en = False
        self.state = "IDLE"

        # Coherence detection logic (from Verilog)
        self.coherence_lock = self.detector_count > (steps * 0.15)

        print(f"🜏 [HIL] Pulse complete. Detector count: {self.detector_count}")
        print(f"🜏 [HIL] Coherence Lock: {self.coherence_lock}")
        return self.coherence_lock

if __name__ == "__main__":
    hil = FPGASimulator(laser_duration_ns=5000)
    print("--- Starting FPGA HIL Testbench ---")
    for i in range(5):
        print(f"\nCycle {i+1}:")
        locked = hil.trigger()
        time.sleep(0.5)
    print("\n--- Testbench Complete ---")
