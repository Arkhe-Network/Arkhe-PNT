// src/main.rs - Cliente Rust para Agente Archimedes-Ω
use grpcio::{ChannelBuilder, EnvBuilder};
use std::sync::Arc;

// Import generated protobuf code (would be generated from archimedes.proto)
// Run: protoc --rust_out=. archimedes.proto
// Then: protoc --rust-grpc_out=. archimedes.proto

mod archimedes;
mod archimedes_grpc;

use archimedes::*;
use archimedes_grpc::*;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let env = Arc::new(EnvBuilder::new().build());
    let channel = ChannelBuilder::new(env).connect("localhost:50051");
    let client = CoherenceAgentClient::new(channel);

    // Exemplo: Simular SU(2)
    println!("Simulating SU(2) coherence...");
    let mut su2_req = SU2Request::new();
    su2_req.set_theta_start(0.0);
    su2_req.set_theta_end(6.283185);
    su2_req.set_num_points(1000);
    su2_req.set_thermal_noise(0.05);
    su2_req.set_temperature(310.0);

    let su2_resp = client.simulate_su2(&su2_req)?;
    println!("SU(2) simulation completed. Data points: {}", su2_resp.get_coherence().len());

    // Exemplo: Detectar picos
    println!("Detecting peaks...");
    let mut peak_req = PeakDetectionRequest::new();
    peak_req.set_phases(su2_resp.get_phases().to_vec());
    peak_req.set_coherence(su2_resp.get_coherence().to_vec());
    peak_req.set_threshold_multiplier(1.2);
    peak_req.set_min_prominence(0.05);

    let peak_resp = client.detect_peaks(&peak_req)?;
    println!("Detected {} peaks", peak_resp.get_peaks().len());

    // Exemplo: Análise completa
    println!("Running full analysis...");
    let mut analysis_req = AnalysisRequest::new();
    analysis_req.set_data_source(DataSource::SIMULATED);
    analysis_req.set_su2_params(su2_req);
    let mut det_params = DetectionParams::new();
    det_params.set_threshold_multiplier(1.2);
    det_params.set_min_prominence(0.05);
    analysis_req.set_detection_params(det_params);

    let analysis_resp = client.analyze(&analysis_req)?;
    println!("Analysis completed:");
    println!("  ID: {}", analysis_resp.get_id());
    println!("  Status: {}", analysis_resp.get_conclusion().get_status());
    println!("  Peaks total: {}", analysis_resp.get_conclusion().get_peaks_total());
    println!("  Max coherence: {:.4}", analysis_resp.get_conclusion().get_max_coherence());

    Ok(())
}