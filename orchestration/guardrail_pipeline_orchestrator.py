#!/usr/bin/env python3
"""
ARKHE OS Substrato 241+∞: Guardrail Pipeline Orchestrator
Canon: ∞.Ω.∇+++.241.orchestration.guardrail_pipeline
Função: Orquestrar HSM-PQC, Seccomp e AST-ML em pipeline unificado
com gating por Φ_C, health checks e fallbacks configuráveis.
"""

import asyncio
import hashlib
import json
import time
import logging
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum, auto
from pathlib import Path

# Import components from hardened substrates
from security.hsm_pqc_signer import HSMConfig
from security.semantic_molecule_signer import SemanticMoleculeSigner
from security.chemistry_seccomp_runner import ChemistrySeccompRunner, ReactionSandboxProfile
from ml.ast_reaction_rule_learner import ASTReactionRuleLearner

logger = logging.getLogger(__name__)

class GuardrailStatus(Enum):
    """Status de verificação de guardrail."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

@dataclass
class GuardrailCheck:
    """Resultado de verificação de guardrail."""
    guardrail_name: str
    status: GuardrailStatus
    message: str
    confidence: float
    details: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class PipelineExecutionResult:
    """Resultado de execução de pipeline com guardrails."""
    execution_id: str
    reaction_id: str
    guardrail_checks: List[GuardrailCheck]
    overall_status: GuardrailStatus
    output: Optional[Dict]
    signed_molecule: Optional[Dict]
    temporal_seal: Optional[str]
    total_duration_ms: float
    phi_c_score: float

class GuardrailPipelineOrchestrator:
    """
    Orquestrador de pipeline com guardrails unificados.

    Pipeline de execução:
    1. Φ_C Gating: Verificar coerência mínima da molécula/regra
    2. HSM Health Check: Verificar disponibilidade do HSM-PQC
    3. AST-ML Validation: Validar código da reação com regras aprendidas
    4. Seccomp Profile Selection: Selecionar perfil de sandbox apropriado
    5. Reaction Execution: Executar reação em sandbox
    6. Molecule Signing: Assinar molécula resultante com HSM-PQC
    7. TemporalChain Anchoring: Ancorar toda a execução na cadeia temporal
    8. Output Delivery: Retornar resultado com selos de integridade

    Características:
    • Circuit breaker por guardrail para fallbacks configuráveis
    • Health checks contínuos para HSM, seccomp e ML components
    • Logging canônico de todas as verificações e decisões
    • Métricas de Φ_C agregadas para visibilidade operacional
    """

    # Thresholds de pipeline
    PIPELINE_CONFIG = {
        "min_phi_c_for_execution": 0.80,
        "hsm_health_check_interval_sec": 60,
        "seccomp_fallback_profile": ReactionSandboxProfile.CREATIVE_MINIMAL,
        "max_guardrail_failures": 1,  # Permitir 1 warning antes de falhar
        "temporal_anchor_required": True
    }

    def __init__(
        self,
        hsm_config: HSMConfig,
        temporal_chain=None,
        phi_bus=None,
        guardian=None
    ):
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self.guardian = guardian

        # Inicializar componentes de guardrail
        self.molecule_signer = SemanticMoleculeSigner(
            hsm_config=hsm_config,
            temporal_chain=temporal_chain,
            phi_bus=phi_bus
        )

        self.seccomp_runner = ChemistrySeccompRunner(
            temporal_chain=temporal_chain,
            phi_bus=phi_bus
        )

        self.rule_learner = ASTReactionRuleLearner(
            temporal_chain=temporal_chain,
            phi_bus=phi_bus
        )

        # Estado de health checks
        self._hsm_healthy = False
        self._seccomp_available = False
        self._ml_model_loaded = False

        # Histórico de execuções
        self._execution_history: List[PipelineExecutionResult] = []

        # Inicializar componentes
        self._initialize_components()

    def _initialize_components(self):
        """Inicializa componentes e executa health checks iniciais."""
        # HSM
        try:
            self._hsm_healthy = self.molecule_signer.initialize()
            logger.info(f"{'✅' if self._hsm_healthy else '❌'} HSM-PQC: {'saudável' if self._hsm_healthy else 'indisponível'}")
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar HSM: {e}")
            self._hsm_healthy = False

        # Seccomp
        self._seccomp_available = self.seccomp_runner.seccomp._lib is not None
        logger.info(f"{'✅' if self._seccomp_available else '⚠️'} Seccomp: {'disponível' if self._seccomp_available else 'fallback mode'}")

        # ML Rules
        self._ml_model_loaded = len(self.rule_learner._rules) > 0
        logger.info(f"{'✅' if self._ml_model_loaded else 'ℹ️'} AST-ML Rules: {'{len(self.rule_learner._rules)} regras carregadas' if self._ml_model_loaded else 'apenas heurísticas'}")

    async def execute_reaction_pipeline(
        self,
        reaction_code: str,
        input_molecules: List[Dict],
        reaction_name: str,
        phi_c_context: Optional[Dict] = None
    ) -> PipelineExecutionResult:
        """
        Executa pipeline completo de reação com todos os guardrails.

        Args:
            reaction_code: Código Python da reação a executar
            input_molecules: Lista de moléculas de entrada (dicionários)
            reaction_name: Nome descritivo da reação
            phi_c_context: Contexto opcional para scoring de Φ_C

        Returns:
            PipelineExecutionResult com todos os metadados de segurança
        """
        import time
        start_time = time.time()

        # Gerar IDs únicos
        execution_id = hashlib.sha3_256(
            f"{reaction_code}:{reaction_name}:{time.time()}".encode()
        ).hexdigest()[:12]
        reaction_id = hashlib.sha3_256(
            f"{reaction_name}:{json.dumps(input_molecules, sort_keys=True)}".encode()
        ).hexdigest()[:12]

        guardrail_checks: List[GuardrailCheck] = []
        overall_status = GuardrailStatus.PASSED

        # === GUARDRAIL 1: Φ_C Gating ===
        phi_check = await self._check_phi_c_gating(
            input_molecules, reaction_code, phi_c_context
        )
        guardrail_checks.append(phi_check)
        if phi_check.status == GuardrailStatus.FAILED:
            overall_status = GuardrailStatus.FAILED
            return self._build_failed_result(
                execution_id, reaction_id, guardrail_checks,
                "Φ_C gating failed", start_time
            )

        # === GUARDRAIL 2: HSM Health Check ===
        hsm_check = self._check_hsm_health()
        guardrail_checks.append(hsm_check)
        if hsm_check.status == GuardrailStatus.FAILED:
            # Fallback: permitir execução sem assinatura se configurado
            if self.PIPELINE_CONFIG.get("allow_unsigned_fallback", False):
                hsm_check.status = GuardrailStatus.WARNING
                hsm_check.message += " — proceeding without signature"
            else:
                overall_status = GuardrailStatus.FAILED
                return self._build_failed_result(
                    execution_id, reaction_id, guardrail_checks,
                    "HSM health check failed", start_time
                )

        # === GUARDRAIL 3: AST-ML Validation ===
        ast_check = await self._validate_reaction_ast(reaction_code)
        guardrail_checks.append(ast_check)
        if ast_check.status == GuardrailStatus.FAILED:
            overall_status = GuardrailStatus.FAILED
            return self._build_failed_result(
                execution_id, reaction_id, guardrail_checks,
                "AST-ML validation failed", start_time
            )

        # === GUARDRAIL 4: Seccomp Profile Selection ===
        seccomp_check = self._select_seccomp_profile(reaction_code)
        guardrail_checks.append(seccomp_check)
        selected_profile = seccomp_check.details.get("selected_profile")

        # === EXECUTION: Run Reaction in Sandbox ===
        execution_result = await self._execute_sandboxed_reaction(
            reaction_code, selected_profile, reaction_id,
            {"input_molecules": input_molecules}
        )

        if not execution_result.get("success"):
            overall_status = GuardrailStatus.FAILED
            return self._build_failed_result(
                execution_id, reaction_id, guardrail_checks,
                f"Reaction execution failed: {execution_result.get('error')}",
                start_time, execution_result
            )

        # === GUARDRAIL 5: Molecule Signing (if HSM available) ===
        signed_molecule = None
        if self._hsm_healthy and execution_result.get("output_molecule"):
            sign_result = await self._sign_output_molecule(
                execution_result["output_molecule"]
            )
            if sign_result:
                signed_molecule = sign_result.to_dict()

        # === GUARDRAIL 6: TemporalChain Anchoring ===
        temporal_seal = None
        if self.PIPELINE_CONFIG["temporal_anchor_required"] and self.temporal:
            temporal_seal = await self._anchor_execution_to_chain(
                execution_id, reaction_id, guardrail_checks,
                execution_result, signed_molecule
            )

        # Calcular Φ_C agregado da execução
        phi_c_score = self._compute_aggregate_phi_c(guardrail_checks, execution_result)

        # Determinar status final
        failed_checks = sum(1 for c in guardrail_checks if c.status == GuardrailStatus.FAILED)
        if failed_checks > self.PIPELINE_CONFIG["max_guardrail_failures"]:
            overall_status = GuardrailStatus.FAILED
        elif any(c.status == GuardrailStatus.WARNING for c in guardrail_checks):
            overall_status = GuardrailStatus.WARNING

        # Construir resultado
        duration_ms = (time.time() - start_time) * 1000
        result = PipelineExecutionResult(
            execution_id=execution_id,
            reaction_id=reaction_id,
            guardrail_checks=guardrail_checks,
            overall_status=overall_status,
            output=execution_result,
            signed_molecule=signed_molecule,
            temporal_seal=temporal_seal,
            total_duration_ms=duration_ms,
            phi_c_score=phi_c_score
        )

        # Registrar histórico
        self._execution_history.append(result)

        # Publicar métrica no Phi-Bus
        if self.phi_bus:
            await self.phi_bus.publish_metric("guardrail_pipeline_executed", {
                "execution_id": execution_id,
                "reaction_name": reaction_name,
                "overall_status": overall_status.value,
                "phi_c_score": phi_c_score,
                "duration_ms": duration_ms,
                "guardrails_passed": sum(1 for c in guardrail_checks if c.status in (GuardrailStatus.PASSED, GuardrailStatus.WARNING))
            })

        logger.info(
            f"{'✅' if overall_status == GuardrailStatus.PASSED else '⚠️'} Pipeline concluído: {execution_id} | "
            f"Status: {overall_status.value} | "
            f"Φ_C: {phi_c_score:.3f} | "
            f"Duração: {duration_ms:.1f}ms"
        )

        return result

    async def _check_phi_c_gating(
        self,
        molecules: List[Dict],
        reaction_code: str,
        context: Optional[Dict]
    ) -> GuardrailCheck:
        """Verifica Φ_C mínimo para permitir execução."""
        # Calcular Φ_C médio das moléculas de entrada
        if molecules:
            avg_phi = np.mean([m.get("atoms", [{}])[0].get("phi_c", 0.5) for m in molecules])
        else:
            avg_phi = 0.9  # Default para reações sem moléculas

        # Verificar threshold
        min_phi = self.PIPELINE_CONFIG["min_phi_c_for_execution"]
        if avg_phi >= min_phi:
            return GuardrailCheck(
                guardrail_name="phi_c_gating",
                status=GuardrailStatus.PASSED,
                message=f"Φ_C={avg_phi:.3f} >= threshold={min_phi}",
                confidence=0.95,
                details={"avg_phi_c": avg_phi, "threshold": min_phi}
            )
        else:
            return GuardrailCheck(
                guardrail_name="phi_c_gating",
                status=GuardrailStatus.FAILED,
                message=f"Φ_C={avg_phi:.3f} < threshold={min_phi}",
                confidence=1.0,
                details={"avg_phi_c": avg_phi, "threshold": min_phi}
            )

    def _check_hsm_health(self) -> GuardrailCheck:
        """Verifica saúde do HSM-PQC."""
        if self._hsm_healthy:
            return GuardrailCheck(
                guardrail_name="hsm_health",
                status=GuardrailStatus.PASSED,
                message="HSM-PQC operational",
                confidence=0.99,
                details={"slot": self.molecule_signer.hsm.config.slot_id}
            )
        else:
            return GuardrailCheck(
                guardrail_name="hsm_health",
                status=GuardrailStatus.FAILED,
                message="HSM-PQC unavailable",
                confidence=1.0,
                details={"error": "initialization_failed"}
            )

    async def _validate_reaction_ast(self, reaction_code: str) -> GuardrailCheck:
        """Valida código da reação com AST-ML."""
        is_safe, violations, matched_rule = self.rule_learner.validate_reaction_code(
            reaction_code, context={"reaction_type": "semantic_chemistry"}
        )

        if is_safe:
            confidence = 0.90 if matched_rule else 0.85
            return GuardrailCheck(
                guardrail_name="ast_ml_validation",
                status=GuardrailStatus.PASSED,
                message="Reaction code validated" + (f" via rule '{matched_rule}'" if matched_rule else ""),
                confidence=confidence,
                details={"violations_found": len(violations), "matched_rule": matched_rule}
            )
        else:
            return GuardrailCheck(
                guardrail_name="ast_ml_validation",
                status=GuardrailStatus.FAILED,
                message=f"AST validation failed: {[v.pattern.name for v in violations[:3]]}",
                confidence=0.95,
                details={"violations": [asdict(v) for v in violations]}
            )

    def _select_seccomp_profile(self, reaction_code: str) -> GuardrailCheck:
        """Seleciona perfil de seccomp baseado na complexidade da reação."""
        # Heurística simples: contar operações potencialmente perigosas
        dangerous_ops = sum(1 for op in ["subprocess", "eval", "exec", "__import__"] if op in reaction_code)

        if dangerous_ops == 0:
            profile = ReactionSandboxProfile.CREATIVE_MINIMAL
        elif dangerous_ops <= 2:
            profile = ReactionSandboxProfile.CREATIVE_STANDARD
        else:
            profile = ReactionSandboxProfile.CREATIVE_FULL

        return GuardrailCheck(
            guardrail_name="seccomp_profile_selection",
            status=GuardrailStatus.PASSED,
            message=f"Selected profile: {profile.name}",
            confidence=0.88,
            details={
                "selected_profile": profile,
                "dangerous_ops_detected": dangerous_ops,
                "allowed_syscalls_count": len(self.seccomp_runner.seccomp.get_allowed_syscalls(
                    self.seccomp_runner.PROFILE_CONFIG[profile]["seccomp_profile"]
                )) if self._seccomp_available else 0
            }
        )

    async def _execute_sandboxed_reaction(
        self,
        reaction_code: str,
        profile: ReactionSandboxProfile,
        reaction_id: str,
        input_data: Dict
    ) -> Dict:
        """Executa reação em sandbox seccomp."""
        # run_reaction_sandboxed is synchronous
        return self.seccomp_runner.run_reaction_sandboxed(
            reaction_code=reaction_code,
            profile=profile,
            input_data=input_data,
            reaction_id=reaction_id
        )

    async def _sign_output_molecule(self, molecule_dict: Dict) -> Optional[Any]:
        """Assina molécula de saída com HSM-PQC."""
        # Mock: em produção, reconstruir objeto SemanticMolecule do dict
        # Aqui, simulamos assinatura
        from security.semantic_molecule_signer import SignedSemanticMolecule

        molecule_hash = hashlib.sha3_256(
            json.dumps(molecule_dict, sort_keys=True).encode()
        ).hexdigest()

        return SignedSemanticMolecule(
            molecule_hash=molecule_hash,
            signature_hex="mock_signature_" + hashlib.sha3_256(molecule_hash.encode()).hexdigest()[:32],
            signature_algorithm="CRYSTALS-Dilithium3",
            hsm_slot=self.molecule_signer.hsm.config.slot_id,
            key_label=self.molecule_signer.hsm.config.key_label,
            signed_at=time.time(),
            phi_c_verified=True
        )

    async def _anchor_execution_to_chain(
        self,
        execution_id: str,
        reaction_id: str,
        guardrail_checks: List[GuardrailCheck],
        execution_result: Dict,
        signed_molecule: Optional[Dict]
    ) -> str:
        """Ancora execução completa na TemporalChain."""
        if not self.temporal:
            return None

        return await self.temporal.anchor_event("guardrail_pipeline_anchored", {
            "execution_id": execution_id,
            "reaction_id": reaction_id,
            "guardrail_results": [
                {"name": c.guardrail_name, "status": c.status.value, "confidence": c.confidence}
                for c in guardrail_checks
            ],
            "execution_success": execution_result.get("success"),
            "molecule_signed": signed_molecule is not None,
            "phi_c_score": self._compute_aggregate_phi_c(guardrail_checks, execution_result),
            "timestamp": time.time()
        })

    def _compute_aggregate_phi_c(
        self,
        guardrail_checks: List[GuardrailCheck],
        execution_result: Dict
    ) -> float:
        """Calcula Φ_C agregado da execução."""
        # Média ponderada das confidences dos guardrails
        if guardrail_checks:
            guardrail_phi = np.mean([c.confidence for c in guardrail_checks])
        else:
            guardrail_phi = 0.5

        # Fator de sucesso da execução
        execution_phi = 1.0 if execution_result.get("success") else 0.3

        # Combinar com pesos
        return 0.6 * guardrail_phi + 0.4 * execution_phi

    def _build_failed_result(
        self,
        execution_id: str,
        reaction_id: str,
        guardrail_checks: List[GuardrailCheck],
        failure_reason: str,
        start_time: float,
        partial_output: Optional[Dict] = None
    ) -> PipelineExecutionResult:
        """Constrói resultado de falha do pipeline."""
        duration_ms = (time.time() - start_time) * 1000
        return PipelineExecutionResult(
            execution_id=execution_id,
            reaction_id=reaction_id,
            guardrail_checks=guardrail_checks,
            overall_status=GuardrailStatus.FAILED,
            output=partial_output,
            signed_molecule=None,
            temporal_seal=None,
            total_duration_ms=duration_ms,
            phi_c_score=0.0
        )

    def get_pipeline_statistics(self) -> Dict:
        """Retorna estatísticas de execuções do pipeline."""
        if not self._execution_history:
            return {"total_executions": 0}

        by_status = {}
        for r in self._execution_history:
            by_status[r.overall_status.value] = by_status.get(r.overall_status.value, 0) + 1

        return {
            "total_executions": len(self._execution_history),
            "by_status": by_status,
            "avg_phi_c": np.mean([r.phi_c_score for r in self._execution_history]),
            "avg_duration_ms": np.mean([r.total_duration_ms for r in self._execution_history]),
            "hsm_healthy": self._hsm_healthy,
            "seccomp_available": self._seccomp_available,
            "ml_rules_loaded": len(self.rule_learner._rules)
        }

    async def run_periodic_health_checks(self, interval_sec: int = 60):
        """Executa health checks periódicos dos componentes."""
        while True:
            # HSM
            try:
                self._hsm_healthy = self.molecule_signer.hsm._initialized
            except:
                self._hsm_healthy = False

            # Seccomp
            self._seccomp_available = self.seccomp_runner.seccomp._lib is not None

            # ML Rules
            self._ml_model_loaded = len(self.rule_learner._rules) > 0

            # Publicar métricas de saúde
            if self.phi_bus:
                await self.phi_bus.publish_metric("guardrail_health", {
                    "hsm_healthy": self._hsm_healthy,
                    "seccomp_available": self._seccomp_available,
                    "ml_rules_loaded": self._ml_model_loaded,
                    "timestamp": time.time()
                })

            await asyncio.sleep(interval_sec)
