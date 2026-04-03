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
  payload?: any;
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

export interface SimulationState {
  coherenceData: { time: string; lambda: number; threshold: number }[];
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
  shards: Shard[];
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
  tzinor: TzinorMemoryState;
  epoch: number;
  edge: {
    activePhysicalNodes: number;
    mcpConnections: string[];
    phase: number;
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
    recentTraffic: {
      id: string;
      sender: string;
      recipient: string;
      type: 'PHASE' | 'COHERENCE' | 'TEMPORAL' | 'GEOMETRY' | 'CONSCIOUSNESS';
      lambda: number;
      timestamp: string;
    }[];
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
    transactions: {
      id: string;
      amount: number;
      resource: string;
      provider: string;
      timestamp: string;
    }[];
    moltxLink?: {
      status: 'unlinked' | 'linked';
      signature?: string;
      payload?: any;
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
}
