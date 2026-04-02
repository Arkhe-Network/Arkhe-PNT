use crate::fem_to_snn::{SpikingNetwork, Synapse};

/// Configuração para chip Loihi 2
pub struct Loihi2Config {
    /// Número de chips (cada um tem 128k neurônios)
    pub num_chips: usize,
    /// neurônios por chip
    pub neurons_per_chip: usize,
    /// Sinapses por chip
    pub synapses_per_chip: usize,
}

impl Default for Loihi2Config {
    fn default() -> Self {
        Self {
            num_chips: 1,
            neurons_per_chip: 128_000,
            synapses_per_chip: 120_000_000,
        }
    }
}

/// Formato binário para flash no Loihi 2
pub struct LoihiBinary {
    pub neuron_config: Vec<u8>,
    pub synapse_config: Vec<u8>,
    pub routing_table: Vec<u8>,
}

/// Exportador para hardware Loihi 2
pub struct LoihiExporter {
    config: Loihi2Config,
}

impl LoihiExporter {
    pub fn new(config: Loihi2Config) -> Self {
        Self { config }
    }

    /// Exportar rede para formato binário do Loihi 2
    pub fn export(&self, network: &SpikingNetwork) -> Result<LoihiBinary, String> {
        // Verificar se cabe no hardware
        if network.neurons.len() > self.config.neurons_per_chip * self.config.num_chips {
            return Err("Too many neurons for hardware".into());
        }
        
        // Formato simplificado - real implementação usaria Nx SDK
        let mut neuron_config = Vec::new();
        for neuron in &network.neurons {
            // Cada neurônio: 16 bytes
            neuron_config.extend_from_slice(&neuron.id.to_le_bytes());
            neuron_config.extend_from_slice(&(neuron.threshold as f32).to_le_bytes());
            neuron_config.extend_from_slice(&neuron.refractory.to_le_bytes());
            neuron_config.extend_from_slice(&[0u8; 6]); // padding
        }

        let mut synapse_config = Vec::new();
        for synapse in &network.synapses {
            // Cada sinapse: 8 bytes
            synapse_config.extend_from_slice(&synapse.pre_neuron.to_le_bytes()[..2]);
            synapse_config.extend_from_slice(&synapse.post_neuron.to_le_bytes()[..2]);
            synapse_config.extend_from_slice(&(synapse.weight as f32).to_le_bytes()[..2]);
            synapse_config.extend_from_slice(&synapse.delay.to_le_bytes()[..2]);
        }

        // Tabela de roteamento (simplificada)
        let routing_table = self.build_routing_table(network);

        Ok(LoihiBinary {
            neuron_config,
            synapse_config,
            routing_table,
        })
    }

    fn build_routing_table(&self, network: &SpikingNetwork) -> Vec<u8> {
        // Mapear neurônios para cores físicos
        let mut table = Vec::new();
        
        for (i, _neuron) in network.neurons.iter().enumerate() {
            let chip = i / self.config.neurons_per_chip;
            let local_id = i % self.config.neurons_per_chip;
            let core = local_id / 1024;
            
            table.push(chip as u8);
            table.extend_from_slice(&core.to_le_bytes()[..2]);
            table.extend_from_slice(&(local_id as u16).to_le_bytes());
        }
        
        table
    }

    /// Salvar para arquivo
    pub fn save_to_file(&self, binary: &LoihiBinary, path: &str) -> std::io::Result<()> {
        use std::fs::File;
        use std::io::Write;
        
        let mut file = File::create(path)?;
        
        // Header mágico
        file.write_all(b"LOIHI2\0")?;
        file.write_all(&(binary.neuron_config.len() as u32).to_le_bytes())?;
        file.write_all(&(binary.synapse_config.len() as u32).to_le_bytes())?;
        
        file.write_all(&binary.neuron_config)?;
        file.write_all(&binary.synapse_config)?;
        file.write_all(&binary.routing_table)?;
        
        Ok(())
    }
}
