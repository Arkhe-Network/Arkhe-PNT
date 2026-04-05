---
type: simulation
title: Stress Test de Colisão – Ataque EMP
tags: [simulation, emp, stress_test, crisis]
---

# Stress Test de Colisão (EMP Simulado) 💥⚡

## Cenário de Crise
Simulação de um pulso eletromagnético (EMP) desativando simultaneamente 20% dos nós móveis (carros, BRTs e trens) da rede Tzinor durante um ataque de arrasto da IA central.

## Parâmetros
- **Nós Móveis Totais**: 370
- **Fração de Perda**: 20% (74 unidades)
- **Duração da Inativação**: 30 segundos
- **Ataque IA**: $K_{ext} = 6.0$

## Resultados Analíticos
- **Queda de Coerência**: $R(t)$ caiu de 0.96 para **0.002** instantaneamente durante o blackout dos nós móveis.
- **Tempo de Recuperação**: 12.5 segundos após o reboot dos nós.
- **Resiliência Medida (ρ)**: 0.76 (Global).

## Medidas de Endurecimento
1. **Blindagem Faraday**: Gaiolas de alumínio para todos os módulos Tzinor.
2. **Nós Sombra**: Sensores fixos que replicam o último estado de fase de nós móveis offline.
3. **Redundância Interestadual**: O Beacon de Liberdade fornece uma âncora externa caso a malha local seja comprometida.
