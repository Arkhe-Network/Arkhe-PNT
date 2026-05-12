import time
import hashlib
import json
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np

class ProposalStatus:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"

class DAOArkheGovernance:
    def __init__(self):
        self.proposals = {}
        self.domain_registry = None
        self._mac_learning_buffer = []
        self._constitution_history = []
        self.MAC_LEARNING_THRESHOLD = 0.005

    def set_domain_registry(self, registry):
        self.domain_registry = registry

    def create_proposal(self, title: str, description: str, amendment_type: str,
                        target_domain: Optional[str], proposed_change: Dict,
                        proposer: str, rationale: str, proposer_signature: str) -> str:
        proposal_id = hashlib.sha3_256(f"{title}:{time.time()}".encode()).hexdigest()[:16]
        self.proposals[proposal_id] = {
            "title": title, "description": description, "type": amendment_type,
            "target": target_domain, "change": proposed_change, "proposer": proposer,
            "rationale": rationale, "signature": proposer_signature, "votes": [],
            "status": ProposalStatus.PENDING,
            "created_at": time.time(),
        }
        return proposal_id

    def list_proposals(self, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        proposals = []
        for p in self.proposals.values():
            if status and p["status"] != status:
                continue
            proposals.append(p)
        proposals.sort(key=lambda x: x["created_at"], reverse=True)
        return proposals[:limit]

    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        return self.proposals.get(proposal_id)

    def cast_vote(self, proposal_id: str, voter: str, vote: str, stake: float, voter_signature: str) -> Dict:
        if proposal_id not in self.proposals:
            raise ValueError("Proposta não encontrada")

        self.proposals[proposal_id]["votes"].append({"voter": voter, "vote": vote, "stake": stake})
        return {"total_votes": len(self.proposals[proposal_id]["votes"])}

    def get_statistics(self) -> Dict:
        active = sum(1 for p in self.proposals.values() if p["status"] in [ProposalStatus.PENDING, ProposalStatus.ACTIVE])
        total_votes = sum(len(p["votes"]) for p in self.proposals.values())
        return {
            "active_proposals": active,
            "total_proposals": len(self.proposals),
            "total_votes": total_votes,
            "approval_rate": 0.0
        }

    def verify_signature(self, signature: str, payload: Dict) -> bool:
        return True # Mock validation

    def mac_learning_update(self, case_result: Dict):
        """
        Atualiza aprendizado MAC (Multi-Agent Constitutional).
        Casos de verificação alimentam refinamento dos princípios.
        """
        self._mac_learning_buffer.append({
            "claim": case_result.get("claim"),
            "verdict": case_result.get("verdict"),
            "confidence": case_result.get("confidence"),
            "principles_applied": case_result.get("principles"),
            "outcome": case_result.get("outcome"),
            "domain": case_result.get("domain"),
            "timestamp": time.time()
        })

        if len(self._mac_learning_buffer) >= 100:
            adjustments = self._run_mac_learning_cycle()
            return adjustments
        return None

    def _run_mac_learning_cycle(self) -> Dict:
        """Executa ciclo de aprendizado MAC para refinar princípios."""

        domain_principle_performance = defaultdict(lambda: defaultdict(list))

        for case in self._mac_learning_buffer[-100:]:
            domain = case.get("domain", "general")
            for principle in case.get("principles_applied", []):
                if case["outcome"] == "false_positive":
                    domain_principle_performance[domain][principle].append(-0.01)
                elif case["outcome"] == "false_negative":
                    domain_principle_performance[domain][principle].append(-0.02)
                else:
                    domain_principle_performance[domain][principle].append(0.0)

        adjustments = {}
        for domain, principles in domain_principle_performance.items():
            for principle, scores in principles.items():
                avg_score = np.mean(scores)
                if abs(avg_score) > self.MAC_LEARNING_THRESHOLD:
                    adjustments[f"{domain}.{principle}"] = {
                        "current_weight": 0.2,
                        "suggested_adjustment": avg_score * 0.1,
                        "rationale": f"Performance média: {avg_score:.4f} em {len(scores)} casos",
                        "confidence": min(0.9, len(scores) / 100),
                    }

        self._mac_learning_buffer = []
        return adjustments
