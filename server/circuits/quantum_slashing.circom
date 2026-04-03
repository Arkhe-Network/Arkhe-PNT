pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";
include "circomlib/gates.circom";

template QuantumSlashing() {
    // ============================================================
    // INPUTS PRIVADOS (Witness) - Dados do incidente
    // ============================================================

    // Identidade do nó (commitment, não o ID em claro)
    signal input node_commitment;
    signal input node_stake;              // Stake em tokens (escalado)

    // Métricas quânticas do incidente
    signal input t2_star_before;          // T₂* antes do incidente (μs × 1000)
    signal input t2_star_after;           // T₂* durante/depois (μs × 1000)
    signal input coherence_duration;      // Quanto tempo durou a falha (ms)
    signal input recovery_time;           // Tempo para recuperação (ms)

    // Provas de contexto
    signal input environmental_noise;     // Ruído ambiental medido (0-1000)
    signal input seismic_activity;        // Atividade sísmica (Richter × 100)
    signal input solar_flux_index;        // Índice de atividade solar (0-1000)
    signal input network_challenges_sent; // Desafios enviados ao nó
    signal input network_challenges_failed; // Desafios não respondidos

    // Histórico do nó
    signal input previous_slashings;      // Número de infrações anteriores
    signal input uptime_percentage;       // Uptime histórico (0-1000)

    // Nonce único do incidente
    signal input incident_salt;

    // ============================================================
    // INPUTS PÚBLICOS
    // ============================================================

    signal input threshold_t2_critical;   // Limiar crítico de T₂* (40000 = 40μs)
    signal input min_uptime_required;     // Uptime mínimo (950 = 95%)
    signal input max_recovery_time;       // Tempo máximo de recuperação (60000ms)
    signal input environmental_exemption; // Limiar de isenção ambiental (800)

    // ============================================================
    // OUTPUTS
    // ============================================================

    signal output slashing_valid;         // 1 se a penalidade é válida
    signal output slashing_severity;      // 0-3 (0=nenhuma, 1=leve, 2=severa, 3=ban)
    signal output penalty_amount;         // Tokens a serem queimados/slashados
    signal output incident_hash;          // Hash público do incidente
    signal output node_reputation_delta;  // Mudança na reputação (-100 a 0)

    // ============================================================
    // 1. CÁLCULO DA GRAVIDADE DA FALHA
    // ============================================================

    // Delta de coerência: quanto caiu T₂*
    signal t2_delta <== t2_star_before - t2_star_after;

    // Componente 1: Magnitude da perda de coerência
    component t2_critical = GreaterThan(64);
    t2_critical.in[0] <== threshold_t2_critical;
    t2_critical.in[1] <== t2_star_after;  // 1 se threshold > T2_after

    // Proper integer division for severity_raw
    signal severity_raw_numerator <== t2_critical.out * t2_delta * 1000;
    signal severity_raw;
    signal severity_raw_remainder;

    severity_raw <-- t2_star_before > 0 ? severity_raw_numerator / t2_star_before : 0;
    severity_raw_remainder <-- t2_star_before > 0 ? severity_raw_numerator % t2_star_before : 0;

    severity_raw_numerator === severity_raw * t2_star_before + severity_raw_remainder;

    component severity_raw_rem_bound = LessThan(64);
    severity_raw_rem_bound.in[0] <== severity_raw_remainder;
    severity_raw_rem_bound.in[1] <== t2_star_before + (1 - (t2_star_before > 0)); // handle div by zero logic
    severity_raw_rem_bound.out === 1;

    // Componente 2: Duração da falha
    component long_duration = GreaterThan(64);
    long_duration.in[0] <== coherence_duration;
    long_duration.in[1] <== 10000;  // > 10 segundos é grave

    signal duration_severity <== long_duration.out * 500;  // +50% severidade

    // Componente 3: Falha em desafios de rede
    signal challenge_num <== network_challenges_failed * 1000;
    signal challenge_den <== (network_challenges_sent + 1) * 2;
    signal challenge_severity;
    signal challenge_rem;

    component high_failure = GreaterThan(32);
    high_failure.in[0] <== network_challenges_failed * 1000;
    high_failure.in[1] <== 500 * (network_challenges_sent + 1);  // > 50% falha é grave

    challenge_severity <-- high_failure.out * challenge_num / challenge_den;
    challenge_rem <-- high_failure.out * challenge_num % challenge_den;
    high_failure.out * challenge_num === challenge_severity * challenge_den + challenge_rem;

    component challenge_rem_bound = LessThan(64);
    challenge_rem_bound.in[0] <== challenge_rem;
    challenge_rem_bound.in[1] <== challenge_den;
    challenge_rem_bound.out === 1;

    // ============================================================
    // 2. AVALIAÇÃO DE CULPABILIDADE (Natural vs. Malícia)
    // ============================================================

    signal environmental_stress <== environmental_noise + seismic_activity + solar_flux_index;

    component high_environmental = GreaterThan(32);
    high_environmental.in[0] <== environmental_stress;
    high_environmental.in[1] <== environmental_exemption * 3;

    signal environmental_mitigation <== high_environmental.out * 700;

    component fast_recovery = LessThan(64);
    fast_recovery.in[0] <== recovery_time;
    fast_recovery.in[1] <== max_recovery_time;

    signal recovery_mitigation <== fast_recovery.out * 300;

    component good_uptime = GreaterThan(32);
    good_uptime.in[0] <== uptime_percentage;
    good_uptime.in[1] <== min_uptime_required;

    signal reputation_mitigation <== good_uptime.out * 200;

    signal recidivism_penalty <== previous_slashings * 150;

    // ============================================================
    // 3. CÁLCULO FINAL DA SEVERIDADE
    // ============================================================

    signal raw_severity_sum <== severity_raw + duration_severity + challenge_severity + recidivism_penalty;

    signal total_mitigation <== environmental_mitigation + recovery_mitigation + reputation_mitigation;

    component underflow_check = GreaterThan(64);
    underflow_check.in[0] <== raw_severity_sum;
    underflow_check.in[1] <== total_mitigation;

    signal mitigated_severity <== underflow_check.out * (raw_severity_sum - total_mitigation);

    component is_severe = GreaterThan(32);
    is_severe.in[0] <== mitigated_severity;
    is_severe.in[1] <== 2000;

    component is_moderate = GreaterThan(32);
    is_moderate.in[0] <== mitigated_severity;
    is_moderate.in[1] <== 800;

    component is_minor = GreaterThan(32);
    is_minor.in[0] <== mitigated_severity;
    is_minor.in[1] <== 100;

    signal severity_1 <== is_minor.out * (1 - is_moderate.out) * 1;
    signal severity_2 <== is_moderate.out * (1 - is_severe.out) * 2;
    signal severity_3 <== is_severe.out * 3;

    slashing_severity <== severity_1 + severity_2 + severity_3;

    // ============================================================
    // 4. CÁLCULO DA PENALIDADE ECONÔMICA
    // ============================================================

    component s1 = IsEqual(); s1.in[0] <== slashing_severity; s1.in[1] <== 1;
    component s2 = IsEqual(); s2.in[0] <== slashing_severity; s2.in[1] <== 2;
    component s3 = IsEqual(); s3.in[0] <== slashing_severity; s3.in[1] <== 3;

    signal severity_factor <== s1.out * 50 + s2.out * 300 + s3.out * 1000;

    signal recidivism_multiplier <== 1000 + (previous_slashings * 200);

    // penalty_amount * 1000000 = node_stake * severity_factor * recidivism_multiplier
    signal penalty_num <== node_stake * severity_factor * recidivism_multiplier;
    signal penalty_final;
    penalty_final <-- penalty_num / 1000000;
    penalty_final * 1000000 === penalty_num;

    component penalty_cap = LessThan(64);
    penalty_cap.in[0] <== penalty_final;
    penalty_cap.in[1] <== node_stake;

    penalty_amount <== penalty_cap.out * penalty_final + (1 - penalty_cap.out) * node_stake;

    // ============================================================
    // 5. IMPACTO NA REPUTAÇÃO
    // ============================================================

    signal rep_impact <== s1.out * 5 + s2.out * 30 + s3.out * 100;
    node_reputation_delta <== 0 - rep_impact;

    // ============================================================
    // 6. VALIDAÇÃO E HASH DO INCIDENTE
    // ============================================================

    component actual_failure = GreaterThan(64);
    actual_failure.in[0] <== t2_delta;
    actual_failure.in[1] <== 5000;

    component has_severity = GreaterThan(32);
    has_severity.in[0] <== slashing_severity;
    has_severity.in[1] <== 0;

    slashing_valid <== actual_failure.out * has_severity.out;

    component incident_hasher = Poseidon(8);
    incident_hasher.inputs[0] <== node_commitment;
    incident_hasher.inputs[1] <== t2_star_before;
    incident_hasher.inputs[2] <== t2_star_after;
    incident_hasher.inputs[3] <== coherence_duration;
    incident_hasher.inputs[4] <== environmental_stress;
    incident_hasher.inputs[5] <== slashing_severity;
    incident_hasher.inputs[6] <== penalty_amount;
    incident_hasher.inputs[7] <== incident_salt;

    incident_hash <== incident_hasher.out;
}

component main {public [threshold_t2_critical, min_uptime_required, max_recovery_time, environmental_exemption]} = QuantumSlashing();
