"""
State Manager – Resiliência estilo Prevayler para Termux
Salva e restaura estado do sistema em caso de crash.
"""
import os
import json
import pickle
import sqlite3
from datetime import datetime
from threading import Lock

STATE_DIR = "/data/data/com.termux/files/home/selix/state"
STATE_FILE = f"{STATE_DIR}/selix_state.pkl"
DB_BACKUP = f"{STATE_DIR}/selix.db.backup"

class StateManager:
    def __init__(self):
        os.makedirs(STATE_DIR, exist_ok=True)
        self.lock = Lock()
        self._load_state()
    
    def _load_state(self):
        """Carrega o último estado salvo"""
        try:
            with open(STATE_FILE, 'rb') as f:
                self.state = pickle.load(f)
            print(f"✅ Estado carregado: {self.state.get('last_action', 'N/A')}")
        except:
            self.state = {
                "last_action": None,
                "last_brent": None,
                "last_selic": None,
                "last_timestamp": None,
                "conversations": []
            }
    
    def save_state(self, action, brent=None, selic=None):
        """Salva estado atual (thread-safe)"""
        with self.lock:
            self.state["last_action"] = action
            self.state["last_brent"] = brent
            self.state["last_selic"] = selic
            self.state["last_timestamp"] = datetime.now().isoformat()
            with open(STATE_FILE, 'wb') as f:
                pickle.dump(self.state, f)
    
    def backup_db(self):
        """Backup do banco SQLite"""
        try:
            import shutil
            shutil.copy2('/data/data/com.termux/files/home/selix/selix.db', DB_BACKUP)
            return True
        except Exception as e:
            print(f"Backup DB falhou: {e}")
            return False
    
    def restore_db(self):
        """Restaura banco do último backup"""
        try:
            import shutil
            shutil.copy2(DB_BACKUP, '/data/data/com.termux/files/home/selix/selix.db')
            print("✅ Banco restaurado do backup")
            return True
        except:
            return False

state_mgr = StateManager()
