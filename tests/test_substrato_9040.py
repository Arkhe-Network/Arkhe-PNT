import pytest
import asyncio
from mirage import Workspace
from mirage.resource.ram import RAMResource
from arkhe_mirage.secure_workspace import SecureMirageWorkspace

class MockTemporal:
    async def anchor_event(self, event_type, data):
        return "a3f2b8c9d1e4f5a6"

class MockGuardian:
    def exorcise(self, command):
        if "rm -rf" in command:
            return False, None
        return True, None

class MockPhiBus:
    def get_mesh_coherence(self):
        return 0.997

@pytest.mark.asyncio
async def test_secure_mirage_workspace_safe_command():
    ws = Workspace({'/data': RAMResource()})
    secure_ws = SecureMirageWorkspace(
        ws,
        temporal_chain=MockTemporal(),
        guardian=MockGuardian(),
        phi_bus=MockPhiBus()
    )
    result = await secure_ws.execute("cp /data/test.txt /data/copy.txt")

    assert result.success is True
    assert result.guardian_approved is True
    assert result.phi_c_before == 0.997
    assert result.phi_c_after == 0.997
    assert result.temporal_seal == "a3f2b8c9d1e4f5a6"
    assert len(secure_ws.operation_log) == 1

@pytest.mark.asyncio
async def test_secure_mirage_workspace_blocked_command_by_pattern():
    ws = Workspace({'/data': RAMResource()})
    secure_ws = SecureMirageWorkspace(
        ws,
        temporal_chain=MockTemporal(),
        guardian=MockGuardian(),
        phi_bus=MockPhiBus()
    )
    result = await secure_ws.execute("rm -rf /")

    assert result.success is False
    assert result.guardian_approved is False
    assert result.blocked_reason is not None
    assert "padrão de segurança" in result.blocked_reason
    assert len(secure_ws.operation_log) == 1

@pytest.mark.asyncio
async def test_secure_mirage_workspace_blocked_command_by_guardian():
    ws = Workspace({'/data': RAMResource()})
    # Remove rm -rf from blocked patterns to test guardian directly
    secure_ws = SecureMirageWorkspace(
        ws,
        temporal_chain=MockTemporal(),
        guardian=MockGuardian(),
        phi_bus=MockPhiBus()
    )
    secure_ws.BLOCKED_PATTERNS = []

    result = await secure_ws.execute("rm -rf /data")

    assert result.success is False
    assert result.guardian_approved is False
    assert result.blocked_reason == "Comando bloqueado pelo Guardian Attractor"
    assert len(secure_ws.operation_log) == 1

@pytest.mark.asyncio
async def test_custom_arkhe_commands():
    ws = Workspace({'/data': RAMResource()})
    secure_ws = SecureMirageWorkspace(
        ws,
        temporal_chain=MockTemporal(),
        guardian=MockGuardian(),
        phi_bus=MockPhiBus()
    )

    phi_res = await secure_ws._cmd_arkhe_phi_c("/data")
    assert "0.9970" in phi_res

    anchor_res = await secure_ws._cmd_arkhe_anchor("/data/test.txt")
    assert "a3f2b8c9d1e4f5a6" in anchor_res
