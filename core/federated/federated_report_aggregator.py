# federated_report_aggregator.py — Agregação de relatórios com consenso BFT
import hashlib
import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict, field
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.backends import default_backend
import numpy as np

@dataclass
class FieldReport:
    """Relatório de campo de um único nó."""
    report_id: str
    node_id: str
    timestamp: float
    metrics: Dict[str, float]  # {metric_name: value}
    raw_data_hash: str  # SHA256 dos dados brutos
    signature: str  # ECDSA signature do nó
    public_key_pem: str

    def verify_signature(self) -> bool:
        """Verifica assinatura do relatório."""
        try:
            public_key = serialization.load_pem_public_key(
                self.public_key_pem.encode(), backend=default_backend()
            )
            message = json.dumps({
                'report_id': self.report_id,
                'node_id': self.node_id,
                'timestamp': self.timestamp,
                'metrics': self.metrics,
                'raw_data_hash': self.raw_data_hash
            }, sort_keys=True).encode()

            signature = bytes.fromhex(self.signature)
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except:
            return False

@dataclass
class FederatedMetaReport:
    """Meta-relatório agregado de múltiplos nós."""
    meta_report_id: str
    timestamp: float
    contributing_reports: List[str]  # IDs dos relatórios incluídos
    aggregated_metrics: Dict[str, Dict]  # {metric: {mean, std, min, max, n}}
    consensus_signatures: Dict[str, str]  # {validator_id: signature}
    byzantine_threshold: int  # N tolerável de nós maliciosos
    status: str  # "finalized", "pending", "rejected"

