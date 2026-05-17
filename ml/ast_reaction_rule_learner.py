#!/usr/bin/env python3
"""
ARKHE OS Substrato 241+∞: AST Reaction Rule Learner
Canon: ∞.Ω.∇+++.241.ml.ast_rule_learner
Função: Aprender e adaptar regras de reação semântica via análise AST
com detecção de padrões maliciosos e melhoria contínua via ML.
"""

import ast
import hashlib
import json
import time
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from pathlib import Path

# Import from hardened Unbuildable substrate
from security.ast_attack_detector import ASTAttackDetector, AttackPattern, ASTViolation

logger = logging.getLogger(__name__)

@dataclass
class ReactionRule:
    """Regra de reação semântica com metadados de aprendizado."""
    rule_id: str
    name: str
    ast_pattern: str  # Representação serializada do padrão AST
    allowed_operations: List[str]
    forbidden_patterns: List[str]
    confidence_score: float  # 0.0-1.0 baseado em histórico
    training_samples: int
    last_updated: float
    phi_c_threshold: float = 0.80
    adaptive: bool = True  # Se a regra pode ser atualizada via ML

@dataclass
class RuleLearningEvent:
    """Evento de aprendizado de regra."""
    event_id: str
    rule_id: str
    event_type: str  # "new_pattern_detected", "rule_updated", "false_positive", etc.
    ast_sample: str
    detection_result: Dict
    confidence_delta: float
    timestamp: float
    temporal_seal: Optional[str] = None

