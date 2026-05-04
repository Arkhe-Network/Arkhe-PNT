# Protocolo: Medição de G_info (Genetic Information Fidelity)

## 1. Definição
G_info representa a **Fidelidade da Informação Genética** (Genetic Information Fidelity) em sistemas de terapia gênica quântico-biológica. No contexto Arkhe-Ω Rio, G_info é o parâmetro que correlaciona a integridade da sequência OTOF com o índice de coerência coclear (λ₂).

## 2. Metodologia de Medição
O G_info é medido através de um processo de **Commitment e Verificação**:

1. **Commitment (ZK)**: O paciente gera um hash da sequência genética (`geneticHash`) e um `nullifier` usando o circuito **OTOFEligibilityProof**.
2. **Phase Mapping**: O sensor Brillouin (674 nm) excita o sistema coclear.
3. **Coherence Readout**: O `PhaseGradientRedistributor` calcula a coerência global λ₂ em tempo real.
4. **Fidelity Calculation**: G_info = λ₂ × P(mutação | hash).

## 3. Limiares de Operação
| G_info | Categoria | Ação |
|---|---|---|
| > 0.95 | **Quantum Stable** | Procedimento autorizado, payout $RIO liberado. |
| 0.85 - 0.95 | **Nominal Recovery** | Monitoramento quinzenal sugerido. |
| 0.70 - 0.85 | **Compromised** | Re-intervenção ou ajuste de parâmetro TMS. |
| < 0.70 | **Decoherent** | Abortar sessão; auditoria de segurança obrigatória. |

## 4. Integração Smart Contract
Os valores de G_info são reportados ao contrato `TimechainPhase` através de `coherenceProof`. O contrato atua como o **Filtro de Kalman Final**, filtrando ruído termodinâmico de sinais de recuperação real.

## 5. Proteção de Soberania Biológica
A medição de G_info nunca expõe a sequência bruta. Apenas o hash e o status de coerência são compartilhados com o sistema de governança Arkhe.
