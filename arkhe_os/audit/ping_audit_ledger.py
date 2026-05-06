import hashlib
import json
from datetime import datetime
from arkhe_os.crypto.zinc import CoSNARKProver
from arkhe_os.parser.frontends.ping_frontend import PingResult

class PingAuditLedger:
    """Ledger imutável de sessões de ping com provas de integridade."""

    def __init__(self, prover: CoSNARKProver, ledger_path: str = "ping_audit.jsonl"):
        self.prover = prover
        self.ledger_path = ledger_path

    def log_session(self, result: PingResult, session_id: str) -> dict:
        """Registra sessão de ping com prova de integridade."""
        entry = {
            "session_id": session_id,
            "target": result.target,
            "coherence": result.coherence,
            "metrics": {
                "rtt_avg": result.rtt_avg_ms,
                "loss": result.loss_rate,
                "jitter": result.jitter_ms,
                "ttl": result.ttl
            },
            "timestamp": datetime.now().isoformat(),
        }
        # Gerar prova CoSNARK de integridade da entrada
        witness = {
            "entry_hash": hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        }
        public_input = {
            "session_id": session_id,
            "target": result.target,
            "timestamp": entry["timestamp"]
        }
        entry["proof"] = self.prover.prove(witness, public_input)

        # Persistir no ledger em formato JSONL
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        return entry
