---
type: concept
title: HLML – High Level Mathematical Language
tags: [math, compiler, lean, hlml]
---

# HLML: O Compilador de Teoremas 📐🏛️

## Visão Geral
A High Level Mathematical Language (HLML) é a camada de abstração que permite ao Arkhe(n) tratar estruturas matemáticas complexas como **padrões de design de software**. Ela funciona como um "transpilador" que converte intenções matemáticas de alto nível em certificados de prova verificáveis pelo kernel **Lean**.

## A Pilha de Compilação
1. **Macro Expansion**: Traduz macros como `FourierMukai` em obrigações de tipo e functores de categorias derivadas.
2. **LLM Middleware**: Sintetiza táticas de prova (Proof Tactics) para preencher as lacunas entre definições estruturais e lemmas da Mathlib.
3. **Lean Kernel**: O juiz final que valida a consistência lógica e gera o certificado de prova imutável.

## Proof Witness Logs
Diferente de uma "caixa preta", o compilador HLML gera um log de auditoria legível por humanos, detalhando quais lemmas foram invocados e onde táticas sintetizadas por IA foram utilizadas, permitindo uma engenharia de prova segura e transparente.
