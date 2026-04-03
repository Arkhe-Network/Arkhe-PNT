// arkhe-core/governance/standby_health_prover.rs
// Atestação de Saúde do Nó Standby sem Consumo de Pares EPR

use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone)]
pub struct StandbyNode {
    pub id: [u8; 32],
    pub calibration_a: u64, // x1000
    pub calibration_b: u64, // x1000
    pub last_health_proof: Option<HealthProof>,
    pub status: StandbyStatus,
}

#[derive(Debug, Clone)]
pub enum StandbyStatus {
    Standby,
    Active,
    Maintenance,
    Removed,
}

#[derive(Debug, Clone)]
pub struct HealthProof {
    pub is_healthy: bool,
    pub t2_inferred: u64,
    pub proof_hash: String,
    pub timestamp: u64,
}

impl StandbyNode {
    pub fn new(id: [u8; 32], a: u64, b: u64) -> Self {
        Self {
            id,
            calibration_a: a,
            calibration_b: b,
            last_health_proof: None,
            status: StandbyStatus::Standby,
        }
    }

    /// Simula a geração de uma prova ZK de saúde
    pub fn generate_health_proof(&mut self, fringes: [u64; 8]) -> HealthProof {
        let t2_measured: u64 = fringes.iter().enumerate()
            .map(|(i, &f)| f * (i as u64 + 1) * 10)
            .sum::<u64>() / 8;

        let t2_main = (self.calibration_a * t2_measured) / 1000 + self.calibration_b;
        let is_healthy = t2_main >= 45000; // 45μs

        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let proof = HealthProof {
            is_healthy,
            t2_inferred: t2_main,
            proof_hash: format!("0x-zk-proof-health-{}", timestamp),
            timestamp,
        };

        self.last_health_proof = Some(proof.clone());
        proof
    }

    pub fn is_eligible(&self) -> bool {
        if let Some(proof) = &self.last_health_proof {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
            // Prova deve ter menos de 1 hora
            proof.is_healthy && (now - proof.timestamp) < 3600
        } else {
            false
        }
    }
}
