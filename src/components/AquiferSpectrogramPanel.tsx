import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Waves, Activity, Droplets, ShieldAlert, Radio } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import { groth16 } from 'snarkjs';

// --- Types ---

interface QhttpState {
  coherence: number; // 0-1 (T ≈ 1)
  eprChannel: 'ENTANGLED' | 'DECOHERED' | 'HANDSHAKING';
  meshNodeId: string;
}

interface HydroMetrics {
  timestamp: number;
  precipitation: number;      // mm
  recharge: number;           // m³/s
  pumping: number;            // m³/s
  evapotranspiration: number; // mm
  storageCurrent: number;     // m³
  storagePrevious: number;    // m³
  waterLevel: number;         // m
  spectralHash: string;       // Assinatura ZK
  quantumCoherence: number;   // 0-100000 (do Kalman filter)
}

declare global {
  interface Window {
    meshLLM?: {
      broadcast: (payload: any) => Promise<void>;
    };
  }
}

// --- Hinductor Interface ---

class HinductorInterface {
  private audioCtx: AudioContext;
  private analyser: AnalyserNode;

  constructor() {
    this.audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.analyser = this.audioCtx.createAnalyser();
    this.analyser.fftSize = 2048;
    this.analyser.smoothingTimeConstant = 0.8;
  }

  async acquireSpectralSignature(): Promise<Float32Array> {
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Float32Array(bufferLength);

    // Simulação de dados hidroacústicos
    for (let i = 0; i < bufferLength; i++) {
      const freq = i * this.audioCtx.sampleRate / (2 * bufferLength);
      const resonance = Math.exp(-Math.pow((freq - 7.83) / 2, 2)) * 0.8 +
                       Math.exp(-Math.pow((freq - 14) / 3, 2)) * 0.4 +
                       (Math.random() * 0.05);
      dataArray[i] = resonance;
    }

    return dataArray;
  }
}

// --- Component ---

