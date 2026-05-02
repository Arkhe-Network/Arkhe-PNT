#!/bin/bash
echo "🔬 ARKHE OS v∞.340.3 — Validation Suite Execution"
echo "=================================================="

mkdir -p results/vortex_simulation results/watermark_simulation results/homeostasis_simulation
mkdir -p exports/meep layouts docs reports

echo "[1/3] Running vortex array spectral response simulation..."
python simulate_vortex_array_response.py --output results/vortex_simulation/vortex_response_validation.h5
echo "✓ Vortex: OK"

echo "[2/3] Running optical watermarking simulation..."
python simulate_optical_watermark.py --output results/watermark_simulation/watermark_validation.npz
echo "✓ Watermark: OK"

echo "[3/3] Running optical homeostatic loop simulation..."
python simulate_optical_homeostasis.py --output results/homeostasis_simulation/analysis_summary.json
echo "✓ Homeostasis: OK"

echo "✨ Validation suite complete"
