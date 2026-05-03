# config/experimental_data_substrate85_89.py
"""
Reference experimental data for validation:
  • Substrate 85: PMMA micro-vortex spectrometer (optical, λ=532nm)
  • Substrate 89: Irrotational antenna array (RF, λ=8.5mm, Ka-band)
"""

from core.validation.experimental_comparison import ExperimentalDataset

SUBSTRATE_85_DATA = ExperimentalDataset(
    substrate_id='85',
    band='optical',
    wavelength=532e-9,  # 532 nm (green laser)
    numerical_aperture=0.35,  # High-NA micro-optics
    focal_length=2.5e-3,  # 2.5 mm focal length

    # Measured values from PMMA vortex spectrometer calibration
    peak_position=0.89e-3,  # 0.89 mm displacement at focal plane
    peak_position_err=0.03e-3,  # ±30 μm measurement uncertainty
    spectral_width_fwhm=42e-6,  # 42 μm FWHM spectral width
    spectral_width_err=3e-6,  # ±3 μm uncertainty
    spatial_coherence=0.94,  # Measured spatial coherence
    coherence_err=0.02,  # ±0.02 uncertainty

    measurement_date='2026-03-15',
    instrument_calibration='NIST-traceable beam profiler, λ/10 wavefront accuracy',
    notes='Micro-vortex array in PMMA; 64-element hexagonal lattice; measured at room temperature'
)

SUBSTRATE_89_DATA = ExperimentalDataset(
    substrate_id='89',
    band='rf',
    wavelength=8.5e-3,  # 8.5 mm (Ka-band, 35 GHz)
    numerical_aperture=0.32,  # Antenna array effective NA
    focal_length=0.15,  # 15 cm focal distance

    # Measured values from irrotational antenna array characterization
    peak_position=15.2e-3,  # 15.2 mm displacement at focal plane
    peak_position_err=0.4e-3,  # ±0.4 mm uncertainty (RF positioning)
    spectral_width_fwhm=1.8e-3,  # 1.8 mm FWHM beam width
    spectral_width_err=0.15e-3,  # ±0.15 mm uncertainty
    spatial_coherence=0.91,  # Measured spatial coherence via interferometry
    coherence_err=0.03,  # ±0.03 uncertainty

    measurement_date='2026-04-02',
    instrument_calibration='Vector network analyzer, phase-locked reference, anechoic chamber',
    notes='Irrotational monopole array; 16-element circular configuration; measured in far-field regime'
)

EXPERIMENTAL_DATASETS = [SUBSTRATE_85_DATA, SUBSTRATE_89_DATA]
