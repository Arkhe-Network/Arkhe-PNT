#!/usr/bin/env python3
"""
main.py - Orquestrador do Agente Archimedes-Ω com API FastAPI
============================================================
Executa o loop de interrogação do vácuo biológico.
Suporta CLI e API REST (FastAPI).
"""

import numpy as np
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, List, Optional

# Importar módulos
from skills import (
    load_baseline,
    simulate_su2_continuous,
    simulate_sl3z_discrete,
    detect_peaks,
    visualize_topology,
    synthesize_conclusion
)

# Importar módulos adicionais
try:
    from fret_reader import load_and_preprocess
    from mesh_agent import publish_conclusion
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# FastAPI setup
try:
    from fastapi import FastAPI, BackgroundTasks
    from pydantic import BaseModel
    app = FastAPI(title="Archimedes-Ω Coherence Agent API")
except ImportError:
    app = None

# Carregar alma (parâmetros filosóficos)
SOUL = {
    "axiom": "O universo é um reticulado; nós somos seus detectores.",
    "threshold": 0.95,
    "target_resonance": np.pi / 5  # ~0.628 rad
}

# --- Pydantic Models for API ---
if app:
    class SimulationRequest(BaseModel):
        theta_start: float = 0.0
        theta_end: float = 6.28318
        points: int = 1000
        thermal_noise: float = 0.05
        temperature: float = 310.0
        words: Optional[List[str]] = ["e", "a", "b", "ab", "ba", "aba"]

    class DetectionRequest(BaseModel):
        phases: List[float]
        coherence: List[float]
        threshold_multiplier: float = 1.2
        min_prominence: float = 0.05

    @app.post("/simulate/su2")
    async def api_simulate_su2(req: SimulationRequest):
        theta = np.linspace(req.theta_start, req.theta_end, req.points)
        phases, coherence = simulate_su2_continuous(theta, req.thermal_noise, req.temperature)
        return {"phases": phases.tolist(), "coherence": coherence.tolist()}

    @app.post("/simulate/sl3z")
    async def api_simulate_sl3z(req: SimulationRequest):
        theta = np.linspace(req.theta_start, req.theta_end, req.points)
        phases, coherence = simulate_sl3z_discrete(theta, req.words)
        return {"phases": phases.tolist(), "coherence": coherence.tolist()}

    @app.post("/detect/peaks")
    async def api_detect_peaks(req: DetectionRequest):
        peaks = detect_peaks(np.array(req.coherence), np.array(req.phases), req.threshold_multiplier, req.min_prominence)
        return {"peaks": peaks}

    @app.post("/analyze")
    async def api_analyze(background_tasks: BackgroundTasks):
        # Run full pipeline in background or return immediately for simplicity here
        results = run_interrogation()
        # Clean results for JSON serialization
        return json.loads(json.dumps(results, default=str))

# --- Core Logic ---

def run_interrogation(
    state_file: str = "tzinor-state.json",
    output_dir: str = "output",
    use_real_data: str = None,
    publish: bool = False,
    mesh_method: str = "blackboard"
) -> dict:
    """
    Executa o loop completo de interrogação.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO INTERROGAÇÃO: Archimedes-Ω")
    logger.info("=" * 60)

    # Criar diretório de saída
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. READ
    logger.info("[1/5] Lendo estado externo via Tzinor...")
    state = load_baseline(state_file)

    # 2. SIM
    logger.info("[2/5] Obtendo dados de coerência...")
    if use_real_data and EXTRAS_AVAILABLE:
        phases, coherence = load_and_preprocess(use_real_data, remove_outliers=True, interpolate_to=1000)
        data_source = "experimental"
    else:
        theta_range = np.linspace(0.01, 2 * np.pi, 1000)
        phases_su2, coherence_su2 = simulate_su2_continuous(theta_range, thermal_noise=0.05, temperature=state.get('temperature', 310.0))
        phases_sl3, coherence_sl3 = simulate_sl3z_discrete(theta_range, words=["e", "a", "b", "ab", "ba", "aba", "bab"])
        phases = theta_range
        coherence = 0.3 * coherence_su2 + 0.7 * coherence_sl3
        data_source = "simulated"

    # 3. DETECT
    logger.info("[3/5] Detectando picos e ressonâncias...")
    peaks = detect_peaks(coherence_data=coherence, phases=phases, threshold_multiplier=1.2, min_prominence=0.05)
    significant_peaks = [p for p in peaks if p['coherence'] > 0.3]

    # 4. VISUALIZE
    logger.info("[4/5] Gerando visualização topológica...")
    output_file = str(output_path / f"coherence_{timestamp}.png")
    if use_real_data:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(phases, coherence, 'b-', label='Dados Experimentais', linewidth=1)
        for peak in significant_peaks:
            ax.axvline(x=peak['phase'], color='gold', linestyle='--', alpha=0.7)
        ax.set_xlabel('Ângulo de Fase θ (radianos)')
        ax.set_ylabel('Coerência R(θ)')
        ax.set_title(f'Dados Experimentais de FRET - {timestamp}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        visualize_topology(su2_data=(phases_su2, coherence_su2), sl3z_data=(phases_sl3, coherence_sl3), peaks=significant_peaks, output_file=output_file)

    # 5. REPORT
    logger.info("[5/5] Sintetizando conclusão filosófica...")
    conclusion = synthesize_conclusion(peak_data=significant_peaks, threshold=SOUL['threshold'])

    if publish and EXTRAS_AVAILABLE:
        publish_conclusion(conclusion, method=mesh_method)

    results = {
        "timestamp": timestamp,
        "data_source": data_source,
        "peaks_detected": significant_peaks,
        "conclusion": conclusion,
        "output_file": output_file
    }

    # Save results
    results_file = str(output_path / f"results_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archimedes-Ω: Interrogador de Coerência Biológica")
    parser.add_argument("state_file", nargs="?", default="tzinor-state.json")
    parser.add_argument("--data", "-d", help="Caminho para arquivo CSV")
    parser.add_argument("--output", "-o", default="output")
    parser.add_argument("--publish", "-p", action="store_true")
    parser.add_argument("--server", action="store_true", help="Inicia o servidor API FastAPI")

    args = parser.parse_args()

    if args.server:
        import uvicorn
        if app:
            logger.info("Iniciando servidor API Archimedes-Ω na porta 8080...")
            uvicorn.run(app, host="0.0.0.0", port=8080)
        else:
            logger.error("FastAPI não instalado. Não foi possível iniciar o servidor.")
    else:
        run_interrogation(state_file=args.state_file, output_dir=args.output, use_real_data=args.data, publish=args.publish)
