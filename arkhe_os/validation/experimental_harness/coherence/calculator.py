# arkhe_os/validation/experimental_harness/coherence/calculator.py
"""Cálculo de coerência entre valor observado e predição Ψ_ToE."""
import numpy as np

class CoherenceCalculator:
    def __init__(self, mercy_gap: tuple = (0.04, 0.10)):
        self.mercy_gap = mercy_gap

    def compute(
        self,
        observed: float,
        observed_err: float,
        predicted: float,
        predicted_err: float
    ) -> tuple[float, bool]:
        """
        Calcula Φ_C como decaimento gaussiano da diferença normalizada.
        Retorna (coherence, mercy_gap_valid).
        """
        if np.isnan(observed) or predicted == 0:
            return 0.0, False

        # Diferença normalizada pela incerteza combinada
        delta = abs(observed - predicted)
        sigma = np.sqrt(observed_err**2 + predicted_err**2 + 1e-10)

        # Coerência: Φ_C = exp(-(delta/sigma)^2 / 2)
        normalized_delta = delta / sigma
        coherence = np.exp(-0.5 * normalized_delta**2)

        # Mercy gap: a diferença relativa deve estar entre 0.04 e 0.10
        relative_delta = delta / abs(predicted) if predicted != 0 else 0.0
        mercy_valid = (self.mercy_gap[0] <= relative_delta <= self.mercy_gap[1])

        return float(coherence), mercy_valid