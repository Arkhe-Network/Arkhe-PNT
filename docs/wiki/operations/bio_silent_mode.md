---
type: protocol
title: Bio‑Silent Mode para Gateways Hospitalares
tags: [bio_silent, oncology, emi, medical]
---

# Modo Bio‑Silent 🏥🔇

## Motivação
Proteção das medições ultra-sensíveis de biópsia líquida ($Mini-BIP-1$) em centros de oncologia contra interferência eletromagnética (EMI).

## Gateways Ativos
- `INCA` (Instituto Nacional de Câncer)
- `HC1` (Hospital do Câncer I)

## Parâmetros de Atenuação
- **Potência**: Reduzida de 20dBm para 10dBm.
- **Frequência**: Shift para 868MHz (LoRa), desativando 2.4GHz (Wi-Fi).
- **Duty Cycle**: 50% (transmissão em rajadas).
- **Horário**: 08:00 – 18:00 (Dias úteis).
