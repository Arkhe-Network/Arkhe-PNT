import React from 'react';
import { X, Database, Activity, AlertCircle, RefreshCcw, Layout } from 'lucide-react';
import { motion } from 'motion/react';
import { useArkheSimulation } from '../hooks/useArkheSimulation';

interface DataCoherenceDashboardProps {
  onClose: () => void;
}

export default function DataCoherenceDashboard({ onClose }: DataCoherenceDashboardProps) {
  const state = useArkheSimulation();
  const { domains, overallHealth } = state.scaData;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-[#0a0a0c] border border-blue-500/30 rounded-xl w-full max-w-4xl overflow-hidden shadow-[0_0_50px_rgba(59,130,246,0.15)] flex flex-col"
      >
        {/* Header */}
        <div className="p-4 border-b border-blue-500/20 flex justify-between items-center bg-blue-500/5">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-blue-400" />
            <h2 className="font-mono text-sm uppercase tracking-widest text-blue-400 font-bold">
              SCA-Data: Arkhe Data Coherence Platform
            </h2>
          </div>
          <button onClick={onClose} className="text-arkhe-muted hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Score */}
          <div className="md:col-span-2 space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xs font-mono uppercase tracking-widest text-arkhe-muted">Overall System Health (λ₂-data)</h3>
                <span className="text-2xl font-bold font-mono text-blue-400">{(overallHealth * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-white/5 h-4 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-blue-500"
                  animate={{ width: `${overallHealth * 100}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {domains.map((domain) => (
                <div key={domain.name} className="bg-white/5 border border-white/10 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded bg-black/40 ${domain.health === 'CRITICAL' ? 'text-arkhe-red' : 'text-blue-400'}`}>
                      <Activity className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-mono font-bold uppercase">{domain.name} Domain</div>
                      <div className="text-[10px] font-mono text-arkhe-muted">Control: {domain.action}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-mono font-bold ${domain.health === 'CRITICAL' ? 'text-arkhe-red' : 'text-blue-400'}`}>
                      {domain.lambda2.toFixed(3)}
                    </div>
                    <div className={`text-[8px] font-mono uppercase ${domain.health === 'CRITICAL' ? 'text-arkhe-red/70' : 'text-arkhe-muted'}`}>
                      {domain.health}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar Info */}
          <div className="space-y-4">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3 text-blue-400">
                <AlertCircle className="w-4 h-4" />
                <h4 className="text-[10px] font-mono uppercase font-bold text-blue-400">Critical Alerts</h4>
              </div>
              <div className="space-y-2">
                <div className="text-[9px] font-mono text-arkhe-red border-l-2 border-arkhe-red pl-2 py-1 bg-arkhe-red/5">
                  Marketing: Freshness > 5min on campaign_metrics
                </div>
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-lg p-4 space-y-3">
               <h4 className="text-[10px] font-mono uppercase font-bold text-arkhe-muted">Operational Controls</h4>
               <button className="w-full py-2 bg-blue-500 text-black font-mono text-[9px] uppercase font-bold rounded hover:bg-white transition-colors flex items-center justify-center gap-2">
                 <RefreshCcw className="w-3 h-3" />
                 Trigger Remediation
               </button>
               <button className="w-full py-2 border border-white/10 text-arkhe-text font-mono text-[9px] uppercase rounded hover:bg-white/5 transition-colors flex items-center justify-center gap-2">
                 <Layout className="w-3 h-3" />
                 View Lineage
               </button>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
              <h4 className="text-[10px] font-mono uppercase font-bold text-blue-400 mb-4">Topologia da Malha ASD (N=3)</h4>
              <div className="relative h-32 flex items-center justify-center">
                {/* Visualizing the Trinity Vortex */}
                <motion.div
                  className="w-16 h-16 border-2 border-blue-500/30 rounded-full flex items-center justify-center"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                >
                  <div className="absolute -top-1 w-2 h-2 bg-blue-400 rounded-full" title="Alpha (0 rad)" />
                  <div className="absolute bottom-1 -left-1 w-2 h-2 bg-blue-400 rounded-full" title="Beta (2.09 rad)" />
                  <div className="absolute bottom-1 -right-1 w-2 h-2 bg-blue-400 rounded-full" title="Gamma (4.18 rad)" />
                </motion.div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-[8px] font-mono text-blue-400 animate-pulse font-bold">VÓRTICE QUIRAL</div>
                </div>
              </div>
              <div className="mt-4 space-y-1">
                <div className="flex justify-between text-[8px] font-mono">
                  <span>Modo:</span>
                  <span className="text-blue-400">TRIANGULAR_VORTEX</span>
                </div>
                <div className="flex justify-between text-[8px] font-mono">
                  <span>R(t):</span>
                  <span className="text-blue-400">0.58</span>
                </div>
                <div className="flex justify-between text-[8px] font-mono">
                  <span>Resiliência:</span>
                  <span className="text-arkhe-green">TOPOLÓGICA</span>
                </div>
              </div>
            </div>

            <div className="p-2">
               <h4 className="text-[8px] font-mono uppercase text-arkhe-muted mb-2">Strategy: Edge-of-Chaos (SBM)</h4>
               <p className="text-[8px] font-mono text-arkhe-muted leading-relaxed">
                 O SCA-Data utiliza o controlador Stabilized by Memory para equilibrar throughput e latência. Circuit-breakers são ativados quando λ₂ cai abaixo de 0.90.
               </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
