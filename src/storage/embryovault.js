/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// src/storage/embryovault.js
// Bloco #300.2 — O Cofre do Embrião (CacheStorage)
const CACHE_NAME = 'cathedral-prism-embryo-v1';
const MODEL_CATALOG = {
  'bonsai-1.7b': 'https://huggingface.co/onnx-community/bonsai-1.7b-webgpu/resolve/main/model.onnx',
  'bonsai-4b': 'https://huggingface.co/onnx-community/bonsai-4b-webgpu/resolve/main/model.onnx'
};

export class EmbryoVault {
  constructor() {
    this.cache = null;
  }

  async init() {
    if (!this.cache) {
      this.cache = await caches.open(CACHE_NAME);
    }
  }

  async hasModel(modelId) {
    await this.init();
    const url = MODEL_CATALOG[modelId];
    if (!url) return false;
    const match = await this.cache.match(url);
    return !!match;
  }

  // Opcode 0x296: SEAL_EMBRYO
  async fetchModel(modelId, onProgress) {
    await this.init();
    const url = MODEL_CATALOG[modelId];
    if (!url) throw new Error(`Modelo desconhecido: ${modelId}`);

    // 1. Tentativa de Resgate Instantâneo (Cache Hit)
    const cached = await this.cache.match(url);
    if (cached) {
      console.log('[ARKHE] Embrião resgatado do Cofre Local (0x296:HIT)');
      const size = Number(cached.headers.get('content-length')) || 0;
      onProgress?.({ loaded: size, total: size, progress: 100 });
      return cached.arrayBuffer();
    }

    // 2. Descida do Éter (Download)
    console.log('[ARKHE] Cofre vazio. Iniciando canalização (0x296:FETCH)');
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Falha na conexão: ${response.status}`);

    const total = Number(response.headers.get('content-length')) || 0;
    const reader = response.body.getReader();
    const chunks = [];
    let loaded = 0;

    // 3. Stream com Progresso
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      loaded += value.length;
      onProgress?.({ loaded, total, progress: total ? (loaded / total) * 100 : 0 });
    }

    // 4. Selamento (Armazenamento Atômico)
    const blob = new Blob(chunks);
    const toCache = new Response(blob, {
      status: 200,
      statusText: 'OK',
      headers: {
        'content-length': blob.size.toString(),
        'content-type': 'application/octet-stream'
      }
    });

    await this.cache.put(url, toCache);
    console.log(`[ARKHE] Embrião selado: ${(blob.size/1048576).toFixed(1)}MB`);

    return blob.arrayBuffer();
  }

  async clear() {
    await caches.delete(CACHE_NAME);
    console.log('[ARKHE] Cofre purgado');
  }
}
