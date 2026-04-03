import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Waves, Activity, Droplets, ShieldAlert, Radio, Box } from 'lucide-react';
import { motion } from 'framer-motion';
import * as THREE from 'three';

// Data types based on the protocol
interface HydroMetrics {
  timestamp: number;
  precipitation: number;      // mm
  recharge: number;           // m³/s
  pumping: number;            // m³/s
  evapotranspiration: number; // mm
  storageCurrent: number;     // m³
  storagePrevious: number;    // m³
  waterLevel: number;         // m
  spectralHash: string;       // ZK Signature
}

interface QhttpState {
  coherence: number; // 0-1 (T ≈ 1)
  eprChannel: 'ENTANGLED' | 'DECOHERED' | 'HANDSHAKING';
  meshNodeId: string;
}

export default function AquiferSpectrogramPanel({ onClose }: { onClose?: () => void }) {
  const [metrics, setMetrics] = useState<HydroMetrics | null>(null);
  const [qhttpState, setQhttpState] = useState<QhttpState>({
    coherence: 0.85,
    eprChannel: 'HANDSHAKING',
    meshNodeId: 'node-alpha-01'
  });
  const [zkStatus, setZkStatus] = useState<'idle' | 'proving' | 'verified' | 'error'>('idle');
  const [isPlaying, setIsPlaying] = useState(false);
  const [fftData, setFftData] = useState<Float32Array>(new Float32Array(64));

  const canvas3DRef = useRef<HTMLCanvasElement>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const torusKnotRef = useRef<THREE.Mesh | null>(null);
  const animationIdRef = useRef<number | null>(null);

  // Initialize Three.js Visualization
  useEffect(() => {
    if (!canvas3DRef.current) return;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(75, 600 / 400, 0.1, 1000);
    camera.position.z = 30;

    const renderer = new THREE.WebGLRenderer({
      canvas: canvas3DRef.current,
      alpha: true,
      antialias: true
    });
    renderer.setSize(600, 400);
    rendererRef.current = renderer;

    // Hopf Toroid (2,3) Geometry
    const geometry = new THREE.TorusKnotGeometry(10, 3, 100, 16, 2, 3);
    const material = new THREE.MeshPhongMaterial({
      color: 0x00d4ff,
      emissive: 0x001133,
      wireframe: true,
      transparent: true,
      opacity: 0.8
    });
    const torusKnot = new THREE.Mesh(geometry, material);
    torusKnotRef.current = torusKnot;
    scene.add(torusKnot);

    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    
    const pointLight = new THREE.PointLight(0xffffff, 1, 100);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);

      if (torusKnotRef.current) {
        const coherence = qhttpState.coherence;
        torusKnotRef.current.rotation.x += 0.01 * coherence;
        torusKnotRef.current.rotation.y += 0.02 * coherence;

        if (metrics) {
          const scale = 1 + (metrics.waterLevel / 100) * 0.5;
          torusKnotRef.current.scale.set(scale, scale, scale);
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
      renderer.dispose();
    };
  }, [qhttpState.coherence, metrics]);

  // Simulation Loop
  useEffect(() => {
    const interval = setInterval(() => {
      const newMetrics: HydroMetrics = {
        timestamp: Date.now(),
        precipitation: Math.random() * 50,
        recharge: Math.random() * 2,
        pumping: Math.random() * 1.5,
        evapotranspiration: Math.random() * 30,
        storageCurrent: 50000 + Math.random() * 1000,
        storagePrevious: 50000,
        waterLevel: 50 + Math.sin(Date.now() / 10000) * 5,
        spectralHash: Math.random().toString(36).substring(7)
      };
      setMetrics(newMetrics);

      setQhttpState(s => ({
        ...s,
        coherence: 0.8 + Math.random() * 0.2,
        eprChannel: 'ENTANGLED'
      }));

      // Simulate ZK Proving
      if (Math.random() > 0.3) {
        setZkStatus('proving');
        setTimeout(() => setZkStatus('verified'), 1500);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Audio and FFT Analysis
  const toggleAudio = () => {
    if (isPlaying) {
      if (audioCtxRef.current) audioCtxRef.current.suspend();
      setIsPlaying(false);
    } else {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        analyserRef.current = audioCtxRef.current.createAnalyser();
        analyserRef.current.fftSize = 128;
      }
      audioCtxRef.current.resume();
      setIsPlaying(true);
      updateFFT();
    }
  };

  const updateFFT = () => {
    if (!isPlaying || !analyserRef.current) return;
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    // Simulate some "hydro-acoustic" data if no real input
    const simulated = new Float32Array(64);
    for (let i = 0; i < 64; i++) {
      const freq = i * 2; // scale
      const resonance = Math.exp(-Math.pow((freq - 7.83) / 2, 2)) * 0.8 +
                        Math.exp(-Math.pow((freq - 14) / 3, 2)) * 0.4 +
                        (Math.random() * 0.05);
      simulated[i] = resonance;
    }
    setFftData(simulated);
    requestAnimationFrame(updateFFT);
  };

  const massBalance = useMemo(() => {
    if (!metrics) return 0;
    const inputs = metrics.precipitation + metrics.recharge * 86.4; // rough conversion
    const outputs = metrics.pumping * 86.4 + metrics.evapotranspiration;
    return inputs - outputs;
  }, [metrics]);

  const safetyStatus = useMemo(() => {
    if (!metrics) return 'UNKNOWN';
    if (metrics.waterLevel < 10) return 'CRITICAL_LOW';
    if (metrics.waterLevel > 100) return 'CRITICAL_HIGH';
    if (metrics.pumping > 5) return 'OVER_EXTRACTION';
    return 'OPERATIONAL';
  }, [metrics]);

  return (
    <div className="bg-[#0a0e27] text-[#e2e8f0] min-h-[600px] rounded-xl border border-[#00d4ff]/30 p-6 font-mono overflow-hidden flex flex-col gap-6">
      <header className="flex justify-between items-center border-b border-[#00d4ff] pb-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-[#00d4ff] to-[#7c3aed] bg-clip-text text-transparent">
          HYDRO-Ω <span className="text-xs border border-[#00d4ff] px-2 py-0.5 rounded ml-2 text-[#00d4ff]">HINDUCTOR LINKED</span>
        </h1>
        <div className={`text-xl font-bold transition-colors ${qhttpState.coherence > 0.9 ? 'text-[#00d4ff] shadow-[0_0_10px_rgba(0,212,255,0.5)]' : 'text-red-500'}`}>
          T = {qhttpState.coherence.toFixed(3)}
        </div>
        {onClose && (
          <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors">
            [X] CLOSE
          </button>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Phase View (3D) */}
        <div className="lg:col-span-2 relative bg-black/30 rounded-xl border border-[#00d4ff]/20 overflow-hidden">
          <canvas ref={canvas3DRef} className="w-full h-[400px]" />
          <div className="absolute top-4 left-4 flex gap-4">
            <div className="bg-black/70 p-3 rounded border-l-4 border-[#00d4ff]">
              <label className="block text-[10px] text-zinc-400">Impedância Casada</label>
              <div className="text-sm font-bold text-[#00d4ff]">{qhttpState.coherence > 0.95 ? 'Z ≈ 1' : 'Z < 1'}</div>
            </div>
            <div className="bg-black/70 p-3 rounded border-l-4 border-[#10b981]">
              <label className="block text-[10px] text-zinc-400">Canal EPR</label>
              <div className={`text-sm font-bold ${qhttpState.eprChannel === 'ENTANGLED' ? 'text-[#10b981] animate-pulse' : 'text-zinc-400'}`}>
                {qhttpState.eprChannel}
              </div>
            </div>
          </div>
        </div>

        {/* Spectrogram Panel */}
        <div className="bg-white/5 rounded-xl border border-[#7c3aed]/30 p-4 flex flex-col gap-4">
          <h3 className="text-[#7c3aed] text-sm uppercase font-bold flex items-center gap-2">
            <Activity className="w-4 h-4" /> Assinatura Espectral
          </h3>
          <div className="flex items-end h-[150px] gap-0.5 border-b border-[#7c3aed]/20 pb-1">
            {Array.from(fftData).map((amp, i) => (
              <div
                key={i}
                className="flex-1 min-w-[2px] rounded-t-sm transition-all duration-300"
                style={{
                  height: `${(amp as number) * 100}%`,
                  background: `hsl(${200 + (amp as number) * 60}, 70%, 50%)`
                }}
              />
            ))}
          </div>
          <div className="flex justify-between text-[10px] text-zinc-500">
            <span>2Hz (Schumann)</span>
            <span>14Hz (H₂O)</span>
            <span>20Hz (Limit)</span>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 mt-auto">
            <div className={`bg-white/5 p-3 rounded border-l-2 ${safetyStatus !== 'OPERATIONAL' ? 'border-amber-500 bg-amber-500/10' : 'border-[#00d4ff]'}`}>
              <label className="block text-[10px] text-zinc-400">Nível Freático</label>
              <div className="text-lg font-bold">{metrics?.waterLevel.toFixed(2) || '--'} m</div>
            </div>
            <div className={`bg-white/5 p-3 rounded border-l-2 ${massBalance < 0 ? 'border-red-500 bg-red-500/10' : 'border-[#00d4ff]'}`}>
              <label className="block text-[10px] text-zinc-400">Balanço Massa</label>
              <div className="text-lg font-bold">{massBalance.toFixed(1)} mm/d</div>
            </div>
          </div>
        </div>

        {/* ZK Panel */}
        <div className="lg:col-span-3 bg-gradient-to-r from-[#00d4ff]/10 to-[#7c3aed]/10 border border-[#00d4ff]/30 rounded-xl p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-[#00d4ff] text-sm uppercase font-bold flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" /> Prova de Conservação Hídrica
            </h3>
            <div className={`flex items-center gap-2 px-3 py-1 rounded text-xs ${zkStatus === 'verified' ? 'bg-[#10b981]/20 text-[#10b981]' : 'bg-black/30 text-zinc-400'}`}>
              <div className={`w-2 h-2 rounded-full ${zkStatus === 'proving' ? 'bg-amber-500 animate-ping' : zkStatus === 'verified' ? 'bg-[#10b981]' : 'bg-zinc-500'}`} />
              {zkStatus === 'idle' ? 'Aguardando dados...' :
               zkStatus === 'proving' ? 'Gerando prova ZK (Groth16)...' :
               zkStatus === 'verified' ? 'Prova Verificada' : 'Falha na Prova'}
            </div>
          </div>

          {zkStatus === 'verified' && (
            <div className="flex flex-wrap gap-6 text-xs">
              <div>
                <span className="text-zinc-500">Hash Espectral:</span>
                <code className="ml-2 text-[#00d4ff]">{metrics?.spectralHash.slice(0, 16)}...</code>
              </div>
              <div>
                <span className="text-zinc-500">Mesh-LLM Node:</span>
                <span className="ml-2">{qhttpState.meshNodeId}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-4">
        <button
          onClick={toggleAudio}
          className={`flex-1 py-3 rounded-lg border font-bold uppercase transition-all flex items-center justify-center gap-2 ${isPlaying ? 'bg-purple-500/20 border-purple-500 text-purple-400' : 'bg-[#00d4ff]/10 border-[#00d4ff] text-[#00d4ff] hover:bg-[#00d4ff]/20'}`}
        >
          <Radio className={isPlaying ? 'animate-pulse' : ''} />
          {isPlaying ? 'Desativar Monitoramento Acústico' : 'Ativar Monitoramento Acústico'}
        </button>
      </div>

      {safetyStatus === 'CRITICAL_LOW' && (
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="fixed bottom-8 right-8 max-w-sm bg-red-600/90 text-white p-4 rounded-lg border border-red-400 shadow-2xl z-50 font-bold"
        >
          ⚠️ MODO DE ALERTA GEOFENCE: Nível crítico. Autocomplete System Decontamination ativado. Nó desconectado da federação.
        </motion.div>
      )}
    </div>
  );
}
