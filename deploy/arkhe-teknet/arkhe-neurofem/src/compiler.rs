use labyrinth_rs::eisenstein::Eisenstein;
use num_complex::Complex64;

/// Modelo de Neurônio Leaky Integrate-and-Fire (LIF)
/// Na Teknet, o limiar de disparo (threshold) corresponde à coerência de fase.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct LifNeuron {
    pub id: u64,
    pub threshold: f64,
    pub leak_rate: f64,
    pub phase_state: Complex64,
}

/// Sinapse que conecta dois neurônios.
/// O peso (weight) é o acoplamento K de Kuramoto.
/// O atraso (delay) é o deslocamento de fase não-associativo (Φ_ij).
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Synapse {
    pub source_id: u64,
    pub target_id: u64,
    pub weight: f64,
    pub delay: u32,
}

/// A Malha de Rede Neural de Spiking (SNN) que representa a Equação Diferencial Parcial (PDE).
pub struct SnnMesh {
    pub neurons: Vec<LifNeuron>,
    pub synapses: Vec<Synapse>,
}

impl SnnMesh {
    /// Compila a topologia do Labyrinth Transform (Coordenadas de Eisenstein) 
    /// diretamente em uma rede neural de spiking (NeuroFEM).
    pub fn compile_from_labyrinth(nodes: &[Eisenstein], coupling_k: f64) -> Self {
        let mut neurons = Vec::with_capacity(nodes.len());
        let mut synapses = Vec::new();

        // 1. Mapeia cada coordenada de Eisenstein para um neurônio físico
        for (i, _node) in nodes.iter().enumerate() {
            neurons.push(LifNeuron {
                id: i as u64,
                threshold: 1.6180339887, // Proporção Áurea como limiar de disparo
                leak_rate: 0.01,
                phase_state: Complex64::new(0.0, 0.0),
            });
        }

        // 2. Mapeia as distâncias de Eisenstein para pesos sinápticos e atrasos
        for i in 0..nodes.len() {
            for j in 0..nodes.len() {
                if i != j {
                    let dist = nodes[i].distance(&nodes[j]);
                    // Conecta apenas vizinhos próximos na rede hexagonal
                    if dist <= 1.5 {
                        synapses.push(Synapse {
                            source_id: i as u64,
                            target_id: j as u64,
                            weight: coupling_k / dist, // Lei do inverso da distância para acoplamento
                            delay: (dist * 10.0) as u32, // Atraso proporcional à distância
                        });
                    }
                }
            }
        }

        Self { neurons, synapses }
    }
}
