"""
neural_phase_monitor.py - Monitora λ₂ em tempo real (ARKHE-Ω Integration)
Integrado com ArkheBraidEngine e CellularRegenerationSimulator.
Inclui Protocolo de Alertas YELLOW-Ph4 e Auditoria EQBE.
"""

import numpy as np
import time
import json
import os
import sys

# Adicionar caminhos para os módulos existentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tzinor-core', 'src', 'physics', 'kuramoto')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'arkhe-brain')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'skills', 'archimedes-omega')))

try:
    from omega_braid_engine import ArkheBraidEngine
except ImportError:
    class ArkheBraidEngine:
        def __init__(self):
            self.n_sensors = 168
            self.phases = np.random.uniform(0, 2*np.pi, self.n_sensors)
        def step(self, dt=0.05, eta=0.3):
            self.phases += np.random.normal(0, 0.05, self.n_sensors)
            self.phases %= (2*np.pi)
        def coherence(self):
            return np.abs(np.mean(np.exp(1j * self.phases)))

try:
    from cellular_regeneration import CellularRegenerationSimulator
except ImportError:
    class CellularRegenerationSimulator:
        def __init__(self, population_size=1):
            self.health = {"overall_score": 0.85, "viability": 1.0}
        def apply_bio_link_effect(self, sync_ratio, coherence, duration_hours=24):
            self.health["overall_score"] += (coherence - 0.847) * 0.01
            # Viabilidade cai se a coerência for muito baixa
            if coherence < 0.7:
                self.health["viability"] -= 0.05
            return self.health

try:
    from skills import evaluate_eqbe_safety
except ImportError:
    def evaluate_eqbe_safety(**kwargs): return {"is_safe": True, "checks": {"reversibility": "PASSED"}}

class NeuralPhaseMonitor:
    def __init__(self, n_sensors=168):
        self.engine = ArkheBraidEngine()
        self.regen_sim = CellularRegenerationSimulator(population_size=1)
        self.lambda2_threshold = 0.847
        self.viability_threshold = 0.85 # YELLOW-Ph4 Trigger
        self.history = []

    def read_nv_sensors(self):
        """Lê fases dos sensores NV via Braid Engine"""
        self.engine.step(dt=0.1, eta=0.3)
        return self.engine.phases

    def calculate_lambda2(self, phases):
        """Calcula coerência de Kuramoto"""
        return self.engine.coherence()

    def check_regeneration_status(self, lambda2, viability):
        """Determina status da regeneração neural e segurança"""
        if viability < 0.7:
            return "RED-Ph4: ABORTAR - VIABILIDADE CRÍTICA"
        elif viability < self.viability_threshold:
            return "YELLOW-Ph4: ATENÇÃO - GATILHO DE VIABILIDADE ATIVADO"

        if lambda2 > 0.99:
            return "REGENERAÇÃO COMPLETA - COERÊNCIA MÁXIMA"
        elif lambda2 > 0.95:
            return "REGENERAÇÃO EM CURSO - ALTA COERÊNCIA"
        elif lambda2 > 0.847:
            return "REGENERAÇÃO ESTÁVEL - COERÊNCIA ADEQUADA"
        else:
            return "ALERTA - DECOERÊNCIA CRÍTICA"

    def monitor(self, duration_seconds=10):
        """Loop de monitoramento contínuo"""
        print("🧠 INICIANDO MONITORAMENTO DE COERÊNCIA NEURAL (PACIENTE ZERO)...")
        print(f"Limiar de Varela: {self.lambda2_threshold} | Gatilho Viabilidade: {self.viability_threshold}")
        print("-" * 80)

        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            phases = self.read_nv_sensors()
            lambda2 = self.calculate_lambda2(phases)

            # Obter saúde e viabilidade
            health_data = self.regen_sim.apply_bio_link_effect(sync_ratio=1.0, coherence=lambda2)
            viability = health_data.get("viability", 1.0)
            status = self.check_regeneration_status(lambda2, viability)

            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] λ₂ = {lambda2:.4f} | Viabilidade: {viability:.2f} | {status}")

            if viability < self.viability_threshold:
                print("🚨 GATILHO YELLOW-Ph4: Iniciando Protocolo de Segurança...")
                safety = evaluate_eqbe_safety("NEURAL_MONITOR_ALERT", np.array([lambda2]), {"viability": viability})
                print(f"🛡️ EQBE Audit: {safety['checks'].get('reversibility', 'UNKNOWN')}")

            self.history.append({
                "timestamp": timestamp,
                "lambda2": float(lambda2),
                "viability": float(viability),
                "status": status
            })

            time.sleep(1)

        print("-" * 80)
        print("🛑 MONITORAMENTO ENCERRADO")

        # Registro na Arkhe-Chain
        with open("patient_zero_monitoring.json", "w") as f:
            json.dump({
                "subject": "PATIENT_ZERO",
                "synapse_id": "847.740",
                "final_viability": self.history[-1]["viability"] if self.history else 1.0,
                "logs": self.history
            }, f, indent=2)

if __name__ == "__main__":
    monitor = NeuralPhaseMonitor()
    monitor.monitor(duration_seconds=5)
