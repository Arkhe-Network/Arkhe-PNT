#!/usr/bin/env python3
"""
ARKHE OS Substrato 241: Semantic Chemistry Engine
Canon: ∞.Ω.∇+++.241.semantic_chemistry
"""

import random
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

@dataclass
class SemanticAtom:
    """Um átomo semântico — a menor unidade de significado."""
    concept: str
    charge: float = 0.0  # polaridade semântica (-1 a +1)
    phi_c: float = 0.9

@dataclass
class SemanticBond:
    """Ligação entre átomos em uma molécula."""
    atom_a: int
    atom_b: int
    relation: str
    strength: float = 1.0

@dataclass
class SemanticMolecule:
    """Molécula — uma combinação de átomos ligados semanticamente."""
    atoms: List[SemanticAtom]
    bonds: List[SemanticBond]
    stability: float = 0.5
    creation_timestamp: float = field(default_factory=time.time)

    def canonical_hash(self) -> str:
        h = hashlib.sha3_256()
        for a in sorted(self.atoms, key=lambda x: x.concept):
            h.update(a.concept.encode())
        for b in self.bonds:
            h.update(f"{b.atom_a}{b.relation}{b.atom_b}".encode())
        return h.hexdigest()

class SemanticChemistryEngine:
    """
    Reator de Semantic Chemistry.
    Mantém um "caldo" de moléculas e aplica regras de reação para gerar novas.
    """

    def __init__(self, temporal_chain=None, phi_bus=None):
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self.molecules: List[SemanticMolecule] = []
        self.reaction_rules = [
            self._reaction_combination,
            self._reaction_decomposition,
            self._reaction_substitution,
            self._reaction_catalysis,
        ]

    def add_molecule(self, molecule: SemanticMolecule):
        self.molecules.append(molecule)

    def react(self, steps: int = 1) -> List[SemanticMolecule]:
        """Executa reações químicas entre moléculas por um número de passos."""
        new_molecules = []
        for _ in range(steps):
            if len(self.molecules) < 2:
                break
            m1, m2 = random.sample(self.molecules, 2)
            rule = random.choice(self.reaction_rules)
            products = rule(m1, m2)
            for p in products:
                # Validação: molécula resultante deve ter estabilidade mínima
                p.stability = self._compute_stability(p)
                if p.stability > 0.3:
                    new_molecules.append(p)
                    self.molecules.append(p)
                    # Ancorar na TemporalChain
                    if self.temporal:
                        self.temporal.anchor_event("semantic_reaction", {
                            "reactants": [m1.canonical_hash()[:8], m2.canonical_hash()[:8]],
                            "product": p.canonical_hash()[:8],
                            "rule": rule.__name__,
                            "stability": p.stability
                        })
        return new_molecules

    def _reaction_combination(self, m1: SemanticMolecule, m2: SemanticMolecule) -> List[SemanticMolecule]:
        """Combina duas moléculas em uma maior (síntese)."""
        new_atoms = m1.atoms + m2.atoms
        # Criar uma nova ligação entre átomos aleatórios
        if new_atoms:
            a = random.randint(0, len(m1.atoms)-1) if m1.atoms else 0
            b = random.randint(0, len(m2.atoms)-1) + len(m1.atoms) if m2.atoms else 0
            new_bond = SemanticBond(a, b, "synthesized", strength=random.uniform(0.3, 1.0))
            return [SemanticMolecule(atoms=new_atoms, bonds=m1.bonds + m2.bonds + [new_bond])]
        return []

    def _reaction_decomposition(self, m1: SemanticMolecule, m2: SemanticMolecule) -> List[SemanticMolecule]:
        """Quebra uma molécula em duas menores (análise)."""
        # Usa m2 como catalisador para quebrar m1
        if len(m1.atoms) >= 3:
            split = len(m1.atoms) // 2
            left = SemanticMolecule(atoms=m1.atoms[:split], bonds=[])
            right = SemanticMolecule(atoms=m1.atoms[split:], bonds=[])
            return [left, right]
        return []

    def _reaction_substitution(self, m1: SemanticMolecule, m2: SemanticMolecule) -> List[SemanticMolecule]:
        """Substitui um átomo de m1 por um átomo de m2."""
        if m1.atoms and m2.atoms:
            idx = random.randint(0, len(m1.atoms)-1)
            new_atom = random.choice(m2.atoms)
            new_atoms = m1.atoms.copy()
            new_atoms[idx] = SemanticAtom(concept=f"{new_atoms[idx].concept}-{new_atom.concept}")
            return [SemanticMolecule(atoms=new_atoms, bonds=m1.bonds)]
        return []

    def _reaction_catalysis(self, m1: SemanticMolecule, m2: SemanticMolecule) -> List[SemanticMolecule]:
        """Catalisador (Φ_C) acelera a estabilidade sem consumir-se."""
        # Apenas retorna m1 com estabilidade aumentada
        m1.stability = min(1.0, m1.stability + 0.2)
        return [m1, m2]  # m2 (catalisador) permanece inalterado

    def _compute_stability(self, molecule: SemanticMolecule) -> float:
        """Calcula estabilidade baseada na coerência Φ_C dos átomos."""
        if not molecule.atoms:
            return 0.0
        avg_phi = sum(a.phi_c for a in molecule.atoms) / len(molecule.atoms)
        bond_strength = sum(b.strength for b in molecule.bonds) / max(1, len(molecule.bonds))
        return (avg_phi * 0.6 + bond_strength * 0.4)
