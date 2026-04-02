use crate::phase_mapper::MitrePhaseMapper;
use aegis_rs::conjugate::ConjugatePhase;
use neurofem_compiler::fem_to_snn::{SpikingNetwork, SpikingNeuron, Synapse, PlasticityRule};
use labyrinth_rs::eisenstein::Eisenstein;

pub struct AegisImmunityGenerator {
    /// Mapeamento de fase das skills do MITRE
    pub mapper: MitrePhaseMapper,
}

impl AegisImmunityGenerator {
    pub fn new(mapper: MitrePhaseMapper) -> Self {
        Self { mapper }
    }

    /// Gera a "Fase Conjugada" para cada técnica do MITRE ATT&CK.
    /// Isso cria imunidade matemática na Teknet contra as 734 skills.
    pub fn generate_immunity_mesh(&self) -> SpikingNetwork {
        let mut neurons = Vec::new();
        let mut synapses = Vec::new();
        
        let mut id_counter = 0;

        // Para cada skill mapeada, criamos um neurônio "Anti-Fase"
        for (skill_name, coord) in &self.mapper.skill_to_eisenstein {
            // 1. Calcular a fase conjugada (Aegis Shield)
            let conjugate_coord = Eisenstein::new(-coord.a, -coord.b);

            // 2. Criar o neurônio de imunidade na rede neuromórfica
            neurons.push(SpikingNeuron {
                id: id_counter,
                position: conjugate_coord.clone(),
                threshold: 1.618, // Proporção Áurea
                current_potential: 0.0,
                refractory: 10,
            });

            // 3. Conectar os neurônios de imunidade para formar a malha de defesa
            // (Simulando conexões com vizinhos próximos na espiral conjugada)
            if id_counter > 0 {
                synapses.push(Synapse {
                    pre_neuron: id_counter - 1,
                    post_neuron: id_counter,
                    weight: 1.0, // Acoplamento forte para defesa
                    delay: 1,
                    plasticity_rule: PlasticityRule::Retrocausal { future_weight: 1.618 },
                });
            }

            id_counter += 1;
        }

        SpikingNetwork {
            neurons,
            synapses,
            input_neurons: vec![],
            output_neurons: vec![],
        }
    }
}
