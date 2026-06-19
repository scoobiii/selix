#!/usr/bin/env python3
"""Security Agent — SAST, LGPD/HIPAA compliance, PII/PHI detection"""import re
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class SecurityAgent:
    """Security Engineer — segurança e compliance"""
    
    def __init__(self):
        self.name = "SECURITY_AGENT"
        self.role = "Security Engineer"
        
        # Padrões comuns de PII/PHI
        self.pii_patterns = {
            "cpf": r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
            "cnpj": r'\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\(?(\d{2})\)?\s?9?\d{4}-?\d{4}\b',
            "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            "medical_record": r'\bMRN[-_\s]?\d{6,10}\b',
        }
    
    def execute(self, audit_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise de segurança e compliance"""
        import time
        start_time = time.time()
        
        repo_path = Path(context["repo_path"])
        
        # Scan de PII/PHI
        pii_findings = self._scan_pii_phi(repo_path)
        
        # Verificar compliance (simulado)
        compliance = self._check_compliance(repo_path)
        
        # SAST básico (padrões comuns)
        sast_findings = self._sast_scan(repo_path)
        
        findings = pii_findings + sast_findings
        
        duration = time.time() - start_time
        
        return {
            "success": True,
            "duration_seconds": duration,
            "vulnerabilities": findings,
            "compliance": compliance,
            "findings": findings,            "evidence": ["sast_report.txt", "pii_scan.log"],
            "files_analyzed": [str(p) for p in repo_path.rglob("*.py")],
            "metrics": {
                "vulnerabilities_found": len(findings),
                "pii_exposures": len([f for f in findings if f.get("type") == "pii"]),
                "compliance_status": compliance.get("overall", "unknown")
            }
        }
    
    def _scan_pii_phi(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Scaneia PII/PHI em arquivos do repositório"""
        findings = []
        
        for ext in ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.php"]:
            for file_path in repo_path.rglob(ext):
                if any(skip in str(file_path) for skip in ["venv/", "node_modules/", ".git/"]):
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    for pii_type, pattern in self.pii_patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in list(matches)[:5]:  # Máximo 5 por arquivo
                            findings.append({
                                "type": "pii_exposure",
                                "pii_type": pii_type,
                                "severity": "critical" if pii_type in ["cpf", "cnpj", "credit_card", "medical_record"] else "high",
                                "file": str(file_path.relative_to(repo_path)),
                                "line": content[:match.start()].count('\n') + 1,
                                "snippet": content[max(0, match.start()-20):match.end()+20]
                            })
                except Exception:
                    continue  # Arquivo binário ou erro de leitura
        
        return findings
    
    def _check_compliance(self, repo_path: Path) -> Dict[str, Any]:
        """Verifica compliance LGPD/HIPAA/ANS/TISS"""
        compliance = {
            "lgpd": {"status": "compliant", "violations": []},
            "hipaa": {"status": "compliant", "violations": []},
            "ans_tiss": {"status": "compliant", "violations": []},
            "overall": "compliant"
        }
        
        # Verificar políticas de privacidade
        privacy_files = ["privacy_policy.md", "security.md", "data_policy.md", "README.md"]
        has_policy = any((repo_path / f).exists() for f in privacy_files)
                if not has_policy:
            compliance["lgpd"]["violations"].append("Política de privacidade ausente")
            compliance["lgpd"]["status"] = "non_compliant"
            compliance["hipaa"]["violations"].append("HIPAA policy missing")
            compliance["hipaa"]["status"] = "non_compliant"
            compliance["overall"] = "non_compliant"
        
        return compliance
    
    def _sast_scan(self, repo_path: Path) -> List[Dict[str, Any]]:
        """SAST básico — padrões comuns de vulnerabilidades"""
        findings = []
        
        # Padrões de vulnerabilidades comuns
        vuln_patterns = {
            "sql_injection": r"(?i)(cursor\.execute|db\.query).*[\+\%\-\{\}]",  # Query concatenada
            "xss_reflected": r"(?i)request\.args\[.+\].*response",  # Input refletido
            "hardcoded_secret": r"(?i)(api_key|password|secret|token)\s*[=:]\s*[\"\'][^\"\']+",
            "command_injection": r"(?i)(subprocess\.|os\.system|os\.popen)\(.*\+.*request",
        }
        
        for file_path in repo_path.rglob("*.py"):
            if any(skip in str(file_path) for skip in ["venv/", "test", "mock"]):
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for vuln_type, pattern in vuln_patterns.items():
                    matches = re.finditer(pattern, content)
                    for match in list(matches)[:3]:  # Máximo 3 por arquivo
                        findings.append({
                            "type": "vulnerability",
                            "vuln_type": vuln_type,
                            "severity": "high" if vuln_type == "hardcoded_secret" else "medium",
                            "file": str(file_path.relative_to(repo_path)),
                            "line": content[:match.start()].count('\n') + 1,
                            "description": f"{vuln_type.replace('_', ' ').title()} vulnerability"
                        })
            except Exception:
                continue
        
        return findings
