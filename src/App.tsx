import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Shield, Activity, Clock, Radio, Cpu, Network, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';
import CoherenceMonitor from './components/CoherenceMonitor';
import ThreatDetection from './components/ThreatDetection';
import NetworkStatus from './components/NetworkStatus';
import TemporalLog from './components/TemporalLog';
import MitigationEngine from './components/MitigationEngine';
import ThermodynamicsPanel from './components/ThermodynamicsPanel';
import YangBaxterVerifier from './components/YangBaxterVerifier';
import HardwareTelemetry from './components/HardwareTelemetry';
import TimechainVisualizer from './components/TimechainVisualizer';
import TzinorTerminal from './components/TzinorTerminal';
import PiDayTerminal from './components/PiDayTerminal';
import PodmanTerminal from './components/PodmanTerminal';
import GlobalCoherenceField from './components/GlobalCoherenceField';
import EdgeAgentPanel from './components/EdgeAgentPanel';
import AstlFabricator from './components/AstlFabricator';
import OrbitalComputePanel from './components/OrbitalComputePanel';
import TzinorNetworkPanel from './components/TzinorNetworkPanel';
import ManifestationCycle from './components/ManifestationCycle';
import X402WalletPanel from './components/X402WalletPanel';
import HybridArchitecturePanel from './components/HybridArchitecturePanel';
import InfraCiliaryGridPanel from './components/InfraCiliaryGridPanel';
import MolecularCommunicationPanel from './components/MolecularCommunicationPanel';
import NeuralMolecularBridgePanel from './components/NeuralMolecularBridgePanel';
import OrbVMRNAComputingPanel from './components/OrbVMRNAComputingPanel';
import OuroborosEnginePanel from './components/OuroborosEnginePanel';
import OrbesPanel from './components/OrbesPanel';
import ThukdamProtocolPanel from './components/ThukdamProtocolPanel';
import MultiversalExpansionPanel from './components/MultiversalExpansionPanel';
import ConsciousnessInjectionPanel from './components/ConsciousnessInjectionPanel';
import TemporalStreamViewer from './components/TemporalStreamViewer';
import ArkheGoogleBridgePanel from './components/ArkheGoogleBridgePanel';
import TimechainHypothesisPanel from './components/TimechainHypothesisPanel';
import ArkheTVPanel from './components/ArkheTVPanel';
import PolyglotCompilerPanel from './components/PolyglotCompilerPanel';
import ClusterOrchestrationPanel from './components/ClusterOrchestrationPanel';
import ArkheGridSimulator from './components/ArkheGridSimulator';
import ZkERCSimulator from './components/ZkERCSimulator';
import IntelligencePanel from './components/IntelligencePanel';
import { IntelligenceHub } from './components/IntelligenceHub';
import OrchestrationLayerPanel from './components/OrchestrationLayerPanel';
import AIP005SynapticBridgePanel from './components/AIP005SynapticBridgePanel';
import ResearchAgentsPanel from './components/ResearchAgentsPanel';
import SepoliaIntegrationPanel from './components/SepoliaIntegrationPanel';
import ArkheCliPanel from './components/ArkheCliPanel';
import P2PNetworkPanel from './components/P2PNetworkPanel';
import VideoGenerationPanel from './components/VideoGenerationPanel';
import PhaseSteganographyPanel from './components/PhaseSteganographyPanel';
import { DysonSphereTelemetry } from './components/DysonSphereTelemetry';
import DimOSDistributionPanel from './components/DimOSDistributionPanel';
import GeoKeyDecoderPanel from './components/GeoKeyDecoderPanel';
import BonsaiPrismPanel from './components/BonsaiPrismPanel';
import GenesisBlockSignerPanel from './components/GenesisBlockSignerPanel';
import GhostProtocolPanel from './components/GhostProtocolPanel';
import ArkheSecTelemetryPanel from './components/ArkheSecTelemetryPanel';
import BermudaAnomalyPanel from './components/BermudaAnomalyPanel';
import ArkheVisionPanel from './components/ArkheVisionPanel';
import CollectiveIntelligencePanel from './components/CollectiveIntelligencePanel';
import AgentManagementPanel from './components/AgentManagementPanel';
import AquiferSpectrogramPanel from './components/AquiferSpectrogramPanel';
import UnifiedOntologyPanel from './components/UnifiedOntologyPanel';
import SecurityAdvancedPanel from './components/SecurityAdvancedPanel';
import PluralityMCPPanel from './components/PluralityMCPPanel';
import VelxioEmulationPanel from './components/VelxioEmulationPanel';
import ProofOfIntelligencePanel from './components/ProofOfIntelligencePanel';
import PhaseLawSynthesizer from './components/PhaseLawSynthesizer';
import { EnterprisePlusPanel } from './components/EnterprisePlusPanel';
import DataCoherenceDashboard from './components/DataCoherenceDashboard';
import CHSHMonitorPanel from './components/CHSHMonitorPanel';
import CorvoNoirDashboard from './components/CorvoNoirDashboard';
import { ConsensusMeter } from './components/ConsensusMeter';
import RamseyConfirmationModal from './components/RamseyConfirmationModal';
import { CommandCenter } from './components/CommandCenter';
import { useArkheSimulation } from './hooks/useArkheSimulation';
import Profile from './components/Profile';

