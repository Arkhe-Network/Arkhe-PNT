import numpy as np

class DielectricInterface:
    def __init__(self, n1: float, n2: float, wavelength: float, material1: str, material2: str):
        self.n1 = n1
        self.n2 = n2
        self.wavelength = wavelength
        self.material1 = material1
        self.material2 = material2
