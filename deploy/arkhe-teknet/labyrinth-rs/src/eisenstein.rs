use num_complex::Complex64;
use std::ops::{Add, Mul};

/// ω = e^(2πi/3) = -1/2 + i√3/2
pub const OMEGA: Complex64 = Complex64 { re: -0.5, im: 0.8660254037844386 };

/// Inteiro de Eisenstein a + bω
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub struct Eisenstein {
    pub a: i64,
    pub b: i64,
}

impl Eisenstein {
    pub fn new(a: i64, b: i64) -> Self {
        Self { a, b }
    }

    /// Norma a² - ab + b²
    pub fn norm(&self) -> i64 {
        self.a * self.a - self.a * self.b + self.b * self.b
    }

    /// Multiplicação por ω (rotação de 60°)
    pub fn mul_omega(self) -> Self {
        // (a + bω) * ω = -b + (a - b)ω
        Self {
            a: -self.b,
            b: self.a - self.b,
        }
    }

    /// Multiplicação por ω² (rotação de 120°)
    pub fn mul_omega2(self) -> Self {
        // (a + bω) * ω² = -a + (a + b)ω? Verificar álgebra
        // Na prática, usar multiplicação por OMEGA no plano complexo
        unimplemented!()
    }

    /// Distância (em número de passos) na rede hexagonal
    pub fn distance(&self, other: &Self) -> f64 {
        let diff_a = self.a - other.a;
        let diff_b = self.b - other.b;
        let re = diff_a as f64 - 0.5 * diff_b as f64;
        let im = (3.0f64).sqrt() * 0.5 * diff_b as f64;
        (re * re + im * im).sqrt()
    }

    /// Converte para Complex64 (plano complexo)
    pub fn to_complex(&self) -> Complex64 {
        Complex64::new(
            self.a as f64 - 0.5 * self.b as f64,
            (3.0f64).sqrt() * 0.5 * self.b as f64,
        )
    }
}

impl Add for Eisenstein {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Self {
            a: self.a + other.a,
            b: self.b + other.b,
        }
    }
}

impl Mul for Eisenstein {
    type Output = Self;
    fn mul(self, other: Self) -> Self {
        // (a + bω)(c + dω) = ac + (ad + bc)ω + bdω²
        // ω² = -1 - ω
        // Portanto: ac - bd + (ad + bc - bd)ω
        Self {
            a: self.a * other.a - self.b * other.b,
            b: self.a * other.b + self.b * other.a - self.b * other.b,
        }
    }
}
