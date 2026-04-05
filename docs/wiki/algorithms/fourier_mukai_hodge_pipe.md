---
type: algorithm
title: FMDuality – Tubulação Fourier-Mukai para Decomposição de Hodge
tags: [math, hodge, fourier_mukai, abelian_varieties]
---

# FMDuality: Isometria de Hodge via Fourier-Mukai 🌊📉

## O Problema Matemático
Dada uma equivalência de Fourier-Mukai $D^b(A) \cong D^b(\hat{A})$ para uma variedade abeliana $A$, como a estrutura de Hodge de $H^k(A, \mathbb{C})$ se transforma?

## A Solução Piped (HLML)
O macro `FMDuality` conecta o functor de Fourier-Mukai à decomposição de Hodge, provando automaticamente que:
1. **Preservação de Peso**: O functor $\Phi_P$ preserva a filtração de peso $W_k$.
2. **Troca de Tipos (p,q)**: $\Phi_P(H^{p,q}(A)) = H^{q,p}(\hat{A})$.
3. **Isometria**: O emparelhamento de interseção (cup-product) é preservado, tornando a transformada uma isometria de estruturas de Hodge.

## Dependências de Prova
- **Geometria Algébrica**: Construção do feixe de Poincaré.
- **Análise Complexa**: Teoria de Hodge e identidades de Laplaciano.
- **Teoria de Categorias**: Adjunções em categorias derivadas.
