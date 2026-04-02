pub use labyrinth_rs::eisenstein::Eisenstein;

#[derive(Debug, Clone)]
pub struct SacksPoint {
    pub radius: f64,
    pub angle: f64,
}

#[derive(Debug, Clone)]
pub struct LMLSymbol {
    pub prime_index: u64,
    pub phase: f64,
}
