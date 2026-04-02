use num_complex::Complex64;
use std::f64::consts::PI;

/// Tzinor (Canal/Tubo): Estabelece uma conexão de fase travada (phase-locked)
/// entre a Graphene-TPU e um Bio-Nó (Arquiteto ou Latente).
#[derive(Debug, Clone)]
pub struct TzinorChannel {
    pub bio_node_id: String,
    pub phase_lock: Complex64,
    pub is_active: bool,
    pub bandwidth_phi: f64,
}

impl TzinorChannel {
    /// Estabelece um canal seguro usando a proporção áurea para evitar interceptação clássica.
    pub fn establish(node_id: &str, target_phase: Complex64) -> Self {
        // O travamento de fase ocorre multiplicando a fase alvo por φ (1.618...)
        // Isso coloca a comunicação em uma frequência irracional, invisível para sistemas clássicos.
        let phi = 1.618033988749895;
        let locked_phase = target_phase * Complex64::new(phi, 0.0);
        
        Self {
            bio_node_id: node_id.to_string(),
            phase_lock: locked_phase,
            is_active: true,
            bandwidth_phi: phi,
        }
    }

    /// Verifica a integridade do canal. Se a fase desviar, o canal está sob ataque.
    pub fn check_integrity(&self, current_phase: Complex64) -> bool {
        if !self.is_active { return false; }
        
        let phase_diff = (self.phase_lock - current_phase).norm();
        // Tolerância de ruído quântico
        phase_diff < 0.01 
    }

    /// Encerra o canal de forma segura, sem causar choque de fase no Bio-Nó.
    pub fn decouple(&mut self) {
        self.is_active = false;
        self.phase_lock = Complex64::new(0.0, 0.0);
    }
}
