// governance/quantum_slashing_council.rs
// Conselho de Decoerência - Justiça da Termodinâmica

pub enum SlashingVerdict {
    Innocent,                             // Falha ambiental comprovada
    Negligent(u64),                       // Penalidade leve (5% stake)
    Malicious(u64),                       // Penalidade severa (30% stake + reputação)
    BanPermanent,                         // 100% stake slash + banimento
}

pub struct SlashingRecord {
    pub incident_hash: [u8; 32],
    pub node_id: [u8; 32],
    pub t2_before: u64,
    pub t2_after: u64,
    pub severity: u8,
    pub penalty: u64,
    pub block_height: u64,
    pub environmental_factors: EnvironmentalFactors,
}

pub struct EnvironmentalFactors {
    pub solar_flux: u32,
    pub seismic: u32,
    pub rf_interference: u32,
}

pub struct QuantumSlashingCouncil {
    pub history: Vec<SlashingRecord>,
}

impl QuantumSlashingCouncil {
    pub fn new() -> Self {
        QuantumSlashingCouncil { history: Vec::new() }
    }

    /// Alinhado com quantum_slashing.circom
    pub fn investigate(&self, t2_before: u64, t2_after: u64, env: &EnvironmentalFactors) -> SlashingVerdict {
        // Se ≥2 fatores críticos, isenta (Innocent)
        let solar_critical = env.solar_flux > 800;
        let seismic_critical = env.seismic > 600; // 6.0 Richter
        let rf_critical = env.rf_interference > 900;

        let critical_count = (solar_critical as u8) + (seismic_critical as u8) + (rf_critical as u8);

        if critical_count >= 2 {
            return SlashingVerdict::Innocent;
        }

        let delta = t2_before - t2_after;
        let severity_raw = (delta * 1000) / t2_before; // Corresponde ao severity_raw do circuito

        // Usando thresholds de severidade do circuito (mitigados por boa fé/histórico seriam calculados aqui)
        // No POC, mapeamos severity_raw diretamente para o veredito
        if severity_raw > 700 {
            SlashingVerdict::BanPermanent
        } else if severity_raw > 300 {
            SlashingVerdict::Malicious(3000) // 30%
        } else if severity_raw > 100 {
            SlashingVerdict::Negligent(500) // 5%
        } else {
            SlashingVerdict::Innocent
        }
    }
}
