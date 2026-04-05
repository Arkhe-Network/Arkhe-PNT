---
type: implementation
title: Phase Gradient Redistributor – Versão C++/LibTorch
tags: [cpp, libtorch, redistributor, gateway]
updated: 2026-04-05
---

# Redistribuidor de Acoplamento em C++

## Arquivo fonte
- `phase_redistributor/include/PhaseGradientRedistributor.h`
- `phase_redistributor/src/PhaseGradientRedistributor.cpp`
- Compilado com LibTorch 2.0+.

## Integração nos gateways
- Executado como serviço systemd nos nós de borda (Raspberry Pi / Jetson).
- Acionado automaticamente quando `R < 0.7` e a taxa de nós ativos `alive_ratio < 0.85`.

## Performance (Benchmarking)
- **Cenário**: 1000 nós.
- **Duração**: 50 iterações em ~0,8 segundos (NVIDIA Jetson Nano).
- **Consumo**: ~50 MB RAM.

## Próximos passos
- Adicionar suporte a aceleração via GPU (CUDA) para redes urbanas de larga escala (>10.000 nós).
- Criar bindings Python (Pybind11) para facilitar testes rápidos no dashboard Archimedes-Ω.
