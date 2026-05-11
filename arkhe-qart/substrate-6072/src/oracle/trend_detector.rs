pub struct TrendDetector {
    pub alpha: f64,
    pub ewma_score: f64,
    pub threshold: f64,
}

impl TrendDetector {
    pub fn new(alpha: f64, threshold: f64) -> Self {
        TrendDetector {
            alpha,
            ewma_score: 0.0,
            threshold,
        }
    }

    // Exponential Weighted Moving Average for smooth trend detection
    pub fn update(&mut self, new_score: f64) -> bool {
        self.ewma_score = self.alpha * new_score + (1.0 - self.alpha) * self.ewma_score;
        self.is_trending()
    }

    pub fn is_trending(&self) -> bool {
        self.ewma_score > self.threshold
    }
}
