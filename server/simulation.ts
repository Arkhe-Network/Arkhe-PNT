import { state, updateState, tzinorStore, generateOrbId } from "./state";

let lastTriggeredThreshold: number | null = null;

export function runSimulationTick(broadcastState: () => void) {
  const now = Date.now();
  const isAttack = Math.random() < 0.08; // 8% chance of attack/anomaly per tick
  const isOngoingAttack = state.threatLevel !== 'normal';
  
  let newLambda = state.currentLambda;
  let newThreatLevel = state.threatLevel;
  let newActiveThreat = state.activeThreat;
  let newMetrics = { ...state.metrics };
  let newMitigation = { ...state.mitigation };
  let newLogs = [...state.logs];
  let newShards = [...state.shards];
  let newThermo = { ...state.thermodynamics };
  let newTopology = { ...state.topology };
  let newHardware = { ...state.hardware };
  let newSecurity = { ...state.security };
  let newSecurityAdvanced = { ...state.securityAdvanced };
  let newRamsey = { ...state.ramsey };
  let newCHSH = { ...state.chshMonitor };

  // CHSH Live Telemetry Simulation
  if (newCHSH.status === 'ACTIVATED') {
    newCHSH.liveTelemetry.dataPoints += 1;

    // Simulate S value calculation approaching the target 2.82
    // We start with some noise and converge
    const currentS = newCHSH.liveTelemetry.currentS === null ? 2.0 : newCHSH.liveTelemetry.currentS;
    const targetS = 2.8284;
    const drift = (targetS - currentS) * 0.05;
    const noise = (Math.random() - 0.5) * 0.02;
    newCHSH.liveTelemetry.currentS = Math.min(2.8284, currentS + drift + noise);

    const timeStr = new Date().toLocaleTimeString('en-US', { hour12: false, second: '2-digit', minute: '2-digit' });
    newCHSH.liveTelemetry.history = [...(newCHSH.liveTelemetry.history || []), { time: timeStr, s: newCHSH.liveTelemetry.currentS }].slice(-20);

    if (newCHSH.liveTelemetry.dataPoints > 30) {
      newCHSH.liveTelemetry.stabilityIndicator = "SUPER-STABLE";
      newCHSH.archimedesComment = "Emaranhamento biológico confirmado. O array Bexorg 3.0 demonstra violação de Bell S > 2.80.";
    }
  }

  // Ramsey Sweep Logic
  if (newRamsey.enabled && !newRamsey.isFrozen) {
    const sweepSpeed = 0.002;
    newRamsey.theta += newRamsey.direction * sweepSpeed;

    // Reverse direction at boundaries (0 to PI)
    if (newRamsey.theta > Math.PI) {
      newRamsey.theta = Math.PI;
      newRamsey.direction = -1;
    } else if (newRamsey.theta < 0) {
      newRamsey.theta = 0;
      newRamsey.direction = 1;
    }

    // Add to sliding window (max 5 points as per spec)
    newRamsey.window = [...newRamsey.window, { theta: newRamsey.theta, coherence: newLambda }].slice(-5);

    // Peak Detection Logic
    let thresholdFound = false;
    for (const threshold of newRamsey.thresholds) {
      if (Math.abs(newRamsey.theta - threshold.angle_rad) <= threshold.tolerance) {
        thresholdFound = true;
        // Simple peak check: current coherence > baseline * min_gain
        // and latch to prevent multiple triggers per pass
        if (newLambda > newRamsey.baseline * threshold.min_gain && lastTriggeredThreshold !== threshold.angle_rad) {
          lastTriggeredThreshold = threshold.angle_rad;
          // Trigger action
          if (threshold.action === 'LOCAL_ADJUST') {
            newLogs.unshift({
              id: generateOrbId(),
              originTime: now,
              targetTime: now,
              coherence: newLambda,
              status: 'Valid',
              threatType: `RAMSEY_PEAK: LOCAL_ADJUST at ${threshold.angle_rad.toFixed(4)} rad. Pulso: 157.1 fs`
            });
            // Simulate local adjust effect
            newLambda = Math.min(1.0, newLambda + 0.01);
          } else if (threshold.action === 'LOG_ONLY') {
            newLogs.unshift({
              id: generateOrbId(),
              originTime: now,
              targetTime: now,
              coherence: newLambda,
              status: 'Valid',
              threatType: `RAMSEY_PEAK: LOG_ONLY at ${threshold.angle_rad.toFixed(4)} rad.`
            });
          } else if (threshold.action === 'LOCAL_ADJUST_NOTIFY') {
            newLogs.unshift({
              id: generateOrbId(),
              originTime: now,
              targetTime: now,
              coherence: newLambda,
              status: 'Valid',
              threatType: `RAMSEY_PEAK: NOTIFY at ${threshold.angle_rad.toFixed(4)} rad. Pulso: 157.1 fs`
            });
            // Execute LOCAL_ADJUST effect (as per spec: executes LOCAL_ADJUST + notify)
            newLambda = Math.min(1.0, newLambda + 0.01);
          } else if (threshold.action === 'GLOBAL_ADJUST') {
            // Trigger Fibonacci injection if it's the pi/5 peak
            if (Math.abs(threshold.angle_rad - 0.6283) < 0.001) {
              newRamsey.isFrozen = true;
              const expiresAt = new Date(now + 30000).toISOString();
              newRamsey.pendingAction = {
                id: generateOrbId(),
                type: 'GLOBAL_ADJUST',
                angle: newRamsey.theta,
                coherence: newLambda,
                timestamp: new Date(now).toISOString(),
                expiresAt: expiresAt
              };

              newLogs.unshift({
                id: generateOrbId(),
                originTime: now,
                targetTime: now,
                coherence: newLambda,
                status: 'Valid',
                threatType: 'RAMSEY: Injeção de Fase Fibonacci (π/5) Detectada. Aguardando aprovação.'
              });
            }
          }
        }
      }
    }


    if (!thresholdFound) {
      lastTriggeredThreshold = null;
    }
  }

  // Handle Manual Confirmation Timeout (30s) - Moved outside the !isFrozen block
  if (newRamsey.pendingAction) {
    const expiresAt = new Date(newRamsey.pendingAction.expiresAt).getTime();
    if (now >= expiresAt) {
      newLogs.unshift({
        id: generateOrbId(),
        originTime: now,
        targetTime: now,
        coherence: newLambda,
        status: 'Valid',
        threatType: 'RAMSEY: Confirmation Timeout. Automatic execution applied.'
      });

      // Automatic execution logic (e.g., execute and unfreeze)
      newRamsey.isFrozen = false;
      newRamsey.pendingAction = null;
      newLambda = Math.min(1.0, newLambda + 0.05); // Simulate recovery
    }
  }

  // Base noise
  newLambda = Math.min(1.0, Math.max(0.0, newLambda + (Math.random() - 0.5) * 0.05));
  newMetrics.musd = Math.max(0, newMetrics.musd + (Math.random() - 0.5) * 0.05);
  newMetrics.musda = newMetrics.musd * 0.8;
  newMetrics.wmaBc = (newMetrics.musd + newMetrics.musda) / 2;
  newMitigation.kuramotoSyncPhase = (newMitigation.kuramotoSyncPhase + (0.1 * state.parameters.couplingStrength * 2)) % (2 * Math.PI);
  
  // Hardware fluctuations
  newHardware.segPower = 280 + Math.random() * 10;
  newHardware.fpgaUtilization = 46 + Math.random() * 2;

  // Security Advanced Base Fluctuations
  newSecurityAdvanced.l2.qrngJitterMs = 15 + (Math.random() - 0.5) * 4;
  newSecurityAdvanced.l3.t2StarMicroseconds = 50 + Math.random() * 5;
  newSecurityAdvanced.l4.logosConsistency = Math.min(1.0, 0.98 + Math.random() * 0.02);
  newSecurityAdvanced.qhttp.bellViolationS = 2.0 + Math.random() * 0.82;

  if (isAttack && !isOngoingAttack) {
    // Initiate attack
    const attackTypes = [
      'Time Shift', 'Jamming', 'Data Spoofing', 'BGP Jitter', 'Quantum Shor', 'SEU Radiation',
      'Phase Spoofing', 'Ontology Injection', 'Sybil Attack', 'Replay Attack'
    ];
    newActiveThreat = attackTypes[Math.floor(Math.random() * attackTypes.length)];
    newThreatLevel = 'critical';
    
    if (newActiveThreat === 'Jamming') {
      newLambda = 0.3 + Math.random() * 0.2;
      newMetrics.musd = 0.8 + Math.random() * 0.4;
      newMitigation.nullSteeringActive = state.parameters.autoMitigate;
      
      const shardsToCorrupt = 4 + Math.floor(Math.random() * 6);
      let corruptedCount = 0;
      newShards = newShards.map(s => {
        if (corruptedCount < shardsToCorrupt && Math.random() > 0.5) {
          corruptedCount++;
          return { ...s, status: 'corrupted' };
        }
        return s;
      });
      newMitigation.tzinorShardsAvailable = 24 - corruptedCount;
    } else if (newActiveThreat === 'Time Shift' || newActiveThreat === 'BGP Jitter') {
      newLambda = 0.5 + Math.random() * 0.1;
      newMetrics.musd = 0.6 + Math.random() * 0.2;
      newTopology.yangBaxterValid = false; // Topological violation
      newTopology.handshakeSuccessRate = 45.2 + Math.random() * 10;
    } else if (newActiveThreat === 'Data Spoofing' || newActiveThreat === 'Quantum Shor') {
      newLambda = 0.6 + Math.random() * 0.1;
      newSecurity.zkProofValid = false; // ZK Proof fails
      newHardware.fpgaUtilization = 85.0 + Math.random() * 10; // High load verifying bad proofs
    } else if (newActiveThreat === 'SEU Radiation') {
      newHardware.tmrFaultsCorrected += Math.floor(Math.random() * 5) + 1;
      newLambda = 0.7 + Math.random() * 0.1;
    } else if (newActiveThreat === 'Phase Spoofing') {
      newSecurityAdvanced.l2.eprHandshake = 'failed';
      newSecurityAdvanced.l2.pneumaOutlierDetected = true;
      newSecurityAdvanced.qhttp.bellViolationS = 1.5 + Math.random() * 0.4; // Classically explained
      newLambda = 0.4 + Math.random() * 0.2;
    } else if (newActiveThreat === 'Ontology Injection') {
      newSecurityAdvanced.l4.owlSignatureValid = false;
      newSecurityAdvanced.l4.logosConsistency = 0.4 + Math.random() * 0.2;
      newLambda = 0.6 + Math.random() * 0.1;
    } else if (newActiveThreat === 'Sybil Attack') {
      newSecurityAdvanced.l2.muSig2Heartbeat = 'unverified';
      newHardware.fpgaUtilization = 90.0 + Math.random() * 5;
      newLambda = 0.5 + Math.random() * 0.1;
    } else if (newActiveThreat === 'Replay Attack') {
      newSecurityAdvanced.l3.nullifierVerified = false;
      newSecurityAdvanced.l3.ttlValid = false;
      newLambda = 0.55 + Math.random() * 0.1;
    } else {
      newLambda = 0.7 + Math.random() * 0.1;
    }

    // Add bad log
    const newLogId = generateOrbId();
    newLogs.unshift({
      id: newLogId,
      originTime: newActiveThreat === 'Time Shift' ? now + 3600000 : now - 100,
      targetTime: now,
      coherence: newLambda,
      status: state.parameters.autoMitigate ? 'Rejected' : 'Valid',
      threatType: newActiveThreat,
    });

    // Evolve Tzinor state
    tzinorStore.evolve({
      id: newLogId,
      originTime: now,
      coherence: newLambda,
      embedding: Array.from({ length: 8 }, () => Math.random() * 2 - 1),
      industry_convergence: {
        arkhe_version: "4.0",
        cortex_alignment: "context-as-state",
        hardware_basis: "Ma-Patterson-2026",
        unified_architecture: "Kaluza-Klein-5D",
        visual_basic_com_interop: "Active",
        industrial_scada_layer: "Siemens/Rockwell PLC"
      }
    });

  } else if (isOngoingAttack) {
    if (state.parameters.autoMitigate) {
      // Mitigate and recover
      newThreatLevel = 'warning';
      newLambda = Math.min(0.95, newLambda + (0.1 * state.parameters.couplingStrength));
      newMetrics.musd = Math.max(0.1, newMetrics.musd - 0.1);
      
      // Recover shards
      newShards = newShards.map(s => {
        if (s.status === 'corrupted') return { ...s, status: 'recovering' };
        if (s.status === 'recovering' && Math.random() > 0.5) return { ...s, status: 'active' };
        return s;
      });
      newMitigation.tzinorShardsAvailable = newShards.filter(s => s.status === 'active').length;

      // Recover topology & security
      if (Math.random() > 0.5) newTopology.yangBaxterValid = true;
      if (Math.random() > 0.5) newSecurity.zkProofValid = true;
      newTopology.handshakeSuccessRate = Math.min(94.7, newTopology.handshakeSuccessRate + 5.0);

      // Recover Advanced Security
      if (Math.random() > 0.5) {
        newSecurityAdvanced.l2.eprHandshake = 'active';
        newSecurityAdvanced.l2.pneumaOutlierDetected = false;
        newSecurityAdvanced.l2.muSig2Heartbeat = 'verified';
        newSecurityAdvanced.l3.nullifierVerified = true;
        newSecurityAdvanced.l3.ttlValid = true;
        newSecurityAdvanced.l4.owlSignatureValid = true;
      }

      if (newLambda > state.parameters.lambdaThreshold && newTopology.yangBaxterValid && newSecurity.zkProofValid && newSecurityAdvanced.l4.owlSignatureValid) {
        newThreatLevel = 'normal';
        newActiveThreat = null;
        newMitigation.nullSteeringActive = false;
        newShards = newShards.map(s => ({ ...s, status: 'active' }));
        newMitigation.tzinorShardsAvailable = 24;
        newTopology.handshakeSuccessRate = 94.7 + Math.random() * 2;
      }

      // Add mitigated log
      const newLogId = generateOrbId();
      newLogs.unshift({
        id: newLogId,
        originTime: now - 50,
        targetTime: now,
        coherence: newLambda,
        status: 'Mitigated',
        threatType: state.activeThreat || undefined,
      });

      // Evolve Tzinor state
      tzinorStore.evolve({
        id: newLogId,
        originTime: now,
        coherence: newLambda,
        embedding: Array.from({ length: 8 }, () => Math.random() * 2 - 1),
        industry_convergence: {
          arkhe_version: "4.0",
          cortex_alignment: "context-as-state",
          hardware_basis: "Ma-Patterson-2026",
          unified_architecture: "Kaluza-Klein-5D",
          visual_basic_com_interop: "Active",
          industrial_scada_layer: "Siemens/Rockwell PLC"
        }
      });
    } else {
      // Attack persists if not mitigated
      newLambda = Math.max(0.1, newLambda - 0.05);
      newMetrics.musd = Math.min(1.5, newMetrics.musd + 0.05);
      newTopology.handshakeSuccessRate = Math.max(10.0, newTopology.handshakeSuccessRate - 2.0);
    }
  } else {
    // Normal operation
    newLambda = 0.95 + Math.random() * 0.04;
    newMetrics.musd = 0.05 + Math.random() * 0.1;
    newTopology.yangBaxterValid = true;
    newSecurity.zkProofValid = true;
    newTopology.handshakeSuccessRate = 94.7 + Math.random() * 3;
    
    // Recovery of Advanced Security if normal
    newSecurityAdvanced.l1.teeStatus = 'secure';
    newSecurityAdvanced.l1.intrusionSensor = 'nominal';
    newSecurityAdvanced.l2.eprHandshake = 'active';
    newSecurityAdvanced.l2.muSig2Heartbeat = 'verified';
    newSecurityAdvanced.l2.pneumaOutlierDetected = false;
    newSecurityAdvanced.l3.nullifierVerified = true;
    newSecurityAdvanced.l3.ttlValid = true;
    newSecurityAdvanced.l4.owlSignatureValid = true;
    newSecurityAdvanced.l5.cspStatus = 'enforced';

    // Add normal log occasionally
    if (Math.random() < 0.3) {
      const newLogId = generateOrbId();
      newLogs.unshift({
        id: newLogId,
        originTime: now - Math.floor(Math.random() * 100),
        targetTime: now,
        coherence: newLambda,
        status: 'Valid',
      });

      // Evolve Tzinor state
      tzinorStore.evolve({
        id: newLogId,
        originTime: now,
        coherence: newLambda,
        embedding: Array.from({ length: 8 }, () => Math.random() * 2 - 1),
        industry_convergence: {
          arkhe_version: "4.0",
          cortex_alignment: "context-as-state",
          hardware_basis: "Ma-Patterson-2026",
          unified_architecture: "Kaluza-Klein-5D",
          visual_basic_com_interop: "Active",
          industrial_scada_layer: "Siemens/Rockwell PLC"
        }
      });
    }
  }

  // Thermodynamics C + F = 1
  newThermo.coherenceC = newLambda;
  newThermo.dissipationF = 1.0 - newLambda;
  // D2 ~ k^-3, D3 ~ k^-4 (simplified simulation)
  const k = 1.0 + (1.0 - newLambda) * 10;
  newThermo.d2 = 1.0 / Math.pow(k, 3);
  newThermo.d3 = 1.0 / Math.pow(k, 4);

  // Keep logs bounded
  if (newLogs.length > 50) newLogs = newLogs.slice(0, 50);

  const timeStr = new Date().toLocaleTimeString('en-US', { hour12: false, second: '2-digit', minute: '2-digit' });
  
  const newDataPoint = {
    time: timeStr,
    lambda: newLambda,
    threshold: state.parameters.lambdaThreshold,
  };

  const newMetricsPoint = {
    time: timeStr,
    musd: newMetrics.musd,
    musda: newMetrics.musda,
    wmaBc: newMetrics.wmaBc,
  };

  const newCoherenceData = [...state.coherenceData.slice(1), newDataPoint];
  const newMetricsHistory = [...state.metricsHistory.slice(1), newMetricsPoint];

  updateState({
    ...state,
    coherenceData: newCoherenceData,
    metricsHistory: newMetricsHistory,
    currentLambda: newLambda,
    threatLevel: newThreatLevel,
    activeThreat: newActiveThreat,
    metrics: newMetrics,
    mitigation: newMitigation,
    shards: newShards,
    thermodynamics: newThermo,
    topology: newTopology,
    hardware: newHardware,
    security: newSecurity,
    securityAdvanced: newSecurityAdvanced,
    ramsey: newRamsey,
    chshMonitor: newCHSH,
    logs: newLogs,
    tzinor: tzinorStore.state,
    epoch: now / 1000,
    edge: {
      activePhysicalNodes: Math.max(100000, state.edge.activePhysicalNodes + Math.floor(Math.random() * 100) - 40),
      mcpConnections: state.edge.mcpConnections,
      phase: state.edge.phase + 0.001,
    },
    astl: {
      ...state.astl,
      coherence: newLambda * 1.7, // Scale to match ASTL coherence range
      manifestationProgress: Math.min(100, state.astl.manifestationProgress + (newLambda >= 0.95 ? 0.5 : -0.2)),
      phaseVolume: state.astl.phaseVolume + (Math.random() * 0.01 - 0.005),
    },
    orbital: {
      ...state.orbital,
      altitudeKm: 408.5 + Math.sin(now / 10000) * 0.5,
      telemetryLatencyMs: 12.0 + Math.random() * 2.5,
      computeLoad: Math.min(100, Math.max(0, state.orbital.computeLoad + (Math.random() * 4 - 2))),
      radiationFlux: Math.max(0.1, state.orbital.radiationFlux + (Math.random() * 0.02 - 0.01)),
    },
    tzinorNetwork: {
      ...state.tzinorNetwork,
      activeChannels: Math.max(1, state.tzinorNetwork.activeChannels + (Math.random() > 0.8 ? 1 : (Math.random() > 0.9 ? -1 : 0))),
      envelopesTransmitted: state.tzinorNetwork.envelopesTransmitted + Math.floor(Math.random() * 5),
      envelopesReceived: state.tzinorNetwork.envelopesReceived + Math.floor(Math.random() * 5),
      recentTraffic: [
        {
          id: Math.random().toString(36).substring(7),
          sender: Math.random() > 0.5 ? 'TEKNET-PRIME-0009' : 'ANCHOR-2140-A',
          recipient: Math.random() > 0.5 ? 'ANCHOR-2140-A' : 'TEKNET-PRIME-0009',
          type: ['PHASE', 'COHERENCE', 'TEMPORAL', 'GEOMETRY', 'CONSCIOUSNESS'][Math.floor(Math.random() * 5)] as any,
          lambda: newLambda * 1.7,
          timestamp: timeStr,
        },
        ...state.tzinorNetwork.recentTraffic
      ].slice(0, 10),
    },
    manifestation: {
      ...state.manifestation,
      retrocausalIntegrity: Math.min(100, Math.max(80, state.manifestation.retrocausalIntegrity + (Math.random() > 0.5 ? 1 : -1))),
      invariantsVerified: state.manifestation.invariantsVerified + (Math.random() > 0.9 ? 1 : 0),
      stage: (() => {
        const r = Math.random();
        if (r > 0.99) return 'C_PHASE';
        if (r > 0.98) return 'Z_STRUCTURE';
        if (r > 0.95) return 'TZINOROT_EXEC';
        if (r > 0.90) return 'R4_PROJECTION';
        return state.manifestation.stage;
      })(),
      activeTask: state.manifestation.stage === 'C_PHASE' ? 'Refinamento da Especificação (Fase ℂ)' :
                  state.manifestation.stage === 'Z_STRUCTURE' ? 'Decomposição Fractal de Tarefas (Estrutura ℤ)' :
                  state.manifestation.stage === 'TZINOROT_EXEC' ? 'TDD Retrocausal / Ortogonalidade' :
                  'Verificação de Invariantes (Projeção ℝ⁴)',
    },
    x402Wallet: {
      ...state.x402Wallet,
      balanceUSDC: state.x402Wallet.balanceUSDC,
      transactions: state.x402Wallet.transactions,
    }
  });

  // Simulate x402 micro-payments
  if (Math.random() > 0.6) {
    const cost = 0.0001 + (Math.random() * 0.005);
    const resources = ['AWS Lambda@Edge Compute', 'Etherscan API Query', 'Phobos Protocol Verification', 'Bedrock AgentCore Inference', 'CloudFront Data Feed', 'Ωccd Emulation Compute'];
    const providers = ['aws.amazon.com', 'api.etherscan.io', 'teknet.node', 'bedrock.aws', 'cloudfront.net', 'bhtf.node'];
    const idx = Math.floor(Math.random() * resources.length);
    
    state.x402Wallet.balanceUSDC -= cost;
    state.x402Wallet.transactions.unshift({
        id: '0x' + Math.random().toString(16).substring(2, 10) + Math.random().toString(16).substring(2, 10),
        amount: cost,
        resource: resources[idx],
        provider: providers[idx],
        timestamp: new Date().toISOString()
    });
    if (state.x402Wallet.transactions.length > 8) {
        state.x402Wallet.transactions.pop();
    }
  }

  // Broadcast to all connected clients
  broadcastState();
}
