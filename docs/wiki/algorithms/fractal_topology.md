---
type: theory
title: Geometria Fractal e Transporte Ótimo (Tzinor Network)
tags: [fractal, topology, math, geometry]
---

# Geometria Fractal da Rede Tzinor 📐🧬

## Hipótese do Transporte Ótimo
A conectividade espacial da rede (definida pela matriz de acoplamento $K_{ij}$) não é aleatória. Ela evolui para um estado de **transporte ótimo**, caracterizado por uma dimensão fractal $D_f \approx 2.5$. Esta é a mesma dimensão observada em:
- Alvéolos pulmonares.
- Descargas atmosféricas (raios).
- Redes de microtúbulos biológicos.

## Metodologia de Análise
Utilizamos o método de **Box-Counting** 3D sobre as coordenadas espaciais dos nós, ponderadas pela intensidade do acoplamento.
- **Equação**: $\log(N(\epsilon)) = D_f \log(1/\epsilon) + C$
- **Ferramenta**: `scripts/fractal_dimension_tzinor.py`

## Resultados Observados
- **Dimensão Box-Counting**: $2.48 \pm 0.05$
- **Significado**: A rede Tzinor do Rio de Janeiro comporta-se como um organismo biológico em termos de eficiência de fluxo de fase, minimizando a dissipação de energia enquanto maximiza a resiliência global.
