import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Zap } from 'lucide-react';

interface SlashingRecord {
  incidentHash: string;
  nodeId: string;
  timestamp: string;
  t2Before: number;
  t2After: number;
  severity: 0 | 1 | 2 | 3;
  verdict: 'Innocent' | 'Negligent' | 'Malicious' | 'Ban';
  penalty: string;
  environmentalFactors: {
    solarFlux: number;
    seismic: number;
    rfInterference: number;
  };
  zkProofValid: boolean;
}

export const QuantumSlashingPanel: React.FC = () => {
  const [incidents, setIncidents] = React.useState<SlashingRecord[]>([
    {
      incidentHash: '0x8f2d...b4e1',
      nodeId: 'QD-SYD-0xA4',
      timestamp: new Date().toISOString(),
      t2Before: 52400,
      t2After: 12100,
      severity: 2,
      verdict: 'Malicious',
      penalty: '3.5 ARKHE',
      environmentalFactors: { solarFlux: 120, seismic: 1.2, rfInterference: 45 },
      zkProofValid: true
    },
    {
      incidentHash: '0x1c9b...a8f3',
      nodeId: 'QD-LON-0xB2',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      t2Before: 55200,
      t2After: 48500,
      severity: 0,
      verdict: 'Innocent',
      penalty: '0 ARKHE',
      environmentalFactors: { solarFlux: 850, seismic: 2.1, rfInterference: 110 },
      zkProofValid: true
    }
  ]);

  return (
    <div className="bg-[#0a0e27] text-[#e2e8f0] p-6 rounded-xl border border-arkhe-border font-mono text-xs">
      <header className="flex justify-between items-center mb-6 border-b border-arkhe-border pb-4">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6 text-arkhe-red" />
          <div>
            <h2 className="text-lg font-bold tracking-widest uppercase">Conselho de Decoerência</h2>
            <p className="text-[8px] text-arkhe-muted uppercase">Justiça Termodinâmica e Slashing Quântico</p>
          </div>
        </div>
        <div className="flex gap-4">
          <div className="text-right">
            <div className="text-[8px] text-arkhe-muted uppercase">Incidentes 24h</div>
            <div className="text-sm font-bold">12</div>
          </div>
          <div className="text-right">
            <div className="text-[8px] text-arkhe-muted uppercase">Taxa de Inocência</div>
            <div className="text-sm font-bold text-emerald-400">25%</div>
          </div>
        </div>
      </header>

      <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
        {incidents.map((incident, idx) => (
          <div key={idx} className={`p-4 rounded-lg bg-white/5 border-l-4 ${
            incident.verdict === 'Innocent' ? 'border-emerald-500' :
            incident.verdict === 'Negligent' ? 'border-amber-500' : 'border-red-500'
          }`}>
            <div className="flex justify-between items-start mb-3">
              <span className="text-arkhe-cyan font-bold">{incident.incidentHash}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                incident.verdict === 'Innocent' ? 'bg-emerald-500/20 text-emerald-400' :
                incident.verdict === 'Malicious' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
              }`}>
                {incident.verdict.toUpperCase()}
              </span>
            </div>

            <div className="space-y-2 mb-3">
              <div className="flex items-center gap-2 h-4 bg-black/40 rounded overflow-hidden">
                <div className="bg-cyan-500 h-full flex items-center px-2 text-[8px]" style={{ width: `${(incident.t2Before/600).toFixed(0)}%` }}>
                  T2* Baseline: {(incident.t2Before/1000).toFixed(1)}μs
                </div>
              </div>
              <div className="flex items-center gap-2 h-4 bg-black/40 rounded overflow-hidden">
                <div className="bg-red-500 h-full flex items-center px-2 text-[8px]" style={{ width: `${(incident.t2After/600).toFixed(0)}%` }}>
                  T2* Fall: {(incident.t2After/1000).toFixed(1)}μs
                </div>
              </div>
            </div>

            <div className="flex justify-between items-end">
              <div className="flex flex-col gap-1">
                {incident.verdict === 'Innocent' ? (
                  <div className="flex gap-2 text-[8px] text-white/50">
                    <span>SOLAR: {incident.environmentalFactors.solarFlux}</span>
                    <span>SEISMIC: {incident.environmentalFactors.seismic}</span>
                  </div>
                ) : (
                  <div className="text-red-400 font-bold">PENALIDADE: {incident.penalty}</div>
                )}
                <div className="flex items-center gap-1 text-[8px] text-emerald-400">
                  <CheckCircle className="w-2 h-2" />
                  <span>ZK-PROOF VERIFICADA</span>
                </div>
              </div>
              <div className="text-[8px] text-arkhe-muted">
                {incident.nodeId} // {new Date(incident.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
