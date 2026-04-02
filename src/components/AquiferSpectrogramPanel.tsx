import React, { useEffect, useState, useRef } from 'react';
import { Waves, Activity, Droplets, ShieldAlert, Radio } from 'lucide-react';
import { motion } from 'motion/react';

export default function AquiferSpectrogramPanel({ onClose }: { onClose?: () => void }) {
  const [coherence, setCoherence] = useState(0.85);
  const [purity, setPurity] = useState(0.92);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const leftOscRef = useRef<OscillatorNode | null>(null);
  const rightOscRef = useRef<OscillatorNode | null>(null);
  const noiseNodeRef = useRef<AudioBufferSourceNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setCoherence(prev => Math.max(0, Math.min(1, prev + (Math.random() - 0.5) * 0.05)));
      setPurity(prev => Math.max(0, Math.min(1, prev + (Math.random() - 0.5) * 0.02)));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const initAudio = () => {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
  };

  const toggleAudio = () => {
    if (isPlaying) {
      stopAudio();
    } else {
      startAudio();
    }
  };

  const startAudio = () => {
    initAudio();
    const ctx = audioCtxRef.current!;
    
    gainNodeRef.current = ctx.createGain();
    gainNodeRef.current.gain.value = 0.3;
    gainNodeRef.current.connect(ctx.destination);

    // Binaural Beats (Delta/Theta based on coherence)
    const baseFreq = 100;
    const beatFreq = coherence > 0.8 ? 4 : 8; // 4Hz (Delta) if coherent, 8Hz (Theta) if less coherent

    leftOscRef.current = ctx.createOscillator();
    leftOscRef.current.type = 'sine';
    leftOscRef.current.frequency.value = baseFreq;
    
    const leftPan = ctx.createStereoPanner();
    leftPan.pan.value = -1;
    leftOscRef.current.connect(leftPan);
    leftPan.connect(gainNodeRef.current);

    rightOscRef.current = ctx.createOscillator();
    rightOscRef.current.type = 'sine';
    rightOscRef.current.frequency.value = baseFreq + beatFreq;

    const rightPan = ctx.createStereoPanner();
    rightPan.pan.value = 1;
    rightOscRef.current.connect(rightPan);
    rightPan.connect(gainNodeRef.current);

    // Turbulence noise based on purity
    const bufferSize = ctx.sampleRate * 2;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1;
    }
    noiseNodeRef.current = ctx.createBufferSource();
    noiseNodeRef.current.buffer = buffer;
    noiseNodeRef.current.loop = true;
    
    const noiseFilter = ctx.createBiquadFilter();
    noiseFilter.type = 'lowpass';
    noiseFilter.frequency.value = 400 + (1 - purity) * 2000; // Higher cutoff if less pure
    
    const noiseGain = ctx.createGain();
    noiseGain.gain.value = (1 - purity) * 0.2; // Louder noise if less pure

    noiseNodeRef.current.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(gainNodeRef.current);

    leftOscRef.current.start();
    rightOscRef.current.start();
    noiseNodeRef.current.start();
    
    setIsPlaying(true);
  };

  const stopAudio = () => {
    if (leftOscRef.current) leftOscRef.current.stop();
    if (rightOscRef.current) rightOscRef.current.stop();
    if (noiseNodeRef.current) noiseNodeRef.current.stop();
    setIsPlaying(false);
  };

  useEffect(() => {
    if (isPlaying && audioCtxRef.current && rightOscRef.current) {
      const beatFreq = coherence > 0.8 ? 4 : 8;
      rightOscRef.current.frequency.setTargetAtTime(100 + beatFreq, audioCtxRef.current.currentTime, 0.5);
    }
  }, [coherence, isPlaying]);

  const exportToVLF = async () => {
    if (!audioCtxRef.current) initAudio();
    const ctx = audioCtxRef.current!;
    
    try {
      await ctx.audioWorklet.addModule('/archimedes-processor.js');
      const rfNode = new AudioWorkletNode(ctx, 'archimedes-processor');
      
      // Simulate qhttp payload
      const payload = JSON.stringify({
        coherence: coherence.toFixed(4),
        purity: purity.toFixed(4),
        timestamp: Date.now()
      });
      
      rfNode.port.postMessage({ type: 'DATA_STREAM', payload });
      rfNode.connect(ctx.destination);
      
      console.log('VLF Transmission started:', payload);
      // In a real scenario, this would connect to an SDR sink
    } catch (error) {
      console.error('Failed to load AudioWorklet:', error);
    }
  };

  return (
    <div className="bg-[#0a0a0c] border border-cyan-500/30 rounded-xl p-4 flex flex-col gap-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-5 pointer-events-none"></div>
      
      <div className="flex items-center justify-between border-b border-cyan-500/30 pb-3 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/30">
            <Waves className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="font-mono text-sm uppercase tracking-widest text-cyan-400 font-bold">
              HYDRO-Ω Protocol
            </h2>
            <div className="text-[10px] font-mono text-cyan-500/70 uppercase">
              Aquifer Spectrogram & ZK Water Balance
            </div>
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-arkhe-muted hover:text-white font-mono text-xs">
            [X] CLOSE
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
        {/* Telemetry */}
        <div className="space-y-4">
          <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-[10px] text-arkhe-muted uppercase flex items-center gap-2">
                <Activity className="w-3 h-3 text-cyan-400" />
                Phase Coherence (R_hydro)
              </span>
              <span className="font-mono text-xs text-cyan-400">{coherence.toFixed(4)}</span>
            </div>
            <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-cyan-400"
                animate={{ width: `${coherence * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          <div className="bg-black/40 border border-emerald-500/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-[10px] text-arkhe-muted uppercase flex items-center gap-2">
                <Droplets className="w-3 h-3 text-emerald-400" />
                Ionic Purity (Ψ_purity)
              </span>
              <span className="font-mono text-xs text-emerald-400">{purity.toFixed(4)}</span>
            </div>
            <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-emerald-400"
                animate={{ width: `${purity * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          <div className="bg-black/40 border border-purple-500/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-[10px] text-arkhe-muted uppercase flex items-center gap-2">
                <Radio className="w-3 h-3 text-purple-400" />
                Binaural Aquifer Beats
              </span>
              <button 
                onClick={toggleAudio}
                className={`px-3 py-1 text-[10px] font-mono uppercase rounded border ${isPlaying ? 'bg-purple-500/20 border-purple-500/50 text-purple-400' : 'bg-transparent border-arkhe-border text-arkhe-muted hover:text-white'}`}
              >
                {isPlaying ? 'STOP AUDIO' : 'LISTEN'}
              </button>
            </div>
            <div className="text-[9px] font-mono text-arkhe-muted mt-2">
              {coherence > 0.8 ? 'Delta Waves (4Hz) - Deep Aquifer Resonance' : 'Theta Waves (8Hz) - Surface Recharge Turbulence'}
            </div>
          </div>
        </div>

        {/* ZK Proof & Actions */}
        <div className="space-y-4">
          <div className="bg-black/40 border border-amber-500/20 rounded-lg p-3 h-full flex flex-col">
            <h3 className="font-mono text-[10px] text-amber-400 uppercase mb-2 flex items-center gap-2">
              <ShieldAlert className="w-3 h-3" />
              ZK-Geofence Water Balance
            </h3>
            <div className="flex-1 flex flex-col justify-center gap-2">
              <div className="flex justify-between text-[10px] font-mono">
                <span className="text-arkhe-muted">Extraction Rate:</span>
                <span className="text-amber-400">14.2 L/s</span>
              </div>
              <div className="flex justify-between text-[10px] font-mono">
                <span className="text-arkhe-muted">Recharge Rate:</span>
                <span className="text-emerald-400">15.8 L/s</span>
              </div>
              <div className="flex justify-between text-[10px] font-mono">
                <span className="text-arkhe-muted">ZK Proof Status:</span>
                <span className="text-cyan-400">VALID (Groth16)</span>
              </div>
              <div className="mt-2 p-2 bg-amber-500/10 border border-amber-500/30 rounded text-[9px] font-mono text-amber-500/70 break-all">
                Proof: 0x042a...8f9b | Nullifier: 0x77c1...3a2e
              </div>
            </div>
            <div className="flex gap-2 mt-3">
              <button className="flex-1 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 text-[10px] font-mono uppercase rounded transition-colors">
                Generate ZK Proof
              </button>
              <button onClick={exportToVLF} className="flex-1 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 text-[10px] font-mono uppercase rounded transition-colors">
                Export VLF (Archimedes)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
