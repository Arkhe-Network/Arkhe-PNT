import sys
import pytest

from src.arkhe.layers.ecosystem_arkp import (
    ArkToml,
    ArtBlock,
    Registry,
    QIPRoyaltyEngine,
    ConRAGAudit,
    ArkpCLI,
)

def test_integration():
    reg = Registry()
    qip = QIPRoyaltyEngine()
    audit = ConRAGAudit()
    cli = ArkpCLI(reg, qip, audit)

    m = cli.new("quantum-probe", template="quantum", author="ORCID:RAFAEL")
    m.substrates["interstellar"] = "5555"
    m.royalties = {"author_share": 0.70, "relay_share": 0.30}

    code = "def main():\n    let q = Qubit::zero()\n    prove(q.coherence() > 0.99)"
    b = cli.build("quantum-probe", code)
    assert b["success"]

    t = cli.test("quantum-probe")
    assert t["success"]

    p = cli.publish("quantum-probe", code, "ORCID:RAFAEL")
    assert p["success"]

    inst = cli.install("quantum-probe")
    assert inst["success"]
    assert inst["verified"]

    assert qip.get_balance("ORCID:RAFAEL") > 0
    assert reg.get_stats()["total_packages"] == 1
    assert reg.get_stats()["verified"] == 1