class FederatedReportAggregator:
    """Agrega relatórios de campo via consenso BFT simplificado."""

    def __init__(
        self,
        validator_keys: Dict[str, str],  # {validator_id: public_key_pem}
        byzantine_tolerance: float = 0.33,  # fração máxima de nós bizantinos
        min_reports_for_consensus: int = 3,
        aggregation_window_seconds: int = 300  # 5 minutos
    ):
        self.validator_keys = validator_keys
        self.byzantine_tolerance = byzantine_tolerance
        self.min_reports = min_reports_for_consensus
        self.window_seconds = aggregation_window_seconds

        self.pending_reports: Dict[str, FieldReport] = {}
        self.finalized_reports: Dict[str, FederatedMetaReport] = {}
        self.validator_private_key: Optional[ec.EllipticCurvePrivateKey] = None

    def set_validator_key(self, private_key_pem: str):
        """Configura chave privada para assinar como validador."""
        self.validator_private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )

    def submit_report(self, report: FieldReport) -> bool:
        """Submete relatório para agregação."""
        # Verificar assinatura do relatório
        if not report.verify_signature():
            print(f"❌ Invalid signature for report {report.report_id}")
            return False

        # Verificar timestamp dentro da janela
        if time.time() - report.timestamp > self.window_seconds * 2:
            print(f"⏰ Report {report.report_id} too old")
            return False

        self.pending_reports[report.report_id] = report
        print(f"✅ Report {report.report_id} from {report.node_id} accepted")
        return True

    def try_finalize_meta_report(self) -> Optional[FederatedMetaReport]:
        """Tenta agregar relatórios pendentes em meta-relatório via consenso."""
        # Filtrar relatórios dentro da janela temporal
        now = time.time()
        valid_reports = [
            r for r in self.pending_reports.values()
            if now - r.timestamp <= self.window_seconds
        ]

        if len(valid_reports) < self.min_reports:
            return None

        # Verificar consenso: pelo menos (1 - byzantine_tolerance) * N válidos
        n_valid = sum(1 for r in valid_reports if r.verify_signature())
        n_total = len(valid_reports)

        if n_valid < (1 - self.byzantine_tolerance) * n_total:
            print(f"⚠️ Insufficient valid reports: {n_valid}/{n_total}")
            return None

        # Agregar métricas
        aggregated = self._aggregate_metrics(valid_reports)

        # Criar meta-relatório
        meta_report = FederatedMetaReport(
            meta_report_id=hashlib.sha256(
                f"meta_{now}_{n_valid}".encode()
            ).hexdigest()[:16],
            timestamp=now,
            contributing_reports=[r.report_id for r in valid_reports],
            aggregated_metrics=aggregated,
            consensus_signatures={},
            byzantine_threshold=int(self.byzantine_tolerance * n_total),
            status="pending"
        )

        # Assinar como validador local
        if self.validator_private_key:
            signature = self._sign_meta_report(meta_report)
            meta_report.consensus_signatures["local_validator"] = signature

        # (Em produção: coletar assinaturas de outros validadores via P2P)
        # Aqui: simular consenso com assinaturas simuladas
        meta_report.status = "finalized"

        # Registrar e limpar pendentes
        self.finalized_reports[meta_report.meta_report_id] = meta_report
        for r in valid_reports:
            self.pending_reports.pop(r.report_id, None)

        print(f"🎯 Meta-report {meta_report.meta_report_id} finalized with {n_valid}/{n_total} valid reports")
        return meta_report

    def _aggregate_metrics(self, reports: List[FieldReport]) -> Dict[str, Dict]:
        """Agrega métricas de múltiplos relatórios com estatísticas robustas."""
        aggregated = {}

        # Coletar valores por métrica
        metric_values: Dict[str, List[float]] = {}
        for report in reports:
            for metric, value in report.metrics.items():
                if metric not in metric_values:
                    metric_values[metric] = []
                metric_values[metric].append(value)

        # Calcular estatísticas robustas (mediana, MAD para outliers)
        for metric, values in metric_values.items():
            if not values:
                continue

            arr = np.array(values)
            mean_val = float(np.mean(arr))
            dp_mean_val = add_differential_privacy_noise(mean_val)
            aggregated[metric] = {
                'mean': dp_mean_val,
                'median': float(np.median(arr)),
                'std': float(np.std(arr)),
                'mad': float(np.median(np.abs(arr - np.median(arr)))),  # Median Absolute Deviation
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'n': len(arr),
                'outliers_removed': int(np.sum(np.abs(arr - np.median(arr)) > 3 * np.median(np.abs(arr - np.median(arr)))))
            }

        return aggregated

    def _sign_meta_report(self, meta_report: FederatedMetaReport) -> str:
        """Assina meta-relatório com chave do validador."""
        if not self.validator_private_key:
            raise ValueError("Validator private key not set")

        message = json.dumps({
            'meta_report_id': meta_report.meta_report_id,
            'timestamp': meta_report.timestamp,
            'contributing_reports': meta_report.contributing_reports,
            'aggregated_metrics': meta_report.aggregated_metrics
        }, sort_keys=True).encode()

        signature = self.validator_private_key.sign(message, ec.ECDSA(hashes.SHA256()))
        return signature.hex()

    def verify_meta_report(self, meta_report: FederatedMetaReport) -> bool:
        """Verifica integridade e consenso de meta-relatório."""
        # Verificar número mínimo de assinaturas
        n_validators = len(self.validator_keys)
        min_signatures = int((1 - self.byzantine_tolerance) * n_validators) + 1

        if len(meta_report.consensus_signatures) < min_signatures:
            print(f"❌ Insufficient signatures: {len(meta_report.consensus_signatures)} < {min_signatures}")
            return False

        # Verificar assinaturas dos validadores
        message = json.dumps({
            'meta_report_id': meta_report.meta_report_id,
            'timestamp': meta_report.timestamp,
            'contributing_reports': meta_report.contributing_reports,
            'aggregated_metrics': meta_report.aggregated_metrics
        }, sort_keys=True).encode()

        for validator_id, signature_hex in meta_report.consensus_signatures.items():
            if validator_id not in self.validator_keys:
                print(f"⚠️ Unknown validator: {validator_id}")
                continue

            try:
                public_key = serialization.load_pem_public_key(
                    self.validator_keys[validator_id].encode(), backend=default_backend()
                )
                signature = bytes.fromhex(signature_hex)
                public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            except Exception as e:
                print(f"❌ Invalid signature from {validator_id}: {e}")
                return False

        return True

    def export_meta_report(self, meta_report: FederatedMetaReport, path: str):
        """Exporta meta-relatório para arquivo JSON."""
        export_data = {
            'meta_report': asdict(meta_report),
            'verification': {
                'signature_count': len(meta_report.consensus_signatures),
                'byzantine_threshold': meta_report.byzantine_threshold,
                'verified': self.verify_meta_report(meta_report)
            },
            'export_timestamp': time.time()
        }

        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"📄 Meta-report exported to {path}")

def add_differential_privacy_noise(value: float, epsilon: float = 1.0, sensitivity: float = 1.0) -> float:
    """Adds Laplacian noise for differential privacy."""
    import numpy as np
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return float(value + noise)
