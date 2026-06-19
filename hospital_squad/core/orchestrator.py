#!/usr/bin/env python3
"""
Hospital Squad Orchestrator
Coordena o squad de 13 agentes em pipeline sequencial
"""
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path

from hospital_squad.events.event_bus import emit_event, event_bus
from hospital_squad.agents.po_agent import POAgent
from hospital_squad.agents.qa_agent import QAAgent
from hospital_squad.agents.security_agent import SecurityAgent


class HospitalSquadOrchestrator:
    """Orquestra o squad completo"""
    
    def __init__(self):
        # Squad de agentes (MVP com 3, escalável para 13)
        self.agents = {
            "PO": POAgent(),
            "QA": QAAgent(),
            "SECURITY": SecurityAgent(),
            # TODO: Adicionar os outros 10 agentes
        }
        
        # Timeline de execução
        self.timeline = []
    
    def run_audit(self, repo_path: str, client_id: str = "default") -> Dict[str, Any]:
        """Executa auditoria completa"""
        audit_id = str(uuid.uuid4())
        
        # Emitir evento de início
        emit_event(
            audit_id=audit_id,
            agent="ORCHESTRATOR",
            event_type="audit_start",
            action=f"Auditoria iniciada para {repo_path}",
            metrics={"client_id": client_id, "repo_path": repo_path}
        )
        
        started_at = datetime.now(timezone.utc)
        context = {
            "repo_path": repo_path,
            "audit_id": audit_id,            "client_id": client_id
        }
        results = {}
        
        # Pipeline sequencial
        pipeline = [
            ("PO", "product_owner_analysis"),
            ("QA", "quality_assurance"),
            ("SECURITY", "security_compliance"),
        ]
        
        for agent_key, phase in pipeline:
            agent = self.agents[agent_key]
            
            # Merge context com resultados anteriores
            agent_context = {**context, **results}
            
            # Executar agente
            result = agent.execute(audit_id, agent_context)
            results[phase] = result
            
            # Registrar na timeline
            self.timeline.append({
                "phase": phase,
                "agent": agent.name,
                "status": "success" if result.get("success") else "failed",
                "duration": result.get("metrics", {}).get("duration_seconds", 0),
                "findings": len(result.get("findings", result.get("vulnerabilities", [])))
            })
        
        # Gerar relatório final
        completed_at = datetime.now(timezone.utc)
        report = self._generate_final_report(audit_id, results, started_at, completed_at)
        
        # Emitir evento de conclusão
        emit_event(
            audit_id=audit_id,
            agent="ORCHESTRATOR",
            event_type="audit_complete",
            action="Auditoria concluída",
            metrics={
                "total_duration": (completed_at - started_at).total_seconds(),
                "phases_completed": len(self.timeline),
                "health_score": report.get("health_score", 0)
            }
        )
        
        return report
    
    def _generate_final_report(self, audit_id: str, results: Dict,                               started_at: datetime, completed_at: datetime) -> Dict[str, Any]:
        """Gera relatório consolidado"""
        
        # Calcular health score (0-1000, Fórmula 1)
        health_score = self._calculate_health_score(results)
        
        # Consolidar findings
        all_findings = []
        for phase, result in results.items():
            findings = result.get("vulnerabilities", result.get("business_rules", []))
            all_findings.extend(findings)
        
        # Timeline completa
        timeline = event_bus.get_timeline(audit_id)
        
        report = {
            "audit_id": audit_id,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": (completed_at - started_at).total_seconds(),
            "health_score": health_score,
            "timeline": self.timeline,
            "phases": results,
            "summary": {
                "total_findings": len(all_findings),
                "critical": sum(1 for f in all_findings if f.get("severity") == "critical"),
                "high": sum(1 for f in all_findings if f.get("severity") == "high"),
                "coverage": results.get("quality_assurance", {}).get("final_coverage", 0),
                "tests_generated": len(results.get("quality_assurance", {}).get("generated_tests", []))
            },
            "events_count": len(timeline)
        }
        
        # Salvar relatório
        report_path = Path(f"/root/selix/logs/audit_{audit_id}.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, default=str))
        
        return report
    
    def _calculate_health_score(self, results: Dict) -> int:
        """Calcula health score 0-1000"""
        score = 1000
        
        # Cobertura de testes (até 400 pontos)
        coverage = results.get("quality_assurance", {}).get("final_coverage", 0)
        score -= int((100 - coverage) * 4)
        
        # Vulnerabilidades críticas (-100 cada)
        vulns = results.get("security_compliance", {}).get("vulnerabilities", [])
        critical = sum(1 for v in vulns if v.get("severity") == "critical")
        score -= critical * 100
        
        # Vulnerabilidades high (-50 cada)
        high = sum(1 for v in vulns if v.get("severity") == "high")
        score -= high * 50
        
        # Compliance (-200 se não conforme)
        compliance = results.get("security_compliance", {}).get("compliance", {})
        if compliance.get("lgpd", {}).get("status") == "non_compliant":
            score -= 200
        
        return max(0, min(1000, score))


# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python orchestrator.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    orchestrator = HospitalSquadOrchestrator()
    report = orchestrator.run_audit(repo_path)
    
    print(json.dumps(report, indent=2, default=str))
