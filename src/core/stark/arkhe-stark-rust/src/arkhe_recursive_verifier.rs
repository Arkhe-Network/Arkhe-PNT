// arkhe_recursive_verifier.rs — Circuito de verificação recursiva
// Implementa o operador JOIN: verifica 2 proofs e produz 1 proof

use winterfell::{
    verify, StarkProof, VerifierError, AcceptableOptions,
    math::{fields::f128::BaseElement, FieldElement, StarkField},
    crypto::{hashers::Blake3_256, DefaultRandomCoin},
};
use sha2::{Sha256, Digest};
use serde::{Serialize, Deserialize};
use crate::arkhe_merkabah_air::{MerkabahAir, MerkabahInputs};

/// Estrutura que representa uma proof já verificada (output do JOIN)
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct VerifiedProof {
    pub merkle_root: [u8; 32],
    pub aggregated_coherence: u128,
    pub aggregated_phase: u128,
    pub num_leaf_proofs: u32,
    pub level: u8,
}

/// Circuito de verificação recursiva
/// Em Risc0, isto seria um guest program; em Winterfell, um AIR separado.
pub struct RecursiveJoinCircuit;

impl RecursiveJoinCircuit {
    /// Verifica duas proofs filhas e produz uma proof agregada
    pub fn join(
        left: &StarkProof,
        right: &StarkProof,
        left_inputs: &MerkabahInputs,
        right_inputs: &MerkabahInputs,
    ) -> Result<VerifiedProof, VerifierError> {
        // 1. Verificar proof esquerda
        verify::<MerkabahAir, Blake3_256<BaseElement>, DefaultRandomCoin<Blake3_256<BaseElement>>>(left.clone(), left_inputs.clone(), &AcceptableOptions::OptionSet(vec![left.options().clone()]))?;

        // 2. Verificar proof direita
        verify::<MerkabahAir, Blake3_256<BaseElement>, DefaultRandomCoin<Blake3_256<BaseElement>>>(right.clone(), right_inputs.clone(), &AcceptableOptions::OptionSet(vec![right.options().clone()]))?;

        // 3. Calcular métricas agregadas
        let agg_coherence = (left_inputs.final_coherence + right_inputs.final_coherence)
            / BaseElement::new(2);

        // Média circular da fase simplificada para o field de inteiros:
        // Apenas a média aritmética sobre o campo, assumindo que as fases não contornam 2pi
        // de maneira problemática para o caso médio.
        let agg_phase = (left_inputs.final_phase + right_inputs.final_phase) / BaseElement::new(2);

        // 4. Merkle root dos commitments
        let mut hasher = Sha256::new();
        hasher.update(&left.to_bytes());
        hasher.update(&right.to_bytes());
        let merkle_root = hasher.finalize().into();

        Ok(VerifiedProof {
            merkle_root,
            aggregated_coherence: agg_coherence.as_int(),
            aggregated_phase: agg_phase.as_int(),
            num_leaf_proofs: 2,
            level: 1,
        })
    }

    /// Agrega N proofs via árvore binária
    pub fn aggregate_tree(
        proofs: &[StarkProof],
        inputs: &[MerkabahInputs],
    ) -> Result<VerifiedProof, VerifierError> {
        assert_eq!(proofs.len(), inputs.len());
        assert!(proofs.len().is_power_of_two(), "N deve ser potência de 2");

        let mut current: Vec<(StarkProof, MerkabahInputs)> =
            proofs.iter().cloned().zip(inputs.iter().cloned()).collect();

        let mut level: u8 = 0;
        while current.len() > 1 {
            let mut next = Vec::new();
            for i in (0..current.len()).step_by(2) {
                let (left_p, left_i) = &current[i];
                let (right_p, right_i) = &current[i + 1];

                let joined = Self::join(left_p, right_p, left_i, right_i)?;

                // Criar proof dummy para próximo nível (em produção: gerar STARK real)
                let dummy_proof_bytes = vec![];
                let dummy_proof = StarkProof::from_bytes(&dummy_proof_bytes).unwrap_or(left_p.clone());
                next.push((dummy_proof, MerkabahInputs::from_joined(&joined)));
            }
            current = next;
            level += 1;
        }

        Ok(VerifiedProof {
            merkle_root: current[0].0.to_bytes()[0..32].try_into().unwrap_or([0; 32]),
            aggregated_coherence: current[0].1.final_coherence.as_int(),
            aggregated_phase: current[0].1.final_phase.as_int(),
            num_leaf_proofs: proofs.len() as u32,
            level,
        })
    }
}