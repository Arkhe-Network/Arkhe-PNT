---
type: implementation
title: Phase Gradient Redistributor – Embedded Neural Control (v3.1)
tags: [cpp, libtorch, redistributor, healing, embedded]
---

# Phase Gradient Redistributor (Embedded C++)

## Architecture
The redistributor is a LibTorch-based module that adjusts the coupling matrix $K_{ij}$ in real-time. It acts as an autonomic nervous system for the Tzinor network.

## Key Features
- **Autonomic Healing**: Automatically recovers coherence after EMP attacks or node failures.
- **Energy Calibration**: Penalizes high-power coupling for nodes with low battery levels.
- **Sybil Resistance**: Adjusts weights to "expel" noise-injected nodes (simulated in `sybil_test.cpp`).
- **Low Latency**: C++ implementation ensures < 10ms processing time per iteration on ARM64 hardware.

## Files
- `include/PhaseGradientRedistributor.h`: Module definition.
- `src/gateway_main.cpp`: Entry point for SuperVia gateways.
- `scripts/export_redistributor.py`: Python-to-TorchScript export pipeline.

## Performance Metrics
- **Post-EMP Recovery**: Coherence $R$ increases from 0.04 to 0.80 in ~50 iterations.
- **Memory Footprint**: ~50 MB including LibTorch runtime.
