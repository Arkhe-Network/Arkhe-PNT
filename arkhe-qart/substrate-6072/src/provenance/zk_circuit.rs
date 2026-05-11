use anyhow::Result;
use plonky2::field::types::Field;
use plonky2::iop::witness::{PartialWitness, WitnessWrite};
use plonky2::plonk::circuit_builder::CircuitBuilder;
use plonky2::plonk::circuit_data::{CircuitConfig, CircuitData};
use plonky2::plonk::config::{GenericConfig, PoseidonGoldilocksConfig};
use plonky2::iop::target::Target;

const D: usize = 2;
type C = PoseidonGoldilocksConfig;
type F = <C as GenericConfig<D>>::F;

pub struct ProvenanceCircuit {
    pub circuit_data: CircuitData<F, C, D>,
    pub secret_input: Target,
    pub public_output: Target,
}

impl ProvenanceCircuit {
    pub fn build() -> Result<Self> {
        let config = CircuitConfig::standard_recursion_config();
        let mut builder = CircuitBuilder::<F, D>::new(config);

        // Simple real circuit: secret_input^2 = public_output
        let secret_input = builder.add_virtual_target();
        let public_output = builder.add_virtual_target();

        let squared = builder.mul(secret_input, secret_input);
        builder.connect(squared, public_output);

        builder.register_public_input(public_output);

        let circuit_data = builder.build::<C>();
        Ok(Self { circuit_data, secret_input, public_output })
    }

    pub fn prove(&self, secret: u64) -> Result<plonky2::plonk::proof::ProofWithPublicInputs<F, C, D>> {
        let mut pw = PartialWitness::new();
        pw.set_target(self.secret_input, F::from_canonical_u64(secret))?;
        pw.set_target(self.public_output, F::from_canonical_u64(secret * secret))?;

        self.circuit_data.prove(pw)
    }

    pub fn verify(&self, proof: plonky2::plonk::proof::ProofWithPublicInputs<F, C, D>) -> Result<()> {
        self.circuit_data.verify(proof)
    }
}
