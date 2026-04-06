import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { useArkheSimulation } from '../hooks/useArkheSimulation';
import { Activity, Shield, Zap, Cpu, Heart, Fingerprint } from 'lucide-react';
import TemporalLensPanel from './TemporalLensPanel';

const CorvoNoirDashboard: React.FC = () => {
  const state = useArkheSimulation();

  // Simulated time-series data for the Kuramoto R(t)
  const chartData = React.useMemo(() => {
    return Array.from({ length: 20 }, (_, i) => ({
      time: i,
      coherence: state.currentLambda * (0.95 + Math.random() * 0.1),
      threat: state.threatLevel === 'critical' ? 0.8 : 0.1,
    }));
  }, [state.currentLambda, state.threatLevel]);

  return (
    <div className="bg-neutral-950 text-neutral-100 p-6 rounded-xl border border-neutral-800 space-y-6 font-mono">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tighter text-neutral-50 flex items-center gap-2">
            <Activity className="text-emerald-500 w-6 h-6" />
            CORVO NOIR OS <span className="text-neutral-500 text-sm font-normal">v4.0.1-LUCENT</span>
          </h2>
          <p className="text-neutral-500 text-xs">AQUIFER COHERENCE REAL-TIME ANALYTICS</p>
        </div>
        <div className="flex gap-4">
          <div className="text-right">
            <p className="text-[10px] text-neutral-500 uppercase tracking-widest">Kuramoto R(t)</p>
            <p className={`text-xl font-bold ${state.currentLambda > 0.8 ? 'text-emerald-400' : 'text-amber-400'}`}>
              {(state.currentLambda * 100).toFixed(2)}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-neutral-500 uppercase tracking-widest">Threat Level</p>
            <p className={`text-xl font-bold uppercase ${state.threatLevel === 'normal' ? 'text-emerald-400' : 'text-red-500'}`}>
              {state.threatLevel}
            </p>
          </div>
        </div>

        {/* Temporal Lens & Population Feedback */}
        <div className="lg:col-span-1">
          <TemporalLensPanel state={state} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main Coherence Chart */}
        <div className="lg:col-span-2 bg-neutral-900/50 p-4 rounded-lg border border-neutral-800 h-64">
          <p className="text-[10px] text-neutral-400 mb-2 uppercase tracking-widest flex items-center gap-1">
            <Zap className="w-3 h-3 text-emerald-500" /> Phase Synchronization (θ)
          </p>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorCoh" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
              <XAxis dataKey="time" hide />
              <YAxis domain={[0, 1.2]} hide />
              <Tooltip
                contentStyle={{ backgroundColor: '#000', border: '1px solid #333', fontSize: '12px' }}
                itemStyle={{ color: '#10b981' }}
              />
              <Area
                type="monotone"
                dataKey="coherence"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorCoh)"
                strokeWidth={2}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* System Stats Sidebar */}
        <div className="space-y-4">
          <div className="bg-neutral-900/50 p-4 rounded-lg border border-neutral-800">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-5 h-5 text-blue-500" />
              <p className="text-xs font-bold uppercase tracking-widest">Security Substrate</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-[10px]">
                <span className="text-neutral-500">ZK-PROOF INTEGRITY</span>
                <span className={state.security.zkProofValid ? 'text-emerald-400' : 'text-red-400'}>
                  {state.security.zkProofValid ? 'VERIFIED' : 'FAILED'}
                </span>
              </div>
              <div className="w-full bg-neutral-800 h-1 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full" style={{ width: '92%' }}></div>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-neutral-500">YANG-BAXTER TOPOLOGY</span>
                <span className={state.topology.yangBaxterValid ? 'text-emerald-400' : 'text-red-400'}>
                  {state.topology.yangBaxterValid ? 'STABLE' : 'UNSTABLE'}
                </span>
              </div>
              <div className="w-full bg-neutral-800 h-1 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full" style={{ width: '100%' }}></div>
              </div>
            </div>
          </div>

          <div className="bg-neutral-900/50 p-4 rounded-lg border border-neutral-800">
            <div className="flex items-center gap-3 mb-2">
              <Cpu className="w-5 h-5 text-purple-500" />
              <p className="text-xs font-bold uppercase tracking-widest">Hardware Layer</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-black/40 p-2 rounded">
                <p className="text-[8px] text-neutral-500 uppercase">TMR Faults</p>
                <p className="text-sm font-bold text-neutral-300">{state.hardware.tmrFaultsCorrected}</p>
              </div>
              <div className="bg-black/40 p-2 rounded">
                <p className="text-[8px] text-neutral-500 uppercase">Shards Active</p>
                <p className="text-sm font-bold text-neutral-300">{state.mitigation.tzinorShardsAvailable}/24</p>
              </div>
            </div>
          </div>

          {/* Wetware Biometrics Sidebar */}
          <div className="bg-neutral-900/50 p-4 rounded-lg border border-neutral-800">
            <div className="flex items-center gap-3 mb-2">
              <Fingerprint className="w-5 h-5 text-emerald-500" />
              <p className="text-xs font-bold uppercase tracking-widest text-emerald-500">Wetware Biometrics</p>
            </div>
            {state.biometrics ? (
              <div className="space-y-3">
                <div className="flex justify-between items-end">
                  <div>
                    <p className="text-[8px] text-neutral-500 uppercase">Liveness Score</p>
                    <p className={`text-lg font-bold ${(state.biometrics.livenessScore || 0) > 0.8 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {((state.biometrics.livenessScore || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-[8px] text-neutral-500 uppercase">Status</p>
                    <p className={`text-xs font-bold uppercase ${state.biometrics.isAuthentic ? 'text-emerald-400' : 'text-red-400'}`}>
                      {state.biometrics.isAuthentic ? 'AUTHENTIC' : 'UNAUTHORIZED'}
                    </p>
                  </div>
                </div>

                <div>
                  <p className="text-[8px] text-neutral-500 uppercase mb-1 flex items-center gap-1">
                    <Heart className="w-2 h-2 text-red-500" /> Heartbeat Coherence
                  </p>
                  <div className="w-full bg-neutral-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-red-500 h-full transition-all duration-500"
                      style={{ width: `${(state.biometrics.heartbeatCoherence || 0) * 100}%` }}
                    ></div>
                  </div>
                </div>

                {state.biometrics.phaseSignature && (
                  <div>
                    <p className="text-[8px] text-neutral-500 uppercase mb-1">Phase Signature</p>
                    <div className="flex gap-0.5 h-4 items-end">
                      {state.biometrics.phaseSignature.map((val, idx) => (
                        <div
                          key={idx}
                          className="bg-emerald-500/50 flex-1 hover:bg-emerald-500 transition-colors"
                          style={{ height: `${val * 100}%` }}
                        ></div>
                      ))}
                    </div>
                  </div>
                )}

                <p className="text-[7px] text-neutral-600 uppercase text-center italic">
                  Last verified: {state.biometrics.lastVerification ? new Date(state.biometrics.lastVerification).toLocaleTimeString() : 'N/A'}
                </p>
              </div>
            ) : (
              <p className="text-[10px] text-neutral-500 italic">No biometric data available.</p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-black/80 border border-neutral-800 rounded p-3 h-32 overflow-y-auto scrollbar-hide">
        <p className="text-[10px] text-neutral-500 mb-2 font-bold tracking-widest uppercase">System Log (CORVO_OS_KERNEL)</p>
        {state.logs.slice(0, 10).map((log) => (
          <div key={log.id} className="flex gap-2 mb-1">
            <span className="text-neutral-600 text-[10px] shrink-0">[{new Date(log.originTime).toLocaleTimeString()}]</span>
            <span className={`text-[10px] ${log.status === 'Valid' ? 'text-neutral-400' : 'text-red-400'}`}>
              {log.threatType}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CorvoNoirDashboard;
