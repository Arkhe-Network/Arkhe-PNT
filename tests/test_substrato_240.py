#!/usr/bin/env python3
import asyncio
import pytest
from pypi.pypi_canonical_tool import PyPICanonicalTool
from tool_calling.canonical_tool_system import CanonicalToolCallingSystem, ToolCallRequest

class MockTemporalNetwork:
    async def anchor_event(self, event_type: str, details: dict) -> str:
        return f"SEAL_{event_type}"

class MockHSM:
    async def sign(self, payload: bytes) -> str:
        return "MOCK_SIGNATURE"

@pytest.mark.asyncio
async def test_pypi_canonical_tool_registration():
    tool_system = CanonicalToolCallingSystem(temporal=MockTemporalNetwork())
    pypi_tool = PyPICanonicalTool(working_dir="/tmp", temporal=MockTemporalNetwork(), hsm=MockHSM())

    pypi_tool.register_all_tools(tool_system)

    assert "pip_install" in tool_system.tool_registry
    assert "pip_freeze" in tool_system.tool_registry
    assert "create_venv" in tool_system.tool_registry
    assert "poetry_new" in tool_system.tool_registry

@pytest.mark.asyncio
async def test_pip_install_missing_params():
    pypi_tool = PyPICanonicalTool(working_dir="/tmp", temporal=MockTemporalNetwork(), hsm=MockHSM())
    result = await pypi_tool.pip_install({})
    assert result["status"] == "error"
    assert "required" in result["reason"]
