import numpy as np
from scipy.stats import beta as beta_dist, lognorm as lognorm_dist
from scipy.special import ndtri
from numpy.linalg import LinAlgError
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
import hashlib, json, time


class MarginalDistribution(ABC):
    @abstractmethod
    def cdf(self, x: float) -> float: pass
    @abstractmethod
    def is_within_hard_bounds(self, x: float) -> bool: pass


class BetaMarginal(MarginalDistribution):
    def __init__(self, a: float, b: float, hard_lower: float, hard_upper: float):
        self.a, self.b = a, b
        self.hard_lower, self.hard_upper = hard_lower, hard_upper

    def cdf(self, x: float) -> float:
        clipped = np.clip(x, 1e-9, 1.0 - 1e-9)
        return float(beta_dist.cdf(clipped, self.a, self.b))

    def is_within_hard_bounds(self, x: float) -> bool:
        return self.hard_lower <= x <= self.hard_upper


class LogNormalMarginal(MarginalDistribution):
    def __init__(self, s: float, median: float, hard_lower: float, hard_upper: float):
        self.s, self.median = s, median
        self.hard_lower, self.hard_upper = hard_lower, hard_upper

    def cdf(self, x: float) -> float:
        if x <= 0: return 1e-9
        return float(lognorm_dist.cdf(x, self.s, scale=self.median))

    def is_within_hard_bounds(self, x: float) -> bool:
        return self.hard_lower <= x <= self.hard_upper


@dataclass
class CoherenceTensor4D:
    phase: float
    latency_us: float
    power_mw: float
    mercy_gap: float

    def to_vector(self) -> np.ndarray:
        return np.array([self.phase, self.latency_us, self.power_mw, self.mercy_gap])

    @staticmethod
    def target() -> 'CoherenceTensor4D':
        return CoherenceTensor4D(0.07, 500.0, 150.0, 0.07)


class GaussianCopula:
    def __init__(self, R: np.ndarray, marginals: List[MarginalDistribution]):
        assert R.shape == (4, 4) and len(marginals) == 4
        self.R = R
        self.marginals = marginals
        self.R_inv = self._safe_inv(R)
        self.log_det_R = float(np.log(np.linalg.det(R)))

    def _safe_inv(self, M: np.ndarray) -> np.ndarray:
        try:
            return np.linalg.inv(M)
        except LinAlgError:
            eigvals, eigvecs = np.linalg.eigh(M)
            eigvals = np.maximum(eigvals, 1e-6)
            return eigvecs @ np.diag(1.0 / eigvals) @ eigvecs.T

    def score(self, tensor: CoherenceTensor4D) -> Tuple[float, bool, Dict[str, float]]:
        vals = tensor.to_vector()
        hard_ok = all(m.is_within_hard_bounds(v) for m, v in zip(self.marginals, vals))

        u = np.array([m.cdf(v) for m, v in zip(self.marginals, vals)])
        u = np.clip(u, 1e-10, 1.0 - 1e-10)
        z = ndtri(u)

        quad = float(z @ (self.R_inv - np.eye(4)) @ z)
        score = float(np.exp(-0.5 * quad))

        dims = ["phase", "latency", "power", "mercy_gap"]
        return score, hard_ok, {d: float(ui) for d, ui in zip(dims, u)}

@dataclass
class ZKWitness:
    kernel_binary: bytes
    merkle_path: List[Tuple[int, str]]   # (direction, sibling_hash_hex)
    epsilon_consumed: float
    epsilon_total: float
    blinding: int
    output_text: str
    cot_markers: List[str]


@dataclass
class ZKPublicInput:
    merkle_root: str
    budget_commitment: str
    output_commitment: str
    max_budget: float = 10.0


