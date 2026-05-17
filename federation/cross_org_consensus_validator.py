#!/usr/bin/env python3
"""
ARKHE OS Substrato 236: Cross-Org Consensus Validator
Canon: ∞.Ω.∇+++.236.cross_org_consensus
Função: Validação de configurações federadas via consenso multi-org
com ponderação por Φ_C, detecção de nós maliciosos, e ancoragem imutável.
"""

import asyncio
import hashlib
import json
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum, auto
from collections import defaultdict, deque
import logging
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

class ConsensusOutcome(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    TIMEOUT = "timeout"

@dataclass
class OrgValidationVote:
    """Voto de validação de uma organização."""
    org_id: str
    config_hash: str
    vote: bool  # True = aprovar, False = rejeitar
    confidence: float  # Φ_C do votante
    rationale: str
    pqc_signature: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ConsensusResult:
    """Resultado de rodada de consenso cross-org."""
    consensus_id: str
    config_hash: str
    config_metadata: Dict
    outcome: ConsensusOutcome
    approval_ratio: float
    weighted_phi_c: float
    approving_orgs: List[str]
    rejecting_orgs: List[str]
    abstaining_orgs: List[str]
    temporal_seal: Optional[str] = None
    completed_at: float = field(default_factory=time.time)

class CrossOrgConsensusValidator:
    """
    Validador de configurações federadas via consenso multi-org.

    Protocolo:
    1. Configuração é submetida com hash SHA3-256 e metadados
    2. Cada organização participante valida localmente e emite voto
    3. Votos são ponderados por Φ_C histórico da organização
    4. Consenso é atingido se:
       • ≥ 2/3 dos votos são favoráveis E
       • Φ_C ponderado ≥ 0.90
    5. Resultado é ancorado na TemporalChain com selo PQC
    6. Configurações aprovadas são distribuídas via gossip protocol

    Segurança:
    • Detecção de votos maliciosos via desvio de Φ_C histórico
    • Penalização de organizações com comportamento inconsistente
    • Quórum configurável para diferentes níveis de sensibilidade
    """

    # Thresholds de consenso
    CONFIG = {
        "quorum_ratio": 2/3,           # Mínimo de votos favoráveis
        "min_weighted_phi_c": 0.90,    # Φ_C ponderado mínimo para aprovação
        "min_orgs_for_consensus": 3,   # Mínimo de organizações participantes
        "vote_timeout_seconds": 120,   # Timeout para coleta de votos
        "malicious_vote_threshold": 0.3,  # Desvio máximo de Φ_C histórico
        "trust_decay_factor": 0.99     # Decaimento de trust score por voto malicioso
    }

    def __init__(
        self,
        org_id: str,
        federation_members: List[str],
        temporal_chain=None,
        phi_bus=None,
        guardian=None
    ):
        self.org_id = org_id
        self.federation_members = set(federation_members)
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self.guardian = guardian

        # Trust scores históricos por organização
        self._org_trust_scores: Dict[str, float] = {
            oid: 0.90 for oid in federation_members
        }
        self._org_trust_scores[org_id] = 1.0  # Confiança máxima em si mesmo

        # Cache de votos e resultados
        self._pending_validations: Dict[str, Dict] = {}
        self._consensus_history: deque = deque(maxlen=1000)

        # Estatísticas de votação
        self._vote_stats: Dict[str, List[Dict]] = defaultdict(list)

    async def initiate_validation(
        self,
        config_content: Dict,
        config_metadata: Dict,
        sensitivity_level: str = "standard"  # "low", "standard", "high"
    ) -> str:
        """Inicia processo de validação cross-org para uma configuração."""
        # Calcular hash único da configuração
        config_json = json.dumps(config_content, sort_keys=True)
        config_hash = hashlib.sha3_256(config_json.encode()).hexdigest()

        # Gerar ID único de consenso
        consensus_id = hashlib.sha3_256(
            f"{config_hash}:{time.time()}".encode()
        ).hexdigest()[:12]

        # Preparar payload de validação
        validation_request = {
            "consensus_id": consensus_id,
            "config_hash": config_hash,
            "config_metadata": config_metadata,
            "initiator_org": self.org_id,
            "sensitivity_level": sensitivity_level,
            "timestamp": time.time(),
            "federation_members": list(self.federation_members)
        }

        # Assinar com PQC (mock para sandbox)
        validation_request["pqc_signature"] = hashlib.sha3_256(
            json.dumps(validation_request, sort_keys=True).encode()
        ).hexdigest()

        # Armazenar localmente
        self._pending_validations[consensus_id] = {
            "request": validation_request,
            "votes": {},
            "started_at": time.time(),
            "timeout_at": time.time() + self.CONFIG["vote_timeout_seconds"]
        }

        # Disparar votação para peers
        await self._broadcast_validation_request(validation_request)

        # Ancorar início na TemporalChain
        if self.temporal:
            await self.temporal.anchor_event("cross_org_validation_initiated", {
                "consensus_id": consensus_id,
                "config_hash": config_hash[:16],
                "initiator": self.org_id,
                "sensitivity": sensitivity_level,
                "timestamp": time.time()
            })

        logger.info(f"🗳️  Validação cross-org iniciada: {consensus_id}")
        return consensus_id

    async def _broadcast_validation_request(self, request: Dict):
        """Dispara solicitação de votação para organizações parceiras."""
        tasks = []
        for org_id in self.federation_members:
            if org_id == self.org_id:
                continue
            tasks.append(self._send_vote_request(org_id, request))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_vote_request(self, org_id: str, request: Dict):
        """Envia solicitação de voto para uma organização específica."""
        # Mock: em produção, chamar endpoint de votação da organização
        await asyncio.sleep(0.05)  # Simular latência de rede

        # Simular resposta de voto (em produção: aguardar resposta real)
        vote = await self._simulate_org_vote(org_id, request)
        await self.receive_vote(vote)

    async def _simulate_org_vote(self, org_id: str, request: Dict) -> OrgValidationVote:
        """Simula voto de organização (substituir por chamada real em produção)."""
        # Determinar voto baseado em trust score e aleatoriedade controlada
        trust = self._org_trust_scores.get(org_id, 0.5)

        # Organizações confiáveis tendem a votar de forma consistente
        if trust > 0.85:
            vote = np.random.random() < 0.9  # 90% de chance de aprovar configs válidas
        else:
            vote = np.random.random() < 0.6  # Menos confiável → mais aleatório

        # Gerar rationale
        rationale = "Configuração aprovada" if vote else "Preocupações de segurança detectadas"

        # Assinar voto com PQC (mock)
        vote_payload = f"{org_id}:{request['consensus_id']}:{vote}:{time.time()}"
        pqc_sig = hashlib.sha3_256(vote_payload.encode()).hexdigest()

        return OrgValidationVote(
            org_id=org_id,
            config_hash=request["config_hash"],
            vote=vote,
            confidence=trust,
            rationale=rationale,
            pqc_signature=pqc_sig
        )

    async def receive_vote(self, vote: OrgValidationVote) -> bool:
        """Recebe e processa voto de validação de organização parceira."""
        # Encontrar validação pendente correspondente
        pending = None
        for cid, data in self._pending_validations.items():
            if data["request"]["config_hash"] == vote.config_hash:
                pending = data
                break

        if not pending:
            logger.warning(f"⚠️  Voto recebido para validação desconhecida: {vote.config_hash[:16]}")
            return False

        # Verificar assinatura PQC do voto
        if not self._verify_vote_signature(vote):
            logger.warning(f"⚠️  Assinatura PQC inválida para voto de {vote.org_id}")
            return False

        # Verificar timeout
        if time.time() > pending["timeout_at"]:
            logger.warning(f"⏱️  Voto recebido após timeout: {vote.org_id}")
            return False

        # Registrar voto
        pending["votes"][vote.org_id] = vote

        # Verificar se todos os votos foram recebidos ou timeout
        if len(pending["votes"]) >= len(self.federation_members) - 1 or time.time() > pending["timeout_at"]:
            await self._finalize_consensus(pending["request"]["consensus_id"])

        return True

    def _verify_vote_signature(self, vote: OrgValidationVote) -> bool:
        """Verifica assinatura PQC de voto recebido."""
        # Mock: em produção, verificar com chave pública da organização
        expected_sig = hashlib.sha3_256(
            f"{vote.org_id}:{vote.config_hash}:{vote.vote}:{vote.timestamp}".encode()
        ).hexdigest()
        return vote.pqc_signature == expected_sig

    async def _finalize_consensus(self, consensus_id: str):
        """Finaliza processo de consenso e calcula resultado."""
        pending = self._pending_validations.get(consensus_id)
        if not pending:
            return

        request = pending["request"]
        votes = pending["votes"]

        # Calcular métricas de consenso
        approving = [v for v in votes.values() if v.vote]
        rejecting = [v for v in votes.values() if not v.vote]

        approval_ratio = len(approving) / max(1, len(votes))

        # Calcular Φ_C ponderado dos votos favoráveis
        if approving:
            weighted_phi_c = np.average(
                [v.confidence for v in approving],
                weights=[self._org_trust_scores.get(v.org_id, 0.5) for v in approving]
            )
        else:
            weighted_phi_c = 0.0

        # Determinar outcome
        quorum_met = approval_ratio >= self.CONFIG["quorum_ratio"]
        phi_c_met = weighted_phi_c >= self.CONFIG["min_weighted_phi_c"]
        min_orgs_met = len(votes) >= self.CONFIG["min_orgs_for_consensus"]

        if quorum_met and phi_c_met and min_orgs_met:
            outcome = ConsensusOutcome.APPROVED
        elif approval_ratio < 0.33:
            outcome = ConsensusOutcome.REJECTED
        else:
            outcome = ConsensusOutcome.NEEDS_REVIEW

        # Atualizar trust scores baseado em consistência dos votos
        await self._update_trust_scores(votes, outcome)

        # Criar resultado de consenso
        result = ConsensusResult(
            consensus_id=consensus_id,
            config_hash=request["config_hash"],
            config_metadata=request["config_metadata"],
            outcome=outcome,
            approval_ratio=approval_ratio,
            weighted_phi_c=weighted_phi_c,
            approving_orgs=[v.org_id for v in approving],
            rejecting_orgs=[v.org_id for v in rejecting],
            abstaining_orgs=[oid for oid in self.federation_members if oid not in votes]
        )

        # Ancorar resultado na TemporalChain
        if self.temporal:
            result.temporal_seal = await self.temporal.anchor_event(
                "cross_org_consensus_completed",
                {
                    "consensus_id": consensus_id,
                    "outcome": outcome.value,
                    "approval_ratio": approval_ratio,
                    "weighted_phi_c": weighted_phi_c,
                    "approving_orgs": result.approving_orgs,
                    "rejecting_orgs": result.rejecting_orgs,
                    "config_hash": request["config_hash"][:16],
                    "timestamp": time.time()
                }
            )

        # Publicar métrica no Phi-Bus
        if self.phi_bus:
            await self.phi_bus.publish_metric("cross_org_consensus", {
                "consensus_id": consensus_id,
                "outcome": outcome.value,
                "approval_ratio": approval_ratio,
                "phi_c": weighted_phi_c,
                "orgs_voted": len(votes)
            })

        # Armazenar histórico
        self._consensus_history.append(result)
        self._pending_validations.pop(consensus_id, None)

        # Notificar distribuição se aprovado
        if outcome == ConsensusOutcome.APPROVED:
            await self._distribute_approved_config(request)

        logger.info(
            f"✅ Consenso finalizado: {consensus_id} | "
            f"{outcome.value} | "
            f"Aprovação: {approval_ratio:.1%} | "
            f"Φ_C ponderado: {weighted_phi_c:.3f}"
        )

    async def _update_trust_scores(self, votes: Dict[str, OrgValidationVote], outcome: ConsensusOutcome):
        """Atualiza trust scores baseado em consistência dos votos."""
        if outcome == ConsensusOutcome.NEEDS_REVIEW:
            return  # Sem ajuste em casos ambíguos

        # Determinar voto "correto" baseado no consenso final
        expected_vote = (outcome == ConsensusOutcome.APPROVED)

        for org_id, vote in votes.items():
            current_trust = self._org_trust_scores.get(org_id, 0.5)

            # Penalizar votos inconsistentes com o consenso
            if vote.vote != expected_vote:
                # Verificar se o desvio é justificado (Φ_C baixo do votante)
                if vote.confidence < 0.7:
                    # Voto de baixa confiança → penalidade leve
                    new_trust = current_trust * 0.98
                else:
                    # Voto de alta confiança mas inconsistente → possível comportamento malicioso
                    new_trust = current_trust * self.CONFIG["trust_decay_factor"]
                    logger.warning(
                        f"⚠️  Trust score reduzido para {org_id}: "
                        f"{current_trust:.3f} → {new_trust:.3f} (voto inconsistente)"
                    )
            else:
                # Recompensar consistência
                new_trust = min(1.0, current_trust * 1.01)

            self._org_trust_scores[org_id] = new_trust

            # Registrar estatística de votação
            self._vote_stats[org_id].append({
                "consensus_id": votes[list(votes.keys())[0]].config_hash[:12],
                "vote": vote.vote,
                "expected": expected_vote,
                "trust_before": current_trust,
                "trust_after": new_trust,
                "timestamp": time.time()
            })

    async def _distribute_approved_config(self, request: Dict):
        """Distribui configuração aprovada para organizações da federação."""
        # Mock: em produção, usar gossip protocol ou API de distribuição
        logger.info(f"📤 Distribuindo configuração aprovada: {request['consensus_id']}")

        # Ancorar distribuição na TemporalChain
        if self.temporal:
            await self.temporal.anchor_event("approved_config_distributed", {
                "consensus_id": request["consensus_id"],
                "config_hash": request["config_hash"][:16],
                "distributed_to": list(self.federation_members),
                "timestamp": time.time()
            })

    def get_consensus_statistics(self) -> Dict:
        """Retorna estatísticas de validações cross-org."""
        if not self._consensus_history:
            return {"total_validations": 0}

        by_outcome = defaultdict(int)
        for r in self._consensus_history:
            by_outcome[r.outcome.value] += 1

        return {
            "org_id": self.org_id,
            "total_validations": len(self._consensus_history),
            "by_outcome": dict(by_outcome),
            "avg_approval_ratio": np.mean([r.approval_ratio for r in self._consensus_history]),
            "avg_weighted_phi_c": np.mean([r.weighted_phi_c for r in self._consensus_history]),
            "active_federation_members": len(self.federation_members),
            "avg_trust_scores": {
                oid: score for oid, score in self._org_trust_scores.items()
                if score >= 0.7  # Apenas organizações confiáveis
            },
            "pending_validations": len(self._pending_validations)
        }
