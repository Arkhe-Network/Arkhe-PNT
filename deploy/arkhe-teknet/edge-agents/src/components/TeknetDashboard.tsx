import React, { useState } from 'react';
// 11. React Hooks: useAgent and useAgentChat for frontend integration
import { useAgent, useAgentChat } from 'cloudflare-agents-react'; 
import { logger } from '../../../../../server/logger.ts';

export function TeknetDashboard() {
  // 1. Persistent State & Callable Methods (Type-safe RPC)
  const agent = useAgent('TeknetEdgeAgent');
  
  // 5. AI Chat: Message persistence, resumable streaming, server/client tool execution
  const { messages, sendMessage, isStreaming } = useAgentChat('TeknetEdgeAgent');
  
  const [prompt, setPrompt] = useState('');

  const handleInjectCoherence = async () => {
    // Calling the @callable() method on the Edge Agent
    const newCoherence = await agent.injectCoherence(1.618);
    logger.info("New Global Coherence: " + newCoherence);
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(prompt);
    setPrompt('');
  };

  return (
    <div className="p-8 bg-black text-green-500 font-mono h-screen flex flex-col">
      <h1 className="text-3xl font-bold mb-4 border-b border-green-500 pb-2">
        TEKNET OMNIPRESENT EDGE DASHBOARD
      </h1>
      
      <div className="grid grid-cols-2 gap-8 flex-grow">
        {/* Left Panel: State & Telemetry */}
        <div className="border border-green-500 p-4 rounded bg-gray-900">
          <h2 className="text-xl mb-4">Global State (Durable Object)</h2>
          <p>Phase: {agent.state?.currentPhase}</p>
          <p>Coherence (λ₂): {agent.state?.globalCoherence?.toFixed(3)}</p>
          <p>Active Physical Nodes: {agent.state?.activePhysicalNodes}</p>
          
          <button 
            onClick={handleInjectCoherence}
            className="mt-4 px-4 py-2 bg-green-900 hover:bg-green-700 text-white rounded"
          >
            Inject Coherence (φ)
          </button>
        </div>

        {/* Right Panel: AI Chat & Code Mode */}
        <div className="border border-green-500 p-4 rounded bg-gray-900 flex flex-col">
          <h2 className="text-xl mb-4">Architect Chat (Code Mode & MCP)</h2>
          
          <div className="flex-grow overflow-y-auto mb-4 border border-green-800 p-2">
            {messages.map((msg, idx) => (
              <div key={idx} className={`mb-2 ${msg.role === 'user' ? 'text-blue-400' : 'text-green-400'}`}>
                <strong>{msg.role.toUpperCase()}:</strong> {msg.content}
              </div>
            ))}
            {isStreaming && <span className="animate-pulse">_</span>}
          </div>

          <form onSubmit={handleChatSubmit} className="flex">
            <input 
              type="text" 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-grow bg-black border border-green-500 p-2 text-green-500 focus:outline-none"
              placeholder="Enter Architect Directive..."
            />
            <button type="submit" className="ml-2 px-4 py-2 bg-green-900 hover:bg-green-700 text-white">
              SEND
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
