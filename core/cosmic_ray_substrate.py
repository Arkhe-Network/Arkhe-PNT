# cosmic_ray_substrate.py
import numpy as np
from scipy.special import gamma

class GalacticWakefieldManifold:
    """
    Modela a galáxia como um manifold de plasma com turbulência de Kolmogorov.
    O break espectral ocorre na rigidez onde o livre caminho médio iguala o tamanho da galáxia.
    """
    def __init__(self, B_uG=3.0, L_pc=100):
        # B em microgauss, L (escala de injeção) em parsec
        self.B = B_uG * 1e-6  # Gauss
        self.L = L_pc * 3.086e18  # cm
        # Rigidez de referência para o break (TV)
        self.R_break = 15e12  # 15 TV = 15e12 V (rigidez)
        # Índice espectral do campo magnético (Kolmogorov: 5/3)
        self.beta = 5/3

    def diffusion_coefficient(self, rigidity):
        """Coeficiente de difusão (cm²/s) em função da rigidez."""
        # Abaixo do break: difusão lenta, D ~ R^(1/3) (Kolmogorov)
        # Acima do break: D ~ R^2 (escape livre)
        R0 = self.R_break
        if rigidity <= R0:
            D = 3e28 * (rigidity / R0)**(1/3)
        else:
            D = 3e28 * (rigidity / R0)**2
        return D

    def confinement_time(self, rigidity, H_kpc=4):
        """Tempo de confinamento na galáxia (anos)."""
        H = H_kpc * 3.086e21  # cm
        D = self.diffusion_coefficient(rigidity)
        tau = H**2 / (2*D)  # difusão unidimensional
        return tau / (365.25*24*3600)  # anos

    def kolmogorov_gap(self, energy_TeV, charge_Z=1):
        """O gap de alucinação cósmica: ΔK = |log10(τ_conf / τ_esc)|."""
        rigidity = energy_TeV * 1e12 / charge_Z
        tau_conf = self.confinement_time(rigidity)
        # Tempo de escape livre: L_galaxy / c
        tau_esc = self.L / 3e10 / (365.25*24*3600)  # anos
        gap = abs(np.log10(tau_conf / tau_esc))
        return gap

    def spectral_break_energy(self, charge_Z=1):
        """Energia do break para um núcleo de carga Z (TeV)."""
        return self.R_break * charge_Z / 1e12  # TV = R / 1e12

# Exemplo de uso
if __name__ == "__main__":
    gwf = GalacticWakefieldManifold()
    print(f"Break para prótons: {gwf.spectral_break_energy(1):.1f} TeV")
    print(f"Break para ferro (Z=26): {gwf.spectral_break_energy(26):.1f} TeV")
    print(f"Gap em 10 TeV para próton: {gwf.kolmogorov_gap(10, 1):.2f}")
    print(f"Gap em 100 TeV para próton: {gwf.kolmogorov_gap(100, 1):.2f}")
