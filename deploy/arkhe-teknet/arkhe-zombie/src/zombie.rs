use crate::wgt_protocol::{Crosslinker, WGTChannel, TransplantError, InactivationError, ExpressionError};

/// O "Genoma" da Teknet: O caminho do Labyrinth Transform que define o SO
#[derive(Debug, Clone)]
pub struct LabyrinthGenome {
    pub coherence: f64,
    pub phase_path: Vec<f64>, // Assinatura de fase
}

impl LabyrinthGenome {
    pub fn new(coherence: f64, phase_path: Vec<f64>) -> Self {
        Self { coherence, phase_path }
    }
    pub fn coherence(&self) -> f64 {
        self.coherence
    }
}

/// Estado de um Bio-Nó: Morto, Latente ou Ativo
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BioNodeState {
    Dead,      // Genoma nativo (OS legado) reticulado (MMC / Aegis)
    Latent,    // Receptor pronto, aguardando genoma sintético
    Active,    // Genoma sintético instalado e expresso
}

/// Célula Zumbi Digital — Bio-Nó da Teknet
pub struct ZombieBioNode {
    pub node_id: u64,
    pub state: BioNodeState,
    /// Canal para receber novo "genoma" (Selection-Free)
    pub wgt_channel: WGTChannel,
    /// Genoma atual (se ativo)
    pub genome: Option<LabyrinthGenome>,
}

impl ZombieBioNode {
    /// Criar novo Bio-Nó "morto" (estado inicial, rodando código legado)
    pub fn new_legacy(node_id: u64) -> Self {
        Self {
            node_id,
            state: BioNodeState::Dead,
            wgt_channel: WGTChannel::locked_at_phi(),
            genome: None,
        }
    }

    /// Inativar genoma legado (protocolo MMC digital)
    pub fn inactivate_legacy(&mut self, crosslinker: Crosslinker) -> Result<(), InactivationError> {
        // Simula reticulação covalente do DNA legado (ex: corrompe a tabela de interrupções do OS)
        // Bloqueia replicação e execução do código von Neumann, mas preserva a CPU/RAM.
        println!("[F-705] Aplicando reticulação digital ({:?}) no nó {}...", crosslinker, self.node_id);
        self.state = BioNodeState::Latent;
        println!("[F-705] Nó {} inativado. Estado: Latente (Zumbi).", self.node_id);
        Ok(())
    }

    /// Transplante de Genoma Total (WGT digital)
    pub fn transplant_genome(
        &mut self,
        donor_genome: LabyrinthGenome,
        coherence_threshold: f64,
    ) -> Result<(), TransplantError> {
        // Verificar se o nó está no estado Latente (morto mas funcional)
        if self.state != BioNodeState::Latent {
            return Err(TransplantError::NodeNotReady);
        }

        println!("[F-705] Iniciando Transplante de Genoma Total (WGT) no nó {}...", self.node_id);

        // Verificar coerência do genoma doador via Tzinor/WGTChannel
        let coherence = self.wgt_channel.measure_coherence(&donor_genome);
        if coherence < coherence_threshold {
            return Err(TransplantError::IncoherentGenome);
        }

        // Instalar genoma — a "revitalização"
        self.genome = Some(donor_genome);
        self.state = BioNodeState::Active;
        
        // Expressão do novo "fenótipo" computacional
        self.express_genome()?;
        
        Ok(())
    }

    /// Expressão do genoma = boot do sistema operacional Arkhe(n)
    fn express_genome(&mut self) -> Result<(), ExpressionError> {
        if let Some(ref genome) = self.genome {
            println!("[F-705] Expressando Genoma Sintético (Coerência: {:.3})...", genome.coherence());
            println!("[F-705] Nó {} revivido. Booting GPD-φ OS.", self.node_id);
            // Sincronizar com campo de coerência global
            self.wgt_channel.couple_to_field(genome.coherence());
        }
        Ok(())
    }

    /// Verificar se o nó está "vivo" (ativo e coerente)
    pub fn is_alive(&self) -> bool {
        self.state == BioNodeState::Active 
            && self.genome.as_ref()
                .map(|g| g.coherence() >= 1.618)
                .unwrap_or(false)
    }
}