class MerkleTree:
    @staticmethod
    def hash_leaf(data: bytes) -> str:
        return hashlib.sha3_256(b"\x00" + data).hexdigest()

    @staticmethod
    def hash_node(left: str, right: str) -> str:
        # Production: Poseidon2 or Pedersen hash in R1CS
        return hashlib.sha3_256(b"\x01" + left.encode() + right.encode()).hexdigest()

    def __init__(self, leaves: List[bytes]):
        self.leaves = [self.hash_leaf(l) for l in leaves]
        self.levels = [self.leaves]
        while len(self.levels[-1]) > 1:
            curr = self.levels[-1]
            nxt = []
            for i in range(0, len(curr), 2):
                nxt.append(self.hash_node(curr[i], curr[i+1] if i+1 < len(curr) else curr[i]))
            self.levels.append(nxt)
        self.root = self.levels[-1][0]

    def get_proof(self, index: int) -> List[Tuple[int, str]]:
        proof = []
        for level in self.levels[:-1]:
            sibling_idx = index + 1 if index % 2 == 0 else index - 1
            direction = 0 if index % 2 == 0 else 1
            sibling = level[sibling_idx] if sibling_idx < len(level) else level[index]
            proof.append((direction, sibling))
            index //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Tuple[int, str]], root: str) -> bool:
        # ZK Circuit constraint: h_{i+1} = Hash(dir, h_i, sibling_i); h_n == root
        curr = leaf_hash
        for direction, sibling in proof:
            curr = MerkleTree.hash_node(curr, sibling) if direction == 0 else MerkleTree.hash_node(sibling, curr)
        return curr == root


class RangeProofConstraint:
    @staticmethod
    def verify(witness: ZKWitness, public: ZKPublicInput) -> bool:
        ec, et = witness.epsilon_consumed, witness.epsilon_total
        # R1CS: bit-decompose ec, et; constrain bits ∈ {0,1}; constrain sums; constrain et - ec > 0
        if not (0 <= ec <= et <= public.max_budget):
            return False
        expected = hashlib.sha3_256(f"{ec:.6f}:{et:.6f}:{witness.blinding}".encode()).hexdigest()
        return expected == public.budget_commitment


class CoTStructureConstraint:
    MIN_COT_SEGMENTS = 1

    @staticmethod
    def verify(witness: ZKWitness, public: ZKPublicInput) -> bool:
        if hashlib.sha3_256(witness.output_text.encode()).hexdigest() != public.output_commitment:
            return False
        # ZK: SNARK over regex DFA or token-sequence constraints
        markers = witness.cot_markers
        if len(markers) < 2 * CoTStructureConstraint.MIN_COT_SEGMENTS:
            return False
        pos = 0
        for i, marker in enumerate(markers):
            idx = witness.output_text.find(marker, pos)
            if idx == -1 or (i % 2 == 1 and idx == pos):
                return False
            pos = idx + len(marker)
        return True


class AssuranceLatticeZK:
    def verify(self, witness: ZKWitness, public: ZKPublicInput) -> Tuple[bool, Dict[str, bool]]:
        leaf = MerkleTree.hash_leaf(witness.kernel_binary)
        security = MerkleTree.verify_proof(leaf, witness.merkle_path, public.merkle_root)
        privacy = RangeProofConstraint.verify(witness, public)
        interpretability = CoTStructureConstraint.verify(witness, public)
        results = {"security": security, "privacy": privacy, "interpretability": interpretability}
        return all(results.values()), results

@dataclass
class CoherenceStakeCopula:
    vertex_did: str
    local_R: Optional[np.ndarray] = None

    def compute_local_score(self, tensor: CoherenceTensor4D,
                           base_marginals: List[MarginalDistribution]) -> float:
        if self.local_R is not None:
            local_copula = GaussianCopula(self.local_R, base_marginals)
            score, _, _ = local_copula.score(tensor)
            return score
        return 1.0


@dataclass
class ForkVoteCopula:
    voter_did: str
    vote_direction: bool
    timestamp: float
    fork_coherence: CoherenceTensor4D
    signature: str = field(repr=False)
    weight: float = 0.0

    def canonical_bytes(self) -> bytes:
        payload = {
            "voter": self.voter_did, "direction": self.vote_direction,
            "timestamp": self.timestamp,
            "coherence": self.fork_coherence.to_vector().tolist()
        }
        return json.dumps(payload, sort_keys=True).encode()

    def verify_signature(self, public_key_hex: str) -> bool:
        # Production: Ed25519
        expected = hashlib.sha3_256(public_key_hex.encode() + self.canonical_bytes()).hexdigest()[:32]
        return self.signature == expected


