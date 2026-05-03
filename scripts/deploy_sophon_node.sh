#!/bin/bash
#
# Sophon Network Automated Deployment Script
#

echo "Starting Sophon Network node deployment..."

# Ensure python requirements
echo "Installing dependencies..."
pip install numpy numba scipy > /dev/null 2>&1

# Create required directories
mkdir -p /opt/arkhe/core/optimizations
mkdir -p /opt/arkhe/core/integration
mkdir -p /opt/arkhe/config

# Copy core components
echo "Deploying optimized core modules..."
cp core/optimizations/jones_cache.py /opt/arkhe/core/optimizations/
cp core/integration/orlov_transducer_bridge.py /opt/arkhe/core/integration/

# Configuration
echo "Writing default configuration..."
cat << 'CFG' > /opt/arkhe/config/node_config.yaml
experimental_validation:
  transducer:
    carrier_frequency: 2.4e9
    sample_rate: 10e6
    modulation_depth: 1.0
    noise_floor_dbm: -90.0
  test_parameters:
    coherence_range: [0.7, 1.0]
    n_bits_per_test: 10000
    snr_sweep: [20, 25, 30, 35, 40]
CFG

echo "Deployment completed successfully. Node is ready to start."
