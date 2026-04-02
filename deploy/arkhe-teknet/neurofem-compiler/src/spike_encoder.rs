/// Codificar uma fase contínua em timing de spike
pub fn phase_to_spike_time(phase: f64, period_ms: f64) -> f64 {
    // Fase 0 = spike no início do período
    // Fase π = spike no meio do período
    (phase / (2.0 * std::f64::consts::PI)) * period_ms
}

/// Decodificar timing de spike de volta para fase
pub fn spike_time_to_phase(spike_time_ms: f64, period_ms: f64) -> f64 {
    (spike_time_ms / period_ms) * 2.0 * std::f64::consts::PI
}

/// Codificar uma sequência de fases LML em padrão de spikes
pub struct SpikePattern {
    pub neuron_id: u64,
    pub spike_times_ms: Vec<f64>,
}

pub fn encode_lml_message(
    symbols: &[crate::labyrinth::LMLSymbol],
    symbol_duration_ms: f64,
) -> Vec<SpikePattern> {
    let mut patterns = Vec::new();
    
    for (i, symbol) in symbols.iter().enumerate() {
        let base_time = i as f64 * symbol_duration_ms;
        
        // Cada símbolo tem uma fase associada
        let spike_time = base_time + phase_to_spike_time(symbol.phase, symbol_duration_ms);
        
        patterns.push(SpikePattern {
            neuron_id: symbol.prime_index,
            spike_times_ms: vec![spike_time],
        });
    }
    
    patterns
}

/// Decodificar padrão de spikes em fases
pub fn decode_spike_pattern(
    spikes: &[SpikePattern],
    period_ms: f64,
) -> Vec<f64> {
    spikes
        .iter()
        .flat_map(|p| &p.spike_times_ms)
        .map(|&t| spike_time_to_phase(t, period_ms))
        .collect()
}
