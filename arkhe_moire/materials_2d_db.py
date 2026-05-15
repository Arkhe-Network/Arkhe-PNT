import math
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict

class MaterialClass(Enum):
    TMD = "transition_metal_dichalcogenide"
    GRAPHENE = "graphene_family"
    XENE = "xene"
    PEROVSKITE_2D = "perovskite_2d"       # ← NOVO
    MAGNETIC_TMD = "magnetic_tmd"         # ← NOVO
    JANUS_TMD = "janus_tmd"               # ← NOVO
    VAN_DER_WAALS = "van_der_waals"       # ← NOVO
    TOPOLOGICAL = "topological_insulator"

@dataclass
class MoireMaterial:
    name: str
    formula: str
    material_class: MaterialClass
    lattice_constant_a: float
    monolayer_bandgap_ev: float
    spin_orbit_coupling_ev: float
    critical_angles: List[float]
    phi_c_peak: float
    valley_coherence_time_ps: float
    spin_coherence_time_ps: float
    applications: List[str] = field(default_factory=list)

    def compute_phi_c_at_angle(self, angle: float, temperature_k: float = 4.2) -> float:
        """
        Calcula a coerência Φ_C baseada no ângulo de torção e temperatura.
        Função aproximada que atinge picos nos ângulos críticos.
        """
        if not self.critical_angles:
            return self.phi_c_peak * 0.5  # Valor base

        # O modelo atinge o phi_c_peak no ângulo crítico primário (índice 0)
        closest_angle = min(self.critical_angles, key=lambda a: abs(a - angle))

        # Uma função Lorentziana ao redor do ângulo crítico
        width = 0.5  # largura do pico
        lorentzian = (width**2) / ((angle - closest_angle)**2 + width**2)

        # Degradação com temperatura
        temp_degradation = math.exp(-temperature_k / 300.0)

        return self.phi_c_peak * lorentzian * temp_degradation


MATERIALS_2D_CATALOG: Dict[str, MoireMaterial] = {
    # ── Perovskitas 2D ───────────────────────────────────────────
    "BaTiO3_2d": MoireMaterial(
        name="Barium Titanate (2D)",
        formula="BaTiO₃ (monolayer)",
        material_class=MaterialClass.PEROVSKITE_2D,
        lattice_constant_a=3.99,
        monolayer_bandgap_ev=3.4,
        spin_orbit_coupling_ev=0.05,
        critical_angles=[0.0, 1.8, 4.2],
        phi_c_peak=0.965,
        valley_coherence_time_ps=5.0,
        spin_coherence_time_ps=40.0,
        applications=["ferroelectric_memory", "quantum_capacitors", "moiré_multiferroics"],
    ),
    "SrTiO3_2d": MoireMaterial(
        name="Strontium Titanate (2D)",
        formula="SrTiO₃ (monolayer)",
        material_class=MaterialClass.PEROVSKITE_2D,
        lattice_constant_a=3.90,
        monolayer_bandgap_ev=3.2,
        spin_orbit_coupling_ev=0.03,
        critical_angles=[0.0, 2.0, 4.5],
        phi_c_peak=0.958,
        valley_coherence_time_ps=4.0,
        spin_coherence_time_ps=35.0,
        applications=["superconductivity_interface", "oxide_electronics"],
    ),

    # ── Dicalcogenetos Magnéticos ───────────────────────────────
    "CrI3": MoireMaterial(
        name="Chromium Triiodide",
        formula="CrI₃",
        material_class=MaterialClass.MAGNETIC_TMD,
        lattice_constant_a=6.87,
        monolayer_bandgap_ev=1.2,
        spin_orbit_coupling_ev=0.35,
        critical_angles=[0.0, 1.0, 2.0],
        phi_c_peak=0.988,
        valley_coherence_time_ps=10.0,
        spin_coherence_time_ps=80.0,
        applications=["magnetic_order_control", "spintronics", "moiré_magnetism"],
    ),
    "CrBr3": MoireMaterial(
        name="Chromium Tribromide",
        formula="CrBr₃",
        material_class=MaterialClass.MAGNETIC_TMD,
        lattice_constant_a=6.26,
        monolayer_bandgap_ev=1.4,
        spin_orbit_coupling_ev=0.30,
        critical_angles=[0.0, 1.2, 2.5],
        phi_c_peak=0.982,
        valley_coherence_time_ps=8.0,
        spin_coherence_time_ps=70.0,
        applications=["magnetic_tunnel_junctions", "valley_magnetism"],
    ),
    "Fe3GeTe2": MoireMaterial(
        name="Iron Germanium Telluride",
        formula="Fe₃GeTe₂",
        material_class=MaterialClass.MAGNETIC_TMD,
        lattice_constant_a=4.02,
        monolayer_bandgap_ev=0.0,  # Metálico, mas com forte correlação
        spin_orbit_coupling_ev=0.25,
        critical_angles=[0.0, 1.5, 3.0],
        phi_c_peak=0.975,
        valley_coherence_time_ps=6.0,
        spin_coherence_time_ps=120.0,
        applications=["itinerant_ferromagnetism", "spin_transport", "skyrmions"],
    ),

    # ── Janus TMDs ──────────────────────────────────────────────
    "MoSSe": MoireMaterial(
        name="Molybdenum Sulfide Selenide",
        formula="MoSSe (Janus)",
        material_class=MaterialClass.JANUS_TMD,
        lattice_constant_a=3.22,
        monolayer_bandgap_ev=1.55,
        spin_orbit_coupling_ev=0.22,
        critical_angles=[0.0, 1.1, 3.8],
        phi_c_peak=0.987,
        valley_coherence_time_ps=10.0,
        spin_coherence_time_ps=90.0,
        applications=["piezoelectricity", "photocatalysis", "valley_spin_hall"],
    ),

    # ── Outros materiais de van der Waals ────────────────────────
    "In2Se3": MoireMaterial(
        name="Indium Selenide (α-phase)",
        formula="α-In₂Se₃",
        material_class=MaterialClass.VAN_DER_WAALS,
        lattice_constant_a=4.05,
        monolayer_bandgap_ev=1.39,
        spin_orbit_coupling_ev=0.18,
        critical_angles=[0.0, 0.8, 2.2],
        phi_c_peak=0.980,
        valley_coherence_time_ps=7.0,
        spin_coherence_time_ps=60.0,
        applications=["ferroelectricity", "non_volatile_memory", "photodetectors"],
    ),
}
