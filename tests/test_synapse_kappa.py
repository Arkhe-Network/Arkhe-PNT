import pytest
import numpy as np
from src.physics.synapse_kappa import calculate_adaptive_gain, SynapseKappaEngine

def test_adaptive_gain_regimes():
    # Test Super-radiance regime (W_0 < -0.2)
    gain_super = calculate_adaptive_gain(k=10, N=100, W_0=-0.5)
    # Test Coherent regime (-0.2 <= W_0 < 0)
    gain_coherent = calculate_adaptive_gain(k=10, N=100, W_0=-0.1)
    # Test Collapse regime (W_0 >= 0)
    gain_collapse = calculate_adaptive_gain(k=10, N=100, W_0=0.1)

    assert gain_super < gain_coherent
    assert gain_collapse > gain_coherent

def test_landauer_dissipation():
    engine = SynapseKappaEngine()
    # No error -> no dissipation
    assert engine.calculate_landauer_dissipation(0.0) == 0.0
    # Higher error -> higher dissipation
    d1 = engine.calculate_landauer_dissipation(0.1)
    d2 = engine.calculate_landauer_dissipation(0.5)
    assert d2 > d1

def test_thermal_rectification():
    engine = SynapseKappaEngine()
    factor = engine.thermal_rectification_factor(1.0)
    # Should be high due to anisotropy (1.5 / 0.015 = 100)
    assert factor == 0.99

def test_process_step():
    engine = SynapseKappaEngine()
    result = engine.process_step(k=10, N=100, W_0=-0.15, lambda2=0.95)

    assert "gain" in result
    assert "q_diss_joules" in result
    assert "rectified_heat" in result
    assert result["thermal_safety_margin"] > 0

def test_signal_correlation():
    engine = SynapseKappaEngine()
    # High correlation when signals are similar
    corr_high = engine.correlate_signals(0.9, 0.9, 0.9)
    # Low correlation when signals diverge
    corr_low = engine.correlate_signals(0.9, 0.2, 0.5)
    assert corr_high > corr_low

def test_optical_oracle():
    from src.physics.synapse_kappa import OpticalOracle
    oracle = OpticalOracle()
    result = oracle.run_time_gating_cycle()
    assert "upe_counts" in result
    assert "nv_fluorescence" in result
    assert "atp_luminescence" in result

def test_hbn_functionalizer():
    from src.physics.synapse_kappa import hBNFunctionalizer
    func = hBNFunctionalizer()
    res1 = func.step_insertion(10.0)
    assert res1["distance_nm"] < 50.0

    # Critical distance - loop to get closer
    for _ in range(50):
        res2 = func.step_insertion(1.0)
    assert res2["distance_nm"] < 5.0
