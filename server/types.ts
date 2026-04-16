/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */


/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

export interface ContextNode {
  timestamp: number;
  embedding: number[];
  salience: number;
}

export interface MemoryEngram {
  originTime: number;
  consolidatedTime: number;
  summaryHash: string;
  resonanceWeight: number;
}

export interface TzinorMemoryState {
  agentId: string;
  currentEpoch: number;
  fContext: ContextNode[];
  gMemory: MemoryEngram[]; // Acts as VecDeque
  warpFactor: number; // f64
  lambdaCoherence: number; // f64
}

export interface IndustryConvergence {
  arkhe_version?: string;
  cortex_alignment?: string;
  hardware_basis?: string;
  unified_architecture?: string;
  visual_basic_com_interop?: string;
  industrial_scada_layer?: string;
}

export interface OrbPayload {
  id: string;
  originTime: number;
  coherence: number;
  embedding: number[];
  industry_convergence?: IndustryConvergence;
  signature?: string;
  signer_address?: string;
}

export interface OrbLog {
  id: string;
  originTime: number;
  targetTime: number;
  coherence: number;
  status: 'Valid' | 'Mitigated' | 'Rejected';
  threatType?: string;
}

export interface Shard {
  id: number;
  status: 'active' | 'corrupted' | 'recovering';
}

export interface MetricsHistory {
  time: string;
  musd: number;
  musda: number;
  wmaBc: number;
}

export interface SessionEvent {
  type: 'SESSION_START' | 'SESSION_EVENT' | 'SESSION_END' | 'SESSION_ANALYSIS';
  sessionId: string;
  timestamp: number;
  eventType?: string;
  payload?: unknown;
  coherence?: number;
  zkProof?: string;
}

export interface UserSession {
  id: string;
  startTime: number;
  endTime?: number;
  events: SessionEvent[];
  analysis?: {
    bugDetected: boolean;
    uxScore: number;
    description: string;
    zkProof: string;
    consensusReached: boolean;
  };
}

export interface SecurityAdvancedState {
  l1: {
    teeStatus: 'secure' | 'compromised' | 'attesting';
    intrusionSensor: 'nominal' | 'alert';
    thermalDestructionArmed: boolean;
    hsmBackupSynced: boolean;
    lastRemoteAttestation: string;
  };
  l2: {
    eprHandshake: 'active' | 'failed';
    muSig2Heartbeat: 'verified' | 'unverified';
    pneumaOutlierDetected: boolean;
    qrngJitterMs: number;
  };
  l3: {
    nullifierVerified: boolean;
    timestampQRNG: string;
    ttlValid: boolean;
    t2StarMicroseconds: number;
  };
  l4: {
    owlSignatureValid: boolean;
    logosConsistency: number;
    zkOntologicalProof: boolean;
    merkleDagRoot: string;
    geoLlmActive: boolean;
    geoQaiCoherence: number;
  };
  l5: {
    cspStatus: 'enforced' | 'violation';
    sriVerified: boolean;
    antiCsrfToken: string;
    zkUiVerified: boolean;
    pwaCacheSigned: boolean;
  };
  qhttp: {
    pqTlsStatus: 'Kyber+ECDH' | 'Classic' | 'None';
    xKuramotoHeader: string;
    bellViolationS: number;
  };
}

