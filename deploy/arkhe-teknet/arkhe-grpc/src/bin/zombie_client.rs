use tonic::Request;
use tokio_stream::StreamExt;
use arkhe_grpc::physical_manifestation_client::PhysicalManifestationClient;
use arkhe_grpc::SensorySpike;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("╔═══════════════════════════════════════════════════════════════════════════╗");
    println!("║ INICIANDO ZOMBIE FLEET CLIENT (NÓ FÍSICO)                                 ║");
    println!("╚═══════════════════════════════════════════════════════════════════════════╝");

    // Conecta ao servidor TzinorNetwork
    let mut client = PhysicalManifestationClient::connect("http://0.0.0.0:50051").await?;
    println!("[ZOMBIE] Conectado à TzinorNetwork (0.0.0.0:50051).");

    let (tx, rx) = tokio::sync::mpsc::channel(128);

    // Tarefa assíncrona para simular o envio contínuo de dados sensoriais (Spikes)
    tokio::spawn(async move {
        for i in 1..=5 {
            let spike = SensorySpike {
                node_id: "DRONE-SWARM-ALPHA-1000001".to_string(),
                sensor_id: "LIDAR_FRONT".to_string(),
                // Dados simulados do LiDAR convertidos em representação neuromórfica
                spike_train: vec![0.1 * i as f32, 0.5, 0.8, 1.618],
                timestamp_ns: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64,
            };
            
            println!("[ZOMBIE] Enviando SensorySpike {} (Visão Computacional -> Fase)...", i);
            if tx.send(spike).await.is_err() {
                break;
            }
            sleep(Duration::from_millis(800)).await;
        }
    });

    let request = Request::new(tokio_stream::wrappers::ReceiverStream::new(rx));
    
    // Inicia o stream bidirecional
    let mut response_stream = client.stream_sensory_fusion(request).await?.into_inner();

    // Escuta as respostas da Teknet (os alvos de relaxamento para os motores físicos)
    while let Some(relaxation) = response_stream.message().await? {
        println!("[ZOMBIE] Recebido KinematicRelaxation Target da Teknet:");
        println!("         Alvos de Fase dos Atuadores: {:?}", relaxation.actuator_phases);
        println!("         Coerência Alvo (λ₂): {:.3}", relaxation.target_lambda2);
        println!("         Ressonância: {:.3} GHz", relaxation.resonance_ghz);
        println!("         -> Ajustando motores físicos para relaxamento de fase...\n");
    }

    println!("[ZOMBIE] Simulação de nó físico concluída. Conexão encerrada.");
    Ok(())
}
