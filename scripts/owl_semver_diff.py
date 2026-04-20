#!/usr/bin/env python3
"""
owl_semver_diff.py
Compara duas ontologias OWL e determina o impacto SemVer da mudança.
Uso: python owl_semver_diff.py ontology_v1.owl ontology_v2.owl
"""

import sys
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from typing import Set, Tuple, Literal
import json

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

class OWLSemVerDiff:
    def __init__(self, old_path: str, new_path: str):
        self.old_g = Graph()
        self.new_g = Graph()
        self.old_g.parse(old_path, format="xml")
        self.new_g.parse(new_path, format="xml")

    def _get_axioms(self, g: Graph) -> Set[Tuple]:
        """Extrai axiomas relevantes como tuplas hashable."""
        axioms = set()

        # Classes
        for s in g.subjects(RDF.type, OWL.Class):
            axioms.add(("ClassDeclaration", str(s)))

        # Subclasses
        for s, o in g.subject_objects(RDFS.subClassOf):
            axioms.add(("SubClassOf", str(s), str(o)))

        # DisjointClasses
        for s, o in g.subject_objects(OWL.disjointWith):
            axioms.add(("DisjointWith", str(s), str(o)))

        # Properties
        for s in g.subjects(RDF.type, OWL.ObjectProperty):
            axioms.add(("ObjectProperty", str(s)))

        # Domain/Range
        for s, o in g.subject_objects(RDFS.domain):
            axioms.add(("Domain", str(s), str(o)))
        for s, o in g.subject_objects(RDFS.range):
            axioms.add(("Range", str(s), str(o)))

        # Inverse properties
        for s, o in g.subject_objects(OWL.inverseOf):
            axioms.add(("InverseOf", str(s), str(o)))

        return axioms

    def classify_change(self) -> Tuple[Literal["MAJOR", "MINOR", "PATCH"], dict]:
        old_axioms = self._get_axioms(self.old_g)
        new_axioms = self._get_axioms(self.new_g)

        removed = old_axioms - new_axioms
        added = new_axioms - old_axioms

        report = {
            "removed_axioms": [list(r) for r in removed],
            "added_axioms": [list(a) for a in added],
            "breaking_changes": [],
            "safe_changes": []
        }

        # Regras de classificação
        is_major = False

        for ax in removed:
            if ax[0] in ("ClassDeclaration", "ObjectProperty"):
                is_major = True
                report["breaking_changes"].append({
                    "type": "ENTITY_REMOVAL",
                    "axiom": ax,
                    "reason": "Remoção de classe ou propriedade quebra queries existentes"
                })
            elif ax[0] == "SubClassOf":
                is_major = True
                report["breaking_changes"].append({
                    "type": "HIERARCHY_CHANGE",
                    "axiom": ax,
                    "reason": "Alteração na hierarquia de classes afeta inferência"
                })
            elif ax[0] == "DisjointWith":
                is_major = True
                report["breaking_changes"].append({
                    "type": "DISJOINTNESS_ADDED",
                    "axiom": ax,
                    "reason": "Adição de disjunção pode invalidar instâncias existentes"
                })

        for ax in added:
            if ax[0] == "DisjointWith":
                is_major = True
                report["breaking_changes"].append({
                    "type": "DISJOINTNESS_ADDED",
                    "axiom": ax,
                    "reason": "Nova disjunção entre classes existentes"
                })

        # Se não é major, verifica se há adições (minor) ou só refactor (patch)
        if is_major:
            return "MAJOR", report
        elif added:
            return "MINOR", report
        else:
            return "PATCH", report

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python owl_semver_diff.py old.owl new.owl")
        sys.exit(1)

    diff = OWLSemVerDiff(sys.argv[1], sys.argv[2])
    semver, report = diff.classify_change()

    print(f"SEMVER IMPACT: {semver}")
    print(json.dumps(report, indent=2))

    if semver == "MAJOR":
        sys.exit(2)  # Código de erro para CI/CD
    elif semver == "MINOR":
        sys.exit(1)  # Warning
    else:
        sys.exit(0)