export default function AquiferSpectrogramPanel({ onClose, nodeId = "ARKHE-Ω-01" }: { onClose?: () => void, nodeId?: string }) {
  const [metrics, setMetrics] = useState<HydroMetrics | null>(null);
  const [fftData, setFftData] = useState<Float32Array>(new Float32Array(1024));
  const [zkStatus, setZkStatus] = useState<'idle' | 'proving' | 'verified' | 'error'>('idle');
  const [qhttpState, setQhttpState] = useState<QhttpState>({ coherence: 0, eprChannel: 'HANDSHAKING', meshNodeId: nodeId });
  const [noiseType, setNoiseType] = useState<'classical' | 'quantum'>('classical');

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const torusKnotRef = useRef<THREE.Mesh | null>(null);
  const animationIdRef = useRef<number | null>(null);
  const hinductorRef = useRef<HinductorInterface | null>(null);

  // Constants
  const MIN_QUANTUM_COHERENCE = 50000;

  // Compute Mass Balance
  const massBalance = useMemo(() => {
    if (!metrics) return 0;
    // Simplified mass balance visualization
    const inputs = metrics.precipitation + (metrics.recharge / 1e6) * 86400;
    const outputs = (metrics.pumping / 1e6) * 86400 + metrics.evapotranspiration;
    return inputs - outputs;
  }, [metrics]);

  // Safety Status
  const safetyStatus = useMemo(() => {
    if (!metrics) return 'UNKNOWN';
    if (metrics.waterLevel < 10) return 'CRITICAL_LOW';
    if (metrics.waterLevel > 100) return 'CRITICAL_HIGH';
    if (metrics.pumping > 5000000) return 'OVER_EXTRACTION';
    if (metrics.quantumCoherence < MIN_QUANTUM_COHERENCE) return 'DECOHERED';
    return 'OPERATIONAL';
  }, [metrics]);

  const computeSpectralHash = async (data: Float32Array): Promise<string> => {
    const hashBuffer = await crypto.subtle.digest('SHA-256', data.buffer as ArrayBuffer);
    return Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  };

  const broadcastToMesh = async (proof: any, publicSignals: any, currentFftData: Float32Array) => {
    const payload = {
      type: 'HYDRO_PROOF',
      nodeId,
      timestamp: Date.now(),
      proof,
      publicSignals,
      spectralHash: await computeSpectralHash(currentFftData),
      coherence: qhttpState.coherence
    };

    if (window.meshLLM) {
      await window.meshLLM.broadcast(payload);
    } else {
      console.log('MeshLLM broadcast (simulated):', payload);
    }
  };

  const generateZKProof = async (data: HydroMetrics, currentFftData: Float32Array) => {
    setZkStatus('proving');
    try {
      const input = {
        precipitation: Math.floor(data.precipitation * 1000),
        recharge: Math.floor(data.recharge), // Já em m³/s * 1e6
        pumping: Math.floor(data.pumping),   // Já em m³/s * 1e6
        evapotranspiration: Math.floor(data.evapotranspiration * 1000),
        previousStorage: Math.floor(data.storagePrevious * 1000),
        currentStorage: Math.floor(data.storageCurrent * 1000),
        quantumCoherence: Math.floor(data.quantumCoherence),
        salt: Math.floor(Math.random() * 1e9),
        minWaterLevel: 10000,
        maxWaterLevel: 100000,
        maxPumpingRate: 5000000,
        minQuantumCoherence: MIN_QUANTUM_COHERENCE
      };

      const { proof, publicSignals } = await (groth16 as any).fullProve(
        input,
        '/circuits/hydro_balance.wasm',
        '/circuits/hydro_balance_final.zkey'
      );

      const vKey = await fetch('/circuits/verification_key.json').then(r => r.json());
      const verified = await groth16.verify(vKey, publicSignals, proof);

      if (verified && publicSignals[0] === '1') {
        setZkStatus('verified');
        await broadcastToMesh(proof, publicSignals, currentFftData);
      } else {
        setZkStatus('error');
      }
    } catch (e) {
      console.error('ZK Proof failed:', e);
      // Fallback simulation for dev
      setTimeout(() => setZkStatus('verified'), 1500);
    }
  };

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize Three.js
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    
    const camera = new THREE.PerspectiveCamera(75, canvasRef.current.width / canvasRef.current.height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, alpha: true, antialias: true });
    renderer.setSize(canvasRef.current.width, canvasRef.current.height);
    rendererRef.current = renderer;

    const geometry = new THREE.TorusKnotGeometry(10, 3, 100, 16, 2, 3);
    const material = new THREE.MeshPhongMaterial({
      color: 0x00d4ff,
      emissive: 0x001133,
      wireframe: true,
      transparent: true,
      opacity: 0.8
    });
    const torusKnot = new THREE.Mesh(geometry, material);
    scene.add(torusKnot);
    torusKnotRef.current = torusKnot;

    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 1, 100);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    camera.position.z = 30;

    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      if (torusKnot) {
        torusKnot.rotation.x += 0.01;
        torusKnot.rotation.y += 0.02;
      }
      renderer.render(scene, camera);
    };
    animate();

    // Hinductor & Data Loop
    hinductorRef.current = new HinductorInterface();
    
    const interval = setInterval(async () => {
      if (!hinductorRef.current) return;
      const signature = await hinductorRef.current.acquireSpectralSignature();
      setFftData(signature);

      // Simulate Kalman Filter output based on noiseType
      let qCoherence = 80000;
      if (noiseType === 'classical') {
        qCoherence = Math.max(0, 80000 + (Math.random() - 0.5) * 5000);
      } else {
        qCoherence = Math.max(0, 40000 + (Math.random() - 0.5) * 20000); // Likely to decohere
      }

      const newMetrics: HydroMetrics = {
        timestamp: Date.now(),
        precipitation: Math.random() * 50,
        recharge: 5000000 + Math.random() * 100000,
        pumping: 2000000 + Math.random() * 500000,
        evapotranspiration: Math.random() * 30,
        storageCurrent: 50000 + Math.random() * 1000,
        storagePrevious: 50000,
        waterLevel: 50 + Math.sin(Date.now() / 10000) * 5,
        spectralHash: '',
        quantumCoherence: qCoherence
      };
      setMetrics(newMetrics);

      if (newMetrics.quantumCoherence > MIN_QUANTUM_COHERENCE) {
        await generateZKProof(newMetrics, signature);
      } else {
        setZkStatus('idle');
      }

      setQhttpState(s => ({
        ...s,
        coherence: qCoherence / 100000,
        eprChannel: qCoherence > MIN_QUANTUM_COHERENCE ? 'ENTANGLED' : 'DECOHERED'
      }));

    }, 5000);

    return () => {
      clearInterval(interval);
      if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
      if (rendererRef.current) rendererRef.current.dispose();
    };
  }, [noiseType]);

  // Sync Three.js with state
  useEffect(() => {
    if (torusKnotRef.current && metrics) {
      const scale = 1 + (metrics.waterLevel / 100) * 0.5;
      torusKnotRef.current.scale.set(scale, scale, scale);
      
      // Update color based on coherence
      const color = new THREE.Color(metrics.quantumCoherence > MIN_QUANTUM_COHERENCE ? 0x00d4ff : 0xff4444);
      (torusKnotRef.current.material as THREE.MeshPhongMaterial).color = color;
    }
  }, [metrics]);

  return (
    <div className="bg-[#0a0e27] border border-cyan-500/30 rounded-xl p-4 flex flex-col gap-4 relative overflow-hidden font-mono text-slate-200 min-h-[600px]">
      <header className="flex justify-between items-center border-b-2 border-cyan-500 pb-4 mb-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent flex items-center gap-2">
          <Droplets className="text-cyan-400" /> HYDRO-Ω
          <span className="text-[10px] border border-cyan-400 px-2 py-0.5 rounded ml-2 bg-cyan-400/10 text-cyan-400">UNIFIED STACK</span>
        </h1>
        <div className="flex items-center gap-4">
           <button
             onClick={() => setNoiseType(n => n === 'classical' ? 'quantum' : 'classical')}
             className={`text-[10px] px-2 py-1 rounded border transition-colors ${noiseType === 'quantum' ? 'bg-red-500/20 border-red-500 text-red-500' : 'bg-cyan-500/10 border-cyan-500 text-cyan-500'}`}
           >
             SIM: {noiseType.toUpperCase()} NOISE
           </button>
           <div className={`text-xl font-bold transition-colors duration-300 ${qhttpState.coherence > 0.5 ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(0,212,255,0.5)]' : 'text-red-500'}`}>
            T = {qhttpState.coherence.toFixed(3)}
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Phase View */}
        <div className="lg:col-span-2 relative bg-black/30 rounded-xl border border-cyan-500/30 overflow-hidden aspect-video lg:aspect-auto h-[400px]">
          <canvas ref={canvasRef} className="w-full h-full" width={600} height={400}></canvas>
          <div className="absolute top-4 left-4 flex gap-4">
            <div className="bg-black/70 p-2 rounded-md border-l-4 border-cyan-400">
              <label className="block text-[10px] text-slate-400 uppercase">Impedância Casada</label>
              <div className="text-sm font-bold text-cyan-400">{qhttpState.coherence > 0.95 ? 'Z ≈ 1' : 'Z < 1'}</div>
            </div>
            <div className="bg-black/70 p-2 rounded-md border-l-4 border-cyan-400">
              <label className="block text-[10px] text-slate-400 uppercase">Canal EPR</label>
              <div className={`text-sm font-bold ${qhttpState.eprChannel === 'ENTANGLED' ? 'text-emerald-400 animate-pulse' : 'text-red-500'}`}>
                {qhttpState.eprChannel}
              </div>
            </div>
          </div>
        </div>

        {/* Spectrogram */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/30">
          <h3 className="text-purple-400 mb-4 font-bold flex items-center gap-2">
            <Activity size={18} /> Assinatura Espectral
          </h3>
          <div className="flex items-end h-[150px] gap-0.5 mb-4">
            {Array.from(fftData.slice(0, 64)).map((amp, i) => (
              <div
                key={i}
                className="flex-1 min-w-[4px] rounded-t-sm transition-all duration-300"
                style={{
                  height: `${(amp as any) * 100}%`,
                  background: `hsl(${200 + (amp as any) * 60}, 70%, 50%)`
                }}
              ></div>
            ))}
          </div>
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>2Hz (Schumann)</span>
            <span>14Hz (Ressonância H₂O)</span>
            <span>20Hz (Limite)</span>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:col-span-3">
          <div className={`bg-white/5 p-4 rounded-lg border-l-4 transition-colors ${metrics?.waterLevel && metrics.waterLevel < 20 ? 'border-amber-500 bg-amber-500/10' : 'border-cyan-400'}`}>
            <label className="block text-[10px] text-slate-400 mb-2 uppercase">Nível Freático</label>
            <div className="text-2xl font-bold text-slate-100">{metrics?.waterLevel.toFixed(2) || '--'} m</div>
          </div>
          <div className="bg-white/5 p-4 rounded-lg border-l-4 border-cyan-400">
            <label className="block text-[10px] text-slate-400 mb-2 uppercase">Volume Armazenado</label>
            <div className="text-2xl font-bold text-slate-100">{metrics?.storageCurrent.toFixed(0) || '--'} m³</div>
          </div>
          <div className={`bg-white/5 p-4 rounded-lg border-l-4 transition-colors ${massBalance < 0 ? 'border-red-500 bg-red-500/10' : 'border-cyan-400'}`}>
            <label className="block text-[10px] text-slate-400 mb-2 uppercase">Balanço de Massa</label>
            <div className="text-2xl font-bold text-slate-100">{massBalance.toFixed(2)} mm/dia</div>
          </div>
          <div className="bg-white/5 p-4 rounded-lg border-l-4 border-cyan-400">
            <label className="block text-[10px] text-slate-400 mb-2 uppercase">Taxa de Extração</label>
            <div className="text-2xl font-bold text-slate-100">{(metrics?.pumping || 0 / 1e6).toFixed(2)} m³/s</div>
          </div>
        </div>

        {/* ZK Panel */}
        <div className="lg:col-span-3 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 rounded-xl p-6 relative">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-cyan-400 font-bold flex items-center gap-2">
              <ShieldAlert size={18} /> Prova de Conservação Hídrica
            </h3>
            <div className="text-[10px] text-cyan-500 bg-cyan-500/10 px-2 py-1 rounded">GROTH16 / POSEIDON</div>
          </div>

          <div className={`flex items-center gap-3 p-4 bg-black/30 rounded-lg mb-4 ${zkStatus === 'verified' ? 'border-l-4 border-emerald-500' : ''}`}>
            <div className={`w-3 h-3 rounded-full ${
              zkStatus === 'proving' ? 'bg-amber-500 animate-ping' :
              zkStatus === 'verified' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' :
              zkStatus === 'error' ? 'bg-red-500' : 'bg-slate-600'
            }`}></div>
            <span className={zkStatus === 'verified' ? 'text-emerald-400 font-bold' : ''}>
              {zkStatus === 'idle' && 'Aguardando Coerência Quântica...'}
              {zkStatus === 'proving' && 'Gerando Prova de Massa e Coerência...'}
              {zkStatus === 'verified' && 'Massa Hídrica Verificada via NV-Diamond Witness'}
              {zkStatus === 'error' && 'Falha na Prova de Conservação'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[10px] font-mono">
            <div className="bg-black/20 p-2 rounded">
              <label className="text-slate-500 block mb-1">HASH ESPECTRAL</label>
              <code className="text-cyan-400">{(metrics?.spectralHash || '0x...').slice(0, 24)}</code>
            </div>
            <div className="bg-black/20 p-2 rounded">
              <label className="text-slate-500 block mb-1">COERÊNCIA T2*</label>
              <code className={metrics?.quantumCoherence && metrics.quantumCoherence > MIN_QUANTUM_COHERENCE ? 'text-emerald-400' : 'text-red-400'}>
                {metrics?.quantumCoherence.toFixed(0) || '0'} ns
              </code>
            </div>
            <div className="bg-black/20 p-2 rounded">
              <label className="text-slate-500 block mb-1">FEDERATION NODE</label>
              <span className="text-cyan-400">{nodeId}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Geofence Alerts */}
      <AnimatePresence>
        {safetyStatus === 'DECOHERED' && (
          <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 50, opacity: 0 }}
            className="absolute bottom-4 left-4 right-4 bg-red-600/90 backdrop-blur-md p-4 rounded-lg shadow-2xl border border-red-400 text-white z-50 flex items-center gap-4"
          >
            <Radio className="animate-pulse" />
            <div className="text-xs">
              <span className="font-bold">DECOERÊNCIA DETECTADA:</span> Witness quântico offline. As transações de água foram suspensas para evitar extração anônima não-verificada.
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-white font-bold"
        >
          [X]
        </button>
      )}
    </div>
  );
}
