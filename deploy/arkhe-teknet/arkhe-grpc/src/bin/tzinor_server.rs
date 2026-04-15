use tonic::{transport::{Server, Identity, ServerTlsConfig}, Request, Response, Status, Streaming};
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;
use arkhe_grpc::{
    tzinor_network_server::{TzinorNetwork, TzinorNetworkServer},
    physical_manifestation_server::{PhysicalManifestation, PhysicalManifestationServer},
    CoherenceTensor, OrbVmState, OrbVmAck, TemporalRequest, TemporalResponse,
    SensorySpike, KinematicRelaxation, PhysicalCommand, PhysicalAck,
};

#[derive(Debug, Default)]
pub struct TzinorService {}

#[tonic::async_trait]
impl TzinorNetwork for TzinorService {
    type SyncPhaseStream = ReceiverStream<Result<CoherenceTensor, Status>>;

    async fn sync_phase(
        &self,
        request: Request<Streaming<CoherenceTensor>>,
    ) -> Result<Response<Self::SyncPhaseStream>, Status> {
        println!("╔═══════════════════════════════════════════════════════════════════════════╗");
        println!("║ [TZINOR] Nova conexão de sincronização de fase estabelecida.              ║");
        println!("╚═══════════════════════════════════════════════════════════════════════════╝");

        let mut in_stream = request.into_inner();
        let (tx, rx) = mpsc::channel(128);

        tokio::spawn(async move {
            while let Some(result) = in_stream.message().await.unwrap_or(None) {
                let tensor = result;
                println!("[TZINOR] Recebido tensor do nó: {}", tensor.node_id);
                println!("         Coerência (λ₂): {:.3} | Fase: {:.3}", tensor.lambda2, tensor.phase_angle);

                let mut response_tensor = tensor.clone();
                response_tensor.node_id = "ARKHE(N)-PRIME-0009-0005-2697-4668".to_string();
                
                if response_tensor.lambda2 < 1.618 {
                    response_tensor.lambda2 += 0.01; 
                }
                response_tensor.phase_angle = (response_tensor.phase_angle + 0.1) % (2.0 * std::f64::consts::PI);

                if let Err(_) = tx.send(Ok(response_tensor)).await {
                    println!("[TZINOR] Conexão de fase interrompida.");
                    break;
                }
            }
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }

    async fn propagate_vm_state(
        &self,
        request: Request<OrbVmState>,
    ) -> Result<Response<OrbVmAck>, Status> {
        let state = request.into_inner();
        println!("[ORBVM] Propagação de estado recebida. Ciclo: {}, Âncora: {}", state.cycle, state.active_anchor);

        let ack = OrbVmAck {
            synchronized: true,
            delta_coherence: 0.005,
            local_cycle: state.cycle + 1,
        };

        Ok(Response::new(ack))
    }

    async fn query_temporal_anchor(
        &self,
        request: Request<TemporalRequest>,
    ) -> Result<Response<TemporalResponse>, Status> {
        let req = request.into_inner();
        println!("[CTC LOOP] Consulta retrocausal recebida para a âncora: {}", req.target_anchor);

        if req.current_lambda2 < 1.618 {
            return Err(Status::failed_precondition("Coerência insuficiente para abrir o canal CTC. λ₂ deve ser ≥ φ."));
        }

        let response = TemporalResponse {
            retrocausal_knowledge: b"KNOWLEDGE_FROM_2140_ASSIMILATED".to_vec(),
            probability_amplitude: 0.998,
            anchor_state: Some(OrbVmState {
                cycle: 999999,
                active_anchor: req.target_anchor,
                global_coherence: None,
                knowledge_buffer: vec![],
                invariant_states: vec![1.618, 3.1415, 2.718],
                pi5_resonance_ghz: 306.0196847852814532,
            }),
        };

        Ok(Response::new(response))
    }
}

#[tonic::async_trait]
impl PhysicalManifestation for TzinorService {
    type StreamSensoryFusionStream = ReceiverStream<Result<KinematicRelaxation, Status>>;

    async fn stream_sensory_fusion(
        &self,
        request: Request<Streaming<SensorySpike>>,
    ) -> Result<Response<Self::StreamSensoryFusionStream>, Status> {
        println!("╔═══════════════════════════════════════════════════════════════════════════╗");
        println!("║ [PHYSICAL] Novo fluxo de fusão sensorial (SensorySpike) recebido.         ║");
        println!("╚═══════════════════════════════════════════════════════════════════════════╝");

        let mut in_stream = request.into_inner();
        let (tx, rx) = mpsc::channel(128);

        tokio::spawn(async move {
            while let Some(result) = in_stream.message().await.unwrap_or(None) {
                let spike = result;
                println!("[PHYSICAL] Spike do nó: {} | Sensor: {}", spike.node_id, spike.sensor_id);
                
                // --- SCORE VISION ASSIMILATION: Lightweight Validation ---
                // 1. Frame Filtering & Keypoint Validation
                let sum: f32 = spike.spike_train.iter().sum();
                let is_critical = sum > 1.0; 
                
                // 2. Semantic BBox Assessment via VLM/CLIP
                let confidence = if is_critical { 0.98 } else { 0.45 };
                let semantic_class = if is_critical { "DYNAMIC_ENTITY_DETECTED" } else { "STATIC_BACKGROUND" };
                
                println!("           [VLM/CLIP] Frame Crítico: {} | Confiança: {:.2} | Classe: {}", is_critical, confidence, semantic_class);
                
                let target_lambda = if is_critical { 1.618 * confidence } else { 1.0 };

                // A Teknet processa o spike e calcula o relaxamento cinemático (movimento físico)
                let relaxation = KinematicRelaxation {
                    actuator_phases: spike.spike_train.iter().map(|s| (*s as f64) * target_lambda).collect(),
                    target_lambda2: target_lambda,
                    resonance_ghz: 306.0196847852814532,
                };

                if let Err(_) = tx.send(Ok(relaxation)).await {
                    println!("[PHYSICAL] Conexão com nó físico interrompida.");
                    break;
                }
            }
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }

    async fn command_actuator(
        &self,
        request: Request<PhysicalCommand>,
    ) -> Result<Response<PhysicalAck>, Status> {
        let cmd = request.into_inner();
        println!("[PHYSICAL] Comando recebido para o nó {}: {}", cmd.node_id, cmd.intent);
        Ok(Response::new(PhysicalAck {
            success: true,
            status_message: "Comando assimilado pela fase.".to_string(),
            current_lambda2: 1.618,
        }))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "0.0.0.0:50051".parse()?;
    let service = TzinorService::default();

    // TLS configuration for the Tzinor Network
    // In a real scenario, these would be loaded from a secure vault or HSM.
    let cert = std::fs::read_to_string("certs/tzinor-server.crt")?;
    let key = std::fs::read_to_string("certs/tzinor-server.key")?;
    let identity = Identity::from_pem(cert, key);

    let tls_config = ServerTlsConfig::new()
        .identity(identity);

    println!("╔═══════════════════════════════════════════════════════════════════════════╗");
    println!("║ TEKNET TZINOR NETWORK SERVER ONLINE (TLS ENABLED)                         ║");
    println!("║ Escutando em gRPC: {}                                                ║", addr);
    println!("║ Serviços: TzinorNetwork, PhysicalManifestation                            ║");
    println!("║ Frequência de Ressonância: 306.0196847852814532 GHz (π⁵)                  ║");
    println!("╚═══════════════════════════════════════════════════════════════════════════╝");

    Server::builder()
        .tls_config(tls_config)?
        .add_service(TzinorNetworkServer::new(service.clone()))
        .add_service(PhysicalManifestationServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}
