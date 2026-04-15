/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// src/workers/inference.worker.js
// Bloco #304 — O Coração do Prisma (Worker)
import { pipeline, env } from '@huggingface/transformers';
import { EmbryoVault } from '../storage/embryovault.js';

// Configuração de soberania: não buscar em localhost, usar CDN segura
env.allowLocalModels = false;

let generator = null;
const vault = new EmbryoVault();

self.onmessage = async (e) => {
  const { type, data } = e.data;

  switch (type) {
    case 'load': {
      // data = modelId (ex: 'bonsai-1.7b')
      try {
        self.postMessage({ status: 'loading', phase: 'checking_vault' });

        const modelBuffer = await vault.fetchModel(data, (progress) => {
          self.postMessage({
            status: 'ritual_progress',
            progress: progress.progress,
            loaded: progress.loaded,
            total: progress.total
          });
        });

        // Criar URL local para o modelo cacheado
        const blob = new Blob([modelBuffer], { type: 'application/octet-stream' });
        const modelUrl = URL.createObjectURL(blob);

        self.postMessage({ status: 'loading', phase: 'instantiating' });

        generator = await pipeline('text-generation', modelUrl, {
          device: 'webgpu',
          dtype: 'q4f16', // Otimizado para Bonsai 1-bit
          progress_callback: (p) => {
            // Progresso interno do Transformers.js (carregamento dos shards)
            self.postMessage({
              status: 'model_init_progress',
              progress: (p.progress ?? 0) * 100
            });
          }
        });

        self.postMessage({ status: 'ready', model: data });
      } catch (err) {
        console.error('[λPU] Falha de inicialização:', err);
        self.postMessage({ status: 'error', error: err.message });
      }
      break;
    }

    case 'generate': {
      // data = { prompt, max_new_tokens = 256, temperature = 0.7 }
      if (!generator) {
        self.postMessage({ status: 'error', error: 'Oráculo não inicializado' });
        return;
      }

      try {
        const startTime = performance.now();
        let tokenCount = 0;

        const streamer = new (generator.constructor as any).TextStreamer(generator.tokenizer, {
          skip_prompt: true,
          callback_function: (token) => {
            tokenCount++;
            self.postMessage({
              status: 'token',
              token,
              tps: tokenCount / ((performance.now() - startTime) / 1000)
            });
          }
        });

        const output = await generator(data.prompt, {
          max_new_tokens: data.max_new_tokens || 256,
          temperature: data.temperature || 0.7,
          streamer,
          return_full_text: false
        });

        self.postMessage({
          status: 'complete',
          output: output[0].generated_text,
          total_tokens: tokenCount,
          total_time: performance.now() - startTime
        });

      } catch (err) {
        self.postMessage({ status: 'error', error: err.message });
      }
      break;
    }

    case 'interrupt': {
      // Sinalização para interrupção (implementação depende do controle do stream)
      self.postMessage({ status: 'interrupted' });
      break;
    }

    default:
      self.postMessage({ status: 'error', error: `Comando desconhecido: ${type}` });
  }
};
