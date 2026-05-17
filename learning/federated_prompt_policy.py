#!/usr/bin/env python3
"""
ARKHE OS Substrato 236: Federated Prompt Policy Learning
Canon: ∞.Ω.∇+++.236.federated_prompt_rl
Função: Aprendizado federado de políticas de prompt entre organizações
com privacidade diferencial, agregação segura, e validação Φ_C cross-org.
"""

import asyncio
import hashlib
import json
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum, auto
from collections import defaultdict, deque
import logging
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LocalPolicyUpdate:
    """Atualização local de política para agregação federada."""
    org_id: str
    policy_version: str
    q_table_delta: Dict[str, List[float]]  # state_hash → delta de Q-values
    experience_count: int
    avg_reward: float
    avg_phi_c: float
    dp_noise_epsilon: float  # Ruído de privacidade diferencial aplicado
    timestamp: float = field(default_factory=time.time)
    pqc_signature: Optional[str] = None

@dataclass
class FederatedPolicy:
    """Política federada agregada."""
    policy_id: str
    version: str
    participating_orgs: List[str]
    aggregation_method: str  # "fedavg", "fedprox", "secure_agg"
    global_q_table: Dict[str, List[float]]
    aggregation_phi_c: float
    temporal_seal: Optional[str] = None
    created_at: float = field(default_factory=time.time)

