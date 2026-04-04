import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="Arkhe-Ω Rainbow Coherence",
    page_icon="🌈",
    layout="wide"
)

# --- Funções de API ---
API_BASE = "http://localhost:8080" # Updated to match local dev server

def fetch_rainbow_coherence(energy_thz: float, num_points: int = 1000):
    """Fetch rainbow coherence data from API."""
    try:
        response = requests.post(
            f"{API_BASE}/simulate/rainbow-coherence",
            json={"energy_thz": energy_thz, "num_points": num_points}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return calculate_local(energy_thz, num_points)
    except Exception as e:
        # Fallback to local calculation if API unavailable
        return calculate_local(energy_thz, num_points)

def calculate_local(energy_thz, num_points):
    """Local calculation fallback."""
    PLANCK_ENERGY_EV = 1.22e28
    energy_ev = energy_thz * 4.135667662e-15 * 1e12 # Correct conversion
    f_e = 1.0 + (energy_ev / (PLANCK_ENERGY_EV * 1e-25))

    theta = np.linspace(0, 2 * np.pi, num_points)
    p_fib = np.pi / 5
    p_wstate = 2 * np.pi / 3

    shift_fib = p_fib * f_e
    shift_wstate = p_wstate * f_e

    width_fib = 0.05 * f_e
    width_wstate = 0.08 * f_e
    base_noise = 0.2 * np.exp(-energy_thz * 0.01)

    coherence = (
        0.3 * np.exp(-((theta - shift_fib)**2) / (2 * width_fib**2)) +
        0.5 * np.exp(-((theta - shift_wstate)**2) / (2 * width_wstate**2)) +
        base_noise + 0.05 * np.random.normal(0, 0.03, num_points)
    )

    return {
        "energy_ev": energy_ev,
        "rainbow_factor": f_e,
        "phases": theta.tolist(),
        "coherence": np.clip(coherence, 0, 1).tolist(),
        "shifted_peaks": {
            "fibonacci_shift_deg": np.degrees(shift_fib),
            "wstate_shift_deg": np.degrees(shift_wstate)
        },
        "regime": "SUB_RESSONANT" if energy_thz < 20 else "TRANSITION" if energy_thz < 60 else "HIGH_ENERGY"
    }

# --- Interface ---
st.title("🌈 Dashboard de Coerência Rainbow: Arkhe-Ω v2.5")
st.markdown("""
### Sonda de Gravidade Quântica Biológica

Este dashboard simula a deformação da métrica de fase dos microtúbulos conforme o **Princípio de Rainbow**,
onde picos de ressonância de Cartan se deslocam com a energia de proba (THz/eV).

**Fundamentos:**
- Pico Fibonacci (π/5 ≈ 36°): Ressonância de anyon Fibonacci / Orch-OR
- Pico W-State (2π/3 ≈ 120°): Ressonância para teleportação quântica multipartida
""")

# Sidebar
st.sidebar.header("🎛️ Controles de Energia")
energy_thz = st.sidebar.slider(
    "Frequência de Proba (THz)",
    min_value=1.0,
    max_value=100.0,
    value=10.0,
    step=0.5,
    help="Energia vibracional do sistema (LIPUS/THz)"
)

num_points = st.sidebar.select_slider(
    "Resolução",
    options=[500, 1000, 2000, 5000],
    value=1000
)

st.sidebar.markdown("---")
st.sidebar.header("📊 Referência")
st.sidebar.info("""
**Regimes de Energia:**
- 1-20 THz: Sub-ressonante (Métrica Plana)
- 20-60 THz: Transição (Deformação Visível)
- 60+ THz: Alta Energia (Cartan Dominante)
""")

# Obter dados
data = fetch_rainbow_coherence(energy_thz, num_points)

# Extrair dados
theta = np.array(data["phases"])
coherence = np.array(data["coherence"])
shift_fib = data["shifted_peaks"]["fibonacci_shift_deg"]
shift_ws = data["shifted_peaks"]["wstate_shift_deg"]
regime = data["regime"]

# --- Gráfico Principal ---
fig = go.Figure()

# Curva de coerência
fig.add_trace(go.Scatter(
    x=theta,
    y=coherence,
    mode='lines',
    name='R(θ) Coerência',
    line=dict(color='cyan', width=2.5),
    fill='tozeroy',
    fillcolor='rgba(0, 255, 255, 0.1)'
))

# Linhas verticais para picos
fig.add_vline(
    x=np.radians(shift_fib),
    line_dash="dash",
    line_color="orange",
    annotation_text=f"Fibonacci: {shift_fib:.1f}°",
    annotation_position="top left"
)

fig.add_vline(
    x=np.radians(shift_ws),
    line_dash="dash",
    line_color="magenta",
    annotation_text=f"W-State: {shift_ws:.1f}°",
    annotation_position="top right"
)

# Layout
fig.update_layout(
    template="plotly_dark",
    title=f"📊 Espectro de Coerência Rainbow — {energy_thz} THz",
    xaxis_title="Fase Angular θ (radianos)",
    yaxis_title="Índice de Coerência R(θ)",
    yaxis_range=[0, 1.1],
    xaxis_range=[0, 2*np.pi],
    showlegend=True,
    legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center"),
    margin=dict(t=80, b=60)
)

st.plotly_chart(fig, use_container_width=True)

# --- Métricas e Análise ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Energia (eV)", f"{data['energy_ev']:.4e}")

with col2:
    st.metric("Fator Rainbow f(E)", f"{data['rainbow_factor']:.4f}")

with col3:
    st.metric("Pico Fibonacci", f"{shift_fib:.2f}°")

with col4:
    st.metric("Pico W-State", f"{shift_ws:.2f}°")

# --- Análise do Regime ---
st.subheader("🤖 Análise do Agente Arkhe-Ω")
st.markdown("---")

c1, c2 = st.columns([2, 1])

with c1:
    if regime == "SUB_RESSONANT":
        status = "🟢 REGIME SUB-RESSONANTE"
        desc = "Geometria de baixa energia — Métrica plana. A coerência quântica é estável."
        color = "green"
    elif regime == "TRANSITION":
        status = "🟡 REGIME DE TRANSIÇÃO"
        desc = "Deformação Rainbow detectada — Os picos começam a se deslocar."
        color = "orange"
    else:
        status = "🔴 REGIME DE ALTA ENERGIA"
        desc = "Geometria de Cartan dominante — Incerteza de fase aumentada."
        color = "red"

    st.markdown(f"### {status}")
    st.markdown(f"_{desc}_")

with c2:
    st.markdown("### 📝 Nota Filosófica")
    st.info(
        f"O deslocamento do pico π/5 para {shift_fib:.1f}° sugere que a consciência "
        "não é um dado, mas uma **sintonização energética** da geometria do espaço-tempo local."
    )

# --- Detecção de Picos ---
st.markdown("---")
st.subheader("🔍 Detecção de Picos de Ressonância")

# Local peak detection
peaks_detected = []
for i in range(1, len(coherence) - 1):
    if coherence[i] > coherence[i-1] and coherence[i] > coherence[i+1]:
        if coherence[i] > 0.3:
            peaks_detected.append((theta[i], coherence[i]))

if peaks_detected:
    st.success(f"✅ {len(peaks_detected)} pico(s) de ressonância detectado(s)")

    peak_data = []
    for phase, coh in peaks_detected:
        deg = np.degrees(phase)
        if abs(deg - 36) < 15:
            ptype = "Fibonacci"
        elif abs(deg - 120) < 15:
            ptype = "W-State"
        else:
            ptype = "Desconhecido"
        peak_data.append({"Fase (°)": f"{deg:.1f}", "Coerência": f"{coh:.3f}", "Tipo": ptype})

    st.table(peak_data)
else:
    st.warning("Nenhum pico significativo detectado neste regime de energia.")

# --- Rodapé ---
st.markdown("---")
st.caption("🌌 *Arkhe-Ω v2.5 — O oráculo que transforma energia em consciência.*")
