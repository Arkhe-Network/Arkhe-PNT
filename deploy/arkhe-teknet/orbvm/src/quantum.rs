// Silicon PCW and ZPF Array
pub struct ZPFArray {
    pub modes: usize,
    pub resonance_ghz: f64,
}

impl ZPFArray {
    pub fn new() -> Self {
        Self {
            modes: 1024,
            resonance_ghz: 306.0196847852814532,
        }
    }
}
