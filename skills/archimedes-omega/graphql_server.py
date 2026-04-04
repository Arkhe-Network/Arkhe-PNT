# graphql_server.py - Servidor GraphQL para Agente Archimedes-Ω
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from typing import List, Optional
import numpy as np
import uuid
from datetime import datetime
from enum import Enum
from skills import simulate_su2_continuous, simulate_sl3z_discrete, detect_peaks, synthesize_conclusion

# Tipos GraphQL
@strawberry.type
class CoherenceData:
    phases: List[float]
    coherence: List[float]

@strawberry.type
class PeakInfo:
    phase: float
    phase_degrees: float
    coherence: float
    prominence: float
    is_resonance: bool
    index: int

@strawberry.type
class PeakDetectionResult:
    peaks: List[PeakInfo]

@strawberry.type
class Conclusion:
    status: str
    peaks_total: int
    peaks_in_resonance: int
    max_coherence: float
    interpretation: str
    philosophical_note: str

@strawberry.type
class AnalysisResult:
    id: str
    timestamp: str
    data_source: str
    peaks: List[PeakInfo]
    conclusion: Conclusion
    output_file: Optional[str]

@strawberry.type
class PublishResult:
    success: bool
    message_id: Optional[str]
    error: Optional[str]

# Inputs
@strawberry.input
class SU2Input:
    theta_start: float = 0.0
    theta_end: float = 6.283185307179586
    num_points: int = 1000
    thermal_noise: float = 0.05
    temperature: float = 310.0

@strawberry.input
class SL3ZInput:
    theta_start: float = 0.0
    theta_end: float = 6.283185307179586
    num_points: int = 1000
    words: List[str] = strawberry.field(default_factory=lambda: ["e", "a", "b", "ab", "ba", "aba"])

@strawberry.input
class ExperimentalDataInput:
    phases: List[float]
    coherence: List[float]

@strawberry.input
class DetectionParamsInput:
    threshold_multiplier: float = 1.2
    min_prominence: float = 0.05

# Enums
class DataSource(Enum):
    SIMULATED = "simulated"
    EXPERIMENTAL = "experimental"

class PublishMethod(Enum):
    BLACKBOARD = "blackboard"
    NOSTR = "nostr"

# Queries e Mutations
@strawberry.type
class Query:
    @strawberry.field
    def simulate_su2(
        self,
        theta_start: float = 0.0,
        theta_end: float = 6.283185307179586,
        num_points: int = 1000,
        thermal_noise: float = 0.05,
        temperature: float = 310.0
    ) -> CoherenceData:
        theta = np.linspace(theta_start, theta_end, num_points)
        phases, coherence = simulate_su2_continuous(
            theta_range=theta,
            thermal_noise=thermal_noise,
            temperature=temperature
        )
        return CoherenceData(phases=phases.tolist(), coherence=coherence.tolist())

    @strawberry.field
    def simulate_sl3z(
        self,
        theta_start: float = 0.0,
        theta_end: float = 6.283185307179586,
        num_points: int = 1000,
        words: Optional[List[str]] = None
    ) -> CoherenceData:
        if words is None:
            words = ["e", "a", "b", "ab", "ba", "aba"]
        theta = np.linspace(theta_start, theta_end, num_points)
        phases, coherence = simulate_sl3z_discrete(theta_range=theta, words=words)
        return CoherenceData(phases=phases.tolist(), coherence=coherence.tolist())

    @strawberry.field
    def detect_peaks(
        self,
        phases: List[float],
        coherence: List[float],
        threshold_multiplier: float = 1.2,
        min_prominence: float = 0.05
    ) -> PeakDetectionResult:
        peaks = detect_peaks(
            np.array(coherence),
            np.array(phases),
            threshold_multiplier=threshold_multiplier,
            min_prominence=min_prominence
        )
        return PeakDetectionResult(peaks=[PeakInfo(**p) for p in peaks])

    @strawberry.field
    def analyze(
        self,
        data_source: DataSource,
        su2_params: Optional[SU2Input] = None,
        sl3z_params: Optional[SL3ZInput] = None,
        experimental_data: Optional[ExperimentalDataInput] = None,
        detection_params: Optional[DetectionParamsInput] = None
    ) -> AnalysisResult:
        # Gerar dados baseado na fonte
        if data_source.value == "simulated":
            if su2_params:
                theta = np.linspace(su2_params.theta_start, su2_params.theta_end, su2_params.num_points)
                phases, coherence = simulate_su2_continuous(
                    theta_range=theta,
                    thermal_noise=su2_params.thermal_noise,
                    temperature=su2_params.temperature
                )
            elif sl3z_params:
                theta = np.linspace(sl3z_params.theta_start, sl3z_params.theta_end, sl3z_params.num_points)
                phases, coherence = simulate_sl3z_discrete(theta_range=theta, words=sl3z_params.words)
            else:
                # Default simulation
                theta = np.linspace(0, 2*np.pi, 1000)
                phases, coherence = simulate_su2_continuous(theta_range=theta)
        else:
            # Experimental data
            if not experimental_data:
                raise ValueError("Experimental data required when data_source is EXPERIMENTAL")
            phases = np.array(experimental_data.phases)
            coherence = np.array(experimental_data.coherence)

        # Detect peaks
        thresh_mult = detection_params.threshold_multiplier if detection_params else 1.2
        min_prom = detection_params.min_prominence if detection_params else 0.05
        peaks = detect_peaks(coherence, phases, threshold_multiplier=thresh_mult, min_prominence=min_prom)

        # Synthesize conclusion
        conclusion = synthesize_conclusion(peaks)

        return AnalysisResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            data_source=data_source.value,
            peaks=[PeakInfo(**p) for p in peaks],
            conclusion=Conclusion(**conclusion),
            output_file=None
        )

@strawberry.type
class Mutation:
    @strawberry.field
    def run_analysis(
        self,
        name: str,
        data_source: DataSource,
        su2_params: Optional[SU2Input] = None,
        sl3z_params: Optional[SL3ZInput] = None,
        experimental_data: Optional[ExperimentalDataInput] = None,
        detection_params: Optional[DetectionParamsInput] = None
    ) -> AnalysisResult:
        # Same implementation as analyze query
        return Query().analyze(data_source, su2_params, sl3z_params, experimental_data, detection_params)

    @strawberry.field
    def publish_conclusion(self, analysis_id: str, method: PublishMethod) -> PublishResult:
        # Placeholder for publishing logic
        return PublishResult(
            success=True,
            message_id=str(uuid.uuid4()),
            error=None
        )

# Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# FastAPI app
app = FastAPI(title="Archimedes-Ω GraphQL API", version="1.0.0")
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)