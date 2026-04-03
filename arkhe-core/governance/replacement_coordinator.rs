// arkhe-core/governance/replacement_coordinator.rs
// Protocolo de Re‑entanglement de Substituição – Ressonância de Gizé Dinâmica

use std::collections::HashMap;
use crate::governance::standby_health_prover::{StandbyNode, StandbyStatus};

#[derive(Debug, Clone)]
pub struct QDNode {
    pub id: [u8; 32],
    pub t2_star: u64,     // μs * 1000
    pub stake: u64,       // λΩ
    pub uptime: f64,      // 0.0 - 1.0
    pub latency_ms: u64,
}

#[derive(Debug)]
pub enum RemovalReason {
    Retirement,
    SlashingSevero,
    FalhaSilenciosa,
    AtualizacaoPlanejada,
}

pub struct ReplacementCoordinator {
    pub standby_nodes: Vec<StandbyNode>,
    pub active_nodes: HashMap<[u8; 32], QDNode>,
}

impl ReplacementCoordinator {
    pub fn new() -> Self {
        Self {
            standby_nodes: Vec::new(),
            active_nodes: HashMap::new(),
        }
    }

    /// Fase 2: Seleção do melhor substituto baseado na função de pontuação e prova ZK de saúde
    pub fn select_best_standby(&self) -> Option<StandbyNode> {
        self.standby_nodes.iter()
            .filter(|node| node.is_eligible()) // Só considera nós com prova ZK válida
            .map(|node| {
                let score = self.calculate_standby_score(node);
                (score, node)
            })
            .max_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal))
            .map(|(_, node)| node.clone())
    }

    fn calculate_standby_score(&self, node: &StandbyNode) -> f64 {
        let t2 = node.last_health_proof.as_ref().map(|p| p.t2_inferred).unwrap_or(0);
        let t2_factor = (t2 as f64) / 50000.0;
        // Simplificado para o POC
        0.4 * t2_factor + 0.6
    }

    /// Score = 0.4*(T2/50) + 0.3*(Stake/1M) + 0.2*Uptime - 0.1*(Lat/100)
    fn calculate_score(&self, node: &QDNode) -> f64 {
        let w1 = 0.4;
        let w2 = 0.3;
        let w3 = 0.2;
        let w4 = 0.1;

        let t2_factor = (node.t2_star as f64) / 50000.0;
        let stake_factor = (node.stake as f64) / 1000000.0;
        let uptime_factor = node.uptime;
        let latency_factor = 1.0 - (node.latency_ms as f64 / 100.0);

        (w1 * t2_factor) + (w2 * stake_factor) + (w3 * uptime_factor) + (w4 * (latency_factor.max(0.0)))
    }

    /// Fase 4: Redistribuição de Carga e Transferência de Stake
    pub fn execute_replacement(&mut self, old_node_id: &[u8; 32], substitute: StandbyNode, reason: RemovalReason) -> Result<(), String> {
        if !self.active_nodes.contains_key(old_node_id) {
            return Err("Nó antigo não encontrado".to_string());
        }

        // Converte StandbyNode para QDNode ativo
        let new_active = QDNode {
            id: substitute.id,
            t2_star: substitute.last_health_proof.as_ref().map(|p| p.t2_inferred).unwrap_or(0),
            stake: 1000000, // Exemplo: stake mínimo transferido
            uptime: 1.0,
            latency_ms: 10,
        };

        // Simulação de transferência de responsabilidade
        println!("🜏 [COORDINATOR] Substituindo {:?} por {:?} devido a {:?}", old_node_id, substitute.id, reason);

        self.active_nodes.remove(old_node_id);
        self.active_nodes.insert(new_active.id, new_active);

        Ok(())
    }
}