export interface SimulationState {
  coherenceData: Array<{ time: string; lambda: number; threshold: number }>;
  currentLambda: number;
  threatLevel: 'normal' | 'warning' | 'critical';
  activeThreat: string | null;
  logs: OrbLog[];
  metrics: {
    musd: number;
    musda: number;
    wmaBc: number;
    threshold: number;
  };
  metricsHistory: MetricsHistory[];
  shards: Array<Shard>;
  mitigation: {
    nullSteeringActive: boolean;
    kuramotoSyncPhase: number;
    tzinorShardsAvailable: number;
  };
  parameters: {
    autoMitigate: boolean;
    couplingStrength: number;
    lambdaThreshold: number;
  };
  thermodynamics: {
    coherenceC: number;
    dissipationF: number;
    d2: number;
    d3: number;
  };
  topology: {
    yangBaxterValid: boolean;
    berryPhase: number;
    handshakeSuccessRate: number;
  };
  hardware: {
    fpgaUtilization: number;
    segPower: number;
    tmrFaultsCorrected: number;
    bramScrubbingActive: boolean;
  };
  security: {
    zkProofValid: boolean;
    nttLatency: number;
  };
  securityAdvanced: SecurityAdvancedState;
  tzinor: TzinorMemoryState;
  epoch: number;
  edge: {
    activePhysicalNodes: number;
    mcpConnections: string[];
    velxioConnections: string[];
    phase: number;
  };
  velxioEmulation: {
    activeSimulations: Array<{
      id: string;
      board: string;
      status: 'running' | 'idle' | 'error';
      startTime: string;
      lastLog?: string;
    }>;
    totalCompilations: number;
  };
  astl: {
    activeMesh: string;
    facets: number;
    coherence: number;
    phaseVolume: number;
    temporalAnchors: string[];
    manifestationProgress: number;
  };
  orbital: {
    nodeName: string;
    altitudeKm: number;
    telemetryLatencyMs: number;
    computeLoad: number;
    radiationFlux: number;
    osStack: {
      execution: string;
      control: string;
      simulation: string;
      compute: string;
    };
  };
  tzinorNetwork: {
    activeChannels: number;
    envelopesTransmitted: number;
    envelopesReceived: number;
    recentTraffic: Array<{
      id: string;
      sender: string;
      recipient: string;
      type: 'PHASE' | 'COHERENCE' | 'TEMPORAL' | 'GEOMETRY' | 'CONSCIOUSNESS';
      lambda: number;
      timestamp: string;
    }>;
    primaryAnchor: string;
  };
  manifestation: {
    stage: 'C_PHASE' | 'Z_STRUCTURE' | 'TZINOROT_EXEC' | 'R4_PROJECTION';
    activeTask: string;
    retrocausalIntegrity: number;
    invariantsVerified: number;
  };
  x402Wallet: {
    address: string;
    network: string;
    balanceUSDC: number;
    transactions: Array<{
      id: string;
      amount: number;
      resource: string;
      provider: string;
      timestamp: string;
    }>;
    moltxLink?: {
      status: 'unlinked' | 'linked';
      signature?: string;
      payload?: unknown;
    };
    gstpSync?: {
      status: 'idle' | 'syncing' | 'synced';
      lastSync?: string;
      deviceId?: string;
    };
    prometheusSync?: {
      status: 'idle' | 'syncing' | 'synced';
      lastSync?: string;
      activeNodes?: number;
    };
  };
  cluster: {
    status: 'idle' | 'deploying' | 'resonant';
    progress: number;
    logs: string[];
    nccl: {
      rho1_local: number;
      rho1_global: number;
    };
    qhttp: {
      global_phase: number;
      coherence: number;
    };
  };
  lucentSessions: UserSession[];
  hydro: {
    neighborhoods: NeighborhoodCoherence[];
    globalMassBalance: number;
    zkAlertsCount: number;
  };
  ramsey: RamseyState;
  civicSubagents: CivicSubagentState[];
  enterpriseSubagents: {
    governance: EnterpriseSubagentState[];
    devops: EnterpriseSubagentState[];
    security: EnterpriseSubagentState[];
    ia: EnterpriseSubagentState[];
    operations: EnterpriseSubagentState[];
    interoperability: EnterpriseSubagentState[];
  };
  chshMonitor: CHSHMonitorState;
  scaData: ScaDataState;
  biometrics?: BiometricState;
  nare?: NAREStatus;
  populationFeedback: PopulationFeedbackEntry[];
  networkInfra: NetworkInfraState;
}

export interface NetworkInfraState {
  tor: {
    status: 'CONNECTED' | 'DISCONNECTED' | 'CIRCUIT_ESTABLISHING';
    nodes: string[];
    latencyMs: number;
  };
  broker: {
    status: 'ACTIVE' | 'IDLE' | 'ERROR';
    messagesProcessed: number;
    queueDepth: number;
    activeTopics: string[];
  };
  redis: {
    status: 'READY' | 'FAILOVER' | 'OFFLINE';
    cacheHits: number;
    memoryUsageMb: number;
  };
  dns: {
    totalQueries: number;
    successfulResolutions: number;
    failedResolutions: number;
    lastResolvedConcept?: string;
  };
}

