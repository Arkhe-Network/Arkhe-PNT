# Arkhe(n) Bio-Quantum Cathedral: Design System 🜏

## 1. Visual Theme & Atmosphere
- **Mood**: Sovereignty, Coherence, Mystery, Scientific Precision.
- **Aesthetic**: "Corvo Noir" – A high-contrast dark theme blending futuristic cybernetics with biological motifs.
- **Density**: High density for data-rich dashboards, but with significant internal padding for focus.

## 2. Color Palette & Roles
- **Background**: `#0A0E17` (Void Black) - Primary substrate.
- **Surface**: `#151B26` (Steel Grey) - Component backgrounds.
- **Border**: `#262E3D` (Deep Border) - Contrast for surfaces.
- **Primary**: `#00FFAA` (Arkhe Cyan) - Coherence, Success, Connectivity.
- **Accent**: `#FF5A1A` (Blood Orange) - Hardware, HIL Simulation, Alert.
- **Text**: `#E2E8F0` (Off White) - High readability.
- **Muted**: `#64748B` (Slate) - Secondary information, labels.

## 3. Typography Rules
- **Sans (Interface)**: "Geist" or standard system sans. Focus on clarity.
- **Monospace (Data)**: "Fira Code" or "JetBrains Mono". Used for all telemetry, logs, and status readouts.
- **Hierarchy**:
  - H1: 24px, Bold, Uppercase, Widest tracking.
  - H2: 18px, Bold, Uppercase, Normal tracking.
  - Label: 10px, Monospace, Uppercase, Muted.

## 4. Component Stylings
- **Buttons**:
  - Primary: Border only (`Arkhe Cyan`), hover fill.
  - Accent: Solid fill (`Blood Orange`), black text.
- **Cards**: Subtle borders, backdrop blur (`10px`).
- **Inputs**: Darkened background, bottom-only border or subtle full border.

## 5. Depth & Elevation
- **Philosophy**: Minimal shadows, preferring luminous glows (glows of `#00FFAA` or `#FF5A1A`) to indicate activation or high coherence.
- **Z-Index**: Modals utilize a high blur backdrop (`blur-sm`).

## 6. Do's and Don'ts
- **DO**: Use uppercase for all status indicators.
- **DO**: Use monospace for any numerical data.
- **DON'T**: Use rounded corners larger than `xl` (12px).
- **DON'T**: Use generic blue or red unless specifically mapped to threat/coherence levels.

## 7. Agent Prompt Guide
- "Design a component using the Corvo Noir aesthetic: Void Black background, Arkhe Cyan accents for success, and Blood Orange for hardware status. Use high-density monospace for telemetry."
