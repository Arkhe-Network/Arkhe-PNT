use neurofem_compiler::*;
// use neurofem_compiler::fem_to_snn::PlasticityRule;

#[test]
fn test_compile_kuramoto_network() {
    let compiler = NeuroFEMCompiler::new();
    
    // 64 osciladores Kuramoto
    let n = 64;
    let coupling = 1.5;
    let frequencies: Vec<f64> = (0..n).map(|i| 1.0 + (i as f64 * 0.01)).collect();
    
    let network = compiler.compile_kuramoto_network(n, coupling, &frequencies);
    
    // Verificar estrutura
    assert_eq!(network.neurons.len(), n);
    assert_eq!(network.synapses.len(), n * (n - 1));
    
    // Verificar pesos
    for syn in &network.synapses {
        assert!((syn.weight - coupling / n as f64).abs() < 0.001);
    }
}

#[test]
fn test_coherence_monitor() {
    let mut monitor = CoherenceMonitor::new(100.0);
    
    // Simular spikes sincronizados
    for t in 0..100 {
        let time = t as f64;
        for neuron in 0..10 {
            monitor.record_spike(neuron, time);
        }
    }
    
    // Deve estar coerente
    assert!(monitor.is_coherent());
    assert!(monitor.check_collapse());
}

#[test]
fn test_loihi_export() {
    let compiler = NeuroFEMCompiler::new();
    let network = compiler.compile_kuramoto_network(
        100,
        1.0,
        &vec![1.0; 100]
    );
    
    let exporter = LoihiExporter::new(Loihi2Config::default());
    let binary = exporter.export(&network).unwrap();
    
    // Verificar tamanhos
    assert!(binary.neuron_config.len() > 0);
    assert!(binary.synapse_config.len() > 0);
}