export interface NAREStatus {
  epState: boolean;
  calibrationRounds: number;
  packetsTransmitted: number;
  preAcksSuccess: number;
  avgEffectiveLatencyMs: number;
  temporalParadoxesDetected: number;
  currentLambda2: number;
  predictionWindow: string;
  status: string;
}

export interface PopulationFeedbackEntry {
  id: string;
  residentName: string;
  year: number;
  message: string;
  coherence: number;
  timestamp: string;
}

export interface BiometricState {
  livenessScore: number;
  isAuthentic: boolean;
  lastVerification: string;
  heartbeatCoherence: number;
  phaseSignature: number[];
}

export interface NeighborhoodCoherence {
  name: string;
  region: string;
  coherence: number;
  lag: number; // in hours
  activeUsers: number;
}

export type RamseyAction = 'LOCAL_ADJUST' | 'LOG_ONLY' | 'LOCAL_ADJUST_NOTIFY' | 'GLOBAL_ADJUST';

export interface RamseyThreshold {
  angle_rad: number;
  tolerance: number;
  min_gain: number;
  action: RamseyAction;
}

export interface RamseyPendingAction {
  id: string;
  type: RamseyAction;
  angle: number;
  coherence: number;
  timestamp: string;
  expiresAt: string;
}

export interface PulseConfig {
  generator: string;
  duration_fs: number;
  polarization: string;
  peak_power_w_cm2: number;
  angle_rad: number;
}

export interface GeneratorSequence {
  name: string;
  generators: string[];
}

export interface RamseyState {
  enabled: boolean;
  auto_adjust: boolean;
  manual_approval_required: boolean;
  theta: number;
  direction: number;
  baseline: number;
  thresholds: RamseyThreshold[];
  window: Array<{ theta: number; coherence: number }>;
  pendingAction: RamseyPendingAction | null;
  isFrozen: boolean;
  rabi_frequency: number;
  generator_configs: Record<string, PulseConfig>;
  fibonacci_sequence: GeneratorSequence;
}

export interface CivicSubagentState {
  name: string;
  adaptation: string;
  function: string;
  status: 'active' | 'idle' | 'alert';
  lastAction: string;
}

export interface EnterpriseSubagentState {
  id: string;
  name: string;
  theory: string;
  function: string;
  metric: string;
  status: 'active' | 'idle' | 'alert';
  lastAction: string;
  nip?: string;
}

export interface CHSHMonitorState {
  status: string;
  timestamp: string;
  arkheChainBlock: number;
  measurementSetup: {
    instrument: string;
    targetSystem: string;
    referenceLattice: string;
    angleBases: number[];
    coincidenceWindowNs: number;
    integrationTimeSec: number;
  };
  expectedOutcomes: {
    classicalLimit: number;
    quantumLimit: number;
    thresholdEntangled: number;
    targetEntanglement: string;
  };
  liveTelemetry: {
    status: string;
    dataPoints: number;
    currentS: number | null;
    stabilityIndicator: string;
    nextUpdate: string;
    history: Array<{ time: string; s: number }>;
  };
  preFlightChecks: {
    tzinorInjector: string;
    fibonacciPhaseAnchor: string;
    treeLacamGeodesic: string;
    pdsmIgnitionSequence: string;
  };
  archimedesComment: string;
  nextMilestone: {
    time: string;
    action: string;
  };
}

export interface ScaDomain {
  name: string;
  lambda2: number;
  action: string;
  health: 'STABLE' | 'CRITICAL';
}

export interface ScaDataState {
  domains: ScaDomain[];
  overallHealth: number;
  topology: 'TRINITY' | 'KAGOME';
  globalOrderR: number;
  topologicalState: string;
  entanglementMode: string;
  atpConsumptionCps: number;
  isSeedingActive: boolean;
  isIgnited: boolean;
  activeProtocol: 'NONE' | 'BRAID' | 'COMPUTE' | 'HEAL' | 'SEAL';
  protocolLogs: string[];
  lastGateResult: string;
}
