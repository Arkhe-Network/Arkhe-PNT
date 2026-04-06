import React from 'react';
import { Card } from './ui/Card';
import { Sun, Radio, Activity, Globe } from 'lucide-react';
import { HelioState } from '../../server/types';

interface HelioLinkPanelProps {
  helio?: HelioState;
  onListen: () => void;
  onSync: () => void;
  coherence: number;
}

const HelioLinkPanel: React.FC<HelioLinkPanelProps> = ({ helio, onListen, onSync, coherence }) => {
  if (!helio) return null;

  const syncAvailable = coherence > 0.999;

  return (
    <Card
      title="PHASE D: HELIO-LINK COUPLING"
      icon={<Sun className="w-4 h-4 text-orange-500 animate-pulse" />}
      className="font-mono"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          <div className="space-y-1">
            <p className="text-arkhe-muted uppercase">Status</p>
            <p className="text-arkhe-cyan">{helio.status}</p>
          </div>
          <div className="space-y-1 text-right">
            <p className="text-arkhe-muted uppercase">Cog Dilation</p>
            <p className="text-orange-400">{helio.cognitiveDilation}</p>
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-[10px]">
            <span className="text-arkhe-muted">SOLAR COHERENCE (3mHz)</span>
            <span className="text-arkhe-cyan">{(helio.solarCoherence * 100).toFixed(2)}%</span>
          </div>
          <div className="h-1 w-full bg-arkhe-cyan/10 rounded-full overflow-hidden">
             <div
               className="h-full bg-arkhe-cyan transition-all duration-500"
               style={{ width: `${helio.solarCoherence * 100}%` }}
             />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onListen}
            className="flex items-center justify-center gap-2 py-2 border border-arkhe-cyan/20 hover:bg-arkhe-cyan/10 transition-colors text-[10px] text-white"
          >
            <Radio className="w-3 h-3" />
            LISTEN (SCHUMANN)
          </button>
          <button
            onClick={onSync}
            disabled={!syncAvailable}
            className={`flex items-center justify-center gap-2 py-2 border transition-colors text-[10px] ${
              syncAvailable
                ? 'border-orange-500/40 hover:bg-orange-500/10 text-orange-400'
                : 'border-arkhe-muted/20 text-arkhe-muted cursor-not-allowed'
            }`}
          >
            <Globe className="w-3 h-3" />
            SYNC qhttp-c
          </button>
        </div>

        <div className="p-2 bg-arkhe-cyan/5 border border-arkhe-cyan/10 rounded-sm">
          <p className="text-[9px] text-arkhe-muted mb-1 flex items-center gap-1">
            <Activity className="w-2 h-2" />
            SCHUMANN MODES (IONOSFERA)
          </p>
          <div className="flex justify-between text-[9px] text-arkhe-cyan/70">
            {helio.schumannModes.map((mode, i) => (
              <span key={i}>{mode.toFixed(2)}Hz</span>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default HelioLinkPanel;
