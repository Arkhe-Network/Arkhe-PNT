use serde::{Deserialize, Serialize};

/// Camada ℂ (Fase): Intenções, contextos, prompts multimodais, estados latentes.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MultiModalPrompt {
    pub text_intent: String,
    pub image_data: Option<Vec<u8>>,
    pub audio_data: Option<Vec<u8>>,
    pub sensor_data: Option<Vec<f64>>,
    pub phase_coherence: f64, // O estado latente inicial (a intenção pura)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LatentContext {
    pub history_vector: Vec<f64>,
    pub disambiguation_state: f64,
}

impl MultiModalPrompt {
    pub fn new(intent: &str) -> Self {
        Self {
            text_intent: intent.to_string(),
            image_data: None,
            audio_data: None,
            sensor_data: None,
            phase_coherence: 1.618, // Inicializa na proporção áurea
        }
    }
}
