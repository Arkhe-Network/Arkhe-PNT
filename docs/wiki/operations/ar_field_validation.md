---
type: validation
title: Validação AR – Protocolo de Campo (Central do Brasil)
tags: [ar, validation, field_test]
---

# Protocolo de Validação AR 🧪✅

## Testes Realizados (Abril 2026)
Local: Plataforma 5, Estação Central do Brasil.

### 1. Acurácia de Diagnóstico
- **Cenário**: Sensores com bateria removida e obstruídos com placas de metal.
- **Resultado**: 95% de correspondência entre o "Nó Vermelho" no tablet e a causa física real.

### 2. Estabilidade de Oclusão
- **Cenário**: Fluxo de 50 passageiros/segundo cruzando a linha de visão.
- **Resultado**: Rastreamento mantido via Dead Reckoning (sensores inerciais). Perda de alinhamento < 5%.

### 3. Manual K Override
- **Cenário**: Técnico forçando $K \times 2.0$ via interface AR.
- **Resultado**: Propagação de comando em < 1s; recuperação local de $R$ em 8s.

## Veredito
Sistema aprovado para deploy operacional na frota de manutenção da SuperVia.
