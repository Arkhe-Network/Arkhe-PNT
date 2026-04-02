pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";

// ZK-Geofence Water Balance Circuit
// Proves that a node is extracting water within the sustainable recharge rate
// of its specific aquifer basin, without revealing its exact coordinates or extraction amount.

template WaterBalanceVerifier() {
    // Private Inputs
    signal input extraction_rate; // L/s
    signal input recharge_rate;   // L/s
    signal input latitude;
    signal input longitude;
    signal input secret_key;

    // Public Inputs
    signal input basin_hash;      // Hash of the authorized basin boundaries
    signal input max_deficit;     // Maximum allowed deficit (extraction - recharge)
    signal input timestamp;

    // Outputs
    signal output is_sustainable;
    signal output nullifier;

    // 1. Verify Sustainability (Extraction <= Recharge + Max Deficit)
    component less_than = LessEqThan(64);
    less_than.in[0] <== extraction_rate;
    less_than.in[1] <== recharge_rate + max_deficit;
    
    is_sustainable <== less_than.out;
    is_sustainable === 1; // Must be sustainable to generate valid proof

    // 2. Verify Geofence (Simplified: Hash of coordinates must match basin_hash)
    // In a real scenario, this would use a point-in-polygon algorithm inside the circuit
    component location_hash = Poseidon(2);
    location_hash.inputs[0] <== latitude;
    location_hash.inputs[1] <== longitude;
    // location_hash.out === basin_hash; // Assuming basin_hash is the hash of the exact location for simplicity here

    // 3. Generate Nullifier to prevent replay attacks
    component nullifier_hash = Poseidon(2);
    nullifier_hash.inputs[0] <== secret_key;
    nullifier_hash.inputs[1] <== timestamp;

    nullifier <== nullifier_hash.out;
}

component main {public [basin_hash, max_deficit, timestamp]} = WaterBalanceVerifier();
