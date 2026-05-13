"""
Extensões da Camada 4:
- DependencyCache: cache incremental de pacotes
- SemVer: parsing, comparação, resolução de versões
- Integração com MythosGate e plugins de auditoria
"""
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from .ecosystem_arkp import ArkToml, ArtBlock, Registry as PackageRegistry, ConRAGAudit as ConRAGAuditor, ArkpCLI, QIPRoyaltyEngine

# Mock MythosGate since governance isn't implemented here yet.
class MythosGate:
    def __init__(self, mode='planetary'):
        self.mode = mode
    def evaluate_irreversible(self, action: str, context: Dict) -> bool:
        risk = context.get('foresight_risk', 0.0)
        if risk > 0.5:
            return False
        return True

# ========== SEMANTIC VERSIONING ==========
class SemVer:
    PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")
    def __init__(self, version_str: str):
        match = self.PATTERN.match(version_str.strip())
        if not match:
            raise ValueError(f"Invalid semver: {version_str}")
        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.pre = match.group(4)
        self.build = match.group(5)

    def __str__(self):
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            base += f"-{self.pre}"
        if self.build:
            base += f"+{self.build}"
        return base

    def __lt__(self, other: 'SemVer'):
        # Compare major, minor, patch, then pre-release
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        # Pre-release: absence > presence, then lexical
        if self.pre == other.pre:
            return False
        if self.pre is None:
            return False  # self is greater
        if other.pre is None:
            return True
        return self.pre < other.pre

    def __eq__(self, other):
        return (self.major, self.minor, self.patch, self.pre) == (other.major, other.minor, other.patch, other.pre)
    def __le__(self, other): return self < other or self == other
    def __gt__(self, other): return not self <= other
    def __ge__(self, other): return not self < other

# ========== DEPENDENCY CACHE ==========
class DependencyCache:
    """Cache em disco para dependências, evitando re-downloads."""
    def __init__(self, cache_dir: Path = Path(".arkhe-cache/deps")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, name: str, version: SemVer) -> str:
        return f"{name}@{version}"

    def has(self, name: str, version: SemVer) -> bool:
        return (self.cache_dir / self._key(name, version)).exists()

    def get(self, name: str, version: SemVer) -> Optional[bytes]:
        path = self.cache_dir / self._key(name, version)
        if path.exists():
            return path.read_bytes()
        return None

    def store(self, name: str, version: SemVer, content: bytes):
        path = self.cache_dir / self._key(name, version)
        path.write_bytes(content)

    def resolve_latest(self, name: str, registry: PackageRegistry) -> Optional[SemVer]:
        """Procura a versão mais recente no registry e retorna o SemVer."""
        versions = []
        if name in registry.packages:
            for block in registry.packages[name]:
                try:
                    versions.append(SemVer(block.version))
                except ValueError:
                    continue
        return max(versions) if versions else None

class ArkpCLI_Enhanced(ArkpCLI):
    def __init__(self, registry, qip, auditor, cache_dir=".arkhe-cache", mythos_gate=None):
        super().__init__(registry, qip, auditor)
        self.cache = DependencyCache(Path(cache_dir))
        self.gate = mythos_gate or MythosGate(mode='planetary')
        self.current_manifest = None

    def resolve_dependencies(self, manifest: ArkToml) -> Dict[str, bytes]:
        """Resolve todas as dependências usando cache local e registry."""
        resolved = {}
        for name, version_req in manifest.dependencies.items():
            if version_req.startswith('^'):
                base = SemVer(version_req[1:])
                versions = []
                if name in self.registry.packages:
                    for block in self.registry.packages[name]:
                        try:
                            versions.append(SemVer(block.version))
                        except ValueError:
                            pass
                compatible = [v for v in versions if v.major == base.major and v >= base]
                if compatible:
                    version = max(compatible)
                else:
                    raise ValueError(f"No compatible version for {name} {version_req}")
            elif version_req.startswith('~'):
                base = SemVer(version_req[1:])
                versions = []
                if name in self.registry.packages:
                    for block in self.registry.packages[name]:
                        try:
                            versions.append(SemVer(block.version))
                        except ValueError:
                            pass
                compatible = [v for v in versions if v.major == base.major and v.minor == base.minor and v >= base]
                if compatible:
                    version = max(compatible)
                else:
                    raise ValueError(f"No compatible version for {name} {version_req}")
            else:
                version = SemVer(version_req)

            content = self.cache.get(name, version)
            if content is None:
                content = f"package {name}@{version}".encode()
                self.cache.store(name, version, content)
            resolved[name] = content
        return resolved

    def build(self, name: str, code: str = "") -> Dict:
        manifest = self.projects.get(name)
        if not manifest:
            return {"error": "project_not_found"}
        try:
            deps = self.resolve_dependencies(manifest)
        except Exception as e:
            return {"success": False, "error": str(e)}
        return super().build(name, code)

    def publish(self, name: str, code: str, author_orcid: str, dry_run=False) -> Dict:
        """Publicação com Mythos Gate para decisões irreversíveis."""
        manifest = self.projects.get(name)
        if not manifest:
            return {"success": False, "error": "project_not_found"}

        audit_report = self.audit.audit(manifest, code)
        if not audit_report["passed"] and not dry_run:
            return {"success": False, "error": "Audit failed", "audit": audit_report}

        gate_decision = self.gate.evaluate_irreversible(
            f"publish {manifest.name}@{manifest.version}",
            context={"foresight_risk": self._compute_risk(manifest)}
        )
        if not gate_decision:
            return {"success": False, "error": "Mythos Gate rejected publication"}

        if dry_run:
            return {"success": True, "dry_run": True}
        return super().publish(name, code, author_orcid)

    def _compute_risk(self, manifest: ArkToml) -> float:
        risk = 0.05
        if any(kw in manifest.name.lower() for kw in ["nuclear", "bioweapon", "genesis"]):
            risk = 0.9
        elif "unsafe" in manifest.description.lower():
            risk = 0.6
        return risk

class AuditReport:
    def __init__(self, passed, score, checks=None, issues=None, zk_proof=None, temporal_anchor=None):
        self.passed = passed
        self.score = score
        self.checks = checks or {}
        self.issues = issues or []
        self.zk_proof = zk_proof
        self.temporal_anchor = temporal_anchor

class PluggableAuditor(ConRAGAuditor):
    def __init__(self):
        super().__init__()
        self.plugins: List[Callable] = []

    def register_plugin(self, plugin_fn):
        self.plugins.append(plugin_fn)

    def audit(self, manifest, source):
        base_report = super().audit(manifest, source)

        combined_passed = base_report["passed"]
        combined_issues = base_report.get("violations", [])
        combined_checks = base_report.get("scores", {})

        for plugin in self.plugins:
            plugin_report = plugin(manifest, source)
            combined_passed = combined_passed and plugin_report.passed
            combined_issues.extend(plugin_report.issues)
            combined_checks.update(plugin_report.checks)

        score = sum(1 for v in combined_checks.values() if v) / len(combined_checks) if combined_checks else 0.0

        report = {
            "manifest": manifest.name,
            "passed": combined_passed,
            "scores": combined_checks,
            "violations": combined_issues,
            "overall": score,
        }
        return report

def license_audit_plugin(manifest: ArkToml, source: str) -> AuditReport:
    if manifest.license in ["MIT", "Apache-2.0", "BSD-3-Clause", "ARKHE-1.0"]:
        return AuditReport(passed=True, score=1.0, checks={"license_ok": True})
    return AuditReport(passed=False, score=0.0, issues=["License not recognized"],
                       checks={"license_ok": False})
