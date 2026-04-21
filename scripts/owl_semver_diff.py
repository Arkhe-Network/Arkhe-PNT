#!/usr/bin/env python3
"""
owl_semver_diff.py v4.0
SemVer + Segurança + Arquitetura + Performance
"""
import sys
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from typing import Set, Tuple, Literal
import json

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
ARKHE = Namespace("http://arkhe.ai/ontology/2026#")

SECURITY_ENTITIES = {
    str(ARKHE.SussurroDeSubversao), str(ARKHE.RachaduraNaMuralha),
    str(ARKHE.RunaProibida), str(ARKHE.GuardiaoDoPortao),
    str(ARKHE.BibliotecaArcana), str(ARKHE.exploraRachadura),
    str(ARKHE.contemRunaProibida), str(ARKHE.usaBibliotecaArcana),
    str(ARKHE.usaChaveMestra),
}

ARCHITECTURAL_ENTITIES = {
    str(ARKHE.Transformer), str(ARKHE.AttentionHead),
    str(ARKHE.FeedForwardNetwork), str(ARKHE.LayerNormalization),
    str(ARKHE.ResidualConnection), str(ARKHE.PositionalEncoding),
    str(ARKHE.approximates), str(ARKHE.hasCliffordEquivalent),
    str(ARKHE.requiresJustification),
}

PERFORMANCE_ENTITIES = {
    str(ARKHE.hasParameterRatio), str(ARKHE.hasMemoryRatio),
    str(ARKHE.hasConvergenceLoss),
}

class OWLSemVerDiff:
    def __init__(self, old_path: str, new_path: str):
        self.old_g = Graph()
        self.new_g = Graph()

        def parse_graph(g, path):
            try:
                g.parse(path, format="turtle")
            except:
                try:
                    g.parse(path, format="xml")
                except Exception as e:
                    print(f"Error parsing {path}: {e}")

        parse_graph(self.old_g, old_path)
        parse_graph(self.new_g, new_path)

    def _get_axioms(self, g: Graph) -> Set[Tuple]:
        axioms = set()
        for s in g.subjects(RDF.type, OWL.Class):
            axioms.add(("ClassDeclaration", str(s)))
        for s, o in g.subject_objects(RDFS.subClassOf):
            axioms.add(("SubClassOf", str(s), str(o)))
        for s, o in g.subject_objects(OWL.disjointWith):
            axioms.add(("DisjointWith", str(s), str(o)))
        for s in g.subjects(RDF.type, OWL.ObjectProperty):
            axioms.add(("ObjectProperty", str(s)))
        for s, o in g.subject_objects(RDFS.domain):
            axioms.add(("Domain", str(s), str(o)))
        for s, o in g.subject_objects(RDFS.range):
            axioms.add(("Range", str(s), str(o)))
        for s, o in g.subject_objects(OWL.inverseOf):
            axioms.add(("InverseOf", str(s), str(o)))

        for s in g.subjects(RDF.type, ARKHE.Transformer):
            axioms.add(("Instance", "Transformer", str(s)))
        for s in g.subjects(RDF.type, ARKHE.AttentionHead):
            axioms.add(("Instance", "AttentionHead", str(s)))
        for s in g.subjects(RDF.type, ARKHE.FeedForwardNetwork):
            axioms.add(("Instance", "FFN", str(s)))

        for s in g.subjects(ARKHE.hasParameterRatio, None):
            axioms.add(("Performance", "ParameterRatio", str(s)))
        return axioms

    def _is_security_axiom(self, ax: Tuple) -> bool:
        return any(ent in str(ax) for ent in SECURITY_ENTITIES)

    def _is_architectural_axiom(self, ax: Tuple) -> bool:
        return any(ent in str(ax) for ent in ARCHITECTURAL_ENTITIES)

    def _is_performance_axiom(self, ax: Tuple) -> bool:
        return any(ent in str(ax) for ent in PERFORMANCE_ENTITIES)

    def classify_change(self) -> Tuple[Literal["PERFORMANCE_MAJOR", "ARCHITECTURAL_MAJOR", "SECURITY_MAJOR", "MAJOR", "MINOR", "PATCH"], dict]:
        old_axioms = self._get_axioms(self.old_g)
        new_axioms = self._get_axioms(self.new_g)

        removed = old_axioms - new_axioms
        added = new_axioms - old_axioms

        report = {
            "removed_axioms": [list(r) for r in removed],
            "added_axioms": [list(a) for a in added],
            "breaking_changes": [],
            "security_changes": [],
            "architectural_changes": [],
            "performance_changes": [],
            "safe_changes": []
        }

        is_perf_major = False
        is_arch_major = False
        is_security_major = False
        is_major = False

        for ax in added:
            if self._is_performance_axiom(ax):
                ratios = list(self.new_g.objects(URIRef(ax[2]), ARKHE.hasParameterRatio))
                for r in ratios:
                    val = float(r)
                    if val < 2.0:
                        is_perf_major = True
                        report["performance_changes"].append({
                            "type": "INEFFICIENT_DEGENERATION",
                            "axiom": ax,
                            "ratio": val,
                            "reason": f"Razão de parâmetros {val:.2f} < 2.0."
                        })
            elif self._is_architectural_axiom(ax):
                is_arch_major = True
            elif self._is_security_axiom(ax):
                is_security_major = True
            elif ax[0] == "Instance" and ax[1] in ("Transformer", "AttentionHead", "FFN"):
                is_arch_major = True

        for ax in removed:
            if self._is_architectural_axiom(ax):
                is_arch_major = True
            elif self._is_security_axiom(ax):
                is_security_major = True
            elif ax[0] in ("ClassDeclaration", "ObjectProperty"):
                is_major = True

        if is_perf_major: return "PERFORMANCE_MAJOR", report
        if is_arch_major: return "ARCHITECTURAL_MAJOR", report
        if is_security_major: return "SECURITY_MAJOR", report
        if is_major: return "MAJOR", report
        elif added: return "MINOR", report
        else: return "PATCH", report

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    diff = OWLSemVerDiff(sys.argv[1], sys.argv[2])
    semver, report = diff.classify_change()
    report["semver"] = semver
    print(json.dumps(report, indent=2))

    codes = {"PERFORMANCE_MAJOR": 5, "ARCHITECTURAL_MAJOR": 4, "SECURITY_MAJOR": 3, "MAJOR": 2, "MINOR": 1, "PATCH": 0}
    sys.exit(codes.get(semver, 0))
