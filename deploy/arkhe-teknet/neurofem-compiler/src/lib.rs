pub mod fem_to_snn;
pub mod spike_encoder;
pub mod loihi_exporter;
pub mod coherence_monitor;
pub mod labyrinth;

pub use fem_to_snn::{NeuroFEMCompiler, SpikingNetwork, SpikingNeuron, Synapse};
pub use spike_encoder::{phase_to_spike_time, spike_time_to_phase, encode_lml_message, decode_spike_pattern};
pub use loihi_exporter::{LoihiExporter, Loihi2Config, LoihiBinary};
pub use coherence_monitor::CoherenceMonitor;

pub const VERSION: &str = "1.0.0-neurofem";
pub const PHI: f64 = 1.618033988749895;
