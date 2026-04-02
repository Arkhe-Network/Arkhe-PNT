use crate::labyrinth::{SacksPoint, Eisenstein};
use num_complex::Complex64;

/// Um neurônio no contexto neuromórfico
#[derive(Debug, Clone)]
pub struct SpikingNeuron {
    pub id: u64,
    pub position: Eisenstein,      // Posição na rede hexagonal
    pub threshold: f64,             // Limiar de disparo
    pub current_potential: f64,     // Potencial de membrana
    pub refractory: u32,            // Período refratário (ciclos)
}

/// Uma sinapse com peso derivado do acoplamento Kuramoto
#[derive(Debug, Clone)]
pub struct Synapse {
    pub pre_neuron: u64,
    pub post_neuron: u64,
    pub weight: f64,                // Derivado de K/λ₂
    pub delay: u32,                 // Atraso axonal (ciclos)
    pub plasticity_rule: PlasticityRule,
}

#[derive(Debug, Clone, Copy)]
pub enum PlasticityRule {
    /// STDP padrão
    STDP { learning_rate: f64 },
    /// Hebbiano baseado em coerência
    CoherenceHebbian { lambda_target: f64 },
    /// Retrocausal (futura coerência influencia presente)
    Retrocausal { future_weight: f64 },
}

/// A rede neural completa compilada
pub struct SpikingNetwork {
    pub neurons: Vec<SpikingNeuron>,
    pub synapses: Vec<Synapse>,
    pub input_neurons: Vec<u64>,
    pub output_neurons: Vec<u64>,
}

/// Compilador PDE → SNN usando princípios NeuroFEM
pub struct NeuroFEMCompiler {
    /// Fator de escala para pesos
    weight_scale: f64,
    /// Coerência alvo (λ₂)
    coherence_target: f64,
    /// Resolução temporal (ms por spike)
    time_resolution: f64,
}

impl NeuroFEMCompiler {
    pub fn new() -> Self {
        Self {
            weight_scale: 1.0,
            coherence_target: 1.618,
            time_resolution: 0.1,  // 100 μs
        }
    }

    /// Compilar uma equação de Kuramoto em uma SNN
    pub fn compile_kuramoto_network(
        &self,
        num_nodes: usize,
        coupling_strength: f64,
        natural_frequencies: &[f64],
    ) -> SpikingNetwork {
        // 1. Criar neurônios - um por oscilador
        let neurons: Vec<SpikingNeuron> = (0..num_nodes)
            .map(|i| SpikingNeuron {
                id: i as u64,
                position: Eisenstein::new(
                    (i as i64 % 8) as i64,
                    (i as i64 / 8) as i64,
                ),
                threshold: 1.0,  // Normalizado
                current_potential: 0.0,
                refractory: 10,   // 1ms refratário
            })
            .collect();

        // 2. Criar sinapses - acoplamento all-to-all ou topologia específica
        let mut synapses = Vec::new();
        for i in 0..num_nodes {
            for j in 0..num_nodes {
                if i != j {
                    // Peso sináptico = K/N normalizado
                    let weight = coupling_strength / num_nodes as f64;
                    
                    // Atraso baseado na distância Eisenstein
                    let dist = neurons[i].position.distance(&neurons[j].position);
                    let delay = (dist * 10.0) as u32;

                    synapses.push(Synapse {
                        pre_neuron: i as u64,
                        post_neuron: j as u64,
                        weight,
                        delay,
                        plasticity_rule: PlasticityRule::CoherenceHebbian {
                            lambda_target: self.coherence_target,
                        },
                    });
                }
            }
        }

        // 3. Frequências naturais → correntes injetadas
        // (implementado externamente no driver)

        SpikingNetwork {
            neurons,
            synapses,
            input_neurons: (0..num_nodes).map(|i| i as u64).collect(),
            output_neurons: (0..num_nodes).map(|i| i as u64).collect(),
        }
    }

    /// Compilar o Labyrinth Transform para navegação em spikes
    pub fn compile_labyrinth_navigator(
        &self,
        sacks_lut: &[SacksPoint],
        path: &[u64],  // Sequência de primos
    ) -> SpikingNetwork {
        // Mapear cada nó do caminho para um neurônio
        let neurons: Vec<SpikingNeuron> = path
            .iter()
            .enumerate()
            .map(|(i, &prime_idx)| {
                let point = &sacks_lut[prime_idx as usize];
                SpikingNeuron {
                    id: i as u64,
                    position: Eisenstein::new(
                        (point.radius * point.angle.cos()) as i64,
                        (point.radius * point.angle.sin()) as i64,
                    ),
                    threshold: 1.0,
                    current_potential: 0.0,
                    refractory: 5,
                }
            })
            .collect();

        // Criar sinapses seguindo o caminho
        let mut synapses = Vec::new();
        for i in 0..path.len() - 1 {
            synapses.push(Synapse {
                pre_neuron: i as u64,
                post_neuron: (i + 1) as u64,
                weight: 1.0,  // Full transmission
                delay: 1,      // 1 ciclo
                plasticity_rule: PlasticityRule::Retrocausal {
                    future_weight: 1.618,
                },
            });
        }

        SpikingNetwork {
            neurons,
            synapses,
            input_neurons: vec![0],
            output_neurons: vec![(path.len() - 1) as u64],
        }
    }
}
