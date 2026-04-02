import React, { useState, useRef } from 'react';
import { X, Video, Play, Loader2, Download } from 'lucide-react';
import { Card } from '../components/ui/Card';

interface VideoGenerationPanelProps {
  onClose: () => void;
}

export default function VideoGenerationPanel({ onClose }: VideoGenerationPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError(null);
    setVideoUrl(null);

    try {
      const response = await fetch('/api/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate video');
      }

      const data = await response.json();
      setVideoUrl(data.videoUrl);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-3xl bg-[#111214] border-arkhe-cyan/30 text-arkhe-text shadow-[0_0_30px_rgba(0,255,170,0.1)]">
        <div className="flex flex-row items-center justify-between border-b border-[#1f2024] p-4">
          <div className="flex items-center gap-3">
            <Video className="w-6 h-6 text-arkhe-cyan" />
            <h2 className="font-mono text-lg uppercase tracking-widest text-arkhe-cyan">
              Veo-3.1 Synthesis Engine
            </h2>
          </div>
          <button onClick={onClose} className="text-arkhe-muted hover:text-arkhe-red p-2 rounded-md hover:bg-white/5 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <label htmlFor="prompt" className="text-xs font-mono uppercase tracking-widest text-arkhe-muted">
              Synthesis Prompt
            </label>
            <div className="flex gap-2">
              <input
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the visual manifestation..."
                className="flex-1 bg-[#0a0a0a] border border-[#1f2024] rounded-md px-3 py-2 font-mono text-sm focus:outline-none focus:border-arkhe-cyan text-arkhe-text"
                disabled={isGenerating}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isGenerating) {
                    handleGenerate();
                  }
                }}
              />
              <button 
                onClick={handleGenerate} 
                disabled={isGenerating || !prompt.trim()}
                className="flex items-center justify-center px-4 py-2 rounded-md bg-arkhe-cyan/20 text-arkhe-cyan hover:bg-arkhe-cyan/30 border border-arkhe-cyan/50 font-mono uppercase tracking-widest disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                {isGenerating ? 'Synthesizing...' : 'Generate'}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-arkhe-red/10 border border-arkhe-red/30 text-arkhe-red rounded text-sm font-mono">
              {error}
            </div>
          )}

          <div className="relative aspect-video bg-[#0a0a0a] border border-[#1f2024] rounded-lg overflow-hidden flex items-center justify-center">
            {isGenerating ? (
              <div className="flex flex-col items-center gap-4 text-arkhe-cyan">
                <Loader2 className="w-12 h-12 animate-spin" />
                <div className="font-mono text-xs uppercase tracking-widest animate-pulse">
                  Establishing connection to Veo-3.1...
                  <br/>
                  This process may take several minutes.
                </div>
              </div>
            ) : videoUrl ? (
              <video 
                ref={videoRef}
                src={videoUrl} 
                controls 
                autoPlay 
                loop 
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="text-arkhe-muted font-mono text-xs uppercase tracking-widest opacity-50 flex flex-col items-center gap-2">
                <Video className="w-8 h-8" />
                Awaiting Input Parameters
              </div>
            )}
            
            {videoUrl && !isGenerating && (
              <button
                className="absolute top-4 right-4 p-2 rounded-md bg-black/50 border border-arkhe-cyan/50 text-arkhe-cyan hover:bg-arkhe-cyan/20 transition-colors"
                onClick={() => {
                  const a = document.createElement('a');
                  a.href = videoUrl;
                  a.download = `arkhe-synthesis-${Date.now()}.mp4`;
                  a.click();
                }}
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
