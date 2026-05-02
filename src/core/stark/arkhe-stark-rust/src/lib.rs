// lib.rs — Bindings Python para Winterfell via PyO3

use pyo3::prelude::*;
use winterfell::{
    verify, StarkProof, ProofOptions, FieldExtension, AcceptableOptions, TraceTable, StarkDomain, TraceInfo,
    math::{fields::f128::BaseElement},
    crypto::{hashers::Blake3_256, DefaultRandomCoin},
    Prover,
};
use winter_prover::{
    matrix::ColMatrix, TracePolyTable, AuxTraceRandElements, ConstraintCompositionCoefficients,
    DefaultTraceLde, DefaultConstraintEvaluator
};

pub mod arkhe_merkabah_air;
pub mod arkhe_recursive_verifier;

use arkhe_merkabah_air::{MerkabahAir, MerkabahInputs};
use arkhe_recursive_verifier::RecursiveJoinCircuit;

struct MerkabahProver {
    options: ProofOptions,
    inputs: MerkabahInputs,
}

impl Prover for MerkabahProver {
    type BaseField = BaseElement;
    type Air = MerkabahAir;
    type Trace = TraceTable<BaseElement>;
    type HashFn = Blake3_256<BaseElement>;
    type RandomCoin = DefaultRandomCoin<Blake3_256<BaseElement>>;
    type TraceLde<E: winter_math::FieldElement<BaseField = Self::BaseField>> = DefaultTraceLde<E, Self::HashFn>;
    type ConstraintEvaluator<'a, E: winter_math::FieldElement<BaseField = Self::BaseField>> = DefaultConstraintEvaluator<'a, Self::Air, E>;

    fn get_pub_inputs(&self, _trace: &Self::Trace) -> MerkabahInputs {
        self.inputs.clone()
    }

    fn options(&self) -> &ProofOptions {
        &self.options
    }

    fn new_trace_lde<E: winter_math::FieldElement<BaseField = Self::BaseField>>(
        &self,
        trace_info: &TraceInfo,
        main_trace: &ColMatrix<Self::BaseField>,
        domain: &StarkDomain<Self::BaseField>,
    ) -> (Self::TraceLde<E>, TracePolyTable<E>) {
        DefaultTraceLde::new(trace_info, main_trace, domain)
    }

    fn new_evaluator<'a, E: winter_math::FieldElement<BaseField = Self::BaseField>>(
        &self,
        air: &'a Self::Air,
        aux_rand_elements: AuxTraceRandElements<E>,
        composition_coefficients: ConstraintCompositionCoefficients<E>,
    ) -> Self::ConstraintEvaluator<'a, E> {
        DefaultConstraintEvaluator::new(air, aux_rand_elements, composition_coefficients)
    }
}


/// Gera uma proof STARK para um nó Merkabah
#[pyfunction]
fn generate_merkabah_proof(
    node_id: [u8; 32],
    initial_phase: u128,
    target_phase: u128,
    trace_data: Vec<Vec<u128>>,
) -> PyResult<Vec<u8>> {
    let inputs = MerkabahInputs {
        node_id,
        initial_phase: BaseElement::new(initial_phase),
        target_phase: BaseElement::new(target_phase),
        final_phase: BaseElement::new(trace_data.last().unwrap()[0]),
        final_coherence: BaseElement::new(trace_data.last().unwrap()[1]),
    };

    let options = ProofOptions::new(
        80,                     // num_queries
        8,                      // blowup_factor
        16,                     // grinding_factor
        FieldExtension::Quadratic,
        8,                      // FRI folding_factor
        255,                    // FRI max_remainder_size
    );

    let mut trace_columns: Vec<Vec<BaseElement>> = vec![vec![]; 4];
    for row in trace_data {
        for (i, val) in row.into_iter().enumerate() {
            trace_columns[i].push(BaseElement::new(val));
        }
    }
    let trace = TraceTable::init(trace_columns);

    let prover = MerkabahProver { options, inputs };
    let proof = prover.prove(trace)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Proof generation failed: {:?}", e)))?;

    Ok(proof.to_bytes())
}

/// Verifica uma proof STARK
#[pyfunction]
fn verify_merkabah_proof(proof_bytes: Vec<u8>, initial_phase: u128, target_phase: u128, final_phase: u128, final_coherence: u128, node_id: [u8; 32]) -> PyResult<bool> {
    let proof = StarkProof::from_bytes(&proof_bytes)
        .map_err(|_e| pyo3::exceptions::PyRuntimeError::new_err("Invalid proof bytes"))?;

    let inputs = MerkabahInputs {
        node_id,
        initial_phase: BaseElement::new(initial_phase),
        target_phase: BaseElement::new(target_phase),
        final_phase: BaseElement::new(final_phase),
        final_coherence: BaseElement::new(final_coherence)
    };

    let acceptable_options = AcceptableOptions::OptionSet(vec![proof.options().clone()]);

    verify::<MerkabahAir, Blake3_256<BaseElement>, DefaultRandomCoin<Blake3_256<BaseElement>>>(proof, inputs, &acceptable_options)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Verification failed: {:?}", e)))?;

    Ok(true)
}

/// Agrega N proofs recursivamente
#[pyfunction]
fn aggregate_proofs_recursive(
    proofs: Vec<Vec<u8>>,
    inputs_initial_phase: Vec<u128>,
    inputs_target_phase: Vec<u128>,
    inputs_final_phase: Vec<u128>,
    inputs_final_coherence: Vec<u128>,
    inputs_node_id: Vec<[u8; 32]>
) -> PyResult<Vec<u8>> {
    let stark_proofs: Vec<StarkProof> = proofs.iter()
        .map(|p| StarkProof::from_bytes(p).unwrap())
        .collect();

    let inputs: Vec<MerkabahInputs> = (0..proofs.len()).map(|i| MerkabahInputs {
        node_id: inputs_node_id[i],
        initial_phase: BaseElement::new(inputs_initial_phase[i]),
        target_phase: BaseElement::new(inputs_target_phase[i]),
        final_phase: BaseElement::new(inputs_final_phase[i]),
        final_coherence: BaseElement::new(inputs_final_coherence[i]),
    }).collect();

    let result = RecursiveJoinCircuit::aggregate_tree(&stark_proofs, &inputs)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Aggregation failed: {:?}", e)))?;

    Ok(serde_json::to_vec(&result).unwrap())
}

#[pymodule]
fn arkhe_stark_rust(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_merkabah_proof, m)?)?;
    m.add_function(wrap_pyfunction!(verify_merkabah_proof, m)?)?;
    m.add_function(wrap_pyfunction!(aggregate_proofs_recursive, m)?)?;
    Ok(())
}