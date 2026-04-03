pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";
include "circomlib/bitify.circom";
include "circomlib/gates.circom";

template FrustrationProof() {
    // ============================================================
    // INPUTS PRIVADOS (Witness) - Dados da sessão
    // ============================================================

    // Sequência temporal de eventos (últimos 60 segundos)
    signal input click_timestamps[100];      // Timestamps em ms
    signal input click_positions[100][2];    // Coordenadas x,y normalizadas (0-1000)
    signal input scroll_velocities[50];      // Velocidade de scroll (pixels/ms)
    signal input key_intervals[50];          // Intervalos entre teclas (ms)

    // Métricas comportamentais
    signal input mouse_distance_traveled;    // Distância total do mouse (pixels)
    signal input time_on_page;               // Tempo na página (ms)
    signal input form_corrections;           // Número de correções em formulários

    // Nonce e identificador
    signal input session_salt;
    signal input user_did_commitment;        // Commitment do DID (não o DID em si)

    // ============================================================
    // INPUTS PÚBLICOS
    // ============================================================

    signal input min_human_typing_interval;  // 50ms (limite fisiológico)
    signal input max_bot_consistency;        // 0.95 (bots são muito consistentes)
    signal input frustration_threshold;      // 0.7 (score para considerar frustrado)

    // ============================================================
    // OUTPUTS
    // ============================================================

    signal output isHuman;                   // 1 se padrão é humano
    signal output isFrustrated;              // 1 se frustrado
    signal output frustrationScore;          // 0-1000 (normalizado)
    signal output sessionNullifier;          // Previne replay de sessões

    // ============================================================
    // 1. DETECÇÃO DE HUMANIDADE (Anti-Bot)
    // ============================================================

    // 1.1 Teste de entropia temporal (humanos são irregulares)
    component varianceCheck[99];
    signal varianceCheckOut[99];
    var tempVarSum = 0;
    for (var i = 1; i < 100; i++) {
        varianceCheck[i] = GreaterThan(32);
        varianceCheck[i].in[0] <== click_timestamps[i] - click_timestamps[i-1];
        varianceCheck[i].in[1] <== 0;  // Verifica variabilidade
        varianceCheckOut[i-1] <== varianceCheck[i].out;
    }

    signal varianceSum;
    var sV = 0;
    for (var i=0; i<99; i++) { sV += varianceCheckOut[i]; }
    varianceSum <== sV;

    // 1.2 Teste de curvatura de movimento (humanos fazem curvas suaves)
    component curvatureCheck[98];
    signal curvatureCheckOut[98];
    for (var i = 2; i < 100; i++) {
        signal dx1 <== click_positions[i-1][0] - click_positions[i-2][0];
        signal dy1 <== click_positions[i-1][1] - click_positions[i-2][1];
        signal dx2 <== click_positions[i][0] - click_positions[i-1][0];
        signal dy2 <== click_positions[i][1] - click_positions[i-1][1];

        signal cross <== dx1 * dy2 - dy1 * dx2;

        curvatureCheck[i-2] = GreaterThan(32);
        curvatureCheck[i-2].in[0] <== cross * cross;  // cross^2 como proxy
        curvatureCheck[i-2].in[1] <== 100;  // Threshold de curvatura
        curvatureCheckOut[i-2] <== curvatureCheck[i-2].out;
    }

    signal curvatureSum;
    var sC = 0;
    for (var i=0; i<98; i++) { sC += curvatureCheckOut[i]; }
    curvatureSum <== sC;

    // 1.3 Teste de intervalo de digitação (limite fisiológico)
    component typingCheck[50];
    signal typingCheckOut[50];
    for (var i = 0; i < 50; i++) {
        typingCheck[i] = GreaterThan(32);
        typingCheck[i].in[0] <== key_intervals[i];
        typingCheck[i].in[1] <== min_human_typing_interval;
        typingCheckOut[i] <== typingCheck[i].out;
    }

    signal sumValidIntervals;
    var sT = 0;
    for (var i=0; i<50; i++) { sT += typingCheckOut[i]; }
    sumValidIntervals <== sT;

    component humanTyping = GreaterThan(32);
    humanTyping.in[0] <== sumValidIntervals;
    humanTyping.in[1] <== 35;  // Pelo menos 35/50 intervalos válidos

    // 1.4 Score composto de humanidade
    // Proper integer division: numerator === quotient * denominator + remainder
    signal humanScoreNumerator <== varianceSum * 10 + curvatureSum * 10 + humanTyping.out * 1000;
    signal humanScoreFinal;
    signal humanScoreRemainder;

    humanScoreFinal <-- humanScoreNumerator / 248;
    humanScoreRemainder <-- humanScoreNumerator % 248;

    humanScoreNumerator === humanScoreFinal * 248 + humanScoreRemainder;

    component humanScoreBound = LessThan(32);
    humanScoreBound.in[0] <== humanScoreRemainder;
    humanScoreBound.in[1] <== 248;
    humanScoreBound.out === 1;

    component humanThreshold = GreaterThan(32);
    humanThreshold.in[0] <== humanScoreFinal;
    humanThreshold.in[1] <== 600;  // Threshold 60% humanidade
    isHuman <== humanThreshold.out;

    // ============================================================
    // 2. DETECÇÃO DE FRUSTRAÇÃO
    // ============================================================

    // 2.1 Rage clicks (cliques rápidos no mesmo local)
    component timeClose[99];
    component distClose[99];
    component rageAnd[99];
    signal rageCheckOut[99];
    for (var i = 1; i < 100; i++) {
        signal timeDiff <== click_timestamps[i] - click_timestamps[i-1];
        signal dx <== click_positions[i][0] - click_positions[i-1][0];
        signal dy <== click_positions[i][1] - click_positions[i-1][1];
        signal distSq <== dx * dx + dy * dy;

        timeClose[i-1] = LessThan(32);
        timeClose[i-1].in[0] <== timeDiff;
        timeClose[i-1].in[1] <== 300;

        distClose[i-1] = LessThan(32);
        distClose[i-1].in[0] <== distSq;
        distClose[i-1].in[1] <== 100;  // 10^2

        rageAnd[i-1] = AND();
        rageAnd[i-1].a <== timeClose[i-1].out;
        rageAnd[i-1].b <== distClose[i-1].out;
        rageCheckOut[i-1] <== rageAnd[i-1].out;
    }

    signal rageClickCount;
    var sR = 0;
    for (var i=0; i<99; i++) { sR += rageCheckOut[i]; }
    rageClickCount <== sR;

    // 2.2 Scroll errático (mudanças rápidas de direção)
    component scrollChecks[49];
    component velNeg[49];
    signal scrollCheckOut[49];
    for (var i = 1; i < 50; i++) {
        signal velChange <== scroll_velocities[i] - scroll_velocities[i-1];

        velNeg[i-1] = LessThan(32);
        velNeg[i-1].in[0] <== velChange + (1 << 31);
        velNeg[i-1].in[1] <== (1 << 31);

        signal negVelChange <== 0 - velChange;
        signal absVelChange <== velNeg[i-1].out * negVelChange + (1 - velNeg[i-1].out) * velChange;

        scrollChecks[i-1] = GreaterThan(32);
        scrollChecks[i-1].in[0] <== absVelChange;
        scrollChecks[i-1].in[1] <== 500;  // pixels/ms^2
        scrollCheckOut[i-1] <== scrollChecks[i-1].out;
    }

    signal erraticScrollCount;
    var sS = 0;
    for (var i=0; i<49; i++) { sS += scrollCheckOut[i]; }
    erraticScrollCount <== sS;

    signal correctionScore <== form_corrections * 100;
    signal rawFrustration <== rageClickCount * 50 + erraticScrollCount * 30 + correctionScore;

    component capFrustration = LessThan(32);
    capFrustration.in[0] <== rawFrustration;
    capFrustration.in[1] <== 1000;

    frustrationScore <== capFrustration.out * rawFrustration + (1 - capFrustration.out) * 1000;

    component frustrationThresholdC = GreaterThan(32);
    frustrationThresholdC.in[0] <== frustrationScore;
    frustrationThresholdC.in[1] <== frustration_threshold * 1000;

    isFrustrated <== frustrationThresholdC.out * isHuman;

    // ============================================================
    // 3. INTEGRIDADE E NULLIFIER
    // ============================================================

    component sessionHasher = Poseidon(5);
    sessionHasher.inputs[0] <== user_did_commitment;
    sessionHasher.inputs[1] <== session_salt;
    sessionHasher.inputs[2] <== humanScoreFinal;
    sessionHasher.inputs[3] <== frustrationScore;
    sessionHasher.inputs[4] <== time_on_page;

    component nullifierHasher = Poseidon(2);
    nullifierHasher.inputs[0] <== sessionHasher.out;
    nullifierHasher.inputs[1] <== session_salt;

    sessionNullifier <== nullifierHasher.out;
}

component main {public [min_human_typing_interval, max_bot_consistency, frustration_threshold]} = FrustrationProof();
