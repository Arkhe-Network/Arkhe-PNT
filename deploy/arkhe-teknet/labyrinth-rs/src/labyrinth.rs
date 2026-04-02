use crate::{sacks::SacksLUT, eisenstein::Eisenstein};

pub struct Labyrinth {
    sacks: SacksLUT,
    eisenstein_cache: Vec<Eisenstein>,
}

impl Labyrinth {
    pub fn new(max_primes: usize) -> Self {
        let sacks = SacksLUT::new(max_primes);
        // construir cache de coordenadas Eisenstein para cada primo
        let eisenstein_cache = sacks.points.iter()
            .map(|pt| {
                // mapear raio/ângulo para Eisenstein aproximado
                let r = pt.radius;
                let theta = pt.angle;
                let a = (r * theta.cos()).round() as i64;
                let b = (r * theta.sin() / 0.8660254).round() as i64;
                Eisenstein::new(a, b)
            })
            .collect();
        Self { sacks, eisenstein_cache }
    }

    /// Transformada direta: fase → próximo primo
    pub fn forward(&self, current_prime: u64, phase: f64) -> Option<u64> {
        // encontra índice do primo atual
        let idx = self.sacks.points.iter().position(|p| p.prime == current_prime)?;
        let current = &self.sacks.points[idx];
        let current_e = self.eisenstein_cache[idx];

        // calcular direção baseada na fase
        // ... (usar Eisenstein para calcular vizinhos)
        unimplemented!()
    }

    /// Transformada inversa (colapso interferométrico)
    pub fn interferometric_collapse(&self, phases: &[f64]) -> Vec<u64> {
        // implementar Viterbi em treliça de Eisenstein
        unimplemented!()
    }
}
