# dynamic_consent_protocol.py — Gestão de consentimento granular

import json
import time
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

class PrivacyProfile(Enum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    OPEN = "OPEN"

class DataCategory(Enum):
    IDENTIFIERS = "identificadores"
    CONTACT = "contato"
    FINANCIAL = "financeiros"
    LOCATION = "localizacao"
    HEALTH = "saude"
    BEHAVIORAL = "comportamental"
    BIOMETRIC = "biometrico"
    JUDICIAL = "judicial"
    POLITICAL = "opiniao_politica"

class Purpose(Enum):
    SERVICE_PROVISION = "prestacao_servico"
    SECURITY = "seguranca"
    PRODUCT_IMPROVEMENT = "melhoria_produto"
    MARKETING = "marketing"
    RESEARCH = "pesquisa"
    LEGAL_OBLIGATION = "obrigacao_legal"
    THIRD_PARTY_ANALYTICS = "terceiro_analise"
    AI_TRAINING = "ia_treinamento"

@dataclass
class CitizenConsent:
    citizen_id: str
    profile: PrivacyProfile = PrivacyProfile.BALANCED
    # Matrix: matrix[category][purpose] = bool
    matrix: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.matrix:
            self.apply_profile_defaults(self.profile)

    def apply_profile_defaults(self, profile: PrivacyProfile):
        self.profile = profile
        self.matrix = {}

        essential_purposes = {Purpose.SERVICE_PROVISION.value, Purpose.SECURITY.value, Purpose.LEGAL_OBLIGATION.value}

        for cat in DataCategory:
            self.matrix[cat.value] = {}
            for pur in Purpose:
                if profile == PrivacyProfile.OPEN:
                    self.matrix[cat.value][pur.value] = True
                elif profile == PrivacyProfile.CONSERVATIVE:
                    self.matrix[cat.value][pur.value] = pur.value in essential_purposes
                else: # BALANCED
                    if pur.value in essential_purposes:
                        self.matrix[cat.value][pur.value] = True
                    elif pur in {Purpose.PRODUCT_IMPROVEMENT, Purpose.RESEARCH}:
                        self.matrix[cat.value][pur.value] = cat not in {DataCategory.BIOMETRIC, DataCategory.HEALTH, DataCategory.FINANCIAL}
                    else:
                        self.matrix[cat.value][pur.value] = False
        self.updated_at = time.time()

class ConsentManager:
    """
    Gerencia o consentimento granular (Matriz Categoria x Finalidade).
    """
    def __init__(self):
        self._citizen_consents: Dict[str, CitizenConsent] = {}

    def get_consent(self, citizen_id: str) -> CitizenConsent:
        if citizen_id not in self._citizen_consents:
            self._citizen_consents[citizen_id] = CitizenConsent(citizen_id=citizen_id)
        return self._citizen_consents[citizen_id]

    def update_entry(self, citizen_id: str, category: DataCategory, purpose: Purpose, allowed: bool):
        consent = self.get_consent(citizen_id)
        consent.matrix.setdefault(category.value, {})[purpose.value] = allowed
        consent.updated_at = time.time()

    def update_profile(self, citizen_id: str, profile: PrivacyProfile):
        consent = self.get_consent(citizen_id)
        consent.apply_profile_defaults(profile)

    def is_allowed(self, citizen_id: str, category: DataCategory, purpose: Purpose) -> bool:
        consent = self.get_consent(citizen_id)
        return consent.matrix.get(category.value, {}).get(purpose.value, False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            cid: {
                "profile": c.profile.value,
                "matrix": c.matrix,
                "updated_at": c.updated_at
            } for cid, c in self._citizen_consents.items()
        }
