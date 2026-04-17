/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { X, Play, Pause, Square, Radio, Shield, Zap, Globe, Clock, Rewind, FastForward } from 'lucide-react';
import React, { useState, useEffect, useRef } from 'react';
// @ts-ignore
import shaka from 'shaka-player';

interface TemporalStreamViewerProps {
  onClose: () => void;
  streamId?: string;
}

export default function TemporalStreamViewer({ onClose, streamId = 'ARKHE-O-01' }: TemporalStreamViewerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLive, setIsLive] = useState(true);
  const [coherence, setCoherence] = useState(0.992);
  const [latencyMs, setLatencyMs] = useState(42);
  const [logs, setLogs] = useState<string[]>([]);
  const [activeChannel, setActiveChannel] = useState('PNT-1');

  const videoRef = useRef<HTMLVideoElement>(null);
  const playerRef = useRef<any>(null);

  const addLog = (msg: string) => {
    setLogs(prev => [`[${new Date().toISOString().split('T')[1].slice(0, 8)}] ${msg}`, ...prev].slice(0, 5));
  };

  useEffect(() => {
    if (!videoRef.current) return;

    shaka.polyfill.installAll();

    if (shaka.Player.isBrowserSupported()) {
      const player = new shaka.Player(videoRef.current);
      playerRef.current = player;

      player.addEventListener('error', (event: any) => {
        console.error('Shaka error:', event.detail);
        addLog(`STREAM ERROR: ${event.detail?.code}`);
      });

      // Load a sample stream (HLS/DASH)
      // For this demo, we'll just use a placeholder video if the URL fails
      const manifestUri = 'https://storage.googleapis.com/shaka-demo-assets/angel-one/dash.mpd';
      
      player.load(manifestUri).then(() => {
        addLog(`CONNECTED TO TEMPORAL STREAM: ${streamId}`);
        addLog('ZK-SYNC CHANNEL ESTABLISHED.');
      }).catch((e: any) => {
        addLog('FAILED TO LOAD MANIFEST. USING FALLBACK CHANNEL.');
      });
    }

    return () => {
      playerRef.current?.destroy();
    };
  }, [streamId]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-4">
      <div className="w-full max-w-5xl bg-[#0a0a0c] border border-[#7c3aed]/30 rounded-2xl shadow-[0_0_50px_rgba(124,58,237,0.2)] overflow-hidden flex flex-col aspect-video lg:aspect-auto lg:h-[80vh]">

        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#7c3aed]/20 bg-[#7c3aed]/5">
          <div className="flex items-center gap-4">
            <Radio className="w-6 h-6 text-[#7c3aed] animate-pulse" />
            <div>
              <h2 className="text-lg font-bold text-white tracking-widest uppercase flex items-center gap-2">
                TEMPORAL STREAM: {streamId}
                {isLive && <span className="text-[10px] bg-red-600 text-white px-2 py-0.5 rounded-full animate-pulse ml-2">LIVE</span>}
              </h2>
              <div className="text-[10px] font-mono text-arkhe-muted">Quantum Sync Mode: ZK-STARK v2 // Coherence: {coherence.toFixed(4)}</div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4 text-xs font-mono">
                <div className="flex flex-col items-end">
                    <span className="text-arkhe-muted text-[10px] uppercase">Latency</span>
                    <span className="text-[#00d4ff]">{latencyMs}ms</span>
                </div>
                <div className="flex flex-col items-end">
                    <span className="text-arkhe-muted text-[10px] uppercase">Channel</span>
                    <span className="text-[#7c3aed]">{activeChannel}</span>
                </div>
            </div>
            <button onClick={onClose} className="text-arkhe-muted hover:text-white transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col relative bg-black">
            <video
              ref={videoRef}
              className="w-full h-full object-contain"
              poster="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=2000"
            />

            {/* Overlay Controls */}
            <div className="absolute inset-x-0 bottom-0 p-6 bg-gradient-to-t from-black to-transparent opacity-0 hover:opacity-100 transition-opacity">
               <div className="flex flex-col gap-4">
                  {/* Progress Bar */}
                  <div className="h-1 bg-white/10 rounded-full overflow-hidden group cursor-pointer">
                      <div className="h-full bg-[#7c3aed] w-3/4 group-hover:bg-[#a855f7] transition-colors"></div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button onClick={togglePlay} className="text-white hover:text-[#7c3aed] transition-colors">
                            {isPlaying ? <Pause className="w-6 h-6 fill-current" /> : <Play className="w-6 h-6 fill-current" />}
                        </button>
                        <button className="text-white hover:text-[#7c3aed] transition-colors">
                            <Rewind className="w-5 h-5 fill-current" />
                        </button>
                        <button className="text-white hover:text-[#7c3aed] transition-colors">
                            <FastForward className="w-5 h-5 fill-current" />
                        </button>
                        <div className="text-xs font-mono text-white/70 ml-2">
                            00:42:14 / 01:00:00
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <button className="text-white hover:text-[#7c3aed] transition-colors">
                            <Shield className="w-5 h-5" />
                        </button>
                        <button className="text-white hover:text-[#7c3aed] transition-colors">
                            <Globe className="w-5 h-5" />
                        </button>
                    </div>
                  </div>
               </div>
            </div>
          </div>

          {/* Sidebar Telemetry */}
          <div className="w-72 border-l border-[#7c3aed]/20 bg-[#0d0e12] p-4 flex flex-col gap-6 font-mono shrink-0 overflow-y-auto">

            <section>
                <h3 className="text-[10px] text-[#7c3aed] font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
                    <Zap className="w-3 h-3" /> Signal Integrity
                </h3>
                <div className="space-y-3">
                    <div className="bg-black/40 border border-[#1f2024] p-2 rounded">
                        <div className="flex justify-between text-[10px] mb-1">
                            <span className="text-arkhe-muted">BITRATE</span>
                            <span className="text-white">4.2 Gbps</span>
                        </div>
                        <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                            <div className="h-full bg-[#7c3aed] w-4/5"></div>
                        </div>
                    </div>
                    <div className="bg-black/40 border border-[#1f2024] p-2 rounded">
                        <div className="flex justify-between text-[10px] mb-1">
                            <span className="text-arkhe-muted">JITTER</span>
                            <span className="text-white">0.02 ms</span>
                        </div>
                        <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                            <div className="h-full bg-[#00d4ff] w-1/5"></div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="flex-1">
                <h3 className="text-[10px] text-[#7c3aed] font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
                    <Clock className="w-3 h-3" /> ZK-Sync Events
                </h3>
                <div className="space-y-2">
                    {logs.map((log, i) => (
                        <div key={i} className={`text-[9px] p-2 rounded border border-transparent ${i === 0 ? 'bg-[#7c3aed]/10 border-[#7c3aed]/20 text-[#7c3aed]' : 'text-arkhe-muted'}`}>
                            {log}
                        </div>
                    ))}
                </div>
            </section>

            <div className="mt-auto">
                <div className="p-3 bg-[#7c3aed]/5 border border-[#7c3aed]/20 rounded-lg text-center">
                    <div className="text-[9px] text-[#7c3aed] uppercase font-bold mb-1">Phase Locking</div>
                    <div className="text-xl font-bold text-white">θ = 0.0014</div>
                    <div className="text-[8px] text-arkhe-muted uppercase mt-1">Convergent</div>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
