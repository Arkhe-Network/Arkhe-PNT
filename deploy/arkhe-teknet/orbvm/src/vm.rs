use std::ffi::c_void;

#[repr(C)]
pub struct OrbVM {
    pub coherence: f64,
    pub state: u64,
}

impl OrbVM {
    pub fn new() -> Self {
        Self {
            coherence: 1.6180339887,
            state: 0,
        }
    }

    pub fn execute_cycle(&mut self) {
        self.state += 1;
        self.coherence *= 1.0001;
    }
}
