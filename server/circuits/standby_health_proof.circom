pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";
include "circomlib/bitify.circom";

// StandbyHealthProof: Prova de que um nó standby mantém coerência T2*
// na zona de saúde sem comprometer a zona de emaranhamento.
template StandbyHealthProof() {
    // Inputs privados (Witness)
    signal input ramsey_fringes[8];    // Amplitudes de fluorescência normalizadas (x1000)
    signal input calibration_a;        // Coeficiente angular do modelo (x1000)
    signal input calibration_b;        // Coeficiente linear do modelo (x1000)
    signal input sensor_nonce;
    signal input timestamp;

    // Inputs públicos
    signal input t2_threshold;         // Limiar de saúde (ex: 45000 para 45μs)
    signal input min_confidence;       // Confiança mínima exigida (x1000)
    signal input attested_fringes_hash;// Hash das medições assinado pelo TEE

    // Outputs públicos
    signal output is_healthy;          // 1 se T2* > threshold
    signal output nullifier;           // Previne replay
    signal output commitment;          // Hash do estado de saúde

    // 1. Cálculo simplificado de T2* a partir das Ramsey fringes
    signal t2_measured;
    var sum = 0;
    for (var i = 0; i < 8; i++) {
        sum += ramsey_fringes[i] * (i + 1) * 10;
    }

    // t2_measured = sum / 8
    signal t2_q;
    signal t2_r;
    t2_q <-- sum / 8;
    t2_r <-- sum % 8;
    sum === t2_q * 8 + t2_r;

    component t2_rem_check = LessThan(32);
    t2_rem_check.in[0] <== t2_r;
    t2_rem_check.in[1] <== 8;
    t2_rem_check.out === 1;

    t2_measured <== t2_q;

    // 2. Aplicar modelo de calibração para inferir T2* da zona principal
    // T2_main = (calibration_a * T2_measured) / 1000 + calibration_b
    signal main_num <== calibration_a * t2_measured;
    signal main_q;
    signal main_r;
    main_q <-- main_num / 1000;
    main_r <-- main_num % 1000;
    main_num === main_q * 1000 + main_r;

    component main_rem_check = LessThan(64);
    main_rem_check.in[0] <== main_r;
    main_rem_check.in[1] <== 1000;
    main_rem_check.out === 1;

    signal t2_main <== main_q + calibration_b;

    // 3. Verificação de Saúde
    component healthCheck = GreaterThan(64);
    healthCheck.in[0] <== t2_main;
    healthCheck.in[1] <== t2_threshold;
    is_healthy <== healthCheck.out;

    // 4. Verificação de Proveniência (Simulada)
    component proofHasher = Poseidon(8);
    for(var i=0; i<8; i++) { proofHasher.inputs[i] <== ramsey_fringes[i]; }
    proofHasher.out === attested_fringes_hash;

    // 5. Nullifier e Commitment
    component nullHasher = Poseidon(3);
    nullHasher.inputs[0] <== sensor_nonce;
    nullHasher.inputs[1] <== timestamp;
    nullHasher.inputs[2] <== t2_main;
    nullifier <== nullHasher.out;

    component commitHasher = Poseidon(4);
    commitHasher.inputs[0] <== is_healthy;
    commitHasher.inputs[1] <== timestamp;
    commitHasher.inputs[2] <== t2_threshold;
    commitHasher.inputs[3] <== attested_fringes_hash;
    commitment <== commitHasher.out;
}

component main {public [t2_threshold, min_confidence, attested_fringes_hash]} = StandbyHealthProof();
