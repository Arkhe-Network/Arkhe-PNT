---
type: tool
title: AR Field Tool – Visualização da Nuvem de Fase
tags: [ar, visualization, field_service, maintenance]
---

# AR Field Tool – Nuvem de Fase 🧩📡

## Visão Geral
Aplicação de Realidade Aumentada (Unity + AR Foundation) para técnicos de campo da SuperVia, permitindo a inspeção visual e intervenção direta na rede Tzinor.

## Funcionalidades Core
- **Mapa de Calor 3D**: Sobreposição colorida no chão representando a coerência média ($R$) da área.
- **Grafo de Arestas**: Visualização dos pesos de acoplamento ($K$) entre gateways e sensores.
- **Diagnóstico Instantâneo**: Identificação automática de causas de falha (ex: Bateria Baixa, Obstrução Física).
- **Manual Override**: Interface touch para forçar aumento temporário de $K$ em situações de crise.

## Arquitetura de Dados
- **Stream**: WebSocket em `/api/ar/stream` fornecendo lat/lon/alt e métricas a 2Hz.
- **Intervenção**: API REST `/api/ar/manual-override` para submissão de comandos de técnico.
