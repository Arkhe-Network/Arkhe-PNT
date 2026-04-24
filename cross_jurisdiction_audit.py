# cross_jurisdiction_audit.py — Protocolo de auditoria com Merkle Proofs

import hashlib
import json
import time
from typing import List, Tuple, Dict, Any, Optional, Callable
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

@dataclass
class AuditQuery:
    id: str
    framework: str
    article: str
    start_time: float
    end_time: float
    predicate: Callable[[Dict[str, Any]], bool]

@dataclass
class AuditProof:
    query_id: str
    framework: str
    article: str
    merkle_root: str
    merkle_signature: str
    total_events_in_period: int
    compliant_count: int
    proofs: List[Dict[str, Any]]
    generated_at: float

class MerkleTree:
    """Implementação simples de Merkle Tree para auditoria."""
    def __init__(self, events: List[Dict[str, Any]]):
        self.leaves = [self.hash_event(e) for e in events]
        if not self.leaves:
            self.leaves = [hashlib.sha256(b"EMPTY").hexdigest()]
        self.tree = self._build_tree(self.leaves)

    @staticmethod
    def hash_event(event: Dict[str, Any]) -> str:
        event_str = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()

    def _build_tree(self, leaves: List[str]) -> List[List[str]]:
        tree = [leaves]
        while len(tree[-1]) > 1:
            layer = []
            prev_layer = tree[-1]
            for i in range(0, len(prev_layer), 2):
                left = prev_layer[i]
                right = prev_layer[i+1] if i+1 < len(prev_layer) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                layer.append(combined)
            tree.append(layer)
        return tree

    def root(self) -> str:
        return self.tree[-1][0]

    def get_proof(self, leaf_hash: str) -> List[Dict[str, str]]:
        if leaf_hash not in self.leaves:
            return []

        index = self.leaves.index(leaf_hash)
        proof = []
        for layer in self.tree[:-1]:
            is_right = index % 2
            sibling_index = index - 1 if is_right else index + 1
            if sibling_index < len(layer):
                proof.append({
                    "position": "left" if is_right else "right",
                    "hash": layer[sibling_index]
                })
            else:
                proof.append({
                    "position": "right",
                    "hash": layer[index]
                })
            index //= 2
        return proof

class CrossJurisdictionAuditor:
    def __init__(self, private_key_pem: bytes, ledger: Any):
        self.private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        self.ledger = ledger

    async def handle_audit_query(self, query: AuditQuery) -> AuditProof:
        # query: {framework, article, start_time, end_time, predicate}
        events = await self.ledger.query_events(query.start_time, query.end_time)

        # Constrói árvore de Merkle com todos os eventos do período (inclui não‑conformes)
        all_events = await self.ledger.get_all_events_in_period(query.start_time, query.end_time)
        merkle_tree = MerkleTree(all_events)
        root = merkle_tree.root()

        # Assina a raiz com a chave privada da Catedral
        signature = self.private_key.sign(
            root.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        # Seleciona eventos que satisfazem o predicado
        compliant_events = [e for e in events if query.predicate(e)]

        # Gera prova para cada evento conforme: ramos de Merkle
        proofs = []
        for event in compliant_events:
            leaf = MerkleTree.hash_event(event)
            proof_path = merkle_tree.get_proof(leaf)
            proofs.append({
                "event_identifier": hashlib.sha256(str(event.get('id', '')).encode()).hexdigest()[:16],
                "merkle_path": proof_path,
            })

        return AuditProof(
            query_id=query.id,
            framework=query.framework,
            article=query.article,
            merkle_root=root,
            merkle_signature=signature.hex(),
            total_events_in_period=len(all_events),
            compliant_count=len(compliant_events),
            proofs=proofs,
            generated_at=time.time()
        )
