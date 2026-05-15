#!/usr/bin/env python3
"""Demonstração da integração Arkhe-Mirage."""

import asyncio
from mirage import Workspace
from mirage.resource.ram import RAMResource
from mirage.resource.s3 import S3Resource, S3Config
from mirage.resource.slack import SlackResource, SlackConfig
from arkhe_mirage.secure_workspace import SecureMirageWorkspace

async def demo():
    print("═" * 60)
    print("ARKHE-MIRAGE — Secure Virtual Filesystem Demo")
    print("═" * 60)

    # Criar workspace Mirage padrão
    ws = Workspace({
        '/data': RAMResource(),
        '/s3': S3Resource(S3Config(bucket='my-bucket')),
        '/slack': SlackResource(SlackConfig()),
    })

    # Mock para dependências Arkhe
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

    # Envolver com proteção Arkhe
    secure = SecureMirageWorkspace(
        ws,
        temporal_chain=MockTemporal(),
        guardian=MockGuardian(),
        phi_bus=MockPhiBus()
    )

    # Operação 1: Comando seguro
    print("\n📂 Operação segura:")
    result = await secure.execute("cp /s3/report.csv /data/local.csv")
    print(f"  Status: {'✅' if result.success else '❌'}")
    print(f"  Φ_C: {result.phi_c_before:.4f} → {result.phi_c_after:.4f}")
    print(f"  Seal: {result.temporal_seal or 'simulated'}")

    # Operação 2: Comando bloqueado
    print("\n🛡️ Comando bloqueado:")
    result = await secure.execute("rm -rf /")
    print(f"  Status: {'✅' if result.success else '❌'}")
    print(f"  Reason: {result.blocked_reason}")

    # Operação 3: Comando Arkhe personalizado
    print("\n🌀 Comando Arkhe:")
    phi_result = await secure._cmd_arkhe_phi_c("/s3")
    print(f"  {phi_result}")

    # Estatísticas
    print(f"\n📊 Audit Log: {len(secure.operation_log)} operações registradas")

    print("\n✅ Demo completed")

if __name__ == "__main__":
    asyncio.run(demo())