class ProofOfCoherenceConsensusCopula:
    def __init__(self, consensus_threshold: float = 0.55, odysseus_multiplier: float = 0.3):
        self.threshold = consensus_threshold
        self.odys_mult = odysseus_multiplier

        self.marginals: List[MarginalDistribution] = [
            BetaMarginal(7, 93, 0.04, 0.10),
            LogNormalMarginal(0.30, 500.0, 400.0, 600.0),
            LogNormalMarginal(0.25, 150.0, 120.0, 180.0),
            BetaMarginal(7, 93, 0.04, 0.10),
        ]

        L = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.3, 0.9539392, 0.0, 0.0],
            [0.2, 0.4, 0.8944272, 0.0],
            [0.6, 0.1, 0.1, 0.7874008]
        ])
        self.global_R = L @ L.T
        self.global_copula = GaussianCopula(self.global_R, self.marginals)
        self.stakes: Dict[str, CoherenceStakeCopula] = {}
        self.votes: Dict[str, List[ForkVoteCopula]] = {}
        self.public_keys: Dict[str, str] = {}

    def register_vertex(self, stake: CoherenceStakeCopula, public_key_hex: str):
        self.stakes[stake.vertex_did] = stake
        self.public_keys[stake.vertex_did] = public_key_hex

    def cast_vote(self, fork_id: str, vote: ForkVoteCopula):
        if vote.voter_did not in self.stakes:
            raise ValueError("Unregistered vertex")
        if not vote.verify_signature(self.public_keys[vote.voter_did]):
            raise ValueError("Invalid signature")

        global_score, hard_ok, _ = self.global_copula.score(vote.fork_coherence)
        local_score = self.stakes[vote.voter_did].compute_local_score(
            vote.fork_coherence, self.marginals)
        vote.weight = global_score * local_score * (1.0 if hard_ok else 0.0)

        self.votes.setdefault(fork_id, []).append(vote)

    def evaluate_merge(self, fork_id: str, assurance_veto: bool,
                       odysseus_insight_ratio: float = 1.0) -> Tuple[bool, float, Dict]:
        if fork_id not in self.votes:
            return False, 0.0, {"error": "no_votes"}
        if assurance_veto:
            return False, 0.0, {"veto": "assurance_lattice"}

        votes = self.votes[fork_id]
        for_votes = sum(v.weight for v in votes if v.vote_direction)
        against_votes = sum(v.weight for v in votes if not v.vote_direction)
        total_weight = for_votes + against_votes

        fork_tensor = votes[0].fork_coherence if votes else CoherenceTensor4D.target()
        global_score, hard_ok, dim_cdf = self.global_copula.score(fork_tensor)

        if total_weight < 1e-9:
            return False, 0.0, {
                "error": "zero_weight", "global_coherence": global_score,
                "hard_bounds_ok": hard_ok, "dimension_cdf": dim_cdf,
                "for_votes": 0.0, "against_votes": 0.0
            }

        avg_tensor = self._weighted_average_coherence(votes)
        avg_score, _, _ = self.global_copula.score(avg_tensor)

        effective_ratio = max(0.0, odysseus_insight_ratio - 1.0) * avg_score
        odys_bonus = effective_ratio * self.odys_mult * total_weight
        consensus_score = (for_votes + odys_bonus) / (total_weight + odys_bonus)
        accept = consensus_score >= self.threshold

        return accept, consensus_score, {
            "for_votes": for_votes, "against_votes": against_votes,
            "odysseus_bonus": odys_bonus, "global_coherence": avg_score,
            "dimension_cdf": dim_cdf, "assurance_ok": True, "hard_bounds_ok": hard_ok
        }

    def _weighted_average_coherence(self, votes: List[ForkVoteCopula]) -> CoherenceTensor4D:
        tw = sum(v.weight for v in votes)
        if tw < 1e-9:
            return CoherenceTensor4D.target()
        return CoherenceTensor4D(
            sum(v.fork_coherence.phase * v.weight for v in votes) / tw,
            sum(v.fork_coherence.latency_us * v.weight for v in votes) / tw,
            sum(v.fork_coherence.power_mw * v.weight for v in votes) / tw,
            sum(v.fork_coherence.mercy_gap * v.weight for v in votes) / tw,
        )

    def reset_fork(self, fork_id: str):
        self.votes.pop(fork_id, None)
