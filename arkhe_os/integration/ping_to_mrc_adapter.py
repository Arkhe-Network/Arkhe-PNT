from arkhe_os.mrc.active_path_prober import ActivePathProber, ProbeRequest
from arkhe_os.parser.frontends.ping_frontend import PingResult
from arkhe_os.coherence.adaptive_baseline import AdaptiveBaseline
import numpy as np
import time

class PingToMRCProbeAdapter:
    """Alimenta o MRC com saúde de caminho derivada de ping."""

    def __init__(self, prober: ActivePathProber, baseline: AdaptiveBaseline,
                 trigger_threshold: float = 0.6):
        self.prober = prober
        self.baseline = baseline
        self.trigger_threshold = trigger_threshold

    async def sync(self, result: PingResult) -> None:
        """Processa resultado de ping e atualiza o MRC."""
        # Atualizar baseline com o RTT médio
        self.baseline.update(result.target, result.rtt_avg_ms)
        r_base = self.baseline.get_baseline(result.target)

        # Recalcular coerência com baseline atualizada
        latency_factor = max(0.0, 1.0 - (result.rtt_avg_ms - r_base) / (self.baseline.r_max - r_base + 1e-6))
        coherence = max(0.0, min(1.0,
            latency_factor * (1.0 - result.loss_rate) * np.exp(-0.1 * result.jitter_ms)
        ))

        # Notificar o prober se a coerência estiver baixa
        if coherence < self.trigger_threshold:
            probe = ProbeRequest(
                probe_id=f"ping_{result.target}_{int(time.time())}",
                dest_node=result.target,
                path_id=result.target,  # simplificado
                entropy_value=int(coherence * 100),
                payload_size=64,
                timeout_ms=2000.0,
                priority=1 if coherence < 0.3 else 0
            )
            self.prober.schedule_probe(probe.dest_node, probe.path_id, probe.entropy_value)
