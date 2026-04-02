import React, { useEffect, useState, useRef } from 'react';
import { Waves, Activity, Droplets, ShieldAlert, Radio } from 'lucide-react';
import { motion } from 'motion/react';

export default function AquiferSpectrogramPanel({ onClose }: { onClose?: () => void }) {
  const [coherence, setCoherence] = useState(0.85);
  const [purity, setPurity] = useState(0.92);
  const [waterLevel, setWaterLevel] = useState(72.3);
  const [rechargeRate, setRechargeRate] = useState(0.32);
  const [isPlaying, setIsPlaying] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationIdRef = useRef<number | null>(null);
  const frequencyHistoryRef = useRef<number[][]>([]);

  const HISTORY_SIZE = 100;
  const FREQ_BINS = 64;

  const leftOscRef = useRef<OscillatorNode | null>(null);
  const rightOscRef = useRef<OscillatorNode | null>(null);
  const noiseNodeRef = useRef<AudioBufferSourceNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setCoherence(prev => Math.max(0, Math.min(1, prev + (Math.random() - 0.5) * 0.05)));
      setPurity(prev => Math.max(0, Math.min(1, prev + (Math.random() - 0.5) * 0.02)));
      setWaterLevel(prev => Math.max(0, Math.min(100, prev + (Math.random() - 0.5))));
      setRechargeRate(prev => Math.max(0, prev + (Math.random() - 0.5) * 0.05));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const initAudio = () => {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    if (!analyserRef.current && audioCtxRef.current) {
      analyserRef.current = audioCtxRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
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
    const analyser = analyserRef.current!;
    
    gainNodeRef.current = ctx.createGain();
    gainNodeRef.current.gain.value = 0.3;
    gainNodeRef.current.connect(analyser);
    analyser.connect(ctx.destination);

    // Binaural Beats (Delta/Theta based on coherence)
    const baseFreq = 200 + coherence * 800;
    const beatFreq = coherence > 0.8 ? 4 : 8;

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
    noiseFilter.frequency.value = 400 + (1 - purity) * 2000;
    
    const noiseGain = ctx.createGain();
    noiseGain.gain.value = (1 - purity) * 0.2;

    noiseNodeRef.current.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(gainNodeRef.current);

    leftOscRef.current.start();
    rightOscRef.current.start();
    noiseNodeRef.current.start();
    
    setIsPlaying(true);
    startSpectrogramLoop();
  };

  const stopAudio = () => {
    if (leftOscRef.current) try { leftOscRef.current.stop(); } catch(e) {}
    if (rightOscRef.current) try { rightOscRef.current.stop(); } catch(e) {}
    if (noiseNodeRef.current) try { noiseNodeRef.current.stop(); } catch(e) {}
    if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
    setIsPlaying(false);
  };

  const startSpectrogramLoop = () => {
    const draw = () => {
      if (!analyserRef.current || !canvasRef.current) return;
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);
      const currentSlice = Array.from(dataArray.slice(0, FREQ_BINS));
      frequencyHistoryRef.current.unshift(currentSlice);
      if (frequencyHistoryRef.current.length > HISTORY_SIZE) frequencyHistoryRef.current.pop();
      drawSpectrogram();
      animationIdRef.current = requestAnimationFrame(draw);
    };
    animationIdRef.current = requestAnimationFrame(draw);
  };

  const drawSpectrogram = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const w = canvas.width, h = canvas.height;
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, w, h);
    const cellW = w / FREQ_BINS;
    const cellH = h / HISTORY_SIZE;

    for (let t = 0; t < frequencyHistoryRef.current.length; t++) {
      const slice = frequencyHistoryRef.current[t];
      if (!slice) continue;
      for (let f = 0; f < FREQ_BINS; f++) {
        const intensity = slice[f] / 255;
        const r = Math.min(255, intensity * 255 * (coherence + 0.2));
        const g = Math.min(255, intensity * 255 * (0.5 + coherence * 0.5));
        const b = Math.min(255, intensity * 255 * (1 - coherence * 0.5));
        ctx.fillStyle = `rgb(${Math.floor(r)}, ${Math.floor(g)}, ${Math.floor(b)})`;
        ctx.fillRect(f * cellW, t * cellH, cellW, cellH);
      }
    }

    if (coherence < 0.618) {
      ctx.strokeStyle = '#ff3366';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(0, 0, w, h);
    }
  };

  useEffect(() => {
    if (isPlaying && audioCtxRef.current && rightOscRef.current && leftOscRef.current) {
      const baseFreq = 200 + coherence * 800;
      const beatFreq = coherence > 0.8 ? 4 : 8;
      leftOscRef.current.frequency.setTargetAtTime(baseFreq, audioCtxRef.current.currentTime, 0.5);
      rightOscRef.current.frequency.setTargetAtTime(baseFreq + beatFreq, audioCtxRef.current.currentTime, 0.5);
    }
  }, [coherence, isPlaying]);

  const exportToVLF = async () => {
    if (!audioCtxRef.current) initAudio();
    const ctx = audioCtxRef.current!;
    
    try {
      await ctx.audioWorklet.addModule('/archimedes-processor.js');
      const rfNode = new AudioWorkletNode(ctx, 'archimedes-processor');
      
      const payload = JSON.stringify({
        coherence: coherence.toFixed(4),
        purity: purity.toFixed(4),
        waterLevel: waterLevel.toFixed(1),
        timestamp: Date.now()
      });
      
      rfNode.port.postMessage({ type: 'DATA_STREAM', payload });
      rfNode.connect(ctx.destination);
      
      console.log('VLF Transmission started:', payload);
    } catch (error) {
      console.error('Failed to load AudioWorklet:', error);
    }
  };

  useEffect(() => {
    return () => {
      if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
      if (audioCtxRef.current) audioCtxRef.current.close();
    };
  }, []);

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
        <div className="text-xs font-mono text-cyan-400">
          λ₂: {coherence.toFixed(3)} | Nível: {waterLevel.toFixed(1)}%
        </div>
        {onClose && (
          <button onClick={onClose} className="text-arkhe-muted hover:text-white font-mono text-xs">
            [X] CLOSE
          </button>
        )}
      </div>

      <div className="relative z-10">
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          className="w-full h-64 bg-black/50 rounded-lg border border-cyan-500/20"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
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
        </div>

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
                <span className="text-emerald-400">{rechargeRate.toFixed(2)} m³/s</span>
              </div>
              <div className="flex justify-between text-[10px] font-mono">
                <span className="text-arkhe-muted">ZK Proof Status:</span>
                <span className="text-cyan-400">VALID (Groth16)</span>
              </div>
            </div>
            <div className="flex gap-2 mt-3">
              <button
                onClick={() => alert('Prova ZK enviada')}
                className="flex-1 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 text-[10px] font-mono uppercase rounded transition-colors"
              >
                Generate ZK Proof
              </button>
              <button onClick={exportToVLF} className="flex-1 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 text-[10px] font-mono uppercase rounded transition-colors">
                Export VLF (Archimedes)
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex gap-4 justify-between mt-auto relative z-10 border-t border-cyan-500/10 pt-3">
        <button
          onClick={toggleAudio}
          className={`flex-1 py-2 font-mono text-xs uppercase rounded border flex items-center justify-center gap-2 transition-all ${isPlaying ? 'bg-purple-500/20 border-purple-500/50 text-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.2)]' : 'bg-transparent border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10'}`}
        >
          <Radio className={`w-4 h-4 ${isPlaying ? 'animate-pulse' : ''}`} />
          {isPlaying ? 'STOP AQUIFER AUDIO' : '🎧 LISTEN TO AQUIFER'}
        </button>
      </div>
    </div>
  );
}
