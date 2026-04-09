---
tags: [quantum, dqd, stanza, protocol, automation]
date: 2026-04-07
source_count: 1
---

# 🜏 Stanza DQD Search Protocol

This protocol describes the automated discovery and tuning of **Double Quantum Dots (DQDs)** using the **Stanza** framework. This is a critical step for establishing stable spin qubits in silicon-based quantum devices.

## 1. Overview

The Stanza framework automates the transition from a fresh device to a functional Double Quantum Dot regime through a hierarchical, machine-learning-guided search. This minimizes measurement time by avoiding exhaustive high-resolution scans in non-promising voltage regions.

## 2. Hierarchical Search Stages

| Stage | Routine/Method | Objective | Computational Cost |
| :--- | :--- | :--- | :--- |
| **0. Health Check** | `device_health_check` | Validate device functionality and define safe voltage bounds. | **Mandatory** |
| **1. Scale Calibration** | `compute_peak_spacing` | Determine Coulomb peak spacing ($\Delta V$) to scale the search grid. | Medium |
| **2. Grid Search** | `run_dqd_search_fixed_barriers` | Hierarchical exploration of plunger gate (P1, P2) space. | Variable (Optimized) |
| **2a. Fast Filter** | *Current Trace* | 1D diagonal sweep (128 points). ML filtering for potential. | Low |
| **2b. Confirmation** | *Low-Res CSD* | 2D scan (16x16) of promising regions. | Medium |
| **2c. Characterization**| *High-Res CSD* | 2D scan (48x48) to confirm honeycomb patterns. | High |
| **3. Refinement** | `run_dqd_search` | Barrier gate (B0, B1, B2) sweeps if fixed barriers fail. | Very High |

## 3. Critical Parameters and Best Practices

- **Mandatory Health Check:** Never skip `device_health_check`. It establishes `max_safe_voltage_bound`.
- **Peak Spacing Calibration:** The `compute_peak_spacing` routine is the "eye" of the system. Typical values range from 10-200 mV. Outside this range indicates barrier configuration issues.
- **Grid Scaling:** The algorithm sets `grid_square_size = peak_spacing × 3/√2`.
- **Resolution Trade-offs:** The default resolutions (128/16/48) are optimized for the pre-trained ML classifiers (`coulomb-blockade-classifier-v3`). Increasing resolution (e.g., to 64x64) improves image quality but significantly increases measurement time.
- **Search Strategy:** The algorithm prioritizes neighboring squares (`include_diagonals`) once a DQD is found, as DQDs typically exist in continuous phase space regions.

## 4. Troubleshooting Guide

| Symptom | Probable Cause | Recommended Action |
| :--- | :--- | :--- |
| `No peak spacings found` | Not in Coulomb blockade regime. | Increase `max_search_scale` or adjust barrier voltages. |
| `dqd_squares` is empty | Sub-optimal tunnel coupling. | Run `run_dqd_search` with barrier sweeps. |
| Search is too slow | Resolution too high or `max_samples` too large. | Revert to default resolutions; set `num_dqds_for_exit: 1`. |
| False Positives | ML overfit or measurement noise. | Visual inspection; prioritize `total_score > 2.0`. |
| Out of Bounds | Grid reached safe operating limits. | **Expected.** Verify `v_lower_bound` and `v_upper_bound` in config. |

## 5. Integration with Arkhe(n)

The discovered DQD states are mapped to the **C-Domain** (Phase Coherence). A stable DQD configuration contributes to the global coherence parameter $\lambda_2$ within the **Kuramoto Engine**, enabling high-level quantum logic operations.

---
*Derived from Stanza Technical Documentation. Verified by Arkhe Quantum Systems Engineering.*
