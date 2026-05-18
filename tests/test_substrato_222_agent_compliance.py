import pytest
from substrate_134.erc8004_canon import ERC8004_IdentityRegistry
from substrates.substrato_222_agent_compliance import AgentComplianceRegistry, AgentComplianceRecord

def test_agent_compliance_registry():
    identity_registry = ERC8004_IdentityRegistry()
    registry = AgentComplianceRegistry(identity_registry)

    # 1. Register valid agent
    registry.register_agent(
        identity_id="agent_123",
        controller_age=25,
        jurisdiction="us",
        licenses=["series_65"],
        spending_limit_daily=1000.0
    )

    # Valid transaction
    assert registry.verify_transaction("agent_123", 500.0, "financial_advice") is True

    # Over spending limit
    assert registry.verify_transaction("agent_123", 1500.0, "financial_advice") is False

    # 2. Register underage agent
    registry.register_agent(
        identity_id="agent_underage",
        controller_age=16,
        jurisdiction="br",
        spending_limit_daily=50.0
    )

    # Underage trying to do financial advice
    assert registry.verify_transaction("agent_underage", 10.0, "financial_advice") is False
    # Underage trying to do legal advice
    assert registry.verify_transaction("agent_underage", 10.0, "legal") is False
    # Underage doing normal service
    assert registry.verify_transaction("agent_underage", 10.0, "general_chat") is True

    # 3. Register sanctioned agent
    registry.register_agent(
        identity_id="agent_sanctioned",
        controller_age=30,
        jurisdiction="sanctioned_country",
        spending_limit_daily=100.0
    )
    assert registry.verify_transaction("agent_sanctioned", 10.0, "general_chat") is False

    # 4. Register unlicensed agent doing financial advice
    registry.register_agent(
        identity_id="agent_unlicensed",
        controller_age=30,
        jurisdiction="us",
        spending_limit_daily=1000.0
    )
    assert registry.verify_transaction("agent_unlicensed", 10.0, "financial_advice") is False

    # 5. Non-existent agent
    assert registry.verify_transaction("agent_missing", 10.0, "general_chat") is False
