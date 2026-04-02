#!/bin/bash
set -e

echo "[OrbVM] Building Rust Core..."
cargo build --release

echo "[OrbVM] Building C++ Bindings..."
mkdir -p cpp/build
cd cpp/build
cmake ..
make
cd ../..

echo "[OrbVM] Building Swift Module..."
cd swift
swift build
cd ..

echo "[OrbVM] Compiling Verilog Core..."
# Assuming iverilog is installed
# iverilog -o verilog/orbvm_core.vvp verilog/orbvm_core.v

echo "[OrbVM] Build Complete."