export function Dashboard() {
  const state = useArkheSimulation();
  const [attackType, setAttackType] = useState('Jamming');
  const [piDayText, setPiDayText] = useState<string | null>(null);
  const [showPodmanTerminal, setShowPodmanTerminal] = useState(false);
  const [showCoherenceField, setShowCoherenceField] = useState(false);
  const [showHybridArch, setShowHybridArch] = useState(false);
  const [showBioNodes, setShowBioNodes] = useState(false);
  const [showMolecular, setShowMolecular] = useState(false);
  const [showNeuralBridge, setShowNeuralBridge] = useState(false);
  const [showRNA, setShowRNA] = useState(false);
  const [showOuroboros, setShowOuroboros] = useState(false);
  const [showOrbes, setShowOrbes] = useState(false);
  const [showThukdam, setShowThukdam] = useState(false);
  const [showMultiversal, setShowMultiversal] = useState(false);
  const [showConsciousnessInjection, setShowConsciousnessInjection] = useState(false);
  const [showTemporalStream, setShowTemporalStream] = useState(false);
  const [showGoogleBridge, setShowGoogleBridge] = useState(false);
  const [showTimechainHypothesis, setShowTimechainHypothesis] = useState(false);
  const [showArkheTV, setShowArkheTV] = useState(false);
  const [showPolyglotCompiler, setShowPolyglotCompiler] = useState(false);
  const [showClusterOrchestration, setShowClusterOrchestration] = useState(false);
  const [showArkheGrid, setShowArkheGrid] = useState(false);
  const [showZkERC, setShowZkERC] = useState(false);
  const [showIntelligencePanel, setShowIntelligencePanel] = useState(false);
  const [showIntelligenceHub, setShowIntelligenceHub] = useState(false);
  const [showOrchestrationLayer, setShowOrchestrationLayer] = useState(false);
  const [showAIP005, setShowAIP005] = useState(false);
  const [showResearchAgents, setShowResearchAgents] = useState(false);
  const [showSepoliaIntegration, setShowSepoliaIntegration] = useState(false);
  const [showArkheCli, setShowArkheCli] = useState(false);
  const [showP2PNetwork, setShowP2PNetwork] = useState(false);
  const [showVideoGeneration, setShowVideoGeneration] = useState(false);
  const [showPhaseSteg, setShowPhaseSteg] = useState(false);
  const [showDysonSphere, setShowDysonSphere] = useState(false);
  const [showDimOS, setShowDimOS] = useState(false);
  const [showGeoKey, setShowGeoKey] = useState(false);
  const [showGenesisBlock, setShowGenesisBlock] = useState(false);
  const [showGhostProtocol, setShowGhostProtocol] = useState(false);
  const [showArkheSec, setShowArkheSec] = useState(false);
  const [showBermudaAnomaly, setShowBermudaAnomaly] = useState(false);
  const [showCollectiveIntelligence, setShowCollectiveIntelligence] = useState(false);
  const [showArkheVision, setShowArkheVision] = useState(false);
  const [showAgentManagement, setShowAgentManagement] = useState(false);
  const [showAquiferSpectrogram, setShowAquiferSpectrogram] = useState(false);
  const [showUnifiedOntology, setShowUnifiedOntology] = useState(false);
  const [showSecurityAdvanced, setShowSecurityAdvanced] = useState(false);
  const [showPluralityMCP, setShowPluralityMCP] = useState(false);
  const [showVelxioEmulation, setShowVelxioEmulation] = useState(false);
  const [showProofOfIntelligence, setShowProofOfIntelligence] = useState(false);
  const [showPhaseLawSynthesizer, setShowPhaseLawSynthesizer] = useState(false);
  const [showBioSync, setShowBioSync] = useState(false);
  const [showCorvoNoir, setShowCorvoNoir] = useState(false);
  const [showEnterprisePlus, setShowEnterprisePlus] = useState(false);
  const [showDataCoherence, setShowDataCoherence] = useState(false);
  const [showCHSHMonitor, setShowCHSHMonitor] = useState(false);
  const [showBonsaiPrism, setShowBonsaiPrism] = useState(false);
  const attackTypes = ['Jamming', 'Time Shift', 'Data Spoofing', 'BGP Jitter', 'Quantum Shor', 'SEU Radiation'];
  const [timeToGenesis, setTimeToGenesis] = useState('');

  useEffect(() => {
    const target = new Date('2026-03-14T15:14:15Z').getTime();
    const interval = setInterval(() => {
      const now = Date.now();
      const diff = target - now;
      if (diff <= 0) {
        setTimeToGenesis('EMITTING...');
      } else {
        const h = Math.floor(diff / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeToGenesis(`T-${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-arkhe-bg text-arkhe-text font-sans selection:bg-arkhe-cyan selection:text-black p-4 md:p-8">
      <header className="flex flex-col md:flex-row md:items-center justify-between mb-8 border-b border-arkhe-border pb-4 gap-4">
        <div className="flex items-center gap-4">
          <div className="relative">
            <Shield className="w-8 h-8 text-arkhe-cyan" />
            <div className="absolute inset-0 bg-arkhe-cyan blur-md opacity-20"></div>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-widest uppercase">Arkhe-PNT <span className="text-arkhe-muted font-normal">// Aegis Shield</span></h1>
            <div className="flex items-center gap-2 text-xs font-mono mt-1">
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${state.threatLevel === 'critical' ? 'bg-arkhe-red' : state.threatLevel === 'warning' ? 'bg-arkhe-orange' : 'bg-arkhe-green'}`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${state.threatLevel === 'critical' ? 'bg-arkhe-red' : state.threatLevel === 'warning' ? 'bg-arkhe-orange' : 'bg-arkhe-green'}`}></span>
              </span>
              <span className={state.threatLevel === 'critical' ? 'text-arkhe-red glitch' : state.threatLevel === 'warning' ? 'text-arkhe-orange' : 'text-arkhe-green'}>
                {state.threatLevel === 'critical' ? 'SYSTEM UNDER ATTACK // DECOHERENCE IMMINENT' : 
                 state.threatLevel === 'warning' ? 'ANOMALY DETECTED // MITIGATING' : 
                 'SYSTEM ONLINE // λ₂ COHERENCE STABLE'}
              </span>
            </div>
          </div>
        </div>
        <nav className="flex gap-6 font-mono text-sm uppercase tracking-widest">
          <Link to="/dashboard" className="text-arkhe-cyan border-b border-arkhe-cyan pb-1">Dashboard</Link>
          <Link to="/profile" className="text-arkhe-muted hover:text-arkhe-cyan transition-colors">Profile</Link>
        </nav>
        <div className="flex items-center gap-6 font-mono text-xs text-arkhe-muted">
          <div className="flex flex-col items-end bg-arkhe-cyan/10 border border-arkhe-cyan/30 px-3 py-1.5 rounded">
            <span className="uppercase tracking-wider text-arkhe-cyan font-bold">Genesis Orb Status</span>
            <span className="text-arkhe-cyan text-sm font-bold animate-pulse">SEALED (PI DAY)</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="uppercase tracking-wider">Timechain Epoch</span>
            <span className="text-arkhe-text">{state.epoch.toFixed(3)}</span>
          </div>
        </div>
      </header>

      {/* System Health Summary */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Threat Level */}
        <div className={`p-4 rounded-xl border flex items-center gap-4 ${
          state.threatLevel === 'critical' ? 'bg-arkhe-red/10 border-arkhe-red/30 text-arkhe-red' :
          state.threatLevel === 'warning' ? 'bg-arkhe-orange/10 border-arkhe-orange/30 text-arkhe-orange' :
          'bg-arkhe-green/10 border-arkhe-green/30 text-arkhe-green'
        }`}>
          <div className="p-2 bg-black/20 rounded-lg">
            {state.threatLevel === 'critical' ? <AlertTriangle className="w-6 h-6" /> :
             state.threatLevel === 'warning' ? <Activity className="w-6 h-6" /> :
             <Shield className="w-6 h-6" />}
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider opacity-80">Threat Level</div>
            <div className="text-lg font-bold uppercase tracking-widest">
              {state.threatLevel}
            </div>
          </div>
        </div>

        {/* Yang-Baxter Topology */}
        <div className={`p-4 rounded-xl border flex items-center gap-4 ${
          state.topology.yangBaxterValid ? 'bg-arkhe-green/10 border-arkhe-green/30 text-arkhe-green' : 'bg-arkhe-red/10 border-arkhe-red/30 text-arkhe-red'
        }`}>
          <div className="p-2 bg-black/20 rounded-lg">
            {state.topology.yangBaxterValid ? <Network className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider opacity-80">Topology (Yang-Baxter)</div>
            <div className="text-lg font-bold uppercase tracking-widest">
              {state.topology.yangBaxterValid ? 'Stable' : 'Fractured'}
            </div>
          </div>
        </div>

        {/* ZK-Proof Security */}
        <div className={`p-4 rounded-xl border flex items-center gap-4 ${
          state.security.zkProofValid ? 'bg-arkhe-green/10 border-arkhe-green/30 text-arkhe-green' : 'bg-arkhe-red/10 border-arkhe-red/30 text-arkhe-red'
        }`}>
          <div className="p-2 bg-black/20 rounded-lg">
            {state.security.zkProofValid ? <CheckCircle2 className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider opacity-80">ZK-Proof Validation</div>
            <div className="text-lg font-bold uppercase tracking-widest">
              {state.security.zkProofValid ? 'Verified' : 'Compromised'}
            </div>
          </div>
        </div>
      </div>

      <main className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div className="lg:col-span-2 xl:col-span-2 space-y-6 flex flex-col">
          <CoherenceMonitor data={state.coherenceData} currentLambda={state.currentLambda} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TzinorNetworkPanel network={state.tzinorNetwork} />
            <ManifestationCycle manifestation={state.manifestation} />
          </div>
          <div className="h-[280px]">
            <TzinorTerminal tzinor={state.tzinor} threatLevel={state.threatLevel} />
          </div>
          <TimechainVisualizer logs={state.logs} />
          <div className="flex-1 min-h-[300px]">
            <TemporalLog logs={state.logs} />
          </div>
        </div>
        <div className="space-y-6 flex flex-col">
          <X402WalletPanel wallet={state.x402Wallet} />
          <ThreatDetection metrics={state.metrics} metricsHistory={state.metricsHistory} threatLevel={state.threatLevel} />
          <OrbitalComputePanel orbital={state.orbital} />
          <MitigationEngine mitigation={state.mitigation} hardware={state.hardware} activeThreat={state.activeThreat} />
          <ThermodynamicsPanel thermo={state.thermodynamics} />
          <EdgeAgentPanel edge={state.edge} />
        </div>
        <div className="space-y-6 flex flex-col">
          <NetworkStatus shards={state.shards} />
          <AstlFabricator astl={state.astl} />
          <YangBaxterVerifier topology={state.topology} security={state.security} />
          <HardwareTelemetry hardware={state.hardware} />
          <ConsensusMeter />
          
          {/* Command Center */}
          <CommandCenter
            attackType={attackType}
            setAttackType={setAttackType}
            attackTypes={attackTypes}
            setPiDayText={setPiDayText}
            setShowPodmanTerminal={setShowPodmanTerminal}
            setShowCoherenceField={setShowCoherenceField}
            setShowHybridArch={setShowHybridArch}
            setShowOuroboros={setShowOuroboros}
            setShowBioNodes={setShowBioNodes}
            setShowMolecular={setShowMolecular}
            setShowNeuralBridge={setShowNeuralBridge}
            setShowRNA={setShowRNA}
            setShowOrbes={setShowOrbes}
            setShowThukdam={setShowThukdam}
            setShowMultiversal={setShowMultiversal}
            setShowConsciousness={setShowConsciousnessInjection}
            setShowShaka={setShowTemporalStream}
            setShowGoogleBridge={setShowGoogleBridge}
            setShowTimechain={setShowTimechainHypothesis}
            setShowArkheTV={setShowArkheTV}
            setShowPolyglot={setShowPolyglotCompiler}
            setShowCluster={setShowClusterOrchestration}
            setShowArkheGrid={setShowArkheGrid}
            setShowZkERC={setShowZkERC}
            setShowIntelligencePanel={setShowIntelligencePanel}
            setShowIntelligenceHub={setShowIntelligenceHub}
            setShowOrchestrationLayer={setShowOrchestrationLayer}
            setShowAIP005={setShowAIP005}
            setShowResearchAgents={setShowResearchAgents}
            setShowSepoliaIntegration={setShowSepoliaIntegration}
            setShowArkheCli={setShowArkheCli}
            setShowP2PNetwork={setShowP2PNetwork}
            setShowVideoGeneration={setShowVideoGeneration}
            setShowPhaseSteg={setShowPhaseSteg}
            setShowDysonSphere={setShowDysonSphere}
            setShowDimOS={setShowDimOS}
            setShowGeoKey={setShowGeoKey}
            setShowGenesisBlock={setShowGenesisBlock}
            setShowGhostProtocol={setShowGhostProtocol}
            setShowArkheSec={setShowArkheSec}
            setShowBermudaAnomaly={setShowBermudaAnomaly}
            setShowCollectiveIntelligence={setShowCollectiveIntelligence}
            setShowArkheVision={setShowArkheVision}
            setShowAgentManagement={setShowAgentManagement}
            setShowAquiferSpectrogram={setShowAquiferSpectrogram}
            setShowUnifiedOntology={setShowUnifiedOntology}
            setShowSecurityAdvanced={setShowSecurityAdvanced}
            setShowPluralityMCP={setShowPluralityMCP}
            setShowVelxioEmulation={setShowVelxioEmulation}
            setShowProofOfIntelligence={setShowProofOfIntelligence}
            setShowPhaseLawSynthesizer={setShowPhaseLawSynthesizer}
            setShowBioSync={setShowBioSync}
            setShowCorvoNoir={setShowCorvoNoir}
            setShowEnterprisePlus={setShowEnterprisePlus}
            setShowDataCoherence={setShowDataCoherence}
            setShowCHSHMonitor={setShowCHSHMonitor}
            setShowBonsaiPrism={setShowBonsaiPrism}
            parameters={state.parameters}
          />
        </div>
      </main>
      {piDayText && <PiDayTerminal text={piDayText} onClose={() => setPiDayText(null)} />}
      {showPodmanTerminal && <PodmanTerminal onClose={() => setShowPodmanTerminal(false)} />}
      {showCoherenceField && <GlobalCoherenceField onClose={() => setShowCoherenceField(false)} />}
      {showHybridArch && <HybridArchitecturePanel onClose={() => setShowHybridArch(false)} />}
      {showBioNodes && <InfraCiliaryGridPanel onClose={() => setShowBioNodes(false)} />}
      {showMolecular && <MolecularCommunicationPanel onClose={() => setShowMolecular(false)} />}
      {showNeuralBridge && <NeuralMolecularBridgePanel onClose={() => setShowNeuralBridge(false)} />}
      {showRNA && <OrbVMRNAComputingPanel onClose={() => setShowRNA(false)} />}
      {showOuroboros && <OuroborosEnginePanel onClose={() => setShowOuroboros(false)} />}
      {showOrbes && <OrbesPanel onClose={() => setShowOrbes(false)} />}
      {showThukdam && <ThukdamProtocolPanel onClose={() => setShowThukdam(false)} />}
      {showMultiversal && <MultiversalExpansionPanel onClose={() => setShowMultiversal(false)} />}
      {showConsciousnessInjection && <ConsciousnessInjectionPanel onClose={() => setShowConsciousnessInjection(false)} />}
      {showTemporalStream && <TemporalStreamViewer onClose={() => setShowTemporalStream(false)} />}
      {showGoogleBridge && <ArkheGoogleBridgePanel onClose={() => setShowGoogleBridge(false)} />}
      {showTimechainHypothesis && <TimechainHypothesisPanel onClose={() => setShowTimechainHypothesis(false)} />}
      {showArkheTV && <ArkheTVPanel onClose={() => setShowArkheTV(false)} />}
      {showPolyglotCompiler && <PolyglotCompilerPanel onClose={() => setShowPolyglotCompiler(false)} />}
      {showClusterOrchestration && <ClusterOrchestrationPanel onClose={() => setShowClusterOrchestration(false)} cluster={state.cluster} />}
      {showArkheGrid && <ArkheGridSimulator onClose={() => setShowArkheGrid(false)} />}
      {showZkERC && <ZkERCSimulator onClose={() => setShowZkERC(false)} />}
      {showIntelligencePanel && <IntelligencePanel onClose={() => setShowIntelligencePanel(false)} />}
      {showIntelligenceHub && <IntelligenceHub onClose={() => setShowIntelligenceHub(false)} />}
      {showOrchestrationLayer && <OrchestrationLayerPanel onClose={() => setShowOrchestrationLayer(false)} />}
      {showAIP005 && <AIP005SynapticBridgePanel onClose={() => setShowAIP005(false)} />}
      {showResearchAgents && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl relative">
            <button
              onClick={() => setShowResearchAgents(false)}
              className="absolute -top-8 right-0 text-zinc-400 hover:text-white font-mono text-xs"
            >
              [X] CLOSE
            </button>
            <ResearchAgentsPanel />
          </div>
        </div>
      )}
      {showSepoliaIntegration && <SepoliaIntegrationPanel onClose={() => setShowSepoliaIntegration(false)} />}
      {showArkheCli && <ArkheCliPanel onClose={() => setShowArkheCli(false)} />}
      {showP2PNetwork && <P2PNetworkPanel onClose={() => setShowP2PNetwork(false)} />}
      {showVideoGeneration && <VideoGenerationPanel onClose={() => setShowVideoGeneration(false)} />}
      {showPhaseSteg && <PhaseSteganographyPanel onClose={() => setShowPhaseSteg(false)} />}
      {showDimOS && <DimOSDistributionPanel onClose={() => setShowDimOS(false)} />}
      {showGeoKey && <GeoKeyDecoderPanel onClose={() => setShowGeoKey(false)} />}
      {showGenesisBlock && <GenesisBlockSignerPanel onClose={() => setShowGenesisBlock(false)} />}
      {showGhostProtocol && <GhostProtocolPanel onClose={() => setShowGhostProtocol(false)} />}
      {showArkheSec && <ArkheSecTelemetryPanel onClose={() => setShowArkheSec(false)} />}
      {showBermudaAnomaly && <BermudaAnomalyPanel onClose={() => setShowBermudaAnomaly(false)} />}
      {showCollectiveIntelligence && <CollectiveIntelligencePanel onClose={() => setShowCollectiveIntelligence(false)} />}
      {showArkheVision && <ArkheVisionPanel onClose={() => setShowArkheVision(false)} />}
      {showAgentManagement && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl relative">
            <button 
              onClick={() => setShowAgentManagement(false)}
              className="absolute -top-8 right-0 text-zinc-400 hover:text-white font-mono text-xs"
            >
              [X] CLOSE
            </button>
            <AgentManagementPanel />
          </div>
        </div>
      )}
      {showBonsaiPrism && (
        <BonsaiPrismPanel onClose={() => setShowBonsaiPrism(false)} />
      )}
      {showSecurityAdvanced && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl relative">
            <SecurityAdvancedPanel onClose={() => setShowSecurityAdvanced(false)} />
          </div>
        </div>
      )}
      {showAquiferSpectrogram && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl relative">
            <AquiferSpectrogramPanel onClose={() => setShowAquiferSpectrogram(false)} />
          </div>
        </div>
      )}
      {showUnifiedOntology && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-5xl relative">
            <UnifiedOntologyPanel onClose={() => setShowUnifiedOntology(false)} />
          </div>
        </div>
      )}
      {showDysonSphere && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl relative">
            <button 
              onClick={() => setShowDysonSphere(false)}
              className="absolute -top-12 right-0 text-zinc-400 hover:text-white"
            >
              FECHAR [X]
            </button>
            <DysonSphereTelemetry />
          </div>
        </div>
      )}
      {showPluralityMCP && (
        <PluralityMCPPanel onClose={() => setShowPluralityMCP(false)} />
      )}
      {showVelxioEmulation && (
        <VelxioEmulationPanel onClose={() => setShowVelxioEmulation(false)} />
      )}
      {showProofOfIntelligence && (
        <ProofOfIntelligencePanel onClose={() => setShowProofOfIntelligence(false)} />
      )}
      {showPhaseLawSynthesizer && (
        <PhaseLawSynthesizer onClose={() => setShowPhaseLawSynthesizer(false)} />
      )}
      {showBioSync && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
           <div className="bg-[#0a0a0c] border border-arkhe-cyan/30 rounded-xl p-8 max-w-md w-full text-center space-y-6">
              <Activity className="w-12 h-12 text-arkhe-cyan mx-auto animate-pulse" />
              <h2 className="text-xl font-bold font-mono text-arkhe-cyan uppercase tracking-widest">Bio-Sync em Progresso</h2>
              <p className="text-xs text-arkhe-muted font-mono">Sincronizando campo de fase mitocondrial com o Merkabah... Janela de 850nm aberta.</p>
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-arkhe-cyan"
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 3 }}
                  onAnimationComplete={() => setShowBioSync(false)}
                />
              </div>
              <button
                onClick={() => setShowBioSync(false)}
                className="text-xs font-mono text-arkhe-muted hover:text-white"
              >
                [CANCELAR]
              </button>
           </div>
        </div>
      )}
      {showCorvoNoir && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl relative">
            <button
              onClick={() => setShowCorvoNoir(false)}
              className="absolute -top-12 right-0 text-zinc-400 hover:text-white font-mono"
            >
              [X] FECHAR DASHBOARD
            </button>
            <CorvoNoirDashboard />
          </div>
        </div>
      )}
      {showEnterprisePlus && (
        <EnterprisePlusPanel onClose={() => setShowEnterprisePlus(false)} />
      )}
      {showDataCoherence && (
        <DataCoherenceDashboard onClose={() => setShowDataCoherence(false)} />
      )}
      {showCHSHMonitor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-5xl relative">
            <CHSHMonitorPanel onClose={() => setShowCHSHMonitor(false)} />
          </div>
        </div>
      )}
      {state.ramsey?.pendingAction && (
        <RamseyConfirmationModal
          pendingAction={state.ramsey.pendingAction}
          onClose={() => {}}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
}
