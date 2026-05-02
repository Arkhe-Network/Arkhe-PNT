# ARKHE OS v∞.340.3

## Protocolo de Preparação: Setup Experimental Pós-Fabricação

Este documento especifica o setup necessário para a caracterização do chip fotônico (MPW) que contém a matriz de micro-vórtices e o circuito de watermarking óptico.

### Equipamentos Necessários

1. **Laser Sintonizável (Tunable Laser):**
   * Faixa de operação: 400 nm a 1550 nm.
   * Acoplamento via fibra óptica single-mode ou espaço livre.

2. **Espectrômetro de Alta Resolução:**
   * Resolução espectral: < 1 nm.
   * Responsividade otimizada para capturar o perfil modulado em 1550 nm.

3. **Modulador Espacial de Luz (SLM):**
   * Resolução: 1920x1080 (HD) mínimo.
   * Utilizado para gerar padrões de fase arbitrários para calibrar o fechamento do loop homeostático (Kerr/termo-óptico).

### Procedimento de Caracterização

1. Acoplar a fonte de luz na entrada do chip.
2. Injetar o padrão base configurado via SLM.
3. Coletar e validar o espectro na saída para confirmar a decodificação da fase, a coerência do loop e a correlação do watermarking criptográfico ZEE200 (SN > 21.1 dB).
