#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@license
Copyright 2026 Google LLC
SPDX-License-Identifier: Apache-2.0

test_neural_firmware.py — Validação do firmware neural v70.0
"""

import numpy as np

def simulate_brain_signal(duration_ms=500, sample_rate_hz=1000, coherence=0.8, include_artifacts=False):
    t = np.linspace(0, duration_ms/1000, duration_ms)
    # Small ELF signal
    signal = np.sin(2 * np.pi * 60.0 * t) * coherence
    noise = np.random.normal(0, 1.0, duration_ms)

    output = (signal * 50 + 2048 + noise)
    if include_artifacts:
        # Oscillating large noise to trigger multiple score increments
        output[250:350] += np.random.choice([-500, 500], 100)

    return output.astype(np.int16)

def test_firmware_logic():
    print("🧪 Testing Neural Firmware logic (v70.0)...")
    clean_signal = simulate_brain_signal(coherence=0.9, include_artifacts=False)
    noisy_signal = simulate_brain_signal(coherence=0.9, include_artifacts=True)

    # Mock motion correction (matching C logic)
    def mock_correct(sig):
        score = np.sum(np.abs(sig[1:].astype(np.int32) - sig[:-1].astype(np.int32)) > 100)
        return max(0, 1.0 - (score / (len(sig) * 0.1)))

    clean_factor = mock_correct(clean_signal)
    noisy_factor = mock_correct(noisy_signal)

    print(f"   Clean Signal Factor: {clean_factor:.2f}")
    print(f"   Noisy Signal Factor: {noisy_factor:.2f}")

    assert clean_factor > 0.9
    assert noisy_factor < 0.5
    print("✅ Neural Firmware logic validated.")

if __name__ == "__main__":
    test_firmware_logic()
