# Protocolo: Terapia Gênica OTOF & Sensor de Coerência Auditiva Brillouin

## 1. Visão Geral
Este protocolo descreve a integração da terapia gênica para surdez congênita (mutação OTOF) no ecossistema Arkhe-Ω Rio. A intervenção utiliza vetores AAV para restaurar a produção de otoferlina, atuando como um transdutor de fase coclear.

## 2. Especificações do Sensor Brillouin (674 nm)
O sensor emula o monitoramento da resposta auditiva de tronco cerebral (BERA) correlacionado com excitação laser.

| Componente | Especificação | Função |
|------------|---------------|--------|
| **Fonte Óptica** | Laser Brillouin (674 nm) | Excitação de fase controlada |
| **Processador** | FPGA + `PhaseGradientRedistributor` | Cálculo de λ₂ em tempo real |
| **Alvo** | Membrana Timpânica / Nervo Auditivo | Detecção de coerência sensorial |

## 3. Parâmetros Clínicos
- **Threshold Basal**: 80-110 dB.
- **Janela Terapêutica**: Recuperação observada em 4-12 semanas.
- **Métrica de Sucesso**: λ₂ > 0.85 (Coerência Estabilizada).

## 4. Governança e Subsídio (Smart Contracts)
A gestão financeira do protocolo é automatizada via Arkhe-Chain utilizando o token **$RIO**.

### 4.1 Arquitetura de Contratos
| Contrato | Função |
|----------|--------|
| **RIOToken** | Token ERC-20 para pagamentos e governança da Cidade-Estado. |
| **PatientRegistry** | Registro anônimo de elegibilidade (hash genético + consentimento). |
| **SubsidyManager** | Orquestração de solicitações e desembolso multi-sig (3/5). |
| **RioGovernor** | DAO para votação de parâmetros (ex: % de subsídio, idade limite). |

### 4.2 Fluxo de Desembolso
1. **Inscrição**: Médico registra o paciente no `PatientRegistry`.
2. **Aprovação Ética**: EQBE valida o consentimento digital.
3. **Solicitação**: Tutor solicita o subsídio (padrão 80%) via `SubsidyManager`.
4. **Consenso**: Comitê multi-sig (médicos + bioética) aprova a transação.
5. **Liquidação**: Mintagem de $RIO para a carteira do paciente/clínica.

## 5. Diretrizes Éticas (EQBE)
1. **Acesso Universal**: Subvenção integral para cidadãos de baixa renda via tesouro da DAO.
2. **Limite de Melhoramento**: Restrição de ganho auditivo ao limiar normal (ISO 20dB).
3. **Soberania de Dados**: Registro obrigatório de marcos de coerência (λ₂) na Arkhe-Chain.

## 6. Implementação Técnica
- **Simulação**: `skills/archimedes-omega/skills.py` (API: `/therapy/otof/simulate`).
- **Firmware**: `contracts/*.sol` (Solidy 0.8.20).
