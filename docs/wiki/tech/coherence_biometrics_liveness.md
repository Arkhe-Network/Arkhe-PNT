---
type: protocol
title: Liveness Detection – Micro‑saccades & GSR (Σ‑Level 0)
tags: [liveness, security, sigma0, eye_tracking, gsr]
---

# Liveness Detection para Segurança Crítica 👁️🔌

## Objetivo
Adicionar uma camada de vitalidade dinâmica para áreas Σ‑Level 0 (ex: núcleo do reator STEP).

## Canais de Validação
1. **Micro-sacadas Oculares**: Movimentos involuntários de alta frequência (120-240 Hz) detectados via câmera IR. Inimitação por IA ou vídeo.
2. **Resposta Galvânica (GSR)**: Correlação entre a condutância da pele e flutuações magnéticas do STEP. O corpo humano atua como uma antena passiva, provando presença física no local.

## Critério de Autenticação
- **VitalID Match** (Similaridade $\ge 0.85$)
- **Liveness Score** (Combinado $\ge 0.90$)
- **Clone Defense** (Similaridade $< 0.92$)
