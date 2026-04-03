pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";

// alpha_calculator.circom - Cálculo dinâmico do limiar de governança (alpha)
template AlphaCalculator() {
    // Inputs de contexto
    signal input globalThreatLevel;      // 0-100 (de feeds de inteligência)
    signal input networkCoherence;       // R(t) do Kuramoto (0-1000)
    signal input recentSlashingEvents;   // Número de penalidades recentes
    signal input regulatoryPressure;     // 0-100 (indicadores externos)

    // Parâmetros históricos
    signal input avgTransactionValue;    // Valor médio das transações recentes

    // Output
    signal output alpha;                 // 0-1000 (representa 0.0 a 1.0)
    signal output regime;                // 0=transparent, 1=balanced, 2=private

    // ============================================================
    // LÓGICA DE CÁLCULO DE α
    // ============================================================

    // Componente de ameaça: α aumenta com ameaça (mais privacidade)
    signal threatComponent <== globalThreatLevel * 10;  // 0-1000

    // Componente de coerência: α diminui com coerência (mais transparência)
    signal coherenceComponent <== (1000 - networkCoherence) * 5;  // 0-5000

    // Componente de slashing: α aumenta se houver abuso recente
    signal slashingComponent <== recentSlashingEvents * 100;  // 0-1000+

    // Componente regulatório: α diminui sob pressão (compliance)
    signal regulatoryComponent <== (100 - regulatoryPressure) * 3;  // 0-300

    // Componente de valor: α aumenta com valor médio (proteção)
    signal logValue;
    // Aproximação linear por faixas para o circuito ZK
    component v1 = GreaterThan(32); v1.in[0] <== avgTransactionValue; v1.in[1] <== 1000000;
    component v2 = GreaterThan(32); v2.in[0] <== avgTransactionValue; v2.in[1] <== 100000;
    component v3 = GreaterThan(32); v3.in[0] <== avgTransactionValue; v3.in[1] <== 10000;

    logValue <== v1.out * 1000 + (1 - v1.out) * (v2.out * 700 + (1 - v2.out) * (v3.out * 400 + (1 - v3.out) * 100));

    // Soma ponderada
    signal rawAlphaNumerator <== threatComponent * 3 +
                coherenceComponent * 2 +
                slashingComponent * 4 +
                regulatoryComponent * 1 +
                logValue * 2;

    // Replacing division with proper integer division (quotient and remainder)
    signal normalizedAlpha;
    signal normalizedAlphaRemainder;

    normalizedAlpha <-- rawAlphaNumerator / 12;
    normalizedAlphaRemainder <-- rawAlphaNumerator % 12;

    rawAlphaNumerator === normalizedAlpha * 12 + normalizedAlphaRemainder;

    component alphaRemBound = LessThan(32);
    alphaRemBound.in[0] <== normalizedAlphaRemainder;
    alphaRemBound.in[1] <== 12;
    alphaRemBound.out === 1;

    // Limites de saturação
    component alphaCap = LessThan(32);
    alphaCap.in[0] <== normalizedAlpha;
    alphaCap.in[1] <== 1000;

    alpha <== alphaCap.out * normalizedAlpha + (1 - alphaCap.out) * 1000;

    // ============================================================
    // DETERMINAÇÃO DO REGIME
    // ============================================================

    component isTransparent = LessThan(32);
    isTransparent.in[0] <== alpha;
    isTransparent.in[1] <== 250;  // α < 0.25

    component isBalanced = LessThan(32);
    isBalanced.in[0] <== alpha;
    isBalanced.in[1] <== 750;  // α < 0.75

    // regime = 0 se transparent, 1 se balanced, 2 se private
    signal isNotTransparent <== 1 - isTransparent.out;
    signal isPrivate <== 1 - isBalanced.out;

    regime <== isTransparent.out * 0 +
              isNotTransparent * isBalanced.out * 1 +
              isNotTransparent * isPrivate * 2;
}

component main {public [globalThreatLevel, networkCoherence, recentSlashingEvents, regulatoryPressure]} = AlphaCalculator();
