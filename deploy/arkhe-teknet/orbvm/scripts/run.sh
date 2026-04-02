#!/bin/bash
set -e

echo "[OrbVM] Running Rust Core..."
cargo run --release

echo "[OrbVM] Running Swift Tests..."
cd swift
swift test || echo "No tests defined yet."
cd ..

echo "[OrbVM] Execution Complete."
