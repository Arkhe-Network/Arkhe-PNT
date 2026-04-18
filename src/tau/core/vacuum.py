import time
import logging

class VacuumState:
    """
    O Vácuo Hidrodinâmico (v1.1).
    Gerencia o estado ao vivo (RTDB) vs persistência local (ChromaDB/Git).
    """
    def __init__(self):
        self.live_state = {
            "lambda_mesh": 1.0,
            "last_collapse": time.time(),
            "agents": {},
            "task_queue": [],
            "metrics": {
                "ram_usage_gb": 12.0,
                "firebase_size_mb": 150,
                "actions_budget_pct": 15
            }
        }
        self.logger = logging.getLogger("TAU-Vacuum")

    def update_agent(self, agent_id: str, data: dict):
        self.live_state["agents"][agent_id] = {
            "last_ping": time.time(),
            "data": data
        }
        # Em v1.1, heartbeats antigos seriam limpos aqui (TTL 1 dia)

    def get_coherence(self) -> float:
        return self.live_state["lambda_mesh"]

    def set_coherence(self, val: float):
        self.live_state["lambda_mesh"] = val
        self.live_state["last_collapse"] = time.time()

    def get_metrics(self) -> dict:
        return self.live_state["metrics"]
