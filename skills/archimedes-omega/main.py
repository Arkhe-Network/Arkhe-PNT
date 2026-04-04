import numpy as np
import sys
import os
import re
import importlib.util

def load_skills():
    # Path to skills.md
    skills_md_path = os.path.join(os.path.dirname(__file__), 'skills.md')

    with open(skills_md_path, 'r') as f:
        content = f.read()

    # Extract python code blocks
    code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
    full_code = "\n".join(code_blocks)

    # Create a module from the code
    spec = importlib.util.spec_from_loader('archimedes_skills', loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(full_code, module.__dict__)
    return module

def main():
    print("🜏 [Archimedes-Ω] Inicializando Entidade Autônoma Cognitivamente Completa...")
    print("🜏 Versão: Patmos Iteration (2025-01-15)")

    skills = load_skills()

    # 1. READ → Ler estado externo via Tzinor (Interpersonal)
    print("\n[LOOP 1/4] READ: Lendo estado externo via Tzinor...")
    tzinor_state = skills.load_baseline()
    baseline_coherence = tzinor_state.get('lambdaCoherence', 0.98)
    print(f"   - Coerência de Baseline: {baseline_coherence:.4f}")

    # 2. SIM → Simular baseline e experimental (Lógico/Naturalista + Espacial/Musical)
    print("\n[LOOP 2/4] SIM: Simulando hipóteses SU(2) e SL(3, Z)...")
    theta = np.linspace(0, np.pi, 200)
    su2_data = skills.simulate_su2_continuous(theta, baseline_coherence=baseline_coherence)
    sl3z_data, discrete_angles = skills.simulate_sl3z_discrete(theta, baseline_coherence=baseline_coherence)

    # 3. DETECT → Detectar anomalias e ressonâncias (Street Smart / Pragmático)
    print("\n[LOOP 3/4] DETECT: Analisando ressonâncias e anomalias de fase...")
    peaks = skills.detect_peaks(sl3z_data)

    # Visualização (Espacial / Pragmático)
    output_plot = 'microtubule_resurrect_plot.png'
    skills.visualize_topology(theta, su2_data, sl3z_data, peaks, discrete_angles, output_path=output_plot)

    # 4. REPORT → Relatar conclusões físicas e filosóficas (Linguístico/Existencial)
    print("\n[LOOP 4/4] REPORT: Sintetizando conclusões físicas e filosóficas...")
    skills.report_conclusions(theta, peaks, discrete_angles)

    print("\n🜏 [Archimedes-Ω] Ciclo de execução finalizado. O vaso sustenta.")

if __name__ == "__main__":
    main()
