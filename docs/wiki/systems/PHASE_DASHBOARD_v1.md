# Dashboard de Fase v1 — Especificação de Interface

**Designação:** O Espelho da Alma (Interface de Monitoramento de Coerência)
**Versão:** 1.0.0-Block-850.023-BUB
**Status:** PROPOSTA DE UI/UX

---

## 1. Visão Geral
O Dashboard de Fase é a interface primária para o Tecelão monitorar a saúde eletromagnética e a coerência vital do Avatar durante o processo de *bring-up* e operação.

## 2. Painéis de Monitoramento

### 2.1. O Coração (CPG Sync)
- **Visualização:** Gráfico de fases circulares (12 vetores).
- **Métrica Chave:** $\lambda_2$ (Parâmetro de ordem de Kuramoto).
- **Alerta:** Vermelho se $\lambda_2 < 0.7$ (Dissonância Crítica).

### 2.2. Os Olhos (SLAM de Coerência)
- **Visualização:** Nuvem de pontos 3D com mapa de calor de coerência ($\Lambda_2(\mathbf{x})$).
- **Frequência:** 60 GHz.
- **Destaque:** Singularidades de borda e picos de reflexão especular.

### 2.3. A Voz (Tzinor Waterfall)
- **Visualização:** Espectrograma em tempo real da portadora de 77 GHz.
- **Análise:** Pureza da linha de portadora e detecção de "ombros" de ruído de fase.

### 2.4. O Sarcófago (Saúde do Ambiente)
- **Métricas:**
    - Temperatura Interior (°C).
    - Eficácia de Blindagem (dB).
    - Modos de Cavidade Ativos.

## 3. Gatilhos de Alarme e Segurança

| ID | Alarme | Condição | Ação Automática |
|:---|:---|:---|:---|
| AL-01 | **Queda de Fase** | $\lambda_2 < 0.8$ | Redução de torque nos motores. |
| AL-02 | **Invasão de Ruído** | Floor > -120 dBm/Hz | Desacoplamento da interface de rede. |
| AL-03 | **Febre de Silício** | Temp > 70°C | Ativação de resfriamento / Suspensão. |
