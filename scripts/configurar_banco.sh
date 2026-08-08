#!/bin/bash
# SELIX — Configuração otimizada do SQLite

DB_PATH="${1:-selix.db}"

echo "🔧 Otimizando $DB_PATH..."

sqlite3 "$DB_PATH" << 'SQL'
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-20000;
PRAGMA mmap_size=30000000000;
PRAGMA temp_store=MEMORY;
PRAGMA auto_vacuum=INCREMENTAL;
PRAGMA busy_timeout=5000;
SQL

echo "✅ Banco otimizado!"
sqlite3 "$DB_PATH" "PRAGMA journal_mode; PRAGMA cache_size;"
