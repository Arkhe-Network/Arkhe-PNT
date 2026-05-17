#!/usr/bin/env python3
"""
ARKHE OS Substrato 241+∞: Semantic Molecule PQC Signer
Canon: ∞.Ω.∇+++.241.security.molecule_signer
Função: Assinar moléculas semânticas com Dilithium3 via HSM para
integridade, não-repúdio e verificação de proveniência criativa.
"""

import hashlib
import json
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path

# Import from hardened Unbuildable substrate
from security.hsm_pqc_signer import HSM_PQC_Signer, HSMConfig

logger = logging.getLogger(__name__)

@dataclass
class SignedSemanticMolecule:
    """Molécula semântica com assinatura PQC e metadados de segurança."""
    molecule_hash: str
    signature_hex: str
    signature_algorithm: str
    hsm_slot: int
    key_label: str
    signed_at: float
    phi_c_verified: bool
    temporal_seal: Optional[str] = None
    parent_signatures: List[str] = None  # Para moléculas derivadas

    def to_dict(self) -> Dict:
        return asdict(self)

class SemanticMoleculeSigner:
    """
    Assinador de moléculas semânticas com HSM-PQC.

    Características:
    • Assinatura Dilithium3 do hash canônico da molécula
    • Verificação de Φ_C mínimo antes de assinar
    • Rastreamento de linhagem para moléculas derivadas
    • Ancoragem na TemporalChain para auditoria criativa
    • Suporte a assinatura em lote para reações poliméricas
    """

    MIN_PHI_C_FOR_SIGNING = 0.75  # Threshold mínimo de coerência

    def __init__(
        self,
        hsm_config: HSMConfig,
        temporal_chain=None,
        phi_bus=None
    ):
        self.hsm = HSM_PQC_Signer(hsm_config)
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self._signature_log: List[Dict] = []

    def initialize(self) -> bool:
        """Inicializa conexão com HSM."""
        return self.hsm.initialize()

    def sign_molecule(
        self,
        molecule: 'SemanticMolecule',  # Forward reference
        verify_phi_c: bool = True
    ) -> Optional[SignedSemanticMolecule]:
        """
        Assina molécula semântica com Dilithium3 via HSM.

        Args:
            molecule: Instância de SemanticMolecule a ser assinada
            verify_phi_c: Se True, verifica Φ_C mínimo antes de assinar

        Returns:
            SignedSemanticMolecule com assinatura e metadados, ou None se falhar
        """
        # Verificar Φ_C se solicitado
        if verify_phi_c:
            avg_phi = sum(a.phi_c for a in molecule.atoms) / max(1, len(molecule.atoms))
            if avg_phi < self.MIN_PHI_C_FOR_SIGNING:
                logger.warning(
                    f"⚠️  Molécula rejeitada para assinatura: Φ_C={avg_phi:.3f} < {self.MIN_PHI_C_FOR_SIGNING}"
                )
                return None

        # Calcular hash canônico da molécula
        molecule_hash = molecule.canonical_hash()

        # Assinar com HSM-PQC
        sign_result = self.hsm.sign_transformation(
            json.dumps(molecule.to_dict(), sort_keys=True)
        )

        if sign_result["status"] != "success":
            logger.error(f"❌ Falha na assinatura: {sign_result.get('reason')}")
            return None

        # Criar registro assinado
        signed = SignedSemanticMolecule(
            molecule_hash=molecule_hash,
            signature_hex=sign_result["signature"],
            signature_algorithm=sign_result["algorithm"],
            hsm_slot=self.hsm.config.slot_id,
            key_label=self.hsm.config.key_label,
            signed_at=time.time(),
            phi_c_verified=verify_phi_c,
            parent_signatures=[a.get("signature") for a in molecule.parent_hashes]
                if hasattr(molecule, 'parent_hashes') else None
        )

        # Ancorar na TemporalChain
        if self.temporal:
            seal = self.temporal.anchor_event("semantic_molecule_signed", {
                "molecule_hash": molecule_hash[:16],
                "signature_algorithm": sign_result["algorithm"],
                "phi_c_verified": verify_phi_c,
                "generation": molecule.generation,
                "timestamp": time.time()
            })
            signed.temporal_seal = seal

        # Log para auditoria
        self._signature_log.append({
            "molecule_hash": molecule_hash,
            "signed_at": signed.signed_at,
            "phi_c": sum(a.phi_c for a in molecule.atoms) / max(1, len(molecule.atoms)),
            "temporal_seal": signed.temporal_seal
        })

        logger.info(
            f"✅ Molécula assinada: {molecule_hash[:16]}... | "
            f"Φ_C={'verificado' if verify_phi_c else 'pulado'} | "
            f"Algoritmo: {sign_result['algorithm']}"
        )

        return signed

    def verify_molecule_signature(
        self,
        molecule_dict: Dict,
        signature_hex: str
    ) -> bool:
        """Verifica assinatura PQC de molécula."""
        return self.hsm.verify_signature(
            json.dumps(molecule_dict, sort_keys=True),
            signature_hex
        )

    def get_signing_statistics(self) -> Dict:
        """Retorna estatísticas de assinaturas."""
        if not self._signature_log:
            return {"total_signed": 0}

        return {
            "total_signed": len(self._signature_log),
            "avg_phi_c": sum(log["phi_c"] for log in self._signature_log) / len(self._signature_log),
            "last_signed": self._signature_log[-1]["signed_at"] if self._signature_log else None,
            "hsm_slot": self.hsm.config.slot_id,
            "key_label": self.hsm.config.key_label
        }

    def close(self):
        """Fecha conexão com HSM."""
        self.hsm.close()

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
