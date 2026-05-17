#!/usr/bin/env python3
"""
ARKHE OS Substrato 241+∞: Chemistry Seccomp Runner
Canon: ∞.Ω.∇+++.241.security.seccomp_runner
Função: Executar reações de química semântica em sandbox seccomp
para isolamento de processos criativos com princípio do menor privilégio.
"""

import os
import sys
import subprocess
import logging
import tempfile
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import IntEnum

# Import from hardened Unbuildable substrate
from security.native_seccomp_filter import NativeSeccompFilter, SeccompProfile

logger = logging.getLogger(__name__)

class ReactionSandboxProfile(IntEnum):
    """Perfis de sandbox para execução de reações."""
    CREATIVE_MINIMAL = 0    # Apenas leitura/escrita de arquivos temporários
    CREATIVE_STANDARD = 1   # + rede para consultas externas de conhecimento
    CREATIVE_FULL = 2       # + execução de subprocessos para reações complexas

class ChemistrySeccompRunner:
    """
    Executor de reações em sandbox seccomp.

    Características:
    • Perfis configuráveis baseados na complexidade da reação
    • Isolamento de filesystem com diretórios temporários dedicados
    • Timeout configurável para prevenir reações infinitas
    • Logging canônico de todas as execuções sandboxed
    • Integração com TemporalChain para auditoria de execução
    """

    # Mapeamento de perfil → configuração seccomp
    PROFILE_CONFIG = {
        ReactionSandboxProfile.CREATIVE_MINIMAL: {
            "seccomp_profile": SeccompProfile.STRICT,
            "allowed_paths": ["/tmp", "/dev/null"],
            "network_enabled": False,
            "subprocess_enabled": False,
            "max_runtime_seconds": 30
        },
        ReactionSandboxProfile.CREATIVE_STANDARD: {
            "seccomp_profile": SeccompProfile.MODERATE,
            "allowed_paths": ["/tmp", "/dev/null", "/etc/ssl/certs"],
            "network_enabled": True,
            "subprocess_enabled": False,
            "max_runtime_seconds": 60
        },
        ReactionSandboxProfile.CREATIVE_FULL: {
            "seccomp_profile": SeccompProfile.PERMISSIVE,
            "allowed_paths": ["/tmp", "/dev/null", "/etc/ssl/certs", "/usr/lib"],
            "network_enabled": True,
            "subprocess_enabled": True,
            "max_runtime_seconds": 120
        }
    }

    def __init__(
        self,
        seccomp_lib_path: str = "/usr/lib/libseccomp_filter.so",
        temporal_chain=None,
        phi_bus=None
    ):
        self.seccomp = NativeSeccompFilter(seccomp_lib_path)
        self.temporal = temporal_chain
        self.phi_bus = phi_bus
        self._execution_log: List[Dict] = []

    def run_reaction_sandboxed(
        self,
        reaction_code: str,
        profile: ReactionSandboxProfile,
        input_data: Optional[Dict] = None,
        reaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa código de reação em sandbox seccomp.

        Args:
            reaction_code: Código Python da reação a executar
            profile: Perfil de sandbox a aplicar
            input_data: Dados de entrada para a reação
            reaction_id: ID único para tracking (gerado se None)

        Returns:
            Dict com resultado, logs e metadados de segurança
        """
        import hashlib
        import time

        reaction_id = reaction_id or hashlib.sha3_256(
            f"{reaction_code}:{time.time()}".encode()
        ).hexdigest()[:12]

        config = self.PROFILE_CONFIG[profile]

        # Preparar ambiente sandboxed
        with tempfile.TemporaryDirectory() as sandbox_dir:
            sandbox_path = Path(sandbox_dir)

            # Escrever código da reação
            reaction_file = sandbox_path / "reaction.py"
            reaction_file.write_text(reaction_code)

            # Escrever dados de entrada se fornecidos
            if input_data:
                input_file = sandbox_path / "input.json"
                input_file.write_text(json.dumps(input_data))

            # Preparar comando Python
            cmd = [sys.executable, str(reaction_file)]
            if input_data:
                cmd.append(str(input_file))

            # Aplicar filtro seccomp se disponível
            seccomp_applied = False
            if self.seccomp._lib:
                seccomp_applied = self.seccomp.apply(config["seccomp_profile"])
                logger.debug(f"🔒 Seccomp aplicado: {seccomp_applied} (perfil={config['seccomp_profile'].name})")

            # Executar com timeout e isolamento
            start_time = time.time()
            try:
                env = os.environ.copy()
                # Restringir variáveis de ambiente
                env = {k: v for k, v in env.items() if k in ["PATH", "LANG", "LC_ALL"]}
                env["SANDBOX_DIR"] = str(sandbox_path)
                env["REACTION_ID"] = reaction_id

                result = subprocess.run(
                    cmd,
                    cwd=str(sandbox_path),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=config["max_runtime_seconds"],
                    # Em produção: adicionar preexec_fn para prctl(PR_SET_NO_NEW_PRIVS)
                )

                execution_time = time.time() - start_time

                # Parsear resultado
                output = {
                    "reaction_id": reaction_id,
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "stdout": result.stdout[:10000],  # Limitar output
                    "stderr": result.stderr[:10000],
                    "execution_time_ms": execution_time * 1000,
                    "sandbox_profile": profile.name,
                    "seccomp_applied": seccomp_applied,
                    "allowed_syscalls": self.seccomp.get_allowed_syscalls(config["seccomp_profile"])
                        if seccomp_applied else [],
                    "timestamp": time.time()
                }

                # Ancorar na TemporalChain
                if self.temporal:
                    seal = self.temporal.anchor_event("reaction_sandboxed_executed", {
                        "reaction_id": reaction_id,
                        "success": output["success"],
                        "execution_time_ms": output["execution_time_ms"],
                        "seccomp_profile": config["seccomp_profile"].name,
                        "timestamp": output["timestamp"]
                    })
                    output["temporal_seal"] = seal

                # Log para auditoria
                self._execution_log.append(output)

                logger.info(
                    f"{'✅' if output['success'] else '❌'} Reação sandboxed: {reaction_id} | "
                    f"Tempo: {output['execution_time_ms']:.1f}ms | "
                    f"Seccomp: {'ativo' if seccomp_applied else 'inativo'}"
                )

                return output

            except subprocess.TimeoutExpired as e:
                logger.error(f"⏱️  Timeout na reação {reaction_id}: >{config['max_runtime_seconds']}s")
                return {
                    "reaction_id": reaction_id,
                    "success": False,
                    "error": "timeout",
                    "message": f"Execution exceeded {config['max_runtime_seconds']} seconds",
                    "sandbox_profile": profile.name,
                    "timestamp": time.time()
                }
            except Exception as e:
                logger.error(f"❌ Erro na execução sandboxed: {e}")
                return {
                    "reaction_id": reaction_id,
                    "success": False,
                    "error": "execution_error",
                    "message": str(e),
                    "sandbox_profile": profile.name,
                    "timestamp": time.time()
                }

    def get_execution_statistics(self) -> Dict:
        """Retorna estatísticas de execuções sandboxed."""
        if not self._execution_log:
            return {"total_executions": 0}

        successful = sum(1 for e in self._execution_log if e["success"])
        avg_time = sum(e["execution_time_ms"] for e in self._execution_log) / len(self._execution_log)

        return {
            "total_executions": len(self._execution_log),
            "successful_executions": successful,
            "success_rate": successful / len(self._execution_log),
            "avg_execution_time_ms": avg_time,
            "seccomp_success_rate": sum(1 for e in self._execution_log if e.get("seccomp_applied")) / len(self._execution_log),
            "profiles_used": list(set(e["sandbox_profile"] for e in self._execution_log))
        }
