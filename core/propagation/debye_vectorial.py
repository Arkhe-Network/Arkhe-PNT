import torch
from typing import Optional, Dict, Any
from core.optics.sellmeier_dispersion import DispersiveMaterial, create_dispersive_interface

class DebyeVectorialPropagator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dispersive_interface = None
        if config.get('material1') and config.get('material2') and config.get('wavelength'):
            self.dispersive_interface = create_dispersive_interface(
                config['material1'],
                config['material2'],
                config['wavelength'] * 1e6  # Convert m → μm for Sellmeier
            )

    def propagate(self, U_in: torch.Tensor, wavelength: Optional[float] = None) -> torch.Tensor:
        """
        Propagate incident field with optional wavelength-dependent Fresnel coefficients.

        Args:
            U_in: Incident field at lens pupil
            wavelength: Optional wavelength in meters for dispersive interface

        Returns:
            U_focal: Vectorial field at focal plane
        """
        # Use wavelength-specific interface if provided and material is dispersive
        interface = self.dispersive_interface
        if wavelength is not None and self.dispersive_interface is not None:
            # Re-evaluate refractive indices at new wavelength
            wavelength_um = wavelength * 1e6
            interface = create_dispersive_interface(
                self.dispersive_interface.material1.split()[0],  # Extract base name
                self.dispersive_interface.material2.split()[0],
                wavelength_um
            )

        # ... mock rest of propagation for now
        return U_in
