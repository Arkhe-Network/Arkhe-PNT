pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";

template HydroBalanceProof() {
    // Inputs privados
    signal input private precipitation;      // mm (×1000)
    signal input private recharge;           // m³/s (×10^6)
    signal input private pumping;            // m³/s (×10^6)
    signal input private evapotranspiration; // mm (×1000)
    signal input private previousStorage;    // m³ (×1000)
    signal input private currentStorage;     // m³ (×1000)
    signal input private sensorSignature[2];
    signal input private salt;

    // Outputs públicos
    signal output massBalanceValid;
    signal output safetyCompliant;
    signal output integrityHash;
    signal output nullifier;

    // 1. Hash dos dados (autenticidade)
    component dataHasher = Poseidon(6);
    dataHasher.inputs[0] <== precipitation;
    dataHasher.inputs[1] <== recharge;
    dataHasher.inputs[2] <== pumping;
    dataHasher.inputs[3] <== evapotranspiration;
    dataHasher.inputs[4] <== currentStorage;
    dataHasher.inputs[5] <== salt;
    integrityHash <== dataHasher.out;

    // 2. Balanço de massa (conservação)
    signal precipContribution <== precipitation * 1000;
    signal totalInputs <== precipContribution + recharge;
    signal evapContribution <== evapotranspiration * 1000;
    signal totalOutputs <== pumping + evapContribution;
    signal deltaStorage <== currentStorage - previousStorage;
    signal theoreticalDelta <== totalInputs - totalOutputs;

    component diff = LessThan(64);
    diff.in[0] <== (deltaStorage - theoreticalDelta) * (deltaStorage - theoreticalDelta);
    diff.in[1] <== 1;  // erro quadrático < 1 → dentro do limiar
    massBalanceValid <== diff.out;

    // 3. Limites operacionais (segurança)
    component minLevel = GreaterThan(64);
    minLevel.in[0] <== currentStorage;
    minLevel.in[1] <== 10000;      // 10 m (mínimo)
    component maxLevel = LessThan(64);
    maxLevel.in[0] <== currentStorage;
    maxLevel.in[1] <== 100000;     // 100 m (máximo)
    component pumpingLimit = LessThan(64);
    pumpingLimit.in[0] <== pumping;
    pumpingLimit.in[1] <== 5000;   // 5 m³/s (limite sustentável)
    safetyCompliant <== minLevel.out * maxLevel.out * pumpingLimit.out;

    // 4. Nullifier (anti‑replay)
    component nullHasher = Poseidon(2);
    nullHasher.inputs[0] <== integrityHash;
    nullHasher.inputs[1] <== salt;
    nullifier <== nullHasher.out;
}

component main {public []} = HydroBalanceProof();
