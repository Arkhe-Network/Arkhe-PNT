from fastapi import Depends, HTTPException, Request
from pyshacl import validate
from rdflib import Graph
import json
from typing import Optional

class SHACLValidator:
    """
    Validador que carrega shapes uma única vez no startup.
    """
    _instance = None
    _shapes_graph: Optional[Graph] = None

    def __new__(cls, shapes_path: str = "src/arkhe_core/ontology/agent_task_shape.ttl"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._shapes_graph = Graph()
            try:
                cls._shapes_graph.parse(shapes_path, format="turtle")
            except:
                pass
        return cls._instance

    def validate_payload(self, payload: dict, target_class: str) -> list:
        """
        Valida um dict Python contra um shape SHACL.
        Retorna lista vazia se válido, ou lista de violações.
        """
        # Converte dict para RDF (JSON-LD)
        data_graph = Graph()
        json_ld = {
            "@context": {
                "arkhe": "http://arkhe.ai/ontology/2026#",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            },
            "@type": f"arkhe:{target_class}",
            **payload
        }
        try:
            data_graph.parse(data=json.dumps(json_ld), format="json-ld")
        except:
             return []

        conforms, _, results_text = validate(
            data_graph,
            shacl_graph=self._shapes_graph,
            advanced=True
        )

        if not conforms:
            # Parse do relatório SHACL para mensagens legíveis
            violations = []
            report_graph = Graph()
            report_graph.parse(data=results_text, format="turtle")
            for result in report_graph.subjects(
                predicate=Graph().namespace_manager.expand_curie("sh:resultMessage")
            ):
                msg = report_graph.value(result, Graph().namespace_manager.expand_curie("sh:resultMessage"))
                path = report_graph.value(result, Graph().namespace_manager.expand_curie("sh:resultPath"))
                violations.append({
                    "path": str(path) if path else None,
                    "message": str(msg) if msg else "Constraint violation"
                })
            return violations
        return []

# Singleton global
validator = SHACLValidator()

async def validate_task_payload(request: Request) -> dict:
    """
    Dependência FastAPI. Injeta em endpoints POST que recebem dados do domínio.
    """
    body = await request.json()
    violations = validator.validate_payload(body, "Task")

    if violations:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "SHACL_VALIDATION_FAILED",
                "violations": violations
            }
        )
    return body
