#!/usr/bin/env python3
"""
audit_protocol.py — Protocolo de auditoria híbrida expandido
Usa funções de hash do Moonlab (SHA3-256, SHAKE128, SHAKE256) para integridade
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

# Mock moonlab for audit protocol
class MoonlabMock:
    @staticmethod
    def sha3_256(data):
        try:
            return hashlib.sha3_256(data).digest()
        except AttributeError:
            return hashlib.sha256(data).digest()

ml = MoonlabMock()

@dataclass
class EngineeringMetrics:
    """Métricas de engenharia quântica (mensuráveis)"""
    s_value: float  # Violação Bell-CHSH ou Mermin-Klyshko
    gate_fidelity: float  # Fidelidade de porta de 2 qubits
    logical_error_rate: float  # Taxa de erro lógico por ciclo
    ghz_fidelity: float  # Fidelidade do estado GHZ7
    coherence_time_ms: float  # Tempo de coerência efetivo

    def normalize_s_value(self) -> float:
        """Normaliza S-value para [0, 1] (clássico=0, quântico máximo=1)"""
        # For n=2: Limite clássico: 2.0, Limite Tsirelson: 2.828
        # For demo, we assume 2.828 is max
        return (self.s_value - 2.0) / (2 * 2**0.5 - 2.0)

    def compute_physical_score(self) -> float:
        """Calcula score físico composto [0, 1]"""
        s_norm = max(0.0, min(1.0, self.normalize_s_value()))
        return s_norm * self.gate_fidelity * (1 - self.logical_error_rate) * self.ghz_fidelity

@dataclass
class QuartzTestimony:
    """Testemunhos de quartzo (qualitativos)"""
    narrative_coherence: float  # [0, 1]
    semantic_resonance: float   # [0, 1]
    observer_stability: float   # [0, 1]
    value_alignment: float      # [0, 1]

    def compute_quartz_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de quartzo com pesos configuráveis"""
        if weights is None:
            weights = {
                'narrative_coherence': 0.3,
                'semantic_resonance': 0.3,
                'observer_stability': 0.2,
                'value_alignment': 0.2
            }
        return sum(
            weights[key] * getattr(self, key)
            for key in weights
        )

@dataclass
class HybridAuditResult:
    """Resultado da auditoria híbrida"""
    engineering_metrics: EngineeringMetrics
    quartz_testimony: QuartzTestimony
    physical_score: float
    quartz_score: float
    fusion_score: float
    classification: str  # "VALID", "WARNING", "CRITICAL"
    audit_hash: str  # SHA3-256 do registro de auditoria

    def to_dict(self) -> Dict:
        """Converte para dicionário para serialização"""
        return {
            'engineering': asdict(self.engineering_metrics),
            'quartz': asdict(self.quartz_testimony),
            'scores': {
                'physical': self.physical_score,
                'quartz': self.quartz_score,
                'fusion': self.fusion_score
            },
            'classification': self.classification,
            'audit_hash': self.audit_hash
        }

class HybridAuditor:
    """Motor de auditoria híbrida com integridade via SHA3"""

    def __init__(self, threshold_valid: float = 0.85, threshold_warning: float = 0.60):
        self.threshold_valid = threshold_valid
        self.threshold_warning = threshold_warning
        self.audit_log: List[HybridAuditResult] = []

    def compute_fusion_score(self, physical_score: float, quartz_score: float) -> float:
        """Calcula score de fusão via média geométrica (penaliza assimetrias)"""
        return (physical_score * quartz_score) ** 0.5

    def classify_result(self, fusion_score: float) -> str:
        """Classifica resultado com base no score de fusão"""
        if fusion_score >= self.threshold_valid:
            return "VALID"
        elif fusion_score >= self.threshold_warning:
            return "WARNING"
        else:
            return "CRITICAL"

    def generate_audit_hash(self, result: HybridAuditResult) -> str:
        """Gera hash de auditoria usando SHA3-256 do Moonlab"""
        # Serializar resultado (excluindo o próprio hash)
        data = result.to_dict()
        data.pop('audit_hash', None)
        json_data = json.dumps(data, sort_keys=True).encode()

        # Calcular SHA3-256
        return ml.sha3_256(json_data).hex()

    def verify_audit_integrity(self, result: HybridAuditResult) -> bool:
        """Verifica integridade de um resultado de auditoria"""
        expected_hash = result.audit_hash
        computed_hash = self.generate_audit_hash(result)
        return expected_hash == computed_hash

    def execute_audit(
        self,
        engineering: EngineeringMetrics,
        quartz: QuartzTestimony,
        operation_id: str
    ) -> HybridAuditResult:
        """Executa auditoria híbrida completa"""
        # Calcular scores
        physical_score = engineering.compute_physical_score()
        quartz_score = quartz.compute_quartz_score()
        fusion_score = self.compute_fusion_score(physical_score, quartz_score)
        classification = self.classify_result(fusion_score)

        # Criar resultado preliminar
        result = HybridAuditResult(
            engineering_metrics=engineering,
            quartz_testimony=quartz,
            physical_score=physical_score,
            quartz_score=quartz_score,
            fusion_score=fusion_score,
            classification=classification,
            audit_hash=""  # Será preenchido abaixo
        )

        # Gerar hash de auditoria
        result.audit_hash = self.generate_audit_hash(result)

        # Registrar no log
        self.audit_log.append(result)

        return result

    def generate_audit_report(self, output_format: str = "ascii") -> str:
        """Gera relatório de auditoria em formato ASCII ou JSON"""
        if output_format == "json":
            return json.dumps([r.to_dict() for r in self.audit_log], indent=2)

        # Formato ASCII
        lines = [
            "╔════════════════════════════════════════════════════╗",
            "║         RELATÓRIO DE AUDITORIA HÍBRIDA            ║",
            "╠════════════════════════════════════════════════════╣"
        ]

        for i, result in enumerate(self.audit_log, 1):
            status_icon = "✓" if result.classification == "VALID" else "⚠" if result.classification == "WARNING" else "✗"
            lines.append(f"║ [{i}] {status_icon} {result.classification:8} | Fusão: {result.fusion_score:.3f} │")
            lines.append(f"║     Físico: {result.physical_score:.3f} | Quartzo: {result.quartz_score:.3f} │")
            lines.append(f"║     Hash: {result.audit_hash[:32]}... │")
            lines.append("║" + "─" * 48 + "║")

        lines.append("╚════════════════════════════════════════════════════╝")
        return "\n".join(lines)

# Exemplo de uso
def demo_audit_protocol():
    """Demonstra o protocolo de auditoria híbrida"""
    auditor = HybridAuditor()

    # Simular métricas de engenharia
    engineering = EngineeringMetrics(
        s_value=2.81,  # Próximo do limite Tsirelson
        gate_fidelity=0.999,
        logical_error_rate=1e-11,
        ghz_fidelity=0.96,
        coherence_time_ms=15000
    )

    # Simular testemunhos de quartzo
    quartz = QuartzTestimony(
        narrative_coherence=0.94,
        semantic_resonance=0.91,
        observer_stability=0.97,
        value_alignment=0.92
    )

    # Executar auditoria
    result = auditor.execute_audit(engineering, quartz, "VQC_JUDGMENT_001")

    # Exibir resultado
    print(auditor.generate_audit_report())

    # Verificar integridade
    if auditor.verify_audit_integrity(result):
        print("\n[✓] Integridade da auditoria verificada (SHA3-256)")
    else:
        print("\n[✗] Falha na verificação de integridade!")

    return result

if __name__ == "__main__":
    import sys
    demo_audit_protocol()
    sys.exit(0)
