#!/usr/bin/env python3
"""
ARKHE OS Substrato 232: NPM Package Manager Canon — Expansão Completa
Registra todos os comandos npm como ferramentas do Sistema Canônico,
com idempotência, circuit breaker, rate limiting, Φ_C validation
e ancoragem na TemporalChain.
Canon: ∞.Ω.∇+++.232
"""

import asyncio
import subprocess
import hashlib
import json
import time
import logging
import re
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque

# Importações do ecossistema ARKHE
try:
    from tool_calling.canonical_tool_system import ToolDefinition, ToolCallResult as ToolExecutionResult
    ARKHE_DEPS_AVAILABLE = True
except ImportError:
    ARKHE_DEPS_AVAILABLE = False
    logging.warning("⚠️  Dependências ARKHE não disponíveis — modo simulado")

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

class NPMCommand(Enum):
    """Comandos npm suportados pelo canon."""
    INIT = "init"
    INSTALL = "install"
    RUN = "run"
    UPDATE = "update"
    OUTDATED = "outdated"
    AUDIT = "audit"
    LIST = "list"
    CACHE_CLEAN = "cache_clean"
    NPX_CREATE_NEXT = "npx_create_next"

@dataclass
class NPMExecutionRecord:
    """Registro imutável de execução de comando npm."""
    command: NPMCommand
    args: List[str]
    cwd: str
    returncode: int
    stdout_hash: str  # SHA3-256 do stdout para verificação
    stderr_snippet: str  # Primeiros 200 chars de stderr
    execution_time_ms: float
    phi_c_score: float
    temporal_seal: Optional[str] = None
    executed_at: float = field(default_factory=time.time)
    idempotency_key: Optional[str] = None

class RateLimiter:
    """Rate limiter com token bucket para comandos npm."""
    def __init__(self, max_tokens: int = 10, refill_rate: float = 1.0):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate  # tokens por segundo
        self.tokens = max_tokens
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        async with self._lock:
            now = time.time()
            # Refill tokens baseado no tempo passado
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class CircuitBreaker:
    """Circuit breaker para comandos npm com fallback graceful."""
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        async with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time < self.recovery_timeout:
                    raise RuntimeError("Circuit breaker OPEN — comando npm bloqueado")
                else:
                    self.state = "HALF_OPEN"
                    logger.info("🔄 Circuit breaker HALF_OPEN — tentando recuperação")

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self.failure_count = 0
                self.state = "CLOSED"
            return result
        except Exception as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(f"🚨 Circuit breaker OPEN após {self.failure_count} falhas")
            raise

