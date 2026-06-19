#!/usr/bin/env python3
"""Product Owner Agent — Extrai requisitos do README/docs"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class POAgent:
    """Product Owner — requisitos e regras de negócio"""
    
    def __init__(self):
        self.name = "PO_AGENT"
        self.role = "Product Owner Senior"
    
    def execute(self, audit_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise de requisitos"""
        import time
        start_time = time.time()
        
        repo_path = Path(context["repo_path"])
        
        # Extrair README e documentos
        readme_path = repo_path / "README.md"
        readme_content = readme_path.read_text(encoding='utf-8', errors='ignore') if readme_path.exists() else ""
        
        # Extrair regras de negócio (padrões comuns)
        business_rules = []
        for keyword in ["LGPD", "HIPAA", "ANS", "TISS", "deve", "DEVE", "requisito", "requirement"]:
            if keyword.lower() in readme_content.lower():
                business_rules.append({
                    "id": f"BR{len(business_rules)+1:03d}",
                    "description": f"Regra identificada: {keyword}",
                    "source": "README.md",
                    "criticality": "high" if keyword in ["LGPD", "HIPAA", "ANS", "TISS"] else "medium"
                })
        
        duration = time.time() - start_time
        
        return {
            "success": True,
            "duration_seconds": duration,
            "business_rules": business_rules,
            "findings": business_rules,
            "evidence": ["README.md"],
            "files_analyzed": [str(readme_path)],
            "metrics": {
                "rules_extracted": len(business_rules),
                "readme_size": len(readme_content)            }
        }
