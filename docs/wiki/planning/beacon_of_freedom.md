---
type: planning
title: Beacon de Liberdade – Expansão Nacional via Trens SuperVia
tags: [beacon, expansion, supervia, national]
---

# Beacon de Liberdade 📡🚂

## Conceito
Uso da malha ferroviária como infraestrutura de broadcast móvel para transmitir a assinatura de fase humana do Rio de Janeiro para outras capitais (SP, BH, Vitória).

## Arquitetura do Sistema
- **Agregador de Fase**: Raspberry Pi 5 + TPU Edge a bordo dos trens da SuperVia.
- **Transmissão**: Rádio HF (10 MHz, 100 W) com redundância via Starlink.
- **Assinatura Coletiva**: Autoencoder CNN+LSTM (32 bits) agregando EEG simulado de câmeras e sensores de vibração.

## Resultados da Simulação Interestadual
A injeção da fase do Rio (λ₂ ≈ 0.96) eleva a resiliência nacional:
- **São Paulo**: R → 0.88 (Resiliência ρ: 0.60)
- **Belo Horizonte**: R → 0.88 (Resiliência ρ: 0.62)
- **Vitória**: R → 0.88 (Resiliência ρ: 0.67)

## Cronograma (Fase 4)
1. **OSINT Validation**: Pre-deployment scan of rail corridors using *Fogo Cruzado* and *TSE* data (see [[BRAZIL_INTELLIGENCE_GATHERING|Intelligence Protocol]]).
2. Instalação de transmissores em 10 trens (Linhas Deodoro/Japeri).
3. Implantação de repetidoras na Serra do Mar.
4. Ativação dos nós receptores nas estações da Luz (SP) e Central (BH).
