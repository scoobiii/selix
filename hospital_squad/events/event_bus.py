#!/usr/bin/env python3
"""
Event Bus — Event Sourcing Pattern
Timeline imutável de todas as ações dos agentes
"""
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AuditEvent:
    """Evento imutável da auditoria"""
    id: str
    timestamp: str
    audit_id: str
    agent: str
    event_type: str
    action: str
    evidence: List[str]
    metrics: Dict[str, Any]
    files: List[str]
    next_step: str
    severity: str = "info"

    def to_dict(self) -> Dict:
        return asdict(self)


class EventBus:
    def __init__(self, db_path: str = "/root/selix/selix.db"):
        self.db_path = db_path
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self._subscribers = []

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                audit_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                event_type TEXT NOT NULL,
                action TEXT NOT NULL,
                evidence TEXT,
                metrics TEXT,
                files TEXT,
                next_step TEXT,
                severity TEXT DEFAULT 'info'
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_audit_id ON audit_events(audit_id, timestamp)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_agent ON audit_events(agent, timestamp)")
        self.db.commit()

    def publish(self, event: AuditEvent):
        self.db.execute("""
            INSERT INTO audit_events 
            (id, timestamp, audit_id, agent, event_type, action, evidence, metrics, files, next_step, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id, event.timestamp, event.audit_id, event.agent,
            event.event_type, event.action,
            json.dumps(event.evidence), json.dumps(event.metrics),
            json.dumps(event.files), event.next_step, event.severity
        ))
        self.db.commit()
        for cb in self._subscribers:
            try:
                cb(event)
            except Exception as e:
                print(f"Erro no subscriber: {e}")

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def get_timeline(self, audit_id: str) -> List[Dict]:
        cursor = self.db.execute("SELECT * FROM audit_events WHERE audit_id = ? ORDER BY timestamp ASC", (audit_id,))
        cols = [d[0] for d in cursor.description]
        rows = []
        for row in cursor.fetchall():
            d = dict(zip(cols, row))
            d['evidence'] = json.loads(d['evidence'] or '[]')
            d['metrics'] = json.loads(d['metrics'] or '{}')
            d['files'] = json.loads(d['files'] or '[]')
            rows.append(d)
        return rows

    def get_agent_events(self, agent: str, limit: int = 50) -> List[Dict]:
        cursor = self.db.execute("SELECT * FROM audit_events WHERE agent = ? ORDER BY timestamp DESC LIMIT ?", (agent, limit))
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


event_bus = EventBus()

def emit_event(audit_id: str, agent: str, event_type: str, action: str,
               evidence: List[str] = None, metrics: Dict = None,
               files: List[str] = None, next_step: str = None,
               severity: str = "info") -> AuditEvent:
    event = AuditEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        audit_id=audit_id,
        agent=agent,
        event_type=event_type,
        action=action,
        evidence=evidence or [],
        metrics=metrics or {},
        files=files or [],
        next_step=next_step,
        severity=severity
    )
    event_bus.publish(event)
    return event
