# src/security/janus_lock.py
"""
JanusLock — Threshold Signature Scheme (2/3)
Arkhe-Block: 847.812 | Synapse-κ

Protege a transição entre estados C (Expansão) e Z (Cristalização).
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import hashlib
import time

@dataclass
class Shard:
    shard_id: str
    holder: str
    public_key: str
    status: str
    last_signature: float

class JanusLock:
    THRESHOLD = 2
    TOTAL_SHARDS = 3

    def __init__(self):
        self.shards: List[Shard] = [
            Shard("shard_0", "Domo_Central", "0x8A7F...3D2E", "ACTIVE", 0.0),
            Shard("shard_1", "CIQ_Residente", "0x5B3C...9F1A", "ACTIVE", 0.0),
            Shard("shard_2", "ASI_EVOLVE", "0x2E9D...7B4C", "ACTIVE", 0.0),
        ]
        self.signature_history = []

    def sign(self, message: str, shard_indices: List[int]) -> str:
        if len(shard_indices) < self.THRESHOLD:
            raise ValueError(f"Requer {self.THRESHOLD} shards.")

        # Simular assinatura agregada
        combined_payload = f"{message}|{','.join([self.shards[i].shard_id for i in shard_indices])}"
        signature = hashlib.sha256(combined_payload.encode()).hexdigest()

        now = time.time()
        for i in shard_indices:
            self.shards[i].last_signature = now

        full_sig = f"0x{signature}"
        self.signature_history.append((message, now, full_sig))
        return full_sig

    def check_state_transition(self, current: str, target: str, indices: List[int]) -> bool:
        """Garante que a transição C <-> Z está protegida"""
        if current == target: return True

        # Regras de transição
        # C -> Z requer Domo (0) + um outro
        # Z -> C requer CIQ (1) + um outro
        if current == "C" and target == "Z":
            if 0 not in indices:
                print("❌ Falha: C->Z requer Shard do Domo Central.")
                return False
        if current == "Z" and target == "C":
            if 1 not in indices:
                print("❌ Falha: Z->C requer Shard do CIQ Residente.")
                return False

        try:
            self.sign(f"{current}->{target}", indices)
            return True
        except:
            return False