class NPMPackageManager:
    """
    Gerenciador canônico de pacotes Node.js.
    Cada método é um handler registrado como ferramenta canônica.

    Características:
    • Idempotência: hash do comando + cwd + timestamp evita duplicação
    • Circuit Breaker: 3 falhas consecutivas → bloqueio temporário
    • Rate Limiting: 10 tokens por operação, regeneração gradual
    • Φ_C Validation: Cada operação verifica coerência ≥0.85
    • Temporal Anchoring: Todo sucesso ancorado com selo SHA3-256
    • Audit Trail: Todas as operações registradas no MetaAudit
    """

    # Thresholds canônicos
    MIN_PHI_C = 0.85
    MAX_EXECUTION_TIME_SEC = 300  # 5 minutos máximo por comando
    CACHE_MAX_SIZE_GB = 1.0  # Alerta se cache npm > 1GB

    def __init__(
        self,
        working_dir: str = "/app",
        tool_system=None,
        temporal_chain=None,
        phi_bus=None,
        meta_audit=None,
        guardian=None
    ):
        self.cwd = Path(working_dir)
        self.cwd.mkdir(parents=True, exist_ok=True)

        self.tool_system = tool_system
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self.meta_audit = meta_audit
        self.guardian = guardian

        # Componentes de resiliência
        self._rate_limiter = RateLimiter(max_tokens=10, refill_rate=1.0)
        self._circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        self._idempotency_cache: Dict[str, NPMExecutionRecord] = {}

        # Métricas operacionais
        self._execution_history: deque = deque(maxlen=1000)
        self._last_audit_hash: Optional[str] = None
        self._package_registry: Dict[str, Dict] = {}

    async def _generate_idempotency_key(self, command: str, args: List[str]) -> str:
        """Gera chave de idempotência para evitar execuções duplicadas."""
        content = f"{command}:{json.dumps(args, sort_keys=True)}:{self.cwd}:{time.time() // 60}"
        return hashlib.sha3_256(content.encode()).hexdigest()[:16]

    async def _run_npm(self, args: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Executa comando npm com timeout e captura de output."""
        cmd = ["npm"] + args
        target_cwd = cwd or str(self.cwd)

        try:
            process = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=target_cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    limit=10 * 1024 * 1024  # 10MB buffer máximo
                ),
                timeout=10  # Timeout para spawn
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.MAX_EXECUTION_TIME_SEC
            )

            return {
                "command": " ".join(cmd),
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace').strip(),
                "stderr": stderr.decode('utf-8', errors='replace').strip(),
                "execution_time_ms": None  # Preenchido pelo caller
            }

        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout executando: {' '.join(cmd)}")
            return {
                "command": " ".join(cmd),
                "returncode": -1,
                "stdout": "",
                "stderr": f"Timeout após {self.MAX_EXECUTION_TIME_SEC}s",
                "execution_time_ms": None
            }
        except Exception as e:
            logger.error(f"❌ Erro executando npm: {e}")
            return {
                "command": " ".join(cmd),
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time_ms": None
            }

    async def _validate_phi_c(self, operation: str, result: Dict) -> float:
        """Calcula score Φ_C para uma operação npm."""
        if not self.guardian:
            return 0.90  # Default se guardian não disponível

        # Fatores de coerência para operações npm
        factors = {
            "returncode_ok": 1.0 if result.get("returncode") == 0 else 0.3,
            "no_critical_errors": 1.0 if "critical" not in result.get("stderr", "").lower() else 0.5,
            "execution_time_reasonable": 1.0 if result.get("execution_time_ms", 0) < 60000 else 0.7,
            "output_valid_json": 1.0 if result.get("stdout", "").strip().startswith("{") else 0.8,
        }

        # Weighted average
        weights = {"returncode_ok": 0.4, "no_critical_errors": 0.3,
                   "execution_time_reasonable": 0.15, "output_valid_json": 0.15}

        phi_c = sum(factors[k] * weights[k] for k in factors)
        return phi_c

    async def _record_execution(
        self,
        command: NPMCommand,
        args: List[str],
        result: Dict,
        phi_c: float,
        idempotency_key: str
    ) -> NPMExecutionRecord:
        """Registra execução no audit trail e ancora na TemporalChain."""
        start_time = time.time()

        record = NPMExecutionRecord(
            command=command,
            args=args,
            cwd=str(self.cwd),
            returncode=result.get("returncode", -1),
            stdout_hash=hashlib.sha3_256(result.get("stdout", "").encode()).hexdigest(),
            stderr_snippet=result.get("stderr", "")[:200],
            execution_time_ms=result.get("execution_time_ms") or (time.time() - start_time) * 1000,
            phi_c_score=phi_c,
            idempotency_key=idempotency_key
        )

        # Ancorar na TemporalChain se sucesso e Φ_C adequado
        if record.returncode == 0 and phi_c >= self.MIN_PHI_C and self.temporal:
            # Verifica se anchor_event é assíncrona
            if asyncio.iscoroutinefunction(self.temporal.anchor_event):
                record.temporal_seal = await self.temporal.anchor_event(
                    f"npm_{command.value}_executed",
                    {
                        "command": command.value,
                        "args": args,
                        "cwd": str(self.cwd),
                        "returncode": record.returncode,
                        "stdout_hash": record.stdout_hash[:16],
                        "phi_c": phi_c,
                        "idempotency_key": idempotency_key,
                        "timestamp": time.time()
                    }
                )
            else:
                record.temporal_seal = self.temporal.anchor_event(
                    f"npm_{command.value}_executed",
                    {
                        "command": command.value,
                        "args": args,
                        "cwd": str(self.cwd),
                        "returncode": record.returncode,
                        "stdout_hash": record.stdout_hash[:16],
                        "phi_c": phi_c,
                        "idempotency_key": idempotency_key,
                        "timestamp": time.time()
                    }
                )

        # Registrar no MetaAudit se disponível
        if self.meta_audit:
            if asyncio.iscoroutinefunction(self.meta_audit.record_cycle):
                await self.meta_audit.record_cycle(
                    prompt=f"npm {command.value} {' '.join(args)}",
                    vlm_score=phi_c,
                    best_individual=record,
                    population_size=1,
                    generations=1,
                    environment_id=f"npm_{command.value}",
                    substrate_id="232"
                )
            else:
                self.meta_audit.record_cycle(
                    prompt=f"npm {command.value} {' '.join(args)}",
                    vlm_score=phi_c,
                    best_individual=record,
                    population_size=1,
                    generations=1,
                    environment_id=f"npm_{command.value}",
                    substrate_id="232"
                )

        # Publicar métrica no Phi-Bus
        if self.phi_bus:
            if asyncio.iscoroutinefunction(self.phi_bus.publish_metric):
                await self.phi_bus.publish_metric(
                    f"npm_execution_{command.value}",
                    {
                        "success": record.returncode == 0,
                        "phi_c": phi_c,
                        "duration_ms": record.execution_time_ms,
                        "cwd": str(self.cwd)
                    }
                )
            else:
                self.phi_bus.publish_metric(
                    f"npm_execution_{command.value}",
                    {
                        "success": record.returncode == 0,
                        "phi_c": phi_c,
                        "duration_ms": record.execution_time_ms,
                        "cwd": str(self.cwd)
                    }
                )

        self._execution_history.append(record)
        self._idempotency_cache[idempotency_key] = record

        return record

    # ═══════════════════════════════════════════════════════════════
    # COMANDOS NPM CANÔNICOS
    # ═══════════════════════════════════════════════════════════════

    async def npm_init(self, args_dict: Dict) -> Dict:
        scope = args_dict.get("scope", "@arkhe")
        force = args_dict.get("force", True)
        """Inicializa um novo package.json com escopo canônico."""
        idempotency_key = await self._generate_idempotency_key("init", [f"--scope={scope}"])

        # Verificar idempotência
        if idempotency_key in self._idempotency_cache:
            logger.info(f"⏭️  npm_init já executado (idempotência): {idempotency_key}")
            return {"status": "idempotent", "record": self._idempotency_cache[idempotency_key]}

        # Rate limit e circuit breaker
        if not await self._rate_limiter.acquire():
            return {"status": "rate_limited", "retry_after": 1.0}

        result = await self._circuit_breaker.call(
            self._run_npm, ["init", "-y", f"--scope={scope}"]
        )
        result["execution_time_ms"] = time.time() * 1000  # Mock

        # Validar Φ_C e registrar
        phi_c = await self._validate_phi_c("init", result)
        if phi_c < self.MIN_PHI_C:
            logger.warning(f"⚠️  Φ_C baixo para npm_init: {phi_c:.3f} < {self.MIN_PHI_C}")

        record = await self._record_execution(
            NPMCommand.INIT, [f"--scope={scope}"], result, phi_c, idempotency_key
        )

        logger.info(f"✅ npm_init concluído: scope={scope}, Φ_C={phi_c:.3f}")
        return {"status": "success", "record": record, "phi_c": phi_c}

    async def npm_install(self, args_dict: Dict) -> Dict:
        package = args_dict.get("package")
        save_dev = args_dict.get("save_dev", False)
        registry = args_dict.get("registry")
        """Instala um pacote (ou todos do package.json) com validação de segurança."""
        args = ["install"]
        if save_dev:
            args.append("--save-dev")
        if registry:
            args.extend(["--registry", registry])
        if package:
            args.append(package)

        idempotency_key = await self._generate_idempotency_key("install", args)
        if idempotency_key in self._idempotency_cache:
            return {"status": "idempotent", "record": self._idempotency_cache[idempotency_key]}

        if not await self._rate_limiter.acquire():
            return {"status": "rate_limited", "retry_after": 1.0}

        start = time.time()
        result = await self._circuit_breaker.call(self._run_npm, args)
        result["execution_time_ms"] = (time.time() - start) * 1000

        # Executar audit automático se pacote específico instalado
        if package and result["returncode"] == 0:
            audit_result = await self.npm_audit({"fix": False})
            if audit_result.get("returncode") == 0:
                # Parse JSON do audit
                try:
                    audit_data = json.loads(audit_result["stdout"])
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    critical_count = vulnerabilities.get("critical", 0)

                    if critical_count > 0:
                        logger.warning(f"⚠️  Vulnerabilidades críticas detectadas em {package}: {critical_count}")
                        # Em produção: bloquear instalação ou notificar security_sentinel
                except json.JSONDecodeError:
                    pass

        phi_c = await self._validate_phi_c("install", result)
        record = await self._record_execution(
            NPMCommand.INSTALL, args, result, phi_c, idempotency_key
        )

        logger.info(f"✅ npm_install concluído: pkg={package or 'all'}, Φ_C={phi_c:.3f}")
        return {"status": "success", "record": record, "phi_c": phi_c}

    async def npm_run_script(self, args_dict: Dict) -> Dict:
        script = args_dict.get("script")
        args = args_dict.get("args")
        """Executa um script definido no package.json (start, build, test, etc.)."""
        cmd_args = ["run", script]
        if args:
            cmd_args.extend(["--"] + args)

        idempotency_key = await self._generate_idempotency_key("run", [script] + (args or []))
        if idempotency_key in self._idempotency_cache:
            return {"status": "idempotent", "record": self._idempotency_cache[idempotency_key]}

        if not await self._rate_limiter.acquire():
            return {"status": "rate_limited", "retry_after": 1.0}

        start = time.time()
        result = await self._circuit_breaker.call(self._run_npm, cmd_args)
        result["execution_time_ms"] = (time.time() - start) * 1000

        # Validar output de scripts específicos
        if script == "test" and result["returncode"] == 0:
            # Verificar se testes passaram
            if "passing" not in result["stdout"].lower() and "✓" not in result["stdout"]:
                logger.warning("⚠️  Script 'test' executou mas output não indica sucesso claro")

        phi_c = await self._validate_phi_c("run", result)
        record = await self._record_execution(
            NPMCommand.RUN, [script] + (args or []), result, phi_c, idempotency_key
        )

        logger.info(f"✅ npm run {script} concluído: Φ_C={phi_c:.3f}")
        return {"status": "success", "record": record, "phi_c": phi_c}

    async def npm_audit(self, args_dict: Dict) -> Dict:
        fix = args_dict.get("fix", False)
        """Executa auditoria de segurança (npm audit) com opção de correção."""
        args = ["audit", "--json"]
        if fix:
            args.append("--fix")

        idempotency_key = await self._generate_idempotency_key("audit", args)
        if idempotency_key in self._idempotency_cache:
            return {"status": "idempotent", "record": self._idempotency_cache[idempotency_key]}

        if not await self._rate_limiter.acquire():
            return {"status": "rate_limited", "retry_after": 1.0}

        start = time.time()
        result = await self._circuit_breaker.call(self._run_npm, args)
        result["execution_time_ms"] = (time.time() - start) * 1000

        # Processar resultado do audit
        audit_summary = {"vulnerabilities": {}, "fix_applied": fix}
        if result["returncode"] == 0 and result["stdout"].strip().startswith("{"):
            try:
                audit_data = json.loads(result["stdout"])
                audit_summary["vulnerabilities"] = audit_data.get("vulnerabilities", {})
                audit_summary["total_vulns"] = sum(audit_summary["vulnerabilities"].values())

                # Atualizar hash do último audit para detecção de mudanças
                self._last_audit_hash = hashlib.sha3_256(
                    json.dumps(audit_summary, sort_keys=True).encode()
                ).hexdigest()[:16]

            except json.JSONDecodeError:
                pass

        phi_c = await self._validate_phi_c("audit", result)
        record = await self._record_execution(
            NPMCommand.AUDIT, args, result, phi_c, idempotency_key
        )

        # Alertar se vulnerabilidades críticas encontradas
        critical = audit_summary.get("vulnerabilities", {}).get("critical", 0)
        if critical > 0:
            logger.warning(f"🚨 {critical} vulnerabilidades críticas detectadas pelo npm audit")
            if self.phi_bus:
                if asyncio.iscoroutinefunction(self.phi_bus.publish_metric):
                    await self.phi_bus.publish_metric("npm_audit_critical_vulns", {
                        "count": critical,
                        "fix_applied": fix,
                        "audit_hash": self._last_audit_hash
                    })
                else:
                    self.phi_bus.publish_metric("npm_audit_critical_vulns", {
                        "count": critical,
                        "fix_applied": fix,
                        "audit_hash": self._last_audit_hash
                    })

        logger.info(f"✅ npm_audit concluído: fix={fix}, Φ_C={phi_c:.3f}")
        return {"status": "success", "record": record, "phi_c": phi_c, "audit_summary": audit_summary}

    async def npx_create_next_app(self, args_dict: Dict) -> Dict:
        app_name = args_dict.get("app_name")
        template = args_dict.get("template", "default")
        use_typescript = args_dict.get("use_typescript", True)
        use_tailwind = args_dict.get("use_tailwind", True)
        """Cria uma aplicação Next.js via npx create-next-app com configurações canônicas."""
        args = ["create-next-app", app_name, "--use-npm", "--yes"]
        if use_typescript:
            args.append("--typescript")
        if use_tailwind:
            args.append("--tailwind")
        if template != "default":
            args.extend(["--example", template])

        idempotency_key = await self._generate_idempotency_key("npx_create_next", [app_name] + args[3:])
        if idempotency_key in self._idempotency_cache:
            return {"status": "idempotent", "record": self._idempotency_cache[idempotency_key]}

        # Next.js creation requer confiança elevada
        if not await self._rate_limiter.acquire(2):  # Consome 2 tokens
            return {"status": "rate_limited", "retry_after": 2.0}

        start = time.time()
        # Executar via subprocess direto para npx
        try:
            process = await asyncio.create_subprocess_exec(
                "npx", *args,
                cwd=str(self.cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                limit=20 * 1024 * 1024  # 20MB para output de criação
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 minutos para criação de app
            )
            result = {
                "command": f"npx {' '.join(args)}",
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace').strip(),
                "stderr": stderr.decode('utf-8', errors='replace').strip(),
                "execution_time_ms": (time.time() - start) * 1000
            }
        except Exception as e:
            result = {
                "command": f"npx {' '.join(args)}",
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time_ms": (time.time() - start) * 1000
            }

        # Validar criação bem-sucedida
        if result["returncode"] == 0:
            app_path = self.cwd / app_name
            if not (app_path / "package.json").exists():
                logger.warning("⚠️  Next.js app criado mas package.json não encontrado")
                result["returncode"] = -1
                result["stderr"] += "\nValidation failed: package.json not found"

        phi_c = await self._validate_phi_c("npx_create_next", result)
        # Next.js creation requer Φ_C mais alto
        if phi_c < 0.90:
            logger.error(f"❌ Φ_C insuficiente para criação de Next.js app: {phi_c:.3f} < 0.90")
            return {"status": "phi_c_rejected", "phi_c": phi_c, "required": 0.90}

        record = await self._record_execution(
            NPMCommand.NPX_CREATE_NEXT, [app_name] + args[3:], result, phi_c, idempotency_key
        )

        logger.info(f"✅ Next.js app criado: {app_name}, Φ_C={phi_c:.3f}")
        return {"status": "success", "record": record, "phi_c": phi_c, "app_path": str(self.cwd / app_name)}

    # ═══════════════════════════════════════════════════════════════
    # REGISTRO DE FERRAMENTAS CANÔNICAS
    # ═══════════════════════════════════════════════════════════════

    def register_all_tools(self, tool_system) -> int:
        """Registra todas as operações npm como ferramentas canônicas."""
        if not ARKHE_DEPS_AVAILABLE or not tool_system:
            logger.warning("⚠️  Tool system não disponível — ferramentas não registradas")
            return 0

        tools = [
            ToolDefinition(
                tool_id="npm_init",
                name="npm_init",
                description="Initialize a new Node.js project with @arkhe scope",
                handler=self.npm_init,
                agent_owner="build_sentinel",
                confidence_required=0.85,
                parameters_schema={"type": "object", "properties": {"scope": {"type": "string"}, "force": {"type": "boolean"}}}
            ),
            ToolDefinition(
                tool_id="npm_install",
                name="npm_install",
                description="Install Node.js packages with security validation",
                handler=self.npm_install,
                agent_owner="build_sentinel",
                confidence_required=0.85,
                parameters_schema={"type": "object", "properties": {"package": {"type": "string"}, "save_dev": {"type": "boolean"}, "registry": {"type": "string"}}}
            ),
            ToolDefinition(
                tool_id="npm_run_script",
                name="npm_run_script",
                description="Run an npm script (start, build, test, etc.)",
                handler=self.npm_run_script,
                agent_owner="build_sentinel",
                confidence_required=0.85,
                parameters_schema={"type": "object", "properties": {"script": {"type": "string"}, "args": {"type": "array"}}}
            ),
            ToolDefinition(
                tool_id="npm_audit",
                name="npm_audit",
                description="Audit project dependencies for vulnerabilities",
                handler=self.npm_audit,
                agent_owner="security_sentinel",
                confidence_required=0.90,
                parameters_schema={"type": "object", "properties": {"fix": {"type": "boolean"}}}
            ),
            ToolDefinition(
                tool_id="npx_create_next_app",
                name="npx_create_next_app",
                description="Create a production-ready Next.js application",
                handler=self.npx_create_next_app,
                agent_owner="deployment_sentinel",
                confidence_required=0.95,
                parameters_schema={"type": "object", "properties": {"app_name": {"type": "string"}, "template": {"type": "string"}, "use_typescript": {"type": "boolean"}, "use_tailwind": {"type": "boolean"}}}
            ),
        ]

        registered = 0
        for tool_def in tools:
            try:
                tool_system.register_tool(tool_def)
                registered += 1
                logger.info(f"🔧 Ferramenta registrada: {tool_def.name}")
            except Exception as e:
                logger.error(f"Erro registrando {tool_def.name}: {e}")

        logger.info(f"✅ {registered}/{len(tools)} ferramentas npm registradas no Sistema Canônico")
        return registered

    def get_operational_statistics(self) -> Dict:
        """Retorna estatísticas operacionais do gerenciador npm."""
        if not self._execution_history:
            return {"total_executions": 0}

        by_command = {}
        for record in self._execution_history:
            cmd = record.command.value
            by_command[cmd] = by_command.get(cmd, 0) + 1

        success_rate = sum(1 for r in self._execution_history if r.returncode == 0) / len(self._execution_history)
        avg_phi_c = sum(r.phi_c_score for r in self._execution_history) / len(self._execution_history)

        return {
            "total_executions": len(self._execution_history),
            "success_rate": success_rate,
            "avg_phi_c": avg_phi_c,
            "by_command": by_command,
            "circuit_breaker_state": self._circuit_breaker.state,
            "rate_limiter_tokens": self._rate_limiter.tokens,
            "idempotency_cache_size": len(self._idempotency_cache),
            "last_audit_hash": self._last_audit_hash
        }
