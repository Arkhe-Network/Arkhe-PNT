#!/usr/bin/env python3
"""Ferramentas MCP para operações seguras no Mirage via Arkhe."""

from mcp.server import Server
from mcp.types import Tool, TextContent
from .secure_workspace import SecureMirageWorkspace

def register_mirage_tools(server: Server, secure_ws: SecureMirageWorkspace):
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="mirage_execute",
                description="Executa comando bash no VFS Mirage com proteção Arkhe",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Comando bash (cat, grep, cp, etc.)"},
                    },
                    "required": ["command"],
                },
            ),
            Tool(
                name="mirage_list_mounts",
                description="Lista todos os mounts ativos no workspace Mirage",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="mirage_phi_c",
                description="Verifica Φ_C de um mount específico",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Caminho do mount"},
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="mirage_audit_log",
                description="Recupera log de auditoria de operações no VFS",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 20},
                    },
                    "required": [],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "mirage_execute":
            result = await secure_ws.execute(arguments["command"])
            status = "✅" if result.success else "❌"
            return [TextContent(
                type="text",
                text=f"{status} {result.operation.value} | Φ_C: {result.phi_c_before:.4f}→{result.phi_c_after:.4f} | "
                     f"Guardian: {'✅' if result.guardian_approved else '❌'} | "
                     f"Seal: {result.temporal_seal or 'N/A'}\n"
                     f"Output: {result.output_preview or '(none)'}"
            )]

        elif name == "mirage_list_mounts":
            mounts = secure_ws.ws._mounts if hasattr(secure_ws.ws, '_mounts') else {}
            return [TextContent(
                type="text",
                text=f"📂 Mounts: {json.dumps({k: type(v).__name__ for k, v in mounts.items()}, indent=2)}"
            )]

        elif name == "mirage_phi_c":
            phi = await secure_ws._cmd_arkhe_phi_c(arguments["path"])
            return [TextContent(type="text", text=phi)]

        elif name == "mirage_audit_log":
            limit = arguments.get("limit", 20)
            log = secure_ws.operation_log[-limit:]
            return [TextContent(
                type="text",
                text="\n".join(
                    f"[{r.operation.value}] {r.path}: {'✅' if r.success else '❌'} | "
                    f"Φ_C={r.phi_c_after:.4f} | Seal={r.temporal_seal or 'N/A'}"
                    for r in log
                )
            )]

        raise ValueError(f"Unknown tool: {name}")
