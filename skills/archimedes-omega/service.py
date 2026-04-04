import os
from typing import Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from skills import (
    load_baseline,
    simulate_su2_continuous,
    simulate_sl3z_discrete,
    detect_peaks,
    visualize_topology,
    synthesize_conclusion,
)

app = FastAPI(
    title="Archimedes-Ω Agent Service",
    description="HTTP service for Archimedes-Ω coherence simulation and peak detection.",
    version="1.0.0",
)


class Su2SimulationRequest(BaseModel):
    theta: Optional[List[float]] = None
    thermal_noise: float = 0.05
    temperature: float = 310.0


class Sl3zSimulationRequest(BaseModel):
    theta: Optional[List[float]] = None
    words: Optional[List[str]] = None


class PeakDetectionRequest(BaseModel):
    coherence_data: List[float]
    phases: List[float]
    threshold_multiplier: float = 1.5
    min_prominence: float = 0.1


class AnalyzeRequest(BaseModel):
    theta: Optional[List[float]] = None
    thermal_noise: float = 0.05
    temperature: float = 310.0
    words: Optional[List[str]] = None
    threshold_multiplier: float = 1.5
    min_prominence: float = 0.1
    output_file: Optional[str] = None


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "Archimedes-Ω Agent"}


@app.post("/simulate/su2")
async def simulate_su2(request: Su2SimulationRequest) -> Dict:
    theta = np.array(request.theta) if request.theta is not None else None
    phases, coherence = simulate_su2_continuous(
        theta_range=theta,
        thermal_noise=request.thermal_noise,
        temperature=request.temperature,
    )
    return {
        "phases": phases.tolist(),
        "coherence": coherence.tolist(),
        "metadata": {
            "thermal_noise": request.thermal_noise,
            "temperature": request.temperature,
        },
    }


@app.post("/simulate/sl3z")
async def simulate_sl3z(request: Sl3zSimulationRequest) -> Dict:
    theta = np.array(request.theta) if request.theta is not None else None
    phases, coherence = simulate_sl3z_discrete(
        theta_range=theta,
        words=request.words,
    )
    return {
        "phases": phases.tolist(),
        "coherence": coherence.tolist(),
        "metadata": {
            "words": request.words or [],
        },
    }


@app.post("/detect/peaks")
async def detect_peaks_endpoint(request: PeakDetectionRequest) -> Dict:
    if len(request.coherence_data) != len(request.phases):
        raise HTTPException(
            status_code=400,
            detail="coherence_data and phases must have the same length",
        )

    coherence_array = np.array(request.coherence_data)
    phases_array = np.array(request.phases)
    peaks = detect_peaks(
        coherence_data=coherence_array,
        phases=phases_array,
        threshold_multiplier=request.threshold_multiplier,
        min_prominence=request.min_prominence,
    )
    return {"peaks": peaks, "count": len(peaks)}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest) -> Dict:
    theta = np.array(request.theta) if request.theta is not None else None

    su2_phases, su2_coherence = simulate_su2_continuous(
        theta_range=theta,
        thermal_noise=request.thermal_noise,
        temperature=request.temperature,
    )
    sl3z_phases, sl3z_coherence = simulate_sl3z_discrete(
        theta_range=theta,
        words=request.words,
    )

    combined_coherence = 0.5 * su2_coherence + 0.5 * sl3z_coherence
    peaks = detect_peaks(
        coherence_data=combined_coherence,
        phases=su2_phases,
        threshold_multiplier=request.threshold_multiplier,
        min_prominence=request.min_prominence,
    )

    conclusion = synthesize_conclusion(peaks)
    output_file = None
    if request.output_file:
        output_file = request.output_file
        try:
            visualize_topology(
                su2_data=(su2_phases, su2_coherence),
                sl3z_data=(sl3z_phases, sl3z_coherence),
                peaks=peaks,
                output_file=output_file,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Visualization failure: {exc}")

    return {
        "status": "analyzed",
        "peaks": peaks,
        "conclusion": conclusion,
        "output_file": output_file,
        "metadata": {
            "thermal_noise": request.thermal_noise,
            "temperature": request.temperature,
            "words": request.words or [],
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
