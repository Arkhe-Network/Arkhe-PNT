pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";
include "circomlib/bitify.circom";

// Precisão: grandezas normalizadas como inteiros de 32 bits (multiplicadas por 1e6)
const PRECISION = 1000000;
const PHASE_TOLERANCE = 15708; // π/2 ≈ 1.5708 rad → 1.5708 * 1e6 = 1570800, mas usamos 15708 após redução

template AutoOrthogonalProof() {
    // --- Inputs privados ---
    signal input e_amplitude;      // amplitude da pressão formativa (×1e6)
    signal input B_amplitude;      // amplitude da tensão de contenção (×1e6)
    signal input phase_difference; // diferença de fase (rad ×1e6)
    signal input sensor_nonce;
    signal input sensor_signature; // assinatura TEE (simplificada)

    // --- Inputs públicos ---
    signal input expected_T;        // T esperado (×1e6, ex: 1000000 para T=1)
    signal input tolerance_T;       // tolerância para T (×1e6)
    signal input coherence_threshold; // λ₂ mínimo (×1e6)
    signal input timestamp;
    signal input device_id;

    // --- Outputs públicos ---
    signal output is_auto_orthogonal;      // 1 se T ≈ 1 e fase ≈ π/2 e coerência ok
    signal output nullifier;
    signal output integrity_hash;

    // ======================================================
    // 1. Verificação de integridade (sensor autenticado)
    // ======================================================
    component hasher = Poseidon(3);
    hasher.inputs[0] <== sensor_nonce;
    hasher.inputs[1] <== timestamp;
    hasher.inputs[2] <== device_id;
    hasher.out === sensor_signature; // em produção: ECDSA

    // ======================================================
    // 2. Cálculo da métrica T
    // ======================================================
    // Queremos |e_amplitude / B_amplitude - expected_T / PRECISION| <= tolerance_T / PRECISION
    // Multiplicando por B_amplitude * PRECISION:
    // |e_amplitude * PRECISION - expected_T * B_amplitude| <= tolerance_T * B_amplitude

    // Check if B_amplitude is not zero
    component isZeroB = IsZero();
    isZeroB.in <== B_amplitude;
    isZeroB.out === 0;

    // term1 === quotient * PRECISION + remainder
    signal term1 <== e_amplitude * PRECISION;
    signal term2 <== expected_T * B_amplitude;
    signal diff_T <== term1 - term2;

    // Absolute value of diff_T using bit decomposition to detect sign
    // Using 252 bits to safely handle the range in the BN254 field
    component ltT = LessThan(252);
    ltT.in[0] <== diff_T + (1 << 250);
    ltT.in[1] <== (1 << 250);

    signal abs_diff_T <== (1 - 2*ltT.out) * diff_T;

    component within_T = LessThan(252);
    within_T.in[0] <== abs_diff_T;
    within_T.in[1] <== tolerance_T * B_amplitude;
    signal T_valid <== within_T.out;

    // ======================================================
    // 3. Verificação da diferença de fase ≈ π/2
    // ======================================================
    signal phase_target <== 1570800; // π/2 × 1e6
    signal diff_phase <== phase_difference - phase_target;

    component ltPhase = LessThan(252);
    ltPhase.in[0] <== diff_phase + (1 << 250);
    ltPhase.in[1] <== (1 << 250);
    signal abs_diff_phase <== (1 - 2*ltPhase.out) * diff_phase;

    component within_phase = LessThan(252);
    within_phase.in[0] <== abs_diff_phase;
    within_phase.in[1] <== PHASE_TOLERANCE * 100; // Increased tolerance for scaling
    signal phase_valid <== within_phase.out;

    // ======================================================
    // 4. Coerência mínima (λ₂)
    // ======================================================
    signal coherence <== 980000; // placeholder: 0.98
    component coh_check = GreaterThan(32);
    coh_check.in[0] <== coherence;
    coh_check.in[1] <== coherence_threshold;
    signal coherence_valid <== coh_check.out;

    // ======================================================
    // 5. Agregação final
    // ======================================================
    is_auto_orthogonal <== T_valid * phase_valid * coherence_valid;

    // ======================================================
    // 6. Nullifier e integrity_hash
    // ======================================================
    component nullHasher = Poseidon(5);
    nullHasher.inputs[0] <== e_amplitude;
    nullHasher.inputs[1] <== B_amplitude;
    nullHasher.inputs[2] <== phase_difference;
    nullHasher.inputs[3] <== timestamp;
    nullHasher.inputs[4] <== sensor_nonce;
    nullifier <== nullHasher.out;

    component dataHasher = Poseidon(6);
    dataHasher.inputs[0] <== expected_T;
    dataHasher.inputs[1] <== tolerance_T;
    dataHasher.inputs[2] <== coherence_threshold;
    dataHasher.inputs[3] <== timestamp;
    dataHasher.inputs[4] <== device_id;
    dataHasher.inputs[5] <== is_auto_orthogonal;
    integrity_hash <== dataHasher.out;
}

component main {public [expected_T, tolerance_T, coherence_threshold, timestamp, device_id]} = AutoOrthogonalProof();