class ASTReactionRuleLearner:
    """
    Aprendizado adaptativo de regras de reação via AST+ML.

    Características:
    • Detecção inicial via regras heurísticas (ASTAttackDetector)
    • Aprendizado supervisionado com feedback humano/automático
    • Adaptação contínua baseada em falsos positivos/negativos
    • Scoring de confiança dinâmico por regra
    • Integração com TemporalChain para auditoria de aprendizado
    """

    # Thresholds de aprendizado
    LEARNING_CONFIG = {
        "min_samples_for_adaptation": 50,      # Mínimo de amostras para adaptar regra
        "confidence_update_rate": 0.05,         # Taxa de atualização de confiança
        "false_positive_threshold": 0.15,       # Máximo de FPs antes de revisão
        "pattern_embedding_dim": 128,           # Dimensão para embeddings de padrões AST
    }

    def __init__(
        self,
        temporal_chain=None,
        phi_bus=None,
        model_storage_path: str = "/tmp/arkhe/models/ast_rules"
    ):
        self.detector = ASTAttackDetector()
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        import tempfile
        import os
        if model_storage_path.startswith("/mnt/"):
             model_storage_path = os.path.join(tempfile.gettempdir(), "arkhe_models", "ast_rules")
        self.model_storage = Path(model_storage_path)
        self.model_storage.mkdir(parents=True, exist_ok=True)

        # Regras carregadas
        self._rules: Dict[str, ReactionRule] = {}
        self._learning_events: deque = deque(maxlen=10000)

        # Cache de embeddings para padrões AST (mock para sandbox)
        self._pattern_embeddings: Dict[str, np.ndarray] = {}

        # Carregar regras pré-treinadas se disponíveis
        self._load_pretrained_rules()

    def _load_pretrained_rules(self):
        """Carrega regras pré-treinadas do armazenamento."""
        rules_file = self.model_storage / "pretrained_rules.json"
        if rules_file.exists():
            try:
                data = json.loads(rules_file.read_text())
                for rule_data in data.get("rules", []):
                    rule = ReactionRule(**rule_data)
                    self._rules[rule.rule_id] = rule
                logger.info(f"📥 {len(self._rules)} regras pré-treinadas carregadas")
            except Exception as e:
                logger.warning(f"⚠️  Falha ao carregar regras: {e}")

    def validate_reaction_code(
        self,
        reaction_code: str,
        context: Optional[Dict] = None
    ) -> Tuple[bool, List[ASTViolation], Optional[str]]:
        """
        Valida código de reação com detector AST + regras aprendidas.

        Returns:
            Tuple (is_safe, violations, matched_rule_id or None)
        """
        # 1. Validação heurística inicial
        is_safe, violations = self.detector.validate_transformation(reaction_code, context)

        if not is_safe:
            # Verificar se alguma regra aprendida pode sobrepor a detecção
            matched_rule = self._check_learned_rules(reaction_code, violations)
            if matched_rule and matched_rule.confidence_score > 0.90:
                logger.info(f"🔄 Regra aprendida '{matched_rule.name}' sobrepõe detecção heurística")
                return True, [], matched_rule.rule_id

        return is_safe, violations, None

    def _check_learned_rules(
        self,
        reaction_code: str,
        heuristic_violations: List[ASTViolation]
    ) -> Optional[ReactionRule]:
        """Verifica se regras aprendidas podem validar código rejeitado heurísticamente."""
        # Mock: em produção, usar embeddings + similarity search
        for rule in self._rules.values():
            if not rule.adaptive:
                continue

            # Verificar se violações estão na lista de padrões permitidos da regra
            violation_patterns = [v.pattern.name for v in heuristic_violations]
            if all(vp in rule.allowed_operations for vp in violation_patterns):
                return rule

        return None

    def record_learning_feedback(
        self,
        reaction_code: str,
        validation_result: bool,
        human_feedback: Optional[bool] = None,
        rule_id: Optional[str] = None
    ) -> Optional[RuleLearningEvent]:
        """
        Registra feedback para aprendizado adaptativo.

        Args:
            reaction_code: Código da reação avaliada
            validation_result: Resultado da validação (True=safe, False=unsafe)
            human_feedback: Feedback humano opcional (sobrescreve automático)
            rule_id: ID da regra aplicada (se houver)

        Returns:
            RuleLearningEvent se aprendizado foi aplicado, None caso contrário
        """
        import hashlib

        event_id = hashlib.sha3_256(
            f"{reaction_code}:{validation_result}:{human_feedback}:{time.time()}".encode()
        ).hexdigest()[:12]

        # Determinar tipo de evento
        if human_feedback is not None:
            if human_feedback != validation_result:
                event_type = "false_positive" if validation_result else "false_negative"
            else:
                event_type = "confirmed_correct"
        else:
            event_type = "auto_validated"

        # Calcular delta de confiança se regra envolvida
        confidence_delta = 0.0
        if rule_id and rule_id in self._rules:
            rule = self._rules[rule_id]
            if event_type == "confirmed_correct":
                confidence_delta = self.LEARNING_CONFIG["confidence_update_rate"]
            elif event_type in ("false_positive", "false_negative"):
                confidence_delta = -self.LEARNING_CONFIG["confidence_update_rate"] * 2

            # Atualizar confiança da regra
            rule.confidence_score = np.clip(
                rule.confidence_score + confidence_delta,
                0.0, 1.0
            )
            rule.training_samples += 1
            rule.last_updated = time.time()

            # Verificar se regra precisa de revisão
            if rule.confidence_score < 0.60:
                logger.warning(f"⚠️  Regra '{rule.name}' com confiança baixa: {rule.confidence_score:.2f}")

        # Criar evento de aprendizado
        event = RuleLearningEvent(
            event_id=event_id,
            rule_id=rule_id or "heuristic_only",
            event_type=event_type,
            ast_sample=hashlib.sha3_256(reaction_code.encode()).hexdigest()[:32],
            detection_result={"validation": validation_result, "human_feedback": human_feedback},
            confidence_delta=confidence_delta,
            timestamp=time.time()
        )

        # Ancorar na TemporalChain
        if self.temporal:
            event.temporal_seal = self.temporal.anchor_event("ast_rule_learning_event", {
                "event_id": event_id,
                "rule_id": rule_id,
                "event_type": event_type,
                "confidence_delta": confidence_delta,
                "timestamp": time.time()
            })

        self._learning_events.append(event)

        # Publicar métrica no Phi-Bus
        if self.phi_bus:
            self.phi_bus.publish_metric("ast_rule_learning", {
                "event_type": event_type,
                "rule_id": rule_id,
                "confidence_delta": confidence_delta
            })

        logger.debug(f"🧠 Evento de aprendizado registrado: {event_id} ({event_type})")
        return event

    def adapt_rules_from_feedback(self, batch_size: int = 100):
        """Aplica aprendizado em lote a partir de eventos acumulados."""
        if len(self._learning_events) < batch_size:
            return

        # Agrupar eventos por regra
        events_by_rule = defaultdict(list)
        for event in list(self._learning_events)[-batch_size:]:
            events_by_rule[event.rule_id].append(event)

        adapted_count = 0
        for rule_id, events in events_by_rule.items():
            if rule_id not in self._rules or not self._rules[rule_id].adaptive:
                continue

            rule = self._rules[rule_id]

            # Calcular métricas de desempenho
            confirmed = sum(1 for e in events if e.event_type == "confirmed_correct")
            false_pos = sum(1 for e in events if e.event_type == "false_positive")
            false_neg = sum(1 for e in events if e.event_type == "false_negative")

            # Atualizar confiança baseada em taxa de erro
            total = len(events)
            error_rate = (false_pos + false_neg) / total if total > 0 else 0

            if error_rate > self.LEARNING_CONFIG["false_positive_threshold"]:
                # Reduzir confiança significativamente se taxa de erro alta
                rule.confidence_score *= 0.8
                logger.warning(
                    f"📉 Regra '{rule.name}': confiança reduzida para {rule.confidence_score:.2f} "
                    f"(error_rate={error_rate:.2%})"
                )
            else:
                # Aumentar confiança gradualmente se desempenho bom
                rule.confidence_score = min(1.0, rule.confidence_score + 0.02)

            rule.last_updated = time.time()
            adapted_count += 1

        if adapted_count > 0:
            # Salvar regras atualizadas
            self._save_rules()
            logger.info(f"✅ {adapted_count} regras adaptadas com base em {batch_size} eventos")

    def _save_rules(self):
        """Salva regras atuais no armazenamento."""
        data = {
            "rules": [asdict(r) for r in self._rules.values()],
            "saved_at": time.time(),
            "version": "1.0"
        }
        rules_file = self.model_storage / "pretrained_rules.json"
        rules_file.write_text(json.dumps(data, indent=2))

    def get_rule_statistics(self) -> Dict:
        """Retorna estatísticas de regras aprendidas."""
        if not self._rules:
            return {"total_rules": 0}

        avg_confidence = np.mean([r.confidence_score for r in self._rules.values()])
        adaptive_count = sum(1 for r in self._rules.values() if r.adaptive)

        return {
            "total_rules": len(self._rules),
            "adaptive_rules": adaptive_count,
            "avg_confidence": avg_confidence,
            "high_confidence_rules": sum(1 for r in self._rules.values() if r.confidence_score > 0.90),
            "low_confidence_rules": sum(1 for r in self._rules.values() if r.confidence_score < 0.60),
            "total_learning_events": len(self._learning_events),
            "recent_events_by_type": self._count_recent_events(100)
        }

    def _count_recent_events(self, limit: int) -> Dict[str, int]:
        """Conta eventos recentes por tipo."""
        from collections import Counter
        recent = list(self._learning_events)[-limit:]
        return dict(Counter(e.event_type for e in recent))

    def export_rule_catalog(self, path: str):
        """Exporta catálogo de regras para auditoria externa."""
        catalog = {
            "substrate": "241+∞",
            "canon": "∞.Ω.∇+++.241.ml.ast_rule_learner",
            "exported_at": time.time(),
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "confidence": r.confidence_score,
                    "training_samples": r.training_samples,
                    "phi_c_threshold": r.phi_c_threshold,
                    "adaptive": r.adaptive,
                    "allowed_operations": r.allowed_operations,
                    "forbidden_patterns": r.forbidden_patterns
                }
                for r in self._rules.values()
            ],
            "statistics": self.get_rule_statistics()
        }
        Path(path).write_text(json.dumps(catalog, indent=2))
        logger.info(f"📤 Catálogo de regras exportado: {path}")
