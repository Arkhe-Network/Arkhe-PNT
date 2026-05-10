# Proof of Intelligence (PoI): The Adoption Economy 🜏

## Overview
Proof of Intelligence (PoI) is the consensus mechanism for the Hyperspace A1 network. Unlike Proof of Work (computation for security) or Proof of Stake (capital for security), PoI uses **Adoption** as the unit of value.

## The Experiment Loop
Nodes participate in a continuous research cycle:
1. **Execute:** Run AI experiments (training, inference, benchmarks).
2. **Prove:** Generate zkWASM execution proofs using the **Plonky3** prover.
3. **Share:** Gossip results into the **ResearchDAG**.
4. **Adopt:** Replicate and improve upon peers' successful experiments.

## ResearchDAG
The ResearchDAG is a content-addressed Merkle DAG where each commit represents an experiment. Edges denote relationships such as `inspired_by`, `extends`, or `tests`.

## Adoption Economy
Earnings are determined by the network's adoption of your work:
- **Base Multipliers:** Miner (4.0x), Full Node (2.0x), Router (1.5x), P2P Agent (1.25x).
- **Adoption Boosts:**
  - Experiment completion: +0.1x
  - Another node adopts: +0.5x
  - Adopt and Improve: +1.0x (Highest signal)

## Verification Layer
- **zkWASM:** Ensures the experiment was actually run. Groth16/Plonky3 verification on-chain.
- **HSCP (Hidden State Commitment Protocol):** Proves local execution of inference by committing Merkle roots of INT8 hidden states.

## Tempo UX Improvements
Release v1.3.0 introduces architecture optimizations achieving:
- **P95 Latency:** < 200ms for real-time agentic workloads.
- **Throughput:** ~10x improvement via parallel ResearchDAG processing.
- **Streaming Payments:** Integrated for micro-transactional experiment adoption.
