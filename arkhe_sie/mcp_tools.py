#!/usr/bin/env python3
"""
mcp_tools.py — Exposição do SIE como ferramentas MCP
Ferramentas: sie_encode, sie_score, sie_extract
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from .sie_client import SIEClient, EncodeRequest, ScoreRequest, ExtractRequest
from .temporal_anchor import SIETemporalAnchor
from .guardian_monitor import SIEQualityMonitor

def register_sie_tools(server: Server, sie_client: SIEClient, anchor: SIETemporalAnchor, monitor: SIEQualityMonitor):
    """Registra as 3 ferramentas SIE no servidor MCP."""

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="sie_encode",
                description="Convert text to vector embeddings using Superlinked Inference Engine",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "texts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Texts to encode"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model name (default: BAAI/bge-large-en-v1.5)",
                            "default": "BAAI/bge-large-en-v1.5"
                        },
                        "pooling": {
                            "type": "string",
                            "description": "Pooling method (mean, cls, max)",
                            "default": "mean"
                        }
                    },
                    "required": ["texts"]
                }
            ),
            Tool(
                name="sie_score",
                description="Rerank documents by relevance to a query using SIE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query text"},
                        "documents": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Documents to score"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model name (default: BAAI/bge-reranker-v2-m3)",
                            "default": "BAAI/bge-reranker-v2-m3"
                        }
                    },
                    "required": ["query", "documents"]
                }
            ),
            Tool(
                name="sie_extract",
                description="Extract entities from unstructured text using SIE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to extract from"},
                        "entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Entity types to extract (person, organization, etc.)"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model name (default: Babelscape/rebel-large)",
                            "default": "Babelscape/rebel-large"
                        }
                    },
                    "required": ["text", "entities"]
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        import time

        if name == "sie_encode":
            start = time.time()
            request = EncodeRequest(
                texts=arguments["texts"],
                model=arguments.get("model", "BAAI/bge-large-en-v1.5"),
                pooling=arguments.get("pooling", "mean"),
            )
            response = await sie_client.encode(request)
            latency = (time.time() - start) * 1000

            # Validar qualidade
            phi_c = await monitor.validate_embeddings(
                arguments["texts"], response.get("embeddings", [])
            )

            # Ancorar
            await anchor.anchor_encode(
                {"texts": arguments["texts"], "model": request.model},
                response, latency, phi_c
            )

            return [TextContent(
                type="text",
                text=f"Encoded {len(arguments['texts'])} texts. "
                     f"Φ_C: {phi_c:.4f}. Latency: {latency:.1f}ms"
            )]

        elif name == "sie_score":
            start = time.time()
            request = ScoreRequest(
                query=arguments["query"],
                documents=arguments["documents"],
                model=arguments.get("model", "BAAI/bge-reranker-v2-m3"),
            )
            response = await sie_client.score(request)
            latency = (time.time() - start) * 1000

            phi_c = await monitor.validate_scores(
                arguments["query"], arguments["documents"],
                response.get("scores", [])
            )

            await anchor.anchor_score(
                {"query": arguments["query"], "documents": arguments["documents"], "model": request.model},
                response, latency, phi_c
            )

            return [TextContent(
                type="text",
                text=f"Scored {len(arguments['documents'])} documents. "
                     f"Top score: {max(response.get('scores', [0])):.4f}. "
                     f"Φ_C: {phi_c:.4f}"
            )]

        elif name == "sie_extract":
            start = time.time()
            request = ExtractRequest(
                text=arguments["text"],
                entities=arguments["entities"],
                model=arguments.get("model", "Babelscape/rebel-large"),
            )
            response = await sie_client.extract(request)
            latency = (time.time() - start) * 1000

            phi_c = await monitor.validate_extractions(
                arguments["text"], response.get("entities", {})
            )

            await anchor.anchor_extract(
                {"text": arguments["text"], "entities": arguments["entities"], "model": request.model},
                response, latency, phi_c
            )

            total = sum(len(v) for v in response.get("entities", {}).values())
            return [TextContent(
                type="text",
                text=f"Extracted {total} entities. Φ_C: {phi_c:.4f}. Latency: {latency:.1f}ms"
            )]

        raise ValueError(f"Unknown tool: {name}")