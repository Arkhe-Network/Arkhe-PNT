// governance/alpha_musig2.rs
// Implementação MuSig2 com Threshold Dinâmico Alpha (α)

use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub enum GovernanceError {
    QuantumDecoherence,
    AlphaMismatch,
    InvalidSignature,
}

impl fmt::Display for GovernanceError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

impl Error for GovernanceError {}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Regime {
    Transparent,  // α < 0.25
    Balanced,     // 0.25 <= α < 0.75
    Private,      // α >= 0.75
}

pub struct NetworkContext {
    pub global_threat_level: u32,
    pub network_coherence: f64,
    pub recent_slashing_events: u32,
    pub regulatory_pressure: u32,
    pub avg_transaction_value: u64,
}

pub struct AlphaCouncil {
    pub alpha_threshold: u64,  // 0-1000
    pub current_regime: Regime,
}

impl AlphaCouncil {
    pub fn new(context: &NetworkContext) -> Self {
        let alpha = Self::calculate_alpha(context);
        let regime = if alpha < 250 {
            Regime::Transparent
        } else if alpha < 750 {
            Regime::Balanced
        } else {
            Regime::Private
        };

        AlphaCouncil {
            alpha_threshold: alpha,
            current_regime: regime,
        }
    }

    /// Alinhado com alpha_calculator.circom
    /// Pesos: Threat(3), Coherence(2), Slashing(4), Regulatory(1), Value(2). Total = 12.
    fn calculate_alpha(context: &NetworkContext) -> u64 {
        let threat = context.global_threat_level as u64 * 10;
        let coherence = ((1.0 - context.network_coherence) * 5000.0) as u64; // (1000-coh)*5
        let slashing = context.recent_slashing_events as u64 * 100;
        let regulatory = (100 - context.regulatory_pressure as u64) * 3;

        let log_value = if context.avg_transaction_value > 1000000 {
            1000
        } else if context.avg_transaction_value > 100000 {
            700
        } else if context.avg_transaction_value > 10000 {
            400
        } else {
            100
        };

        let raw = (threat * 3) + (coherence * 2) + (slashing * 4) + (regulatory * 1) + (log_value * 2);
        let alpha = raw / 12;

        alpha.min(1000)
    }

    pub fn should_reveal(&self, member_idx: usize) -> bool {
        match self.current_regime {
            Regime::Transparent => true,
            Regime::Balanced => member_idx % 2 == 0,
            Regime::Private => false,
        }
    }

    pub fn verify_alpha_sig(&self, sig_alpha: u64) -> Result<bool, GovernanceError> {
        if sig_alpha != self.alpha_threshold {
            return Err(GovernanceError::AlphaMismatch);
        }
        Ok(true)
    }
}
