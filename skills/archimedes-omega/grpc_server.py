# grpc_server.py - Servidor gRPC para Agente Archimedes-Ω
import grpc
from concurrent import futures
import time
import uuid
from datetime import datetime
import numpy as np
from skills import simulate_su2_continuous, simulate_sl3z_discrete, detect_peaks, synthesize_conclusion

# Import generated protobuf code (would be generated from archimedes.proto)
# Run: python -m grpc_tools.protoc --python_out=. --grpc_python_out=. archimedes.proto
import archimedes_pb2
import archimedes_pb2_grpc

class CoherenceAgentServicer(archimedes_pb2_grpc.CoherenceAgentServicer):
    def SimulateSU2(self, request, context):
        theta = np.linspace(request.theta_start, request.theta_end, request.num_points)
        phases, coherence = simulate_su2_continuous(
            theta_range=theta,
            thermal_noise=request.thermal_noise,
            temperature=request.temperature
        )
        return archimedes_pb2.CoherenceResponse(
            phases=phases.tolist(),
            coherence=coherence.tolist()
        )

    def SimulateSL3Z(self, request, context):
        words = list(request.words) if request.words else ["e", "a", "b", "ab", "ba", "aba"]
        theta = np.linspace(request.theta_start, request.theta_end, request.num_points)
        phases, coherence = simulate_sl3z_discrete(theta_range=theta, words=words)
        return archimedes_pb2.CoherenceResponse(
            phases=phases.tolist(),
            coherence=coherence.tolist()
        )

    def DetectPeaks(self, request, context):
        peaks = detect_peaks(
            np.array(request.coherence),
            np.array(request.phases),
            threshold_multiplier=request.threshold_multiplier,
            min_prominence=request.min_prominence
        )
        peak_infos = []
        for p in peaks:
            peak_infos.append(archimedes_pb2.PeakInfo(
                phase=p['phase'],
                phase_degrees=p['phase_degrees'],
                coherence=p['coherence'],
                prominence=p['prominence'],
                is_resonance=p['is_resonance'],
                index=p['index']
            ))
        return archimedes_pb2.PeakDetectionResponse(peaks=peak_infos)

    def Analyze(self, request, context):
        # Generate data based on source
        if request.data_source == archimedes_pb2.AnalysisRequest.DataSource.SIMULATED:
            if request.su2_params.theta_start != 0 or request.su2_params.theta_end != 0:  # Check if su2_params provided
                theta = np.linspace(request.su2_params.theta_start, request.su2_params.theta_end, request.su2_params.num_points)
                phases, coherence = simulate_su2_continuous(
                    theta_range=theta,
                    thermal_noise=request.su2_params.thermal_noise,
                    temperature=request.su2_params.temperature
                )
            elif request.sl3z_params.theta_start != 0 or request.sl3z_params.theta_end != 0:  # Check if sl3z_params provided
                words = list(request.sl3z_params.words) if request.sl3z_params.words else ["e", "a", "b", "ab", "ba", "aba"]
                theta = np.linspace(request.sl3z_params.theta_start, request.sl3z_params.theta_end, request.sl3z_params.num_points)
                phases, coherence = simulate_sl3z_discrete(theta_range=theta, words=words)
            else:
                # Default simulation
                theta = np.linspace(0, 2*np.pi, 1000)
                phases, coherence = simulate_su2_continuous(theta_range=theta)
        else:
            # Experimental data
            phases = np.array(request.experimental_data.phases)
            coherence = np.array(request.experimental_data.coherence)

        # Detect peaks
        thresh_mult = request.detection_params.threshold_multiplier if request.detection_params else 1.2
        min_prom = request.detection_params.min_prominence if request.detection_params else 0.05
        peaks = detect_peaks(coherence, phases, threshold_multiplier=thresh_mult, min_prominence=min_prom)

        # Synthesize conclusion
        conclusion = synthesize_conclusion(peaks)

        peak_infos = []
        for p in peaks:
            peak_infos.append(archimedes_pb2.PeakInfo(
                phase=p['phase'],
                phase_degrees=p['phase_degrees'],
                coherence=p['coherence'],
                prominence=p['prominence'],
                is_resonance=p['is_resonance'],
                index=p['index']
            ))

        return archimedes_pb2.AnalysisResponse(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            data_source=request.data_source,
            peaks=peak_infos,
            conclusion=archimedes_pb2.Conclusion(
                status=conclusion['status'],
                peaks_total=conclusion['peaks_total'],
                peaks_in_resonance=conclusion['peaks_in_resonance'],
                max_coherence=conclusion['max_coherence'],
                interpretation=conclusion['interpretation'],
                philosophical_note=conclusion['philosophical_note']
            ),
            output_file=""
        )

    def StreamCoherence(self, request_iterator, context):
        for request in request_iterator:
            # Simple echo for now - could implement prediction logic
            yield archimedes_pb2.CoherenceStreamResponse(
                session_id=request.session_id,
                predicted_coherence=request.coherence * 1.1,  # Simple prediction
                status="processed"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    archimedes_pb2_grpc.add_CoherenceAgentServicer_to_server(CoherenceAgentServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()