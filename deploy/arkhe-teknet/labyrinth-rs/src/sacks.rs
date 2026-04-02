use rug::Integer;
use std::f64::consts::TAU; // 2π

/// Representa um ponto na Espiral de Sacks com coordenadas (índice, primo, ângulo)
#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize)]
pub struct SacksPoint {
    pub index: u64,
    pub prime: u64,
    pub radius: f64,
    pub angle: f64,   // em radianos, no intervalo [0, 2π)
}

/// Gerador infinito da Espiral de Sacks (lazy)
pub struct SacksSpiral {
    primes: Box<dyn Iterator<Item = u64>>,
    current_index: u64,
}

impl SacksSpiral {
    pub fn new() -> Self {
        Self {
            // Placeholder para o iterador real de primos
            primes: Box::new(2..), 
            current_index: 0,
        }
    }
}

impl Iterator for SacksSpiral {
    type Item = SacksPoint;

    fn next(&mut self) -> Option<Self::Item> {
        let prime = self.primes.next()?;
        self.current_index += 1;
        let r = (self.current_index as f64).sqrt();
        let angle = TAU * r;
        Some(SacksPoint {
            index: self.current_index,
            prime,
            radius: r,
            angle: angle % TAU,
        })
    }
}

/// Cache LUT para consultas rápidas por ângulo (para hardware)
pub struct SacksLUT {
    pub points: Vec<SacksPoint>,
    // buckets para busca rápida por fase
    pub buckets: [Vec<usize>; 360], // 360 buckets de 1° cada
}

impl SacksLUT {
    pub fn new(max_primes: usize) -> Self {
        let spiral = SacksSpiral::new();
        let points: Vec<_> = spiral.take(max_primes).collect();
        let mut buckets = vec![Vec::new(); 360];
        for (i, pt) in points.iter().enumerate() {
            let bucket = (pt.angle.to_degrees().round() as usize) % 360;
            buckets[bucket].push(i);
        }
        Self { points, buckets }
    }

    pub fn nearest_by_phase(&self, phase: f64, n: usize) -> Vec<&SacksPoint> {
        let bucket = (phase.to_degrees().round() as usize) % 360;
        let mut candidates = Vec::new();
        for offset in -5..=5 { // busca vizinhança ±5°
            let b = (bucket as isize + offset + 360) as usize % 360;
            for &idx in &self.buckets[b] {
                candidates.push(&self.points[idx]);
            }
        }
        candidates.sort_by(|a, b| {
            let da = (a.angle - phase).abs();
            let db = (b.angle - phase).abs();
            da.partial_cmp(&db).unwrap()
        });
        candidates.truncate(n);
        candidates
    }
}
