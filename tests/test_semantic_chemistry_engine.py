import pytest
from substrates.semantic_chemistry_engine import (
    SemanticChemistryEngine,
    SemanticAtom,
    SemanticBond,
    SemanticMolecule
)

def test_semantic_chemistry_engine_init():
    engine = SemanticChemistryEngine()
    assert engine.molecules == []
    assert len(engine.reaction_rules) == 4

def test_semantic_chemistry_engine_add_molecule():
    engine = SemanticChemistryEngine()
    atom1 = SemanticAtom(concept="test")
    molecule = SemanticMolecule(atoms=[atom1], bonds=[])

    engine.add_molecule(molecule)
    assert len(engine.molecules) == 1
    assert engine.molecules[0] == molecule

def test_semantic_chemistry_engine_react():
    engine = SemanticChemistryEngine()
    atom1 = SemanticAtom(concept="test1", charge=0.5, phi_c=0.9)
    atom2 = SemanticAtom(concept="test2", charge=-0.5, phi_c=0.8)
    atom3 = SemanticAtom(concept="test3", charge=0.0, phi_c=0.7)

    bond1 = SemanticBond(atom_a=0, atom_b=1, relation="test_relation", strength=0.8)

    molecule1 = SemanticMolecule(atoms=[atom1, atom2], bonds=[bond1])
    molecule2 = SemanticMolecule(atoms=[atom3], bonds=[])

    engine.add_molecule(molecule1)
    engine.add_molecule(molecule2)

    assert len(engine.molecules) == 2

    new_molecules = engine.react(steps=10)

    assert isinstance(new_molecules, list)
    assert len(engine.molecules) >= 2 # could generate new ones or not depending on randomness
