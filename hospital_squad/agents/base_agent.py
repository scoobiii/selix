#!/usr/bin/env python3
"""
Base Agent — Template Method Pattern
Todos os agentes herdam desta classe
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime, timezone
import time
import logging

from hospital_squad.events.event_bus import emit_event, AuditEvent

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agente base com lifecycle padrão"""
    
    def __init__(self, name: str, role: str, llm_provider: str = "local"):
        self.name = name
        self.role = role
        self.llm_provider = llm_provider
        self.audit_id = None
        self.started_at = None
        self.completed_at = None
    
    def execute(self, audit_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Template Method — lifecycle completo"""
        self.audit_id = audit_id
        self.started_at = datetime.now(timezone.utc)
        
        # 1. Emitir evento de início
        emit_event(
            audit_id=audit_id,
            agent=self.name,
            event_type="agent_start",
            action=f"{self.role} iniciou análise",
            metrics={"llm_provider": self.llm_provider}
        )
        
        try:
            start_time = time.time()
            
            # 2. Executar análise específica do agente
            result = self.analyze(context)
            
            duration = time.time() - start_time
                        # 3. Emitir evento de conclusão
            emit_event(
                audit_id=audit_id,
                agent=self.name,
                event_type="agent_complete",
                action=f"{self.role} concluiu análise",
                evidence=result.get("evidence", []),
                metrics={
                    "duration_seconds": round(duration, 2),
                    "findings_count": len(result.get("findings", [])),
                    **result.get("metrics", {})
                },
                files=result.get("files", []),
                next_step=result.get("next_step"),
                severity="info"
            )
            
            self.completed_at = datetime.now(timezone.utc)
            return result
            
        except Exception as e:
            logger.error(f"Erro no agente {self.name}: {e}")
            
            emit_event(
                audit_id=audit_id,
                agent=self.name,
                event_type="agent_error",
                action=f"{self.role} falhou: {str(e)}",
                severity="error"
            )
            
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Método abstrato — cada agente implementa sua lógica"""
        pass
    
    def _call_llm(self, prompt: str, **kwargs) -> str:
        """Chama LLM via LiteLLM (provider-agnostic)"""
        try:
            import litellm
            response = litellm.completion(
                model=self._get_model(),
                messages=[{"role": "user", "content": prompt}],
                **kwargs            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Fallback para determinístico: {e}")
            return self._deterministic_fallback(prompt)
    
    def _get_model(self) -> str:
        """Retorna modelo baseado no provider"""
        models = {
            "local": "ollama/qwen2.5:0.5b",
            "code": "ollama/qwen2.5-coder:1.5b",
            "api_openai": "gpt-4o-mini",
            "api_anthropic": "claude-3-5-sonnet-20241022",
            "api_deepseek": "deepseek/deepseek-chat",
            "api_qwen": "qwen/qwen-2.5-coder-32b-instruct"
        }
        return models.get(self.llm_provider, models["local"])
    
    def _deterministic_fallback(self, prompt: str) -> str:
        """Fallback determinístico quando LLM falha"""
        return "[FALLBACK] Análise determinística — LLM indisponível"
