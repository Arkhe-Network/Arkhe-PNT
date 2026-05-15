import time
from typing import Dict, Optional, Any

from .materials_2d_db import MATERIALS_2D_CATALOG, MoireMaterial
from .qnc_optimizer import QNCCriticalAngleOptimizer

class MoireArkheBridge:
    def __init__(self, temporal_client=None, phi_bus=None):
        self.temporal = temporal_client
        self.phi_bus = phi_bus

    async def run_qnc_optimization(
        self,
        material_key: str,
        temperature_k: float = 4.2,
        use_qnc_prediction: bool = True,
    ) -> Dict:
        """
        Executa otimização de ângulo crítico via QNC e ancora os resultados.

        Combina predição do modelo QNC com otimização local por gradiente
        para encontrar o ângulo de torção que maximiza Φ_C.
        """
        material = MATERIALS_2D_CATALOG.get(material_key)
        if not material:
            raise ValueError(f"Material não encontrado: {material_key}")

        optimizer = QNCCriticalAngleOptimizer()
        optimizer.train(MATERIALS_2D_CATALOG)

        if use_qnc_prediction and optimizer._trained:
            initial_guess = optimizer.predict_optimal_angle(material, temperature_k)
            print(f"🧠 QNC sugeriu ângulo inicial: {initial_guess:.3f}°")
        else:
            initial_guess = material.critical_angles[0] if material.critical_angles else 1.0
            print(f"📐 Usando ângulo crítico conhecido: {initial_guess:.3f}°")

        # Otimização fina via gradiente
        optimal_angle, max_phi_c = optimizer.optimize_via_gradient_ascent(
            material, initial_guess, temperature_k=temperature_k
        )

        result = {
            "material": material.name,
            "initial_guess": initial_guess,
            "optimal_angle": optimal_angle,
            "max_phi_c": max_phi_c,
            "temperature_k": temperature_k,
            "method": "qnc_prediction + gradient_ascent" if use_qnc_prediction else "gradient_ascent",
            "timestamp": time.time(),
        }

        if self.temporal:
            anchor = await self.temporal.anchor_event("qnc_optimization_completed", result)
            result["temporal_seal"] = anchor[:16]

        if self.phi_bus:
            self.phi_bus.sync_phi_c(f"moire_{material_key}_optimized", max_phi_c)

        return result
