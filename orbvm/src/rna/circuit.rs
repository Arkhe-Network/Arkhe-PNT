//! RNA Circuit — Cascading Molecular Computation
//!
//! Implements cascading RNA circuits for complex computation.

use super::{Ribozyme, Nucleotide};
use std::collections::HashMap;

/// An RNA circuit
pub struct RnaCircuit {
    /// Circuit components
    components: Vec<CircuitComponent>,
    
    /// Connections between components
    connections: Vec<Connection>,
    
    /// Input nodes
    inputs: Vec<String>,
    
    /// Output nodes
    outputs: Vec<String>,
    
    /// State variables
    state: HashMap<String, CircuitState>,
}

#[derive(Debug, Clone)]
pub enum CircuitComponent {
    /// Ribozyme processor
    Ribozyme(Ribozyme),
    /// Toehold switch
    ToeholdSwitch {
        toehold: Vec<Nucleotide>,
        output: Vec<Nucleotide>,
        threshold: f64,
    },
    /// Aptamer sensor
    Aptamer {
        ligand: String,
        k_d: f64,
        output: Vec<Nucleotide>,
    },
    /// Strand displacement gate
    StrandDisplacement {
        toehold: Vec<Nucleotide>,
        migration: Vec<Nucleotide>,
        output: Vec<Nucleotide>,
    },
}

#[derive(Debug, Clone)]
pub struct Connection {
    pub from: String,
    pub to: String,
    pub weight: f64,
}

#[derive(Debug, Clone)]
pub struct CircuitState {
    pub concentration: f64,
    pub phase: f64,
    pub active: bool,
}

impl RnaCircuit {
    /// Create new circuit
    pub fn new() -> Self {
        Self {
            components: vec![],
            connections: vec![],
            inputs: vec![],
            outputs: vec![],
            state: HashMap::new(),
        }
    }
    
    /// Add component
    pub fn add_component(&mut self, id: &str, component: CircuitComponent) {
        self.state.insert(id.to_string(), CircuitState {
            concentration: 0.0,
            phase: 0.0,
            active: false,
        });
        self.components.push(component);
    }
    
    /// Connect components
    pub fn connect(&mut self, from: &str, to: &str, weight: f64) {
        self.connections.push(Connection {
            from: from.to_string(),
            to: to.to_string(),
            weight,
        });
    }
    
    /// Execute circuit
    pub fn execute(&mut self, inputs: HashMap<String, f64>) -> HashMap<String, f64> {
        // Initialize inputs
        for (id, conc) in &inputs {
            if let Some(state) = self.state.get_mut(id) {
                state.concentration = *conc;
                state.active = *conc > 0.0;
            }
        }
        
        // Propagate through connections
        for conn in &self.connections {
            if let Some(from_state) = self.state.get(&conn.from) {
                if from_state.active {
                    if let Some(to_state) = self.state.get_mut(&conn.to) {
                        to_state.concentration += from_state.concentration * conn.weight;
                        to_state.active = true;
                    }
                }
            }
        }
        
        // Collect outputs
        let mut outputs = HashMap::new();
        for id in &self.outputs {
            if let Some(state) = self.state.get(id) {
                outputs.insert(id.clone(), state.concentration);
            }
        }
        
        outputs
    }
    
    /// Create a NOT gate circuit
    pub fn not_gate(ribozyme: Ribozyme) -> Self {
        let mut circuit = Self::new();
        
        circuit.add_component("input", CircuitComponent::Ribozyme(ribozyme.clone()));
        circuit.add_component("output", CircuitComponent::Ribozyme(ribozyme));
        
        circuit.inputs.push("input".to_string());
        circuit.outputs.push("output".to_string());
        
        circuit.connect("input", "output", 1.0);
        
        circuit
    }
    
    /// Create an AND gate circuit
    pub fn and_gate(ribozyme_a: Ribozyme, ribozyme_b: Ribozyme) -> Self {
        let mut circuit = Self::new();
        
        circuit.add_component("input_a", CircuitComponent::Ribozyme(ribozyme_a));
        circuit.add_component("input_b", CircuitComponent::Ribozyme(ribozyme_b));
        circuit.add_component("output", CircuitComponent::Ribozyme(
            Ribozyme::hammerhead_not(&[])
        ));
        
        circuit.inputs.extend(vec!["input_a".to_string(), "input_b".to_string()]);
        circuit.outputs.push("output".to_string());
        
        circuit.connect("input_a", "output", 0.5);
        circuit.connect("input_b", "output", 0.5);
        
        circuit
    }
}
