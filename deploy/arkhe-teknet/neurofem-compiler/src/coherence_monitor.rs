use std::collections::HashMap;

/// Monitor de coerência via sincronização de spikes
pub struct CoherenceMonitor {
    /// Histórico de spikes por neurônio
    spike_history: HashMap<u64, Vec<f64>>,
    /// Tamanho da janela temporal (ms)
    window_size: f64,
    /// Coerência calculada
    lambda2: f64,
}

impl CoherenceMonitor {
    pub fn new(window_size: f64) -> Self {
        Self {
            spike_history: HashMap::new(),
            window_size,
            lambda2: 0.0,
        }
    }

    /// Registrar um spike
    pub fn record_spike(&mut self, neuron_id: u64, time_ms: f64) {
        let history = self.spike_history.entry(neuron_id).or_insert_with(Vec::new);
        history.push(time_ms);
        
        // Manter apenas spikes na janela
        let cutoff = time_ms - self.window_size;
        history.retain(|&t| t > cutoff);
        
        // Recalcular coerência
        self.recompute();
    }

    /// Calcular λ₂ a partir da sincronização
    fn recompute(&mut self) {
        let neurons: Vec<_> = self.spike_history.values().collect();
        let n = neurons.len();
        
        if n < 2 {
            self.lambda2 = 0.0;
            return;
        }

        // Calcular matriz de correlação baseada em coincidência de spikes
        let mut correlation = vec![vec![0.0; n]; n];
        
        for (i, hist_i) in neurons.iter().enumerate() {
            for (j, hist_j) in neurons.iter().enumerate() {
                if i != j {
                    // Contar spikes coincidentes (dentro de tolerance)
                    let tolerance = 0.5; // ms
                    let mut coincident = 0;
                    
                    for &t_i in *hist_i {
                        for &t_j in *hist_j {
                            if (t_i - t_j).abs() < tolerance {
                                coincident += 1;
                            }
                        }
                    }
                    
                    let total = hist_i.len().max(hist_j.len());
                    if total > 0 {
                        correlation[i][j] = coincident as f64 / total as f64;
                    }
                }
            }
        }

        // λ₂ é o menor valor singular da matriz de correlação
        // Simplificação: usar traço como proxy
        let trace: f64 = correlation
            .iter()
            .map(|row| row.iter().sum::<f64>())
            .sum();
        
        self.lambda2 = trace / (n * n) as f64;
    }

    pub fn lambda2(&self) -> f64 {
        self.lambda2
    }

    pub fn is_coherent(&self) -> bool {
        self.lambda2 >= 1.618
    }

    /// Detectar se a rede "colapsou" para solução
    pub fn check_collapse(&self) -> bool {
        // Colapso = todos os neurônios disparando sincronizadamente
        let all_synchronized = self.spike_history.values().all(|hist| {
            hist.len() > 0 && hist.windows(2).all(|w| (w[1] - w[0]).abs() < 1.0)
        });
        
        all_synchronized && self.is_coherent()
    }
}