class FederatedPromptPolicyLearner:
    """
    Aprendizado federado de políticas de prompt entre organizações.

    Arquitetura:
    • Cada organização treina política localmente com seus dados de prompt/Φ_C
    • Atualizações são criptografadas e adicionam ruído DP antes do envio
    • Servidor central agrega via FedAvg com validação Φ_C cross-org
    • Política global é distribuída de volta para inferência local
    • Todas as etapas ancoradas na TemporalChain para auditoria

    Privacidade:
    • Ruído Laplace com ε configurável por organização
    • Criptografia homomórfica opcional para agregação segura
    • Validação de contribuições via Φ_C mínimo (0.85)
    """

    # Configurações de aprendizado federado
    CONFIG = {
        "min_orgs_for_aggregation": 3,
        "min_phi_c_for_contribution": 0.85,
        "dp_epsilon_range": (1.0, 5.0),  # Ruído de privacidade diferencial
        "aggregation_method": "fedavg_weighted",  # fedavg | fedprox | secure_agg
        "round_timeout_seconds": 300,
        "min_experiences_per_org": 100,
        "policy_version_format": "v{major}.{minor}.{patch}"
    }

    def __init__(
        self,
        org_id: str,
        action_space: List[str],
        state_dim: int = 64,
        temporal_chain=None,
        phi_bus=None,
        federation_endpoint: Optional[str] = None
    ):
        self.org_id = org_id
        self.action_space = action_space
        self.action_dim = len(action_space)
        self.state_dim = state_dim
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self.federation_endpoint = federation_endpoint

        # Política local (Q-learning simplificado)
        self._local_q_table: Dict[str, np.ndarray] = {}
        self._local_experiences: deque = deque(maxlen=50000)
        self._training_rounds: int = 0

        # Cache de políticas federadas
        self._federated_policies: Dict[str, FederatedPolicy] = {}
        self._current_policy_version: Optional[str] = None

        # Métricas de treinamento
        self._round_metrics: deque = deque(maxlen=100)

    def _state_to_hash(self, prompt: str, context: Dict) -> str:
        """Converte estado em hash para lookup na Q-table."""
        state_str = f"{prompt}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha3_256(state_str.encode()).hexdigest()[:16]

    def select_action(self, prompt: str, context: Dict, epsilon: float = 0.1) -> str:
        """Seleciona ação via ε-greedy usando política atual."""
        state_hash = self._state_to_hash(prompt, context)

        # Carregar política federada se disponível
        policy = self._get_active_policy()
        q_values = policy.global_q_table.get(state_hash) if policy else None

        if q_values is None:
            # Inicializar se necessário
            q_values = np.zeros(self.action_dim)
            if policy:
                policy.global_q_table[state_hash] = q_values

        # ε-greedy
        if np.random.random() < epsilon:
            action_idx = np.random.randint(self.action_dim)
        else:
            action_idx = np.argmax(q_values)

        return self.action_space[action_idx]

    def update_local_policy(
        self,
        prompt: str,
        context: Dict,
        action: str,
        reward: float,
        next_prompt: str,
        next_context: Dict,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95
    ):
        """Atualiza política local via Q-learning."""
        state_hash = self._state_to_hash(prompt, context)
        next_state_hash = self._state_to_hash(next_prompt, next_context)
        action_idx = self.action_space.index(action)

        # Inicializar Q-values se necessário
        if state_hash not in self._local_q_table:
            self._local_q_table[state_hash] = np.zeros(self.action_dim)
        if next_state_hash not in self._local_q_table:
            self._local_q_table[next_state_hash] = np.zeros(self.action_dim)

        # Q-learning update
        current_q = self._local_q_table[state_hash][action_idx]
        max_next_q = np.max(self._local_q_table[next_state_hash])

        self._local_q_table[state_hash][action_idx] = current_q + learning_rate * (
            reward + discount_factor * max_next_q - current_q
        )

        # Registrar experiência
        self._local_experiences.append({
            "prompt": prompt,
            "action": action,
            "reward": reward,
            "phi_c": reward,  # Simplificação: reward ≈ Φ_C
            "timestamp": time.time()
        })

    def compute_local_update(
        self,
        base_policy: Optional[Dict[str, List[float]]] = None
    ) -> LocalPolicyUpdate:
        """Computa atualização local para envio ao servidor federado."""
        # Calcular delta em relação à política base (para FedAvg)
        q_table_delta = {}
        for state_hash, local_q in self._local_q_table.items():
            if base_policy and state_hash in base_policy:
                delta = local_q - np.array(base_policy[state_hash])
                q_table_delta[state_hash] = delta.tolist()
            else:
                # Se não há base, enviar Q-values completos (primeiro round)
                q_table_delta[state_hash] = local_q.tolist()

        # Aplicar ruído de privacidade diferencial (Laplace)
        epsilon = np.random.uniform(*self.CONFIG["dp_epsilon_range"])
        for state_hash in q_table_delta:
            noise = np.random.laplace(0, 1/epsilon, size=len(q_table_delta[state_hash]))
            q_table_delta[state_hash] = (
                np.array(q_table_delta[state_hash]) + noise
            ).tolist()

        # Calcular métricas locais
        experiences = list(self._local_experiences)
        avg_reward = np.mean([e["reward"] for e in experiences]) if experiences else 0.0
        avg_phi_c = np.mean([e["phi_c"] for e in experiences]) if experiences else 0.0

        # Assinar atualização com PQC (mock para sandbox)
        update_json = json.dumps({
            "org_id": self.org_id,
            "q_table_delta_keys": list(q_table_delta.keys())[:10],  # Hash parcial
            "experience_count": len(experiences),
            "timestamp": time.time()
        }, sort_keys=True)
        pqc_signature = hashlib.sha3_256(update_json.encode()).hexdigest()

        return LocalPolicyUpdate(
            org_id=self.org_id,
            policy_version=self._current_policy_version or "v1.0.0",
            q_table_delta=q_table_delta,
            experience_count=len(experiences),
            avg_reward=avg_reward,
            avg_phi_c=avg_phi_c,
            dp_noise_epsilon=epsilon,
            pqc_signature=pqc_signature
        )

    async def submit_to_federation(self, update: LocalPolicyUpdate) -> Dict:
        """Submete atualização local ao servidor de federação."""
        if not self.federation_endpoint:
            logger.warning("⚠️  Federation endpoint not configured — update kept local")
            return {"status": "local_only", "update_id": hashlib.sha3_256(
                json.dumps(update.__dict__, sort_keys=True, default=str).encode()
            ).hexdigest()[:12]}

        payload = {
            "org_id": update.org_id,
            "policy_version": update.policy_version,
            "q_table_delta": update.q_table_delta,
            "experience_count": update.experience_count,
            "avg_reward": update.avg_reward,
            "avg_phi_c": update.avg_phi_c,
            "dp_noise_epsilon": update.dp_noise_epsilon,
            "pqc_signature": update.pqc_signature,
            "timestamp": update.timestamp
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.federation_endpoint}/api/federated/update",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Update federado submetido: {result.get('round_id')}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Falha na submissão federada: HTTP {response.status} — {error}")
                    return {"status": "error", "reason": error}

    async def fetch_federated_policy(self) -> Optional[FederatedPolicy]:
        """Busca política federada agregada do servidor."""
        if not self.federation_endpoint:
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.federation_endpoint}/api/federated/policy",
                headers={"X-Organization-ID": self.org_id},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # Validar assinatura PQC da política federada
                    if not self._verify_federated_policy_signature(data):
                        logger.warning("⚠️  Assinatura PQC da política federada inválida")
                        return None

                    policy = FederatedPolicy(
                        policy_id=data["policy_id"],
                        version=data["version"],
                        participating_orgs=data["participating_orgs"],
                        aggregation_method=data["aggregation_method"],
                        global_q_table={
                            k: np.array(v) for k, v in data["global_q_table"].items()
                        },
                        aggregation_phi_c=data["aggregation_phi_c"],
                        temporal_seal=data.get("temporal_seal"),
                        created_at=data["created_at"]
                    )

                    self._federated_policies[policy.policy_id] = policy
                    self._current_policy_version = policy.version

                    logger.info(
                        f"📥 Política federada recebida: {policy.version} | "
                        f"Orgs: {len(policy.participating_orgs)} | "
                        f"Φ_C: {policy.aggregation_phi_c:.3f}"
                    )

                    # Ancorar recebimento na TemporalChain
                    if self.temporal:
                        await self.temporal.anchor_event("federated_policy_received", {
                            "policy_id": policy.policy_id,
                            "version": policy.version,
                            "orgs_count": len(policy.participating_orgs),
                            "phi_c": policy.aggregation_phi_c,
                            "org_id": self.org_id,
                            "timestamp": time.time()
                        })

                    return policy
                else:
                    logger.warning(f"⚠️  Falha ao buscar política federada: HTTP {response.status}")
                    return None

    def _verify_federated_policy_signature(self, policy_data: Dict) -> bool:
        """Verifica assinatura PQC de política federada recebida."""
        # Mock: em produção, verificar com chave pública da federação
        expected_sig = hashlib.sha3_256(
            f"{policy_data['policy_id']}:{policy_data['version']}".encode()
        ).hexdigest()
        return policy_data.get("pqc_signature") == expected_sig

    def _get_active_policy(self) -> Optional[FederatedPolicy]:
        """Retorna política ativa para inferência."""
        if self._current_policy_version:
            return self._federated_policies.get(
                next((p.policy_id for p in self._federated_policies.values()
                      if p.version == self._current_policy_version), None)
            )
        return None

    async def run_federated_training_round(
        self,
        min_local_experiences: int = 1000
    ) -> Optional[FederatedPolicy]:
        """Executa um round completo de treinamento federado."""
        # Verificar se há experiências suficientes
        if len(self._local_experiences) < min_local_experiences:
            logger.info(f"⏳ Aguardando experiências locais: {len(self._local_experiences)}/{min_local_experiences}")
            return None

        # Buscar política base atual
        base_policy = None
        active = self._get_active_policy()
        if active:
            base_policy = {
                k: v.tolist() if isinstance(v, np.ndarray) else v
                for k, v in active.global_q_table.items()
            }

        # Computar atualização local
        local_update = self.compute_local_update(base_policy)

        # Submeter à federação
        submission_result = await self.submit_to_federation(local_update)
        if submission_result.get("status") != "accepted":
            logger.warning(f"⚠️  Submissão federada não aceita: {submission_result}")
            return None

        # Aguardar agregação e buscar nova política
        await asyncio.sleep(5)  # Tempo para servidor agregar
        new_policy = await self.fetch_federated_policy()

        if new_policy:
            self._training_rounds += 1
            self._round_metrics.append({
                "round": self._training_rounds,
                "orgs": len(new_policy.participating_orgs),
                "phi_c": new_policy.aggregation_phi_c,
                "timestamp": time.time()
            })

            # Publicar métrica no Phi-Bus
            if self.phi_bus:
                await self.phi_bus.publish_metric("federated_training_round", {
                    "round": self._training_rounds,
                    "orgs": len(new_policy.participating_orgs),
                    "phi_c": new_policy.aggregation_phi_c,
                    "org_id": self.org_id
                })

        return new_policy

    def get_training_statistics(self) -> Dict:
        """Retorna estatísticas de treinamento federado."""
        active_policy = self._get_active_policy()

        return {
            "org_id": self.org_id,
            "local_experiences": len(self._local_experiences),
            "local_q_table_size": len(self._local_q_table),
            "training_rounds": self._training_rounds,
            "current_policy_version": self._current_policy_version,
            "active_policy_orgs": len(active_policy.participating_orgs) if active_policy else 0,
            "active_policy_phi_c": active_policy.aggregation_phi_c if active_policy else 0,
            "avg_round_phi_c": np.mean([m["phi_c"] for m in self._round_metrics]) if self._round_metrics else 0,
            "federation_endpoint": self.federation_endpoint
        }
