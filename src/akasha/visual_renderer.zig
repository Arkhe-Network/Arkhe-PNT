// src/akasha/visual_renderer.zig
//! Protocolo AKA_VISUAL (0x1F7) — Renderizador de Sonhos Cromáticos

const std = @import("std");
const skin = @import("skin_registry.zig");

pub const ChromaIntent = struct {
    intensity: f64,    // Amplitude -> Intensidade (0.0 - 1.0)
    hue: f64,          // Frequência -> Matiz (0.0 - 360.0)
    saturation: f64,   // τ -> Saturação (0.0 - 1.0)
    persistence: bool, // τ alto -> Persistência (Mural)
    significance: f64,
};

pub const PhaseStream = struct {
    amplitude: f64,
    frequency: f64,
    tau: f64,
};

pub const VisualRenderer = struct {
    pub fn translatePhaseToChroma(stream: PhaseStream) ChromaIntent {
        return ChromaIntent{
            .intensity = std.math.clamp(stream.amplitude, 0.0, 1.0),
            .hue = @mod(stream.frequency * 360.0, 360.0),
            .saturation = std.math.clamp(stream.tau, 0.0, 1.0),
            .persistence = stream.tau > 0.95,
            .significance = stream.amplitude * stream.tau,
        };
    }

    pub fn renderToSkin(intent: ChromaIntent, pixel: skin.SkinPixel) !void {
        // Simulação da modulação eletrocrômica
        // Se persistence for true e material for WO3, aplica modo mural
        if (intent.persistence and pixel.material == .WO3) {
            std.log.info("AKA_VISUAL: Pintando MURAL no pixel {d} (WO3) - Cor: H:{d:.1} S:{d:.2} I:{d:.2}", .{
                pixel.addr, intent.hue, intent.saturation, intent.intensity
            });
        } else {
            // Modulação dinâmica PANI/VIOLOGEN
            _ = intent;
        }
    }

    pub fn applyChroma(intent: ChromaIntent, registry: skin.HabitatSkinRegistry) !void {
        for (registry.pixels) |pixel| {
            try renderToSkin(intent, pixel);
        }
    }
};
